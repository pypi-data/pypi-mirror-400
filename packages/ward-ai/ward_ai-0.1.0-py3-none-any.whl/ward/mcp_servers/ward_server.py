"""Enhanced MCP Server for Ward - Claude Desktop Integration."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Add the parent directory to the path so we can import ward modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ward.core.config import SandboxConfig, AutonomyLevel, ValidationMode
from ward.core.universal_wrapper import get_wrapper, IsolationMethod

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ward-mcp-server")

# Global configuration
MAIN_CODEBASE = os.getenv("WARD_MAIN_CODEBASE", os.getcwd())
AUTONOMY_LEVEL = os.getenv("WARD_AUTONOMY_LEVEL", "validated")
VALIDATION_MODE = os.getenv("WARD_VALIDATION_MODE", "strict")

# Initialize Ward configuration
config = SandboxConfig(
    main_codebase=Path(MAIN_CODEBASE),
    autonomy_level=AutonomyLevel(AUTONOMY_LEVEL),
    validation_mode=ValidationMode(VALIDATION_MODE),
)

# Global wrapper instance
wrapper = None

# MCP Server instance
server = Server("ward")


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available Ward tools for Claude."""
    return ListToolsResult(
        tools=[
            Tool(
                name="ward_run",
                description="Execute any command safely in Ward's protected sandbox environment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to execute (e.g., 'python script.py', 'npm test', 'make build')"
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Description of what this command does (optional)"
                        },
                        "isolation": {
                            "type": "string",
                            "enum": ["git", "copy", "auto"],
                            "description": "Isolation method: git (worktree), copy (file copy), auto (detect best)",
                            "default": "auto"
                        }
                    },
                    "required": ["command"]
                }
            ),
            Tool(
                name="ward_status",
                description="Check the status of current Ward session and validation results",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="ward_approve",
                description="Approve and apply validated changes to the main codebase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "force": {
                            "type": "boolean",
                            "description": "Force approval even if validations failed",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="ward_start_session",
                description="Start a new protected Ward session for AI work",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task to be performed"
                        },
                        "scope_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Limit changes to specific file paths (optional)"
                        }
                    },
                    "required": ["task_description"]
                }
            ),
            Tool(
                name="ward_kill",
                description="Emergency stop - terminate and cleanup Ward sessions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "all": {
                            "type": "boolean",
                            "description": "Kill all sessions (emergency cleanup)",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="ward_list_sessions",
                description="List all active Ward sessions with their status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="ward_get_diff",
                description="Get diff of changes made in current Ward session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["unified", "markdown", "compact"],
                            "description": "Diff format",
                            "default": "markdown"
                        }
                    },
                    "required": []
                }
            )
        ]
    )


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls from Claude."""
    global wrapper
    
    try:
        # Initialize wrapper if not already done
        if wrapper is None:
            wrapper = await get_wrapper(config)
        
        if name == "ward_run":
            return await handle_ward_run(arguments)
        elif name == "ward_status":
            return await handle_ward_status(arguments)
        elif name == "ward_approve":
            return await handle_ward_approve(arguments)
        elif name == "ward_start_session":
            return await handle_ward_start_session(arguments)
        elif name == "ward_kill":
            return await handle_ward_kill(arguments)
        elif name == "ward_list_sessions":
            return await handle_ward_list_sessions(arguments)
        elif name == "ward_get_diff":
            return await handle_ward_get_diff(arguments)
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}")
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )],
            isError=True
        )


async def handle_ward_run(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle ward_run tool call."""
    command = arguments.get("command")
    task_description = arguments.get("task_description")
    isolation = arguments.get("isolation", "auto")
    
    if not command:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: command parameter is required"
            )],
            isError=True
        )
    
    # Map isolation method
    isolation_method = None
    if isolation == "git":
        isolation_method = IsolationMethod.GIT_WORKTREE
    elif isolation == "copy":
        isolation_method = IsolationMethod.FILE_COPY
    
    # Execute command
    result = await wrapper.wrap_command(
        command=command,
        task_description=task_description,
        isolation_method=isolation_method
    )
    
    # Format response for Claude
    response_parts = [
        f"🛡️ **Ward Command Execution**",
        f"**Command:** `{command}`",
        f"**Isolation:** {result.isolation_method.value}",
        f"**Duration:** {result.execution_time:.2f}s",
        f"**Return Code:** {result.return_code}",
        ""
    ]
    
    if result.stdout:
        response_parts.extend([
            "**Output:**",
            "```",
            result.stdout,
            "```",
            ""
        ])
    
    if result.stderr:
        response_parts.extend([
            "**Errors:**",
            "```",
            result.stderr,
            "```",
            ""
        ])
    
    # Validation results
    if result.validation_results:
        response_parts.append("**Validation Results:**")
        for vr in result.validation_results:
            status = "✅" if vr["passed"] else "❌"
            response_parts.append(f"- {status} {vr['validator']}: {vr['message']}")
        response_parts.append("")
    
    # Next steps
    if result.return_code == 0 and result.validation_passed:
        response_parts.append("✅ **Command executed successfully and passed all validations!**")
        response_parts.append("💡 Use `ward_approve` to apply changes to main codebase.")
    elif result.return_code == 0:
        response_parts.append("⚠️ **Command executed but validation failed.**")
        response_parts.append("💡 Use `ward_status` to see detailed validation results.")
    else:
        response_parts.append("❌ **Command execution failed.**")
    
    return CallToolResult(
        content=[TextContent(
            type="text",
            text="\n".join(response_parts)
        )]
    )


