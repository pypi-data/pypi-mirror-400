from __future__ import annotations

from typing import Any

from mcpk._base import BaseKernel
from mcpk._runtime import (
    call_tool,
    call_tool_async,
    get_prompt,
    get_prompt_async,
    read_resource,
    read_resource_async,
)
from mcpk.events import AsyncEventHandler, EventHandler, LogEvent, LogLevel, ProgressEvent
from mcpk.hooks import AsyncPermissionHook, AsyncValidationHook, PermissionHook, ValidationHook
from mcpk.types import (
    AsyncPromptHandler,
    AsyncResourceHandler,
    AsyncToolHandler,
    ExecutionScope,
    PromptDef,
    PromptHandler,
    PromptResult,
    ResourceDef,
    ResourceHandler,
    ResourceResult,
    ToolDef,
    ToolHandler,
    ToolResult,
)
from mcpk.validation import (
    chain_async_validation_hooks,
    chain_validation_hooks,
    make_async_validation_hook,
    make_validation_hook,
)


class Kernel[ContextT](BaseKernel[ContextT]):
    def __init__(
        self,
        *,
        strict: bool = False,
        permission_hook: PermissionHook[ContextT] | None = None,
        validation_hook: ValidationHook | None = None,
        event_handler: EventHandler | None = None,
    ) -> None:
        super().__init__(strict=strict)
        self._permission_hook = permission_hook
        self._event_handler = event_handler
        self._validation_hook = self._build_validation_hook(validation_hook)

    def register_tool(self, definition: ToolDef, handler: ToolHandler[ContextT]) -> None:
        self._check_schema_if_strict(definition.input_schema)
        self._registry.register_tool(definition, handler)

    def register_resource(
        self, definition: ResourceDef, handler: ResourceHandler[ContextT]
    ) -> None:
        self._registry.register_resource(definition, handler)

    def register_prompt(self, definition: PromptDef, handler: PromptHandler[ContextT]) -> None:
        self._registry.register_prompt(definition, handler)

    def call_tool(
        self, name: str, arguments: dict[str, Any], scope: ExecutionScope[ContextT]
    ) -> ToolResult:
        return call_tool(
            self._registry,
            name,
            arguments,
            scope,
            perm=self._permission_hook,
            val=self._validation_hook,
            emit=self._event_handler,
        )

    def read_resource(self, uri: str, scope: ExecutionScope[ContextT]) -> ResourceResult:
        return read_resource(
            self._registry,
            uri,
            scope,
            perm=self._permission_hook,
            emit=self._event_handler,
        )

    def get_prompt(
        self, name: str, arguments: dict[str, str], scope: ExecutionScope[ContextT]
    ) -> PromptResult:
        return get_prompt(
            self._registry,
            name,
            arguments,
            scope,
            perm=self._permission_hook,
            emit=self._event_handler,
        )

    def emit_progress(
        self,
        scope: ExecutionScope[ContextT],
        progress: float,
        total: float | None = None,
        message: str | None = None,
    ) -> None:
        if not self._event_handler or not scope.progress_token:
            return
        self._event_handler(
            ProgressEvent(
                progress_token=scope.progress_token,
                progress=progress,
                total=total,
                message=message,
            )
        )

    def emit_log(self, level: LogLevel, data: Any, logger: str | None = None) -> None:
        if not self._event_handler:
            return
        self._event_handler(LogEvent(level=level, data=data, logger=logger))

    def _build_validation_hook(self, user_hook: ValidationHook | None) -> ValidationHook | None:
        return self._compile_validation_hooks(
            make_validation_hook, chain_validation_hooks, user_hook
        )


class AsyncKernel[ContextT](BaseKernel[ContextT]):
    def __init__(
        self,
        *,
        strict: bool = False,
        permission_hook: AsyncPermissionHook[ContextT] | None = None,
        validation_hook: AsyncValidationHook | None = None,
        event_handler: AsyncEventHandler | None = None,
    ) -> None:
        super().__init__(strict=strict)
        self._permission_hook = permission_hook
        self._event_handler = event_handler
        self._validation_hook = self._build_validation_hook(validation_hook)

    def register_tool(self, definition: ToolDef, handler: AsyncToolHandler[ContextT]) -> None:
        self._check_schema_if_strict(definition.input_schema)
        self._registry.register_tool(definition, handler)

    def register_resource(
        self, definition: ResourceDef, handler: AsyncResourceHandler[ContextT]
    ) -> None:
        self._registry.register_resource(definition, handler)

    def register_prompt(self, definition: PromptDef, handler: AsyncPromptHandler[ContextT]) -> None:
        self._registry.register_prompt(definition, handler)

    async def call_tool(
        self, name: str, arguments: dict[str, Any], scope: ExecutionScope[ContextT]
    ) -> ToolResult:
        return await call_tool_async(
            self._registry,
            name,
            arguments,
            scope,
            perm=self._permission_hook,
            val=self._validation_hook,
            emit=self._event_handler,
        )

    async def read_resource(self, uri: str, scope: ExecutionScope[ContextT]) -> ResourceResult:
        return await read_resource_async(
            self._registry,
            uri,
            scope,
            perm=self._permission_hook,
            emit=self._event_handler,
        )

    async def get_prompt(
        self, name: str, arguments: dict[str, str], scope: ExecutionScope[ContextT]
    ) -> PromptResult:
        return await get_prompt_async(
            self._registry,
            name,
            arguments,
            scope,
            perm=self._permission_hook,
            emit=self._event_handler,
        )

    async def emit_progress(
        self,
        scope: ExecutionScope[ContextT],
        progress: float,
        total: float | None = None,
        message: str | None = None,
    ) -> None:
        if not self._event_handler or not scope.progress_token:
            return
        await self._event_handler(
            ProgressEvent(
                progress_token=scope.progress_token,
                progress=progress,
                total=total,
                message=message,
            )
        )

    async def emit_log(self, level: LogLevel, data: Any, logger: str | None = None) -> None:
        if not self._event_handler:
            return
        await self._event_handler(LogEvent(level=level, data=data, logger=logger))

    def _build_validation_hook(
        self, user_hook: AsyncValidationHook | None
    ) -> AsyncValidationHook | None:
        return self._compile_validation_hooks(
            make_async_validation_hook, chain_async_validation_hooks, user_hook
        )
