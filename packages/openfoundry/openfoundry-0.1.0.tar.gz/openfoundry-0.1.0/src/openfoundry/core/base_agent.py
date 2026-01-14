"""
Base agent implementation providing common functionality.

Agents can either inherit from BaseAgent or implement AgentProtocol directly.
BaseAgent provides lifecycle hooks, tool management, and execution scaffolding.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

import structlog

from openfoundry.core.protocols import (
    AgentId,
    Event,
    HealthStatus,
    TaskProtocol,
    TaskStatus,
    ToolProtocol,
)
from openfoundry.core.task import TaskResult

if TYPE_CHECKING:
    from openfoundry.core.context import Context


class BaseAgent(ABC):
    """
    Abstract base class for agents.

    Features:
    - Lifecycle hooks (pre/post execution)
    - Tool registration and management
    - Structured logging
    - Health checking
    - Error handling
    """

    MODULE: ClassVar[str] = "core"
    DEFAULT_MAX_ITERATIONS: ClassVar[int] = 10

    def __init__(
        self,
        name: str,
        description: str,
        capabilities: set[str] | None = None,
        tools: list[ToolProtocol] | None = None,
        max_iterations: int | None = None,
    ):
        self._name = name
        self._description = description
        self._capabilities = capabilities or set()
        self._tools: dict[str, ToolProtocol] = {}
        self._max_iterations = max_iterations or self.DEFAULT_MAX_ITERATIONS
        self._agent_id = AgentId.create(name, self.MODULE)
        self._logger = structlog.get_logger().bind(
            agent_id=self._agent_id.value,
            agent_name=self._name,
        )

        for tool in tools or []:
            self.register_tool(tool)

    @property
    def agent_id(self) -> AgentId:
        return self._agent_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def capabilities(self) -> set[str]:
        return self._capabilities

    @property
    def tools(self) -> dict[str, ToolProtocol]:
        return self._tools

    @property
    def max_iterations(self) -> int:
        return self._max_iterations

    def register_tool(self, tool: ToolProtocol) -> None:
        self._tools[tool.name] = tool
        self._logger.debug("tool_registered", tool_name=tool.name)

    def unregister_tool(self, tool_name: str) -> bool:
        if tool_name in self._tools:
            del self._tools[tool_name]
            self._logger.debug("tool_unregistered", tool_name=tool_name)
            return True
        return False

    def get_tool(self, tool_name: str) -> ToolProtocol | None:
        return self._tools.get(tool_name)

    async def can_handle(self, task: TaskProtocol) -> bool:
        return task.task_type in self._capabilities

    async def execute(
        self, task: TaskProtocol, context: Context
    ) -> TaskResult:
        self._logger.info(
            "executing_task",
            task_id=str(task.task_id),
            task_type=task.task_type,
        )

        start_time = time.perf_counter()

        try:
            await self._pre_execute(task, context)
            result = await self._execute_internal(task, context)
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            result.execution_time_ms = execution_time_ms
            await self._post_execute(task, result, context)

            self._logger.info(
                "task_completed",
                task_id=str(task.task_id),
                status=result.status.name,
                execution_time_ms=execution_time_ms,
            )

            return result

        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            self._logger.exception(
                "task_execution_failed",
                task_id=str(task.task_id),
                error=str(e),
            )

            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                output=None,
                error=str(e),
                agent_id=self._agent_id,
                execution_time_ms=execution_time_ms,
            )

            try:
                await self._post_execute(task, result, context)
            except Exception:
                pass

            return result

    @abstractmethod
    async def _execute_internal(
        self, task: TaskProtocol, context: Context
    ) -> TaskResult:
        ...

    async def _pre_execute(
        self, task: TaskProtocol, context: Context
    ) -> None:
        await context.emit_event(
            Event(
                event_type="agent.task.started",
                source=self._agent_id.value,
                data={
                    "task_id": str(task.task_id),
                    "task_type": task.task_type,
                },
                trace_id=context.trace_id,
            )
        )

    async def _post_execute(
        self, task: TaskProtocol, result: TaskResult, context: Context
    ) -> None:
        await context.emit_event(
            Event(
                event_type="agent.task.completed",
                source=self._agent_id.value,
                data={
                    "task_id": str(task.task_id),
                    "status": result.status.name,
                    "execution_time_ms": result.execution_time_ms,
                },
                trace_id=context.trace_id,
            )
        )

    async def health_check(self) -> HealthStatus:
        checks: dict[str, bool] = {"tools_available": len(self._tools) >= 0}
        additional = await self._additional_health_checks()
        checks.update(additional)
        all_healthy = all(checks.values())
        return HealthStatus(
            healthy=all_healthy,
            message="All checks passed" if all_healthy else "Some checks failed",
            checks=checks,
        )

    async def _additional_health_checks(self) -> dict[str, bool]:
        return {}

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema,
                },
            }
            for tool in self._tools.values()
        ]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"capabilities={self._capabilities!r})"
        )
