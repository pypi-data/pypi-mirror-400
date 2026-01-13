"""Tests for mcpk.kernel module."""

from __future__ import annotations

from typing import Any

import pytest

from mcpk.errors import (
    ExecutionError,
    PermissionDeniedError,
    PromptNotFoundError,
    ResourceNotFoundError,
    ToolNotFoundError,
    ValidationError,
)
from mcpk.events import (
    Event,
    LogEvent,
    ProgressEvent,
    PromptGetEvent,
    ResourceReadEvent,
    ToolCallEvent,
)
from mcpk.hooks import PermissionRequest
from mcpk.kernel import AsyncKernel, Kernel
from mcpk.types import (
    ExecutionScope,
    PromptDef,
    PromptMessage,
    PromptResult,
    ResourceContent,
    ResourceDef,
    ResourceResult,
    TextItem,
    ToolDef,
    ToolResult,
)

# =============================================================================
# Fixtures and Helpers
# =============================================================================


def make_scope(ctx: Any = None) -> ExecutionScope[Any]:
    return ExecutionScope(ctx=ctx)


def make_scope_with_progress(ctx: Any = None) -> ExecutionScope[Any]:
    return ExecutionScope(ctx=ctx, progress_token="test-token")


# =============================================================================
# Kernel Tool Tests
# =============================================================================


def test_kernel_register_and_call_tool() -> None:
    kernel: Kernel[None] = Kernel()
    tool_def = ToolDef(name="echo", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text=f"echo: {args.get('msg', '')}"),))

    kernel.register_tool(tool_def, handler)
    result = kernel.call_tool("echo", {"msg": "hello"}, make_scope())

    assert len(result.content) == 1
    assert isinstance(result.content[0], TextItem)
    assert result.content[0].text == "echo: hello"


def test_kernel_call_tool_not_found() -> None:
    kernel: Kernel[None] = Kernel()

    with pytest.raises(ToolNotFoundError) as exc_info:
        kernel.call_tool("nonexistent", {}, make_scope())

    assert exc_info.value.name == "nonexistent"


