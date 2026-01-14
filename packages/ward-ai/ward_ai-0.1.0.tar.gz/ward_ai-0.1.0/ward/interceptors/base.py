"""Base interceptor classes for AI Sandbox Orchestrator."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from ..core.session import Session


@dataclass
class InterceptResult:
    """Result of intercepting a tool call."""
    
    allowed: bool
    executed_in_sandbox: bool = False
    result: Any = None
    error: Optional[str] = None
    feedback: Optional[dict[str, Any]] = None
    modified_args: Optional[dict[str, Any]] = None
    
    @property
    def success(self) -> bool:
        """Check if interception was successful."""
        return self.allowed and self.error is None


class BaseInterceptor(ABC):
    """
    Abstract base class for all interceptors.
    
    Interceptors are responsible for:
    1. Analyzing tool calls before execution
    2. Modifying arguments if needed (path translation, etc.)
    3. Deciding whether to allow, block, or redirect execution
    4. Providing feedback to the AI about the interception
    
    Examples:
        - FilesystemInterceptor: Redirects file writes to sandbox
        - BashInterceptor: Validates and sandboxes command execution
        - NetworkInterceptor: Blocks or logs network requests
    """
    
    def __init__(self, name: str, config: dict[str, Any] | None = None):
        """
        Initialize the interceptor.
        
        Args:
            name: Human-readable name for this interceptor
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
    
    @abstractmethod
    async def intercept(
        self,
        session: Session,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> InterceptResult:
        """
        Intercept a tool call and decide how to handle it.
        
        Args:
            session: Current session context
            tool_name: Name of the tool being called
            arguments: Arguments passed to the tool
            
        Returns:
            InterceptResult with decision and any modifications
        """
        pass
    
    def is_applicable(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        """
        Check if this interceptor should handle the given tool call.
        
        Override this method to filter which tool calls this interceptor handles.
        
        Args:
            tool_name: Name of the tool being called
            arguments: Arguments passed to the tool
            
        Returns:
            True if this interceptor should handle the call
        """
        return self.enabled
    
    def get_feedback_message(self, result: InterceptResult) -> str:
        """
        Generate feedback message for the AI based on interception result.
        
        Args:
            result: The interception result
            
        Returns:
            Human-readable feedback message
        """
        if not result.allowed:
            return f"❌ {self.name}: Operation blocked - {result.error}"
        
        if result.executed_in_sandbox:
            return f"✅ {self.name}: Operation executed in sandbox"
        
        return f"✅ {self.name}: Operation allowed"


class InterceptorRegistry:
    """Registry for managing multiple interceptors."""
    
    def __init__(self):
        self.interceptors: list[BaseInterceptor] = []
    
    def register(self, interceptor: BaseInterceptor) -> None:
        """Register a new interceptor."""
        self.interceptors.append(interceptor)
    
    def unregister(self, interceptor_name: str) -> bool:
        """Unregister an interceptor by name."""
        for i, interceptor in enumerate(self.interceptors):
            if interceptor.name == interceptor_name:
                del self.interceptors[i]
                return True
        return False
    
    async def intercept_tool_call(
        self,
        session: Session,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> InterceptResult:
        """
        Run tool call through all applicable interceptors.
        
        Args:
            session: Current session context
            tool_name: Name of the tool being called
            arguments: Arguments passed to the tool
            
        Returns:
            Combined result from all interceptors
        """
        # Find applicable interceptors
        applicable_interceptors = [
            interceptor for interceptor in self.interceptors
            if interceptor.is_applicable(tool_name, arguments)
        ]
        
        if not applicable_interceptors:
            # No interceptors apply, allow by default
            return InterceptResult(allowed=True, result=arguments)
        
        # Run through interceptors in order
        current_args = arguments.copy()
        feedback_messages = []
        
        for interceptor in applicable_interceptors:
            result = await interceptor.intercept(session, tool_name, current_args)
            
            # If any interceptor blocks, stop processing
            if not result.allowed:
                return result
            
            # Update arguments if interceptor modified them
            if result.modified_args:
                current_args.update(result.modified_args)
            
            # Collect feedback
            feedback_msg = interceptor.get_feedback_message(result)
            if feedback_msg:
                feedback_messages.append(feedback_msg)
        
        # All interceptors passed
        return InterceptResult(
            allowed=True,
            executed_in_sandbox=any(
                getattr(result, 'executed_in_sandbox', False)
                for result in [
                    await interceptor.intercept(session, tool_name, current_args)
                    for interceptor in applicable_interceptors
                ]
            ),
            result=current_args,
            feedback={
                "messages": feedback_messages,
                "interceptors_applied": [i.name for i in applicable_interceptors],
            },
        )