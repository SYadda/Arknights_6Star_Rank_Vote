use async_nats::jetstream;
use chrono::{DateTime, Utc};
use rand::seq::IndexedRandom;
use redis::AsyncCommands;
use sqlx::Row;
use sqlx::postgres::PgPoolOptions;
use tonic::{Request, Response, Status};
use tracing::{info, instrument};

use crate::{
    Snowflake,
    config::AppConfig,
    error::AppError,
    get_redis_conn,
    models::{self, Topic},
    vote,
};

pub struct VotingService {
    db_pool: sqlx::PgPool,
    jetstream: jetstream::Context,
    snowflake: Snowflake,
}

impl VotingService {
    pub async fn new(config: &AppConfig) -> Result<Self, AppError> {
        let db_pool = PgPoolOptions::new()
            .max_connections(config.max_db_connections)
            .connect(&config.database_url)
            .await?;

        let nats_client = async_nats::connect(&config.nats_url).await?;
        let jetstream = jetstream::new(nats_client);

        Ok(Self {
            db_pool,
            jetstream,
            snowflake: Snowflake::new(config.worker_id, config.datacenter_id)?,
        })
    }

    #[instrument(skip_all)]
    pub async fn create_ballot(
        &self,
        request: vote::CreateBallotRequest,
    ) -> Result<vote::BallotPair, AppError> {
        let topic = self.get_topic(&request.topic).await?;
        self.check_topic_status(&topic).await?;

        let identity = request.identity.as_ref().ok_or(AppError::MissingIdentity)?;

        let mut buf = vec![0i32; 2];
        self.generate_operator_pair(&mut buf)?;

        let ballot_code = self.snowflake.next_id()?;
        let ballot_info = vote::BallotInfo {
            topic_id: topic.id,
            topic: request.topic.clone(),
            ballot_code,
            identity: Some(identity.clone()),
            status: vote::BallotStatus::Created as i32,
            options: buf.to_vec(),
            excluded_option: vec![],
            selected_option: vec![],
        };

        self.cache_ballot(ballot_code, &ballot_info).await?;

        Ok(vote::BallotPair {
            topic_id: topic.id,
            topic: request.topic,
            ballot_code,
            options: buf.to_vec(),
        })
    }

    async fn check_topic_status(&self, topic: &Topic) -> Result<(), AppError> {
        let now = chrono::Utc::now();
        if now < topic.start_at {
            return Err(AppError::TopicNotStarted);
        }
        if now > topic.finish_at {
            return Err(AppError::TopicFinished);
        }
        Ok(())
    }

    async fn get_all_topics(&self) -> Result<Vec<Topic>, AppError> {
        Ok(sqlx::query_as("SELECT * FROM topics")
            .fetch_all(&self.db_pool)
            .await?)
    }

    async fn get_topic(&self, topic_name: &str) -> Result<Topic, AppError> {
        sqlx::query_as("SELECT * FROM topics WHERE name = $1")
            .bind(topic_name)
            .fetch_optional(&self.db_pool)
            .await?
            .ok_or(AppError::TopicNotFound)
    }

    async fn get_topics_by_timestamp(
        &self,
        timestamp: DateTime<Utc>,
    ) -> Result<Vec<Topic>, AppError> {
        Ok(
            sqlx::query_as("SELECT * FROM topics WHERE start_at <= $1 AND finish_at >= $1")
                .bind(timestamp)
                .fetch_all(&self.db_pool)
                .await?,
        )
    }

    fn generate_operator_pair(&self, buf: &mut [i32]) -> Result<(), AppError> {
        let mut rng = &mut rand::rng();
        for (b, slot) in crate::OPERATOR_IDS
            .choose_multiple(&mut rng, buf.len())
            .zip(buf.iter_mut())
        {
            *slot = *b;
        }

        Ok(())
    }

    async fn cache_ballot(&self, code: i64, info: &vote::BallotInfo) -> Result<(), AppError> {
        let mut conn = get_redis_conn().await?;
        let bytes = prost::Message::encode_to_vec(info);
        conn.set_ex(format!("ballot:{}", code), bytes, 3600)
            .await
            .map_err(Into::into)
    }

    fn map_topic_to_info(topic: Topic) -> vote::TopicInfo {
        vote::TopicInfo {
            topic_id: topic.id,
            name: topic.name,
            description: topic.description,
            topic_type: topic.r#type as i32,
            styles: serde_json::from_value(topic.style).unwrap_or_default(),
            status: topic.status as i32,
            start_at: topic.start_at.timestamp(),
            finish_at: topic.finish_at.timestamp(),
        }
    }
}

