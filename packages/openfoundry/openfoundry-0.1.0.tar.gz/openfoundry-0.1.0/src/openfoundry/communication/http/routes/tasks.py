"""
Task management endpoints for OpenFoundry API.

Provides endpoints for:
- Submitting tasks
- Getting task status
- Cancelling tasks
- Listing tasks
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, Field

from openfoundry.core.protocols import TaskStatus
from openfoundry.core.task import Task, TaskResult

router = APIRouter()


class TaskSubmitRequest(BaseModel):
    """Request to submit a new task."""

    task_type: str = Field(..., description="Type of task to execute")
    payload: dict[str, Any] = Field(default_factory=dict, description="Task input data")
    priority: int = Field(default=0, description="Task priority (higher = more important)")
    timeout_seconds: int = Field(default=300, description="Task timeout in seconds")
    tags: list[str] = Field(default_factory=list, description="Task tags for filtering")


class TaskResponse(BaseModel):
    """Task information response."""

    task_id: str
    task_type: str
    status: str
    payload: dict[str, Any] = {}
    created_at: str


class TaskResultResponse(BaseModel):
    """Task result response."""

    task_id: str
    status: str
    output: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    agent_id: str | None = None


class TaskListResponse(BaseModel):
    """List of tasks response."""

    tasks: list[TaskResponse]
    total: int


# In-memory task storage (would use proper persistence in production)
_tasks: dict[str, Task] = {}
_results: dict[str, TaskResult] = {}


@router.post("", response_model=TaskResponse, status_code=201)
async def submit_task(
    request: Request,
    task_request: TaskSubmitRequest,
    background_tasks: BackgroundTasks,
) -> TaskResponse:
    """
    Submit a new task for execution.

    The task will be queued and executed by an appropriate agent.
    """
    # Create task
    task = Task.create(
        task_type=task_request.task_type,
        payload=task_request.payload,
        priority=task_request.priority,
        timeout_seconds=task_request.timeout_seconds,
        tags=frozenset(task_request.tags),
    )

    # Store task
    _tasks[task.task_id.value] = task

    # Queue for background execution
    background_tasks.add_task(_execute_task, request.app, task)

    return TaskResponse(
        task_id=task.task_id.value,
        task_type=task.task_type,
        status=task.status.name,
        payload=task.payload,
        created_at=task.metadata.created_at.isoformat(),
    )


async def _execute_task(app, task: Task) -> None:
    """Execute a task in the background."""
    registry = app.state.agent_registry
    settings = app.state.settings

    # Find an agent that can handle this task
    handlers = await registry.find_for_task(task)
    if not handlers:
        _results[task.task_id.value] = TaskResult.failure(
            task_id=task.task_id,
            error=f"No agent found for task type: {task.task_type}",
        )
        _tasks[task.task_id.value] = task.with_status(TaskStatus.FAILED)
        return

    # Use first available handler
    agent = handlers[0]

    # Build context
    from openfoundry.core.context import Context
    from openfoundry.llm import LLMProvider

    llm_provider = LLMProvider(
        default_model=settings.llm.default_model,
    )

    context = Context(
        llm=llm_provider,
        state=app.state.state_store,
        _agent_registry=registry,
    )

    # Update status to running
    _tasks[task.task_id.value] = task.with_status(TaskStatus.RUNNING)

    # Execute
    try:
        result = await agent.execute(task, context)
        _results[task.task_id.value] = result
        _tasks[task.task_id.value] = task.with_status(result.status)
    except Exception as e:
        _results[task.task_id.value] = TaskResult.failure(
            task_id=task.task_id,
            error=str(e),
            agent_id=agent.agent_id,
        )
        _tasks[task.task_id.value] = task.with_status(TaskStatus.FAILED)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """
    Get task details by ID.
    """
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    task = _tasks[task_id]
    return TaskResponse(
        task_id=task.task_id.value,
        task_type=task.task_type,
        status=task.status.name,
        payload=task.payload,
        created_at=task.metadata.created_at.isoformat(),
    )


@router.get("/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: str) -> TaskResultResponse:
    """
    Get task execution result.

    Returns 404 if task not found or result not yet available.
    """
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    if task_id not in _results:
        task = _tasks[task_id]
        raise HTTPException(
            status_code=404,
            detail=f"Result not yet available. Task status: {task.status.name}",
        )

    result = _results[task_id]
    return TaskResultResponse(
        task_id=result.task_id.value,
        status=result.status.name,
        output=result.output,
        error=result.error,
        execution_time_ms=result.execution_time_ms,
        agent_id=result.agent_id.value if result.agent_id else None,
    )


@router.delete("/{task_id}")
async def cancel_task(task_id: str) -> dict[str, str]:
    """
    Cancel a pending or running task.
    """
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    task = _tasks[task_id]
    if task.status not in (TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task in status: {task.status.name}",
        )

    _tasks[task_id] = task.with_status(TaskStatus.CANCELLED)
    _results[task_id] = TaskResult.cancelled(task_id=task.task_id)

    return {"message": f"Task {task_id} cancelled"}


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: str | None = None,
    task_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> TaskListResponse:
    """
    List tasks with optional filtering.
    """
    tasks = list(_tasks.values())

    # Filter by status
    if status:
        try:
            status_enum = TaskStatus[status.upper()]
            tasks = [t for t in tasks if t.status == status_enum]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    # Filter by type
    if task_type:
        tasks = [t for t in tasks if t.task_type == task_type]

    # Sort by creation time (newest first)
    tasks.sort(key=lambda t: t.metadata.created_at, reverse=True)

    # Paginate
    total = len(tasks)
    tasks = tasks[offset : offset + limit]

    return TaskListResponse(
        tasks=[
            TaskResponse(
                task_id=t.task_id.value,
                task_type=t.task_type,
                status=t.status.name,
                payload=t.payload,
                created_at=t.metadata.created_at.isoformat(),
            )
            for t in tasks
        ],
        total=total,
    )
