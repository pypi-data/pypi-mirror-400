use crate::otel::logs::LoggerProviderManager;
use crate::otel::metrics::MeterProviderManager;
use crate::otel::traces::TracerProviderManager;
use opentelemetry_sdk::logs;
use opentelemetry_sdk::metrics::SdkMeterProvider;
use opentelemetry_sdk::trace::SdkTracerProvider;

/// OtelManager owns tracer, logger, and meter providers and can refresh them when the API token changes.
#[derive(Clone, Debug)]
pub struct OtelManager {
    tracer: TracerProviderManager,
    logger: LoggerProviderManager,
    meter: MeterProviderManager,
}

impl OtelManager {
    /// Construct a manager with initial providers created from a token.
    pub fn create_from_token(initial_token: &str) -> anyhow::Result<Self> {
        let tracer = TracerProviderManager::create_from_token(initial_token)?;
        let logger = LoggerProviderManager::create_from_token(initial_token)?;
        let meter = MeterProviderManager::create_from_token(initial_token)?;

        Ok(Self {
            tracer,
            logger,
            meter,
        })
    }

    /// Getters (cloned providers)
    pub fn tracer_provider(&self) -> SdkTracerProvider {
        self.tracer.get()
    }
    pub fn logger_provider(&self) -> logs::SdkLoggerProvider {
        self.logger.get()
    }
    pub fn meter_provider(&self) -> SdkMeterProvider {
        self.meter.get()
    }

    /// Update token by rebuilding all providers with new metadata.
    /// Old providers are shut down to flush pending telemetry.
    pub fn update_token(&self, new_token: &str) -> anyhow::Result<()> {
        self.tracer.update_token(new_token)?;
        self.logger.update_token(new_token)?;
        self.meter.update_token(new_token)?;
        Ok(())
    }

    pub fn shutdown(&self) {
        self.tracer.shutdown();
        self.logger.shutdown();
        self.meter.shutdown();
    }
}
