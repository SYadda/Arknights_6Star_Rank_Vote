use std::sync::OnceLock;

use config::Config;
use serde::Deserialize;

pub fn settings() -> &'static AppConfig {
    static CONFIG: OnceLock<AppConfig> = OnceLock::new();
    CONFIG.get_or_init(|| {
        

        AppConfig::load().unwrap()
    })
}

#[derive(Debug, Clone, Deserialize)]
pub struct AppConfig {
    pub database_url: String,
    pub redis_url: String,
    pub nats_url: String,
    pub max_ip_limit: i64,
    pub server_addr: String,
    pub worker_id: i64,
    pub datacenter_id: i64,
    pub max_db_connections: u32,
    pub max_redis_connections: u32,
    pub max_retry_attempts: usize,
    pub dlq_subject: String,
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