async def handle_ward_status(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle ward_status tool call."""
    sessions = await wrapper.get_active_sessions()
    
    if not sessions:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="📊 **Ward Status**\n\nNo active sessions found."
            )]
        )
    
    # Get most recent session
    latest_session = sessions[0]
    session_id = latest_session["id"]
    
    # Get detailed session info
    session = wrapper.orchestrator.session_manager.get_session(session_id)
    if not session:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="❌ Session not found"
            )],
            isError=True
        )
    
    try:
        metrics = await wrapper.orchestrator.get_session_metrics(session_id)
        
        response_parts = [
            "📊 **Ward Session Status**",
            "",
            f"**Session ID:** {session.id[:8]}...",
            f"**Task:** {session.task_description}",
            f"**Status:** {session.status.value}",
            f"**Duration:** {session.duration_minutes:.1f} minutes",
            f"**Files Changed:** {metrics['files']['total']}",
            f"**Lines:** +{metrics['lines']['added']} -{metrics['lines']['removed']}",
            f"**Validations:** {metrics['validations']['passed']}/{metrics['validations']['total']}",
            ""
        ]
        
        # Show validation results
        if session.validation_results:
            response_parts.append("**Validation Details:**")
            for vr in session.validation_results:
                status = "✅" if vr.passed else "❌"
                response_parts.append(f"- {status} {vr.validator_name}: {vr.message}")
                
                if vr.errors:
                    for error in vr.errors:
                        response_parts.append(f"  ❌ {error}")
                
                if vr.warnings:
                    for warning in vr.warnings:
                        response_parts.append(f"  ⚠️ {warning}")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="\n".join(response_parts)
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ Error getting session status: {str(e)}"
            )],
            isError=True
        )


async def handle_ward_approve(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle ward_approve tool call."""
    force = arguments.get("force", False)
    
    try:
        success = await wrapper.approve_session()
        
        if success:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="✅ **Changes Approved!**\n\nChanges have been successfully applied to the main codebase."
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="❌ **Approval Failed**\n\nFailed to apply changes to main codebase."
                )],
                isError=True
            )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ **Approval Error:** {str(e)}"
            )],
            isError=True
        )


async def handle_ward_start_session(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle ward_start_session tool call."""
    task_description = arguments.get("task_description")
    scope_paths = arguments.get("scope_paths")
    
    if not task_description:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="❌ Error: task_description is required"
            )],
            isError=True
        )
    
    try:
        session = await wrapper.orchestrator.start_session(
            task_description=task_description,
            scope_paths=scope_paths
        )
        
        response_parts = [
            "🚀 **Ward Session Started**",
            "",
            f"**Session ID:** {session.id}",
            f"**Task:** {session.task_description}",
            f"**Sandbox Path:** {session.sandbox_path}",
            f"**Status:** {session.status.value}",
            ""
        ]
        
        if scope_paths:
            response_parts.extend([
                "**Scope Paths:**",
                *[f"- {path}" for path in scope_paths],
                ""
            ])
        
        response_parts.append("💡 Session is ready for AI work. Use `ward_run` to execute commands safely.")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="\n".join(response_parts)
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ **Session Creation Failed:** {str(e)}"
            )],
            isError=True
        )


async def handle_ward_kill(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle ward_kill tool call."""
    kill_all = arguments.get("all", False)
    
    try:
        if kill_all:
            cleanup_result = await wrapper.emergency_cleanup()
            total_cleaned = sum(cleanup_result.values())
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"🧹 **Emergency Cleanup Completed**\n\nCleaned up {total_cleaned} resources:\n- Sessions: {cleanup_result['sessions']}"
                )]
            )
        else:
            success = await wrapper.kill_session()
            
            if success:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="✅ **Session Terminated**\n\nCurrent session has been terminated and cleaned up."
                    )]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="⚠️ **No Session to Kill**\n\nNo active session found to terminate."
                    )]
                )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ **Kill Error:** {str(e)}"
            )],
            isError=True
        )


async def handle_ward_list_sessions(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle ward_list_sessions tool call."""
    try:
        sessions = await wrapper.get_active_sessions()
        
        if not sessions:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="📋 **Ward Sessions**\n\nNo active sessions found."
                )]
            )
        
        response_parts = [
            "📋 **Ward Sessions**",
            ""
        ]
        
        for session in sessions:
            response_parts.extend([
                f"**{session['id'][:8]}...** - {session['task']}",
                f"  Status: {session['status']}",
                f"  Duration: {session['duration_minutes']:.1f}m",
                f"  Files: {session['files_changed']}",
                f"  Created: {session['created']}",
                ""
            ])
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="\n".join(response_parts)
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ **List Sessions Error:** {str(e)}"
            )],
            isError=True
        )


async def handle_ward_get_diff(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle ward_get_diff tool call."""
    format_type = arguments.get("format", "markdown")
    
    try:
        sessions = await wrapper.get_active_sessions()
        
        if not sessions:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="⚠️ **No Active Sessions**\n\nNo sessions found to show diff for."
                )]
            )
        
        # Get most recent session
        latest_session = sessions[0]
        session_id = latest_session["id"]
        
        diff_content = await wrapper.orchestrator.get_session_diff(session_id, format_type)
        
        if not diff_content.strip():
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="📄 **Session Diff**\n\nNo changes detected in current session."
                )]
            )
        
        response_parts = [
            f"📄 **Session Diff** ({session_id[:8]}...)",
            "",
            diff_content
        ]
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="\n".join(response_parts)
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ **Diff Error:** {str(e)}"
            )],
            isError=True
        )


async def main():
    """Main entry point for the Ward MCP server."""
    logger.info("Starting Ward MCP Server")
    logger.info(f"Main codebase: {MAIN_CODEBASE}")
    logger.info(f"Autonomy level: {AUTONOMY_LEVEL}")
    logger.info(f"Validation mode: {VALIDATION_MODE}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ward",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())