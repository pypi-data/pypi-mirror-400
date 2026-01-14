"""
Central coordinator for multi-agent orchestration.

The Coordinator manages:
- Task routing and dispatching
- Agent selection based on capabilities
- Load balancing across agents
- Failure handling and retries
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import structlog

from openfoundry.config import Settings
from openfoundry.core.agent_registry import AgentRegistry
from openfoundry.core.context import Context, ContextBuilder
from openfoundry.core.protocols import (
    AgentProtocol,
    Event,
    LLMProviderProtocol,
    StateProtocol,
    TaskProtocol,
)
from openfoundry.core.task import TaskResult


@dataclass
class ExecutionStats:
    """Statistics for task execution."""

    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time_ms: float = 0.0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    @property
    def average_execution_time_ms(self) -> float:
        """Calculate average execution time."""
        if self.completed_tasks == 0:
            return 0.0
        return self.total_execution_time_ms / self.completed_tasks


class Coordinator:
    """
    Central coordinator for multi-agent orchestration.

    Responsibilities:
    - Accept tasks and route to appropriate agents
    - Manage execution context and state
    - Handle retries and failure recovery
    - Emit events for observability

    Example:
        coordinator = Coordinator(
            registry=agent_registry,
            llm=llm_provider,
            state=state_store,
        )

        result = await coordinator.execute(task)
    """

    def __init__(
        self,
        registry: AgentRegistry,
        llm: LLMProviderProtocol,
        state: StateProtocol,
        settings: Settings | None = None,
    ):
        """
        Initialize the coordinator.

        Args:
            registry: Agent registry for agent lookup
            llm: LLM provider for agent use
            state: State store for persistence
            settings: Optional configuration settings
        """
        self.registry = registry
        self.llm = llm
        self.state = state
        self.settings = settings
        self._logger = structlog.get_logger().bind(component="coordinator")
        self._stats = ExecutionStats()
        self._event_handlers: list[Any] = []

    @property
    def stats(self) -> ExecutionStats:
        """Get execution statistics."""
        return self._stats

    def add_event_handler(self, handler) -> None:
        """Add an event handler for observability."""
        self._event_handlers.append(handler)

    async def execute(
        self,
        task: TaskProtocol,
        agent: AgentProtocol | None = None,
    ) -> TaskResult:
        """
        Execute a task using the appropriate agent.

        Args:
            task: Task to execute
            agent: Optional specific agent to use

        Returns:
            TaskResult from execution

        Raises:
            ValueError: If no suitable agent found
        """
        self._stats.total_tasks += 1

        self._logger.info(
            "executing_task",
            task_id=str(task.task_id),
            task_type=task.task_type,
        )

        # Find agent if not specified
        if agent is None:
            agent = await self._select_agent(task)

        if agent is None:
            self._stats.failed_tasks += 1
            return TaskResult.failure(
                task_id=task.task_id,
                error=f"No agent found for task type: {task.task_type}",
            )

        # Build execution context
        context = self._build_context(task, agent)

        # Execute with retries
        result = await self._execute_with_retries(task, agent, context)

        # Update stats
        if result.is_success:
            self._stats.completed_tasks += 1
            self._stats.total_execution_time_ms += result.execution_time_ms
        else:
            self._stats.failed_tasks += 1

        return result

    async def execute_batch(
        self,
        tasks: list[TaskProtocol],
        parallel: bool = True,
    ) -> list[TaskResult]:
        """
        Execute multiple tasks.

        Args:
            tasks: List of tasks to execute
            parallel: Whether to execute in parallel

        Returns:
            List of task results
        """
        if parallel:
            return await asyncio.gather(
                *[self.execute(task) for task in tasks],
                return_exceptions=False,
            )
        else:
            results = []
            for task in tasks:
                result = await self.execute(task)
                results.append(result)
            return results

    async def _select_agent(self, task: TaskProtocol) -> AgentProtocol | None:
        """
        Select the best agent for a task.

        Uses capability matching and load balancing.
        """
        handlers = await self.registry.find_for_task(task)

        if not handlers:
            self._logger.warning(
                "no_agent_found",
                task_type=task.task_type,
            )
            return None

        # For now, use first available handler
        # TODO: Implement load balancing
        return handlers[0]

    def _build_context(
        self,
        task: TaskProtocol,
        agent: AgentProtocol,
    ) -> Context:
        """Build execution context for a task."""
        context = (
            ContextBuilder()
            .with_llm(self.llm)
            .with_state(self.state)
            .with_registry(self.registry)
            .with_metadata(
                task_id=str(task.task_id),
                task_type=task.task_type,
                agent_id=agent.agent_id.value,
            )
            .build()
        )

        # Add event handlers
        for handler in self._event_handlers:
            context.add_event_handler(handler)

        return context

    async def _execute_with_retries(
        self,
        task: TaskProtocol,
        agent: AgentProtocol,
        context: Context,
    ) -> TaskResult:
        """Execute task with retry logic."""
        max_retries = task.metadata.max_retries
        last_error: str | None = None

        for attempt in range(max_retries + 1):
            try:
                # Emit start event
                await context.emit_event(
                    Event(
                        event_type="coordinator.task.attempt",
                        source="coordinator",
                        data={
                            "task_id": str(task.task_id),
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                        },
                        trace_id=context.trace_id,
                    )
                )

                # Execute with timeout
                result = await asyncio.wait_for(
                    agent.execute(task, context),
                    timeout=task.metadata.timeout_seconds,
                )

                if result.is_success:
                    return result

                # Task failed, maybe retry
                last_error = result.error
                if attempt < max_retries:
                    self._logger.warning(
                        "task_failed_retrying",
                        task_id=str(task.task_id),
                        attempt=attempt + 1,
                        error=last_error,
                    )
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return result

            except asyncio.TimeoutError:
                last_error = f"Task timed out after {task.metadata.timeout_seconds}s"
                self._logger.warning(
                    "task_timeout",
                    task_id=str(task.task_id),
                    attempt=attempt + 1,
                )
                if attempt >= max_retries:
                    return TaskResult.failure(
                        task_id=task.task_id,
                        error=last_error,
                        agent_id=agent.agent_id,
                    )

            except Exception as e:
                last_error = str(e)
                self._logger.exception(
                    "task_exception",
                    task_id=str(task.task_id),
                    attempt=attempt + 1,
                )
                if attempt >= max_retries:
                    return TaskResult.failure(
                        task_id=task.task_id,
                        error=last_error,
                        agent_id=agent.agent_id,
                    )

        return TaskResult.failure(
            task_id=task.task_id,
            error=last_error or "Unknown error after retries",
            agent_id=agent.agent_id,
        )

    async def shutdown(self) -> None:
        """Shutdown the coordinator gracefully."""
        self._logger.info(
            "coordinator_shutdown",
            stats={
                "total_tasks": self._stats.total_tasks,
                "completed_tasks": self._stats.completed_tasks,
                "failed_tasks": self._stats.failed_tasks,
                "success_rate": self._stats.success_rate,
            },
        )
