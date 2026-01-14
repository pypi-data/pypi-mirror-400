"""Session management for AI Sandbox Orchestrator."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class SessionStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    VALIDATING = "validating"
    AWAITING_APPROVAL = "awaiting_approval"
    PROMOTING = "promoting"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class FileChange:
    path: Path
    operation: str  # create, modify, delete
    original_content: Optional[str]
    new_content: Optional[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def lines_added(self) -> int:
        if self.new_content is None:
            return 0
        if self.original_content is None:
            return len(self.new_content.splitlines())
        original_lines = set(self.original_content.splitlines())
        return sum(1 for line in self.new_content.splitlines() if line not in original_lines)
    
    @property
    def lines_removed(self) -> int:
        if self.original_content is None:
            return 0
        if self.new_content is None:
            return len(self.original_content.splitlines())
        new_lines = set(self.new_content.splitlines())
        return sum(1 for line in self.original_content.splitlines() if line not in new_lines)


@dataclass
class CommandExecution:
    command: str
    working_dir: Path
    stdout: str
    stderr: str
    return_code: int
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    
    @property
    def success(self) -> bool:
        return self.return_code == 0


@dataclass
class ValidationResult:
    validator_name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_ms: int = 0


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_description: str = ""
    status: SessionStatus = SessionStatus.INITIALIZING
    
    sandbox_path: Optional[Path] = None
    main_codebase_path: Optional[Path] = None
    
    file_changes: list[FileChange] = field(default_factory=list)
    command_executions: list[CommandExecution] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    max_files: int = 20
    max_lines: int = 1000
    timeout_minutes: int = 60
    
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.started_at = datetime.now()
    
    @property
    def is_active(self) -> bool:
        return self.status in (SessionStatus.ACTIVE, SessionStatus.VALIDATING)
    
    @property
    def is_terminal(self) -> bool:
        return self.status in (
            SessionStatus.COMPLETED, SessionStatus.FAILED,
            SessionStatus.ROLLED_BACK, SessionStatus.EXPIRED, SessionStatus.CANCELLED,
        )
    
    @property
    def total_files_changed(self) -> int:
        return len(self.file_changes)
    
    @property
    def total_lines_changed(self) -> int:
        return sum(fc.lines_added + fc.lines_removed for fc in self.file_changes)
    
    @property
    def exceeds_limits(self) -> tuple[bool, str]:
        if self.total_files_changed > self.max_files:
            return True, f"Exceeded max files: {self.total_files_changed}/{self.max_files}"
        if self.total_lines_changed > self.max_lines:
            return True, f"Exceeded max lines: {self.total_lines_changed}/{self.max_lines}"
        return False, ""
    
    @property
    def all_validations_passed(self) -> bool:
        if not self.validation_results:
            return False
        return all(vr.passed for vr in self.validation_results)
    
    def add_file_change(self, change: FileChange) -> None:
        for i, existing in enumerate(self.file_changes):
            if existing.path == change.path:
                change.original_content = existing.original_content
                self.file_changes[i] = change
                return
        self.file_changes.append(change)
    
    def add_validation_result(self, result: ValidationResult) -> None:
        self.validation_results.append(result)

    def add_command_execution(self, execution: CommandExecution) -> None:
        """Add a command execution record to the session."""
        self.command_executions.append(execution)
    
    def get_diff_summary(self) -> dict[str, Any]:
        files_by_op = {"create": [], "modify": [], "delete": []}
        for fc in self.file_changes:
            files_by_op[fc.operation].append(str(fc.path))
        return {
            "total_files": self.total_files_changed,
            "total_lines_added": sum(fc.lines_added for fc in self.file_changes),
            "total_lines_removed": sum(fc.lines_removed for fc in self.file_changes),
            "files_created": files_by_op["create"],
            "files_modified": files_by_op["modify"],
            "files_deleted": files_by_op["delete"],
        }
    
    def get_feedback(self) -> dict[str, Any]:
        exceeded, limit_msg = self.exceeds_limits
        return {
            "session_id": self.id,
            "status": self.status.value,
            "location": "sandbox",
            "diff_summary": self.get_diff_summary(),
            "limit_exceeded": exceeded,
            "limit_message": limit_msg if exceeded else None,
            "validations": [
                {"name": vr.validator_name, "passed": vr.passed, "message": vr.message}
                for vr in self.validation_results
            ],
        }


class SessionManager:
    def __init__(self, max_concurrent_sessions: int = 5):
        self.max_concurrent_sessions = max_concurrent_sessions
        self._sessions: dict[str, Session] = {}
    
    def create_session(self, task_description: str, sandbox_path: Path,
                       main_codebase_path: Path, **kwargs) -> Session:
        active_count = sum(1 for s in self._sessions.values() if s.is_active)
        if active_count >= self.max_concurrent_sessions:
            raise RuntimeError(f"Max concurrent sessions ({self.max_concurrent_sessions}) reached")
        
        session = Session(
            task_description=task_description,
            sandbox_path=sandbox_path,
            main_codebase_path=main_codebase_path,
            **kwargs
        )
        self._sessions[session.id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def get_session_history(self, limit: int = 100) -> list[Session]:
        """Get session history sorted by creation time (newest first)."""
        sessions = sorted(
            self._sessions.values(),
            key=lambda s: s.created_at,
            reverse=True
        )
        return sessions[:limit]