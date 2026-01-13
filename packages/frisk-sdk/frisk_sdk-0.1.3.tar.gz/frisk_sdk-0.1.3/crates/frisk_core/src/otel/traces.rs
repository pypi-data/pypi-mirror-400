use crate::otel::config::{OTEL_COLLECTOR_ENDPOINT, RESOURCE_ATTRIBUTES};
use crate::otel::runtime::tokio_runtime;
use opentelemetry::global;
use opentelemetry_otlp::{SpanExporter, WithExportConfig, WithTonicConfig};
use opentelemetry_sdk::Resource;
use opentelemetry_sdk::trace::SdkTracerProvider;
use std::sync::{Arc, RwLock};
use tonic::metadata::MetadataMap;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::{EnvFilter, Layer, Registry};

pub fn init_tracing(metadata: MetadataMap) -> anyhow::Result<SdkTracerProvider> {
    // Set global propagator once (idempotent)
    global::set_text_map_propagator(opentelemetry_sdk::propagation::TraceContextPropagator::new());

    let rt = tokio_runtime();

    // Build exporter + tracer provider inside the Tokio runtime
    let tracer_provider = rt.block_on(async {
        // 1) OTLP span exporter over gRPC (tonic)
        let exporter = SpanExporter::builder()
            .with_tonic() // gRPC (tonic) client
            .with_endpoint(OTEL_COLLECTOR_ENDPOINT.as_str())
            .with_metadata(metadata)
            .build()?;

        let resource = Resource::builder()
            .with_attributes(RESOURCE_ATTRIBUTES.iter().cloned())
            .build();

        // 2) Tracer provider with batch exporter + resource
        let provider = SdkTracerProvider::builder()
            .with_resource(resource)
            .with_batch_exporter(exporter)
            .build();

        Ok::<SdkTracerProvider, anyhow::Error>(provider)
    })?;

    // 3) Register as global provider
    global::set_tracer_provider(tracer_provider.clone());

    // 4) Get a tracer from the global provider
    let tracer = global::tracer("policy-engine");

    let filter = EnvFilter::new("info")
        .add_directive("policy_engine=debug".parse()?)
        .add_directive("frisk_py=debug".parse()?)
        .add_directive("opentelemetry=warn".parse()?)
        .add_directive("opentelemetry_otlp=warn".parse()?)
        .add_directive("tonic=warn".parse()?)
        .add_directive("h2=warn".parse()?);
    // 5) Wire tracing → OpenTelemetry
    let otel_layer = tracing_opentelemetry::layer()
        .with_tracer(tracer)
        .with_filter(filter.clone());

    let fmt_layer = tracing_subscriber::fmt::layer()
        .with_target(false)
        .with_filter(filter);

    Registry::default()
        .with(otel_layer)
        .with(fmt_layer)
        .try_init()?;

    Ok(tracer_provider)
}

/// Build a tracer provider using a bearer token string by inserting it into gRPC metadata.
pub fn init_tracing_with_token(token: &str) -> anyhow::Result<SdkTracerProvider> {
    let mut metadata = MetadataMap::new();
    metadata.insert("authorization", format!("Bearer {}", token).parse()?);
    init_tracing(metadata)
}

#[derive(Clone, Debug)]
pub struct TracerProviderManager {
    inner: Arc<RwLock<SdkTracerProvider>>, // current tracer provider
}

impl TracerProviderManager {
    pub fn create_from_token(token: &str) -> anyhow::Result<Self> {
        let provider = init_tracing_with_token(token)?;
        Ok(Self {
            inner: Arc::new(RwLock::new(provider)),
        })
    }
    pub fn get(&self) -> SdkTracerProvider {
        self.inner
            .read()
            .expect("Failed to acquire lock on SdkMeterProvider")
            .clone()
    }
    pub fn update_token(&self, token: &str) -> anyhow::Result<()> {
        let new_provider = init_tracing_with_token(token)?;
        let mut guard = self.inner.write().unwrap();
        let old = std::mem::replace(&mut *guard, new_provider);
        let _ = old.shutdown();
        Ok(())
    }

    pub fn shutdown(&self) {
        let guard = self.inner.write().unwrap();
        let _ = guard.shutdown();
    }
}
