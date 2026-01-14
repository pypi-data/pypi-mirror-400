"""
The Watchtower - Monitoring & Self-Healing Module.

Provides observability and incident response:
- OpenTelemetry integration
- Prometheus metrics
- Structured logging
- Automated incident response
"""

from openfoundry.watchtower.telemetry.setup import setup_telemetry
from openfoundry.watchtower.telemetry.metrics import MetricsCollector

__all__ = [
    "setup_telemetry",
    "MetricsCollector",
]
