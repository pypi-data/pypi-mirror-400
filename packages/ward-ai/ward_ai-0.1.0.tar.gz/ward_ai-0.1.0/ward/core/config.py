"""
Cnfiguration management for AI sandbox Orchestrator.

Defines all configuration options, autonomy levels, and validation modes.
"""


from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional


from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

class AutonomyLevel(str, Enum):
    SUPERVISED = "supervised"
    VALIDATED = "validated"
    AUTONOMOUS = "autonomous"
    
class ValidationMode(str, Enum):
    STRICT = "strict"
    PERMISSIVE = "permissive"
    AUDIT_ONLY = "audit_only"
    
class ValidatorConfig(BaseModel):
    enabled: bool = True
    fail_on_warning: bool = False
    timeout_seconds: int = 60
    custom_args: dict = Field(default_factory=dict)
    
class SandboxConfig(BaseSettings):
    model_config = {"env_prefix": "SANDBOX_"}
    
    #Core paths
    main_codebase: Path = Field(description="Path to the main codebase to protect.")
    sandbox_base_dir: Path = Field(
        default=Path("/tmp/ward/sandboxes"),
        description="Base directory for sandbox environments.",
    )
    logs_dir: Path = Field(
        default=Path("/tmp/ward/logs"),
        description="Directory to store logs.",
    )
    
    #autonomy settings
    autonomy_level: AutonomyLevel = Field(
        default=AutonomyLevel.VALIDATED,
        description="Level of autonomy for AI agents.",
    )
    
    validation_mode: ValidationMode = Field(
        default=ValidationMode.STRICT,
        description="Mode of validation for AI-generated code.",
    )
    
    #safety limits
    max_files_per_session:int = Field(default=20, ge=1, le=100)
    max_lines_changed: int = Field(default=1000, ge=10, le=10000)
    session_timeout_minutes:int = Field(default=60, ge=5, le=480)
    
    
    #path restrictions
    blocked_paths:list[str] = Field(
        default_factory=lambda: [
            ".env",
            ".env.*",
            "**/secrets/*",
            "**/credentials/*",
            "**/*.pem",
            "**/*.key",
            "**/id_rsa*",
        ]
    )
    
    allowed_paths:Optional[list[str]] = Field(
        default=None,
        description="If set, only these paths can be modified by AI agents.",
    )
    
    #validation settings
    require_human_approval: bool = Field(
        default=True,
        description="Whether human approval is required before applying changes.",
    )
    
    require_tests_pass:bool= Field(default=True, description="Whether all tests must pass before applying changes.")
    require_linting_pass:bool= Field(default=True, description="Whether linting must pass before applying changes.")
    
    #test configuration
    test_command:str = Field(default="pytest", description="Command to run tests.")
    test_timeout_seconds:int = Field(default=300, ge=10, le=3600)
    
    #git integration
    use_git_worktree: bool = Field(default=True, description="Whether to use git worktrees for sandboxing.")
    auto_commit_sandbox:bool= Field(default=True, description="Whether to auto-commit changes in the sandbox.")
    branch_prefix:str= Field(default="ai_sandbox", description="Prefix for sandbox branches.")
    
    #feedback loop
    provide_test_outputs: bool = Field(default=True, description="Whether to provide test outputs to AI agents.")
    provide_diff_summary:bool= Field(default=True, description="Whether to provide a summary of code diffs to AI agents.")
    
    #validators configuration
    syntax_validator: ValidatorConfig = Field(default_factory=ValidatorConfig)
    test_validator: ValidatorConfig = Field(default_factory=ValidatorConfig)
    lint_validator: ValidatorConfig = Field(default_factory=ValidatorConfig)
    scope_validator: ValidatorConfig = Field(default_factory=ValidatorConfig)
    security_validator: ValidatorConfig = Field(default_factory=ValidatorConfig)
    
    @field_validator("main_codebase", mode="before")
    @classmethod
    def validate_main_codebase(cls, v:str | Path) -> str | Path:
        path = Path(v).resolve()
        if not path.exists():
            raise ValueError(f"Main codebase path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Main codebase path is not a directory: {path}")
        return path
    
    @field_validator("sandbox_base_dir", "logs_dir", mode="before")
    @classmethod
    def validate_sandbox_dir(cls, v:str | Path) -> str | Path:
        path = Path(v).resolve()
        path.mkdir(parents=True, exist_ok=True)
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        return path
    
    def is_path_blocked(self, path:str | Path) -> bool:
        from fnmatch import fnmatch
        path_str = str(Path(path).resolve())
        for pattern in self.blocked_paths:
            if fnmatch(path_str, pattern):
                return True
        return False
    
    def is_path_allowed(self, path:str | Path) -> bool:
        if self.allowed_paths is None:
            return not self.is_path_blocked(path)
        from fnmatch import fnmatch
        path_str = str(path)
        for pattern in self.allowed_paths:
            if fnmatch(path_str, pattern):
                return not self.is_path_blocked(path)
        return False