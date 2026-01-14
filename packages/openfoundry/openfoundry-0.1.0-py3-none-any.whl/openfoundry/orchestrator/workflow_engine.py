"""
Workflow engine for DAG-based multi-step execution.

Handles complex workflows with:
- Step dependencies
- Parallel execution where possible
- State propagation between steps
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any
import uuid

import structlog

from openfoundry.core.protocols import TaskStatus
from openfoundry.core.task import Task
from openfoundry.orchestrator.coordinator import Coordinator


class WorkflowStatus(Enum):
    """Status of a workflow execution."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    PARTIALLY_COMPLETED = auto()


@dataclass
class WorkflowStep:
    """A step in a workflow."""

    name: str
    task_type: str
    payload_template: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    condition: str | None = None  # Optional condition expression


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""

    name: str
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    version: str = "1.0.0"

    def add_step(
        self,
        name: str,
        task_type: str,
        payload_template: dict[str, Any] | None = None,
        depends_on: list[str] | None = None,
        **kwargs: Any,
    ) -> WorkflowDefinition:
        """Add a step to the workflow."""
        self.steps.append(
            WorkflowStep(
                name=name,
                task_type=task_type,
                payload_template=payload_template or {},
                depends_on=depends_on or [],
                **kwargs,
            )
        )
        return self

    def validate(self) -> list[str]:
        """Validate the workflow definition."""
        errors = []
        step_names = {s.name for s in self.steps}

        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_names:
                    errors.append(f"Step '{step.name}' depends on unknown step '{dep}'")

            # Check for circular dependencies
            visited = set()
            if self._has_cycle(step.name, visited, set(), step_names):
                errors.append(f"Circular dependency detected involving step '{step.name}'")

        return errors

    def _has_cycle(
        self,
        step_name: str,
        visited: set[str],
        rec_stack: set[str],
        all_steps: set[str],
    ) -> bool:
        """Check for cycles using DFS."""
        if step_name not in all_steps:
            return False

        visited.add(step_name)
        rec_stack.add(step_name)

        step = next((s for s in self.steps if s.name == step_name), None)
        if step:
            for dep in step.depends_on:
                if dep not in visited:
                    if self._has_cycle(dep, visited, rec_stack, all_steps):
                        return True
                elif dep in rec_stack:
                    return True

        rec_stack.remove(step_name)
        return False


@dataclass
class StepResult:
    """Result of a workflow step execution."""

    step_name: str
    status: TaskStatus
    output: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class WorkflowExecution:
    """State of a workflow execution."""

    workflow_id: str
    definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.PENDING
    input: dict[str, Any] = field(default_factory=dict)
    step_results: dict[str, StepResult] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def completed_steps(self) -> list[str]:
        """Get names of completed steps."""
        return [
            name
            for name, result in self.step_results.items()
            if result.status == TaskStatus.COMPLETED
        ]

    @property
    def failed_steps(self) -> list[str]:
        """Get names of failed steps."""
        return [
            name
            for name, result in self.step_results.items()
            if result.status == TaskStatus.FAILED
        ]


