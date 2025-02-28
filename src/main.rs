use std::time::Duration;

use ark_vote::{
    config::settings, error::AppError, init_db, init_dlq, init_redis, services::{ConsumerService, VotingService}, signal, snow_flake::Snowflake, vote
};
use async_nats::jetstream::{
    self,
    stream::{self},
};
use futures::StreamExt;
use mimalloc::MiMalloc;
use tokio::{self};
use tonic::transport::Server;
use tracing::{Level, error, info};

#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

#[tokio::main]
async fn main() -> Result<(), AppError> {
    tracing_subscriber::fmt().with_max_level(Level::INFO).init();

    // 初始化配置
    let config = settings();

    // 初始化组件
    let db_pool = init_db(config).await?;
    init_redis(config).await?;

    let nats_client = async_nats::connect(&config.nats.nats_url).await?;
    let jetstream = jetstream::new(nats_client.clone());

    // FIXME: 为了方便调试，每次启动都删除stream
    {
        jetstream
            .delete_stream("ARKVOTE")
            .await
            .map_err(|e| error!("Error deleting stream: {}", e))
            .ok();

        jetstream
            .delete_stream("ARKVOTE_DLQ")
            .await
            .map_err(|e| error!("Error deleting stream: {}", e))
            .ok();
    }

    init_dlq(&jetstream, config).await?;

    let mut shutdown_rx = signal::spawn_handler();
    let snowflake = Snowflake::new(config.snowflake.worker_id, config.snowflake.datacenter_id)?;

    // 启动gRPC服务
    std::thread::Builder::new()
        .name("voting-grpc-server".to_string())
        .spawn({
            let jetstream = jetstream.clone();
            let db_pool = db_pool.clone();

            let service = VotingService::new(jetstream, db_pool, snowflake).await?;
            let mut shutdown_rx = shutdown_rx.clone();
            let grpc_addr = config.grpc.grpc_addr.parse().unwrap();

            move || {
                let _ = tokio::runtime::Builder::new_multi_thread()
                    .worker_threads(4)
                    .enable_all()
                    .build()
                    .unwrap()
                    .block_on(async {
                        Server::builder()
                            .add_service(vote::voting_service_server::VotingServiceServer::new(
                                service,
                            ))
                            .serve_with_shutdown(grpc_addr, async {
                                let _ = shutdown_rx.changed().await;
                            })
                            .await
                            .map_err(|e| error!("voting gRPC server error: {}", e))
                    });
            }
        })
        .unwrap();

    let stream = jetstream
        .get_or_create_stream(jetstream::stream::Config {
            name: "ARKVOTE".to_string(),
            retention: stream::RetentionPolicy::WorkQueue,
            subjects: vec!["submit_vote".to_string()],
            ..Default::default()
        })
        .await?;

    let consumer = stream
        .create_consumer(jetstream::consumer::pull::Config {
            durable_name: Some("processor-1".to_string()),
            max_ack_pending: 100,
            ..Default::default()
        })
        .await?;
    let consumer_src = ConsumerService::new(jetstream, db_pool).await;

    let mut shutdown_rx_clone = shutdown_rx.clone();
    tokio::spawn(async move {
        loop {
            tokio::select! {
                _ = shutdown_rx_clone.changed() => {
                    info!("Received shutdown signal");
                    break;
                }
                result = consumer.fetch().max_messages(100).messages() => {
                    let mut messages = match result {
                        Ok(msgs) => msgs,
                        Err(e) => {
                            error!("Error fetching messages: {}", e);
                            tokio::time::sleep(Duration::from_secs(1)).await;
                            continue;
                        }
                    };

                    while let Some(message) = messages.next().await {
                        let (message, acker) = message.unwrap().split();
                        consumer_src.handle_message(message, acker).await;
                    }
                }
            }
        }
    });

    shutdown_rx.changed().await.unwrap();

    info!("Shutting down...");

    Ok(())
}