def test_kernel_tool_handler_exception_wrapped() -> None:
    kernel: Kernel[None] = Kernel()
    tool_def = ToolDef(name="failing", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        raise ValueError("something broke")

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        kernel.call_tool("failing", {}, make_scope())

    assert "failing" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_kernel_all_tools() -> None:
    kernel: Kernel[None] = Kernel()
    tool1 = ToolDef(name="tool_b", input_schema={"type": "object"})
    tool2 = ToolDef(name="tool_a", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=())

    kernel.register_tool(tool1, handler)
    kernel.register_tool(tool2, handler)

    tools = kernel.all_tools()
    assert len(tools) == 2
    assert tools[0].name == "tool_a"
    assert tools[1].name == "tool_b"


# =============================================================================
# Kernel Resource Tests
# =============================================================================


def test_kernel_register_and_read_resource() -> None:
    kernel: Kernel[None] = Kernel()
    resource_def = ResourceDef(uri="file:///test", name="Test")

    def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        return ResourceResult(contents=(ResourceContent(uri=uri, text="content"),))

    kernel.register_resource(resource_def, handler)
    result = kernel.read_resource("file:///test", make_scope())

    assert len(result.contents) == 1
    assert result.contents[0].text == "content"


def test_kernel_read_resource_not_found() -> None:
    kernel: Kernel[None] = Kernel()

    with pytest.raises(ResourceNotFoundError) as exc_info:
        kernel.read_resource("file:///nonexistent", make_scope())

    assert exc_info.value.uri == "file:///nonexistent"


def test_kernel_all_resources() -> None:
    kernel: Kernel[None] = Kernel()
    res1 = ResourceDef(uri="z://last", name="Last")
    res2 = ResourceDef(uri="a://first", name="First")

    def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        return ResourceResult(contents=())

    kernel.register_resource(res1, handler)
    kernel.register_resource(res2, handler)

    resources = kernel.all_resources()
    assert len(resources) == 2
    assert resources[0].uri == "a://first"


# =============================================================================
# Kernel Prompt Tests
# =============================================================================


def test_kernel_register_and_get_prompt() -> None:
    kernel: Kernel[None] = Kernel()
    prompt_def = PromptDef(name="greeting")

    def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        name = args.get("name", "World")
        return PromptResult(
            messages=(PromptMessage(role="user", content=TextItem(text=f"Hello, {name}!")),)
        )

    kernel.register_prompt(prompt_def, handler)
    result = kernel.get_prompt("greeting", {"name": "Alice"}, make_scope())

    assert len(result.messages) == 1
    assert result.messages[0].content.text == "Hello, Alice!"  # type: ignore[union-attr]


def test_kernel_get_prompt_not_found() -> None:
    kernel: Kernel[None] = Kernel()

    with pytest.raises(PromptNotFoundError) as exc_info:
        kernel.get_prompt("nonexistent", {}, make_scope())

    assert exc_info.value.name == "nonexistent"


def test_kernel_all_prompts() -> None:
    kernel: Kernel[None] = Kernel()
    prompt1 = PromptDef(name="zebra")
    prompt2 = PromptDef(name="alpha")

    def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        return PromptResult(messages=())

    kernel.register_prompt(prompt1, handler)
    kernel.register_prompt(prompt2, handler)

    prompts = kernel.all_prompts()
    assert len(prompts) == 2
    assert prompts[0].name == "alpha"


# =============================================================================
# Kernel Permission Hook Tests
# =============================================================================


def test_kernel_permission_hook_allows() -> None:
    def allow_hook(scope: ExecutionScope[None], req: PermissionRequest) -> None:
        pass

    kernel: Kernel[None] = Kernel(permission_hook=allow_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    kernel.register_tool(tool_def, handler)
    result = kernel.call_tool("tool", {}, make_scope())

    assert result.content[0].text == "ok"  # type: ignore[union-attr]


def test_kernel_permission_hook_denies() -> None:
    def deny_hook(scope: ExecutionScope[None], req: PermissionRequest) -> None:
        raise PermissionDeniedError("not allowed")

    kernel: Kernel[None] = Kernel(permission_hook=deny_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=())

    kernel.register_tool(tool_def, handler)

    with pytest.raises(PermissionDeniedError):
        kernel.call_tool("tool", {}, make_scope())


@pytest.mark.parametrize(
    ("kind", "operation"),
    [
        ("tool", "call_tool"),
        ("resource", "read_resource"),
        ("prompt", "get_prompt"),
    ],
)
def test_kernel_permission_hook_receives_correct_kind(kind: str, operation: str) -> None:
    received_requests: list[PermissionRequest] = []

    def hook(scope: ExecutionScope[None], req: PermissionRequest) -> None:
        received_requests.append(req)

    kernel: Kernel[None] = Kernel(permission_hook=hook)

    tool_def = ToolDef(name="test_tool", input_schema={"type": "object"})
    resource_def = ResourceDef(uri="test://uri", name="Test")
    prompt_def = PromptDef(name="test_prompt")

    def tool_handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    def resource_handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        return ResourceResult(contents=(ResourceContent(uri=uri, text="content"),))

    def prompt_handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        return PromptResult(messages=(PromptMessage(role="user", content=TextItem(text="hi")),))

    kernel.register_tool(tool_def, tool_handler)
    kernel.register_resource(resource_def, resource_handler)
    kernel.register_prompt(prompt_def, prompt_handler)

    if operation == "call_tool":
        kernel.call_tool("test_tool", {}, make_scope())
    elif operation == "read_resource":
        kernel.read_resource("test://uri", make_scope())
    else:
        kernel.get_prompt("test_prompt", {}, make_scope())

    assert len(received_requests) == 1
    assert received_requests[0].kind == kind


# =============================================================================
# Kernel Validation Hook Tests
# =============================================================================


def test_kernel_validation_hook_passes() -> None:
    def validation_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        pass

    kernel: Kernel[None] = Kernel(validation_hook=validation_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    kernel.register_tool(tool_def, handler)
    result = kernel.call_tool("tool", {}, make_scope())

    assert result.content[0].text == "ok"  # type: ignore[union-attr]


def test_kernel_validation_hook_fails() -> None:
    def validation_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        raise ValidationError("invalid input")

    kernel: Kernel[None] = Kernel(validation_hook=validation_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=())

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ValidationError):
        kernel.call_tool("tool", {}, make_scope())


def test_kernel_validation_hook_non_validation_error_wrapped() -> None:
    def validation_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        raise ValueError("schema mismatch")

    kernel: Kernel[None] = Kernel(validation_hook=validation_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=())

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ValidationError) as exc_info:
        kernel.call_tool("tool", {}, make_scope())

    assert "schema mismatch" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, ValueError)


# =============================================================================
# Kernel Event Handler Tests
# =============================================================================


