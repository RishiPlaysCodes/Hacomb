"""
VIGIL LABS - Workflow Engine
Executes multi-step workflows with output piping between tools.
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from app.services.execution_engine import execution_engine


class WorkflowEngine:
    """Execute workflows as sequential pipelines with output piping."""

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
        """
        results = []
        previous_output = ""
        overall_status = "completed"
        start_time = datetime.utcnow()

        for i, step in enumerate(steps):
            step_start = datetime.utcnow()
            
            if on_step_start:
                await on_step_start(workflow_id, i, step)
            
            # Build command for this step
            tool_id = step.get("tool_id")
            arguments = step.get("arguments", {})
            
            # If piping, add previous output as context
            if step.get("pipe_output") and previous_output and i > 0:
                # Store previous output in a temp context variable
                arguments["_previous_output"] = previous_output[:5000]
            
            # Execute step
            command = step.get("command", "")
            if not command:
                # Use tool's command template if available
                command = f"{step.get('executable', step.get('tool_name', ''))} {' '.join(str(v) for v in arguments.values() if v and not str(v).startswith('_'))}"
            
            step_result = {
                "step_index": i,
                "tool_name": step.get("tool_name", ""),
                "command": command,
                "status": "running",
                "stdout": "",
                "stderr": "",
                "started_at": step_start.isoformat(),
            }

            try:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                stdout_data, stderr_data = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=step.get("timeout", 300),
                )
                
                stdout_text = stdout_data.decode("utf-8", errors="replace")
                stderr_text = stderr_data.decode("utf-8", errors="replace")
                
                step_result["stdout"] = stdout_text
                step_result["stderr"] = stderr_text
                step_result["exit_code"] = proc.returncode
                step_result["status"] = "completed" if proc.returncode == 0 else "failed"
                
                # Use stdout as input for next step
                if step.get("pipe_output"):
                    previous_output = stdout_text
                
                if on_step_output:
                    await on_step_output(workflow_id, i, stdout_text)

            except asyncio.TimeoutError:
                step_result["status"] = "timeout"
                step_result["stderr"] = "Step timed out"
                overall_status = "failed"
            except Exception as e:
                step_result["status"] = "failed"
                step_result["stderr"] = str(e)
                overall_status = "failed"
            
            step_end = datetime.utcnow()
            step_result["duration"] = (step_end - step_start).total_seconds()
            step_result["completed_at"] = step_end.isoformat()
            results.append(step_result)
            
            if on_step_complete:
                await on_step_complete(workflow_id, i, step_result)
            
            # Stop pipeline on failure unless configured otherwise
            if step_result["status"] != "completed" and not step.get("continue_on_error"):
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

        if on_workflow_complete:
            await on_workflow_complete(workflow_id, workflow_result)

        return workflow_result


# Singleton
workflow_engine = WorkflowEngine()
