"""Tests for the AI Sandbox Orchestrator."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from ward.core.config import (
    AutonomyLevel,
    SandboxConfig,
    ValidationMode,
)
from ward.core.orchestrator import Orchestrator
from ward.core.session import SessionStatus


class TestOrchestrator:
    """Test suite for the Orchestrator class."""

    @pytest.fixture
    def temp_codebase(self, tmp_path: Path) -> Path:
        """Create a temporary codebase for testing."""
        codebase = tmp_path / "test_project"
        codebase.mkdir()

        # Create some sample files
        (codebase / "main.py").write_text("def main():\n    print('Hello')\n")
        (codebase / "utils.py").write_text("def helper():\n    return 42\n")

        return codebase

    @pytest.fixture
    def config(self, temp_codebase: Path) -> SandboxConfig:
        """Create a test configuration."""
        return SandboxConfig(
            main_codebase=temp_codebase,
            validation_mode=ValidationMode.STRICT,
            autonomy_level=AutonomyLevel.VALIDATED,
        )

    @pytest.fixture
    def orchestrator(self, config: SandboxConfig) -> Orchestrator:
        """Create an orchestrator instance."""
        return Orchestrator(config)

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator: Orchestrator):
        """Test that orchestrator initializes correctly."""
        assert orchestrator.config is not None
        assert orchestrator.session_manager is not None
        assert orchestrator._validator_registry is not None
        assert len(orchestrator._validator_registry.validators) >= 4  # At least 4 default validators

    @pytest.mark.asyncio
    async def test_start_session(self, orchestrator: Orchestrator):
        """Test starting a new session."""
        session = await orchestrator.start_session(
            task_description="Test task",
            scope_paths=["*.py"],
        )

        assert session is not None
        assert session.id is not None
        assert session.task_description == "Test task"
        assert session.sandbox_path is not None
        assert session.sandbox_path.exists()
        assert session.status == SessionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_intercept_file_write(self, orchestrator: Orchestrator):
        """Test file write interception."""
        session = await orchestrator.start_session("Test write")

        result = await orchestrator.intercept_file_write(
            session.id,
            "test.py",
            'def test():\n    return "hello"\n',
        )

        assert result.allowed is True
        assert result.executed_in_sandbox is True
        assert session.total_files_changed == 1

        # Verify file was written to sandbox
        sandbox_file = session.sandbox_path / "test.py"
        assert sandbox_file.exists()
        assert "def test():" in sandbox_file.read_text()

    @pytest.mark.asyncio
    async def test_intercept_file_write_blocked_path(self, orchestrator: Orchestrator):
        """Test that blocked paths are rejected."""
        # Update config to block .env files
        orchestrator.config.blocked_paths = [".env", "*.secret"]

        session = await orchestrator.start_session("Test blocked")

        result = await orchestrator.intercept_file_write(
            session.id,
            ".env",
            "SECRET_KEY=abc123",
        )

        assert result.allowed is False
        assert "blocked" in result.error.lower()

    @pytest.mark.asyncio
    async def test_intercept_file_delete(self, orchestrator: Orchestrator):
        """Test file deletion interception."""
        session = await orchestrator.start_session("Test delete")

        # First create a file
        await orchestrator.intercept_file_write(session.id, "delete_me.py", "# temp")

        # Then delete it
        result = await orchestrator.intercept_file_delete(session.id, "delete_me.py")

        assert result.allowed is True
        assert session.total_files_changed == 2  # One create, one delete

    @pytest.mark.asyncio
    async def test_intercept_command_safe(self, orchestrator: Orchestrator):
        """Test safe command execution."""
        session = await orchestrator.start_session("Test command")

        result = await orchestrator.intercept_command(
            session.id,
            "echo 'hello world'",
        )

        assert result.allowed is True
        assert "hello world" in result.result.get("stdout", "")

    @pytest.mark.asyncio
    async def test_intercept_command_dangerous(self, orchestrator: Orchestrator):
        """Test that dangerous commands are blocked."""
        session = await orchestrator.start_session("Test dangerous")

        result = await orchestrator.intercept_command(
            session.id,
            "rm -rf /",
        )

        assert result.allowed is False
        assert "dangerous" in result.error.lower()

    @pytest.mark.asyncio
    async def test_validate_session_syntax_valid(self, orchestrator: Orchestrator):
        """Test syntax validation with valid Python code."""
        session = await orchestrator.start_session("Test syntax valid")

        await orchestrator.intercept_file_write(
            session.id,
            "valid.py",
            'def valid_function():\n    return "valid"\n',
        )

        results = await orchestrator.validate_session(session.id)

        syntax_result = next((r for r in results if r.validator_name == "syntax"), None)
        assert syntax_result is not None
        assert syntax_result.passed is True

    @pytest.mark.asyncio
    async def test_validate_session_syntax_invalid(self, orchestrator: Orchestrator):
        """Test syntax validation with invalid Python code."""
        session = await orchestrator.start_session("Test syntax invalid")

        await orchestrator.intercept_file_write(
            session.id,
            "invalid.py",
            'def invalid_function(\n    # Missing closing parenthesis\n',
        )

        results = await orchestrator.validate_session(session.id)

        syntax_result = next((r for r in results if r.validator_name == "syntax"), None)
        assert syntax_result is not None
        assert syntax_result.passed is False
        assert len(syntax_result.errors) > 0

    @pytest.mark.asyncio
    async def test_validate_session_security(self, orchestrator: Orchestrator):
        """Test security validation detects secrets."""
        session = await orchestrator.start_session("Test security")

        await orchestrator.intercept_file_write(
            session.id,
            "secrets.py",
            'API_KEY = "sk-1234567890abcdef"\nPASSWORD = "secret123"\n',
        )

        results = await orchestrator.validate_session(session.id)

        security_result = next((r for r in results if r.validator_name == "security"), None)
        assert security_result is not None
        # Security validator should warn but not fail by default
        assert len(security_result.warnings) > 0

    @pytest.mark.asyncio
    async def test_session_limits_files(self, orchestrator: Orchestrator):
        """Test that file limits are enforced."""
        orchestrator.config.max_files_per_session = 2

        session = await orchestrator.start_session("Test limits")

        # Write 3 files (exceeds limit)
        await orchestrator.intercept_file_write(session.id, "file1.py", "# 1")
        await orchestrator.intercept_file_write(session.id, "file2.py", "# 2")
        result = await orchestrator.intercept_file_write(session.id, "file3.py", "# 3")

        assert result.allowed is False
        assert "limit" in result.error.lower()

    @pytest.mark.asyncio
    async def test_promote_session_success(self, orchestrator: Orchestrator, temp_codebase: Path):
        """Test successful promotion of changes."""
        session = await orchestrator.start_session("Test promote")

        # Make a change
        await orchestrator.intercept_file_write(
            session.id,
            "new_file.py",
            'def new_function():\n    return "new"\n',
        )

        # Validate (should pass for valid syntax)
        await orchestrator.validate_session(session.id)

        # Promote
        success = await orchestrator.promote_session(session.id)

        assert success is True
        assert (temp_codebase / "new_file.py").exists()
        assert "def new_function" in (temp_codebase / "new_file.py").read_text()

    @pytest.mark.asyncio
    async def test_promote_session_without_validation_fails(
        self, orchestrator: Orchestrator
    ):
        """Test that promotion fails without validation."""
        session = await orchestrator.start_session("Test promote no validation")

        await orchestrator.intercept_file_write(session.id, "test.py", "# test")

        # Try to promote without validation
        with pytest.raises(ValueError, match="validation"):
            await orchestrator.promote_session(session.id)

    @pytest.mark.asyncio
    async def test_rollback_session(self, orchestrator: Orchestrator, temp_codebase: Path):
        """Test rolling back a session."""
        session = await orchestrator.start_session("Test rollback")

        # Make changes
        await orchestrator.intercept_file_write(
            session.id,
            "temp.py",
            "# This should be rolled back",
        )

        # Rollback
        await orchestrator.rollback_session(session.id)

        # Verify sandbox is cleaned up
        assert not session.sandbox_path.exists()
        assert session.status == SessionStatus.ROLLED_BACK

        # Verify main codebase is unchanged
        assert not (temp_codebase / "temp.py").exists()

    @pytest.mark.asyncio
    async def test_session_feedback(self, orchestrator: Orchestrator):
        """Test getting session feedback."""
        session = await orchestrator.start_session("Test feedback")

        await orchestrator.intercept_file_write(session.id, "test.py", "# test")

        feedback = orchestrator.get_session_feedback(session.id)

        assert feedback is not None
        assert "session_id" in feedback
        assert "status" in feedback
        assert "diff_summary" in feedback
        assert feedback["diff_summary"]["total_files"] == 1

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, orchestrator: Orchestrator):
        """Test multiple concurrent sessions."""
        session1 = await orchestrator.start_session("Task 1")
        session2 = await orchestrator.start_session("Task 2")

        assert session1.id != session2.id

        # Make different changes in each session
        await orchestrator.intercept_file_write(session1.id, "file1.py", "# 1")
        await orchestrator.intercept_file_write(session2.id, "file2.py", "# 2")

        assert session1.total_files_changed == 1
        assert session2.total_files_changed == 1

    @pytest.mark.asyncio
    async def test_scope_validation(self, orchestrator: Orchestrator):
        """Test scope validation."""
        session = await orchestrator.start_session(
            "Test scope",
            scope_paths=["src/*.py"],
        )

        # This should be allowed (matches scope)
        result1 = await orchestrator.intercept_file_write(
            session.id,
            "src/module.py",
            "# in scope",
        )
        assert result1.allowed is True

        # This should fail scope validation (outside scope)
        result2 = await orchestrator.intercept_file_write(
            session.id,
            "tests/test.py",
            "# out of scope",
        )
        assert result2.allowed is False


class TestValidators:
    """Test suite for the validator classes."""

    @pytest.mark.asyncio
    async def test_syntax_validator_import(self):
        """Test that validators can be imported."""
        from ward.validators.validators import SyntaxValidator

        validator = SyntaxValidator()
        assert validator.name == "syntax"

    @pytest.mark.asyncio
    async def test_test_validator_import(self):
        """Test that test validator can be imported."""
        from ward.validators.validators import TestValidator

        validator = TestValidator()
        assert validator.name == "tests"

    @pytest.mark.asyncio
    async def test_validator_registry(self):
        """Test the validator registry."""
        from ward.validators.base import ValidatorRegistry
        from ward.validators.validators import (
            SyntaxValidator,
            TestValidator,
        )

        registry = ValidatorRegistry()
        assert len(registry.validators) == 0

        registry.register(SyntaxValidator())
        registry.register(TestValidator())
        assert len(registry.validators) == 2

        registry.unregister("syntax")
        assert len(registry.validators) == 1


class TestConfig:
    """Test suite for configuration."""

    def test_default_config(self, tmp_path: Path):
        """Test default configuration values."""
        config = SandboxConfig(main_codebase=tmp_path)

        assert config.validation_mode == ValidationMode.STRICT
        assert config.autonomy_level == AutonomyLevel.VALIDATED
        assert config.max_files_per_session == 20
        assert config.max_lines_changed == 1000
        assert config.require_tests_pass is True

    def test_config_with_custom_values(self, tmp_path: Path):
        """Test configuration with custom values."""
        config = SandboxConfig(
            main_codebase=tmp_path,
            validation_mode=ValidationMode.PERMISSIVE,
            autonomy_level=AutonomyLevel.AUTONOMOUS,
            max_files_per_session=10,
            blocked_paths=[".env", "*.secret"],
        )

        assert config.validation_mode == ValidationMode.PERMISSIVE
        assert config.autonomy_level == AutonomyLevel.AUTONOMOUS
        assert config.max_files_per_session == 10
        assert ".env" in config.blocked_paths


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
