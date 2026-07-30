"""
VIGIL LABS - Workflow Routes
Create, manage, and execute multi-tool workflows.
Workflows now actually execute: each step's command is built from its tool
definition and run sequentially (with output piping) via the workflow engine.
"""
import asyncio
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import get_current_user
from app.models.workflow import Workflow, WorkflowRun
from app.models.tool import Tool, ToolArgument
from app.services.execution_engine import execution_engine
from app.services.workflow_engine import workflow_engine

logger = logging.getLogger("vigil_labs.workflows")
router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


class WorkflowStep(BaseModel):
    tool_id: str
    tool_name: str = ""
    order: int = 0
    arguments: dict = {}
    pipe_output: bool = True
    continue_on_error: bool = False
    condition: Optional[str] = None


class CreateWorkflowRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    steps: List[WorkflowStep] = []
    tags: List[str] = []


@router.get("/")
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all workflows for current user."""
    result = await db.execute(
        select(Workflow)
        .where(Workflow.user_id == current_user["sub"], Workflow.is_active == True)
        .order_by(desc(Workflow.updated_at))
    )
    workflows = result.scalars().all()
    return [
        {
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "steps": wf.steps,
            "status": wf.status,
            "last_run": wf.last_run.isoformat() if wf.last_run else None,
            "run_count": wf.run_count,
            "is_favorite": wf.is_favorite,
            "tags": wf.tags,
            "created_at": wf.created_at.isoformat(),
        }
        for wf in workflows
    ]


@router.post("/")
async def create_workflow(
    request: CreateWorkflowRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new workflow."""
    if len(request.steps) < 2:
        raise HTTPException(status_code=400, detail="Workflow must have at least 2 steps")

    workflow = Workflow(
        user_id=current_user["sub"],
        name=request.name,
        description=request.description,
        steps=[s.model_dump() for s in request.steps],
        tags=request.tags,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    return {"id": workflow.id, "name": workflow.name, "message": "Workflow created"}


async def _build_steps_with_commands(db: AsyncSession, steps: list) -> tuple[list, list]:
    """
    Build executable commands for each workflow step from its tool definition.
    Returns (steps_with_commands, errors).
    """
    built = []
    errors = []

    for i, step in enumerate(steps):
        tool_id = step.get("tool_id")
        tool = None
        if tool_id:
            result = await db.execute(select(Tool).where(Tool.id == tool_id))
            tool = result.scalar_one_or_none()

        if not tool:
            errors.append(f"Step {i + 1}: tool not found")
            continue

        # Load argument definitions for command building
        args_result = await db.execute(
            select(ToolArgument).where(ToolArgument.tool_id == tool.id).order_by(ToolArgument.order)
        )
        tool_args = args_result.scalars().all()

        try:
            command = execution_engine.build_command(
                template=tool.command_template,
                executable=tool.executable_path,
                arguments=step.get("arguments", {}),
                tool_args=tool_args,
            )
        except Exception as e:
            errors.append(f"Step {i + 1} ({tool.name}): {e}")
            continue

        built.append({
            "tool_id": tool.id,
            "tool_name": tool.name,
            "executable": tool.executable_path,
            "command": command,
            "arguments": step.get("arguments", {}),
            "pipe_output": step.get("pipe_output", True),
            "continue_on_error": step.get("continue_on_error", False),
            "timeout": tool.execution_timeout or 300,
        })

    return built, errors


async def _run_workflow_background(workflow_id: str, run_id: str, user_id: str, steps: list):
    """Execute the workflow in the background and persist results as it progresses."""
    async with AsyncSessionLocal() as session:

        async def on_step_complete(wf_id, idx, step_result):
            # Persist incremental progress so the frontend can poll live
            res = await session.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
            run = res.scalar_one_or_none()
            if run:
                results = list(run.step_results or [])
                results.append(step_result)
                run.step_results = results
                run.current_step = idx + 1
                await session.commit()

        try:
            final = await workflow_engine.run_workflow(
                steps=steps,
                workflow_id=workflow_id,
                user_id=user_id,
                on_step_complete=on_step_complete,
            )
            status = final["status"]
        except Exception as e:
            logger.error(f"Workflow {workflow_id} run {run_id} crashed: {e}", exc_info=True)
            status = "failed"

        # Finalize run + workflow status
        res = await session.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
        run = res.scalar_one_or_none()
        if run:
            run.status = status
            run.completed_at = datetime.utcnow()
            if run.started_at:
                run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
            await session.commit()

        res = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
        wf = res.scalar_one_or_none()
        if wf:
            wf.status = status
            await session.commit()


@router.post("/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Execute a workflow (runs steps sequentially in the background)."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not your workflow")

    if not workflow.steps or len(workflow.steps) == 0:
        raise HTTPException(status_code=400, detail="Workflow has no steps")

    # Build executable commands from tool definitions
    steps_with_commands, errors = await _build_steps_with_commands(db, workflow.steps)

    if not steps_with_commands:
        raise HTTPException(
            status_code=400,
            detail={"message": "Cannot run workflow", "errors": errors or ["No valid steps"]},
        )

    # Create run record
    run = WorkflowRun(
        workflow_id=workflow_id,
        user_id=current_user["sub"],
        total_steps=len(steps_with_commands),
        status="running",
        step_results=[],
    )
    db.add(run)

    workflow.run_count += 1
    workflow.last_run = datetime.utcnow()
    workflow.status = "running"
    await db.commit()
    await db.refresh(run)

    # Kick off background execution
    asyncio.create_task(
        _run_workflow_background(workflow_id, run.id, current_user["sub"], steps_with_commands)
    )

    return {
        "run_id": run.id,
        "workflow_id": workflow_id,
        "status": "running",
        "total_steps": len(steps_with_commands),
        "warnings": errors,  # steps that were skipped, if any
    }


@router.get("/runs/{run_id}")
async def get_workflow_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Poll the status and results of a workflow run."""
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run.user_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not your run")

    return {
        "id": run.id,
        "workflow_id": run.workflow_id,
        "status": run.status,
        "current_step": run.current_step,
        "total_steps": run.total_steps,
        "step_results": run.step_results or [],
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "duration_seconds": run.duration_seconds,
    }


@router.get("/{workflow_id}/runs")
async def list_workflow_runs(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List recent runs for a workflow."""
    result = await db.execute(
        select(WorkflowRun)
        .where(WorkflowRun.workflow_id == workflow_id, WorkflowRun.user_id == current_user["sub"])
        .order_by(desc(WorkflowRun.started_at))
        .limit(20)
    )
    runs = result.scalars().all()
    return [
        {
            "id": r.id,
            "status": r.status,
            "current_step": r.current_step,
            "total_steps": r.total_steps,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "duration_seconds": r.duration_seconds,
        }
        for r in runs
    ]


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get workflow details."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": workflow.id, "name": workflow.name, "description": workflow.description,
        "steps": workflow.steps, "status": workflow.status, "run_count": workflow.run_count,
        "last_run": workflow.last_run.isoformat() if workflow.last_run else None,
        "is_favorite": workflow.is_favorite, "tags": workflow.tags,
    }


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a workflow (soft delete)."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if workflow.user_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not your workflow")
    workflow.is_active = False
    await db.commit()
    return {"message": "Workflow deleted"}
