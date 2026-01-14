"""
Agent registry for agent discovery and management.

The registry maintains a catalog of available agents and provides
lookup by ID or capability matching.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import structlog

from openfoundry.core.protocols import AgentId, AgentProtocol, HealthStatus, TaskProtocol


@dataclass
class AgentInfo:
    """Information about a registered agent."""

    agent: AgentProtocol
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    endpoint: str | None = None
    last_health_check: HealthStatus | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """
    Central registry for agent discovery and management.

    Features:
    - Register/unregister agents
    - Lookup by ID or capabilities
    - Health monitoring
    """

    def __init__(self) -> None:
        self._agents: dict[str, AgentInfo] = {}
        self._capability_index: dict[str, set[str]] = {}
        self._logger = structlog.get_logger().bind(component="agent_registry")
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the registry."""
        self._logger.info("initializing_registry")
        self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown the registry."""
        self._logger.info("shutting_down_registry", agent_count=len(self._agents))
        self._agents.clear()
        self._capability_index.clear()
        self._initialized = False

    def register(
        self,
        agent: AgentProtocol,
        endpoint: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register an agent with the registry."""
        agent_id = agent.agent_id.value

        if agent_id in self._agents:
            self._logger.warning("agent_already_registered", agent_id=agent_id)
            return

        self._agents[agent_id] = AgentInfo(
            agent=agent,
            endpoint=endpoint,
            metadata=metadata or {},
        )

        for capability in agent.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(agent_id)

        self._logger.info(
            "agent_registered",
            agent_id=agent_id,
            capabilities=list(agent.capabilities),
            endpoint=endpoint,
        )

    def unregister(self, agent_id: AgentId) -> bool:
        """Unregister an agent."""
        agent_id_str = agent_id.value

        if agent_id_str not in self._agents:
            return False

        agent_info = self._agents[agent_id_str]

        for capability in agent_info.agent.capabilities:
            if capability in self._capability_index:
                self._capability_index[capability].discard(agent_id_str)
                if not self._capability_index[capability]:
                    del self._capability_index[capability]

        del self._agents[agent_id_str]
        self._logger.info("agent_unregistered", agent_id=agent_id_str)
        return True

    def get(self, agent_id: AgentId) -> AgentProtocol | None:
        """Get an agent by ID."""
        info = self._agents.get(agent_id.value)
        return info.agent if info else None

    def get_info(self, agent_id: AgentId) -> AgentInfo | None:
        """Get agent info by ID."""
        return self._agents.get(agent_id.value)

    def find_by_capability(self, capability: str) -> list[AgentProtocol]:
        """Find all agents with a specific capability."""
        agent_ids = self._capability_index.get(capability, set())
        return [
            self._agents[aid].agent
            for aid in agent_ids
            if aid in self._agents
        ]

    async def find_for_task(self, task: TaskProtocol) -> list[AgentProtocol]:
        """Find agents that can handle a specific task."""
        candidates = self.find_by_capability(task.task_type)
        handlers = []
        for agent in candidates:
            try:
                if await agent.can_handle(task):
                    handlers.append(agent)
            except Exception as e:
                self._logger.warning(
                    "can_handle_check_failed",
                    agent_id=agent.agent_id.value,
                    error=str(e),
                )
        return handlers

    def list_all(self) -> list[AgentProtocol]:
        """List all registered agents."""
        return [info.agent for info in self._agents.values()]

    def list_capabilities(self) -> set[str]:
        """List all available capabilities."""
        return set(self._capability_index.keys())

    @property
    def count(self) -> int:
        """Number of registered agents."""
        return len(self._agents)

    @property
    def is_initialized(self) -> bool:
        """Whether registry has been initialized."""
        return self._initialized

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, agent_id: AgentId) -> bool:
        return agent_id.value in self._agents
