use std::sync::OnceLock;

use config::Config;
use serde::Deserialize;

pub fn settings() -> &'static AppConfig {
    static CONFIG: OnceLock<AppConfig> = OnceLock::new();
    CONFIG.get_or_init(|| AppConfig::load().unwrap())
}

#[derive(Debug, Clone, Deserialize)]
pub struct GrpcConfig {
    pub grpc_addr: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct NatsConfig {
    pub nats_url: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DatabaseConfig {
    pub database_url: String,
    pub max_connections: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct RedisConfig {
    pub redis_url: String,
    pub max_connections: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct SnowflakeConfig {
    pub worker_id: i64,
    pub datacenter_id: i64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct DlqConfig {
    pub dlq_subject: String,
    pub max_retry_attempts: usize,
}

#[derive(Debug, Clone, Deserialize)]
pub struct AppConfig {
    pub max_ip_limit: i32,
    pub grpc: GrpcConfig,
    pub nats: NatsConfig,
    pub database: DatabaseConfig,
    pub redis: RedisConfig,
    pub snowflake: SnowflakeConfig,
    pub dlq: DlqConfig,
}

impl AppConfig {
    fn load() -> Result<Self, config::ConfigError> {
        let cfg = Config::builder()
            .add_source(config::File::with_name("config.toml"))
            .add_source(config::Environment::with_prefix("ARKVOTE"))
            .build()
            .unwrap();

        cfg.try_deserialize()
    }
}
