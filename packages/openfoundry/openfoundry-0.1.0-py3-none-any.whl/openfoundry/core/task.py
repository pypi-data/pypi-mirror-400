"""
Task and TaskResult implementations for OpenFoundry.

Tasks represent units of work that agents can execute.
TaskResults capture the outcome of task execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from openfoundry.core.protocols import AgentId, TaskId, TaskMetadata, TaskStatus


@dataclass(slots=True)
class Task:
    """
    Represents a unit of work to be executed by an agent.

    Tasks are immutable after creation - use with_* methods to create
    modified copies.
    """

    task_id: TaskId
    task_type: str
    payload: dict[str, Any]
    metadata: TaskMetadata = field(default_factory=TaskMetadata)
    status: TaskStatus = TaskStatus.PENDING

    @classmethod
    def create(
        cls,
        task_type: str,
        payload: dict[str, Any] | None = None,
        priority: int = 0,
        timeout_seconds: int = 300,
        tags: frozenset[str] | None = None,
        parent_task_id: TaskId | None = None,
    ) -> Task:
        """Create a new task with generated ID."""
        return cls(
            task_id=TaskId.generate(),
            task_type=task_type,
            payload=payload or {},
            metadata=TaskMetadata(
                priority=priority,
                timeout_seconds=timeout_seconds,
                tags=tags or frozenset(),
                parent_task_id=parent_task_id,
            ),
            status=TaskStatus.PENDING,
        )

    def with_status(self, status: TaskStatus) -> Task:
        """Return a new task with updated status."""
        return Task(
            task_id=self.task_id,
            task_type=self.task_type,
            payload=self.payload,
            metadata=self.metadata,
            status=status,
        )

    def with_payload(self, payload: dict[str, Any]) -> Task:
        """Return a new task with updated payload."""
        return Task(
            task_id=self.task_id,
            task_type=self.task_type,
            payload=payload,
            metadata=self.metadata,
            status=self.status,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_id": self.task_id.value,
            "task_type": self.task_type,
            "payload": self.payload,
            "status": self.status.name,
            "metadata": {
                "priority": self.metadata.priority,
                "timeout_seconds": self.metadata.timeout_seconds,
                "max_retries": self.metadata.max_retries,
                "created_at": self.metadata.created_at.isoformat(),
                "parent_task_id": (
                    self.metadata.parent_task_id.value
                    if self.metadata.parent_task_id
                    else None
                ),
                "tags": list(self.metadata.tags),
                "correlation_id": self.metadata.correlation_id,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Create task from dictionary."""
        metadata_data = data.get("metadata", {})
        parent_id = metadata_data.get("parent_task_id")

        return cls(
            task_id=TaskId(value=data["task_id"]),
            task_type=data["task_type"],
            payload=data.get("payload", {}),
            status=TaskStatus[data.get("status", "PENDING")],
            metadata=TaskMetadata(
                priority=metadata_data.get("priority", 0),
                timeout_seconds=metadata_data.get("timeout_seconds", 300),
                max_retries=metadata_data.get("max_retries", 3),
                created_at=datetime.fromisoformat(metadata_data["created_at"])
                if "created_at" in metadata_data
                else datetime.now(timezone.utc),
                parent_task_id=TaskId(value=parent_id) if parent_id else None,
                tags=frozenset(metadata_data.get("tags", [])),
                correlation_id=metadata_data.get("correlation_id"),
            ),
        )


@dataclass(slots=True)
class TaskResult:
    """Result of task execution."""

    task_id: TaskId
    status: TaskStatus
    output: Any
    error: str | None = None
    execution_time_ms: float = 0.0
    agent_id: AgentId | None = None
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def success(
        cls,
        task_id: TaskId,
        output: Any,
        agent_id: AgentId | None = None,
        execution_time_ms: float = 0.0,
    ) -> TaskResult:
        """Create a successful result."""
        return cls(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            output=output,
            agent_id=agent_id,
            execution_time_ms=execution_time_ms,
        )

    @classmethod
    def failure(
        cls,
        task_id: TaskId,
        error: str,
        agent_id: AgentId | None = None,
        execution_time_ms: float = 0.0,
    ) -> TaskResult:
        """Create a failed result."""
        return cls(
            task_id=task_id,
            status=TaskStatus.FAILED,
            output=None,
            error=error,
            agent_id=agent_id,
            execution_time_ms=execution_time_ms,
        )

    @property
    def is_success(self) -> bool:
        """Check if task completed successfully."""
        return self.status == TaskStatus.COMPLETED

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "task_id": self.task_id.value,
            "status": self.status.name,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "agent_id": self.agent_id.value if self.agent_id else None,
            "completed_at": self.completed_at.isoformat(),
        }
