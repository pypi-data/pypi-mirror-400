"""
Health check endpoints for OpenFoundry API.

Provides liveness and readiness probes for Kubernetes
and general health monitoring.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str
    checks: dict[str, bool] = {}


class ReadinessResponse(BaseModel):
    """Readiness check response."""

    ready: bool
    checks: dict[str, Any] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns 200 if the service is running.
    Used as a liveness probe.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(request: Request) -> ReadinessResponse:
    """
    Readiness check endpoint.

    Verifies all dependencies are available.
    Used as a readiness probe.
    """
    checks: dict[str, Any] = {}

    # Check agent registry
    if hasattr(request.app.state, "agent_registry"):
        registry = request.app.state.agent_registry
        checks["agent_registry"] = {
            "initialized": registry.is_initialized,
            "agent_count": registry.count,
        }

    # Check state store
    if hasattr(request.app.state, "state_store"):
        try:
            await request.app.state.state_store.set("_health_check", "ok", ttl_seconds=10)
            checks["state_store"] = True
        except Exception as e:
            checks["state_store"] = {"error": str(e)}

    ready = all(
        (isinstance(v, bool) and v) or (isinstance(v, dict) and v.get("initialized", True))
        for v in checks.values()
    )

    return ReadinessResponse(ready=ready, checks=checks)


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Simple liveness check.

    Returns 200 if the process is alive.
    """
    return {"status": "alive"}
