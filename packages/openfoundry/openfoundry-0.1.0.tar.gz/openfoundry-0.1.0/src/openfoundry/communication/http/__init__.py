"""
HTTP API layer using FastAPI.

Provides REST endpoints for:
- Task submission and management
- Agent registry queries
- Workflow execution
- Health and metrics
"""

from openfoundry.communication.http.app import create_app

__all__ = ["create_app"]
