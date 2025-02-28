pub mod config;
pub mod error;
pub mod metrics;
pub mod services;
pub mod signal;
pub mod snow_flake;
pub mod models;

pub mod vote {
    tonic::include_proto!("vote");
}

use std::sync::OnceLock;

use async_nats::jetstream;
use bb8::{Pool, PooledConnection};
use bb8_redis::RedisConnectionManager;
use config::AppConfig;
use error::AppError;
use snow_flake::Snowflake;
use sqlx::postgres::PgPoolOptions;

const OPERATOR_IDS: [i32; 106] = [
    3, 10, 17, 103, 112, 113, 134, 136, 147, 172, 179, 180, 188, 197, 202, 206, 213, 222, 225, 245,
    248, 249, 250, 263, 264, 291, 293, 300, 311, 322, 332, 340, 350, 358, 362, 377, 391, 400, 416,
    420, 423, 426, 427, 430, 437, 456, 472, 474, 479, 485, 1012, 1013, 1014, 1016, 1019, 1020,
    1023, 1026, 1028, 1029, 1031, 1032, 1033, 1034, 1035, 1038, 1039, 1040, 1502, 2012, 2013, 2014,
    2015, 2023, 2024, 2025, 2026, 4009, 4011, 4026, 4027, 4039, 4042, 4046, 4048, 4055, 4058, 4064,
    4065, 4072, 4080, 4082, 4087, 4088, 4098, 4116, 4117, 4121, 4123, 4132, 4133, 4134, 4138, 4141,
    4145, 4146,
];
const BASE_MULTIPLIER: i32 = 100;
const LOW_MULTIPLIER: i32 = 1;

static REDIS_POOL: OnceLock<ConnectionPool> = OnceLock::new();

type ConnectionPool = Pool<RedisConnectionManager>;

// Redis连接管理
pub async fn get_redis_conn() -> Result<PooledConnection<'static, RedisConnectionManager>, AppError>
{
    REDIS_POOL
        .get()
        .ok_or(AppError::RedisPoolNotInitialized)?
        .get()
        .await
        .map_err(Into::into)
}

// 初始化函数
pub async fn init_redis(settings: &AppConfig) -> Result<(), AppError> {
    let manager = RedisConnectionManager::new(settings.redis_url.clone())?;
    let pool = Pool::builder()
        .max_size(settings.max_redis_connections)
        .build(manager)
        .await?;

    REDIS_POOL
        .set(pool)
        .map_err(|_| AppError::RedisPoolInitError)
}

pub async fn init_db(settings: &AppConfig) -> Result<sqlx::PgPool, AppError> {
    let pool = PgPoolOptions::new()
        .max_connections(settings.max_db_connections)
        .connect(&settings.database_url)
        .await?;

    sqlx::migrate!().run(&pool).await?;
    Ok(pool)
}

pub async fn init_dlq(
    jetstream: &jetstream::Context,
    settings: &AppConfig,
) -> Result<(), AppError> {
    jetstream
        .get_or_create_stream(jetstream::stream::Config {
            name: "DLQ".to_string(),
            subjects: vec![settings.dlq_subject.clone()],
            retention: jetstream::stream::RetentionPolicy::Limits,
            ..Default::default()
        })
        .await?;
    Ok(())
}
