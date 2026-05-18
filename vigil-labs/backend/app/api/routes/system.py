"""
VIGIL LABS - System Routes
System info, health checks, analytics, and AI assistant endpoints.
"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.execution_engine import execution_engine
from app.services.ai_assistant import ai_assistant

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/health")
async def health_check():
    """System health check."""
    return {"status": "healthy", "service": "VIGIL LABS"}


@router.get("/info")
async def system_info(current_user: dict = Depends(get_current_user)):
    """Get system information."""
    return execution_engine.get_system_info()


@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics."""
    return {
        "running_processes": execution_engine.running_count,
        "system": execution_engine.get_system_info(),
    }


@router.post("/ai/analyze-help")
async def ai_analyze_help(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI: Analyze tool help output."""
    return ai_assistant.analyze_tool_help(
        data.get("help_output", ""),
        data.get("tool_name", "unknown"),
    )


@router.post("/ai/analyze-error")
async def ai_analyze_error(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI: Analyze error output and suggest fixes."""
    return ai_assistant.analyze_error(
        data.get("error_output", ""),
        data.get("tool_name", "unknown"),
    )


@router.post("/ai/suggest-config")
async def ai_suggest_config(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI: Suggest tool configuration."""
    return ai_assistant.suggest_configuration(
        data.get("tool_name", ""),
        data.get("context", {}),
    )


@router.post("/ai/explain-command")
async def ai_explain_command(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI: Explain what a command does."""
    return {"explanation": ai_assistant.generate_command_explanation(data.get("command", ""))}


@router.post("/ai/check-dependencies")
async def ai_check_deps(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI: Check and report missing dependencies."""
    return {
        "missing": ai_assistant.detect_missing_dependencies(
            data.get("tool_name", ""),
            data.get("dependencies", []),
        )
    }
