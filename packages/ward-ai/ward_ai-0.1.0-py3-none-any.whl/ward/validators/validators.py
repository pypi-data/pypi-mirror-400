"""Concrete validator implementations."""

from __future__ import annotations

import ast
import asyncio
import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from .base import BaseValidator
from ..core.session import Session, ValidationResult


class SyntaxValidator(BaseValidator):
    """
    Validates Python syntax using AST parsing.

    Checks all modified .py files for syntax errors.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("syntax", config)

    def is_applicable(self, session: Session) -> bool:
        """Only applicable if there are Python file changes."""
        if not super().is_applicable(session):
            return False
        return any(
            str(fc.path).endswith(".py") and fc.operation != "delete"
            for fc in session.file_changes
        )

    async def validate(self, session: Session) -> ValidationResult:
        """Validate Python syntax for all changed files."""
        errors = []

        for file_change in session.file_changes:
            if not str(file_change.path).endswith(".py"):
                continue
            if file_change.operation == "delete":
                continue
            if not file_change.new_content:
                continue

            try:
                ast.parse(file_change.new_content)
            except SyntaxError as e:
                errors.append(f"{file_change.path}:{e.lineno}: {e.msg}")

        passed = len(errors) == 0
        return ValidationResult(
            validator_name=self.name,
            passed=passed,
            message="Syntax validation passed" if passed else "Syntax errors found",
            errors=errors,
            details={"files_checked": sum(
                1 for fc in session.file_changes
                if str(fc.path).endswith(".py") and fc.operation != "delete"
            )},
        )


class TestValidator(BaseValidator):
    """
    Runs test suite to validate changes.

    Executes test command (default: pytest) in the sandbox environment.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("tests", config)
        self.test_command = self.config.get("test_command", "pytest")
        self.timeout = self.config.get("timeout", 300)
        self.require_pass = self.config.get("require_pass", True)

    def is_applicable(self, session: Session) -> bool:
        """Only applicable if tests are required."""
        if not super().is_applicable(session):
            return False
        return self.require_pass

    async def validate(self, session: Session) -> ValidationResult:
        """Run tests in the sandbox environment."""
        if not session.sandbox_path:
            return ValidationResult(
                validator_name=self.name,
                passed=False,
                message="No sandbox path available",
                errors=["Sandbox path not set"],
            )

        try:
            process = await asyncio.create_subprocess_shell(
                self.test_command,
                cwd=session.sandbox_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ValidationResult(
                    validator_name=self.name,
                    passed=False,
                    message=f"Tests timed out after {self.timeout}s",
                    errors=[f"Test execution exceeded {self.timeout}s timeout"],
                )

            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            passed = process.returncode == 0

            return ValidationResult(
                validator_name=self.name,
                passed=passed,
                message="Tests passed" if passed else f"Tests failed (exit code: {process.returncode})",
                details={
                    "command": self.test_command,
                    "exit_code": process.returncode,
                    "stdout": stdout_str[-1000:],  # Last 1000 chars
                    "stderr": stderr_str[-1000:],
                },
                errors=[] if passed else [f"Test suite failed with exit code {process.returncode}"],
            )

        except FileNotFoundError:
            return ValidationResult(
                validator_name=self.name,
                passed=False,
                message=f"Test command not found: {self.test_command}",
                errors=[f"Command '{self.test_command}' not found in PATH"],
                warnings=[f"Install test runner or disable test validation"],
            )
        except Exception as e:
            return ValidationResult(
                validator_name=self.name,
                passed=False,
                message=f"Test execution error: {str(e)}",
                errors=[str(e)],
            )


class ScopeValidator(BaseValidator):
    """
    Validates that changes are within allowed scope.

    Ensures modified files match the expected scope patterns.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("scope", config)
        self.scope_patterns = self.config.get("scope_patterns", [])

    def is_applicable(self, session: Session) -> bool:
        """Only applicable if scope patterns are defined."""
        if not super().is_applicable(session):
            return False
        return len(self.scope_patterns) > 0

    async def validate(self, session: Session) -> ValidationResult:
        """Check if all changes are within allowed scope."""
        violations = []

        for file_change in session.file_changes:
            file_path = str(file_change.path)
            matches_scope = any(
                fnmatch(file_path, pattern) for pattern in self.scope_patterns
            )

            if not matches_scope:
                violations.append(
                    f"{file_path} is outside allowed scope: {self.scope_patterns}"
                )

        passed = len(violations) == 0
        return ValidationResult(
            validator_name=self.name,
            passed=passed,
            message="All changes within scope" if passed else "Scope violations detected",
            errors=violations,
            details={
                "scope_patterns": self.scope_patterns,
                "files_checked": len(session.file_changes),
            },
        )


class SecurityValidator(BaseValidator):
    """
    Scans for potential security issues.

    Detects hardcoded secrets, API keys, passwords, and other sensitive data.
    """

    # Patterns for detecting potential secrets
    SECRET_PATTERNS = [
        (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]([^'\"]+)['\"]", "API Key"),
        (r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Password"),
        (r"(?i)(secret|token)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Secret/Token"),
        (r"(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*['\"]([^'\"]+)['\"]", "AWS Access Key"),
        (r"(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*['\"]([^'\"]+)['\"]", "AWS Secret Key"),
        (r"-----BEGIN (RSA |DSA )?PRIVATE KEY-----", "Private Key"),
        (r"(?i)(bearer\s+[a-zA-Z0-9\-._~+/]+=*)", "Bearer Token"),
        (r"(?i)(sk-[a-zA-Z0-9]{32,})", "OpenAI API Key"),
    ]

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("security", config)
        self.fail_on_secrets = self.config.get("fail_on_secrets", False)

    async def validate(self, session: Session) -> ValidationResult:
        """Scan for potential security issues."""
        warnings = []

        for file_change in session.file_changes:
            if file_change.operation == "delete":
                continue
            if not file_change.new_content:
                continue

            for pattern, name in self.SECRET_PATTERNS:
                matches = re.finditer(pattern, file_change.new_content)
                for match in matches:
                    line_num = file_change.new_content[: match.start()].count("\n") + 1
                    warnings.append(
                        f"{file_change.path}:{line_num}: Potential {name} detected"
                    )

        # Security validator typically warns but doesn't fail
        # unless fail_on_secrets is True
        passed = len(warnings) == 0 or not self.fail_on_secrets

        return ValidationResult(
            validator_name=self.name,
            passed=passed,
            message=(
                "No security issues detected"
                if len(warnings) == 0
                else f"Found {len(warnings)} potential security issue(s)"
            ),
            warnings=warnings,
            errors=warnings if not passed else [],
            details={
                "files_scanned": sum(
                    1 for fc in session.file_changes if fc.operation != "delete"
                ),
                "patterns_checked": len(self.SECRET_PATTERNS),
            },
        )


class LintValidator(BaseValidator):
    """
    Runs linter (e.g., ruff, flake8) on changed files.

    Optional validator for code quality checks.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__("lint", config)
        self.lint_command = self.config.get("lint_command", "ruff check")
        self.timeout = self.config.get("timeout", 60)
        self.fail_on_errors = self.config.get("fail_on_errors", False)

    def is_applicable(self, session: Session) -> bool:
        """Only applicable if there are Python file changes."""
        if not super().is_applicable(session):
            return False
        return any(
            str(fc.path).endswith(".py") and fc.operation != "delete"
            for fc in session.file_changes
        )

    async def validate(self, session: Session) -> ValidationResult:
        """Run linter in the sandbox environment."""
        if not session.sandbox_path:
            return ValidationResult(
                validator_name=self.name,
                passed=True,
                message="No sandbox path available - skipped",
                details={"skipped": True},
            )

        try:
            process = await asyncio.create_subprocess_shell(
                self.lint_command,
                cwd=session.sandbox_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ValidationResult(
                    validator_name=self.name,
                    passed=not self.fail_on_errors,
                    message=f"Linter timed out after {self.timeout}s",
                    warnings=[f"Lint execution exceeded {self.timeout}s timeout"],
                )

            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""

            # Most linters return 0 on success, non-zero on issues
            has_issues = process.returncode != 0
            passed = not has_issues or not self.fail_on_errors

            issues = []
            if stdout_str:
                issues = stdout_str.strip().split("\n")

            return ValidationResult(
                validator_name=self.name,
                passed=passed,
                message=(
                    "No lint issues"
                    if not has_issues
                    else f"Found {len(issues)} lint issue(s)"
                ),
                warnings=issues if not self.fail_on_errors else [],
                errors=issues if self.fail_on_errors else [],
                details={
                    "command": self.lint_command,
                    "exit_code": process.returncode,
                    "output": stdout_str[:1000],
                },
            )

        except FileNotFoundError:
            return ValidationResult(
                validator_name=self.name,
                passed=True,
                message=f"Linter not found: {self.lint_command} - skipped",
                warnings=[f"Command '{self.lint_command}' not found in PATH"],
                details={"skipped": True},
            )
        except Exception as e:
            return ValidationResult(
                validator_name=self.name,
                passed=not self.fail_on_errors,
                message=f"Linter error: {str(e)}",
                warnings=[str(e)] if not self.fail_on_errors else [],
                errors=[str(e)] if self.fail_on_errors else [],
            )
