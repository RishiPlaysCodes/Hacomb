"""
VIGIL LABS - Tool Routes
Tool registry CRUD, categories, favorites, search, and dependency checking.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.validators import sanitize_search_query
from app.models.tool import Tool, ToolArgument, ToolCategory
from app.schemas.tool import (
    CreateToolRequest, UpdateToolRequest, ToolResponse,
    CategoryCreate, CategoryResponse, ToolArgumentSchema
)
from app.services.execution_engine import execution_engine

router = APIRouter(prefix="/api/tools", tags=["Tools"])


@router.get("/", response_model=List[ToolResponse])
async def list_tools(
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    favorites_only: bool = False,
    risk_level: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all tools with filtering."""
    query = select(Tool).where(Tool.is_active == True)
    
    if category_id:
        query = query.where(Tool.category_id == category_id)
    if favorites_only:
        query = query.where(Tool.is_favorite == True)
    if risk_level:
        query = query.where(Tool.risk_level == risk_level)
    if search:
        safe_search = sanitize_search_query(search)
        query = query.where(
            or_(
                Tool.name.ilike(f"%{safe_search}%"),
                Tool.description.ilike(f"%{safe_search}%"),
            )
        )
    
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    tools = result.scalars().all()
    
    responses = []
    for tool in tools:
        # Load arguments
        args_result = await db.execute(
            select(ToolArgument).where(ToolArgument.tool_id == tool.id).order_by(ToolArgument.order)
        )
        arguments = args_result.scalars().all()
        
        tool_resp = ToolResponse.model_validate(tool)
        tool_resp.arguments = [ToolArgumentSchema.model_validate(a.__dict__) for a in arguments]
        if tool.category:
            tool_resp.category_name = tool.category.name
        responses.append(tool_resp)
    
    return responses


@router.post("/", response_model=ToolResponse)
async def create_tool(
    request: CreateToolRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new tool in the registry."""
    # Check if executable exists
    validation = execution_engine.validate_executable(request.executable_path)
    
    tool = Tool(
        name=request.name,
        description=request.description,
        category_id=request.category_id,
        executable_path=request.executable_path,
        command_template=request.command_template,
        supports_linux=request.supports_linux,
        supports_windows=request.supports_windows,
        icon=request.icon,
        tags=request.tags,
        notes=request.notes,
        risk_level=request.risk_level,
        version=request.version,
        author=request.author,
        output_format=request.output_format,
        report_path=request.report_path,
        execution_timeout=request.execution_timeout,
        working_directory=request.working_directory,
        run_as_root=request.run_as_root,
        environment_variables=request.environment_variables,
        dependencies=request.dependencies,
        pre_execution_checks=request.pre_execution_checks,
        post_execution_actions=request.post_execution_actions,
        is_installed=validation["valid"],
        created_by=current_user["sub"],
    )
    db.add(tool)
    await db.flush()
    
    # Add arguments
    for i, arg_data in enumerate(request.arguments):
        arg = ToolArgument(
            tool_id=tool.id,
            name=arg_data.name,
            label=arg_data.label,
            description=arg_data.description,
            field_type=arg_data.field_type,
            flag=arg_data.flag,
            placeholder=arg_data.placeholder,
            default_value=arg_data.default_value,
            tooltip=arg_data.tooltip,
            example=arg_data.example,
            is_required=arg_data.is_required,
            validation_regex=arg_data.validation_regex,
            min_value=arg_data.min_value,
            max_value=arg_data.max_value,
            min_length=arg_data.min_length,
            max_length=arg_data.max_length,
            options=arg_data.options,
            order=arg_data.order or i,
            group=arg_data.group,
            width=arg_data.width,
            is_advanced=arg_data.is_advanced,
            depends_on=arg_data.depends_on,
        )
        db.add(arg)
    
    await db.commit()
    await db.refresh(tool)
    
    return ToolResponse.model_validate(tool)


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get tool by ID with full details."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    args_result = await db.execute(
        select(ToolArgument).where(ToolArgument.tool_id == tool.id).order_by(ToolArgument.order)
    )
    arguments = args_result.scalars().all()
    
    tool_resp = ToolResponse.model_validate(tool)
    tool_resp.arguments = [ToolArgumentSchema.model_validate(a.__dict__) for a in arguments]
    if tool.category:
        tool_resp.category_name = tool.category.name
    
    return tool_resp


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: str,
    request: UpdateToolRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update tool configuration."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True, exclude={"arguments"})
    for key, value in update_data.items():
        setattr(tool, key, value)
    
    # Update arguments if provided
    if request.arguments is not None:
        # Delete existing arguments
        args_result = await db.execute(select(ToolArgument).where(ToolArgument.tool_id == tool_id))
        for arg in args_result.scalars().all():
            await db.delete(arg)
        
        # Add new arguments
        for i, arg_data in enumerate(request.arguments):
            arg = ToolArgument(
                tool_id=tool_id,
                name=arg_data.name,
                label=arg_data.label,
                description=arg_data.description,
                field_type=arg_data.field_type,
                flag=arg_data.flag,
                placeholder=arg_data.placeholder,
                default_value=arg_data.default_value,
                tooltip=arg_data.tooltip,
                example=arg_data.example,
                is_required=arg_data.is_required,
                validation_regex=arg_data.validation_regex,
                options=arg_data.options,
                order=arg_data.order or i,
                group=arg_data.group,
                width=arg_data.width,
                is_advanced=arg_data.is_advanced,
                depends_on=arg_data.depends_on,
            )
            db.add(arg)
    
    await db.commit()
    await db.refresh(tool)
    return ToolResponse.model_validate(tool)


@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a tool (soft delete)."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    tool.is_active = False
    await db.commit()
    return {"message": "Tool deleted successfully"}


@router.post("/{tool_id}/favorite")
async def toggle_favorite(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Toggle tool favorite status."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    tool.is_favorite = not tool.is_favorite
    await db.commit()
    return {"is_favorite": tool.is_favorite}


@router.get("/{tool_id}/check-dependencies")
async def check_dependencies(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Check if tool dependencies are installed."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    deps = execution_engine.check_dependencies(tool.dependencies or [])
    exec_check = execution_engine.validate_executable(tool.executable_path)
    
    return {
        "executable": exec_check,
        "dependencies": deps,
        "all_satisfied": exec_check["valid"] and all(deps.values()),
    }


# --- Categories ---

@router.get("/categories/all", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all tool categories."""
    result = await db.execute(select(ToolCategory).order_by(ToolCategory.order))
    categories = result.scalars().all()
    
    responses = []
    for cat in categories:
        count_result = await db.execute(
            select(func.count(Tool.id)).where(Tool.category_id == cat.id, Tool.is_active == True)
        )
        count = count_result.scalar() or 0
        resp = CategoryResponse.model_validate(cat)
        resp.tool_count = count
        responses.append(resp)
    
    return responses


@router.post("/categories/create", response_model=CategoryResponse)
async def create_category(
    request: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new tool category."""
    category = ToolCategory(
        name=request.name,
        description=request.description,
        icon=request.icon,
        color=request.color,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    resp = CategoryResponse.model_validate(category)
    resp.tool_count = 0
    return resp
