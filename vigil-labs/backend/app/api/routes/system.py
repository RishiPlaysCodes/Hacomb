"""
VIGIL LABS - System Routes
System info, health checks, analytics, and AI agent endpoints.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.core.security import get_current_user
from app.services.execution_engine import execution_engine
from app.services.ai_assistant import ai_assistant
from app.services.ai_agent import ai_agent

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



# ─── AI AGENT ENDPOINTS ─────────────────────────────────────────────────────


@router.post("/ai/understand-goal")
async def ai_understand_goal(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI Agent: Understand user's goal and recommend approach."""
    return ai_agent.understand_goal(data.get("goal", ""))


@router.post("/ai/generate-workflow")
async def ai_generate_workflow(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI Agent: Auto-generate a workflow from a goal."""
    return ai_agent.generate_workflow(
        data.get("goal", ""),
        data.get("available_tools", []),
    )


@router.post("/ai/recommend-tools")
async def ai_recommend_tools(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI Agent: Recommend tools for a task."""
    return ai_agent.recommend_tools(
        data.get("task", ""),
        data.get("context", {}),
    )


@router.post("/ai/explain-output")
async def ai_explain_output(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI Agent: Explain tool output in simple language."""
    return ai_agent.explain_output(
        data.get("output", ""),
        data.get("tool_name", "unknown"),
        data.get("command", ""),
    )


@router.post("/ai/analyze-error-advanced")
async def ai_analyze_error_adv(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI Agent: Advanced error analysis with auto-fix suggestions."""
    return ai_agent.analyze_error_advanced(
        data.get("error", ""),
        data.get("tool_name", "unknown"),
        data.get("command", ""),
    )


@router.post("/ai/generate-report")
async def ai_generate_report(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI Agent: Generate professional report from executions."""
    return {"report": ai_agent.generate_report(
        data.get("executions", []),
        data.get("workflow_name"),
    )}


@router.post("/ai/auto-analyze-tool")
async def ai_auto_analyze_tool(
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """AI Agent: Auto-analyze a tool by running --help and generating config."""
    return await ai_agent.auto_analyze_tool(data.get("executable", ""))
