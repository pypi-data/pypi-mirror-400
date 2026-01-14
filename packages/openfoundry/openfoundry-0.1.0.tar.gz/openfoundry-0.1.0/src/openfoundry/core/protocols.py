"""
Core protocol definitions for OpenFoundry.

Uses structural subtyping (PEP 544) for maximum flexibility and loose coupling.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class TaskStatus(Enum):
    """Status of a task in the system."""

    PENDING = auto()
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    RETRYING = auto()


@dataclass(frozen=True, slots=True)
class TaskId:
    """Unique identifier for a task."""

    value: str

    @classmethod
    def generate(cls) -> TaskId:
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AgentId:
    """Unique identifier for an agent."""

    value: str
    module: str

    @classmethod
    def create(cls, name: str, module: str) -> AgentId:
        return cls(value=f"{module}.{name}", module=module)

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class TaskMetadata:
    """Metadata associated with a task."""

    priority: int = 0
    timeout_seconds: int = 300
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    parent_task_id: TaskId | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    correlation_id: str | None = None

    def with_tag(self, tag: str) -> TaskMetadata:
        return TaskMetadata(
            priority=self.priority,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            created_at=self.created_at,
            parent_task_id=self.parent_task_id,
            tags=self.tags | {tag},
            correlation_id=self.correlation_id,
        )


@dataclass(slots=True)
class HealthStatus:
    """Health status of a component."""

    healthy: bool
    message: str = ""
    checks: dict[str, bool] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def ok(cls, message: str = "Healthy") -> HealthStatus:
        return cls(healthy=True, message=message)

    @classmethod
    def unhealthy(cls, message: str, checks: dict[str, bool] | None = None) -> HealthStatus:
        return cls(healthy=False, message=message, checks=checks or {})


@dataclass(slots=True)
class TokenUsage:
    """Token usage statistics from LLM calls."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float = 0.0

    def __add__(self, other: TokenUsage) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
        )


@dataclass(slots=True)
class LLMResponse:
    """Response from LLM provider."""

    content: str
    model: str
    usage: TokenUsage
    finish_reason: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@runtime_checkable
class StateProtocol(Protocol):
    """Protocol for distributed state management."""

    async def get(self, key: str, default: T | None = None) -> T | None:
        ...

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ...

    async def delete(self, key: str) -> bool:
        ...

    async def exists(self, key: str) -> bool:
        ...


class ExecutionContext(Protocol):
    """Context passed during task execution."""

    @property
    def trace_id(self) -> str:
        ...

    @property
    def state(self) -> StateProtocol:
        ...


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol defining the interface for all agents."""

    @property
    def agent_id(self) -> AgentId:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def capabilities(self) -> set[str]:
        ...

    async def health_check(self) -> HealthStatus:
        ...


@dataclass(slots=True)
class GuardrailResult:
    """Result from a guardrail validation."""

    passed: bool
    message: str = ""
    violations: list[str] = field(default_factory=list)
    sanitized_content: str | None = None
    confidence: float = 1.0

    @classmethod
    def allow(cls, message: str = "Allowed") -> GuardrailResult:
        return cls(passed=True, message=message)

    @classmethod
    def block(cls, message: str, violations: list[str] | None = None) -> GuardrailResult:
        return cls(passed=False, message=message, violations=violations or [])