def test_kernel_event_handler_receives_tool_events() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    def tool_handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="done"),))

    kernel.register_tool(tool_def, tool_handler)
    kernel.call_tool("tool", {"x": 1}, make_scope())

    assert len(events) == 2
    assert isinstance(events[0], ToolCallEvent)
    assert events[0].phase == "before"
    assert events[0].tool_name == "tool"
    assert events[0].arguments == {"x": 1}
    assert isinstance(events[1], ToolCallEvent)
    assert events[1].phase == "after"
    assert events[1].result is not None


def test_kernel_event_handler_receives_error_event() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    tool_def = ToolDef(name="failing", input_schema={"type": "object"})

    def tool_handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        raise RuntimeError("oops")

    kernel.register_tool(tool_def, tool_handler)

    with pytest.raises(ExecutionError):
        kernel.call_tool("failing", {}, make_scope())

    assert len(events) == 2
    assert events[0].phase == "before"  # type: ignore[union-attr]
    assert events[1].phase == "error"  # type: ignore[union-attr]
    assert events[1].error is not None  # type: ignore[union-attr]


# =============================================================================
# Kernel Emit Progress Tests
# =============================================================================


def test_kernel_emit_progress_with_token() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    scope = make_scope_with_progress()

    kernel.emit_progress(scope, 50.0, total=100.0, message="Halfway")

    assert len(events) == 1
    assert isinstance(events[0], ProgressEvent)
    assert events[0].progress_token == "test-token"
    assert events[0].progress == 50.0
    assert events[0].total == 100.0
    assert events[0].message == "Halfway"


def test_kernel_emit_progress_without_token_does_nothing() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    scope = make_scope()  # No progress token

    kernel.emit_progress(scope, 50.0)

    assert len(events) == 0


def test_kernel_emit_progress_without_handler_does_nothing() -> None:
    kernel: Kernel[None] = Kernel()  # No event handler
    scope = make_scope_with_progress()

    kernel.emit_progress(scope, 50.0)  # Should not raise


# =============================================================================
# Kernel Emit Log Tests
# =============================================================================


@pytest.mark.parametrize(
    "level",
    ["debug", "info", "warning", "error"],
)
def test_kernel_emit_log(level: str) -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)

    kernel.emit_log(level, {"message": "test"}, logger="test.logger")  # type: ignore[arg-type]

    assert len(events) == 1
    assert isinstance(events[0], LogEvent)
    assert events[0].level == level
    assert events[0].data == {"message": "test"}
    assert events[0].logger == "test.logger"


def test_kernel_emit_log_without_handler_does_nothing() -> None:
    kernel: Kernel[None] = Kernel()  # No event handler

    kernel.emit_log("info", "test")  # Should not raise


# =============================================================================
# AsyncKernel Tests
# =============================================================================


async def test_async_kernel_call_tool() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    tool_def = ToolDef(name="async_tool", input_schema={"type": "object"})

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="async result"),))

    kernel.register_tool(tool_def, handler)
    result = await kernel.call_tool("async_tool", {}, make_scope())

    assert result.content[0].text == "async result"  # type: ignore[union-attr]


async def test_async_kernel_call_tool_not_found() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()

    with pytest.raises(ToolNotFoundError):
        await kernel.call_tool("nonexistent", {}, make_scope())


async def test_async_kernel_read_resource() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    resource_def = ResourceDef(uri="async://resource", name="Async")

    async def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        return ResourceResult(contents=(ResourceContent(uri=uri, text="async content"),))

    kernel.register_resource(resource_def, handler)
    result = await kernel.read_resource("async://resource", make_scope())

    assert result.contents[0].text == "async content"


async def test_async_kernel_get_prompt() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    prompt_def = PromptDef(name="async_prompt")

    async def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        return PromptResult(messages=(PromptMessage(role="user", content=TextItem(text="async")),))

    kernel.register_prompt(prompt_def, handler)
    result = await kernel.get_prompt("async_prompt", {}, make_scope())

    assert result.messages[0].content.text == "async"  # type: ignore[union-attr]


async def test_async_kernel_permission_hook() -> None:
    async def deny_hook(scope: ExecutionScope[None], req: PermissionRequest) -> None:
        raise PermissionDeniedError("async denied")

    kernel: AsyncKernel[None] = AsyncKernel(permission_hook=deny_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=())

    kernel.register_tool(tool_def, handler)

    with pytest.raises(PermissionDeniedError):
        await kernel.call_tool("tool", {}, make_scope())


