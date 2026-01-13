from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from mcpk._enforce import enforce_prompt_result, enforce_resource_result, enforce_tool_result
from mcpk.errors import (
    ExecutionError,
    PromptNotFoundError,
    ResourceNotFoundError,
    ToolNotFoundError,
    ValidationError,
)
from mcpk.events import Event, PromptGetEvent, ResourceReadEvent, ToolCallEvent
from mcpk.hooks import AsyncValidationHook, PermissionRequest, ValidationHook
from mcpk.types import (
    AsyncPromptHandler,
    AsyncResourceHandler,
    AsyncToolHandler,
    ExecutionScope,
    PromptHandler,
    PromptResult,
    ResourceHandler,
    ResourceResult,
    ToolHandler,
    ToolResult,
)

if TYPE_CHECKING:
    from mcpk._registry import Registry


# =============================================================================
# Type Aliases
# =============================================================================

type PermissionHook = Callable[[ExecutionScope[Any], PermissionRequest], None]
type AsyncPermissionHook = Callable[[ExecutionScope[Any], PermissionRequest], Awaitable[None]]

type EmitHook = Callable[[Event], None]
type AsyncEmitHook = Callable[[Event], Awaitable[None]]

type ValidatorCallback = Callable[[], None]
type AsyncValidatorCallback = Callable[[], Awaitable[None]]


# =============================================================================
# Models
# =============================================================================


@dataclass(frozen=True, slots=True)
class BaseExecutionSpec[TResult, TReturn]:
    permission: PermissionRequest
    handler: Callable[[], TReturn]
    validator: Callable[[TResult], TResult]
    before_event: Event
    after_event: Callable[[TResult], Event]
    error_event: Callable[[Exception], Event]
    error_message: str


class ExecutionSpec[TResult](BaseExecutionSpec[TResult, TResult]):
    pass


class AsyncExecutionSpec[TResult](BaseExecutionSpec[TResult, Awaitable[TResult]]):
    pass


# =============================================================================
# Public Functions
# =============================================================================


def call_tool(
    registry: Registry,
    name: str,
    arguments: dict[str, Any],
    scope: ExecutionScope[Any],
    perm: PermissionHook | None = None,
    val: ValidationHook | None = None,
    emit: EmitHook | None = None,
) -> ToolResult:
    schema, handler = _get_tool(registry, name)

    def _valid() -> None:
        if not val:
            return
        val(name, arguments, schema)

    spec = ExecutionSpec[ToolResult](
        permission=PermissionRequest(kind="tool", name=name, arguments=arguments),
        handler=lambda: cast(ToolHandler[Any], handler)(scope, arguments),
        validator=_ensure_tool_result,
        before_event=ToolCallEvent(
            phase="before", tool_name=name, arguments=arguments, scope=scope
        ),
        after_event=lambda r: ToolCallEvent(
            phase="after", tool_name=name, arguments=arguments, scope=scope, result=r
        ),
        error_event=lambda e: ToolCallEvent(
            phase="error", tool_name=name, arguments=arguments, scope=scope, error=e
        ),
        error_message=f"Tool '{name}' raised an exception",
    )

    return _execute_sync(spec, scope, perm, emit, valid=_valid)


async def call_tool_async(
    registry: Registry,
    name: str,
    arguments: dict[str, Any],
    scope: ExecutionScope[Any],
    perm: AsyncPermissionHook | None = None,
    val: AsyncValidationHook | None = None,
    emit: AsyncEmitHook | None = None,
) -> ToolResult:
    schema, handler = _get_tool(registry, name)

    async def _valid() -> None:
        if not val:
            return
        await val(name, arguments, schema)

    async def _handler() -> ToolResult:
        return await cast(AsyncToolHandler[Any], handler)(scope, arguments)

    spec = AsyncExecutionSpec[ToolResult](
        permission=PermissionRequest(kind="tool", name=name, arguments=arguments),
        handler=_handler,
        validator=_ensure_tool_result,
        before_event=ToolCallEvent(
            phase="before", tool_name=name, arguments=arguments, scope=scope
        ),
        after_event=lambda r: ToolCallEvent(
            phase="after", tool_name=name, arguments=arguments, scope=scope, result=r
        ),
        error_event=lambda e: ToolCallEvent(
            phase="error", tool_name=name, arguments=arguments, scope=scope, error=e
        ),
        error_message=f"Tool '{name}' raised an exception",
    )

    return await _execute_async(spec, scope, perm, emit, valid=_valid)


def read_resource(
    registry: Registry,
    uri: str,
    scope: ExecutionScope[Any],
    perm: PermissionHook | None = None,
    emit: EmitHook | None = None,
) -> ResourceResult:
    handler = _get_resource(registry, uri)

    spec = ExecutionSpec[ResourceResult](
        permission=PermissionRequest(kind="resource", name=uri),
        handler=lambda: cast(ResourceHandler[Any], handler)(scope, uri),
        validator=_ensure_resource_result,
        before_event=ResourceReadEvent(phase="before", uri=uri, scope=scope),
        after_event=lambda r: ResourceReadEvent(phase="after", uri=uri, scope=scope, result=r),
        error_event=lambda e: ResourceReadEvent(phase="error", uri=uri, scope=scope, error=e),
        error_message=f"Resource '{uri}' handler raised an exception",
    )

    return _execute_sync(spec, scope, perm, emit)


