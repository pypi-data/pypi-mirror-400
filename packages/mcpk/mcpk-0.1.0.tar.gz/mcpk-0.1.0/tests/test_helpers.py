"""Tests for tests.helpers module."""

from __future__ import annotations

from typing import Any

import pytest
from helpers import (
    MockEventCollector,
    MockScope,
    always_allow,
    always_deny,
    deny_resources,
    deny_tools,
)

from mcpk.errors import PermissionDeniedError
from mcpk.events import (
    LogEvent,
    ProgressEvent,
    PromptGetEvent,
    ResourceReadEvent,
    ToolCallEvent,
)
from mcpk.hooks import PermissionRequest
from mcpk.types import (
    ExecutionScope,
)

# =============================================================================
# MockEventCollector Tests
# =============================================================================


def test_mock_event_collector_collects_events() -> None:
    collector = MockEventCollector()
    scope = ExecutionScope(ctx=None)

    event1 = ToolCallEvent(phase="before", tool_name="t", arguments={}, scope=scope)
    event2 = LogEvent(level="info", data="test")

    collector.handler(event1)
    collector.handler(event2)

    assert len(collector.events) == 2
    assert collector.events[0] is event1
    assert collector.events[1] is event2


async def test_mock_event_collector_async_handler() -> None:
    collector = MockEventCollector()
    event = ProgressEvent(progress_token="t", progress=50.0)

    await collector.async_handler(event)

    assert len(collector.events) == 1
    assert collector.events[0] is event


def test_mock_event_collector_get_tool_calls() -> None:
    collector = MockEventCollector()
    scope = ExecutionScope(ctx=None)

    tool_event = ToolCallEvent(phase="before", tool_name="tool", arguments={}, scope=scope)
    log_event = LogEvent(level="info", data="log")
    resource_event = ResourceReadEvent(phase="before", uri="uri", scope=scope)

    collector.handler(tool_event)
    collector.handler(log_event)
    collector.handler(resource_event)

    tool_calls = collector.get_tool_calls()
    assert len(tool_calls) == 1
    assert tool_calls[0] is tool_event


def test_mock_event_collector_get_resource_reads() -> None:
    collector = MockEventCollector()
    scope = ExecutionScope(ctx=None)

    resource_event = ResourceReadEvent(phase="after", uri="file:///test", scope=scope)
    tool_event = ToolCallEvent(phase="before", tool_name="tool", arguments={}, scope=scope)

    collector.handler(resource_event)
    collector.handler(tool_event)

    reads = collector.get_resource_reads()
    assert len(reads) == 1
    assert reads[0] is resource_event


def test_mock_event_collector_get_prompt_gets() -> None:
    collector = MockEventCollector()
    scope = ExecutionScope(ctx=None)

    prompt_event = PromptGetEvent(phase="before", prompt_name="greeting", arguments={}, scope=scope)

    collector.handler(prompt_event)

    prompts = collector.get_prompt_gets()
    assert len(prompts) == 1
    assert prompts[0] is prompt_event


def test_mock_event_collector_get_progress() -> None:
    collector = MockEventCollector()

    progress_event = ProgressEvent(progress_token="token", progress=25.0)

    collector.handler(progress_event)

    progress = collector.get_progress()
    assert len(progress) == 1
    assert progress[0] is progress_event


def test_mock_event_collector_get_logs() -> None:
    collector = MockEventCollector()

    log_event = LogEvent(level="warning", data={"msg": "test"})

    collector.handler(log_event)

    logs = collector.get_logs()
    assert len(logs) == 1
    assert logs[0] is log_event


def test_mock_event_collector_clear() -> None:
    collector = MockEventCollector()

    collector.handler(LogEvent(level="info", data="test"))
    assert len(collector.events) == 1

    collector.clear()
    assert len(collector.events) == 0


def test_mock_event_collector_multiple_of_same_type() -> None:
    collector = MockEventCollector()
    scope = ExecutionScope(ctx=None)

    collector.handler(ToolCallEvent(phase="before", tool_name="a", arguments={}, scope=scope))
    collector.handler(ToolCallEvent(phase="after", tool_name="a", arguments={}, scope=scope))
    collector.handler(ToolCallEvent(phase="before", tool_name="b", arguments={}, scope=scope))

    tool_calls = collector.get_tool_calls()
    assert len(tool_calls) == 3


# =============================================================================
# MockScope Tests
# =============================================================================


def test_mock_scope_create_minimal() -> None:
    ctx = {"user": "alice"}
    scope = MockScope.create(ctx)

    assert scope.ctx == ctx
    assert scope.request_id is None
    assert scope.progress_token is None
    assert scope.extensions is None


@pytest.mark.parametrize(
    ("ctx", "request_id", "progress_token", "extensions"),
    [
        (None, "req-1", "prog-1", None),
        ({"key": "value"}, "req-2", 123, {"ext": "data"}),
        ("string_ctx", None, "token", {}),
    ],
)
def test_mock_scope_create_with_options(
    ctx: Any,
    request_id: str | None,
    progress_token: str | int | None,
    extensions: dict[str, Any] | None,
) -> None:
    scope = MockScope.create(
        ctx,
        request_id=request_id,
        progress_token=progress_token,
        extensions=extensions,
    )

    assert scope.ctx == ctx
    assert scope.request_id == request_id
    assert scope.progress_token == progress_token
    assert scope.extensions == extensions