async def test_async_kernel_validation_hook() -> None:
    async def validation_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        if "bad" in args:
            raise ValidationError("bad argument")

    kernel: AsyncKernel[None] = AsyncKernel(validation_hook=validation_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=())

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ValidationError):
        await kernel.call_tool("tool", {"bad": True}, make_scope())


async def test_async_kernel_validation_hook_non_validation_error_wrapped() -> None:
    async def validation_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        raise TypeError("wrong type")

    kernel: AsyncKernel[None] = AsyncKernel(validation_hook=validation_hook)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=())

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ValidationError) as exc_info:
        await kernel.call_tool("tool", {}, make_scope())

    assert "wrong type" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, TypeError)


async def test_async_kernel_event_handler() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    async def tool_handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    kernel.register_tool(tool_def, tool_handler)
    await kernel.call_tool("tool", {}, make_scope())

    assert len(events) == 2
    assert events[0].phase == "before"  # type: ignore[union-attr]
    assert events[1].phase == "after"  # type: ignore[union-attr]


async def test_async_kernel_emit_progress() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)
    scope = make_scope_with_progress()

    await kernel.emit_progress(scope, 25.0, total=100.0)

    assert len(events) == 1
    assert isinstance(events[0], ProgressEvent)


async def test_async_kernel_emit_log() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)

    await kernel.emit_log("warning", "Something happened")

    assert len(events) == 1
    assert isinstance(events[0], LogEvent)


async def test_async_kernel_handler_exception_wrapped() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    tool_def = ToolDef(name="failing", input_schema={"type": "object"})

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        raise RuntimeError("async failure")

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        await kernel.call_tool("failing", {}, make_scope())

    assert isinstance(exc_info.value.__cause__, RuntimeError)


async def test_async_kernel_tool_error_emits_error_event() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)
    tool_def = ToolDef(name="failing", input_schema={"type": "object"})

    async def tool_handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        raise ValueError("async tool error")

    kernel.register_tool(tool_def, tool_handler)

    with pytest.raises(ExecutionError):
        await kernel.call_tool("failing", {}, make_scope())

    assert len(events) == 2
    assert events[0].phase == "before"  # type: ignore[union-attr]
    assert events[1].phase == "error"  # type: ignore[union-attr]
    assert events[1].error is not None  # type: ignore[union-attr]


async def test_async_kernel_tool_execution_error_not_rewrapped() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        raise ExecutionError("direct execution error")

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        await kernel.call_tool("tool", {}, make_scope())

    assert str(exc_info.value) == "direct execution error"
    assert exc_info.value.__cause__ is None


# =============================================================================
# Context Type Tests
# =============================================================================


def test_kernel_with_custom_context() -> None:
    kernel: Kernel[dict[str, str]] = Kernel()
    tool_def = ToolDef(name="user_tool", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[dict[str, str]], args: dict[str, Any]) -> ToolResult:
        user = scope.ctx.get("user", "anonymous")
        return ToolResult(content=(TextItem(text=f"Hello, {user}"),))

    kernel.register_tool(tool_def, handler)
    scope = ExecutionScope(ctx={"user": "alice"})
    result = kernel.call_tool("user_tool", {}, scope)

    assert result.content[0].text == "Hello, alice"  # type: ignore[union-attr]


async def test_async_kernel_with_custom_context() -> None:
    kernel: AsyncKernel[dict[str, int]] = AsyncKernel()
    tool_def = ToolDef(name="counter", input_schema={"type": "object"})

    async def handler(scope: ExecutionScope[dict[str, int]], args: dict[str, Any]) -> ToolResult:
        count = scope.ctx.get("count", 0)
        return ToolResult(content=(TextItem(text=str(count)),))

    kernel.register_tool(tool_def, handler)
    scope = ExecutionScope(ctx={"count": 42})
    result = await kernel.call_tool("counter", {}, scope)

    assert result.content[0].text == "42"  # type: ignore[union-attr]


# =============================================================================
# Resource Error Handling Tests
# =============================================================================


def test_kernel_resource_handler_exception_wrapped() -> None:
    kernel: Kernel[None] = Kernel()
    resource_def = ResourceDef(uri="file:///failing", name="Failing")

    def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        raise OSError("file not accessible")

    kernel.register_resource(resource_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        kernel.read_resource("file:///failing", make_scope())

    assert "file:///failing" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, IOError)


