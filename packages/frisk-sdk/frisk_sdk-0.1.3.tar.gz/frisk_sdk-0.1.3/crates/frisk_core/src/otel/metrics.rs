use opentelemetry::global;
use opentelemetry::metrics::{Meter, MeterProvider};
use opentelemetry_otlp::{MetricExporter, WithExportConfig, WithTonicConfig};
use opentelemetry_sdk::metrics::SdkMeterProvider;
use opentelemetry_sdk::{Resource, metrics as sdkmetrics};
use std::sync::{Arc, RwLock};
use tonic::metadata::MetadataMap;

use crate::otel::config::{
    METRICS_READER_INTERVAL_SECONDS, OTEL_COLLECTOR_ENDPOINT, RESOURCE_ATTRIBUTES,
};
use crate::otel::runtime::tokio_runtime;

pub fn init_otel_metrics(metadata: MetadataMap) -> anyhow::Result<sdkmetrics::SdkMeterProvider> {
    let rt = tokio_runtime();

    let meter_provider = rt.block_on(async {
        let metrics_exporter = MetricExporter::builder()
            .with_tonic()
            .with_endpoint(OTEL_COLLECTOR_ENDPOINT.as_str())
            .with_metadata(metadata)
            .build()?;

        let reader = sdkmetrics::PeriodicReader::builder(metrics_exporter)
            .with_interval(std::time::Duration::from_secs(
                METRICS_READER_INTERVAL_SECONDS,
            ))
            .build();

        let resource = Resource::builder_empty()
            .with_attributes(RESOURCE_ATTRIBUTES.iter().cloned())
            .build();

        let meter_provider = SdkMeterProvider::builder()
            .with_resource(resource)
            .with_reader(reader)
            .build();

        Ok::<SdkMeterProvider, anyhow::Error>(meter_provider)
    })?;

    global::set_meter_provider(meter_provider.clone());

    Ok(meter_provider)
}

#[derive(Debug)]
pub struct PolicyEngineMetrics {
    meter_provider: SdkMeterProvider,
    pub decision_latency_ms: opentelemetry::metrics::Histogram<f64>,
}

impl PolicyEngineMetrics {
    pub fn new(meter_provider: SdkMeterProvider) -> Self {
        let meter: Meter = meter_provider.meter("policy-engine");

        Self {
            meter_provider,
            decision_latency_ms: meter
                .f64_histogram("policy_engine.decision_latency_ms")
                .with_description("Latency of policy decisions in milliseconds")
                .with_unit("ms")
                .build(),
        }
    }
}

pub fn init_otel_metrics_with_token(token: &str) -> anyhow::Result<sdkmetrics::SdkMeterProvider> {
    let mut metadata = MetadataMap::new();
    metadata.insert("authorization", format!("Bearer {}", token).parse()?);
    init_otel_metrics(metadata)
}

#[derive(Clone, Debug)]
pub struct MeterProviderManager {
    inner: Arc<RwLock<SdkMeterProvider>>, // current meter provider
}

impl MeterProviderManager {
    pub fn create_from_token(token: &str) -> anyhow::Result<Self> {
        let provider = init_otel_metrics_with_token(token)?;
        Ok(Self {
            inner: Arc::new(RwLock::new(provider)),
        })
    }
    pub fn get(&self) -> SdkMeterProvider {
        self.inner
            .read()
            .expect("Failed to acquire lock on SdkMeterProvider")
            .clone()
    }
    pub fn update_token(&self, token: &str) -> anyhow::Result<()> {
        let new_provider = init_otel_metrics_with_token(token)?;
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
