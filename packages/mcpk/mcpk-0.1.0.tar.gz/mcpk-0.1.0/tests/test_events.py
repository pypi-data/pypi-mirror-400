"""Tests for mcpk.events module."""

from __future__ import annotations

from typing import Any, Literal

import pytest

from mcpk.events import (
    LogEvent,
    LogLevel,
    ProgressEvent,
    PromptGetEvent,
    ResourceReadEvent,
    ToolCallEvent,
)
from mcpk.types import (
    ExecutionScope,
    PromptMessage,
    PromptResult,
    ResourceContent,
    ResourceResult,
    TextItem,
    ToolResult,
)

# =============================================================================
# ToolCallEvent Tests
# =============================================================================


@pytest.mark.parametrize(
    "phase",
    ["before", "after", "error"],
)
def test_tool_call_event_phases(phase: Literal["before", "after", "error"]) -> None:
    scope = ExecutionScope(ctx=None)
    event = ToolCallEvent(
        phase=phase,
        tool_name="my_tool",
        arguments={"x": 1},
        scope=scope,
    )

    assert event.phase == phase
    assert event.tool_name == "my_tool"
    assert event.arguments == {"x": 1}
    assert event.scope is scope


def test_tool_call_event_before_has_no_result() -> None:
    scope = ExecutionScope(ctx=None)
    event = ToolCallEvent(
        phase="before",
        tool_name="tool",
        arguments={},
        scope=scope,
    )

    assert event.result is None
    assert event.error is None


def test_tool_call_event_after_has_result() -> None:
    scope = ExecutionScope(ctx=None)
    result = ToolResult(content=(TextItem(text="done"),))
    event = ToolCallEvent(
        phase="after",
        tool_name="tool",
        arguments={},
        scope=scope,
        result=result,
    )

    assert event.result is result
    assert event.error is None


def test_tool_call_event_error_has_exception() -> None:
    scope = ExecutionScope(ctx=None)
    error = ValueError("something went wrong")
    event = ToolCallEvent(
        phase="error",
        tool_name="tool",
        arguments={},
        scope=scope,
        error=error,
    )

    assert event.result is None
    assert event.error is error


# =============================================================================
# ResourceReadEvent Tests
# =============================================================================


@pytest.mark.parametrize(
    "phase",
    ["before", "after", "error"],
)
def test_resource_read_event_phases(phase: Literal["before", "after", "error"]) -> None:
    scope = ExecutionScope(ctx=None)
    event = ResourceReadEvent(
        phase=phase,
        uri="file:///test",
        scope=scope,
    )

    assert event.phase == phase
    assert event.uri == "file:///test"
    assert event.scope is scope


def test_resource_read_event_after_has_result() -> None:
    scope = ExecutionScope(ctx=None)
    result = ResourceResult(contents=(ResourceContent(uri="file:///test", text="content"),))
    event = ResourceReadEvent(
        phase="after",
        uri="file:///test",
        scope=scope,
        result=result,
    )

    assert event.result is result


def test_resource_read_event_error_has_exception() -> None:
    scope = ExecutionScope(ctx=None)
    error = OSError("file not found")
    event = ResourceReadEvent(
        phase="error",
        uri="file:///test",
        scope=scope,
        error=error,
    )

    assert event.error is error


# =============================================================================
# PromptGetEvent Tests
# =============================================================================


@pytest.mark.parametrize(
    "phase",
    ["before", "after", "error"],
)
def test_prompt_get_event_phases(phase: Literal["before", "after", "error"]) -> None:
    scope = ExecutionScope(ctx=None)
    event = PromptGetEvent(
        phase=phase,
        prompt_name="greeting",
        arguments={"name": "Alice"},
        scope=scope,
    )

    assert event.phase == phase
    assert event.prompt_name == "greeting"
    assert event.arguments == {"name": "Alice"}
    assert event.scope is scope


def test_prompt_get_event_after_has_result() -> None:
    scope = ExecutionScope(ctx=None)
    result = PromptResult(messages=(PromptMessage(role="user", content=TextItem(text="Hello")),))
    event = PromptGetEvent(
        phase="after",
        prompt_name="greeting",
        arguments={},
        scope=scope,
        result=result,
    )

    assert event.result is result


# =============================================================================
# ProgressEvent Tests
# =============================================================================


@pytest.mark.parametrize(
    ("progress_token", "progress", "total", "message"),
    [
        ("token-1", 0.0, None, None),
        ("token-2", 50.0, 100.0, "Half done"),
        (123, 75.5, 100.0, "Almost there"),
        ("t", 100.0, 100.0, "Complete"),
    ],
)
def test_progress_event(
    progress_token: str | int,
    progress: float,
    total: float | None,
    message: str | None,
) -> None:
    event = ProgressEvent(
        progress_token=progress_token,
        progress=progress,
        total=total,
        message=message,
    )

    assert event.progress_token == progress_token
    assert event.progress == progress
    assert event.total == total
    assert event.message == message


def test_progress_event_defaults() -> None:
    event = ProgressEvent(progress_token="t", progress=10.0)

    assert event.total is None
    assert event.message is None


# =============================================================================
# LogEvent Tests
# =============================================================================


@pytest.mark.parametrize(
    "level",
    ["debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"],
)
def test_log_event_levels(level: LogLevel) -> None:
    event = LogEvent(level=level, data="test message")

    assert event.level == level
    assert event.data == "test message"


@pytest.mark.parametrize(
    ("data", "logger"),
    [
        ("string message", None),
        ({"key": "value"}, "my.logger"),
        ([1, 2, 3], "array.logger"),
        (None, None),
    ],
)
def test_log_event_data_types(data: Any, logger: str | None) -> None:
    event = LogEvent(level="info", data=data, logger=logger)

    assert event.data == data
    assert event.logger == logger


# =============================================================================
# Event Union Type Tests
# =============================================================================


def test_event_types_are_distinct() -> None:
    """Events should be distinguishable by type."""
    scope = ExecutionScope(ctx=None)

    tool_event = ToolCallEvent(phase="before", tool_name="t", arguments={}, scope=scope)
    resource_event = ResourceReadEvent(phase="before", uri="u", scope=scope)
    prompt_event = PromptGetEvent(phase="before", prompt_name="p", arguments={}, scope=scope)
    progress_event = ProgressEvent(progress_token="t", progress=0)
    log_event = LogEvent(level="info", data="msg")

    assert isinstance(tool_event, ToolCallEvent)
    assert isinstance(resource_event, ResourceReadEvent)
    assert isinstance(prompt_event, PromptGetEvent)
    assert isinstance(progress_event, ProgressEvent)
    assert isinstance(log_event, LogEvent)

    # Type checking - these should all be Event
    from mcpk.events import Event

    events: list[Event] = [
        tool_event,
        resource_event,
        prompt_event,
        progress_event,
        log_event,
    ]
    assert len(events) == 5
