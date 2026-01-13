"""Base kernel class with shared registry functionality."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mcpk._registry import Registry
from mcpk.types import PromptDef, ResourceDef, ToolDef
from mcpk.validation import check_schema, require_jsonschema


class BaseKernel[ContextT]:
    def __init__(self, *, strict: bool = False) -> None:
        self._registry: Registry = Registry()
        self._strict = strict

        if strict:
            require_jsonschema()

    def all_tools(self) -> tuple[ToolDef, ...]:
        """List all registered tool definitions."""
        return self._registry.all_tools()

    def all_resources(self) -> tuple[ResourceDef, ...]:
        """List all registered resource definitions."""
        return self._registry.all_resources()

    def all_prompts(self) -> tuple[PromptDef, ...]:
        """List all registered prompt definitions."""
        return self._registry.all_prompts()

    def _compile_validation_hooks[T](
        self,
        make_strict: Callable[[], T],
        chain: Callable[[T, T], T],
        user_hook: T | None,
    ) -> T | None:
        if not self._strict:
            return user_hook
        strict_hook = make_strict()
        if user_hook is None:
            return strict_hook
        return chain(strict_hook, user_hook)

    def _check_schema_if_strict(self, schema: dict[str, Any]) -> None:
        if not self._strict:
            return
        check_schema(schema)