class WorkflowEngine:
    """
    Engine for executing DAG-based workflows.

    Example:
        # Define workflow
        workflow = (
            WorkflowDefinition(name="code_review")
            .add_step("analyze", "code_analysis", {"code": "{{input.code}}"})
            .add_step("review", "code_review", depends_on=["analyze"])
            .add_step("report", "generate_report", depends_on=["review"])
        )

        # Execute
        engine = WorkflowEngine(coordinator)
        execution = await engine.execute(workflow, input={"code": "..."})
    """

    def __init__(self, coordinator: Coordinator):
        """
        Initialize the workflow engine.

        Args:
            coordinator: Coordinator for task execution
        """
        self.coordinator = coordinator
        self._logger = structlog.get_logger().bind(component="workflow_engine")
        self._executions: dict[str, WorkflowExecution] = {}

    def get_execution(self, workflow_id: str) -> WorkflowExecution | None:
        """Get workflow execution by ID."""
        return self._executions.get(workflow_id)

    async def execute(
        self,
        definition: WorkflowDefinition,
        input: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow.

        Args:
            definition: Workflow definition
            input: Initial input data

        Returns:
            WorkflowExecution with results
        """
        # Validate workflow
        errors = definition.validate()
        if errors:
            raise ValueError(f"Invalid workflow: {errors}")

        # Create execution
        execution = WorkflowExecution(
            workflow_id=str(uuid.uuid4()),
            definition=definition,
            input=input or {},
            started_at=datetime.now(timezone.utc),
        )

        self._executions[execution.workflow_id] = execution

        self._logger.info(
            "workflow_started",
            workflow_id=execution.workflow_id,
            name=definition.name,
            step_count=len(definition.steps),
        )

        try:
            execution.status = WorkflowStatus.RUNNING

            # Execute steps in dependency order
            await self._execute_steps(execution)

            # Determine final status
            if execution.failed_steps:
                execution.status = WorkflowStatus.PARTIALLY_COMPLETED
            else:
                execution.status = WorkflowStatus.COMPLETED
                # Collect output from all steps
                execution.output = {
                    name: result.output
                    for name, result in execution.step_results.items()
                    if result.output is not None
                }

        except asyncio.CancelledError:
            execution.status = WorkflowStatus.CANCELLED
            execution.error = "Workflow was cancelled"
            raise

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            self._logger.exception(
                "workflow_failed",
                workflow_id=execution.workflow_id,
            )

        finally:
            execution.completed_at = datetime.now(timezone.utc)

        self._logger.info(
            "workflow_completed",
            workflow_id=execution.workflow_id,
            status=execution.status.name,
            completed_steps=len(execution.completed_steps),
            failed_steps=len(execution.failed_steps),
        )

        return execution

    async def _execute_steps(self, execution: WorkflowExecution) -> None:
        """Execute workflow steps respecting dependencies."""
        definition = execution.definition
        pending_steps = {s.name for s in definition.steps}
        completed_steps: set[str] = set()

        while pending_steps:
            # Find steps ready to execute
            ready_steps = []
            for step in definition.steps:
                if step.name in pending_steps:
                    # Check if all dependencies are completed
                    deps_met = all(
                        dep in completed_steps for dep in step.depends_on
                    )
                    if deps_met:
                        ready_steps.append(step)

            if not ready_steps:
                # No steps ready but still pending - deadlock
                raise RuntimeError(
                    f"Workflow deadlock: pending steps {pending_steps} "
                    f"with completed {completed_steps}"
                )

            # Execute ready steps in parallel
            results = await asyncio.gather(
                *[
                    self._execute_step(execution, step)
                    for step in ready_steps
                ],
                return_exceptions=True,
            )

            # Process results
            for step, result in zip(ready_steps, results):
                pending_steps.remove(step.name)

                if isinstance(result, Exception):
                    execution.step_results[step.name] = StepResult(
                        step_name=step.name,
                        status=TaskStatus.FAILED,
                        error=str(result),
                    )
                else:
                    execution.step_results[step.name] = result
                    if result.status == TaskStatus.COMPLETED:
                        completed_steps.add(step.name)

    async def _execute_step(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep,
    ) -> StepResult:
        """Execute a single workflow step."""
        self._logger.debug(
            "executing_step",
            workflow_id=execution.workflow_id,
            step_name=step.name,
        )

        started_at = datetime.now(timezone.utc)

        # Build payload from template
        payload = self._render_payload(
            step.payload_template,
            execution,
        )

        # Create task
        task = Task.create(
            task_type=step.task_type,
            payload=payload,
            timeout_seconds=step.timeout_seconds,
            parent_task_id=None,
        )

        # Execute via coordinator
        result = await self.coordinator.execute(task)

        completed_at = datetime.now(timezone.utc)

        return StepResult(
            step_name=step.name,
            status=result.status,
            output=result.output,
            error=result.error,
            execution_time_ms=result.execution_time_ms,
            started_at=started_at,
            completed_at=completed_at,
        )

    def _render_payload(
        self,
        template: dict[str, Any],
        execution: WorkflowExecution,
    ) -> dict[str, Any]:
        """Render payload template with execution context."""
        # Simple template rendering - replace {{input.key}} and {{steps.name.output}}
        def replace_var(value: Any) -> Any:
            if not isinstance(value, str):
                if isinstance(value, dict):
                    return {k: replace_var(v) for k, v in value.items()}
                if isinstance(value, list):
                    return [replace_var(v) for v in value]
                return value

            # Replace input references
            pattern = r"\{\{input\.(\w+)\}\}"
            value = re.sub(
                pattern,
                lambda m: str(execution.input.get(m.group(1), "")),
                value,
            )

            # Replace step output references
            pattern = r"\{\{steps\.(\w+)\.output\}\}"
            def replace_step(m):
                step_name = m.group(1)
                if step_name in execution.step_results:
                    return str(execution.step_results[step_name].output)
                return ""

            value = re.sub(pattern, replace_step, value)

            return value

        return replace_var(template)

    async def cancel(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        execution = self._executions.get(workflow_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now(timezone.utc)
            return True
        return False
