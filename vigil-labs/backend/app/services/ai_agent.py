"""
VIGIL LABS - AI Automation Agent
Advanced intelligent agent that understands goals, recommends tool combinations,
builds workflows, explains outputs, detects issues, and generates reports.
"""
import re
import os
import shutil
import platform
import subprocess
import asyncio
from typing import Dict, Any, List, Optional
from app.services.store_catalog import TOOL_CATALOG


class AIAgent:
    """
    Advanced AI Agent for VIGIL LABS.
    Provides goal-based automation, workflow generation, tool recommendation,
    error analysis, output explanation, and professional report generation.
    """

    def __init__(self):
        self._knowledge = self._build_knowledge()
        self._workflow_templates = self._build_workflow_templates()

    # ─── GOAL UNDERSTANDING ─────────────────────────────────────────────

    def understand_goal(self, goal: str) -> Dict[str, Any]:
        """Understand user's goal and recommend approach."""
        goal_lower = goal.lower()
        recommendations = []
        workflows = []
        
        # Keyword-based intent detection
        intents = self._detect_intents(goal_lower)
        
        for intent in intents:
            if intent in self._knowledge:
                info = self._knowledge[intent]
                recommendations.append({
                    "intent": intent,
                    "description": info["description"],
                    "recommended_tools": info["tools"],
                    "suggested_workflow": info.get("workflow"),
                    "risk_level": info.get("risk", "medium"),
                    "tips": info.get("tips", []),
                })
        
        # Find matching workflow templates
        for template in self._workflow_templates:
            if any(kw in goal_lower for kw in template["keywords"]):
                workflows.append(template)
        
        return {
            "goal": goal,
            "understood_intents": intents,
            "recommendations": recommendations,
            "suggested_workflows": workflows[:3],
            "safety_notes": self._get_safety_notes(intents),
            "next_steps": self._suggest_next_steps(intents),
        }

    # ─── WORKFLOW GENERATION ─────────────────────────────────────────────

    def generate_workflow(self, goal: str, available_tools: List[str]) -> Dict[str, Any]:
        """Auto-generate a workflow based on the goal and available tools."""
        goal_lower = goal.lower()
        steps = []
        
        # Match against templates
        for template in self._workflow_templates:
            if any(kw in goal_lower for kw in template["keywords"]):
                for tool_name in template["tools"]:
                    # Check if tool is available
                    if tool_name.lower() in [t.lower() for t in available_tools]:
                        steps.append({
                            "tool_name": tool_name,
                            "purpose": self._get_tool_purpose(tool_name),
                            "pipe_output": True,
                            "estimated_duration": "30-120s",
                        })
                
                if steps:
                    return {
                        "name": template["name"],
                        "description": template["description"],
                        "steps": steps,
                        "total_tools": len(steps),
                        "estimated_time": f"{len(steps) * 60}-{len(steps) * 180}s",
                        "risk_level": template.get("risk", "medium"),
                        "requires_confirmation": template.get("risk", "medium") in ("high", "critical"),
                    }
        
        # Fallback: generate from intents
        intents = self._detect_intents(goal_lower)
        for intent in intents:
            if intent in self._knowledge:
                for tool in self._knowledge[intent]["tools"]:
                    if tool.lower() in [t.lower() for t in available_tools]:
                        steps.append({
                            "tool_name": tool,
                            "purpose": self._get_tool_purpose(tool),
                            "pipe_output": True,
                        })
        
        return {
            "name": f"Auto-generated: {goal[:50]}",
            "description": f"AI-generated workflow for: {goal}",
            "steps": steps[:6],
            "total_tools": len(steps[:6]),
            "requires_confirmation": True,
        }

    # ─── TOOL RECOMMENDATION ────────────────────────────────────────────

    def recommend_tools(self, task: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Recommend best tools for a specific task."""
        task_lower = task.lower()
        recommendations = []
        
        for tool in TOOL_CATALOG:
            score = 0
            name_lower = tool["name"].lower()
            desc_lower = tool.get("description", "").lower()
            tags = [t.lower() for t in tool.get("tags", [])]
            
            # Score based on keyword matches
            words = task_lower.split()
            for word in words:
                if word in name_lower:
                    score += 3
                if word in desc_lower:
                    score += 1
                if word in tags:
                    score += 2
                if word in tool.get("category", "").lower():
                    score += 2
            
            if score > 0:
                recommendations.append({
                    "name": tool["name"],
                    "category": tool["category"],
                    "description": tool.get("description", ""),
                    "score": score,
                    "risk_level": tool.get("risk_level", "medium"),
                    "install_method": tool.get("install_method", "manual"),
                })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:8]

    # ─── OUTPUT EXPLANATION ──────────────────────────────────────────────

    def explain_output(self, output: str, tool_name: str, command: str) -> Dict[str, Any]:
        """Explain tool output in simple language."""
        analysis = {
            "tool": tool_name,
            "command": command,
            "summary": "",
            "key_findings": [],
            "risk_items": [],
            "recommendations": [],
        }
        
        lines = output.split('\n')
        
        # Nmap output analysis
        if tool_name.lower() == "nmap":
            open_ports = [l for l in lines if '/tcp' in l and 'open' in l]
            analysis["summary"] = f"Found {len(open_ports)} open port(s)"
            for port_line in open_ports:
                analysis["key_findings"].append(f"Open port: {port_line.strip()}")
            if len(open_ports) > 10:
                analysis["risk_items"].append("Many open ports detected - review for unnecessary services")
            analysis["recommendations"].append("Run service version detection (-sV) for more details")
        
        # Generic analysis
        elif 'vulnerability' in output.lower() or 'vuln' in output.lower():
            vuln_lines = [l for l in lines if 'vuln' in l.lower() or 'cve' in l.lower()]
            analysis["summary"] = f"Found {len(vuln_lines)} potential vulnerability indicators"
            analysis["key_findings"] = vuln_lines[:5]
            analysis["risk_items"].append("Vulnerabilities detected - prioritize remediation")
        
        elif 'error' in output.lower() or 'failed' in output.lower():
            error_lines = [l for l in lines if 'error' in l.lower() or 'fail' in l.lower()]
            analysis["summary"] = "Errors detected in output"
            analysis["key_findings"] = error_lines[:5]
            analysis["recommendations"].append("Review errors and check tool configuration")
        
        else:
            analysis["summary"] = f"{tool_name} completed with {len(lines)} lines of output"
            analysis["key_findings"] = [l.strip() for l in lines[:5] if l.strip()]
        
        return analysis

    # ─── ERROR ANALYSIS (ENHANCED) ──────────────────────────────────────

    def analyze_error_advanced(self, error: str, tool_name: str, command: str) -> Dict[str, Any]:
        """Advanced error analysis with auto-fix suggestions."""
        analysis = {
            "tool": tool_name,
            "command": command,
            "error_type": "unknown",
            "severity": "medium",
            "issues": [],
            "auto_fixes": [],
            "manual_fixes": [],
            "related_docs": [],
        }
        
        error_lower = error.lower()
        
        # Permission errors
        if "permission denied" in error_lower or "operation not permitted" in error_lower:
            analysis["error_type"] = "permission"
            analysis["severity"] = "medium"
            analysis["issues"].append("Insufficient permissions to execute this operation")
            analysis["auto_fixes"].append({
                "description": "Run with sudo/elevated privileges",
                "command": f"sudo {command}",
                "safe": True,
            })
        
        # Not found
        elif "command not found" in error_lower or "not recognized" in error_lower:
            analysis["error_type"] = "missing_tool"
            analysis["severity"] = "high"
            analysis["issues"].append(f"Tool '{tool_name}' is not installed or not in PATH")
            analysis["auto_fixes"].append({
                "description": f"Install {tool_name} from Tool Store",
                "action": "install_from_store",
                "safe": True,
            })
            analysis["manual_fixes"].append(f"Check if {tool_name} is in your PATH: which {tool_name}")
        
        # Network errors
        elif any(x in error_lower for x in ["connection refused", "timeout", "unreachable", "no route"]):
            analysis["error_type"] = "network"
            analysis["severity"] = "medium"
            analysis["issues"].append("Network connectivity issue with the target")
            analysis["manual_fixes"].extend([
                "Verify target is online: ping <target>",
                "Check firewall rules",
                "Verify correct port/protocol",
                "Try increasing timeout value",
            ])
        
        # File errors
        elif any(x in error_lower for x in ["no such file", "file not found", "cannot open"]):
            analysis["error_type"] = "file_missing"
            analysis["severity"] = "low"
            analysis["issues"].append("Referenced file or path does not exist")
            analysis["manual_fixes"].extend([
                "Verify the file path is correct",
                "Check file permissions",
                "Ensure working directory is correct",
            ])
        
        # Dependency errors
        elif any(x in error_lower for x in ["import error", "module not found", "library not loaded"]):
            analysis["error_type"] = "dependency"
            analysis["severity"] = "high"
            analysis["issues"].append("Missing dependency or library")
            analysis["auto_fixes"].append({
                "description": "Check and install dependencies",
                "action": "check_dependencies",
                "safe": True,
            })
        
        # Syntax/argument errors
        elif any(x in error_lower for x in ["invalid option", "unrecognized", "usage:", "invalid argument"]):
            analysis["error_type"] = "argument"
            analysis["severity"] = "low"
            analysis["issues"].append("Invalid command argument or option")
            analysis["auto_fixes"].append({
                "description": f"Show {tool_name} help to verify arguments",
                "command": f"{tool_name} --help",
                "safe": True,
            })
        
        else:
            analysis["issues"].append("Unrecognized error - review full output")
            analysis["manual_fixes"].append(f"Check {tool_name} documentation")
        
        return analysis

    # ─── REPORT GENERATION ───────────────────────────────────────────────

    def generate_report(self, executions: List[Dict], workflow_name: str = None) -> str:
        """Generate a professional markdown report from execution results."""
        report = []
        report.append("# VIGIL LABS - Execution Report\n")
        report.append(f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if workflow_name:
            report.append(f"**Workflow:** {workflow_name}\n")
        
        report.append(f"**Total Executions:** {len(executions)}\n")
        report.append("---\n")
        
        for i, exec_data in enumerate(executions, 1):
            report.append(f"\n## Step {i}: {exec_data.get('tool_name', 'Unknown Tool')}\n")
            report.append(f"**Command:** `{exec_data.get('command', 'N/A')}`\n")
            report.append(f"**Status:** {exec_data.get('status', 'unknown')}\n")
            report.append(f"**Duration:** {exec_data.get('duration', 'N/A')}s\n")
            
            if exec_data.get('stdout'):
                report.append(f"\n### Output\n```\n{exec_data['stdout'][:2000]}\n```\n")
            if exec_data.get('stderr'):
                report.append(f"\n### Errors\n```\n{exec_data['stderr'][:500]}\n```\n")
        
        report.append("\n---\n")
        report.append("*Report generated by VIGIL LABS AI Agent*\n")
        
        return "\n".join(report)

    # ─── AUTO-ANALYZE TOOL HELP ──────────────────────────────────────────

    async def auto_analyze_tool(self, executable: str) -> Dict[str, Any]:
        """Run --help on a tool and auto-generate GUI configuration."""
        result = {"executable": executable, "success": False}
        
        # Try common help flags
        for flag in ["--help", "-h", "help", "-help"]:
            try:
                proc = await asyncio.create_subprocess_shell(
                    f"{executable} {flag}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
                help_text = (stdout or stderr).decode("utf-8", errors="replace")
                
                if len(help_text) > 50:
                    result["success"] = True
                    result["help_output"] = help_text
                    result["arguments"] = self._parse_arguments(help_text)
                    result["description"] = self._extract_description(help_text)
                    result["command_template"] = f"{executable} {{args}}"
                    break
            except (asyncio.TimeoutError, Exception):
                continue
        
        if not result["success"]:
            result["error"] = "Could not retrieve help output"
            result["suggestions"] = [
                f"Try running '{executable} --help' manually",
                "The tool may not support standard help flags",
                "You can manually configure the tool in the Tool Builder",
            ]
        
        return result

    # ─── PRIVATE METHODS ─────────────────────────────────────────────────

    def _detect_intents(self, text: str) -> List[str]:
        """Detect user intents from natural language."""
        intent_keywords = {
            "port_scan": ["port scan", "scan ports", "open ports", "nmap", "port discovery"],
            "web_recon": ["web recon", "website", "web scan", "web testing", "web vulnerability"],
            "subdomain_enum": ["subdomain", "subdomains", "dns enum", "asset discovery"],
            "vulnerability_scan": ["vulnerability", "vuln scan", "cve", "exploit", "security scan"],
            "password_crack": ["password", "hash crack", "brute force", "credential", "login crack"],
            "network_sniff": ["sniff", "capture", "packet", "traffic", "wireshark", "tcpdump"],
            "osint": ["osint", "intelligence", "social media", "email", "username", "reconnaissance"],
            "wifi_test": ["wifi", "wireless", "wpa", "handshake", "aircrack"],
            "web_fuzz": ["fuzz", "directory", "brute", "wordlist", "gobuster", "ffuf"],
            "forensics": ["forensic", "memory", "malware", "binary", "reverse engineer"],
            "cloud_audit": ["cloud", "aws", "azure", "container", "docker", "kubernetes"],
            "ad_pentest": ["active directory", "domain", "kerberos", "smb", "lateral"],
        }
        
        intents = []
        for intent, keywords in intent_keywords.items():
            if any(kw in text for kw in keywords):
                intents.append(intent)
        
        return intents or ["general"]

    def _parse_arguments(self, help_text: str) -> List[Dict]:
        """Parse help output into argument definitions."""
        arguments = []
        lines = help_text.split('\n')
        
        patterns = [
            r'^\s*(-\w),?\s*(--[\w-]+)\s*(?:[=\s](\S+))?\s+(.*)',
            r'^\s*(--[\w-]+)\s*(?:[=\s](\S+))?\s+(.*)',
            r'^\s*(-\w)\s*(?:[=\s](\S+))?\s+(.*)',
        ]
        
        for line in lines:
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    flag = groups[1] if len(groups) > 2 and groups[1] else groups[0]
                    if not flag:
                        continue
                    
                    name = flag.lstrip('-').replace('-', '_')
                    value_hint = groups[2] if len(groups) > 2 else (groups[1] if len(groups) > 1 else None)
                    desc = groups[-1].strip() if groups[-1] else ""
                    
                    field_type = self._infer_field_type(name, value_hint, desc)
                    
                    arguments.append({
                        "name": name,
                        "label": name.replace('_', ' ').title(),
                        "flag": flag,
                        "field_type": field_type,
                        "description": desc,
                        "is_required": False,
                        "placeholder": value_hint or "",
                    })
                    break
        
        return arguments[:30]  # Limit to 30 args

    def _infer_field_type(self, name: str, value_hint: str, desc: str) -> str:
        """Infer GUI field type from argument info."""
        combined = f"{name} {value_hint or ''} {desc}".lower()
        
        if any(x in combined for x in ["file", "path", "wordlist", "input"]):
            return "file"
        if any(x in combined for x in ["dir", "directory", "folder", "output"]):
            return "folder"
        if any(x in combined for x in ["port"]):
            return "port"
        if any(x in combined for x in ["host", "target", "ip", "address"]):
            return "ip"
        if any(x in combined for x in ["url", "uri"]):
            return "url"
        if any(x in combined for x in ["domain"]):
            return "domain"
        if any(x in combined for x in ["num", "count", "threads", "rate", "timeout"]):
            return "number"
        if not value_hint and ("enable" in combined or "disable" in combined or "verbose" in combined):
            return "toggle"
        
        return "text"

    def _extract_description(self, help_text: str) -> str:
        """Extract tool description from help output."""
        lines = help_text.split('\n')
        for line in lines[:5]:
            stripped = line.strip()
            if stripped and not stripped.startswith('-') and len(stripped) > 20:
                return stripped[:200]
        return ""

    def _get_tool_purpose(self, tool_name: str) -> str:
        """Get brief purpose of a tool."""
        for tool in TOOL_CATALOG:
            if tool["name"].lower() == tool_name.lower():
                return tool.get("description", "")
        return f"Execute {tool_name}"

    def _get_safety_notes(self, intents: List[str]) -> List[str]:
        """Get safety notes based on detected intents."""
        notes = ["Always ensure you have proper authorization before testing."]
        
        high_risk = {"password_crack", "wifi_test", "ad_pentest", "vulnerability_scan"}
        if any(i in high_risk for i in intents):
            notes.append("⚠️ This activity involves high-risk operations. Use only in authorized lab environments.")
            notes.append("Document all actions for reporting purposes.")
        
        if "network_sniff" in intents:
            notes.append("Network sniffing may be illegal without authorization on networks you don't own.")
        
        return notes

    def _suggest_next_steps(self, intents: List[str]) -> List[str]:
        """Suggest next steps based on intents."""
        steps = []
        
        if "port_scan" in intents:
            steps.extend(["Run service version detection", "Check for known vulnerabilities on open services"])
        if "web_recon" in intents:
            steps.extend(["Run directory brute-force", "Test for common web vulnerabilities"])
        if "subdomain_enum" in intents:
            steps.extend(["Probe discovered subdomains with httpx", "Run vulnerability scanner on live hosts"])
        if "vulnerability_scan" in intents:
            steps.extend(["Verify findings manually", "Generate detailed report"])
        
        return steps or ["Browse available tools in the Tool Store", "Create a workflow for repeated tasks"]

    def _build_knowledge(self) -> Dict[str, Any]:
        """Build comprehensive knowledge base."""
        return {
            "port_scan": {
                "description": "Network port scanning to discover open services",
                "tools": ["Nmap", "Masscan", "Rustscan"],
                "workflow": "Port Scan → Service Detection → Vulnerability Check",
                "risk": "medium",
                "tips": ["Start with a limited port range", "Use -sV for version detection"],
            },
            "web_recon": {
                "description": "Web application reconnaissance and testing",
                "tools": ["Nikto", "Nuclei", "WhatWeb", "Httpx"],
                "workflow": "Technology Detection → Vulnerability Scan → Report",
                "risk": "medium",
                "tips": ["Identify technology stack first", "Check for common misconfigurations"],
            },
            "subdomain_enum": {
                "description": "Discover subdomains and map attack surface",
                "tools": ["Subfinder", "Amass", "Assetfinder", "DNSx"],
                "workflow": "Subdomain Discovery → DNS Resolution → HTTP Probing",
                "risk": "low",
                "tips": ["Use multiple sources for comprehensive results", "Verify with DNS resolution"],
            },
            "vulnerability_scan": {
                "description": "Scan for known vulnerabilities and CVEs",
                "tools": ["Nuclei", "Nikto", "SearchSploit", "Metasploit"],
                "workflow": "Scan → Verify → Document → Report",
                "risk": "high",
                "tips": ["Always verify automated findings", "Check for false positives"],
            },
            "password_crack": {
                "description": "Password and hash testing in authorized environments",
                "tools": ["Hashcat", "John the Ripper", "Hydra"],
                "risk": "high",
                "tips": ["Use targeted wordlists", "Start with common password patterns"],
            },
            "network_sniff": {
                "description": "Network traffic analysis and monitoring",
                "tools": ["Wireshark", "Tshark", "Tcpdump"],
                "risk": "medium",
                "tips": ["Filter traffic to reduce noise", "Focus on specific protocols"],
            },
            "osint": {
                "description": "Open source intelligence gathering",
                "tools": ["theHarvester", "Sherlock", "SpiderFoot", "Recon-ng"],
                "risk": "low",
                "tips": ["Start with passive reconnaissance", "Respect privacy boundaries"],
            },
            "web_fuzz": {
                "description": "Web directory and content discovery",
                "tools": ["ffuf", "Gobuster", "Feroxbuster", "Dirsearch"],
                "risk": "medium",
                "tips": ["Use appropriate wordlists", "Adjust thread count based on target"],
            },
            "forensics": {
                "description": "Digital forensics and malware analysis",
                "tools": ["Volatility", "Binwalk", "ExifTool", "YARA", "Radare2"],
                "risk": "low",
                "tips": ["Work on copies, never original evidence", "Document chain of custody"],
            },
            "cloud_audit": {
                "description": "Cloud infrastructure security assessment",
                "tools": ["Trivy", "ScoutSuite", "Prowler", "Grype"],
                "risk": "low",
                "tips": ["Use read-only credentials when possible", "Check compliance frameworks"],
            },
            "general": {
                "description": "General CLI tool management",
                "tools": [],
                "risk": "low",
                "tips": ["Browse the Tool Store for available tools", "Create custom workflows for repeated tasks"],
            },
        }

    def _build_workflow_templates(self) -> List[Dict]:
        """Pre-built workflow templates."""
        return [
            {
                "name": "Full Web Recon Pipeline",
                "description": "Complete web application reconnaissance",
                "keywords": ["web recon", "full scan", "web assessment", "website scan"],
                "tools": ["Subfinder", "Httpx", "WhatWeb", "Nuclei"],
                "risk": "medium",
            },
            {
                "name": "Network Discovery & Vuln Scan",
                "description": "Discover network hosts and check for vulnerabilities",
                "keywords": ["network scan", "vulnerability", "host discovery"],
                "tools": ["Nmap", "Nuclei"],
                "risk": "medium",
            },
            {
                "name": "Subdomain Enumeration Pipeline",
                "description": "Find and validate subdomains",
                "keywords": ["subdomain", "enum", "dns", "asset"],
                "tools": ["Subfinder", "Amass", "DNSx", "Httpx"],
                "risk": "low",
            },
            {
                "name": "Web Directory Bruteforce",
                "description": "Discover hidden web directories and files",
                "keywords": ["directory", "brute", "hidden files", "content discovery"],
                "tools": ["ffuf", "Gobuster", "Feroxbuster"],
                "risk": "medium",
            },
            {
                "name": "OSINT Investigation",
                "description": "Gather intelligence from open sources",
                "keywords": ["osint", "investigate", "intelligence", "gather info"],
                "tools": ["theHarvester", "Sherlock", "Holehe"],
                "risk": "low",
            },
            {
                "name": "Container Security Audit",
                "description": "Scan containers and images for vulnerabilities",
                "keywords": ["container", "docker", "image scan", "container security"],
                "tools": ["Trivy", "Grype"],
                "risk": "low",
            },
        ]


# Singleton
ai_agent = AIAgent()
