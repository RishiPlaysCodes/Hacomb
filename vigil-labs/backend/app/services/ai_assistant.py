"""
VIGIL LABS - AI Assistant Service
Intelligent helper for tool understanding, configuration, and troubleshooting.
"""
import re
import subprocess
import platform
from typing import Optional, Dict, Any, List


class AIAssistant:
    """
    Local AI Assistant for VIGIL LABS.
    Provides intelligent guidance without requiring external API keys.
    Uses pattern matching, rule-based analysis, and heuristics.
    """

    def __init__(self):
        self._tool_knowledge_base = self._build_knowledge_base()

    def analyze_tool_help(self, help_output: str, tool_name: str) -> Dict[str, Any]:
        """Analyze --help output and extract tool arguments automatically."""
        arguments = []
        
        # Parse common patterns in help output
        # Pattern: -flag, --long-flag VALUE  description
        flag_pattern = r'^\s*(-\w),?\s*(--[\w-]+)\s*(?:[\s=](\w+))?\s+(.*?)$'
        long_pattern = r'^\s*(--[\w-]+)\s*(?:[\s=](\w+))?\s+(.*?)$'
        short_pattern = r'^\s*(-\w)\s*(?:[\s=](\w+))?\s+(.*?)$'
        
        lines = help_output.split('\n')
        
        for line in lines:
            match = re.match(flag_pattern, line, re.MULTILINE)
            if match:
                short_flag, long_flag, value_hint, description = match.groups()
                arg = self._create_argument_from_flag(
                    short_flag, long_flag, value_hint, description, tool_name
                )
                if arg:
                    arguments.append(arg)
                continue
            
            match = re.match(long_pattern, line)
            if match:
                long_flag, value_hint, description = match.groups()
                arg = self._create_argument_from_flag(
                    None, long_flag, value_hint, description, tool_name
                )
                if arg:
                    arguments.append(arg)
                continue
            
            match = re.match(short_pattern, line)
            if match:
                short_flag, value_hint, description = match.groups()
                arg = self._create_argument_from_flag(
                    short_flag, None, value_hint, description, tool_name
                )
                if arg:
                    arguments.append(arg)
        
        return {
            "tool_name": tool_name,
            "arguments": arguments,
            "raw_sections": self._parse_help_sections(help_output),
        }

    def explain_argument(self, argument_name: str, tool_name: str) -> str:
        """Provide explanation for a tool argument."""
        explanations = {
            "target": "The target IP address, hostname, or URL to scan/connect to.",
            "port": "Network port number (1-65535) for the connection.",
            "output": "File path where results will be saved.",
            "wordlist": "Path to a wordlist file for brute-force or dictionary attacks.",
            "interface": "Network interface to use (e.g., eth0, wlan0).",
            "timeout": "Maximum time to wait for a response in seconds.",
            "threads": "Number of concurrent threads for parallel execution.",
            "verbose": "Enable detailed output for debugging.",
        }
        
        # Check common patterns
        arg_lower = argument_name.lower()
        for key, explanation in explanations.items():
            if key in arg_lower:
                return explanation
        
        return f"Argument '{argument_name}' for {tool_name}. Check tool documentation for details."

    def suggest_configuration(self, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest safe default configuration for a tool."""
        suggestions = {
            "general": {
                "recommendation": "Start with conservative settings and increase intensity gradually.",
                "timeout": 30,
                "threads": 4,
            },
            "scanning": {
                "recommendation": "Use targeted scans rather than broad sweeps.",
                "rate_limit": True,
                "log_output": True,
            },
        }
        
        return {
            "tool": tool_name,
            "suggestions": suggestions.get("general", {}),
            "safety_notes": [
                "Always ensure you have authorization before scanning targets.",
                "Start with low intensity settings.",
                "Monitor system resources during execution.",
                "Save output to files for later analysis.",
            ],
        }

    def analyze_error(self, error_output: str, tool_name: str) -> Dict[str, Any]:
        """Analyze error output and provide fixes."""
        fixes = []
        
        error_lower = error_output.lower()
        
        if "permission denied" in error_lower:
            fixes.append({
                "issue": "Permission denied",
                "fix": "Run with elevated privileges (sudo) or check file permissions.",
                "severity": "medium",
            })
        
        if "command not found" in error_lower or "not recognized" in error_lower:
            fixes.append({
                "issue": "Tool not installed",
                "fix": f"Install {tool_name} or verify it's in your PATH.",
                "severity": "high",
            })
        
        if "connection refused" in error_lower or "connection timed out" in error_lower:
            fixes.append({
                "issue": "Connection failed",
                "fix": "Check target availability, network connection, and firewall settings.",
                "severity": "medium",
            })
        
        if "no such file" in error_lower or "file not found" in error_lower:
            fixes.append({
                "issue": "File not found",
                "fix": "Verify the file path exists and is accessible.",
                "severity": "medium",
            })
        
        if "out of memory" in error_lower or "memory" in error_lower:
            fixes.append({
                "issue": "Memory issue",
                "fix": "Reduce thread count or scan scope. Close unnecessary applications.",
                "severity": "high",
            })
        
        if not fixes:
            fixes.append({
                "issue": "Unrecognized error",
                "fix": "Review the full error output and check tool documentation.",
                "severity": "low",
            })
        
        return {
            "tool": tool_name,
            "analysis": fixes,
            "raw_error": error_output[:500],
        }

    def generate_command_explanation(self, command: str) -> str:
        """Explain what a command does in plain language."""
        parts = command.split()
        if not parts:
            return "Empty command"
        
        executable = parts[0]
        explanation_parts = [f"Runs '{executable}'"]
        
        for i, part in enumerate(parts[1:], 1):
            if part.startswith('-'):
                if i + 1 < len(parts) and not parts[i].startswith('-'):
                    explanation_parts.append(f"with option {part} set to '{parts[i]}'")
                else:
                    explanation_parts.append(f"with flag {part} enabled")
        
        return " ".join(explanation_parts)

    def detect_missing_dependencies(self, tool_name: str, dependencies: List[str]) -> List[Dict[str, Any]]:
        """Check and report missing dependencies."""
        import shutil
        missing = []
        
        for dep in dependencies:
            if not shutil.which(dep):
                install_hint = self._get_install_hint(dep)
                missing.append({
                    "dependency": dep,
                    "installed": False,
                    "install_command": install_hint,
                })
        
        return missing

    def _create_argument_from_flag(
        self, short_flag, long_flag, value_hint, description, tool_name
    ) -> Optional[Dict]:
        """Create an argument definition from parsed flag info."""
        if not (short_flag or long_flag):
            return None
        
        flag = long_flag or short_flag
        name = (long_flag or short_flag).lstrip('-').replace('-', '_')
        
        # Determine field type from hints
        field_type = "text"
        if value_hint:
            hint_lower = value_hint.lower() if value_hint else ""
            if hint_lower in ("file", "path"):
                field_type = "file"
            elif hint_lower in ("dir", "directory"):
                field_type = "folder"
            elif hint_lower in ("port", "ports"):
                field_type = "port"
            elif hint_lower in ("host", "ip", "target"):
                field_type = "ip"
            elif hint_lower in ("num", "number", "count"):
                field_type = "number"
        
        # Check if it's a boolean flag (no value)
        if not value_hint and description:
            field_type = "toggle"
        
        return {
            "name": name,
            "label": name.replace('_', ' ').title(),
            "flag": flag,
            "field_type": field_type,
            "description": description.strip() if description else "",
            "is_required": False,
        }

    def _parse_help_sections(self, help_text: str) -> Dict[str, str]:
        """Parse help output into sections."""
        sections = {}
        current_section = "description"
        current_content = []
        
        for line in help_text.split('\n'):
            if line.strip().endswith(':') and not line.startswith(' '):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip().rstrip(':').lower()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _get_install_hint(self, dependency: str) -> str:
        """Get installation command hint for a dependency."""
        if platform.system() == "Linux":
            return f"sudo apt install {dependency} OR sudo pacman -S {dependency}"
        elif platform.system() == "Windows":
            return f"choco install {dependency} OR winget install {dependency}"
        return f"Install {dependency} using your package manager"

    def _build_knowledge_base(self) -> Dict[str, Any]:
        """Build initial knowledge base for common tools."""
        return {
            "nmap": {
                "category": "Network Scanning",
                "description": "Network discovery and security auditing tool",
                "common_args": ["target", "ports", "scan_type", "output"],
            },
            "hydra": {
                "category": "Password Cracking",
                "description": "Network login cracker supporting numerous protocols",
                "common_args": ["target", "username", "wordlist", "protocol"],
            },
            "ffuf": {
                "category": "Web Fuzzing",
                "description": "Fast web fuzzer",
                "common_args": ["url", "wordlist", "method", "output"],
            },
        }


# Singleton instance
ai_assistant = AIAssistant()
