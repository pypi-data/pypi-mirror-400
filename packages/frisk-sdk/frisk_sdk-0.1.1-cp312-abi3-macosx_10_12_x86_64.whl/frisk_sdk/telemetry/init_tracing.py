from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def init_tracing(access_token: str):
    provider = TracerProvider()
    span_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",  # same as Rust # todo: Config value. https://linear.app/friskai/issue/POL-55/add-config-library-to-sdk
        insecure=True,  # no TLS for local dev
        headers={"authorization": "Bearer " + access_token},
    )
    span_processor = BatchSpanProcessor(span_exporter)
    provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)
    return provider
