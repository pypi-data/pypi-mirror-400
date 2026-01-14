"""
Execution context for agent task execution.

The Context provides access to shared resources like state, LLM providers,
and other agents during task execution.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from openfoundry.core.protocols import AgentId, Event, StateProtocol, TaskProtocol
from openfoundry.core.task import TaskResult

if TYPE_CHECKING:
    from openfoundry.core.protocols import AgentProtocol, LLMProviderProtocol


@dataclass
class Context:
    """
    Execution context passed to agents during task execution.

    Provides access to:
    - Distributed state (Redis, in-memory, etc.)
    - LLM providers for AI completions
    - Other agents for task delegation
    - Event emission for observability
    """

    trace_id: str
    state: StateProtocol
    llm: LLMProviderProtocol
    _agents: dict[str, AgentProtocol] = field(default_factory=dict)
    _events: list[Event] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        state: StateProtocol,
        llm: LLMProviderProtocol,
        trace_id: str | None = None,
    ) -> Context:
        """Create a new execution context with optional trace ID."""
        return cls(
            trace_id=trace_id or str(uuid.uuid4()),
            state=state,
            llm=llm,
        )

    def get_agent(self, agent_id: AgentId) -> AgentProtocol | None:
        """Get another agent by ID for delegation."""
        return self._agents.get(agent_id.value)

    def register_agent(self, agent: AgentProtocol) -> None:
        """Register an agent in the context for delegation."""
        self._agents[agent.agent_id.value] = agent

    async def emit_event(self, event: Event) -> None:
        """Emit an event for observability."""
        self._events.append(event)

    async def delegate(
        self, agent_id: AgentId, task: TaskProtocol
    ) -> TaskResult:
        """Delegate a task to another agent."""
        agent = self.get_agent(agent_id)
        if agent is None:
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"Agent not found: {agent_id}",
            )
        return await agent.execute(task, self)

    @property
    def events(self) -> list[Event]:
        """Get all emitted events."""
        return self._events.copy()


class ContextBuilder:
    """Fluent builder for creating Context instances."""

    def __init__(self) -> None:
        self._trace_id: str | None = None
        self._state: StateProtocol | None = None
        self._llm: LLMProviderProtocol | None = None
        self._agents: list[AgentProtocol] = []

    def with_trace_id(self, trace_id: str) -> ContextBuilder:
        """Set the trace ID for distributed tracing."""
        self._trace_id = trace_id
        return self

    def with_state(self, state: StateProtocol) -> ContextBuilder:
        """Set the state provider."""
        self._state = state
        return self

    def with_llm(self, llm: LLMProviderProtocol) -> ContextBuilder:
        """Set the LLM provider."""
        self._llm = llm
        return self

    def with_agent(self, agent: AgentProtocol) -> ContextBuilder:
        """Add an agent for delegation."""
        self._agents.append(agent)
        return self

    def build(self) -> Context:
        """Build the context. Raises ValueError if required fields missing."""
        if self._state is None:
            raise ValueError("State is required")
        if self._llm is None:
            raise ValueError("LLM provider is required")

        ctx = Context.create(
            state=self._state,
            llm=self._llm,
            trace_id=self._trace_id,
        )

        for agent in self._agents:
            ctx.register_agent(agent)

        return ctx
