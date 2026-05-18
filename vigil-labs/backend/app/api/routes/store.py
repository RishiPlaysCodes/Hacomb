"""
VIGIL LABS - Tool Store Routes
Browse, search, install, uninstall, and manage store tools.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.store import StoreTool, InstalledStoreTool
from app.services.tool_store import tool_store_service
from app.services.store_catalog import TOOL_CATALOG, STORE_CATEGORIES

router = APIRouter(prefix="/api/store", tags=["Tool Store"])


@router.get("/catalog")
async def get_catalog(
    category: Optional[str] = None,
    search: Optional[str] = None,
    installed_only: bool = False,
    featured_only: bool = False,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get tool store catalog with filtering."""
    query = select(StoreTool).where(StoreTool.is_active == True)
    
    if category:
        query = query.where(StoreTool.category == category)
    if featured_only:
        query = query.where(StoreTool.is_featured == True)
    if search:
        query = query.where(
            or_(
                StoreTool.name.ilike(f"%{search}%"),
                StoreTool.description.ilike(f"%{search}%"),
            )
        )
    
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    tools = result.scalars().all()
    
    # Get installed status for each tool
    installed_result = await db.execute(
        select(InstalledStoreTool).where(InstalledStoreTool.user_id == current_user["sub"])
    )
    installed_map = {i.store_tool_id: i for i in installed_result.scalars().all()}
    
    response = []
    for tool in tools:
        tool_dict = {
            "id": tool.id,
            "name": tool.name,
            "slug": tool.slug,
            "category": tool.category,
            "description": tool.description,
            "icon": tool.icon,
            "author": tool.author,
            "version": tool.version,
            "risk_level": tool.risk_level,
            "supports_linux": tool.supports_linux,
            "supports_windows": tool.supports_windows,
            "install_method": tool.install_method,
            "github_url": tool.github_url,
            "tags": tool.tags or [],
            "downloads": tool.downloads,
            "rating": tool.rating,
            "is_featured": tool.is_featured,
            "is_verified": tool.is_verified,
            "executable_name": tool.executable_name,
            "dependencies": tool.dependencies or [],
        }
        
        # Check installation status
        installed = installed_map.get(tool.id)
        if installed:
            tool_dict["install_status"] = installed.status
            tool_dict["is_enabled"] = installed.is_enabled
            tool_dict["installed_version"] = installed.installed_version
        else:
            # Check if system has it
            check = tool_store_service.check_installed(tool.executable_name or tool.slug)
            tool_dict["install_status"] = "available" if check["installed"] else "not_installed"
            tool_dict["is_enabled"] = check["installed"]
            tool_dict["system_path"] = check.get("path")
        
        response.append(tool_dict)
    
    if installed_only:
        response = [t for t in response if t["install_status"] in ("installed", "available")]
    
    return {"tools": response, "total": len(response)}


@router.get("/categories")
async def get_categories():
    """Get all store categories with metadata."""
    return STORE_CATEGORIES


@router.get("/platform")
async def get_platform_info(current_user: dict = Depends(get_current_user)):
    """Get current platform capabilities."""
    return tool_store_service.get_platform_info()


