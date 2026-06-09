"""OpenTelemetry and Prometheus instrumentation setup."""

from typing import TYPE_CHECKING

from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.logging.setup import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = get_logger(__name__)


def setup_telemetry(app: "FastAPI", settings: Settings) -> None:
    """Configure OpenTelemetry tracing and Prometheus metrics."""
    if settings.prometheus_enabled:
        _setup_prometheus(app)

    if settings.otel_enabled:
        _setup_opentelemetry(app, settings)


def _setup_prometheus(app: "FastAPI") -> None:
    """Instrument FastAPI with Prometheus metrics."""
    from prometheus_fastapi_instrumentator import Instrumentator

    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/health", "/metrics"],
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    logger.info("prometheus_instrumentation_enabled")


def _setup_opentelemetry(app: "FastAPI", settings: Settings) -> None:
    """Configure OpenTelemetry distributed tracing."""
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": "0.1.0",
            "deployment.environment": settings.app_env,
        }
    )

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    logger.info(
        "opentelemetry_instrumentation_enabled",
        endpoint=settings.otel_exporter_otlp_endpoint,
    )
