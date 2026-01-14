"""
Main Orchestrator for AI Sandbox.

This is the central coordination point that ties together:
- Session management
- Sandbox environment lifecycle
- Tool interception
- Validation gates
- Promotion to main codebase
"""

from __future__ import annotations

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import structlog

from ward.core.config import (
    AutonomyLevel,
    SandboxConfig,
    ValidationMode,
)
from ward.core.session import (
    CommandExecution,
    FileChange,
    Session,
    SessionManager,
    SessionStatus,
    ValidationResult,
)
from ward.validators.base import ValidatorRegistry
from ward.validators.validators import (
    LintValidator,
    ScopeValidator,
    SecurityValidator,
    SyntaxValidator,
    TestValidator,
)
from ward.interceptors.base import InterceptorRegistry
from ward.interceptors.filesystem import FilesystemInterceptor
from ward.interceptors.bash import BashInterceptor
from ward.sandbox.manager import SandboxManager, SandboxType
from ward.utils.diff import DiffGenerator
from ward.utils.git import GitHelper
from ward.utils.metrics import MetricsCollector

logger = structlog.get_logger()


class ToolInterceptResult:
    """Result of intercepting a tool call."""
    
    def __init__(
        self,
        allowed: bool,
        executed_in_sandbox: bool = False,
        result: Any = None,
        error: Optional[str] = None,
        feedback: Optional[dict[str, Any]] = None,
    ):
        self.allowed = allowed
        self.executed_in_sandbox = executed_in_sandbox
        self.result = result
        self.error = error
        self.feedback = feedback


