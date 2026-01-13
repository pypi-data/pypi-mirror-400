"""MCPK event types and handlers.

Events are emitted during tool/resource/prompt execution for observability.
Adapters can use events to forward notifications to transports.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from mcpk.types import ExecutionScope, PromptResult, ResourceResult, ToolResult


LogLevel = Literal[
    "debug",
    "info",
    "notice",
    "warning",
    "error",
    "critical",
    "alert",
    "emergency",
]


type Phase = Literal["before", "after", "error"]


@dataclass(frozen=True, slots=True)
class ToolCallEvent:
    """Emitted before/after tool execution.

    Attributes:
        phase: "before", "after", or "error"
        tool_name: Name of the tool being called
        arguments: Arguments passed to the tool
        scope: Execution scope
        result: Tool result (only for "after" phase)
        error: Exception (only for "error" phase)
    """

    phase: Phase
    tool_name: str
    arguments: dict[str, Any]
    scope: ExecutionScope[Any]
    result: ToolResult | None = None
    error: Exception | None = None


@dataclass(frozen=True, slots=True)
class ResourceReadEvent:
    """Emitted before/after resource read.

    Attributes:
        phase: "before", "after", or "error"
        uri: Resource URI being read
        scope: Execution scope
        result: Resource result (only for "after" phase)
        error: Exception (only for "error" phase)
    """

    phase: Phase
    uri: str
    scope: ExecutionScope[Any]
    result: ResourceResult | None = None
    error: Exception | None = None


@dataclass(frozen=True, slots=True)
class PromptGetEvent:
    """Emitted before/after prompt get.

    Attributes:
        phase: "before", "after", or "error"
        prompt_name: Name of the prompt being retrieved
        arguments: Arguments for prompt templating
        scope: Execution scope
        result: Prompt result (only for "after" phase)
        error: Exception (only for "error" phase)
    """

    phase: Phase
    prompt_name: str
    arguments: dict[str, str]
    scope: ExecutionScope[Any]
    result: PromptResult | None = None
    error: Exception | None = None


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    """Progress notification to be forwarded to transport.

    Attributes:
        progress_token: Token for correlating progress with request
        progress: Current progress value
        total: Optional total for calculating percentage
        message: Optional human-readable progress message
    """

    progress_token: str | int
    progress: float
    total: float | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class LogEvent:
    """Log notification to be forwarded to transport.

    Attributes:
        level: Log severity level
        data: Log data (any JSON-serializable value)
        logger: Optional logger name
    """

    level: LogLevel
    data: Any
    logger: str | None = None


Event = ToolCallEvent | ResourceReadEvent | PromptGetEvent | ProgressEvent | LogEvent
EventHandler = Callable[[Event], None]
AsyncEventHandler = Callable[[Event], Awaitable[None]]
