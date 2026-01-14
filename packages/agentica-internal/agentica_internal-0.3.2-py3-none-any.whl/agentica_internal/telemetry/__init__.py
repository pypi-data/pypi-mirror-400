"""
Telemetry module for OpenTelemetry tracing and logging.
"""

from .otel import get_tracer
from .otel_config import initialize_tracing

__all__ = ['initialize_tracing', 'get_tracer']
