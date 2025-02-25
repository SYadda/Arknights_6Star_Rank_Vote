use once_cell::sync::Lazy;
use prometheus::{Histogram, IntGauge, Registry};

pub fn registry() -> &'static Registry {
    static REGISTRY: Lazy<Registry> =
        Lazy::new(|| Registry::new_custom(Some("quilkin".into()), None).unwrap());

    &REGISTRY
}

pub fn messages_received_total() -> &'static IntGauge {
    static MESSAGES_RECEIVED_TOTAL: Lazy<IntGauge> = Lazy::new(|| {
        prometheus::register_int_gauge_with_registry! {
            prometheus::opts! {
                "messages_received_total",
                "Total number of messages received",
            },
            registry(),
        }
        .unwrap()
    });

    &MESSAGES_RECEIVED_TOTAL
}

pub fn messages_processed_total() -> &'static IntGauge {
    static MESSAGES_PROCESSED_TOTAL: Lazy<IntGauge> = Lazy::new(|| {
        prometheus::register_int_gauge_with_registry! {
            prometheus::opts! {
                "messages_processed_total",
                "Total number of messages processed",
            },
            registry(),
        }
        .unwrap()
    });

    &MESSAGES_PROCESSED_TOTAL
}

pub fn messages_failed_total() -> &'static IntGauge {
    static MESSAGES_FAILED_TOTAL: Lazy<IntGauge> = Lazy::new(|| {
        prometheus::register_int_gauge_with_registry! {
            prometheus::opts! {
                "messages_failed_total",
                "Total number of messages failed",
            },
            registry(),
        }
        .unwrap()
    });

    &MESSAGES_FAILED_TOTAL
}

pub fn message_process_time() -> &'static Histogram {
    static MESSAGE_PROCESS_TIME: Lazy<Histogram> = Lazy::new(|| {
        prometheus::register_histogram_with_registry! {
            prometheus::HistogramOpts::new(
                "message_process_time",
                "Time taken to process a message",
            )
            .buckets(vec![
                0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0
            ]),
            registry(),
        }
        .unwrap()
    });

    &MESSAGE_PROCESS_TIME
}

pub fn message_process_time_seconds() -> &'static IntGauge {
    static MESSAGE_PROCESS_TIME_SECONDS: Lazy<IntGauge> = Lazy::new(|| {
        prometheus::register_int_gauge_with_registry! {
            prometheus::opts! {
                "message_process_time_seconds",
                "Time taken to process a message",
            },
            registry(),
        }
        .unwrap()
    });

    &MESSAGE_PROCESS_TIME_SECONDS
}

pub fn pending_messages() -> &'static IntGauge {
    static PENDING_MESSAGES: Lazy<IntGauge> = Lazy::new(|| {
        prometheus::register_int_gauge_with_registry! {
            prometheus::opts! {
                "pending_messages",
                "Number of messages pending processing",
            },
            registry(),
        }
        .unwrap()
    });

    &PENDING_MESSAGES
}

pub fn dlq_messages_total() -> &'static IntGauge {
    static DLQ_MESSAGES_TOTAL: Lazy<IntGauge> = Lazy::new(|| {
        prometheus::register_int_gauge_with_registry! {
            prometheus::opts! {
                "dlq_messages_total",
                "Total number of messages sent to the DLQ",
            },
            registry(),
        }
        .unwrap()
    });

    &DLQ_MESSAGES_TOTAL
}

pub fn shutdown_initiated() -> &'static IntGauge {
    static SHUTDOWN_INITATED: Lazy<IntGauge> = Lazy::new(|| {
        prometheus::register_int_gauge_with_registry! {
            prometheus::opts! {
                "shutdown_initiated",
                "Shutdown process has been started",
            },
            registry(),
        }
        .unwrap()
    });

    &SHUTDOWN_INITATED
}
