"""
VIGIL LABS - Workflow Routes
Create, manage, and execute multi-tool workflows.
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.workflow import Workflow, WorkflowRun

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


class WorkflowStep(BaseModel):
    tool_id: str
    tool_name: str = ""
    order: int = 0
    arguments: dict = {}
    pipe_output: bool = True
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


@router.post("/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Execute a workflow (runs steps sequentially)."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create run record
    run = WorkflowRun(
        workflow_id=workflow_id,
        user_id=current_user["sub"],
        total_steps=len(workflow.steps),
        status="running",
    )
    db.add(run)
    
    workflow.run_count += 1
    workflow.last_run = datetime.utcnow()
    workflow.status = "running"
    await db.commit()
    
    # TODO: Execute steps asynchronously via execution engine
    # For now, return the run ID for tracking
    return {"run_id": run.id, "workflow_id": workflow_id, "status": "running", "total_steps": len(workflow.steps)}


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
    workflow.is_active = False
    await db.commit()
    return {"message": "Workflow deleted"}