def test_kernel_resource_execution_error_not_rewrapped() -> None:
    kernel: Kernel[None] = Kernel()
    resource_def = ResourceDef(uri="file:///test", name="Test")

    def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        raise ExecutionError("direct resource error")

    kernel.register_resource(resource_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        kernel.read_resource("file:///test", make_scope())

    assert str(exc_info.value) == "direct resource error"
    assert exc_info.value.__cause__ is None


def test_kernel_resource_error_emits_error_event() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    resource_def = ResourceDef(uri="file:///failing", name="Failing")

    def resource_handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        raise ValueError("resource error")

    kernel.register_resource(resource_def, resource_handler)

    with pytest.raises(ExecutionError):
        kernel.read_resource("file:///failing", make_scope())

    assert len(events) == 2
    assert isinstance(events[0], ResourceReadEvent)
    assert events[0].phase == "before"
    assert isinstance(events[1], ResourceReadEvent)
    assert events[1].phase == "error"
    assert events[1].error is not None


async def test_async_kernel_resource_handler_exception_wrapped() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    resource_def = ResourceDef(uri="async://failing", name="Failing")

    async def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        raise OSError("async io error")

    kernel.register_resource(resource_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        await kernel.read_resource("async://failing", make_scope())

    assert isinstance(exc_info.value.__cause__, IOError)


async def test_async_kernel_resource_execution_error_not_rewrapped() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    resource_def = ResourceDef(uri="async://test", name="Test")

    async def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        raise ExecutionError("async resource exec error")

    kernel.register_resource(resource_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        await kernel.read_resource("async://test", make_scope())

    assert str(exc_info.value) == "async resource exec error"


async def test_async_kernel_resource_error_emits_error_event() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)
    resource_def = ResourceDef(uri="async://failing", name="Failing")

    async def resource_handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        raise ValueError("async resource error")

    kernel.register_resource(resource_def, resource_handler)

    with pytest.raises(ExecutionError):
        await kernel.read_resource("async://failing", make_scope())

    assert len(events) == 2
    assert events[0].phase == "before"  # type: ignore[union-attr]
    assert events[1].phase == "error"  # type: ignore[union-attr]


# =============================================================================
# Prompt Error Handling Tests
# =============================================================================


def test_kernel_prompt_handler_exception_wrapped() -> None:
    kernel: Kernel[None] = Kernel()
    prompt_def = PromptDef(name="failing_prompt")

    def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        raise ValueError("prompt generation failed")

    kernel.register_prompt(prompt_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        kernel.get_prompt("failing_prompt", {}, make_scope())

    assert "failing_prompt" in str(exc_info.value)
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_kernel_prompt_execution_error_not_rewrapped() -> None:
    kernel: Kernel[None] = Kernel()
    prompt_def = PromptDef(name="prompt")

    def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        raise ExecutionError("direct prompt error")

    kernel.register_prompt(prompt_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        kernel.get_prompt("prompt", {}, make_scope())

    assert str(exc_info.value) == "direct prompt error"


def test_kernel_prompt_error_emits_error_event() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    prompt_def = PromptDef(name="failing")

    def prompt_handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        raise RuntimeError("prompt error")

    kernel.register_prompt(prompt_def, prompt_handler)

    with pytest.raises(ExecutionError):
        kernel.get_prompt("failing", {}, make_scope())

    assert len(events) == 2
    assert isinstance(events[0], PromptGetEvent)
    assert events[0].phase == "before"
    assert isinstance(events[1], PromptGetEvent)
    assert events[1].phase == "error"


async def test_async_kernel_prompt_handler_exception_wrapped() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    prompt_def = PromptDef(name="async_failing")

    async def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        raise ValueError("async prompt error")

    kernel.register_prompt(prompt_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        await kernel.get_prompt("async_failing", {}, make_scope())

    assert isinstance(exc_info.value.__cause__, ValueError)


async def test_async_kernel_prompt_execution_error_not_rewrapped() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()
    prompt_def = PromptDef(name="prompt")

    async def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        raise ExecutionError("async prompt exec error")

    kernel.register_prompt(prompt_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        await kernel.get_prompt("prompt", {}, make_scope())

    assert str(exc_info.value) == "async prompt exec error"


async def test_async_kernel_prompt_error_emits_error_event() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)
    prompt_def = PromptDef(name="failing")

    async def prompt_handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        raise RuntimeError("async prompt runtime error")

    kernel.register_prompt(prompt_def, prompt_handler)

    with pytest.raises(ExecutionError):
        await kernel.get_prompt("failing", {}, make_scope())

    assert len(events) == 2
    assert events[0].phase == "before"  # type: ignore[union-attr]
    assert events[1].phase == "error"  # type: ignore[union-attr]


# =============================================================================
# Event Handler Tests for Resources and Prompts
# =============================================================================


def test_kernel_event_handler_receives_resource_events() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    resource_def = ResourceDef(uri="file:///test", name="Test")

    def resource_handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        return ResourceResult(contents=(ResourceContent(uri=uri, text="content"),))

    kernel.register_resource(resource_def, resource_handler)
    kernel.read_resource("file:///test", make_scope())

    assert len(events) == 2
    assert isinstance(events[0], ResourceReadEvent)
    assert events[0].phase == "before"
    assert events[0].uri == "file:///test"
    assert isinstance(events[1], ResourceReadEvent)
    assert events[1].phase == "after"
    assert events[1].result is not None


def test_kernel_event_handler_receives_prompt_events() -> None:
    events: list[Event] = []

    def handler(event: Event) -> None:
        events.append(event)

    kernel: Kernel[None] = Kernel(event_handler=handler)
    prompt_def = PromptDef(name="greeting")

    def prompt_handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        return PromptResult(messages=(PromptMessage(role="user", content=TextItem(text="hi")),))

    kernel.register_prompt(prompt_def, prompt_handler)
    kernel.get_prompt("greeting", {"name": "Alice"}, make_scope())

    assert len(events) == 2
    assert isinstance(events[0], PromptGetEvent)
    assert events[0].phase == "before"
    assert events[0].prompt_name == "greeting"
    assert events[0].arguments == {"name": "Alice"}
    assert isinstance(events[1], PromptGetEvent)
    assert events[1].phase == "after"


async def test_async_kernel_event_handler_receives_resource_events() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)
    resource_def = ResourceDef(uri="async://test", name="Test")

    async def resource_handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        return ResourceResult(contents=(ResourceContent(uri=uri, text="async content"),))

    kernel.register_resource(resource_def, resource_handler)
    await kernel.read_resource("async://test", make_scope())

    assert len(events) == 2
    assert events[0].phase == "before"  # type: ignore[union-attr]
    assert events[1].phase == "after"  # type: ignore[union-attr]


async def test_async_kernel_event_handler_receives_prompt_events() -> None:
    events: list[Event] = []

    async def handler(event: Event) -> None:
        events.append(event)

    kernel: AsyncKernel[None] = AsyncKernel(event_handler=handler)
    prompt_def = PromptDef(name="async_prompt")

    async def prompt_handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        return PromptResult(messages=(PromptMessage(role="user", content=TextItem(text="hi")),))

    kernel.register_prompt(prompt_def, prompt_handler)
    await kernel.get_prompt("async_prompt", {}, make_scope())

    assert len(events) == 2
    assert events[0].phase == "before"  # type: ignore[union-attr]
    assert events[1].phase == "after"  # type: ignore[union-attr]


# =============================================================================
# Sync Kernel ExecutionError passthrough test
# =============================================================================


def test_kernel_tool_execution_error_not_rewrapped() -> None:
    kernel: Kernel[None] = Kernel()
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        raise ExecutionError("direct tool execution error")

    kernel.register_tool(tool_def, handler)

    with pytest.raises(ExecutionError) as exc_info:
        kernel.call_tool("tool", {}, make_scope())

    assert str(exc_info.value) == "direct tool execution error"
    assert exc_info.value.__cause__ is None


# =============================================================================
# Async Permission Hook Tests for Resources and Prompts
# =============================================================================


async def test_async_kernel_resource_permission_hook() -> None:
    async def deny_hook(scope: ExecutionScope[None], req: PermissionRequest) -> None:
        if req.kind == "resource":
            raise PermissionDeniedError("resource access denied")

    kernel: AsyncKernel[None] = AsyncKernel(permission_hook=deny_hook)
    resource_def = ResourceDef(uri="async://protected", name="Protected")

    async def handler(scope: ExecutionScope[None], uri: str) -> ResourceResult:
        return ResourceResult(contents=(ResourceContent(uri=uri, text="secret"),))

    kernel.register_resource(resource_def, handler)

    with pytest.raises(PermissionDeniedError):
        await kernel.read_resource("async://protected", make_scope())


async def test_async_kernel_prompt_permission_hook() -> None:
    async def deny_hook(scope: ExecutionScope[None], req: PermissionRequest) -> None:
        if req.kind == "prompt":
            raise PermissionDeniedError("prompt access denied")

    kernel: AsyncKernel[None] = AsyncKernel(permission_hook=deny_hook)
    prompt_def = PromptDef(name="protected_prompt")

    async def handler(scope: ExecutionScope[None], args: dict[str, str]) -> PromptResult:
        return PromptResult(messages=())

    kernel.register_prompt(prompt_def, handler)

    with pytest.raises(PermissionDeniedError):
        await kernel.get_prompt("protected_prompt", {}, make_scope())


async def test_async_kernel_emit_progress_without_handler() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()  # No event handler
    scope = ExecutionScope(ctx=None, progress_token="token")

    await kernel.emit_progress(scope, 50.0)  # Should not raise


async def test_async_kernel_emit_log_without_handler() -> None:
    kernel: AsyncKernel[None] = AsyncKernel()  # No event handler

    await kernel.emit_log("info", "test")  # Should not raise


# =============================================================================
# Kernel Strict Mode Tests
# =============================================================================


def test_kernel_strict_requires_jsonschema() -> None:
    """strict=True at init raises ImportError if jsonschema not installed."""
    from unittest.mock import patch

    with (
        patch("mcpk.validation.HAS_JSONSCHEMA", False),
        pytest.raises(ImportError, match="jsonschema is required"),
    ):
        Kernel(strict=True)


def test_async_kernel_strict_requires_jsonschema() -> None:
    """AsyncKernel strict=True at init raises ImportError if jsonschema not installed."""
    from unittest.mock import patch

    with (
        patch("mcpk.validation.HAS_JSONSCHEMA", False),
        pytest.raises(ImportError, match="jsonschema is required"),
    ):
        AsyncKernel(strict=True)


def test_kernel_strict_validates_schema_at_registration() -> None:
    """strict=True validates input_schema is valid JSON Schema at register_tool()."""
    kernel: Kernel[None] = Kernel(strict=True)

    # Invalid JSON Schema ($ref must be a string, not a boolean)
    invalid_schema = {"type": "object", "$ref": True}
    tool_def = ToolDef(name="tool", input_schema=invalid_schema)

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    # Should raise ValidationError for invalid schema
    with pytest.raises(ValidationError, match="Invalid JSON Schema"):
        kernel.register_tool(tool_def, handler)


def test_async_kernel_strict_validates_schema_at_registration() -> None:
    """AsyncKernel strict=True validates input_schema at register_tool()."""
    kernel: AsyncKernel[None] = AsyncKernel(strict=True)

    # Invalid JSON Schema ($ref must be a string, not a boolean)
    invalid_schema = {"type": "object", "$ref": True}
    tool_def = ToolDef(name="tool", input_schema=invalid_schema)

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    with pytest.raises(ValidationError, match="Invalid JSON Schema"):
        kernel.register_tool(tool_def, handler)


def test_kernel_strict_validates_arguments_at_call() -> None:
    """strict=True validates call_tool() arguments against schema."""
    kernel: Kernel[None] = Kernel(strict=True)

    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }
    tool_def = ToolDef(name="greet", input_schema=schema)

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text=f"Hello, {args['name']}"),))

    kernel.register_tool(tool_def, handler)

    # Valid arguments work
    result = kernel.call_tool("greet", {"name": "Alice"}, make_scope())
    assert result.content[0].text == "Hello, Alice"  # type: ignore[union-attr]

    # Invalid arguments (missing required field) raise ValidationError
    with pytest.raises(ValidationError, match="Invalid arguments"):
        kernel.call_tool("greet", {}, make_scope())