#[tonic::async_trait]
impl vote::voting_service_server::VotingService for VotingService {
    async fn create_ballot(
        &self,
        request: Request<vote::CreateBallotRequest>,
    ) -> Result<Response<vote::BallotPair>, Status> {
        let request = request.into_inner();
        self.create_ballot(request)
            .await
            .map(Response::new)
            .map_err(Into::into)
    }

    async fn submit_vote(
        &self,
        request: Request<vote::SubmitVoteRequest>,
    ) -> Result<Response<vote::TransactionResponse>, Status> {
        let vote_data = request.into_inner();
        self.jetstream
            .publish(
                "submit_vote",
                prost::Message::encode_to_vec(&vote_data).into(),
            )
            .await
            .map_err(|e| Status::internal(e.to_string()))?
            .await
            .map_err(|e| Status::internal(e.to_string()))?;

        // metrics::increment_counter!("votes_submitted_total");
        Ok(Response::new(vote::TransactionResponse {
            acknowledged: true,
            status_code: 200,
            error_message: String::new(),
        }))
    }

    async fn create_topic(
        &self,
        request: Request<vote::CreateTopicRequest>,
    ) -> Result<Response<vote::CreateTopicResponse>, Status> {
        let request = request.into_inner();

        let start_at = chrono::DateTime::from_timestamp(request.start_at, 0)
            .ok_or_else(|| Status::invalid_argument("Invalid start_at timestamp"))?
            .with_timezone(&chrono::Utc);

        let finish_at = chrono::DateTime::from_timestamp(request.finish_at, 0)
            .ok_or_else(|| Status::invalid_argument("Invalid finish_at timestamp"))?
            .with_timezone(&chrono::Utc);

        if start_at > finish_at {
            return Err(Status::invalid_argument(
                "start_at must be before finish_at",
            ));
        }

        let mut serde_map = serde_json::Map::new();
        for (key, value) in request.styles.iter() {
            serde_map.insert(key.clone(), serde_json::Value::String(value.clone()));
        }

        let topic = Topic {
            id: 0,
            name: request.name.clone(),
            description: request.description.clone(),
            r#type: models::TopicType::from(request.topic_type),
            style: serde_map.into(),
            status: models::TopicStatus::Normal,
            start_at,
            finish_at,
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
        };

        info!("Creating topic: {:?}", topic);

        let id = sqlx::query(
            r#"
            INSERT INTO topics (name, description, type, style, status, start_at, finish_at, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
            "#,
        ).bind(&topic.name)
            .bind(&topic.description)
            .bind(&topic.r#type)
            .bind(&topic.style)
            .bind(&topic.status)
            .bind(topic.start_at)
            .bind(topic.finish_at)
            .bind(topic.created_at)
            .bind(topic.updated_at)
            .fetch_one(&self.db_pool)
            .await
            .map_err(|e| Status::internal(e.to_string()))?
            .get::<i32, _>("id");

        info!("Topic created with ID: {}", id);

        Ok(Response::new(vote::CreateTopicResponse {
            topic_id: id,
            status: vote::TopicStatus::Normal as i32,
            error_message: String::new(),
        }))
    }

    async fn get_topic_info(
        &self,
        request: Request<vote::GetTopicInfoRequest>,
    ) -> Result<Response<vote::TopicInfo>, Status> {
        let topic_name = request.into_inner().topic;
        let topic = self
            .get_topic(&topic_name)
            .await
            .map_err(|e| Status::internal(e.to_string()))?;

        Ok(Response::new(Self::map_topic_to_info(topic)))
    }

    async fn fetch_all_active_topics(
        &self,
        _request: Request<vote::FetchAllActiveTopicsRequest>,
    ) -> Result<Response<vote::FetchAllActiveTopicsResponse>, Status> {
        let rows: Vec<Topic> = self
            .get_topics_by_timestamp(chrono::Utc::now())
            .await
            .map_err(|e| Status::internal(e.to_string()))?;

        let topics = rows.into_iter().map(Self::map_topic_to_info).collect();

        Ok(Response::new(vote::FetchAllActiveTopicsResponse { topics }))
    }

    async fn fetch_all_topics(
        &self,
        _request: Request<vote::FetchAllTopicsRequest>,
    ) -> Result<Response<vote::FetchAllTopicsResponse>, Status> {
        let rows: Vec<Topic> = self
            .get_all_topics()
            .await
            .map_err(|e| Status::internal(e.to_string()))?;

        let topics = rows.into_iter().map(Self::map_topic_to_info).collect();

        Ok(Response::new(vote::FetchAllTopicsResponse { topics }))
    }
}
