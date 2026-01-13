use opentelemetry::KeyValue;
use std::sync::LazyLock;
use tonic::metadata::{Ascii, MetadataMap, MetadataValue};

// Lazily initialized resource attributes (avoid const fn restriction in statics)
pub static RESOURCE_ATTRIBUTES: LazyLock<[KeyValue; 3]> = LazyLock::new(|| {
    [
        KeyValue::new("service.name", "policy-engine"),
        KeyValue::new("service.namespace", "frisk"),
        KeyValue::new("service.instance.id", "policy-engine-1"),
    ]
});
pub static OTEL_COLLECTOR_ENDPOINT: LazyLock<String> =
    LazyLock::new(|| "http://localhost:4317".into());
pub static METRICS_READER_INTERVAL_SECONDS: u64 = 5;

pub fn otlp_metadata(access_token: &str) -> MetadataMap {
    let mut meta = MetadataMap::new();
    let val = format!("Bearer {}", access_token);
    if let Ok(hv) = MetadataValue::<Ascii>::try_from(val) {
        meta.insert("authorization", hv);
    }
    meta
}