@router.post("/install/{tool_id}")
async def install_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Install a tool from the store."""
    result = await db.execute(select(StoreTool).where(StoreTool.id == tool_id))
    store_tool = result.scalar_one_or_none()
    if not store_tool:
        raise HTTPException(status_code=404, detail="Tool not found in store")
    
    # Check if already installed
    existing = await db.execute(
        select(InstalledStoreTool).where(
            InstalledStoreTool.store_tool_id == tool_id,
            InstalledStoreTool.user_id == current_user["sub"],
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tool already installed")
    
    # Create installation record
    installed = InstalledStoreTool(
        store_tool_id=tool_id,
        user_id=current_user["sub"],
        status="installing",
        installed_version=store_tool.version,
    )
    db.add(installed)
    await db.commit()
    
    # Run installation
    tool_data = {
        "name": store_tool.name,
        "executable_name": store_tool.executable_name,
        "install_method": store_tool.install_method,
        "install_command_linux": store_tool.install_command_linux,
        "install_command_windows": store_tool.install_command_windows,
        "github_repo": store_tool.github_repo,
    }
    
    install_result = await tool_store_service.install_tool(tool_data)
    
    if install_result["success"]:
        installed.status = "installed"
        check = tool_store_service.check_installed(store_tool.executable_name or store_tool.slug)
        installed.executable_path = check.get("path")
        store_tool.downloads += 1
    else:
        installed.status = "failed"
    
    await db.commit()
    
    return {
        "success": install_result["success"],
        "tool_name": store_tool.name,
        "status": installed.status,
        "details": install_result,
    }


@router.post("/uninstall/{tool_id}")
async def uninstall_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Uninstall a tool."""
    result = await db.execute(select(StoreTool).where(StoreTool.id == tool_id))
    store_tool = result.scalar_one_or_none()
    if not store_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    tool_data = {
        "name": store_tool.name,
        "executable_name": store_tool.executable_name,
        "install_method": store_tool.install_method,
    }
    
    uninstall_result = await tool_store_service.uninstall_tool(tool_data)
    
    # Remove installation record
    installed = await db.execute(
        select(InstalledStoreTool).where(
            InstalledStoreTool.store_tool_id == tool_id,
            InstalledStoreTool.user_id == current_user["sub"],
        )
    )
    record = installed.scalar_one_or_none()
    if record:
        await db.delete(record)
        await db.commit()
    
    return uninstall_result


@router.post("/toggle/{tool_id}")
async def toggle_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Enable/disable a tool."""
    result = await db.execute(
        select(InstalledStoreTool).where(
            InstalledStoreTool.store_tool_id == tool_id,
            InstalledStoreTool.user_id == current_user["sub"],
        )
    )
    installed = result.scalar_one_or_none()
    if not installed:
        raise HTTPException(status_code=404, detail="Tool not installed")
    
    installed.is_enabled = not installed.is_enabled
    await db.commit()
    return {"is_enabled": installed.is_enabled}


@router.post("/seed")
async def seed_catalog(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Seed the store catalog with preconfigured tools (admin only)."""
    count = 0
    for tool_data in TOOL_CATALOG:
        existing = await db.execute(
            select(StoreTool).where(StoreTool.slug == tool_data["slug"])
        )
        if existing.scalar_one_or_none():
            continue
        
        store_tool = StoreTool(
            name=tool_data["name"],
            slug=tool_data["slug"],
            category=tool_data["category"],
            description=tool_data.get("description", ""),
            executable_name=tool_data.get("executable_name"),
            install_method=tool_data.get("install_method", "manual"),
            install_command_linux=tool_data.get("install_command_linux"),
            install_command_windows=tool_data.get("install_command_windows"),
            github_repo=tool_data.get("github_repo"),
            github_url=tool_data.get("github_url"),
            risk_level=tool_data.get("risk_level", "medium"),
            supports_linux=tool_data.get("supports_linux", True),
            supports_windows=tool_data.get("supports_windows", False),
            tags=tool_data.get("tags", []),
            is_featured=tool_data.get("is_featured", False),
            is_verified=True,
        )
        db.add(store_tool)
        count += 1
    
    await db.commit()
    return {"message": f"Seeded {count} tools into the store catalog"}


@router.get("/check-all")
async def check_all_installed(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Check which catalog tools are already installed on the system."""
    result = await db.execute(select(StoreTool).where(StoreTool.is_active == True))
    tools = result.scalars().all()
    
    status = []
    for tool in tools:
        check = tool_store_service.check_installed(tool.executable_name or tool.slug)
        status.append({
            "id": tool.id,
            "name": tool.name,
            "slug": tool.slug,
            "installed": check["installed"],
            "path": check.get("path"),
        })
    
    installed_count = sum(1 for s in status if s["installed"])
    return {
        "tools": status,
        "total": len(status),
        "installed": installed_count,
        "missing": len(status) - installed_count,
    }
