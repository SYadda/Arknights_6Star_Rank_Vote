use std::{
    str::FromStr,
    time::{Duration, Instant},
};

use async_nats::{
    Message,
    jetstream::{self, AckKind, message::Acker},
};
use bb8::PooledConnection;
use bb8_redis::RedisConnectionManager;
use prost::Message as _;
use redis::AsyncCommands;
use serde_json::json;
use sqlx::{Executor, PgPool, types::ipnetwork::IpNetwork};
use tracing::{error, info, instrument, warn};

use crate::{
    BASE_MULTIPLIER, LOW_MULTIPLIER, config::settings, error::AppError, get_redis_conn, metrics,
    vote,
};

async fn save_ballot(
    vote_request: &vote::SubmitVoteRequest,
    ballot_info: &vote::BallotInfo,
    status: vote::BallotStatus,
    process_info: &Option<serde_json::Value>,
    db: &PgPool,
) -> Result<(), AppError> {
    let voter_identity = vote_request
        .identity
        .as_ref()
        .ok_or(AppError::MissingIdentity)?;
    let voter_ip: Option<IpNetwork> = voter_identity.ip.parse().ok();

    let process_info: serde_json::Value = match process_info {
        Some(value) => value.clone(),
        None => serde_json::Value::Null,
    };

    db.execute(sqlx::query!(
        "INSERT INTO votes (topic_id, ballot_code, fingerprint, ip, is_mobile, selected_options, excluded_options, status, process_info, options) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
        ballot_info.topic_id as i16,
        vote_request.ballot_code.to_string(),
        voter_identity.fingerprint,
        voter_ip,
        voter_identity.is_mobile,
        &vote_request.selected_option,
        &vote_request.excluded_option,
        status as i16,
        process_info,
        &ballot_info.options
    ))
    .await?;

    Ok(())
}

trait MessageExt {
    fn get_retry_count(&self) -> usize;
    fn increment_retry(&mut self) -> usize;
}

impl MessageExt for Message {
    fn get_retry_count(&self) -> usize {
        self.headers
            .as_ref()
            .and_then(|h| h.get(RETRY_HEADER))
            .and_then(|v| v.to_string().parse().ok())
            .unwrap_or(0)
    }

    fn increment_retry(&mut self) -> usize {
        let count = self.get_retry_count() + 1;
        let headers = self.headers.get_or_insert(async_nats::HeaderMap::new());
        headers.insert(
            RETRY_HEADER,
            async_nats::HeaderValue::from(count.to_string()),
        );
        count
    }
}

// 死信队列处理
const RETRY_HEADER: &str = "X-Retry-Count";
const DLQ_REASON_HEADER: &str = "X-DLQ-Reason";

// 消费者服务
pub struct ConsumerService {
    db_pool: sqlx::PgPool,
    jetstream: jetstream::Context,
    dlq_subject: String,
    max_retries: usize,
}

impl ConsumerService {
    pub async fn new(jetstream: jetstream::Context, db_pool: sqlx::PgPool) -> Self {
        Self {
            db_pool,
            jetstream,
            dlq_subject: settings().dlq_subject.clone(),
            max_retries: settings().max_retry_attempts,
        }
    }

    pub async fn handle_message(&self, msg: Message, acker: Acker) {
        let start_time = Instant::now();

        match self.process_message(&msg).await {
            Ok(_) => {
                metrics::messages_processed_total().inc();
                self.ack_message(&acker).await;
            }
            Err(e) => self.handle_error(msg, acker, e).await,
        }

        metrics::message_process_time().observe(start_time.elapsed().as_secs_f64());
    }

    async fn ack_message(&self, acker: &Acker) {
        if let Err(e) = acker.double_ack().await {
            error!("Failed to double ACK message: {}", e);
        }
    }

    async fn handle_error(&self, msg: Message, acker: Acker, error: AppError) {
        warn!("Error processing message: {}", error);
        metrics::messages_failed_total().inc();

        if error.is_retriable() && msg.get_retry_count() < self.max_retries {
            self.retry_message(msg, acker).await;
        } else {
            self.send_to_dlq(msg, &error.to_string()).await;
        }
    }

    async fn send_to_dlq(&self, mut msg: Message, reason: &str) {
        let headers = msg.headers.get_or_insert(async_nats::HeaderMap::new());
        headers.insert(
            DLQ_REASON_HEADER,
            async_nats::HeaderValue::from_str(reason)
                .unwrap_or_else(|_| async_nats::HeaderValue::from_str("unknown").unwrap()),
        );

        if let Err(e) = self
            .jetstream
            .publish(self.dlq_subject.clone(), msg.payload)
            .await
        {
            error!("Failed to publish to DLQ: {}", e);
        }
    }

    async fn retry_message(&self, mut msg: Message, acker: Acker) {
        let retry_count = msg.increment_retry();
        let delay = Duration::from_secs(2u64.pow(retry_count as u32));

        if let Err(e) = acker.ack_with(AckKind::Nak(Some(delay))).await {
            error!("Failed to NAK message: {}", e);
        }
    }

