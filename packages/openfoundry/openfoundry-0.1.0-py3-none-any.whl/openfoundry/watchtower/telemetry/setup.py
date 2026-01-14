"""
Telemetry setup for OpenTelemetry integration.

Configures distributed tracing, metrics, and logging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from openfoundry.config import TelemetrySettings


def setup_telemetry(settings: TelemetrySettings | None = None) -> None:
    """
    Configure OpenTelemetry for the application.

    Sets up:
    - Distributed tracing with OTLP export
    - Metrics collection
    - Structured logging

    Args:
        settings: Telemetry configuration settings
    """
    if settings is None:
        from openfoundry.config import get_settings
        settings = get_settings().telemetry

    if not settings.enabled:
        structlog.get_logger().info("telemetry_disabled")
        return

    # Setup structured logging
    from openfoundry.watchtower.telemetry.logging import setup_logging
    setup_logging(settings)

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        # Create resource
        resource = Resource.create({
            SERVICE_NAME: settings.service_name,
            SERVICE_VERSION: settings.service_version,
        })

        # Setup tracer provider
        tracer_provider = TracerProvider(resource=resource)

        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.otlp_endpoint,
            insecure=settings.otlp_insecure,
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)

        structlog.get_logger().info(
            "telemetry_configured",
            otlp_endpoint=settings.otlp_endpoint,
            service_name=settings.service_name,
        )

    except ImportError:
        structlog.get_logger().warning(
            "opentelemetry_not_installed",
            message="Install opentelemetry packages for full observability",
        )
    except Exception as e:
        structlog.get_logger().error(
            "telemetry_setup_failed",
            error=str(e),
        )


def get_tracer(name: str = "openfoundry"):
    """
    Get an OpenTelemetry tracer.

    Args:
        name: Tracer name (usually module name)

    Returns:
        Tracer instance
    """
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        # Return a no-op tracer
        return NoOpTracer()


class NoOpTracer:
    """No-op tracer for when OpenTelemetry is not installed."""

    def start_span(self, name: str, **kwargs):
        return NoOpSpan()

    def start_as_current_span(self, name: str, **kwargs):
        return NoOpSpanContext()


class NoOpSpan:
    """No-op span."""

    def end(self):
        pass

    def set_attribute(self, key: str, value):
        pass

    def add_event(self, name: str, attributes=None):
        pass


class NoOpSpanContext:
    """Context manager for no-op spans."""

    def __enter__(self):
        return NoOpSpan()

    def __exit__(self, *args):
        pass