class Orchestrator:
    """
    Main orchestration engine for safe AI autonomous coding.
    
    Responsibilities:
    1. Create and manage sandbox environments
    2. Intercept file operations and route to sandbox
    3. Run validation gates
    4. Promote validated changes to main codebase
    5. Provide feedback to AI for self-correction
    
    Usage:
        config = SandboxConfig(main_codebase="/path/to/project")
        orchestrator = Orchestrator(config)
        
        # Start a session
        session = await orchestrator.start_session("Fix payment bug")
        
        # AI tool calls are intercepted
        result = await orchestrator.intercept_file_write(
            session.id, "src/payment.py", new_content
        )
        
        # Validate and promote
        await orchestrator.validate_session(session.id)
        await orchestrator.promote_session(session.id)
    """
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.session_manager = SessionManager()
        self._validators: list[Callable] = []
        self._validator_registry = ValidatorRegistry()
        self._setup_default_validators()
        
        logger.info(
            "Orchestrator initialized",
            main_codebase=str(config.main_codebase),
            autonomy_level=config.autonomy_level.value,
            validation_mode=config.validation_mode.value,
        )
    
    def _setup_default_validators(self) -> None:
        """Setup default validation chain."""
        # Create validator instances from config
        syntax_validator = SyntaxValidator(
            config={
                "enabled": self.config.syntax_validator.enabled,
            }
        )
        self._validator_registry.register(syntax_validator)

        test_validator = TestValidator(
            config={
                "enabled": self.config.test_validator.enabled,
                "test_command": self.config.test_command,
                "timeout": 300,
                "require_pass": self.config.require_tests_pass,
            }
        )
        self._validator_registry.register(test_validator)

        scope_validator = ScopeValidator(
            config={
                "enabled": self.config.scope_validator.enabled,
                "scope_patterns": [],  # Will be set per-session
            }
        )
        self._validator_registry.register(scope_validator)

        security_validator = SecurityValidator(
            config={
                "enabled": self.config.security_validator.enabled,
                "fail_on_secrets": False,  # Typically just warns
            }
        )
        self._validator_registry.register(security_validator)

        # Optional lint validator (disabled by default)
        if hasattr(self.config, "lint_validator") and self.config.lint_validator.enabled:
            lint_validator = LintValidator(
                config={
                    "enabled": self.config.lint_validator.enabled,
                    "lint_command": "ruff check",
                    "fail_on_errors": False,
                }
            )
            self._validator_registry.register(lint_validator)

        logger.debug(
            "Default validators initialized",
            validator_count=len(self._validator_registry.validators),
        )
    
    def add_validator(self, validator: Callable) -> None:
        """Add a custom validator to the chain."""
        self._validators.append(validator)
    
    # === Session Lifecycle ===
    
    async def start_session(
        self,
        task_description: str,
        scope_paths: Optional[list[str]] = None,
    ) -> Session:
        """
        Start a new sandboxed session.
        
        Args:
            task_description: What the AI is trying to accomplish
            scope_paths: Optional list of paths the AI is allowed to modify
        
        Returns:
            Session object to track this work unit
        """
        # Create sandbox directory
        sandbox_path = self._create_sandbox_directory()
        
        # Create session
        session = self.session_manager.create_session(
            task_description=task_description,
            sandbox_path=sandbox_path,
            main_codebase_path=self.config.main_codebase,
            max_files=self.config.max_files_per_session,
            max_lines=self.config.max_lines_changed,
            timeout_minutes=self.config.session_timeout_minutes,
        )
        
        # Store scope in metadata
        if scope_paths:
            session.metadata["allowed_scope"] = scope_paths
        
        # Initialize sandbox with codebase
        await self._initialize_sandbox(session)
        
        session.status = SessionStatus.ACTIVE
        
        logger.info(
            "Session started",
            session_id=session.id,
            task=task_description,
            sandbox_path=str(sandbox_path),
        )
        
        return session
    
    def _create_sandbox_directory(self) -> Path:
        """Create a unique sandbox directory."""
        import uuid
        
        sandbox_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sandbox_name = f"sandbox_{timestamp}_{sandbox_id}"
        sandbox_path = self.config.sandbox_base_dir / sandbox_name
        sandbox_path.mkdir(parents=True, exist_ok=True)
        
        return sandbox_path
    
    async def _initialize_sandbox(self, session: Session) -> None:
        """
        Initialize sandbox with codebase content.
        
        Uses git worktree if available, otherwise copies files.
        """
        if self.config.use_git_worktree:
            success = await self._init_git_worktree(session)
            if success:
                return
        
        # Fallback: copy files
        await self._copy_codebase_to_sandbox(session)
    
    async def _init_git_worktree(self, session: Session) -> bool:
        """Try to initialize sandbox using git worktree."""
        try:
            import git
            
            repo = git.Repo(self.config.main_codebase)
            branch_name = f"{self.config.branch_prefix}{session.id}"
            
            # Create worktree
            repo.git.worktree(
                "add",
                str(session.sandbox_path),
                "-b", branch_name,
                "--detach",
            )
            
            session.metadata["git_branch"] = branch_name
            session.metadata["isolation_method"] = "git_worktree"
            
            logger.info(
                "Git worktree created",
                session_id=session.id,
                branch=branch_name,
            )
            return True
            
        except Exception as e:
            logger.warning(
                "Git worktree failed, falling back to copy",
                error=str(e),
            )
            return False
    
    async def _copy_codebase_to_sandbox(self, session: Session) -> None:
        """Copy codebase files to sandbox (fallback method)."""
        
        def _do_copy():
            shutil.copytree(
                self.config.main_codebase,
                session.sandbox_path,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(
                    ".git",
                    "__pycache__",
                    "*.pyc",
                    "node_modules",
                    ".venv",
                    "venv",
                ),
            )
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _do_copy)
        
        session.metadata["isolation_method"] = "file_copy"
        
        logger.info(
            "Codebase copied to sandbox",
            session_id=session.id,
        )
    
    # === Tool Interception ===
    
    async def intercept_file_write(
        self,
        session_id: str,
        relative_path: str,
        new_content: str,
    ) -> ToolInterceptResult:
        """
        Intercept a file write operation and route to sandbox.
        
        This is called instead of directly writing to the filesystem.
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return ToolInterceptResult(
                allowed=False,
                error=f"Session not found: {session_id}",
            )
        
        if not session.is_active:
            return ToolInterceptResult(
                allowed=False,
                error=f"Session is not active: {session.status.value}",
            )
        
        # Check path restrictions
        if not self.config.is_path_allowed(relative_path):
            logger.warning(
                "Blocked path access",
                session_id=session_id,
                path=relative_path,
            )
            return ToolInterceptResult(
                allowed=False,
                error=f"Path is blocked: {relative_path}",
                feedback=session.get_feedback(),
            )
        
        # Check scope if defined
        allowed_scope = session.metadata.get("allowed_scope")
        if allowed_scope and not self._path_in_scope(relative_path, allowed_scope):
            return ToolInterceptResult(
                allowed=False,
                error=f"Path outside allowed scope: {relative_path}",
                feedback=session.get_feedback(),
            )
        
        # Get original content for diff
        sandbox_file_path = session.sandbox_path / relative_path
        original_content = None
        operation = "create"
        
        if sandbox_file_path.exists():
            original_content = sandbox_file_path.read_text()
            operation = "modify"
        
        # Write to sandbox
        sandbox_file_path.parent.mkdir(parents=True, exist_ok=True)
        sandbox_file_path.write_text(new_content)
        
        # Record change
        file_change = FileChange(
            path=Path(relative_path),
            operation=operation,
            original_content=original_content,
            new_content=new_content,
        )
        session.add_file_change(file_change)
        
        # Check limits
        exceeded, msg = session.exceeds_limits
        if exceeded:
            logger.warning(
                "Session limit exceeded",
                session_id=session_id,
                message=msg,
            )
        
        logger.info(
            "File write intercepted",
            session_id=session_id,
            path=relative_path,
            operation=operation,
            lines_changed=file_change.lines_added + file_change.lines_removed,
        )
        
        return ToolInterceptResult(
            allowed=True,
            executed_in_sandbox=True,
            result={"path": relative_path, "operation": operation},
            feedback=session.get_feedback(),
        )
    
    async def intercept_file_delete(
        self,
        session_id: str,
        relative_path: str,
    ) -> ToolInterceptResult:
        """Intercept a file delete operation."""
        session = self.session_manager.get_session(session_id)
        if not session or not session.is_active:
            return ToolInterceptResult(
                allowed=False,
                error="Invalid or inactive session",
            )
        
        if not self.config.is_path_allowed(relative_path):
            return ToolInterceptResult(
                allowed=False,
                error=f"Path is blocked: {relative_path}",
            )
        
        sandbox_file_path = session.sandbox_path / relative_path
        
        if not sandbox_file_path.exists():
            return ToolInterceptResult(
                allowed=False,
                error=f"File not found: {relative_path}",
            )
        
        original_content = sandbox_file_path.read_text()
        sandbox_file_path.unlink()
        
        file_change = FileChange(
            path=Path(relative_path),
            operation="delete",
            original_content=original_content,
            new_content=None,
        )
        session.add_file_change(file_change)
        
        return ToolInterceptResult(
            allowed=True,
            executed_in_sandbox=True,
            result={"path": relative_path, "operation": "delete"},
            feedback=session.get_feedback(),
        )
    
    async def intercept_command(
        self,
        session_id: str,
        command: str,
        working_dir: Optional[str] = None,
    ) -> ToolInterceptResult:
        """
        Intercept a bash command and execute in sandbox.
        
        Commands are executed with the sandbox as the working directory.
        """
        session = self.session_manager.get_session(session_id)
        if not session or not session.is_active:
            return ToolInterceptResult(
                allowed=False,
                error="Invalid or inactive session",
            )
        
        # Determine working directory
        if working_dir:
            work_path = session.sandbox_path / working_dir
        else:
            work_path = session.sandbox_path
        
        # Check for dangerous commands
        dangerous_patterns = [
            "rm -rf /",
            "rm -rf ~",
            ":(){:|:&};:",  # Fork bomb
            "> /dev/sda",
            "mkfs.",
            "dd if=",
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command:
                return ToolInterceptResult(
                    allowed=False,
                    error=f"Dangerous command pattern detected: {pattern}",
                )
        
        # Execute command
        import time
        
        start_time = time.time()
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=work_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={
                    **dict(__import__("os").environ),
                    "SANDBOX_SESSION_ID": session_id,
                    "SANDBOX_PATH": str(session.sandbox_path),
                },
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300,  # 5 minute timeout
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            execution = CommandExecution(
                command=command,
                working_dir=work_path,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                return_code=process.returncode or 0,
                duration_ms=duration_ms,
            )
            session.add_command_execution(execution)
            
            logger.info(
                "Command executed",
                session_id=session_id,
                command=command[:100],
                return_code=process.returncode,
                duration_ms=duration_ms,
            )
            
            return ToolInterceptResult(
                allowed=True,
                executed_in_sandbox=True,
                result={
                    "stdout": execution.stdout,
                    "stderr": execution.stderr,
                    "return_code": execution.return_code,
                },
                feedback=session.get_feedback(),
            )
            
        except asyncio.TimeoutError:
            return ToolInterceptResult(
                allowed=False,
                error="Command timed out after 300 seconds",
                feedback=session.get_feedback(),
            )
        except Exception as e:
            return ToolInterceptResult(
                allowed=False,
                error=f"Command execution failed: {str(e)}",
                feedback=session.get_feedback(),
            )
    
    def _path_in_scope(self, path: str, scope: list[str]) -> bool:
        """Check if a path is within the allowed scope."""
        from fnmatch import fnmatch
        
        for pattern in scope:
            if fnmatch(path, pattern) or path.startswith(pattern.rstrip("*")):
                return True
        return False
    
    # === Validation ===
    
    async def validate_session(self, session_id: str) -> list[ValidationResult]:
        """
        Run all validation gates on a session.
        
        Returns list of validation results.
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.status = SessionStatus.VALIDATING
        results = []
        
        # Run syntax validation
        if self.config.syntax_validator.enabled:
            result = await self._validate_syntax(session)
            results.append(result)
            session.add_validation_result(result)
        
        # Run tests
        if self.config.test_validator.enabled and self.config.require_tests_pass:
            result = await self._validate_tests(session)
            results.append(result)
            session.add_validation_result(result)
        
        # Run scope validation
        if self.config.scope_validator.enabled:
            result = await self._validate_scope(session)
            results.append(result)
            session.add_validation_result(result)
        
        # Run security validation
        if self.config.security_validator.enabled:
            result = await self._validate_security(session)
            results.append(result)
            session.add_validation_result(result)
        
        # Run custom validators
        for validator in self._validators:
            try:
                result = await validator(session)
                results.append(result)
                session.add_validation_result(result)
            except Exception as e:
                logger.error("Custom validator failed", error=str(e))
        
        # Determine overall status
        all_passed = all(r.passed for r in results)
        has_errors = any(r.errors for r in results)
        
        if self.config.validation_mode == ValidationMode.STRICT:
            if not all_passed or has_errors:
                session.status = SessionStatus.FAILED
            elif self.config.autonomy_level == AutonomyLevel.SUPERVISED:
                session.status = SessionStatus.AWAITING_APPROVAL
            else:
                session.status = SessionStatus.ACTIVE
        elif self.config.validation_mode == ValidationMode.PERMISSIVE:
            if has_errors:
                session.status = SessionStatus.FAILED
            elif self.config.autonomy_level == AutonomyLevel.SUPERVISED:
                session.status = SessionStatus.AWAITING_APPROVAL
            else:
                session.status = SessionStatus.ACTIVE
        else:  # AUDIT_ONLY
            session.status = SessionStatus.ACTIVE
        
        logger.info(
            "Validation complete",
            session_id=session_id,
            all_passed=all_passed,
            status=session.status.value,
        )
        
        return results
    
    async def _validate_syntax(self, session: Session) -> ValidationResult:
        """Validate Python syntax using AST."""
        import ast
        import time
        
        start = time.time()
        errors = []
        warnings = []
        
        for fc in session.file_changes:
            if fc.operation == "delete":
                continue
            if not str(fc.path).endswith(".py"):
                continue
            
            try:
                ast.parse(fc.new_content or "")
            except SyntaxError as e:
                errors.append(f"{fc.path}: Line {e.lineno}: {e.msg}")
        
        duration = int((time.time() - start) * 1000)
        
        return ValidationResult(
            validator_name="syntax",
            passed=len(errors) == 0,
            message=f"Checked {len(session.file_changes)} files",
            errors=errors,
            warnings=warnings,
            duration_ms=duration,
        )
    
    async def _validate_tests(self, session: Session) -> ValidationResult:
        """Run test suite in sandbox."""
        import time
        
        start = time.time()
        
        try:
            process = await asyncio.create_subprocess_shell(
                self.config.test_command,
                cwd=session.sandbox_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.test_timeout_seconds,
            )
            
            duration = int((time.time() - start) * 1000)
            output = stdout.decode("utf-8", errors="replace")
            
            passed = process.returncode == 0
            
            return ValidationResult(
                validator_name="tests",
                passed=passed,
                message=f"Tests {'passed' if passed else 'failed'}",
                details={"output": output[:5000]},  # Truncate
                errors=[stderr.decode()] if not passed else [],
                duration_ms=duration,
            )
            
        except asyncio.TimeoutError:
            return ValidationResult(
                validator_name="tests",
                passed=False,
                message="Test execution timed out",
                errors=[f"Timeout after {self.config.test_timeout_seconds}s"],
                duration_ms=self.config.test_timeout_seconds * 1000,
            )
        except Exception as e:
            return ValidationResult(
                validator_name="tests",
                passed=False,
                message="Test execution failed",
                errors=[str(e)],
                duration_ms=int((time.time() - start) * 1000),
            )
    
    async def _validate_scope(self, session: Session) -> ValidationResult:
        """Validate that changes are within allowed scope."""
        allowed_scope = session.metadata.get("allowed_scope")
        
        if not allowed_scope:
            return ValidationResult(
                validator_name="scope",
                passed=True,
                message="No scope restrictions defined",
            )
        
        violations = []
        for fc in session.file_changes:
            if not self._path_in_scope(str(fc.path), allowed_scope):
                violations.append(f"Out of scope: {fc.path}")
        
        return ValidationResult(
            validator_name="scope",
            passed=len(violations) == 0,
            message=f"Checked {len(session.file_changes)} files against scope",
            errors=violations,
        )
    
    async def _validate_security(self, session: Session) -> ValidationResult:
        """Scan for security issues."""
        import re
        
        # Patterns to detect potential secrets
        secret_patterns = [
            (r'(?i)api[_-]?key\s*[=:]\s*["\'][^"\']+["\']', "API key"),
            (r'(?i)password\s*[=:]\s*["\'][^"\']+["\']', "Password"),
            (r'(?i)secret\s*[=:]\s*["\'][^"\']+["\']', "Secret"),
            (r'(?i)token\s*[=:]\s*["\'][^"\']+["\']', "Token"),
            (r'(?i)aws[_-]?access[_-]?key', "AWS key"),
            (r'(?i)private[_-]?key', "Private key"),
        ]
        
        warnings = []
        
        for fc in session.file_changes:
            if fc.operation == "delete" or not fc.new_content:
                continue
            
            for pattern, name in secret_patterns:
                if re.search(pattern, fc.new_content):
                    warnings.append(f"Potential {name} in {fc.path}")
        
        return ValidationResult(
            validator_name="security",
            passed=True,  # Warnings don't fail by default
            message=f"Scanned {len(session.file_changes)} files",
            warnings=warnings,
        )
    
    # === Promotion ===
    
    async def promote_session(
        self,
        session_id: str,
        force: bool = False,
    ) -> bool:
        """
        Promote validated changes from sandbox to main codebase.
        
        Args:
            session_id: Session to promote
            force: Skip validation check (dangerous!)
        
        Returns:
            True if promotion successful
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Check status
        if not force:
            if session.status == SessionStatus.FAILED:
                raise ValueError("Cannot promote failed session")
            if session.status == SessionStatus.AWAITING_APPROVAL:
                raise ValueError("Session awaiting approval")
            if not session.all_validations_passed:
                raise ValueError("Not all validations passed")
        
        session.status = SessionStatus.PROMOTING
        
        try:
            # Copy changes to main codebase
            for fc in session.file_changes:
                main_file_path = self.config.main_codebase / fc.path
                
                if fc.operation == "delete":
                    if main_file_path.exists():
                        main_file_path.unlink()
                else:
                    main_file_path.parent.mkdir(parents=True, exist_ok=True)
                    main_file_path.write_text(fc.new_content or "")
            
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now()
            
            logger.info(
                "Session promoted",
                session_id=session_id,
                files_changed=len(session.file_changes),
            )
            
            return True
            
        except Exception as e:
            session.status = SessionStatus.FAILED
            logger.error(
                "Promotion failed",
                session_id=session_id,
                error=str(e),
            )
            raise
    
    async def rollback_session(self, session_id: str) -> bool:
        """
        Rollback a session's changes.
        
        For git worktree, deletes the branch.
        For file copy, just removes the sandbox directory.
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Cleanup sandbox
        if session.sandbox_path and session.sandbox_path.exists():
            shutil.rmtree(session.sandbox_path, ignore_errors=True)
        
        # If git worktree, cleanup branch
        if session.metadata.get("isolation_method") == "git_worktree":
            try:
                import git
                
                repo = git.Repo(self.config.main_codebase)
                branch_name = session.metadata.get("git_branch")
                if branch_name:
                    repo.git.worktree("remove", str(session.sandbox_path), "--force")
                    repo.delete_head(branch_name, force=True)
            except Exception as e:
                logger.warning("Git cleanup failed", error=str(e))
        
        session.status = SessionStatus.ROLLED_BACK
        session.completed_at = datetime.now()
        
        logger.info("Session rolled back", session_id=session_id)
        
        return True
    
    # === Utility Methods ===
    
    def get_session_feedback(self, session_id: str) -> dict[str, Any]:
        """Get current feedback for a session."""
        session = self.session_manager.get_session(session_id)
        if not session:
            return {"error": f"Session not found: {session_id}"}
        return session.get_feedback()
    
    def get_all_sessions(self) -> list[dict[str, Any]]:
        """Get all sessions."""
        return self.session_manager.get_session_history()
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Cleanup old completed sessions."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        cleaned = 0
        
        for session in list(self.session_manager._sessions.values()):
            if session.is_terminal and session.completed_at:
                if session.completed_at < cutoff:
                    if session.sandbox_path and session.sandbox_path.exists():
                        shutil.rmtree(session.sandbox_path, ignore_errors=True)
                    del self.session_manager._sessions[session.id]
                    cleaned += 1
        
        return cleaned

    async def get_session_metrics(self, session_id: str) -> dict[str, Any]:
        """Get comprehensive metrics for a session."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        total_files = len(session.file_changes)
        total_lines_added = sum(fc.lines_added for fc in session.file_changes)
        total_lines_removed = sum(fc.lines_removed for fc in session.file_changes)
        
        validation_results = session.validation_results
        passed_validations = sum(1 for vr in validation_results if vr.passed)
        failed_validations = len(validation_results) - passed_validations
        
        return {
            "session_id": session_id,
            "status": session.status.value,
            "duration_minutes": session.duration_minutes,
            "files": {
                "total": total_files,
                "created": sum(1 for fc in session.file_changes if fc.operation == "create"),
                "modified": sum(1 for fc in session.file_changes if fc.operation == "modify"),
                "deleted": sum(1 for fc in session.file_changes if fc.operation == "delete"),
            },
            "lines": {
                "added": total_lines_added,
                "removed": total_lines_removed,
                "net_change": total_lines_added - total_lines_removed,
            },
            "validations": {
                "total": len(validation_results),
                "passed": passed_validations,
                "failed": failed_validations,
                "success_rate": passed_validations / len(validation_results) if validation_results else 0,
            },
            "commands": {
                "total": len(session.command_executions),
                "successful": sum(1 for ce in session.command_executions if ce.success),
                "failed": sum(1 for ce in session.command_executions if not ce.success),
            },
            "limits": {
                "files_used": f"{total_files}/{self.config.max_files_per_session}",
                "lines_used": f"{total_lines_added + total_lines_removed}/{self.config.max_lines_changed}",
                "time_used": f"{session.duration_minutes}/{self.config.session_timeout_minutes}",
            },
        }

    async def auto_commit_changes(self, session_id: str, commit_message: Optional[str] = None) -> bool:
        """Auto-commit changes in sandbox using git."""
        session = self.session_manager.get_session(session_id)
        if not session or not session.sandbox_path:
            return False
        
        try:
            import git
            repo = git.Repo(session.sandbox_path)
            
            # Stage all changes
            repo.git.add(A=True)
            
            # Check if there are changes to commit
            if not repo.is_dirty(staged=True):
                logger.info("No changes to commit", session_id=session_id)
                return True
            
            # Create commit message
            if not commit_message:
                commit_message = f"AI Session {session_id[:8]}: {session.task_description}"
            
            # Commit changes
            repo.index.commit(commit_message)
            logger.info("Auto-committed changes", session_id=session_id, message=commit_message)
            return True
            
        except Exception as e:
            logger.error("Failed to auto-commit", session_id=session_id, error=str(e))
            return False

    async def get_session_diff(self, session_id: str, format: str = "unified") -> str:
        """Get detailed diff of all changes in session."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if not session.file_changes:
            return "No changes in this session."
        
        diff_lines = []
        
        for file_change in session.file_changes:
            diff_lines.append(f"--- {file_change.operation.upper()}: {file_change.path}")
            
            if file_change.operation == "delete":
                diff_lines.append("File deleted")
                continue
            
            if file_change.operation == "create":
                diff_lines.append("New file created")
                if file_change.new_content:
                    for i, line in enumerate(file_change.new_content.splitlines(), 1):
                        diff_lines.append(f"+{i:4d}: {line}")
                continue
            
            # For modify operations, show unified diff
            if file_change.original_content and file_change.new_content:
                import difflib
                original_lines = file_change.original_content.splitlines(keepends=True)
                new_lines = file_change.new_content.splitlines(keepends=True)
                
                unified_diff = difflib.unified_diff(
                    original_lines,
                    new_lines,
                    fromfile=f"a/{file_change.path}",
                    tofile=f"b/{file_change.path}",
                    lineterm="",
                )
                diff_lines.extend(unified_diff)
            
            diff_lines.append("")  # Empty line between files
        
        return "\n".join(diff_lines)

    async def export_session_report(self, session_id: str, format: str = "json") -> dict[str, Any]:
        """Export comprehensive session report."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        metrics = await self.get_session_metrics(session_id)
        diff = await self.get_session_diff(session_id)
        
        report = {
            "session": {
                "id": session.id,
                "task_description": session.task_description,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "duration_minutes": session.duration_minutes,
                "scope_paths": session.scope_paths,
            },
            "metrics": metrics,
            "changes": {
                "summary": session.get_changes_summary(),
                "diff": diff,
                "files": [
                    {
                        "path": str(fc.path),
                        "operation": fc.operation,
                        "lines_added": fc.lines_added,
                        "lines_removed": fc.lines_removed,
                        "timestamp": fc.timestamp.isoformat(),
                    }
                    for fc in session.file_changes
                ],
            },
            "validations": [
                {
                    "validator": vr.validator_name,
                    "passed": vr.passed,
                    "message": vr.message,
                    "errors": vr.errors,
                    "warnings": vr.warnings,
                    "duration_ms": vr.duration_ms,
                }
                for vr in session.validation_results
            ],
            "commands": [
                {
                    "command": ce.command,
                    "working_dir": str(ce.working_dir),
                    "success": ce.success,
                    "return_code": ce.return_code,
                    "stdout": ce.stdout,
                    "stderr": ce.stderr,
                    "duration_ms": ce.duration_ms,
                    "timestamp": ce.timestamp.isoformat(),
                }
                for ce in session.command_executions
            ],
            "config": {
                "autonomy_level": self.config.autonomy_level.value,
                "validation_mode": self.config.validation_mode.value,
                "limits": {
                    "max_files": self.config.max_files_per_session,
                    "max_lines": self.config.max_lines_changed,
                    "timeout_minutes": self.config.session_timeout_minutes,
                },
            },
        }
        
        return report

    def get_orchestrator_status(self) -> dict[str, Any]:
        """Get overall orchestrator status and statistics."""
        sessions = list(self.session_manager._sessions.values())
        
        return {
            "orchestrator": {
                "version": "0.1.0",
                "config": {
                    "main_codebase": str(self.config.main_codebase),
                    "sandbox_base_dir": str(self.config.sandbox_base_dir),
                    "autonomy_level": self.config.autonomy_level.value,
                    "validation_mode": self.config.validation_mode.value,
                },
                "validators": [v.name for v in self._validator_registry.validators],
            },
            "sessions": {
                "total": len(sessions),
                "active": sum(1 for s in sessions if s.status == SessionStatus.ACTIVE),
                "validating": sum(1 for s in sessions if s.status == SessionStatus.VALIDATING),
                "completed": sum(1 for s in sessions if s.status == SessionStatus.COMPLETED),
                "failed": sum(1 for s in sessions if s.status == SessionStatus.FAILED),
            },
            "statistics": {
                "total_files_changed": sum(len(s.file_changes) for s in sessions),
                "total_validations_run": sum(len(s.validation_results) for s in sessions),
                "total_commands_executed": sum(len(s.command_executions) for s in sessions),
                "average_session_duration": (
                    sum(s.duration_minutes for s in sessions if s.completed_at) / 
                    len([s for s in sessions if s.completed_at])
                ) if any(s.completed_at for s in sessions) else 0,
            },
        }