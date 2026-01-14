"""
Agent management endpoints for OpenFoundry API.

Provides endpoints for:
- Listing registered agents
- Getting agent details
- Agent health checks
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from openfoundry.core.protocols import AgentId

router = APIRouter()


class AgentResponse(BaseModel):
    """Agent information response."""

    agent_id: str
    name: str
    description: str
    module: str
    capabilities: list[str]
    healthy: bool = True


class AgentListResponse(BaseModel):
    """List of agents response."""

    agents: list[AgentResponse]
    total: int


class AgentHealthResponse(BaseModel):
    """Agent health check response."""

    agent_id: str
    healthy: bool
    message: str
    checks: dict[str, bool] = {}


@router.get("", response_model=AgentListResponse)
async def list_agents(
    request: Request,
    capability: str | None = None,
) -> AgentListResponse:
    """
    List all registered agents.

    Args:
        capability: Optional filter by capability
    """
    registry = request.app.state.agent_registry

    if capability:
        agents = registry.find_by_capability(capability)
    else:
        agents = registry.list_all()

    agent_responses = [
        AgentResponse(
            agent_id=agent.agent_id.value,
            name=agent.name,
            description=agent.description,
            module=agent.agent_id.module,
            capabilities=list(agent.capabilities),
        )
        for agent in agents
    ]

    return AgentListResponse(
        agents=agent_responses,
        total=len(agent_responses),
    )


@router.get("/capabilities")
async def list_capabilities(request: Request) -> dict[str, list[str]]:
    """
    List all available capabilities.
    """
    registry = request.app.state.agent_registry
    return {"capabilities": list(registry.list_capabilities())}


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    request: Request,
    agent_id: str,
) -> AgentResponse:
    """
    Get details for a specific agent.
    """
    registry = request.app.state.agent_registry

    # Parse agent ID
    parts = agent_id.split(".", 1)
    if len(parts) == 2:
        module, name = parts
        aid = AgentId(value=agent_id, module=module)
    else:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

    agent = registry.get(aid)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    return AgentResponse(
        agent_id=agent.agent_id.value,
        name=agent.name,
        description=agent.description,
        module=agent.agent_id.module,
        capabilities=list(agent.capabilities),
    )


@router.get("/{agent_id}/health", response_model=AgentHealthResponse)
async def check_agent_health(
    request: Request,
    agent_id: str,
) -> AgentHealthResponse:
    """
    Check health of a specific agent.
    """
    registry = request.app.state.agent_registry

    # Parse agent ID
    parts = agent_id.split(".", 1)
    if len(parts) == 2:
        module, name = parts
        aid = AgentId(value=agent_id, module=module)
    else:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

    agent = registry.get(aid)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    health = await agent.health_check()

    return AgentHealthResponse(
        agent_id=agent_id,
        healthy=health.healthy,
        message=health.message,
        checks=health.checks,
    )
