"""
VIGIL LABS - Execution Engine
Safe command generation, validation, templating, and cross-platform execution.
Includes command injection prevention and security validation.
"""
import os
import re
import asyncio
import shlex
import signal
import logging
import platform
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
import psutil

from app.core.config import settings
from app.core.security import sanitize_command_input, validate_command_safety

logger = logging.getLogger("vigil_labs.execution")


@dataclass
class ProcessInfo:
    """Track running process information."""
    pid: int
    execution_id: str
    tool_id: str
    user_id: str
    process: asyncio.subprocess.Process
    started_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "running"


class ExecutionEngine:
    """
    Core execution engine for VIGIL LABS.
    Handles safe command generation, validation, and cross-platform execution.
    """

    def __init__(self):
        self._running_processes: Dict[str, ProcessInfo] = {}
        self._is_windows = platform.system() == "Windows"

    @property
    def running_count(self) -> int:
        return len(self._running_processes)

    def validate_executable(self, executable_path: str) -> Dict[str, Any]:
        """Validate that an executable exists and is accessible."""
        result = {"valid": False, "message": "", "path": executable_path}
        
        # Check if it's a command in PATH
        import shutil
        which_result = shutil.which(executable_path)
        if which_result:
            result["valid"] = True
            result["path"] = which_result
            result["message"] = f"Found at: {which_result}"
            return result
        
        # Check absolute path
        if os.path.isfile(executable_path):
            if os.access(executable_path, os.X_OK):
                result["valid"] = True
                result["message"] = "Executable found and accessible"
            else:
                result["message"] = "File exists but is not executable"
        else:
            result["message"] = f"Executable not found: {executable_path}"
        
        return result

    def validate_arguments(self, arguments: Dict[str, Any], tool_args: list) -> Dict[str, Any]:
        """Validate provided arguments against tool argument definitions."""
        errors = []
        warnings = []
        
        arg_defs = {arg.name: arg for arg in tool_args}
        
        # Check required arguments
        for name, arg_def in arg_defs.items():
            if arg_def.is_required and name not in arguments:
                errors.append(f"Required argument '{arg_def.label}' is missing")
            
            if name in arguments:
                value = arguments[name]
                # Type validation
                if arg_def.field_type in ("ip", "ip_range"):
                    if not self._validate_ip(str(value)):
                        errors.append(f"Invalid IP address in '{arg_def.label}': {value}")
                
                elif arg_def.field_type == "port":
                    if not self._validate_port(value):
                        errors.append(f"Invalid port in '{arg_def.label}': {value}")
                
                elif arg_def.field_type in ("file", "wordlist"):
                    if value and not os.path.isfile(str(value)):
                        warnings.append(f"File not found for '{arg_def.label}': {value}")
                
                elif arg_def.field_type == "folder":
                    if value and not os.path.isdir(str(value)):
                        warnings.append(f"Directory not found for '{arg_def.label}': {value}")
                
                # Regex validation
                if arg_def.validation_regex and value:
                    if not re.match(arg_def.validation_regex, str(value)):
                        errors.append(f"Invalid format for '{arg_def.label}'")
                
                # Length validation
                if arg_def.min_length and len(str(value)) < arg_def.min_length:
                    errors.append(f"'{arg_def.label}' must be at least {arg_def.min_length} characters")
                if arg_def.max_length and len(str(value)) > arg_def.max_length:
                    errors.append(f"'{arg_def.label}' must not exceed {arg_def.max_length} characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def build_command(self, template: str, executable: str, arguments: Dict[str, Any], tool_args: list) -> str:
        """
        Build the final command from template and arguments.
        Template format: {executable} {args}
        Argument placeholders: {{arg_name}}
        
        SECURITY: All values are sanitized and shell-escaped.
        """
        command = template
        
        # SECURITY: Validate executable path
        validation = self.validate_executable(executable)
        if not validation["valid"]:
            raise ValueError(f"Invalid executable: {validation['message']}")
        
        # Replace executable placeholder
        safe_executable = self._escape_value(executable)
        command = command.replace("{executable}", safe_executable)
        command = command.replace("{{executable}}", safe_executable)
        
        # Build argument string from definitions
        arg_parts = []
        arg_defs = {arg.name: arg for arg in tool_args}
        
        for name, value in arguments.items():
            if not value and value != 0:
                continue
                
            arg_def = arg_defs.get(name)
            if not arg_def:
                continue
            
            # SECURITY: Sanitize input value
            str_value = str(value)
            try:
                str_value = sanitize_command_input(str_value)
            except ValueError as e:
                raise ValueError(f"Invalid input for '{arg_def.label}': {e}")
            
            # Handle different field types
            if arg_def.field_type == "checkbox" or arg_def.field_type == "toggle":
                if value:
                    if arg_def.flag:
                        arg_parts.append(arg_def.flag)
            elif arg_def.flag:
                safe_value = self._escape_value(str_value)
                arg_parts.append(f"{arg_def.flag} {safe_value}")
            else:
                safe_value = self._escape_value(str_value)
                arg_parts.append(safe_value)
        
        # Replace {args} placeholder
        args_string = " ".join(arg_parts)
        command = command.replace("{args}", args_string)
        command = command.replace("{{args}}", args_string)
        
        # Replace individual argument placeholders
        for name, value in arguments.items():
            placeholder = "{{" + name + "}}"
            if value:
                str_value = sanitize_command_input(str(value))
                safe_value = self._escape_value(str_value)
            else:
                safe_value = ""
            command = command.replace(placeholder, safe_value)
        
        # Clean up multiple spaces
        command = re.sub(r'\s+', ' ', command).strip()
        
        return command

    async def execute(
        self,
        command: str,
        execution_id: str,
        tool_id: str,
        user_id: str,
        working_directory: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        timeout: int = 300,
        on_stdout: Optional[Callable] = None,
        on_stderr: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
    ) -> ProcessInfo:
        """Execute a command asynchronously with streaming output."""
        
        # SECURITY: Validate command safety
        is_safe, reason = validate_command_safety(command)
        if not is_safe:
            logger.warning(f"Blocked unsafe command from user {user_id}: {reason}")
            raise RuntimeError(f"Command blocked: {reason}")
        
        # Enforce maximum timeout
        timeout = min(timeout, settings.MAX_TIMEOUT)
        
        # Check concurrent process limit
        if self.running_count >= settings.MAX_CONCURRENT_PROCESSES:
            raise RuntimeError(f"Maximum concurrent processes ({settings.MAX_CONCURRENT_PROCESSES}) reached")
        
        # Check for duplicate execution
        for proc_info in self._running_processes.values():
            if proc_info.tool_id == tool_id and proc_info.user_id == user_id and proc_info.status == "running":
                raise RuntimeError(f"Tool is already running (PID: {proc_info.pid})")
        
        # Prepare environment - sanitize
        env = os.environ.copy()
        if environment:
            # Only allow safe environment variable names
            for key, value in environment.items():
                if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key):
                    env[key] = str(value)
                else:
                    logger.warning(f"Skipping invalid env var name: {key}")
        
        # Prepare working directory - validate path
        cwd = None
        if working_directory and os.path.isdir(working_directory):
            # Prevent directory traversal
            real_path = os.path.realpath(working_directory)
            cwd = real_path
        
        logger.info(f"Executing: tool={tool_id}, user={user_id}, exec_id={execution_id}")
        
        # Execute
        if self._is_windows:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=cwd,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
        else:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=cwd,
                preexec_fn=os.setsid,
            )
        
        proc_info = ProcessInfo(
            pid=process.pid,
            execution_id=execution_id,
            tool_id=tool_id,
            user_id=user_id,
            process=process,
        )
        self._running_processes[execution_id] = proc_info
        
        # Start output streaming in background
        asyncio.create_task(
            self._stream_output(proc_info, timeout, on_stdout, on_stderr, on_complete)
        )
        
        return proc_info

    async def _stream_output(
        self,
        proc_info: ProcessInfo,
        timeout: int,
        on_stdout: Optional[Callable],
        on_stderr: Optional[Callable],
        on_complete: Optional[Callable],
    ):
        """Stream process output and handle completion."""
        process = proc_info.process
        
        async def read_stream(stream, callback, is_stderr=False):
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace")
                if callback:
                    await callback(proc_info.execution_id, decoded, is_stderr)
        
        try:
            # Create tasks for stdout and stderr
            stdout_task = asyncio.create_task(read_stream(process.stdout, on_stdout, False))
            stderr_task = asyncio.create_task(read_stream(process.stderr, on_stderr, True))
            
            # Wait with timeout
            await asyncio.wait_for(
                asyncio.gather(stdout_task, stderr_task, process.wait()),
                timeout=timeout
            )
            
            proc_info.status = "completed" if process.returncode == 0 else "failed"
            
        except asyncio.TimeoutError:
            proc_info.status = "timeout"
            await self.stop_process(proc_info.execution_id, force=True)
        
        except Exception as e:
            proc_info.status = "failed"
        
        finally:
            if on_complete:
                await on_complete(
                    proc_info.execution_id,
                    proc_info.status,
                    process.returncode
                )
            # Cleanup
            if proc_info.execution_id in self._running_processes:
                del self._running_processes[proc_info.execution_id]

    async def stop_process(self, execution_id: str, force: bool = False) -> bool:
        """Stop a running process gracefully or forcefully."""
        proc_info = self._running_processes.get(execution_id)
        if not proc_info or proc_info.status != "running":
            return False
        
        process = proc_info.process
        
        try:
            if self._is_windows:
                process.terminate()
            else:
                if force:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    # Wait briefly for graceful shutdown
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            
            proc_info.status = "stopped"
            return True
        except (ProcessLookupError, OSError):
            proc_info.status = "stopped"
            return True

    def get_process_info(self, execution_id: str) -> Optional[ProcessInfo]:
        """Get info about a running process."""
        return self._running_processes.get(execution_id)

    def get_all_running(self) -> list:
        """Get all running processes."""
        return [
            {
                "execution_id": p.execution_id,
                "tool_id": p.tool_id,
                "pid": p.pid,
                "status": p.status,
                "started_at": p.started_at.isoformat(),
            }
            for p in self._running_processes.values()
        ]

    def check_dependencies(self, dependencies: list) -> Dict[str, bool]:
        """Check if required dependencies are installed."""
        import shutil
        results = {}
        for dep in dependencies:
            results[dep] = shutil.which(dep) is not None
        return results

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for platform detection."""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_usage_percent": psutil.disk_usage('/').percent,
        }

    def _escape_value(self, value: str) -> str:
        """Safely escape a command argument value."""
        if self._is_windows:
            # Windows escaping
            if ' ' in value or '"' in value:
                return f'"{value}"'
            return value
        else:
            return shlex.quote(value)

    def _validate_ip(self, value: str) -> bool:
        """Validate IP address format."""
        parts = value.split('.')
        if len(parts) != 4:
            # Could be CIDR notation
            if '/' in value:
                ip_part, cidr = value.rsplit('/', 1)
                return self._validate_ip(ip_part) and cidr.isdigit() and 0 <= int(cidr) <= 32
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    def _validate_port(self, value: Any) -> bool:
        """Validate port number."""
        try:
            port = int(value)
            return 1 <= port <= 65535
        except (ValueError, TypeError):
            # Could be port range
            if isinstance(value, str) and '-' in value:
                parts = value.split('-')
                if len(parts) == 2:
                    try:
                        return 1 <= int(parts[0]) <= 65535 and 1 <= int(parts[1]) <= 65535
                    except ValueError:
                        pass
            return False


# Singleton instance
execution_engine = ExecutionEngine()
