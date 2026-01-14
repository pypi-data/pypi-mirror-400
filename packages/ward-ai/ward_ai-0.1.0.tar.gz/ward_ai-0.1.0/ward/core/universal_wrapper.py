"""Universal command wrapper - the core of Ward's safety layer."""

from __future__ import annotations

import asyncio
import shlex
import shutil
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, AsyncIterator, Dict, Any

import structlog
from pydantic import BaseModel

from .config import SandboxConfig
from .orchestrator import Orchestrator

logger = structlog.get_logger()


class IsolationMethod(Enum):
    """Available isolation methods for command execution."""
    GIT_WORKTREE = "git_worktree"
    FILE_COPY = "file_copy"
    NATIVE = "native"  # No isolation (for testing)


class ExecutionResult(BaseModel):
    """Result of command execution in Ward."""
    return_code: int
    stdout: str
    stderr: str
    session_id: str
    isolation_method: IsolationMethod
    execution_time: float
    validation_passed: bool
    validation_results: list[Dict[str, Any]] = []


class UniversalWrapper:
    """Universal command wrapper that provides safety layer for any command."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.orchestrator = Orchestrator(config)
        self._isolation_method: Optional[IsolationMethod] = None
    
    async def initialize(self) -> None:
        """Initialize the wrapper and detect best isolation method."""
        # Check if git is available and we're in a git repo
        if self._is_git_available() and self._is_git_repo():
            self._isolation_method = IsolationMethod.GIT_WORKTREE
            logger.info("Ward initialized with git worktree isolation")
        else:
            self._isolation_method = IsolationMethod.FILE_COPY
            logger.info("Ward initialized with file copy isolation")
    
    def _is_git_available(self) -> bool:
        """Check if git command is available."""
        return shutil.which("git") is not None
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.config.main_codebase,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def detect_isolation_method(self) -> IsolationMethod:
        """Auto-detect the best isolation method for current platform."""
        if self._isolation_method:
            return self._isolation_method
        
        # Check git availability
        if self._is_git_available() and self._is_git_repo():
            return IsolationMethod.GIT_WORKTREE
        
        # Fall back to file copy isolation
        return IsolationMethod.FILE_COPY
    
    async def wrap_command(
        self, 
        command: str, 
        project_path: Optional[Path] = None,
        task_description: Optional[str] = None,
        isolation_method: Optional[IsolationMethod] = None
    ) -> ExecutionResult:
        """
        Wrap any command in Ward's safety layer.
        
        Args:
            command: The command to execute
            project_path: Project directory (defaults to config.main_codebase)
            task_description: Description of what the command does
            isolation_method: Force specific isolation method
            
        Returns:
            ExecutionResult with command output and validation results
        """
        import time
        start_time = time.time()
        
        # Use provided path or default to config
        if project_path is None:
            project_path = self.config.main_codebase
        
        # Determine isolation method
        if isolation_method is None:
            isolation_method = self.detect_isolation_method()
        
        # Generate task description if not provided
        if task_description is None:
            task_description = f"Execute command: {command}"
        
        logger.info("Ward wrapping command", 
                   command=command,
                   isolation_method=isolation_method.value,
                   project_path=str(project_path))
        
        try:
            # Create Ward session for this command
            session = await self.orchestrator.start_session(
                task_description=task_description,
                scope_paths=None,
            )
            
            # Execute command based on isolation method
            if isolation_method == IsolationMethod.GIT_WORKTREE:
                return_code, stdout, stderr = await self._execute_git_worktree(
                    session.id, command, project_path
                )
            elif isolation_method == IsolationMethod.FILE_COPY:
                return_code, stdout, stderr = await self._execute_file_copy(
                    session.id, command, project_path
                )
            else:  # NATIVE
                return_code, stdout, stderr = await self._execute_native(
                    command, project_path
                )
            
            execution_time = time.time() - start_time
            
            # Run validation if command succeeded
            validation_results = []
            validation_passed = True
            
            if return_code == 0:
                try:
                    validation_results = await self.orchestrator.validate_session(session.id)
                    validation_passed = all(vr.passed for vr in validation_results)
                    
                    logger.info("Command validation completed",
                               session_id=session.id,
                               validation_passed=validation_passed,
                               total_validations=len(validation_results))
                               
                except Exception as e:
                    logger.warning("Validation failed", session_id=session.id, error=str(e))
                    validation_passed = False
            
            return ExecutionResult(
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                session_id=session.id,
                isolation_method=isolation_method,
                execution_time=execution_time,
                validation_passed=validation_passed,
                validation_results=[
                    {
                        "validator": vr.validator_name,
                        "passed": vr.passed,
                        "message": vr.message,
                        "errors": vr.errors,
                        "warnings": vr.warnings,
                    }
                    for vr in validation_results
                ]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error("Command execution failed", 
                        command=command, 
                        error=str(e))
            
            return ExecutionResult(
                return_code=1,
                stdout="",
                stderr=f"Ward execution error: {str(e)}",
                session_id="",
                isolation_method=isolation_method,
                execution_time=execution_time,
                validation_passed=False,
                validation_results=[]
            )
    
    async def _execute_git_worktree(
        self, 
        session_id: str, 
        command: str, 
        project_path: Path
    ) -> tuple[int, str, str]:
        """Execute command in git worktree (safest isolation)."""
        import subprocess
        
        # Create worktree in temp directory
        worktree_path = Path(tempfile.mkdtemp(prefix=f"ward-worktree-{session_id[:8]}-"))
        
        try:
            # Create git worktree
            subprocess.run([
                "git", "worktree", "add", str(worktree_path), "HEAD"
            ], cwd=project_path, check=True)
            
            logger.info("Created git worktree", 
                       session_id=session_id,
                       worktree_path=str(worktree_path))
            
            # Execute command in worktree
            return await self._execute_native(command, worktree_path)
            
        finally:
            # Cleanup worktree
            try:
                subprocess.run([
                    "git", "worktree", "remove", str(worktree_path), "--force"
                ], cwd=project_path, timeout=30)
                logger.info("Cleaned up git worktree", session_id=session_id)
            except Exception as e:
                logger.warning("Failed to cleanup worktree", 
                              session_id=session_id, 
                              error=str(e))
    
    async def _execute_file_copy(
        self, 
        session_id: str, 
        command: str, 
        project_path: Path
    ) -> tuple[int, str, str]:
        """Execute command in copied directory (fallback isolation)."""
        # Create temp directory and copy project
        temp_dir = Path(tempfile.mkdtemp(prefix=f"ward-copy-{session_id[:8]}-"))
        
        try:
            # Copy project files
            shutil.copytree(project_path, temp_dir / "project")
            sandbox_path = temp_dir / "project"
            
            logger.info("Created file copy sandbox", 
                       session_id=session_id,
                       sandbox_path=str(sandbox_path))
            
            # Execute command in copied directory
            return await self._execute_native(command, sandbox_path)
            
        finally:
            # Cleanup temp directory
            try:
                shutil.rmtree(temp_dir)
                logger.info("Cleaned up file copy sandbox", session_id=session_id)
            except Exception as e:
                logger.warning("Failed to cleanup sandbox", 
                              session_id=session_id, 
                              error=str(e))
    
    async def _execute_native(
        self, 
        command: str, 
        project_path: Path
    ) -> tuple[int, str, str]:
        """Execute command natively in specified directory."""
        # Parse command
        cmd_parts = shlex.split(command)
        
        # Execute command
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            cwd=project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        return (
            process.returncode or 0,
            stdout.decode() if stdout else "",
            stderr.decode() if stderr else ""
        )
    
    async def stream_execution(
        self, 
        command: str,
        project_path: Optional[Path] = None,
        task_description: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Stream command execution output in real-time.
        
        Yields lines of output as they become available.
        """
        if project_path is None:
            project_path = self.config.main_codebase
        
        if task_description is None:
            task_description = f"Stream execute: {command}"
        
        isolation_method = self.detect_isolation_method()
        
        logger.info("Ward streaming command", 
                   command=command,
                   isolation_method=isolation_method.value)
        
        # For now, implement basic streaming for native execution
        # TODO: Implement streaming for git worktree and file copy
        cmd_parts = shlex.split(command)
        
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            cwd=project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,  # Combine streams
        )
        
        if process.stdout:
            async for line in process.stdout:
                yield line.decode().rstrip()
        
        await process.wait()
    
    async def get_active_sessions(self) -> list[Dict[str, Any]]:
        """Get list of active Ward sessions."""
        sessions = list(self.orchestrator.session_manager._sessions.values())
        
        return [
            {
                "id": session.id,
                "task": session.task_description,
                "status": session.status.value,
                "created": session.created_at.isoformat(),
                "duration_minutes": session.duration_minutes,
                "files_changed": len(session.file_changes),
            }
            for session in sessions
        ]
    
    async def approve_session(self, session_id: Optional[str] = None) -> bool:
        """Approve and promote a Ward session to main codebase."""
        if session_id is None:
            # Get most recent session
            sessions = list(self.orchestrator.session_manager._sessions.values())
            if not sessions:
                return False
            session_id = max(sessions, key=lambda s: s.created_at).id
        
        return await self.orchestrator.promote_session(session_id)
    
    async def kill_session(self, session_id: Optional[str] = None) -> bool:
        """Kill and cleanup a Ward session."""
        if session_id is None:
            # Get most recent session
            sessions = list(self.orchestrator.session_manager._sessions.values())
            if not sessions:
                return False
            session_id = max(sessions, key=lambda s: s.created_at).id
        
        return await self.orchestrator.rollback_session(session_id)
    
    async def emergency_cleanup(self) -> Dict[str, int]:
        """Emergency cleanup of all Ward resources."""
        logger.warning("Ward emergency cleanup initiated")
        
        # Cleanup orchestrator sessions
        sessions_cleaned = len(self.orchestrator.session_manager._sessions)
        for session_id in list(self.orchestrator.session_manager._sessions.keys()):
            await self.orchestrator.rollback_session(session_id)
        
        return {
            "sessions": sessions_cleaned,
        }


# Global wrapper instance for CLI usage
_wrapper_instance: Optional[UniversalWrapper] = None


async def get_wrapper(config: Optional[SandboxConfig] = None) -> UniversalWrapper:
    """Get or create the global Ward wrapper instance."""
    global _wrapper_instance
    
    if _wrapper_instance is None:
        if config is None:
            # Create default config
            config = SandboxConfig(main_codebase=Path.cwd())
        
        _wrapper_instance = UniversalWrapper(config)
        await _wrapper_instance.initialize()
    
    return _wrapper_instance