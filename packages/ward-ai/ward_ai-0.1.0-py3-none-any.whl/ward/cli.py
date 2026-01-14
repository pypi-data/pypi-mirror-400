"""Command Line Interface for Ward - The Universal Safety Layer for AI Agents."""

from __future__ import annotations

import asyncio
import json
import sys
import shlex
import subprocess
from pathlib import Path
from typing import Optional

import click
import structlog
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.text import Text

from .core.config import SandboxConfig, AutonomyLevel, ValidationMode
from .core.universal_wrapper import get_wrapper, IsolationMethod
from .core.session import SessionStatus

# Setup console and logging
console = Console()
logger = structlog.get_logger()


@click.group()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """Ward - The Universal Safety Layer for AI Agents."""
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer() if not sys.stdout.isatty() else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Load configuration
    if config:
        ctx.obj = {"config_file": config}
    else:
        ctx.obj = {"config_file": None}
    
    console.print("🛡️  Ward - Universal AI Safety Layer", style="bold blue")


@cli.command()
@click.argument("command", required=True)
@click.option("--project", "-p", type=click.Path(exists=True), default=".", help="Project directory (default: current)")
@click.option("--isolation", type=click.Choice(["git", "copy", "auto"]), default="auto", help="Isolation method")
@click.option("--timeout", "-t", type=int, default=300, help="Command timeout in seconds")
@click.option("--stream", is_flag=True, help="Stream output in real-time")
@click.pass_context
def run(ctx, command: str, project: str, isolation: str, timeout: int, stream: bool):
    """Run any command in a protected sandbox environment.
    
    Examples:
        ward run "claude code 'Fix the login bug'"
        ward run "ollama run codellama 'Add tests'"
        ward run "python agent.py --task refactor"
        ward run "npm run build"
    """
    
    async def _run_command():
        config = SandboxConfig(
            main_codebase=Path(project).resolve(),
            autonomy_level=AutonomyLevel.VALIDATED,
            validation_mode=ValidationMode.STRICT,
        )
        
        wrapper = await get_wrapper(config)
        
        # Map isolation choice
        isolation_method = None
        if isolation == "git":
            isolation_method = IsolationMethod.GIT_WORKTREE
        elif isolation == "copy":
            isolation_method = IsolationMethod.FILE_COPY
        # auto = None (let wrapper decide)
        
        if stream:
            # Stream execution
            console.print(f"🔒 Streaming command: [bold]{command}[/bold]")
            console.print("─" * 60)
            
            try:
                async for line in wrapper.stream_execution(
                    command, 
                    Path(project).resolve(),
                    f"Stream execute: {command}"
                ):
                    console.print(line)
                
                console.print("─" * 60)
                console.print("[green]✅ Command completed[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Command failed: {e}[/red]")
                sys.exit(1)
        else:
            # Regular execution with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task_id = progress.add_task("Setting up protected environment...", total=None)
                
                try:
                    progress.update(task_id, description="🔒 Executing command in sandbox...")
                    
                    result = await wrapper.wrap_command(
                        command,
                        Path(project).resolve(),
                        f"Execute: {command}",
                        isolation_method
                    )
                    
                    progress.update(task_id, description="✅ Command completed!")
                    
                    # Display results
                    console.print(f"\n📊 Execution Summary:")
                    console.print(f"   Return Code: {result.return_code}")
                    console.print(f"   Isolation: {result.isolation_method.value}")
                    console.print(f"   Duration: {result.execution_time:.2f}s")
                    console.print(f"   Validation: {'✅ Passed' if result.validation_passed else '❌ Failed'}")
                    
                    # Show output
                    if result.stdout:
                        console.print("\n📤 Output:")
                        console.print(result.stdout)
                    
                    if result.stderr:
                        console.print("\n⚠️  Errors:")
                        console.print(f"[red]{result.stderr}[/red]")
                    
                    # Show validation results
                    if result.validation_results:
                        console.print("\n🔍 Validation Results:")
                        for vr in result.validation_results:
                            status_emoji = "✅" if vr["passed"] else "❌"
                            console.print(f"  {status_emoji} {vr['validator']}: {vr['message']}")
                    
                    # Suggest next steps
                    if result.return_code == 0 and result.validation_passed:
                        console.print(f"\n💡 Use [bold]ward approve[/bold] to apply changes")
                    elif result.return_code == 0:
                        console.print(f"\n💡 Use [bold]ward status[/bold] for validation details")
                    
                    # Store session ID for other commands
                    if result.session_id:
                        ctx.obj["last_session"] = result.session_id
                    
                    # Exit with command's return code
                    if result.return_code != 0:
                        sys.exit(result.return_code)
                    
                except Exception as e:
                    progress.update(task_id, description="❌ Command failed")
                    console.print(f"[red]Error: {e}[/red]")
                    sys.exit(1)
    
    asyncio.run(_run_command())


