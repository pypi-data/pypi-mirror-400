"""OpenTelemetry configuration for distributed tracing."""

import logging
import os
from typing import TYPE_CHECKING

_initialized = False

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import TracerProvider


def initialize_tracing(
    service_name: str,
    environment: str | None = None,
    tempo_endpoint: str | None = None,
    organization_id: str | None = None,
    log_level: str = 'INFO',
    instrument_httpx: bool = False,
) -> 'TracerProvider':
    """Initialize OpenTelemetry tracing with Tempo backend.

    This unified function supports all features from both session_manager and customer_sdk:
    - Optional organization_id for multi-tenant tracing (session_manager feature)
    - Optional httpx auto-instrumentation (customer_sdk feature)
    - Configurable logging level
    - Graceful handling when no endpoint is configured (allows distributed tracing headers)

    Args:
        service_name: Name of the service for traces
        environment: Environment name (e.g., "production", "staging", "local")
                    If None, reads from ENVIRONMENT env var (default: "local")
        tempo_endpoint: Tempo OTLP gRPC endpoint (e.g., "http://localhost:4317")
                       If None, reads from OTEL_EXPORTER_OTLP_ENDPOINT env var
                       If env var is not set, traces will not be exported but trace context
                       headers will still be propagated for distributed tracing
        organization_id: Organization ID that will be sent to the OTel collector as
                        x-scope-orgid header (for multi-tenant setups)
        log_level: Logging level for the otel_config logger (default: 'INFO')
        instrument_httpx: Whether to auto-instrument httpx for HTTP request tracing (default: False)

    Returns:
        TracerProvider instance
    """

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    # Create logger for this module
    logger = logging.getLogger('agentica_internal.telemetry.otel_config')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    global _initialized
    if _initialized:
        logger.warning("OpenTelemetry tracing already initialized, skipping")
        return trace.get_tracer_provider()  # type: ignore

    # Determine environment
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "local")

    # Determine Tempo endpoint
    if tempo_endpoint is None:
        tempo_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if not tempo_endpoint and environment != 'local':
            logger.debug(
                "OTEL_EXPORTER_OTLP_ENDPOINT not set - spans will not be exported "
                "(trace context headers will still work for distributed tracing)"
            )
            tempo_endpoint = None

    # Create resource with service metadata
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": os.getenv("SERVICE_VERSION", "0.2.0"),
            "deployment.environment": environment,
        }
    )

    # Create tracer provider with resource
    tracer_provider = TracerProvider(resource=resource)

    # Add OTLP exporter only if endpoint is configured
    if tempo_endpoint:
        try:
            headers = {}
            if organization_id:
                headers["x-scope-orgid"] = organization_id
                logger.info(f"Setting x-scope-orgid header to: {organization_id}")
            else:
                logger.warning(
                    "No organization_id provided - traces will not include x-scope-orgid header"
                )

            otlp_exporter = OTLPSpanExporter(
                endpoint=tempo_endpoint,
                insecure=True,  # Set to False if using TLS
                headers=headers if headers else None,
            )
            logger.debug(f"OTLP exporter created with endpoint: {tempo_endpoint}")

            # Use BatchSpanProcessor with tuned settings for better span ordering
            # Longer delay allows child spans to arrive before parents export
            batch_processor = BatchSpanProcessor(
                otlp_exporter,
                max_queue_size=2048,  # Larger queue to hold spans (default: 2048)
                schedule_delay_millis=2500,  # Export every 2.5 seconds
                export_timeout_millis=30000,  # 30s timeout (default: 30000)
                max_export_batch_size=512,  # Batch size (default: 512)
            )
            tracer_provider.add_span_processor(batch_processor)
            logger.debug(
                f"OpenTelemetry: OTLP exporter configured for {tempo_endpoint} (export every 2.5s)"
            )
        except Exception as e:
            logger.error(f"Failed to initialize OTLP exporter: {e}")
            logger.warning("Traces will not be sent to backend")

    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Auto-instrument httpx if requested (customer_sdk feature)
    if instrument_httpx:
        try:
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

            HTTPXClientInstrumentor().instrument()
            logger.debug("OpenTelemetry: httpx auto-instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to instrument httpx: {e}")

    _initialized = True
    logger.debug(
        f"OpenTelemetry tracing initialized: service={service_name}, "
        f"environment={environment}, endpoint={tempo_endpoint}, organization_id={organization_id}"
    )

    return tracer_provider
