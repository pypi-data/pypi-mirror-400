"""
Telemetry module for observability.
"""

from openfoundry.watchtower.telemetry.setup import setup_telemetry
from openfoundry.watchtower.telemetry.metrics import MetricsCollector
from openfoundry.watchtower.telemetry.logging import setup_logging

__all__ = [
    "setup_telemetry",
    "MetricsCollector",
    "setup_logging",
]