@cli.command()
@click.argument("task", required=True)
@click.option("--project", "-p", type=click.Path(exists=True), default=".", help="Project directory")
@click.option("--scope", "-s", multiple=True, help="Limit changes to specific paths")
@click.pass_context
def start(ctx, task: str, project: str, scope: tuple[str]):
    """Start a new protected AI session.
    
    Examples:
        ward start "Fix the authentication bug"
        ward start "Add unit tests" --scope src/auth/
        ward start "Refactor database layer" --scope src/db/
    """
    
    async def _start_session():
        config = SandboxConfig(
            main_codebase=Path(project).resolve(),
            autonomy_level=AutonomyLevel.VALIDATED,
            validation_mode=ValidationMode.STRICT,
        )
        
        wrapper = await get_wrapper(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_id = progress.add_task("Creating protected session...", total=None)
            
            try:
                session = await wrapper.orchestrator.start_session(
                    task_description=task,
                    scope_paths=list(scope) if scope else None,
                )
                
                progress.update(task_id, description="✅ Session ready!")
                
                # Display session info
                panel = Panel(
                    f"[bold]Session ID:[/bold] {session.id}\n"
                    f"[bold]Task:[/bold] {session.task_description}\n"
                    f"[bold]Sandbox:[/bold] {session.sandbox_path}\n"
                    f"[bold]Status:[/bold] {session.status.value}",
                    title="🚀 Protected Session Started",
                    border_style="green",
                )
                console.print(panel)
                
                console.print(f"\n💡 Session [bold]{session.id[:8]}[/bold] is ready for AI work")
                console.print("💡 Use [bold]ward status[/bold] to monitor progress")
                
                # Store session ID
                ctx.obj["last_session"] = session.id
                
            except Exception as e:
                progress.update(task_id, description="❌ Failed to create session")
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_start_session())


@cli.command()
@click.option("--project", "-p", type=click.Path(exists=True), default=".", help="Project directory")
@click.pass_context
def status(ctx, project: str):
    """Check status of current protected session."""
    
    async def _get_status():
        config = SandboxConfig(main_codebase=Path(project).resolve())
        wrapper = await get_wrapper(config)
        
        # Get active sessions
        sessions = await wrapper.get_active_sessions()
        
        if not sessions:
            console.print("[yellow]No active sessions found[/yellow]")
            return
        
        # Use last session or most recent
        session_id = ctx.obj.get("last_session") if ctx.obj else None
        if session_id:
            session_data = next((s for s in sessions if s["id"] == session_id), None)
        else:
            session_data = sessions[0]  # Most recent
        
        if not session_data:
            console.print("[red]Session not found[/red]")
            return
        
        try:
            # Get detailed session info
            session = wrapper.orchestrator.session_manager.get_session(session_data["id"])
            if session:
                metrics = await wrapper.orchestrator.get_session_metrics(session.id)
                
                # Create status display
                panel = Panel(
                    f"[bold]Session:[/bold] {session.id[:8]}...\n"
                    f"[bold]Task:[/bold] {session.task_description}\n"
                    f"[bold]Status:[/bold] {session.status.value}\n"
                    f"[bold]Duration:[/bold] {session.duration_minutes:.1f} minutes\n"
                    f"[bold]Files Changed:[/bold] {metrics['files']['total']}\n"
                    f"[bold]Lines:[/bold] +{metrics['lines']['added']} -{metrics['lines']['removed']}\n"
                    f"[bold]Validations:[/bold] {metrics['validations']['passed']}/{metrics['validations']['total']}",
                    title="📊 Session Status",
                    border_style="blue",
                )
                console.print(panel)
                
                # Show validation results if any
                if session.validation_results:
                    console.print("\n🔍 Validation Results:")
                    for vr in session.validation_results:
                        status_emoji = "✅" if vr.passed else "❌"
                        console.print(f"  {status_emoji} {vr.validator_name}: {vr.message}")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
    
    asyncio.run(_get_status())


@cli.command()
@click.option("--project", "-p", type=click.Path(exists=True), default=".", help="Project directory")
@click.option("--force", "-f", is_flag=True, help="Force approval even if validations failed")
@click.pass_context
def approve(ctx, project: str, force: bool):
    """Approve and apply changes to main codebase."""
    
    async def _approve():
        config = SandboxConfig(main_codebase=Path(project).resolve())
        wrapper = await get_wrapper(config)
        
        # Get session to approve
        session_id = ctx.obj.get("last_session") if ctx.obj else None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_id = progress.add_task("Applying changes to main codebase...", total=None)
            
            try:
                success = await wrapper.approve_session(session_id)
                
                if success:
                    progress.update(task_id, description="✅ Changes applied!")
                    console.print(f"\n[green]✅ Changes approved and applied to main codebase![/green]")
                else:
                    progress.update(task_id, description="❌ Approval failed")
                    console.print(f"[red]❌ Failed to apply changes[/red]")
                    sys.exit(1)
                
            except Exception as e:
                progress.update(task_id, description="❌ Approval failed")
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_approve())


@cli.command()
@click.option("--project", "-p", type=click.Path(exists=True), default=".", help="Project directory")
@click.option("--all", "-a", is_flag=True, help="Kill all sessions")
@click.pass_context
def kill(ctx, project: str, all: bool):
    """Emergency stop - terminate and cleanup sessions."""
    
    async def _kill():
        config = SandboxConfig(main_codebase=Path(project).resolve())
        wrapper = await get_wrapper(config)
        
        if all:
            if not click.confirm("Kill all sessions and cleanup all Ward resources?"):
                return
            
            cleanup_result = await wrapper.emergency_cleanup()
            
            total_cleaned = sum(cleanup_result.values())
            console.print(f"[green]✅ Emergency cleanup completed![/green]")
            console.print(f"   Docker containers: {cleanup_result['docker_containers']}")
            console.print(f"   Venv environments: {cleanup_result['venv_environments']}")
            console.print(f"   Sessions: {cleanup_result['sessions']}")
            console.print(f"   Total resources cleaned: {total_cleaned}")
        else:
            # Kill specific session
            session_id = ctx.obj.get("last_session") if ctx.obj else None
            
            if not click.confirm(f"Kill current session?"):
                return
            
            try:
                success = await wrapper.kill_session(session_id)
                if success:
                    console.print(f"[green]✅ Session terminated[/green]")
                else:
                    console.print(f"[red]❌ Failed to terminate session[/red]")
                    sys.exit(1)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_kill())


def main():
    """Main CLI entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()