async def read_resource_async(
    registry: Registry,
    uri: str,
    scope: ExecutionScope[Any],
    perm: AsyncPermissionHook | None = None,
    emit: AsyncEmitHook | None = None,
) -> ResourceResult:
    handler = _get_resource(registry, uri)

    spec = AsyncExecutionSpec[ResourceResult](
        permission=PermissionRequest(kind="resource", name=uri),
        handler=lambda: cast(AsyncResourceHandler[Any], handler)(scope, uri),
        validator=_ensure_resource_result,
        before_event=ResourceReadEvent(phase="before", uri=uri, scope=scope),
        after_event=lambda r: ResourceReadEvent(phase="after", uri=uri, scope=scope, result=r),
        error_event=lambda e: ResourceReadEvent(phase="error", uri=uri, scope=scope, error=e),
        error_message=f"Resource '{uri}' handler raised an exception",
    )

    return await _execute_async(spec, scope, perm, emit)


def get_prompt(
    registry: Registry,
    name: str,
    arguments: dict[str, str],
    scope: ExecutionScope[Any],
    perm: PermissionHook | None = None,
    emit: EmitHook | None = None,
) -> PromptResult:
    handler = _get_prompt_handler(registry, name)

    spec = ExecutionSpec[PromptResult](
        permission=PermissionRequest(kind="prompt", name=name, arguments=arguments),
        handler=lambda: cast(PromptHandler[Any], handler)(scope, arguments),
        validator=_ensure_prompt_result,
        before_event=PromptGetEvent(
            phase="before", prompt_name=name, arguments=arguments, scope=scope
        ),
        after_event=lambda r: PromptGetEvent(
            phase="after",
            prompt_name=name,
            arguments=arguments,
            scope=scope,
            result=r,
        ),
        error_event=lambda e: PromptGetEvent(
            phase="error",
            prompt_name=name,
            arguments=arguments,
            scope=scope,
            error=e,
        ),
        error_message=f"Prompt '{name}' handler raised an exception",
    )

    return _execute_sync(spec, scope, perm, emit)


async def get_prompt_async(
    registry: Registry,
    name: str,
    arguments: dict[str, str],
    scope: ExecutionScope[Any],
    perm: AsyncPermissionHook | None = None,
    emit: AsyncEmitHook | None = None,
) -> PromptResult:
    handler = _get_prompt_handler(registry, name)

    spec = AsyncExecutionSpec[PromptResult](
        permission=PermissionRequest(kind="prompt", name=name, arguments=arguments),
        handler=lambda: cast(AsyncPromptHandler[Any], handler)(scope, arguments),
        validator=_ensure_prompt_result,
        before_event=PromptGetEvent(
            phase="before", prompt_name=name, arguments=arguments, scope=scope
        ),
        after_event=lambda r: PromptGetEvent(
            phase="after",
            prompt_name=name,
            arguments=arguments,
            scope=scope,
            result=r,
        ),
        error_event=lambda e: PromptGetEvent(
            phase="error",
            prompt_name=name,
            arguments=arguments,
            scope=scope,
            error=e,
        ),
        error_message=f"Prompt '{name}' handler raised an exception",
    )

    return await _execute_async(spec, scope, perm, emit)


# =============================================================================
# Private Helper Functions
# =============================================================================


def _execute_sync[TResult](
    spec: ExecutionSpec[TResult],
    scope: ExecutionScope[Any],
    perm: PermissionHook | None = None,
    emit: EmitHook | None = None,
    valid: ValidatorCallback | None = None,
) -> TResult:
    if perm:
        perm(scope, spec.permission)

    if valid:
        try:
            valid()
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(str(e)) from e

    if emit:
        emit(spec.before_event)

    try:
        raw = spec.handler()
    except ExecutionError:
        raise
    except Exception as e:
        err = ExecutionError(spec.error_message, e)
        if emit:
            emit(spec.error_event(err))
        raise err from e

    result = spec.validator(raw)

    if emit:
        emit(spec.after_event(result))

    return result


async def _execute_async[TResult](
    spec: AsyncExecutionSpec[TResult],
    scope: ExecutionScope[Any],
    perm: AsyncPermissionHook | None = None,
    emit: AsyncEmitHook | None = None,
    valid: AsyncValidatorCallback | None = None,
) -> TResult:
    if perm:
        await perm(scope, spec.permission)

    if valid:
        try:
            await valid()
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(str(e)) from e

    if emit:
        await emit(spec.before_event)

    try:
        raw = await spec.handler()
    except ExecutionError:
        raise
    except Exception as e:
        err = ExecutionError(spec.error_message, e)
        if emit:
            await emit(spec.error_event(err))
        raise err from e

    result = spec.validator(raw)

    if emit:
        await emit(spec.after_event(result))

    return result


def _get_tool(registry: Registry, name: str) -> tuple[dict[str, Any], Any]:
    if not (entry := registry.get_tool(name)):
        raise ToolNotFoundError(name)
    return entry[0].input_schema, entry[1]


def _get_resource(registry: Registry, uri: str) -> Any:
    if not (entry := registry.get_resource(uri)):
        raise ResourceNotFoundError(uri)
    return entry[1]


def _get_prompt_handler(registry: Registry, name: str) -> Any:
    if not (entry := registry.get_prompt(name)):
        raise PromptNotFoundError(name)
    return entry[1]


def _ensure_tool_result(result: ToolResult) -> ToolResult:
    enforce_tool_result(result)
    return result


def _ensure_resource_result(result: ResourceResult) -> ResourceResult:
    enforce_resource_result(result)
    return result


def _ensure_prompt_result(result: PromptResult) -> PromptResult:
    enforce_prompt_result(result)
    return result
