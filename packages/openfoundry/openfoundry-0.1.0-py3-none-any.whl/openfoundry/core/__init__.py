"""Core module - foundational abstractions for OpenFoundry."""

from openfoundry.core.base_agent import BaseAgent
from openfoundry.core.context import Context, ContextBuilder
from openfoundry.core.protocols import (
    AgentId,
    AgentProtocol,
    Event,
    ExecutionContext,
    GuardrailResult,
    HealthStatus,
    LLMResponse,
    StateProtocol,
    TaskId,
    TaskMetadata,
    TaskStatus,
    TokenUsage,
    ToolProtocol,
)
from openfoundry.core.task import Task, TaskResult

__all__ = [
    # Base classes
    "BaseAgent",
    "Context",
    "ContextBuilder",
    # Protocols
    "AgentProtocol",
    "ExecutionContext",
    "StateProtocol",
    "ToolProtocol",
    # Data classes
    "AgentId",
    "Event",
    "GuardrailResult",
    "HealthStatus",
    "LLMResponse",
    "Task",
    "TaskId",
    "TaskMetadata",
    "TaskResult",
    "TaskStatus",
    "TokenUsage",
]
