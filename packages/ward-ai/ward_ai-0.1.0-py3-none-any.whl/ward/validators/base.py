"""Base validator classes for AI Sandbox Orchestrator."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..core.session import FileChange, Session, ValidationResult


class BaseValidator(ABC):
    """
    Abstract base class for all validators.

    Validators are responsible for checking specific aspects of code changes
    before they are promoted from sandbox to main codebase.

    Examples:
        - SyntaxValidator: Check for syntax errors
        - TestValidator: Run test suite
        - SecurityValidator: Scan for security issues
        - ScopeValidator: Ensure changes are within allowed scope
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        """
        Initialize the validator.

        Args:
            name: Human-readable name for this validator
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

    @abstractmethod
    async def validate(self, session: Session) -> ValidationResult:
        """
        Validate the session changes.

        Args:
            session: The session to validate

        Returns:
            ValidationResult with passed/failed status and details
        """
        pass

    def is_applicable(self, session: Session) -> bool:
        """
        Check if this validator should run for the given session.

        Override this method to skip validation based on session properties.
        For example, TestValidator might skip if no test files exist.

        Args:
            session: The session to check

        Returns:
            True if validator should run, False to skip
        """
        return self.enabled

    async def run(self, session: Session) -> ValidationResult:
        """
        Execute the validation with applicability check.

        This is the main entry point that should be called by the orchestrator.
        It wraps the validate() method with enable/applicability checks.

        Args:
            session: The session to validate

        Returns:
            ValidationResult
        """
        if not self.enabled:
            return ValidationResult(
                validator_name=self.name,
                passed=True,
                message=f"{self.name} disabled - skipped",
                details={"skipped": True, "reason": "disabled"},
            )

        if not self.is_applicable(session):
            return ValidationResult(
                validator_name=self.name,
                passed=True,
                message=f"{self.name} not applicable - skipped",
                details={"skipped": True, "reason": "not_applicable"},
            )

        return await self.validate(session)


class ValidatorRegistry:
    """
    Registry for managing and running validators.

    Validators are registered in order and run sequentially.
    """

    def __init__(self):
        self._validators: list[BaseValidator] = []

    def register(self, validator: BaseValidator) -> None:
        """Register a validator."""
        self._validators.append(validator)

    def unregister(self, validator_name: str) -> bool:
        """Unregister a validator by name."""
        for i, v in enumerate(self._validators):
            if v.name == validator_name:
                self._validators.pop(i)
                return True
        return False

    def get_validator(self, name: str) -> BaseValidator | None:
        """Get a validator by name."""
        for v in self._validators:
            if v.name == name:
                return v
        return None

    def clear(self) -> None:
        """Remove all validators."""
        self._validators.clear()

    async def validate_all(self, session: Session) -> list[ValidationResult]:
        """
        Run all registered validators on a session.

        Args:
            session: The session to validate

        Returns:
            List of ValidationResult from all validators
        """
        results = []
        for validator in self._validators:
            result = await validator.run(session)
            results.append(result)
        return results

    @property
    def validators(self) -> list[BaseValidator]:
        """Get list of registered validators."""
        return self._validators.copy()
