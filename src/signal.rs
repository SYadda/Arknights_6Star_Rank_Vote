pub type ShutdownRx = tokio::sync::watch::Receiver<ShutdownKind>;
pub type ShutdownTx = tokio::sync::watch::Sender<ShutdownKind>;

pub fn spawn_handler() -> ShutdownRx {
    let (tx, rx) = channel(ShutdownKind::default());
    ShutdownKind::spawn_signal_handler(tx);
    rx
}

pub fn channel(kind: ShutdownKind) -> (ShutdownTx, ShutdownRx) {
    tokio::sync::watch::channel(kind)
}

#[derive(Copy, Clone, PartialEq, Default, Debug)]
pub enum ShutdownKind {
    #[default]
    Normal,
    Testing,
    Benching,
}

impl ShutdownKind {
    #[inline]
    fn spawn_signal_handler(shutdown_tx: ShutdownTx) {
        crate::metrics::shutdown_initiated().set(false as _);

        #[cfg(target_os = "linux")]
        let mut sig_term_fut =
            tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate()).unwrap();

        tokio::spawn(async move {
            #[cfg(target_os = "linux")]
            let sig_term = sig_term_fut.recv();
            #[cfg(not(target_os = "linux"))]
            let sig_term = std::future::pending();

            let signal = tokio::select! {
                _ = tokio::signal::ctrl_c() => "SIGINT",
                _ = sig_term => "SIGTERM",
            };

            crate::metrics::shutdown_initiated().set(true as _);
            tracing::info!(%signal, "shutting down from signal");
            // Don't unwrap in order to ensure that we execute
            // any subsequent shutdown tasks.
            shutdown_tx.send(Self::Normal).ok();
        });
    }
}
