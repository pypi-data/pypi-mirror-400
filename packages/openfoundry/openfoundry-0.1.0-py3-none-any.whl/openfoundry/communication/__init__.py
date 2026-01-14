"""
Communication layer for OpenFoundry.

Provides HTTP (FastAPI) and gRPC interfaces for:
- External API access
- Inter-agent communication
- Service discovery
"""

from openfoundry.communication.http.app import create_app

__all__ = [
    "create_app",
]
