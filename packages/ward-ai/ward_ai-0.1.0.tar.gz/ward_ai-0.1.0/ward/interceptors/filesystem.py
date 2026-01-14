"""Filesystem interceptor for AI Sandbox Orchestrator."""

from __future__ import annotations

import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import structlog

from .base import BaseInterceptor, InterceptResult
from ..core.session import Session

logger = structlog.get_logger()


class FilesystemInterceptor(BaseInterceptor):
    """
    Intercepts filesystem operations and redirects them to sandbox.
    
    Handles:
    - File read/write operations
    - Directory creation/deletion
    - Path validation and translation
    - Blocked path enforcement
    """
    
    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("filesystem", config)
        
        # File operation tools that should be intercepted
        self.file_tools = {
            "write_file", "create_file", "save_file", "fs_write",
            "read_file", "load_file", "fs_read",
            "delete_file", "remove_file", "fs_delete",
            "mkdir", "create_directory", "fs_mkdir",
            "rmdir", "remove_directory", "fs_rmdir",
        }
    
    def is_applicable(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        """Check if this is a filesystem operation."""
        if not super().is_applicable(tool_name, arguments):
            return False
        
        # Check if tool name matches filesystem operations
        return any(fs_tool in tool_name.lower() for fs_tool in self.file_tools)
    
    async def intercept(
        self,
        session: Session,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> InterceptResult:
        """Intercept filesystem operations."""
        
        # Extract file path from arguments
        file_path = self._extract_file_path(arguments)
        if not file_path:
            return InterceptResult(
                allowed=False,
                error="No file path found in arguments"
            )
        
        # Validate path
        validation_result = self._validate_path(session, file_path)
        if not validation_result.allowed:
            return validation_result
        
        # Translate path to sandbox
        sandbox_path = self._translate_to_sandbox(session, file_path)
        if not sandbox_path:
            return InterceptResult(
                allowed=False,
                error="Failed to translate path to sandbox"
            )
        
        # Update arguments with sandbox path
        modified_args = arguments.copy()
        self._update_path_in_args(modified_args, sandbox_path)
        
        # Ensure parent directory exists for write operations
        if self._is_write_operation(tool_name):
            sandbox_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "Filesystem operation intercepted",
            tool=tool_name,
            original_path=str(file_path),
            sandbox_path=str(sandbox_path),
            session_id=session.id,
        )
        
        return InterceptResult(
            allowed=True,
            executed_in_sandbox=True,
            modified_args=modified_args,
            feedback={
                "original_path": str(file_path),
                "sandbox_path": str(sandbox_path),
                "operation": tool_name,
            },
        )
    
    def _extract_file_path(self, arguments: dict[str, Any]) -> Path | None:
        """Extract file path from tool arguments."""
        # Common argument names for file paths
        path_keys = ["path", "file_path", "filename", "file", "target", "source"]
        
        for key in path_keys:
            if key in arguments:
                return Path(arguments[key])
        
        # Check for positional arguments
        if "args" in arguments and arguments["args"]:
            return Path(arguments["args"][0])
        
        return None
    
    def _validate_path(self, session: Session, file_path: Path) -> InterceptResult:
        """Validate if path is allowed to be accessed."""
        path_str = str(file_path)
        
        # Check blocked paths
        for blocked_pattern in session.config.blocked_paths:
            if fnmatch(path_str, blocked_pattern):
                return InterceptResult(
                    allowed=False,
                    error=f"Path blocked by security policy: {blocked_pattern}"
                )
        
        # Check allowed paths (if specified)
        if session.config.allowed_paths:
            allowed = False
            for allowed_pattern in session.config.allowed_paths:
                if fnmatch(path_str, allowed_pattern):
                    allowed = True
                    break
            
            if not allowed:
                return InterceptResult(
                    allowed=False,
                    error="Path not in allowed paths list"
                )
        
        # Check scope paths
        if session.scope_paths:
            in_scope = False
            for scope_pattern in session.scope_paths:
                if fnmatch(path_str, scope_pattern):
                    in_scope = True
                    break
            
            if not in_scope:
                return InterceptResult(
                    allowed=False,
                    error=f"Path outside session scope: {session.scope_paths}"
                )
        
        return InterceptResult(allowed=True)
    
    def _translate_to_sandbox(self, session: Session, file_path: Path) -> Path | None:
        """Translate main codebase path to sandbox path."""
        if not session.sandbox_path:
            return None
        
        # If path is already absolute, make it relative to main codebase
        if file_path.is_absolute():
            try:
                relative_path = file_path.relative_to(session.config.main_codebase)
            except ValueError:
                # Path is outside main codebase, use as-is but relative to sandbox
                relative_path = file_path.name
        else:
            relative_path = file_path
        
        return session.sandbox_path / relative_path
    
    def _update_path_in_args(self, arguments: dict[str, Any], new_path: Path) -> None:
        """Update path in arguments dictionary."""
        path_keys = ["path", "file_path", "filename", "file", "target", "source"]
        
        for key in path_keys:
            if key in arguments:
                arguments[key] = str(new_path)
                return
        
        # Update positional arguments
        if "args" in arguments and arguments["args"]:
            arguments["args"][0] = str(new_path)
    
    def _is_write_operation(self, tool_name: str) -> bool:
        """Check if this is a write operation that needs directory creation."""
        write_tools = {
            "write_file", "create_file", "save_file", "fs_write",
            "mkdir", "create_directory", "fs_mkdir",
        }
        return any(write_tool in tool_name.lower() for write_tool in write_tools)
    
    def get_feedback_message(self, result: InterceptResult) -> str:
        """Generate feedback message for filesystem operations."""
        if not result.allowed:
            return f"🚫 Filesystem: {result.error}"
        
        if result.feedback:
            original = result.feedback.get("original_path", "")
            sandbox = result.feedback.get("sandbox_path", "")
            operation = result.feedback.get("operation", "")
            
            return f"📁 Filesystem: {operation} redirected from {original} to sandbox: {sandbox}"
        
        return "📁 Filesystem: Operation allowed in sandbox"