use async_nats::{ConnectError, Error as NatsError, error::Error as NatsClientError, jetstream};
use prost::DecodeError;
use redis::RedisError;
use sqlx::{Error as SqlxError, migrate::MigrateError};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    // 序列化/反序列化错误
    #[error("Prost decode error: {0}")]
    ProstDecode(#[from] DecodeError),

    // Redis 相关错误
    #[error("Redis error: {0}")]
    Redis(#[from] RedisError),
    #[error("Redis pool not initialized")]
    RedisPoolNotInitialized,
    #[error("Failed to get redis connection")]
    RedisConnectionError,
    #[error("Redis run error: {0}")]
    RedisRunError(#[from] bb8::RunError<RedisError>),

    // NATS 相关错误
    #[error("NATS connection error: {0}")]
    NatsConnection(#[from] ConnectError),
    #[error("NATS error: {0}")]
    Nats(#[from] NatsError),

    // JetStream 相关错误
    #[error("JetStream create stream error: {0}")]
    JetStreamCreateStream(#[from] jetstream::context::CreateStreamError),
    #[error("JetStream consumer error: {0}")]
    JetStreamConsumer(#[from] jetstream::stream::ConsumerError),
    #[error("JetStream stream error: {0}")]
    JetStreamStream(#[from] jetstream::consumer::StreamError),
    #[error("JetStream batch error: {0}")]
    JetStreamBatch(#[from] jetstream::consumer::pull::BatchError),
    #[error("JetStream publish error: {0}")]
    JetStreamPublish(#[from] NatsClientError<jetstream::context::PublishErrorKind>),
    #[error("JetStream error: {0}")]
    JetStream(#[from] jetstream::Error),

    // SQLx 相关错误
    #[error("SQLx error: {0}")]
    Sqlx(#[from] SqlxError),
    #[error("SQLx migration error: {0}")]
    SqlxMigrate(#[from] MigrateError),

    // Snowflake 错误
    #[error("Snowflake error: {0}")]
    Snowflake(#[from] crate::snow_flake::SnowflakeError),

    // 业务逻辑错误
    #[error("Ballot not found: {0}")]
    BallotNotFound(String),
    #[error("Identity mismatch: {0}")]
    BallotIdentityMismatch(String),
    #[error("Missing voter identity")]
    MissingIdentity,
    #[error("Missing ballot identity")]
    MissingBallotIdentity,
    #[error("Rate limit exceeded")]
    RateLimitExceeded,
    #[error("Config error")]
    ConfigError,
    #[error("Redis pool init error")]
    RedisPoolInitError,
    #[error("Invalid header value")]
    InvalidHeaderValue,
    #[error("Invalid ballot status: {0}")]
    InvalidBallotStatus(i32),
    #[error("Invalid vote options")]
    InvalidVoteOptions,
    #[error("Topic not found")]
    TopicNotFound,
    #[error("Topic not started")]
    TopicNotStarted,
    #[error("Topic has finished")]
    TopicFinished,
    #[error("Insufficient operators")]
    InsufficientOperators,

    // 其他错误
    #[error("Unknown error: {0}")]
    Other(#[from] anyhow::Error),
}

impl From<AppError> for tonic::Status {
    fn from(err: AppError) -> Self {
        match err {
            AppError::RedisConnectionError => tonic::Status::unavailable("Redis unavailable"),
            AppError::BallotNotFound(_) => tonic::Status::not_found("Ballot not found"),
            _ => tonic::Status::internal("Internal server error"),
        }
    }
}

impl AppError {
    pub fn is_retriable(&self) -> bool {
        matches!(self, Self::InvalidBallotStatus(_))
    }
}