    #[instrument(skip_all)]
    async fn process_message(&self, msg: &Message) -> Result<(), AppError> {
        let payload = msg.payload.to_vec();
        let subject = msg.subject.as_str();

        match subject {
            "submit_vote" => self.process_vote(&payload).await,
            subject => {
                error!("Received message with unknown subject: {}", subject);
                Ok(())
            }
        }
    }

    #[instrument(skip_all)]
    async fn process_vote(&self, payload: &[u8]) -> Result<(), AppError> {
        let vote_request = vote::SubmitVoteRequest::decode(payload)?;
        info!("Received vote submission: {:?}", vote_request);

        let mut redis_conn = get_redis_conn().await?;
        let ballot_data: Option<Vec<u8>> = redis_conn
            .get_del(format!("ballot:{}", vote_request.ballot_code))
            .await?;

        let ballot_info = match ballot_data {
            Some(data) => vote::BallotInfo::decode(&*data)?,
            None => {
                info!("Ballot not found for code: {}", vote_request.ballot_code);
                return Err(AppError::BallotNotFound(
                    vote_request.ballot_code.to_string(),
                )); // Ballot not found, consider it processed.
            }
        };

        info!("Ballot info: {:?}", ballot_info);

        Self::validate_ballot_status(&ballot_info)?;

        match Self::validate_voter_identity(&vote_request, &ballot_info) {
            Ok(_) => {}
            Err(_) => {
                info!(
                    "Voter identity mismatch for ballot: {}",
                    vote_request.ballot_code
                );

                save_ballot(
                    &vote_request,
                    &ballot_info,
                    vote::BallotStatus::Invalid,
                    &Some(json!(format!(
                        "Voter identity mismatch for ballot: {}",
                        vote_request.ballot_code
                    ))),
                    &self.db_pool,
                )
                .await?;

                return Ok(()); // Voter identity mismatch, consider it processed.
            }
        }

        if Self::validate_vote_options(&vote_request, &ballot_info).is_err() {
            info!(
                "Invalid options for ballot: {}, selected: {:?}, excluded: {:?}",
                vote_request.ballot_code,
                vote_request.selected_option,
                vote_request.excluded_option
            );

            save_ballot(
                &vote_request,
                &ballot_info,
                vote::BallotStatus::Invalid,
                &Some(json!(format!(
                    "Invalid options for ballot: {}, selected: {:?}, excluded: {:?}",
                    vote_request.ballot_code,
                    vote_request.selected_option,
                    vote_request.excluded_option
                ))),
                &self.db_pool,
            )
            .await?;

            return Ok(());
        }

        let identity = vote_request
            .identity
            .as_ref()
            .ok_or(AppError::MissingIdentity)?;

        let _multiplier = Self::calculate_multiplier(&identity.ip, &mut redis_conn).await?;

        save_ballot(
            &vote_request,
            &ballot_info,
            vote::BallotStatus::Processed,
            &None,
            &self.db_pool,
        )
        .await?;

        info!(
            "Vote processed successfully for ballot code: {}, status: {:?}",
            vote_request.ballot_code,
            vote::BallotStatus::Processed
        );

        Ok(())
    }

    async fn calculate_multiplier(
        identifier: &str,
        redis_conn: &mut PooledConnection<'static, RedisConnectionManager>,
    ) -> Result<i64, AppError> {
        let counter_key = format!("ip_counter:{}", identifier);
        let current: i64 = redis_conn.incr(&counter_key, 1).await?;
        let max_ip_limit = settings().max_ip_limit;

        Ok(if current <= max_ip_limit || max_ip_limit < 0 {
            BASE_MULTIPLIER
        } else {
            LOW_MULTIPLIER
        })
    }

    // 验证函数
    fn validate_ballot_status(info: &vote::BallotInfo) -> Result<(), AppError> {
        if info.status != vote::BallotStatus::Created as i32 {
            Err(AppError::InvalidBallotStatus(info.status))
        } else {
            Ok(())
        }
    }

    fn validate_voter_identity(
        request: &vote::SubmitVoteRequest,
        info: &vote::BallotInfo,
    ) -> Result<(), AppError> {
        if request.identity != info.identity {
            Err(AppError::BallotIdentityMismatch(
                request.ballot_code.to_string(),
            ))
        } else {
            Ok(())
        }
    }

    fn validate_vote_options(
        request: &vote::SubmitVoteRequest,
        info: &vote::BallotInfo,
    ) -> Result<(), AppError> {
        let valid_selected = request
            .selected_option
            .iter()
            .all(|o| info.options.contains(o));
        let valid_excluded = request
            .excluded_option
            .iter()
            .all(|o| info.options.contains(o));

        if valid_selected && valid_excluded {
            Ok(())
        } else {
            Err(AppError::InvalidVoteOptions)
        }
    }
}
