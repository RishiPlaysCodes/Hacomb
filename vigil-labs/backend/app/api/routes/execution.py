"""
VIGIL LABS - Execution Routes
Tool execution, process management, history, and reporting.
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.validators import sanitize_search_query
from app.models.tool import Tool, ToolArgument
from app.models.execution import Execution, ExecutionLog
from app.schemas.execution import (
    ExecuteToolRequest, ExecutionResponse, ExecutionListResponse,
    StopExecutionRequest, PresetCreate, PresetResponse
)
from app.models.preset import Preset
from app.services.execution_engine import execution_engine

router = APIRouter(prefix="/api/executions", tags=["Executions"])


@router.post("/run", response_model=ExecutionResponse)
async def execute_tool(
    request: ExecuteToolRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Execute a registered tool."""
    # Get tool
    result = await db.execute(select(Tool).where(Tool.id == request.tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Get arguments
    args_result = await db.execute(
        select(ToolArgument).where(ToolArgument.tool_id == tool.id).order_by(ToolArgument.order)
    )
    tool_args = args_result.scalars().all()
    
    # Validate arguments
    validation = execution_engine.validate_arguments(request.arguments, tool_args)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={
            "message": "Argument validation failed",
            "errors": validation["errors"],
            "warnings": validation["warnings"],
        })
    
    # Build command
    command = execution_engine.build_command(
        template=tool.command_template,
        executable=tool.executable_path,
        arguments=request.arguments,
        tool_args=tool_args,
    )
    
    # Create execution record
    execution = Execution(
        tool_id=tool.id,
        user_id=current_user["sub"],
        command=command,
        arguments_used=request.arguments,
        working_directory=request.working_directory or tool.working_directory,
        status="running",
        started_at=datetime.utcnow(),
        notes=request.notes,
        tags=request.tags,
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # Update tool usage
    tool.use_count += 1
    tool.last_used = datetime.utcnow()
    await db.commit()
    
    # Execute (non-blocking)
    try:
        await execution_engine.execute(
            command=command,
            execution_id=execution.id,
            tool_id=tool.id,
            user_id=current_user["sub"],
            working_directory=request.working_directory or tool.working_directory,
            environment=tool.environment_variables,
            timeout=request.timeout or tool.execution_timeout,
        )
    except RuntimeError as e:
        execution.status = "failed"
        execution.stderr = str(e)
        await db.commit()
        raise HTTPException(status_code=409, detail=str(e))
    
    return ExecutionResponse.model_validate(execution)


@router.post("/stop")
async def stop_execution(
    request: StopExecutionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stop a running execution."""
    success = await execution_engine.stop_process(request.execution_id, request.force)
    if not success:
        raise HTTPException(status_code=404, detail="Process not found or already stopped")
    
    # Update database
    result = await db.execute(select(Execution).where(Execution.id == request.execution_id))
    execution = result.scalar_one_or_none()
    if execution:
        execution.status = "stopped"
        execution.completed_at = datetime.utcnow()
        if execution.started_at:
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        await db.commit()
    
    return {"message": "Process stopped", "execution_id": request.execution_id}


@router.get("/running")
async def get_running(current_user: dict = Depends(get_current_user)):
    """Get all currently running processes."""
    return execution_engine.get_all_running()


@router.get("/history", response_model=ExecutionListResponse)
async def get_history(
    tool_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get execution history with filtering."""
    query = select(Execution).where(Execution.user_id == current_user["sub"])
    
    if tool_id:
        query = query.where(Execution.tool_id == tool_id)
    if status:
        query = query.where(Execution.status == status)
    if search:
        safe_search = sanitize_search_query(search)
        query = query.where(Execution.command.ilike(f"%{safe_search}%"))
    
    # Count total
    from sqlalchemy import func
    count_query = select(func.count(Execution.id)).where(Execution.user_id == current_user["sub"])
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(desc(Execution.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    executions = result.scalars().all()
    
    return ExecutionListResponse(
        executions=[ExecutionResponse.model_validate(e) for e in executions],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get execution details."""
    result = await db.execute(select(Execution).where(Execution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse.model_validate(execution)


@router.delete("/{execution_id}")
async def delete_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete an execution record."""
    result = await db.execute(select(Execution).where(Execution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    await db.delete(execution)
    await db.commit()
    return {"message": "Execution deleted"}


# --- Presets ---

@router.get("/presets/{tool_id}", response_model=List[PresetResponse])
async def get_presets(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get saved presets for a tool."""
    result = await db.execute(
        select(Preset).where(Preset.tool_id == tool_id, Preset.user_id == current_user["sub"])
    )
    return [PresetResponse.model_validate(p) for p in result.scalars().all()]


@router.post("/presets/save", response_model=PresetResponse)
async def save_preset(
    request: PresetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Save a tool configuration preset."""
    preset = Preset(
        tool_id=request.tool_id,
        user_id=current_user["sub"],
        name=request.name,
        description=request.description,
        arguments=request.arguments,
        is_default=request.is_default,
    )
    db.add(preset)
    await db.commit()
    await db.refresh(preset)
    return PresetResponse.model_validate(preset)


# --- Reports & Export ---

@router.get("/{execution_id}/export")
async def export_execution(
    execution_id: str,
    format: str = Query("json", regex="^(json|txt|html)$"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Export execution report."""
    result = await db.execute(select(Execution).where(Execution.id == execution_id))
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if format == "json":
        return ExecutionResponse.model_validate(execution).model_dump()
    elif format == "txt":
        report = f"""VIGIL LABS - Execution Report
================================
Command: {execution.command}
Status: {execution.status}
Started: {execution.started_at}
Duration: {execution.duration_seconds}s
Exit Code: {execution.exit_code}

--- STDOUT ---
{execution.stdout or 'No output'}

--- STDERR ---
{execution.stderr or 'No errors'}
"""
        return {"content": report, "filename": f"report_{execution_id}.txt"}
    elif format == "html":
        html = f"""<!DOCTYPE html>
<html><head><title>VIGIL LABS Report</title>
<style>body{{font-family:monospace;background:#1a1a2e;color:#e2e8f0;padding:2rem}}
.header{{color:#6366f1;font-size:1.5rem}}.section{{margin:1rem 0;padding:1rem;background:#12121a;border-radius:8px}}
pre{{white-space:pre-wrap}}</style></head>
<body><div class="header">VIGIL LABS - Execution Report</div>
<div class="section"><strong>Command:</strong> {execution.command}</div>
<div class="section"><strong>Status:</strong> {execution.status}</div>
<div class="section"><strong>Duration:</strong> {execution.duration_seconds}s</div>
<div class="section"><strong>Output:</strong><pre>{execution.stdout or 'No output'}</pre></div>
</body></html>"""
        return {"content": html, "filename": f"report_{execution_id}.html"}
