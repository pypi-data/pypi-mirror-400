"""Bash command interceptor for AI Sandbox Orchestrator."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import structlog

from .base import BaseInterceptor, InterceptResult
from ..core.session import Session

logger = structlog.get_logger()


class BashInterceptor(BaseInterceptor):
    """
    Intercepts bash/shell command execution and validates safety.
    
    Handles:
    - Command validation against dangerous patterns
    - Working directory translation to sandbox
    - Environment variable filtering
    - Resource limit enforcement
    """
    
    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("bash", config)
        
        # Command execution tools
        self.command_tools = {
            "bash", "shell", "execute", "run_command", "exec",
            "subprocess", "system", "cmd", "terminal"
        }
        
        # Dangerous command patterns
        self.dangerous_patterns = [
            r'\brm\s+-rf\s+/',  # rm -rf /
            r'\bsudo\b',        # sudo commands
            r'\bsu\b',          # switch user
            r'\bchmod\s+777',   # chmod 777
            r'\bdd\s+if=',      # dd command
            r'\bmkfs\.',        # filesystem creation
            r'\bfdisk\b',       # disk partitioning
            r'\bformat\b',      # format command
            r'\bcurl.*\|\s*bash',  # curl | bash
            r'\bwget.*\|\s*bash',  # wget | bash
            r'>\s*/dev/sd[a-z]',   # writing to disk devices
            r'\bkill\s+-9\s+1\b',  # kill init process
            r'\breboot\b',      # system reboot
            r'\bshutdown\b',    # system shutdown
            r'\biptables\b',    # firewall rules
            r'\bufw\b',         # firewall
            r'\bsystemctl\b',   # systemd control
            r'\bservice\b',     # service control
            r'\bmount\b',       # filesystem mounting
            r'\bumount\b',      # filesystem unmounting
        ]
        
        # Network-related commands that should be monitored
        self.network_patterns = [
            r'\bcurl\b', r'\bwget\b', r'\bscp\b', r'\brsync\b',
            r'\bssh\b', r'\bftp\b', r'\bsftp\b', r'\bnc\b',
            r'\btelnet\b', r'\bping\b', r'\bnmap\b'
        ]
        
        # Package manager commands
        self.package_patterns = [
            r'\bapt\b', r'\bapt-get\b', r'\byum\b', r'\bdnf\b',
            r'\bpip\b', r'\bnpm\b', r'\byarn\b', r'\bcomposer\b',
            r'\bbrew\b', r'\bpacman\b', r'\bzypper\b'
        ]
    
    def is_applicable(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        """Check if this is a command execution operation."""
        if not super().is_applicable(tool_name, arguments):
            return False
        
        return any(cmd_tool in tool_name.lower() for cmd_tool in self.command_tools)
    
    async def intercept(
        self,
        session: Session,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> InterceptResult:
        """Intercept command execution."""
        
        # Extract command from arguments
        command = self._extract_command(arguments)
        if not command:
            return InterceptResult(
                allowed=False,
                error="No command found in arguments"
            )
        
        # Validate command safety
        safety_result = self._validate_command_safety(command)
        if not safety_result.allowed:
            return safety_result
        
        # Translate working directory to sandbox
        modified_args = arguments.copy()
        self._translate_working_directory(session, modified_args)
        
        # Filter environment variables
        self._filter_environment(modified_args)
        
        logger.info(
            "Command execution intercepted",
            command=command,
            session_id=session.id,
            working_dir=modified_args.get("cwd", ""),
        )
        
        return InterceptResult(
            allowed=True,
            executed_in_sandbox=True,
            modified_args=modified_args,
            feedback={
                "command": command,
                "safety_level": safety_result.feedback.get("safety_level", "safe"),
                "warnings": safety_result.feedback.get("warnings", []),
            },
        )
    
    def _extract_command(self, arguments: dict[str, Any]) -> str | None:
        """Extract command string from arguments."""
        # Common argument names for commands
        command_keys = ["command", "cmd", "script", "code", "shell"]
        
        for key in command_keys:
            if key in arguments:
                return str(arguments[key])
        
        # Check for positional arguments
        if "args" in arguments and arguments["args"]:
            return str(arguments["args"][0])
        
        return None
    
    def _validate_command_safety(self, command: str) -> InterceptResult:
        """Validate command against dangerous patterns."""
        warnings = []
        safety_level = "safe"
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return InterceptResult(
                    allowed=False,
                    error=f"Dangerous command pattern detected: {pattern}"
                )
        
        # Check for network operations (warn but allow)
        for pattern in self.network_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                warnings.append(f"Network operation detected: {pattern}")
                safety_level = "network"
        
        # Check for package management (warn but allow)
        for pattern in self.package_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                warnings.append(f"Package management detected: {pattern}")
                safety_level = "package"
        
        # Check for file system modifications outside current directory
        if re.search(r'[>|]\s*/[^/]', command):
            warnings.append("Writing to absolute paths detected")
            safety_level = "filesystem"
        
        # Check for background processes
        if re.search(r'&\s*$', command):
            warnings.append("Background process detected")
            safety_level = "background"
        
        return InterceptResult(
            allowed=True,
            feedback={
                "safety_level": safety_level,
                "warnings": warnings,
            }
        )
    
    def _translate_working_directory(self, session: Session, arguments: dict[str, Any]) -> None:
        """Translate working directory to sandbox."""
        if not session.sandbox_path:
            return
        
        # Set working directory to sandbox if not specified
        if "cwd" not in arguments:
            arguments["cwd"] = str(session.sandbox_path)
            return
        
        # Translate existing working directory
        current_cwd = Path(arguments["cwd"])
        
        if current_cwd.is_absolute():
            # Try to make it relative to main codebase
            try:
                relative_cwd = current_cwd.relative_to(session.config.main_codebase)
                arguments["cwd"] = str(session.sandbox_path / relative_cwd)
            except ValueError:
                # Path outside main codebase, use sandbox root
                arguments["cwd"] = str(session.sandbox_path)
        else:
            # Relative path, prepend sandbox path
            arguments["cwd"] = str(session.sandbox_path / current_cwd)
    
    def _filter_environment(self, arguments: dict[str, Any]) -> None:
        """Filter dangerous environment variables."""
        if "env" not in arguments:
            return
        
        env = arguments["env"]
        if not isinstance(env, dict):
            return
        
        # Remove potentially dangerous environment variables
        dangerous_env_vars = {
            "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES",
            "PATH",  # Don't allow PATH modification
            "PYTHONPATH",  # Don't allow Python path modification
            "HOME",  # Don't allow home directory change
            "USER", "USERNAME",  # Don't allow user change
        }
        
        for var in dangerous_env_vars:
            if var in env:
                del env[var]
        
        # Filter environment variables with suspicious values
        for key, value in list(env.items()):
            if isinstance(value, str):
                # Remove env vars with shell injection patterns
                if re.search(r'[;&|`$()]', value):
                    del env[key]
    
    def get_feedback_message(self, result: InterceptResult) -> str:
        """Generate feedback message for command execution."""
        if not result.allowed:
            return f"🚫 Command: {result.error}"
        
        if result.feedback:
            command = result.feedback.get("command", "")
            safety_level = result.feedback.get("safety_level", "safe")
            warnings = result.feedback.get("warnings", [])
            
            emoji_map = {
                "safe": "✅",
                "network": "🌐", 
                "package": "📦",
                "filesystem": "📁",
                "background": "⚡",
            }
            
            emoji = emoji_map.get(safety_level, "⚠️")
            message = f"{emoji} Command: {command[:50]}{'...' if len(command) > 50 else ''}"
            
            if warnings:
                message += f" (Warnings: {len(warnings)})"
            
            return message
        
        return "✅ Command: Execution allowed in sandbox"