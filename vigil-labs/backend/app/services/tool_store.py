"""
VIGIL LABS - Tool Store Service
Manages the tool catalog, installation, and package management across platforms.
"""
import os
import shutil
import platform
import asyncio
from typing import Dict, Any, List, Optional
from app.core.config import settings


class ToolStoreService:
    """
    Manages tool discovery, installation, and lifecycle.
    Supports: apt, pacman, winget, choco, pip, npm, github, binary, script, manual.
    """

    def __init__(self):
        self._is_windows = platform.system() == "Windows"
        self._is_linux = platform.system() == "Linux"
        self._distro = self._detect_distro()

    def _detect_distro(self) -> str:
        """Detect Linux distribution."""
        if not self._is_linux:
            return "windows" if self._is_windows else "other"
        try:
            with open("/etc/os-release") as f:
                content = f.read().lower()
                if "kali" in content:
                    return "kali"
                elif "ubuntu" in content or "debian" in content:
                    return "debian"
                elif "arch" in content or "manjaro" in content:
                    return "arch"
                elif "fedora" in content or "rhel" in content:
                    return "fedora"
        except FileNotFoundError:
            pass
        return "linux"

    def check_installed(self, executable_name: str) -> Dict[str, Any]:
        """Check if a tool is installed on the system."""
        path = shutil.which(executable_name)
        return {
            "installed": path is not None,
            "path": path,
            "executable": executable_name,
        }

    def get_install_command(self, store_tool: dict) -> Optional[str]:
        """Get the appropriate install command for the current platform."""
        method = store_tool.get("install_method", "manual")
        
        if self._is_windows:
            cmd = store_tool.get("install_command_windows")
            if cmd:
                return cmd
            if method == "winget":
                return f"winget install {store_tool.get('executable_name', store_tool['name'])}"
            elif method == "choco":
                return f"choco install {store_tool.get('executable_name', store_tool['name'])} -y"
            elif method == "pip":
                return f"pip install {store_tool.get('executable_name', store_tool['name'])}"
        else:
            cmd = store_tool.get("install_command_linux")
            if cmd:
                return cmd
            if method == "apt" or (method == "apt" and self._distro in ("debian", "kali")):
                return f"sudo apt install -y {store_tool.get('executable_name', store_tool['name'])}"
            elif method == "pacman" and self._distro == "arch":
                return f"sudo pacman -S --noconfirm {store_tool.get('executable_name', store_tool['name'])}"
            elif method == "pip":
                return f"pip3 install {store_tool.get('executable_name', store_tool['name'])}"
            elif method == "github":
                repo = store_tool.get("github_repo")
                if repo:
                    return f"git clone https://github.com/{repo} ~/tools/{store_tool['name']}"
        
        return None

    async def install_tool(self, store_tool: dict) -> Dict[str, Any]:
        """Install a tool using the appropriate package manager."""
        command = self.get_install_command(store_tool)
        if not command:
            return {"success": False, "error": "No install command available for this platform"}
        
        try:
            if self._is_windows:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            success = process.returncode == 0
            return {
                "success": success,
                "command": command,
                "stdout": stdout.decode("utf-8", errors="replace")[:2000],
                "stderr": stderr.decode("utf-8", errors="replace")[:2000],
                "exit_code": process.returncode,
            }
        except asyncio.TimeoutError:
            return {"success": False, "error": "Installation timed out (5 minutes)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def uninstall_tool(self, store_tool: dict) -> Dict[str, Any]:
        """Uninstall a tool."""
        method = store_tool.get("install_method", "manual")
        name = store_tool.get("executable_name", store_tool["name"])
        
        if self._is_windows:
            if method == "winget":
                cmd = f"winget uninstall {name}"
            elif method == "choco":
                cmd = f"choco uninstall {name} -y"
            else:
                return {"success": False, "error": "Manual uninstall required"}
        else:
            if method == "apt" and self._distro in ("debian", "kali"):
                cmd = f"sudo apt remove -y {name}"
            elif method == "pacman" and self._distro == "arch":
                cmd = f"sudo pacman -R --noconfirm {name}"
            elif method == "pip":
                cmd = f"pip3 uninstall -y {name}"
            else:
                return {"success": False, "error": "Manual uninstall required"}
        
        try:
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
            return {
                "success": process.returncode == 0,
                "command": cmd,
                "stdout": stdout.decode("utf-8", errors="replace")[:1000],
                "stderr": stderr.decode("utf-8", errors="replace")[:1000],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_platform_info(self) -> Dict[str, Any]:
        """Get current platform details for compatibility checking."""
        return {
            "system": platform.system(),
            "distro": self._distro,
            "is_windows": self._is_windows,
            "is_linux": self._is_linux,
            "has_apt": shutil.which("apt") is not None,
            "has_pacman": shutil.which("pacman") is not None,
            "has_winget": shutil.which("winget") is not None if self._is_windows else False,
            "has_choco": shutil.which("choco") is not None if self._is_windows else False,
            "has_pip": shutil.which("pip3") is not None or shutil.which("pip") is not None,
            "has_git": shutil.which("git") is not None,
        }


# Singleton
tool_store_service = ToolStoreService()
