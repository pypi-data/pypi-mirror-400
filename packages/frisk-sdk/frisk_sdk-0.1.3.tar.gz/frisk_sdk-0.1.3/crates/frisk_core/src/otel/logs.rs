use opentelemetry_otlp::{LogExporter, WithExportConfig, WithTonicConfig};
use opentelemetry_sdk::{Resource, logs};
use std::sync::{Arc, RwLock};
use tonic::metadata::MetadataMap;

use crate::otel::config::{OTEL_COLLECTOR_ENDPOINT, RESOURCE_ATTRIBUTES};
use crate::otel::runtime::tokio_runtime;

pub fn init_otel_logs(metadata: MetadataMap) -> anyhow::Result<logs::SdkLoggerProvider> {
    let rt = tokio_runtime();

    // Build the OTLP log exporter and logger provider inside the Tokio runtime.
    let logger_provider = rt.block_on(async {
        // 1) OTLP log exporter (gRPC to your collector)
        let log_exporter = LogExporter::builder()
            .with_tonic() // gRPC client
            .with_endpoint(OTEL_COLLECTOR_ENDPOINT.as_str())
            .with_metadata(metadata)
            .build()?; // this is where "no reactor" would occur

        // 2) Resource attributes
        let resource = Resource::builder_empty()
            .with_attributes(RESOURCE_ATTRIBUTES.iter().cloned())
            .build();

        // 3) Logger provider with batch exporter
        let logger_provider = logs::SdkLoggerProvider::builder()
            .with_batch_exporter(log_exporter)
            .with_resource(resource)
            .build();

        Ok::<logs::SdkLoggerProvider, anyhow::Error>(logger_provider)
    })?;

    Ok(logger_provider)
}

/// Build a logger provider using a bearer token string by inserting it into gRPC metadata.
pub fn init_otel_logs_with_token(token: &str) -> anyhow::Result<logs::SdkLoggerProvider> {
    let mut metadata = MetadataMap::new();
    // Common header name for OTLP auth; adjust if your collector expects a different key.
    // For many setups, "authorization: Bearer <token>" works.
    metadata.insert("authorization", format!("Bearer {}", token).parse()?);
    init_otel_logs(metadata)
}

/// A simple manager that holds a current logger provider and can rebuild it when the API token changes.
/// opentelemetry-otlp's exporter metadata is configured at build-time; there isn't a runtime method to mutate it.
/// The recommended approach is to recreate the exporter/provider when credentials change.
#[derive(Clone, Debug)]
pub struct LoggerProviderManager {
    inner: Arc<RwLock<logs::SdkLoggerProvider>>, // current provider
}

impl LoggerProviderManager {
    /// Create a new manager from an initial provider.
    pub fn new(initial_provider: logs::SdkLoggerProvider) -> Self {
        Self {
            inner: Arc::new(RwLock::new(initial_provider)),
        }
    }

    pub fn create_from_token(token: &str) -> anyhow::Result<Self> {
        let provider = init_otel_logs_with_token(token)?;
        Ok(Self {
            inner: Arc::new(RwLock::new(provider)),
        })
    }

    /// Get a clone of the current provider (read-only usage).
    pub fn get(&self) -> logs::SdkLoggerProvider {
        self.inner
            .read()
            .expect("Failed to acquire lock on SdkLoggerProvider")
            .clone()
    }

    /// Replace the provider by rebuilding it with a new token.
    /// This safely swaps the provider so new loggers use updated metadata.
    pub fn update_token(&self, token: &str) -> anyhow::Result<()> {
        let new_provider = init_otel_logs_with_token(token)?;
        // Optionally, shutdown the old provider to flush logs.
        {
            let mut guard = self.inner.write().unwrap();
            let old = std::mem::replace(&mut *guard, new_provider);
            // Try to flush and shutdown old provider. Ignore errors to avoid disrupting callers.
            let _ = old.shutdown();
        }
        Ok(())
    }

    pub fn shutdown(&self) {
        let guard = self.inner.write().unwrap();
        let _ = guard.shutdown();
    }
}
