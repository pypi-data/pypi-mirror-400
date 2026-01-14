"""
FastAPI application factory for OpenFoundry HTTP API.

Creates a fully configured FastAPI application with:
- CORS middleware
- Rate limiting
- OpenTelemetry instrumentation
- API routes for agents, tasks, workflows
"""

from __future__ import annotations

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from openfoundry.config import Settings, get_settings
from openfoundry.core.agent_registry import AgentRegistry


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"

        # Clean old requests
        current_time = time.time()
        cutoff = current_time - self.window_size
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > cutoff
        ]

        # Check rate limit
        if len(self._requests[client_ip]) >= self.requests_per_minute:
            return Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )

        # Record request
        self._requests[client_ip].append(current_time)

        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager for startup/shutdown.

    Handles initialization of:
    - Agent registry
    - State stores
    """
    settings: Settings = app.state.settings

    # Startup
    app.state.agent_registry = AgentRegistry()
    await app.state.agent_registry.initialize()

    # Initialize state store based on settings
    app.state.state_store = await _create_state_store(settings)

    yield

    # Shutdown
    await app.state.agent_registry.shutdown()
    if hasattr(app.state, "state_store") and app.state.state_store:
        await app.state.state_store.close()


async def _create_state_store(settings: Settings):
    """Create state store based on configuration."""
    from openfoundry.communication.http.state import InMemoryState, RedisState

    if settings.state.backend == "redis":
        store = RedisState(settings.state.redis_url)
        await store.connect()
        return store
    return InMemoryState()


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Application factory for creating FastAPI instances.

    Args:
        settings: Configuration settings. If None, loads from environment.

    Returns:
        Configured FastAPI application.
    """
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="OpenFoundry API",
        description="Multi-Agent Orchestration Framework API",
        version="1.0.0",
        docs_url="/docs" if settings.api.enable_docs else None,
        redoc_url="/redoc" if settings.api.enable_docs else None,
        openapi_url="/openapi.json" if settings.api.enable_docs else None,
        lifespan=lifespan,
    )

    # Store settings in app state
    app.state.settings = settings

    # CORS middleware
    if settings.api.cors.enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.api.cors.allowed_origins,
            allow_credentials=settings.api.cors.allow_credentials,
            allow_methods=settings.api.cors.allowed_methods,
            allow_headers=settings.api.cors.allowed_headers,
        )

    # Rate limiting middleware
    if settings.api.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=settings.api.rate_limit_per_minute,
        )

    # Include routers
    from openfoundry.communication.http.routes import (
        agents,
        health,
        tasks,
        workflows,
    )

    app.include_router(health.router, tags=["Health"])
    app.include_router(
        agents.router,
        prefix=f"{settings.api.api_prefix}/agents",
        tags=["Agents"],
    )
    app.include_router(
        tasks.router,
        prefix=f"{settings.api.api_prefix}/tasks",
        tags=["Tasks"],
    )
    app.include_router(
        workflows.router,
        prefix=f"{settings.api.api_prefix}/workflows",
        tags=["Workflows"],
    )

    return app


def get_application() -> FastAPI:
    """Get the default application instance."""
    return create_app()
