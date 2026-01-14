"""OpenTelemetry logging framework for sending logs to Loki via OTEL Collector.

This module provides a simple interface to set up OpenTelemetry logging
with OTLP export capabilities, allowing logs to be sent to Grafana Loki
through an OpenTelemetry Collector.

Example usage:
    ```python
    from agentica_internal.otel_logging import CustomLogFW
    import logging

    # Initialize the logging framework
    logFW = CustomLogFW(service_name='my-service', instance_id='instance-1')
    handler = logFW.setup_logging()
    logging.getLogger().addHandler(handler)

    # Now all logs will be sent via OTLP
    logging.info("This log will be sent to Loki via OTEL Collector")
    ```
"""

import logging
import os

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

# TODO: move this file into telemetry/


class CustomLogFW:
    """
    CustomLogFW sets up logging using OpenTelemetry with a specified service name and instance ID.

    This class configures the OpenTelemetry logging pipeline to send logs to an OTLP endpoint
    (typically an OpenTelemetry Collector) which can then forward them to Loki or other backends.

    Attributes:
        logger_provider: The OpenTelemetry LoggerProvider instance configured with resource attributes.
    """

    def __init__(
        self,
        service_name: str,
        instance_id: str,
        endpoint: str | None = None,
        insecure: bool = True,
        organization_id: str | None = None,
    ):
        """
        Initialize the CustomLogFW with a service name and instance ID.

        Args:
            service_name: Name of the service for logging purposes (e.g., "session-manager").
            instance_id: Unique instance ID of the service (e.g., container ID, hostname).
            endpoint: OTLP endpoint URL (default: reads from OTEL_EXPORTER_OTLP_ENDPOINT env var
                     or falls back to "otel-collector:4317").
            insecure: Whether to use an insecure connection (no TLS). Default is True for
                     local development.
            organization_id: Organization ID for multi-tenant backends. Will be sent as
                     x-scope-orgid header to Loki/Tempo.
        """
        self.service_name = service_name
        self.instance_id = instance_id
        self.organization_id = organization_id

        # Determine endpoint
        if endpoint is None:
            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "otel-collector:4317")

        self.endpoint = endpoint
        self.insecure = insecure

        # Create an instance of LoggerProvider with a Resource object that includes
        # service name and instance ID, identifying the source of the logs.
        self.logger_provider = LoggerProvider(
            resource=Resource.create(
                {
                    "service.name": service_name,
                    "service.instance.id": instance_id,
                    # Add deployment environment if available
                    "deployment.environment": os.getenv("ENVIRONMENT", "local"),
                }
            )
        )

    def setup_logging(self) -> LoggingHandler:
        """
        Set up the logging configuration with OTLP export.

        This method:
        1. Sets the global logger provider
        2. Creates an OTLP log exporter
        3. Adds a batch processor to the logger provider
        4. Returns a LoggingHandler that can be added to Python's logging system

        Returns:
            LoggingHandler instance configured with the logger provider.

        Example:
            ```python
            logFW = CustomLogFW(service_name='my-app', instance_id='1')
            handler = logFW.setup_logging()
            logging.getLogger().addHandler(handler)
            ```
        """
        try:
            # Set the created LoggerProvider as the global logger provider.
            set_logger_provider(self.logger_provider)

            # Create an instance of OTLPLogExporter with the configured endpoint.
            # Include x-scope-orgid header for multi-tenant Loki
            headers = {}
            if self.organization_id:
                headers["x-scope-orgid"] = self.organization_id
                logger.info(f"Setting x-scope-orgid header for logs to: {self.organization_id}")
            else:
                logger.warning(
                    "No organization_id provided! Logs will not be queryable by X-Scope-OrgID."
                )

            exporter = OTLPLogExporter(
                endpoint=self.endpoint,
                insecure=self.insecure,
                headers=headers if headers else None,
            )

            # Add a BatchLogRecordProcessor to the logger provider with the exporter.
            # This batches log records for better performance.
            self.logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

            # Create a LoggingHandler with the specified logger provider and log level set to NOTSET.
            # NOTSET means it will capture all log levels (the level filtering happens elsewhere).
            handler = LoggingHandler(
                level=logging.NOTSET,
                logger_provider=self.logger_provider,
            )

            logger.info(
                f"OpenTelemetry logging initialized: service={self.service_name}, "
                f"instance={self.instance_id}, endpoint={self.endpoint}"
            )

            return handler

        except Exception as e:
            logger.error(f"Failed to set up OpenTelemetry logging: {e}")
            logger.warning("Logs will not be sent via OTLP")
            # Return a NullHandler to prevent breaking the application
            return logging.NullHandler()


def setup_otel_logging(
    service_name: str,
    instance_id: str,
    endpoint: str | None = None,
    log_level: int = logging.INFO,
    organization_id: str | None = None,
) -> LoggingHandler:
    """
    Convenience function to quickly set up OTEL logging and add to root logger.

    This is a higher-level wrapper around CustomLogFW that handles the common
    case of adding OTEL logging to the root logger.

    Args:
        service_name: Name of the service for logging purposes.
        instance_id: Unique instance ID of the service.
        endpoint: OTLP endpoint URL (optional, uses env var or default).
        log_level: Logging level for the handler (default: INFO).
        organization_id: Organization ID for multi-tenant backends (optional).

    Returns:
        The LoggingHandler that was created and added to the root logger.

    Example:
        ```python
        from agentica_internal.otel_logging import setup_otel_logging

        # Quick setup - adds to root logger automatically
        setup_otel_logging(service_name='my-service', instance_id='1')

        # Now just use normal logging
        import logging
        logging.info("This goes to Loki!")
        ```
    """
    logFW = CustomLogFW(
        service_name=service_name,
        instance_id=instance_id,
        endpoint=endpoint,
        organization_id=organization_id,
    )
    handler = logFW.setup_logging()
    handler.setLevel(log_level)

    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    return handler
