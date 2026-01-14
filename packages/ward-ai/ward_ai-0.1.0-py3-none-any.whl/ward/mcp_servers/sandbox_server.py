"""
MCP Server for AI Sandbox Orchestrator.

This server implements the Model Context Protocol (MCP) to intercept
tool calls from Claude and route them through the sandbox environment.

Usage:
    python -m ward.mcp_servers.sandbox_server

Claude Desktop configuration (claude_desktop_config.json):
    {
      "mcpServers": {
        "ward": {
          "command": "python",
          "args": ["-m", "ward.mcp_servers.sandbox_server"],
          "env": {
            "SANDBOX_MAIN_CODEBASE": "/path/to/your/project"
          }
        }
      }
    }
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolResult,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError:
    print("Error: MCP package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

import structlog

from ward.core.config import SandboxConfig
from ward.core.orchestrator import Orchestrator

# Setup logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)
logger = structlog.get_logger()


class SandboxMCPServer:
    """
    MCP Server that intercepts file operations and routes them through sandbox.
    
    Tools provided:
    - sandbox_start_session: Start a new sandboxed work session
    - sandbox_write_file: Write a file in the sandbox
    - sandbox_read_file: Read a file from sandbox or main codebase
    - sandbox_delete_file: Delete a file in the sandbox
    - sandbox_run_command: Execute a command in the sandbox
    - sandbox_get_status: Get current session status and feedback
    - sandbox_validate: Run validation gates
    - sandbox_promote: Promote validated changes to main codebase
    - sandbox_rollback: Rollback all changes
    - sandbox_diff: View diff of all changes
    """
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.orchestrator = Orchestrator(config)
        self.server = Server("ward")
        self._current_session_id: Optional[str] = None
        
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register MCP tool handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """Return list of available sandbox tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="sandbox_start_session",
                        description=(
                            "Start a new sandboxed work session. "
                            "All file operations will be isolated in a sandbox until validated and promoted. "
                            "ALWAYS call this before making any file changes."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "task_description": {
                                    "type": "string",
                                    "description": "Description of what you're trying to accomplish",
                                },
                                "scope_paths": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Optional: List of file/directory patterns you expect to modify",
                                },
                            },
                            "required": ["task_description"],
                        },
                    ),
                    Tool(
                        name="sandbox_write_file",
                        description=(
                            "Write content to a file in the sandbox. "
                            "The file will NOT be written to the main codebase until validated and promoted. "
                            "Returns feedback about the change including validation status."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Relative path from project root",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Content to write",
                                },
                            },
                            "required": ["path", "content"],
                        },
                    ),
                    Tool(
                        name="sandbox_read_file",
                        description=(
                            "Read a file from the sandbox (if modified) or main codebase. "
                            "Use this to see current file contents before making changes."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Relative path from project root",
                                },
                            },
                            "required": ["path"],
                        },
                    ),
                    Tool(
                        name="sandbox_delete_file",
                        description=(
                            "Mark a file for deletion in the sandbox. "
                            "The file will NOT be deleted from main codebase until promoted."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Relative path from project root",
                                },
                            },
                            "required": ["path"],
                        },
                    ),
                    Tool(
                        name="sandbox_run_command",
                        description=(
                            "Execute a shell command in the sandbox environment. "
                            "Commands run with the sandbox as the working directory. "
                            "Use this to run tests, linters, or other verification commands."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Command to execute",
                                },
                                "working_dir": {
                                    "type": "string",
                                    "description": "Optional: subdirectory to run command in",
                                },
                            },
                            "required": ["command"],
                        },
                    ),
                    Tool(
                        name="sandbox_get_status",
                        description=(
                            "Get the current session status, including all changes made, "
                            "validation results, and feedback. Call this to understand "
                            "the current state of your work."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                    Tool(
                        name="sandbox_validate",
                        description=(
                            "Run all validation gates on the current session. "
                            "This includes syntax checking, running tests, and security scans. "
                            "Call this before promoting to ensure changes are safe."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                    Tool(
                        name="sandbox_promote",
                        description=(
                            "Promote validated changes from sandbox to main codebase. "
                            "Only call this after sandbox_validate passes. "
                            "This permanently applies your changes."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "confirm": {
                                    "type": "boolean",
                                    "description": "Must be true to confirm promotion",
                                },
                            },
                            "required": ["confirm"],
                        },
                    ),
                    Tool(
                        name="sandbox_rollback",
                        description=(
                            "Discard all changes and cleanup the sandbox. "
                            "Use this if you want to start over or abandon changes."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "confirm": {
                                    "type": "boolean",
                                    "description": "Must be true to confirm rollback",
                                },
                            },
                            "required": ["confirm"],
                        },
                    ),
                    Tool(
                        name="sandbox_diff",
                        description=(
                            "View a diff of all changes made in the current session. "
                            "Shows what will be applied to the main codebase when promoted."
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Optional: specific file to diff",
                                },
                            },
                        },
                    ),
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "sandbox_start_session":
                    return await self._handle_start_session(arguments)
                elif name == "sandbox_write_file":
                    return await self._handle_write_file(arguments)
                elif name == "sandbox_read_file":
                    return await self._handle_read_file(arguments)
                elif name == "sandbox_delete_file":
                    return await self._handle_delete_file(arguments)
                elif name == "sandbox_run_command":
                    return await self._handle_run_command(arguments)
                elif name == "sandbox_get_status":
                    return await self._handle_get_status(arguments)
                elif name == "sandbox_validate":
                    return await self._handle_validate(arguments)
                elif name == "sandbox_promote":
                    return await self._handle_promote(arguments)
                elif name == "sandbox_rollback":
                    return await self._handle_rollback(arguments)
                elif name == "sandbox_diff":
                    return await self._handle_diff(arguments)
                else:
                    return self._error_result(f"Unknown tool: {name}")
            except Exception as e:
                logger.exception("Tool call failed", tool=name)
                return self._error_result(str(e))
    
    def _error_result(self, message: str) -> CallToolResult:
        """Create an error result."""
        return CallToolResult(
            content=[TextContent(type="text", text=f"ERROR: {message}")],
            isError=True,
        )
    
    def _success_result(self, data: Any) -> CallToolResult:
        """Create a success result."""
        if isinstance(data, str):
            text = data
        else:
            text = json.dumps(data, indent=2, default=str)
        
        return CallToolResult(
            content=[TextContent(type="text", text=text)],
        )
    
    async def _handle_start_session(self, args: dict) -> CallToolResult:
        """Start a new sandbox session."""
        task = args.get("task_description", "Unnamed task")
        scope = args.get("scope_paths")
        
        session = await self.orchestrator.start_session(task, scope)
        self._current_session_id = session.id
        
        return self._success_result({
            "status": "session_started",
            "session_id": session.id,
            "task": task,
            "sandbox_path": str(session.sandbox_path),
            "limits": {
                "max_files": session.max_files,
                "max_lines": session.max_lines,
                "timeout_minutes": session.timeout_minutes,
            },
            "message": (
                f"Session {session.id} created. "
                "All file operations will be sandboxed. "
                "Use sandbox_validate before sandbox_promote."
            ),
        })
    
    async def _handle_write_file(self, args: dict) -> CallToolResult:
        """Write a file in the sandbox."""
        if not self._current_session_id:
            return self._error_result(
                "No active session. Call sandbox_start_session first."
            )
        
        path = args.get("path")
        content = args.get("content")
        
        if not path:
            return self._error_result("Path is required")
        if content is None:
            return self._error_result("Content is required")
        
        result = await self.orchestrator.intercept_file_write(
            self._current_session_id,
            path,
            content,
        )
        
        if not result.allowed:
            return self._error_result(result.error or "Write not allowed")
        
        return self._success_result({
            "status": "written_to_sandbox",
            "path": path,
            "operation": result.result.get("operation"),
            "feedback": result.feedback,
            "message": (
                f"File written to SANDBOX (not main codebase). "
                f"Run sandbox_validate to check, then sandbox_promote to apply."
            ),
        })
    
    async def _handle_read_file(self, args: dict) -> CallToolResult:
        """Read a file from sandbox or main codebase."""
        path = args.get("path")
        if not path:
            return self._error_result("Path is required")
        
        # Try sandbox first if session exists
        if self._current_session_id:
            session = self.orchestrator.session_manager.get_session(
                self._current_session_id
            )
            if session and session.sandbox_path:
                sandbox_file = session.sandbox_path / path
                if sandbox_file.exists():
                    content = sandbox_file.read_text()
                    return self._success_result({
                        "path": path,
                        "source": "sandbox",
                        "content": content,
                    })
        
        # Fall back to main codebase
        main_file = self.config.main_codebase / path
        if main_file.exists():
            content = main_file.read_text()
            return self._success_result({
                "path": path,
                "source": "main_codebase",
                "content": content,
            })
        
        return self._error_result(f"File not found: {path}")
    
    async def _handle_delete_file(self, args: dict) -> CallToolResult:
        """Delete a file in the sandbox."""
        if not self._current_session_id:
            return self._error_result(
                "No active session. Call sandbox_start_session first."
            )
        
        path = args.get("path")
        if not path:
            return self._error_result("Path is required")
        
        result = await self.orchestrator.intercept_file_delete(
            self._current_session_id,
            path,
        )
        
        if not result.allowed:
            return self._error_result(result.error or "Delete not allowed")
        
        return self._success_result({
            "status": "marked_for_deletion",
            "path": path,
            "feedback": result.feedback,
            "message": "File marked for deletion in sandbox. Will be deleted when promoted.",
        })
    
    async def _handle_run_command(self, args: dict) -> CallToolResult:
        """Execute a command in the sandbox."""
        if not self._current_session_id:
            return self._error_result(
                "No active session. Call sandbox_start_session first."
            )
        
        command = args.get("command")
        working_dir = args.get("working_dir")
        
        if not command:
            return self._error_result("Command is required")
        
        result = await self.orchestrator.intercept_command(
            self._current_session_id,
            command,
            working_dir,
        )
        
        if not result.allowed:
            return self._error_result(result.error or "Command not allowed")
        
        return self._success_result({
            "status": "executed",
            "command": command,
            "result": result.result,
            "feedback": result.feedback,
        })
    
    async def _handle_get_status(self, args: dict) -> CallToolResult:
        """Get current session status."""
        if not self._current_session_id:
            return self._success_result({
                "status": "no_active_session",
                "message": "No active session. Call sandbox_start_session to begin.",
            })
        
        feedback = self.orchestrator.get_session_feedback(self._current_session_id)
        return self._success_result(feedback)
    
    async def _handle_validate(self, args: dict) -> CallToolResult:
        """Run validation gates."""
        if not self._current_session_id:
            return self._error_result(
                "No active session. Call sandbox_start_session first."
            )
        
        results = await self.orchestrator.validate_session(self._current_session_id)
        
        all_passed = all(r.passed for r in results)
        
        return self._success_result({
            "status": "validation_complete",
            "all_passed": all_passed,
            "results": [
                {
                    "validator": r.validator_name,
                    "passed": r.passed,
                    "message": r.message,
                    "errors": r.errors,
                    "warnings": r.warnings,
                }
                for r in results
            ],
            "next_step": (
                "Ready for sandbox_promote" if all_passed
                else "Fix errors and run sandbox_validate again"
            ),
        })
    
    async def _handle_promote(self, args: dict) -> CallToolResult:
        """Promote changes to main codebase."""
        if not self._current_session_id:
            return self._error_result(
                "No active session. Call sandbox_start_session first."
            )
        
        if not args.get("confirm"):
            return self._error_result(
                "Must set confirm=true to promote changes"
            )
        
        try:
            success = await self.orchestrator.promote_session(
                self._current_session_id
            )
            
            if success:
                session_id = self._current_session_id
                self._current_session_id = None  # Clear session
                
                return self._success_result({
                    "status": "promoted",
                    "session_id": session_id,
                    "message": "All changes have been applied to the main codebase.",
                })
            else:
                return self._error_result("Promotion failed")
                
        except ValueError as e:
            return self._error_result(str(e))
    
    async def _handle_rollback(self, args: dict) -> CallToolResult:
        """Rollback all changes."""
        if not self._current_session_id:
            return self._error_result("No active session")
        
        if not args.get("confirm"):
            return self._error_result(
                "Must set confirm=true to rollback changes"
            )
        
        await self.orchestrator.rollback_session(self._current_session_id)
        session_id = self._current_session_id
        self._current_session_id = None
        
        return self._success_result({
            "status": "rolled_back",
            "session_id": session_id,
            "message": "All changes have been discarded.",
        })
    
    async def _handle_diff(self, args: dict) -> CallToolResult:
        """View diff of changes."""
        if not self._current_session_id:
            return self._error_result("No active session")
        
        session = self.orchestrator.session_manager.get_session(
            self._current_session_id
        )
        if not session:
            return self._error_result("Session not found")
        
        specific_path = args.get("path")
        
        diffs = []
        for fc in session.file_changes:
            if specific_path and str(fc.path) != specific_path:
                continue
            
            diff_entry = {
                "path": str(fc.path),
                "operation": fc.operation,
                "lines_added": fc.lines_added,
                "lines_removed": fc.lines_removed,
            }
            
            # Generate simple diff
            if fc.original_content and fc.new_content:
                from difflib import unified_diff
                
                diff_lines = list(unified_diff(
                    fc.original_content.splitlines(keepends=True),
                    fc.new_content.splitlines(keepends=True),
                    fromfile=f"a/{fc.path}",
                    tofile=f"b/{fc.path}",
                ))
                diff_entry["diff"] = "".join(diff_lines[:100])  # Limit size
            
            diffs.append(diff_entry)
        
        return self._success_result({
            "session_id": self._current_session_id,
            "total_files": len(diffs),
            "diffs": diffs,
        })
    
    async def run(self) -> None:
        """Run the MCP server."""
        logger.info(
            "Starting Sandbox MCP Server",
            main_codebase=str(self.config.main_codebase),
        )
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


def main():
    """Entry point for the MCP server."""
    # Get config from environment
    main_codebase = os.environ.get("SANDBOX_MAIN_CODEBASE")
    
    if not main_codebase:
        print(
            "Error: SANDBOX_MAIN_CODEBASE environment variable not set",
            file=sys.stderr,
        )
        print(
            "Set it to the path of your project to protect",
            file=sys.stderr,
        )
        sys.exit(1)
    
    try:
        config = SandboxConfig(
            main_codebase=Path(main_codebase),
            validation_mode=os.environ.get("SANDBOX_VALIDATION_MODE", "strict"),
            autonomy_level=os.environ.get("SANDBOX_AUTONOMY_LEVEL", "validated"),
        )
    except Exception as e:
        print(f"Error creating config: {e}", file=sys.stderr)
        sys.exit(1)
    
    server = SandboxMCPServer(config)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()