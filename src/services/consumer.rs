use std::{
    str::FromStr,
    sync::LazyLock,
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
use sqlx::types::ipnetwork::IpNetwork;
use tracing::{error, info, instrument, warn};

use crate::{
    BASE_MULTIPLIER, LOW_MULTIPLIER, config::settings, error::AppError, get_redis_conn, metrics,
    vote,
};

const SINGLE_OPTION_SCRIPT: &str = r#"
local topic_id = ARGV[1]
local selected = tonumber(ARGV[2])
local excluded = tonumber(ARGV[3])
local multiplier = tonumber(ARGV[4])

if selected == excluded then
    return 0  -- 过滤相同选项
end

redis.call("INCRBY", "topic_id"..":"..topic_id..":"..selected..":win", multiplier)
redis.call("INCRBY", "topic_id"..":"..topic_id..":"..excluded..":lose", multiplier)
redis.call("INCRBY", "topic_id"..":"..topic_id..":op_matrix:"..selected..":"..excluded, multiplier)
redis.call("DECRBY", "topic_id"..":"..topic_id..":op_matrix:"..excluded..":"..selected, multiplier)

return 1
"#;

const MULTI_OPTION_SCRIPT: &str = r#"
local topic_id = ARGV[1]
local selected_str = ARGV[2]
local excluded_str = ARGV[3]
local multiplier = tonumber(ARGV[4])

-- 列表解析
local function split_numbers(str)
    local t = {}
    for s in string.gmatch(str, '([^,]+)') do
        table.insert(t, tonumber(s))
    end
    return t
end

local selected = split_numbers(selected_str)
local excluded = split_numbers(excluded_str)

-- 矩阵操作
for _, s in ipairs(selected) do
    for _, e in ipairs(excluded) do
        if s ~= e then
            redis.call("INCRBY", "topic_id"..":"..topic_id..":"..s..":win", multiplier)
            redis.call("INCRBY", "topic_id"..":"..topic_id..":"..e..":lose", multiplier)
            redis.call("INCRBY", "topic_id"..":"..topic_id..":op_matrix:"..s..":"..e, multiplier)
            redis.call("DECRBY", "topic_id"..":"..topic_id..":op_matrix:"..e..":"..s, multiplier)
        end
    end
end

return #selected * #excluded  -- 返回操作组合数
"#;

static REDIS_SINGLE_OPTION_SCRIPT: LazyLock<redis::Script> =
    LazyLock::new(|| redis::Script::new(SINGLE_OPTION_SCRIPT));

static REDIS_MULTI_OPTION_SCRIPT: LazyLock<redis::Script> =
    LazyLock::new(|| redis::Script::new(MULTI_OPTION_SCRIPT));

#[derive(Debug, Clone, sqlx::Type)]
#[sqlx(type_name = "ballot_status")]
enum BallotStatus {
    Created = 0,
    Processed = 1,
    Invalid = 2,
    Discarded = 3,
}

impl From<vote::BallotStatus> for BallotStatus {
    fn from(status: vote::BallotStatus) -> Self {
        match status {
            vote::BallotStatus::Created => BallotStatus::Created,
            vote::BallotStatus::Processed => BallotStatus::Processed,
            vote::BallotStatus::Invalid => BallotStatus::Invalid,
            vote::BallotStatus::Discarded => BallotStatus::Discarded,
        }
    }
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

struct ValidationService;

impl ValidationService {
    pub fn validate_ballot(
        request: &vote::SubmitVoteRequest,
        info: &vote::BallotInfo,
    ) -> Result<(), AppError> {
        Self::validate_status(info)?;
        Self::validate_identity(request, info)?;
        Self::validate_options(request, info)?;
        Ok(())
    }

    fn validate_status(info: &vote::BallotInfo) -> Result<(), AppError> {
        if info.status != vote::BallotStatus::Created as i32 {
            Err(AppError::InvalidBallotStatus(info.status))
        } else {
            Ok(())
        }
    }

    fn validate_identity(
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

    fn validate_options(
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
        let config = settings();
        Self {
            db_pool,
            jetstream,
            dlq_subject: config.dlq.dlq_subject.clone(),
            max_retries: config.dlq.max_retry_attempts,
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
            self.ack_message(&acker).await;
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
        info!("Received vote submission: {}", vote_request.ballot_code);
        let mut redis_conn = get_redis_conn().await?;

        let ballot_info = self
            .get_and_validate_ballot(&vote_request, &mut redis_conn)
            .await?;

        let save_result = async {
            match ValidationService::validate_ballot(&vote_request, &ballot_info) {
                Ok(_) => {
                    self.process_valid_vote(&vote_request, &ballot_info, redis_conn)
                        .await
                }
                Err(e) => {
                    self.save_ballot(
                        &vote_request,
                        &ballot_info,
                        vote::BallotStatus::Invalid,
                        0,
                        Some(&e),
                    )
                    .await?;
                    Err(e)
                }
            }
        }
        .await;

        match save_result {
            Ok(_) => info!("Processed ballot: {}", vote_request.ballot_code),
            Err(e) => warn!(
                "Failed processing ballot: {} - {}",
                vote_request.ballot_code, e
            ),
        }

        Ok(())
    }

    async fn process_valid_vote(
        &self,
        vote_request: &vote::SubmitVoteRequest,
        ballot_info: &vote::BallotInfo,
        mut redis_conn: PooledConnection<'static, RedisConnectionManager>,
    ) -> Result<(), AppError> {
        let multiplier = self
            .calculate_multiplier(vote_request, &mut redis_conn)
            .await?;
        self.update_vote_statistics(vote_request, ballot_info, multiplier, redis_conn)
            .await?;

        self.save_ballot(
            vote_request,
            ballot_info,
            vote::BallotStatus::Processed,
            multiplier,
            None,
        )
        .await
    }

    async fn get_and_validate_ballot(
        &self,
        vote_request: &vote::SubmitVoteRequest,
        redis_conn: &mut PooledConnection<'static, RedisConnectionManager>,
    ) -> Result<vote::BallotInfo, AppError> {
        let ballot_key = format!("ballot:{}", vote_request.ballot_code);

        let ballot_data: Option<Vec<u8>> = redis_conn.get_del(&ballot_key).await?;

        if let Some(data) = ballot_data {
            let ballot_info = vote::BallotInfo::decode(&*data)?;
            match ballot_info.status {
                s if s == vote::BallotStatus::Created as i32 => Ok(ballot_info),
                _ => {
                    warn!("Invalid ballot status: {}", ballot_info.status);
                    Err(AppError::InvalidBallotStatus(ballot_info.status))
                }
            }
        } else {
            warn!("Ballot not found for code: {}", vote_request.ballot_code);
            Err(AppError::BallotNotFound(
                vote_request.ballot_code.to_string(),
            ))
        }
    }

    async fn update_vote_statistics(
        &self,
        vote_request: &vote::SubmitVoteRequest,
        ballot_info: &vote::BallotInfo,
        multiplier: i32,
        mut redis_conn: PooledConnection<'static, RedisConnectionManager>,
    ) -> Result<(), AppError> {
        let selected = &vote_request.selected_option;
        let excluded = &vote_request.excluded_option;

        match (selected.len(), excluded.len()) {
            (1, 1) => {
                let selected = selected.first().unwrap().to_string();
                let excluded = excluded.first().unwrap().to_string();

                let _: () = REDIS_SINGLE_OPTION_SCRIPT
                    .arg(ballot_info.topic_id.to_string())
                    .arg(&selected)
                    .arg(&excluded)
                    .arg(multiplier)
                    .invoke_async(&mut *redis_conn)
                    .await?;
            }
            _ => {
                let selected_str = selected
                    .iter()
                    .map(|n| n.to_string())
                    .collect::<Vec<_>>()
                    .join(",");

                let excluded_str = excluded
                    .iter()
                    .map(|n| n.to_string())
                    .collect::<Vec<_>>()
                    .join(",");

                let _: () = REDIS_MULTI_OPTION_SCRIPT
                    .arg(ballot_info.topic_id.to_string())
                    .arg(selected_str)
                    .arg(excluded_str)
                    .arg(multiplier)
                    .invoke_async(&mut *redis_conn)
                    .await?;
            }
        }

        Ok(())
    }

    async fn calculate_multiplier(
        &self,
        vote_request: &vote::SubmitVoteRequest,
        redis_conn: &mut PooledConnection<'static, RedisConnectionManager>,
    ) -> Result<i32, AppError> {
        let identity = vote_request
            .identity
            .as_ref()
            .ok_or(AppError::MissingIdentity)?;
        let counter_key = format!("ip_counter:{}", identity.ip);

        let current: i32 = redis_conn.incr(&counter_key, 1).await?;
        let max_limit = settings().max_ip_limit;

        Ok(match (current, max_limit) {
            (c, m) if m < 0 || c <= m => BASE_MULTIPLIER,
            _ => LOW_MULTIPLIER,
        })
    }

    async fn save_ballot(
        &self,
        vote_request: &vote::SubmitVoteRequest,
        ballot_info: &vote::BallotInfo,
        status: vote::BallotStatus,
        multiplier: i32,
        error: Option<&AppError>,
    ) -> Result<(), AppError> {
        let voter_identity = vote_request
            .identity
            .as_ref()
            .ok_or(AppError::MissingIdentity)?;
        let voter_ip: Option<IpNetwork> = voter_identity.ip.parse().ok();

        let process_info = json!({
            "error": error.as_ref().map_or("None".to_string(), |e| e.to_string()),
            "code": ballot_info.ballot_code,
            "timestamp": chrono::Utc::now().to_rfc3339()
        });

        sqlx::query(
            r#"
            INSERT INTO votes (
                topic_id, ballot_code, fingerprint, ip, is_mobile,
                selected_options, excluded_options, status,
                process_info, options, multiplier
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            "#,
        )
        .bind(ballot_info.topic_id as i16)
        .bind(vote_request.ballot_code.to_string())
        .bind(voter_identity.fingerprint.clone())
        .bind(voter_ip)
        .bind(voter_identity.is_mobile)
        .bind(&vote_request.selected_option)
        .bind(&vote_request.excluded_option)
        .bind(BallotStatus::from(status))
        .bind(process_info)
        .bind(&ballot_info.options)
        .bind(multiplier)
        .execute(&self.db_pool)
        .await?;

        Ok(())
    }
}
