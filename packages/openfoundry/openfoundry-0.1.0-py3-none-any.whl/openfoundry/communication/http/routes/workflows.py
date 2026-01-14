"""
Workflow management endpoints for OpenFoundry API.

Provides endpoints for:
- Submitting workflows
- Getting workflow status
- Workflow execution history
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter()


class WorkflowStep(BaseModel):
    """A step in a workflow."""

    name: str
    agent_type: str
    task_type: str
    payload: dict[str, Any] = {}
    depends_on: list[str] = []


class WorkflowSubmitRequest(BaseModel):
    """Request to submit a workflow."""

    name: str = Field(..., description="Workflow name")
    description: str = Field(default="", description="Workflow description")
    steps: list[WorkflowStep] = Field(..., description="Workflow steps")
    input: dict[str, Any] = Field(default_factory=dict, description="Initial input")


class WorkflowResponse(BaseModel):
    """Workflow information response."""

    workflow_id: str
    name: str
    status: str
    steps_completed: int
    steps_total: int
    current_step: str | None = None
    output: dict[str, Any] | None = None
    error: str | None = None


class WorkflowListResponse(BaseModel):
    """List of workflows response."""

    workflows: list[WorkflowResponse]
    total: int


# In-memory workflow storage
_workflows: dict[str, dict[str, Any]] = {}


def _validate_workflow(workflow_request: WorkflowSubmitRequest) -> None:
    """Validate workflow definition."""
    if not workflow_request.steps:
        raise HTTPException(status_code=400, detail="Workflow must have at least one step")

    step_names = {s.name for s in workflow_request.steps}

    for step in workflow_request.steps:
        for dep in step.depends_on:
            if dep not in step_names:
                raise HTTPException(
                    status_code=400,
                    detail=f"Step '{step.name}' depends on unknown step '{dep}'",
                )


@router.post("", response_model=WorkflowResponse, status_code=201)
async def submit_workflow(
    request: Request,
    workflow_request: WorkflowSubmitRequest,
) -> WorkflowResponse:
    """
    Submit a new workflow for execution.

    Workflows are DAGs of tasks executed across multiple agents.
    """
    import uuid

    # Validate workflow definition
    _validate_workflow(workflow_request)

    workflow_id = str(uuid.uuid4())

    # Store workflow definition
    _workflows[workflow_id] = {
        "id": workflow_id,
        "name": workflow_request.name,
        "description": workflow_request.description,
        "steps": [s.model_dump() for s in workflow_request.steps],
        "input": workflow_request.input,
        "status": "pending",
        "steps_completed": 0,
        "current_step": None,
        "output": None,
        "error": None,
    }

    # TODO: Queue workflow for execution via orchestrator

    return WorkflowResponse(
        workflow_id=workflow_id,
        name=workflow_request.name,
        status="pending",
        steps_completed=0,
        steps_total=len(workflow_request.steps),
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    """
    Get workflow status and details.
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")

    wf = _workflows[workflow_id]
    return WorkflowResponse(
        workflow_id=wf["id"],
        name=wf["name"],
        status=wf["status"],
        steps_completed=wf["steps_completed"],
        steps_total=len(wf["steps"]),
        current_step=wf.get("current_step"),
        output=wf.get("output"),
        error=wf.get("error"),
    )


@router.delete("/{workflow_id}")
async def cancel_workflow(workflow_id: str) -> dict[str, str]:
    """
    Cancel a running workflow.
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")

    wf = _workflows[workflow_id]
    if wf["status"] in ("completed", "failed", "cancelled"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel workflow in status: {wf['status']}",
        )

    wf["status"] = "cancelled"
    return {"message": f"Workflow {workflow_id} cancelled"}


@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> WorkflowListResponse:
    """
    List workflows with optional filtering.
    """
    workflows = list(_workflows.values())

    # Filter by status
    if status:
        workflows = [w for w in workflows if w["status"] == status]

    # Paginate
    total = len(workflows)
    workflows = workflows[offset : offset + limit]

    return WorkflowListResponse(
        workflows=[
            WorkflowResponse(
                workflow_id=w["id"],
                name=w["name"],
                status=w["status"],
                steps_completed=w["steps_completed"],
                steps_total=len(w["steps"]),
                current_step=w.get("current_step"),
                output=w.get("output"),
                error=w.get("error"),
            )
            for w in workflows
        ],
        total=total,
    )


@router.get("/{workflow_id}/steps")
async def get_workflow_steps(workflow_id: str) -> dict[str, Any]:
    """
    Get detailed step information for a workflow.
    """
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")

    wf = _workflows[workflow_id]
    return {
        "workflow_id": workflow_id,
        "steps": wf["steps"],
    }
