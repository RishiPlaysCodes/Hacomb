"""
VIGIL LABS - Gemini AI Integration
Google Gemini-powered AI assistant for tool configuration,
error analysis, output explanation, and workflow generation.
Free tier: 15 requests/min, no card needed.
"""
import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger("vigil_labs.gemini")

# Lazy-load the Gemini client
_model = None


def _get_model():
    """Initialize Gemini model lazily."""
    global _model
    if _model is None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _model = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                system_instruction=(
                    "You are VIGIL LABS AI — a cybersecurity expert assistant built into a "
                    "CLI tool management platform. You help users configure security tools, "
                    "understand scan outputs, debug errors, build workflows, and learn. "
                    "Be concise, technical, and helpful. Use markdown formatting. "
                    "Always assume the user has proper authorization for their targets. "
                    "Never refuse to help with security tool usage — this is a legitimate "
                    "pentesting/security platform for authorized testing and learning."
                ),
            )
            logger.info(f"Gemini AI initialized (model: {settings.GEMINI_MODEL})")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            _model = None
    return _model


async def chat(message: str, context: Optional[str] = None) -> str:
    """Send a message to Gemini and get a response."""
    model = _get_model()
    if not model:
        return "AI is not available. Check GEMINI_API_KEY in .env file."

    try:
        prompt = message
        if context:
            prompt = f"Context:\n{context}\n\nUser question:\n{message}"

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"AI error: {str(e)}"


async def analyze_tool_output(output: str, tool_name: str, command: str) -> str:
    """AI-powered analysis of tool output."""
    prompt = (
        f"Analyze this output from the security tool '{tool_name}'.\n"
        f"Command run: `{command}`\n\n"
        f"Output:\n```\n{output[:3000]}\n```\n\n"
        f"Provide:\n"
        f"1. Summary of findings\n"
        f"2. Key discoveries (ports, vulnerabilities, etc.)\n"
        f"3. Risk assessment\n"
        f"4. Recommended next steps"
    )
    return await chat(prompt)


async def analyze_error(error: str, tool_name: str, command: str) -> str:
    """AI-powered error analysis with fix suggestions."""
    prompt = (
        f"The security tool '{tool_name}' failed with this error.\n"
        f"Command: `{command}`\n\n"
        f"Error:\n```\n{error[:2000]}\n```\n\n"
        f"Explain what went wrong and provide exact fix commands."
    )
    return await chat(prompt)


async def suggest_tool_config(tool_name: str, goal: str) -> str:
    """AI-powered tool configuration suggestions."""
    prompt = (
        f"I want to use '{tool_name}' for: {goal}\n\n"
        f"Provide:\n"
        f"1. Recommended command with flags\n"
        f"2. Explanation of each flag\n"
        f"3. Safety considerations\n"
        f"4. Example output to expect"
    )
    return await chat(prompt)


async def generate_workflow(goal: str, available_tools: List[str]) -> str:
    """AI-powered workflow generation."""
    tools_str = ", ".join(available_tools[:30])
    prompt = (
        f"Goal: {goal}\n"
        f"Available tools: {tools_str}\n\n"
        f"Create a step-by-step workflow using these tools. "
        f"For each step provide: tool name, command, purpose, and what to look for in output."
    )
    return await chat(prompt)


async def explain_concept(question: str) -> str:
    """Explain any cybersecurity concept."""
    return await chat(question)