async def test_async_kernel_strict_validates_arguments_at_call() -> None:
    """AsyncKernel strict=True validates call_tool() arguments against schema."""
    kernel: AsyncKernel[None] = AsyncKernel(strict=True)

    schema = {
        "type": "object",
        "properties": {"count": {"type": "integer"}},
        "required": ["count"],
    }
    tool_def = ToolDef(name="counter", input_schema=schema)

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text=str(args["count"])),))

    kernel.register_tool(tool_def, handler)

    # Valid arguments work
    result = await kernel.call_tool("counter", {"count": 42}, make_scope())
    assert result.content[0].text == "42"  # type: ignore[union-attr]

    # Wrong type raises ValidationError
    with pytest.raises(ValidationError, match="Invalid arguments"):
        await kernel.call_tool("counter", {"count": "not an int"}, make_scope())


def test_kernel_strict_chains_with_user_validation_hook() -> None:
    """strict=True runs schema validation then user's validation_hook (both execute)."""
    user_hook_calls: list[tuple[str, dict[str, Any]]] = []

    def user_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        user_hook_calls.append((name, args.copy()))
        # Additional custom validation
        if args.get("forbidden"):
            raise ValidationError("forbidden argument not allowed")

    kernel: Kernel[None] = Kernel(strict=True, validation_hook=user_hook)

    schema = {"type": "object", "properties": {"value": {"type": "integer"}}}
    tool_def = ToolDef(name="process", input_schema=schema)

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="processed"),))

    kernel.register_tool(tool_def, handler)

    # Call with valid args - both hooks run, user hook records the call
    result = kernel.call_tool("process", {"value": 10}, make_scope())
    assert result.content[0].text == "processed"  # type: ignore[union-attr]
    assert len(user_hook_calls) == 1
    assert user_hook_calls[0] == ("process", {"value": 10})

    # Call with type error - strict validation fails first (user hook not called)
    user_hook_calls.clear()
    with pytest.raises(ValidationError, match="Invalid arguments"):
        kernel.call_tool("process", {"value": "string"}, make_scope())
    assert len(user_hook_calls) == 0  # User hook never ran

    # Call with valid schema but forbidden by user hook
    user_hook_calls.clear()
    with pytest.raises(ValidationError, match="forbidden argument not allowed"):
        kernel.call_tool("process", {"value": 1, "forbidden": True}, make_scope())
    assert len(user_hook_calls) == 1  # User hook was called (after strict validation passed)


