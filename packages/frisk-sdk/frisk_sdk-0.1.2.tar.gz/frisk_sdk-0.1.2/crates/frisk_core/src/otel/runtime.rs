use once_cell::sync::OnceCell;
use tokio::runtime::{Builder, Runtime};

static TOKIO_RUNTIME: OnceCell<Runtime> = OnceCell::new();

pub fn tokio_runtime() -> &'static Runtime {
    TOKIO_RUNTIME.get_or_init(|| {
        Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("failed to build Tokio runtime")
    })
}
