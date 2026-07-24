"""
VIGIL LABS - Workflow Engine
Executes multi-step workflows using the validated execution engine.
All commands go through the same security checks as individual tool execution.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from app.core.config import settings
from app.core.security import validate_command_safety

logger = logging.getLogger("vigil_labs.workflow")


class WorkflowEngine:
    """
    Execute workflows as sequential pipelines with output piping.
    All execution goes through security validation.
    """

    async def run_workflow(
        self,
        steps: List[Dict[str, Any]],
        workflow_id: str,
        user_id: str,
        on_step_start: Optional[Callable] = None,
        on_step_output: Optional[Callable] = None,
        on_step_complete: Optional[Callable] = None,
        on_workflow_complete: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Execute workflow steps sequentially.
        If pipe_output is True, previous step's stdout is passed as input context.
        
        SECURITY: All commands are validated before execution.
        """
        results = []
        previous_output = ""
        overall_status = "completed"
        start_time = datetime.utcnow()

        logger.info(f"Starting workflow {workflow_id} with {len(steps)} steps for user {user_id}")

        for i, step in enumerate(steps):
            step_start = datetime.utcnow()
            
            if on_step_start:
                await on_step_start(workflow_id, i, step)
            
            # Build command for this step
            arguments = step.get("arguments", {})
            
            # If piping, add previous output as context (limited size)
            if step.get("pipe_output") and previous_output and i > 0:
                arguments["_previous_output"] = previous_output[:5000]
            
            # Get command
            command = step.get("command", "")
            if not command:
                tool_name = step.get("executable", step.get("tool_name", ""))
                if not tool_name:
                    results.append({
                        "step_index": i,
                        "tool_name": "",
                        "command": "",
                        "status": "failed",
                        "stderr": "No command or tool specified for this step",
                        "started_at": step_start.isoformat(),
                        "completed_at": datetime.utcnow().isoformat(),
                        "duration": 0,
                    })
                    overall_status = "failed"
                    if not step.get("continue_on_error"):
                        break
                    continue
                
                # Build command from tool name and arguments safely
                import shlex
                arg_parts = []
                for key, val in arguments.items():
                    if key.startswith("_"):
                        continue  # Skip internal variables
                    if val:
                        arg_parts.append(shlex.quote(str(val)))
                command = f"{shlex.quote(tool_name)} {' '.join(arg_parts)}"
            
            # SECURITY: Validate command safety before execution
            is_safe, reason = validate_command_safety(command)
            if not is_safe:
                logger.warning(
                    f"Workflow {workflow_id} step {i} blocked: {reason} (command: {command})"
                )
                step_result = {
                    "step_index": i,
                    "tool_name": step.get("tool_name", ""),
                    "command": command,
                    "status": "blocked",
                    "stderr": f"Command blocked for security: {reason}",
                    "started_at": step_start.isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "duration": 0,
                }
                results.append(step_result)
                overall_status = "failed"
                
                if on_step_complete:
                    await on_step_complete(workflow_id, i, step_result)
                
                if not step.get("continue_on_error"):
                    break
                continue
            
            step_result = {
                "step_index": i,
                "tool_name": step.get("tool_name", ""),
                "command": command,
                "status": "running",
                "stdout": "",
                "stderr": "",
                "started_at": step_start.isoformat(),
            }

            # Enforce timeout limits
            step_timeout = min(
                step.get("timeout", settings.DEFAULT_TIMEOUT),
                settings.MAX_TIMEOUT,
            )

            try:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                stdout_data, stderr_data = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=step_timeout,
                )
                
                stdout_text = stdout_data.decode("utf-8", errors="replace")
                stderr_text = stderr_data.decode("utf-8", errors="replace")
                
                # Limit output size to prevent memory issues
                max_output = settings.MAX_OUTPUT_SIZE
                step_result["stdout"] = stdout_text[:max_output]
                step_result["stderr"] = stderr_text[:max_output]
                step_result["exit_code"] = proc.returncode
                step_result["status"] = "completed" if proc.returncode == 0 else "failed"
                
                # Use stdout as input for next step
                if step.get("pipe_output"):
                    previous_output = stdout_text
                
                if on_step_output:
                    await on_step_output(workflow_id, i, stdout_text[:max_output])

            except asyncio.TimeoutError:
                step_result["status"] = "timeout"
                step_result["stderr"] = f"Step timed out after {step_timeout}s"
                overall_status = "failed"
                logger.warning(f"Workflow {workflow_id} step {i} timed out after {step_timeout}s")
            except Exception as e:
                step_result["status"] = "failed"
                step_result["stderr"] = str(e)
                overall_status = "failed"
                logger.error(f"Workflow {workflow_id} step {i} error: {e}")
            
            step_end = datetime.utcnow()
            step_result["duration"] = (step_end - step_start).total_seconds()
            step_result["completed_at"] = step_end.isoformat()
            results.append(step_result)
            
            if on_step_complete:
                await on_step_complete(workflow_id, i, step_result)
            
            # Stop pipeline on failure unless configured otherwise
            if step_result["status"] not in ("completed",) and not step.get("continue_on_error"):
                overall_status = "failed"
                break

        end_time = datetime.utcnow()
        
        workflow_result = {
            "workflow_id": workflow_id,
            "status": overall_status,
            "steps_completed": len(results),
            "total_steps": len(steps),
            "results": results,
            "duration": (end_time - start_time).total_seconds(),
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
        }

        logger.info(
            f"Workflow {workflow_id} {overall_status}: "
            f"{len(results)}/{len(steps)} steps in {workflow_result['duration']:.1f}s"
        )

        if on_workflow_complete:
            await on_workflow_complete(workflow_id, workflow_result)

        return workflow_result


# Singleton
workflow_engine = WorkflowEngine()