async def test_async_kernel_strict_chains_with_user_validation_hook() -> None:
    """AsyncKernel strict=True runs schema validation then user's hook (both execute)."""
    user_hook_calls: list[tuple[str, dict[str, Any]]] = []

    async def user_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        user_hook_calls.append((name, args.copy()))
        if args.get("blocked"):
            raise ValidationError("blocked by user hook")

    kernel: AsyncKernel[None] = AsyncKernel(strict=True, validation_hook=user_hook)

    schema = {"type": "object", "properties": {"data": {"type": "string"}}}
    tool_def = ToolDef(name="submit", input_schema=schema)

    async def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="submitted"),))

    kernel.register_tool(tool_def, handler)

    # Valid call - both hooks run
    result = await kernel.call_tool("submit", {"data": "hello"}, make_scope())
    assert result.content[0].text == "submitted"  # type: ignore[union-attr]
    assert len(user_hook_calls) == 1

    # Type validation fails - user hook not called
    user_hook_calls.clear()
    with pytest.raises(ValidationError, match="Invalid arguments"):
        await kernel.call_tool("submit", {"data": 123}, make_scope())
    assert len(user_hook_calls) == 0

    # User hook validation fails
    user_hook_calls.clear()
    with pytest.raises(ValidationError, match="blocked by user hook"):
        await kernel.call_tool("submit", {"data": "test", "blocked": True}, make_scope())
    assert len(user_hook_calls) == 1