def test_mock_scope_returns_execution_scope() -> None:
    scope = MockScope.create("test")

    assert isinstance(scope, ExecutionScope)


# =============================================================================
# Permission Hook Helper Tests
# =============================================================================


def test_always_allow_does_not_raise() -> None:
    hook = always_allow()
    scope = ExecutionScope(ctx=None)
    req = PermissionRequest(kind="tool", name="test")

    hook(scope, req)  # Should not raise


@pytest.mark.parametrize(
    ("kind", "name"),
    [
        ("tool", "any_tool"),
        ("resource", "any://uri"),
        ("prompt", "any_prompt"),
    ],
)
def test_always_allow_allows_all_kinds(kind: str, name: str) -> None:
    hook = always_allow()
    scope = ExecutionScope(ctx=None)
    req = PermissionRequest(kind=kind, name=name)  # type: ignore[arg-type]

    hook(scope, req)  # Should not raise


def test_always_deny_raises() -> None:
    hook = always_deny()
    scope = ExecutionScope(ctx=None)
    req = PermissionRequest(kind="tool", name="test")

    with pytest.raises(PermissionDeniedError) as exc_info:
        hook(scope, req)

    assert exc_info.value.reason == "denied"


def test_always_deny_custom_reason() -> None:
    hook = always_deny(reason="custom reason")
    scope = ExecutionScope(ctx=None)
    req = PermissionRequest(kind="tool", name="test")

    with pytest.raises(PermissionDeniedError) as exc_info:
        hook(scope, req)

    assert exc_info.value.reason == "custom reason"


@pytest.mark.parametrize(
    ("kind", "name"),
    [
        ("tool", "any_tool"),
        ("resource", "any://uri"),
        ("prompt", "any_prompt"),
    ],
)
def test_always_deny_denies_all_kinds(kind: str, name: str) -> None:
    hook = always_deny()
    scope = ExecutionScope(ctx=None)
    req = PermissionRequest(kind=kind, name=name)  # type: ignore[arg-type]

    with pytest.raises(PermissionDeniedError):
        hook(scope, req)


def test_deny_tools_denies_specified_tools() -> None:
    hook = deny_tools("dangerous_tool", "another_bad_tool")
    scope = ExecutionScope(ctx=None)

    # These should raise
    with pytest.raises(PermissionDeniedError):
        hook(scope, PermissionRequest(kind="tool", name="dangerous_tool"))

    with pytest.raises(PermissionDeniedError):
        hook(scope, PermissionRequest(kind="tool", name="another_bad_tool"))


def test_deny_tools_allows_other_tools() -> None:
    hook = deny_tools("bad_tool")
    scope = ExecutionScope(ctx=None)

    # This should not raise
    hook(scope, PermissionRequest(kind="tool", name="good_tool"))


def test_deny_tools_allows_resources_and_prompts() -> None:
    hook = deny_tools("tool_name")
    scope = ExecutionScope(ctx=None)

    # Resources and prompts should be allowed even if name matches
    hook(scope, PermissionRequest(kind="resource", name="tool_name"))
    hook(scope, PermissionRequest(kind="prompt", name="tool_name"))


def test_deny_tools_custom_reason() -> None:
    hook = deny_tools("blocked", reason="tool is blocked")
    scope = ExecutionScope(ctx=None)

    with pytest.raises(PermissionDeniedError) as exc_info:
        hook(scope, PermissionRequest(kind="tool", name="blocked"))

    assert exc_info.value.reason == "tool is blocked"


def test_deny_resources_denies_specified_uris() -> None:
    hook = deny_resources("file:///secret", "http://internal/api")
    scope = ExecutionScope(ctx=None)

    with pytest.raises(PermissionDeniedError):
        hook(scope, PermissionRequest(kind="resource", name="file:///secret"))

    with pytest.raises(PermissionDeniedError):
        hook(scope, PermissionRequest(kind="resource", name="http://internal/api"))


def test_deny_resources_allows_other_uris() -> None:
    hook = deny_resources("file:///secret")
    scope = ExecutionScope(ctx=None)

    # This should not raise
    hook(scope, PermissionRequest(kind="resource", name="file:///public"))


def test_deny_resources_allows_tools_and_prompts() -> None:
    hook = deny_resources("file:///secret")
    scope = ExecutionScope(ctx=None)

    # Tools and prompts should be allowed even if name matches
    hook(scope, PermissionRequest(kind="tool", name="file:///secret"))
    hook(scope, PermissionRequest(kind="prompt", name="file:///secret"))


def test_deny_resources_custom_reason() -> None:
    hook = deny_resources("restricted://", reason="access restricted")
    scope = ExecutionScope(ctx=None)

    with pytest.raises(PermissionDeniedError) as exc_info:
        hook(scope, PermissionRequest(kind="resource", name="restricted://"))

    assert exc_info.value.reason == "access restricted"
