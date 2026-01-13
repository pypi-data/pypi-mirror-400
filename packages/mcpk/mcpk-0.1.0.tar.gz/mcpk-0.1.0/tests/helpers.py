"""MCPK testing utilities.

Provides mock facilities and helpers for testing MCPK-based applications.
"""

from __future__ import annotations

from typing import Any

from mcpk.errors import PermissionDeniedError
from mcpk.events import (
    Event,
    LogEvent,
    ProgressEvent,
    PromptGetEvent,
    ResourceReadEvent,
    ToolCallEvent,
)
from mcpk.hooks import PermissionHook, PermissionRequest
from mcpk.types import ExecutionScope

# =============================================================================
# Mock Event Collector
# =============================================================================


class MockEventCollector:
    """Collects events for testing.

    Use as an event handler to capture events during test execution.

    Example:
        collector = MockEventCollector()
        kernel = Kernel(event_handler=collector.handler)
        # ... execute tools ...
        assert len(collector.get_tool_calls()) == 1
    """

    def __init__(self) -> None:
        self.events: list[Event] = []

    def handler(self, event: Event) -> None:
        """Event handler that collects events."""
        self.events.append(event)

    async def async_handler(self, event: Event) -> None:
        """Async event handler that collects events."""
        self.events.append(event)

    def get_tool_calls(self) -> list[ToolCallEvent]:
        """Get all tool call events."""
        return [e for e in self.events if isinstance(e, ToolCallEvent)]

    def get_resource_reads(self) -> list[ResourceReadEvent]:
        """Get all resource read events."""
        return [e for e in self.events if isinstance(e, ResourceReadEvent)]

    def get_prompt_gets(self) -> list[PromptGetEvent]:
        """Get all prompt get events."""
        return [e for e in self.events if isinstance(e, PromptGetEvent)]

    def get_progress(self) -> list[ProgressEvent]:
        """Get all progress events."""
        return [e for e in self.events if isinstance(e, ProgressEvent)]

    def get_logs(self) -> list[LogEvent]:
        """Get all log events."""
        return [e for e in self.events if isinstance(e, LogEvent)]

    def clear(self) -> None:
        """Clear all collected events."""
        self.events.clear()


# =============================================================================
# Mock Scope Helper
# =============================================================================


class MockScope[ContextT]:
    """Helper for creating test execution scopes.

    Example:
        scope = MockScope.create(MyContext(user_id="123"))
        result = kernel.call_tool("my_tool", {}, scope)
    """

    @staticmethod
    def create(
        ctx: ContextT,
        request_id: str | None = None,
        progress_token: str | int | None = None,
        extensions: dict[str, Any] | None = None,
    ) -> ExecutionScope[ContextT]:
        """Create a test execution scope.

        Args:
            ctx: User-defined context
            request_id: Optional request correlation ID
            progress_token: Optional progress token
            extensions: Optional extensions dict

        Returns:
            ExecutionScope wrapping the user context
        """
        return ExecutionScope(
            ctx=ctx,
            request_id=request_id,
            progress_token=progress_token,
            extensions=extensions,
        )


# =============================================================================
# Permission Hook Helpers
# =============================================================================


def always_allow() -> PermissionHook[Any]:
    """Create a permission hook that allows everything.

    Returns:
        A permission hook function that never raises
    """

    def hook(scope: ExecutionScope[Any], req: PermissionRequest) -> None:
        pass

    return hook


def always_deny(reason: str = "denied") -> PermissionHook[Any]:
    """Create a permission hook that denies everything.

    Args:
        reason: Denial reason message

    Returns:
        A permission hook function that always raises PermissionDeniedError
    """

    def hook(scope: ExecutionScope[Any], req: PermissionRequest) -> None:
        raise PermissionDeniedError(reason)

    return hook


def deny_tools(*tool_names: str, reason: str = "denied") -> PermissionHook[Any]:
    """Create a permission hook that denies specific tools.

    Args:
        tool_names: Names of tools to deny
        reason: Denial reason message

    Returns:
        A permission hook function that denies specified tools
    """

    def hook(scope: ExecutionScope[Any], req: PermissionRequest) -> None:
        if req.kind == "tool" and req.name in tool_names:
            raise PermissionDeniedError(reason)

    return hook


def deny_resources(*uris: str, reason: str = "denied") -> PermissionHook[Any]:
    """Create a permission hook that denies specific resources.

    Args:
        uris: URIs of resources to deny
        reason: Denial reason message

    Returns:
        A permission hook function that denies specified resources
    """

    def hook(scope: ExecutionScope[Any], req: PermissionRequest) -> None:
        if req.kind == "resource" and req.name in uris:
            raise PermissionDeniedError(reason)

    return hook