def test_kernel_non_strict_ignores_invalid_schema() -> None:
    """Non-strict kernel allows invalid JSON Schema at registration."""
    kernel: Kernel[None] = Kernel(strict=False)

    # Invalid JSON Schema ($ref must be a string, not a boolean)
    # Non-strict mode doesn't validate schema structure
    invalid_schema = {"type": "object", "$ref": True}
    tool_def = ToolDef(name="tool", input_schema=invalid_schema)

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    # Should NOT raise - non-strict mode doesn't validate schema
    kernel.register_tool(tool_def, handler)
    result = kernel.call_tool("tool", {}, make_scope())
    assert result.content[0].text == "ok"  # type: ignore[union-attr]


def test_kernel_non_strict_with_user_validation_hook() -> None:
    """Non-strict kernel with user validation_hook only runs user hook."""
    hook_calls: list[str] = []

    def user_hook(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        hook_calls.append(name)

    kernel: Kernel[None] = Kernel(strict=False, validation_hook=user_hook)

    schema = {"type": "object", "properties": {"x": {"type": "integer"}}}
    tool_def = ToolDef(name="calc", input_schema=schema)

    def handler(scope: ExecutionScope[None], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="done"),))

    kernel.register_tool(tool_def, handler)

    # Call with wrong type - non-strict doesn't validate, but user hook runs
    # (user hook doesn't do type checking in this test)
    result = kernel.call_tool("calc", {"x": "string"}, make_scope())
    assert result.content[0].text == "done"  # type: ignore[union-attr]
    assert hook_calls == ["calc"]
