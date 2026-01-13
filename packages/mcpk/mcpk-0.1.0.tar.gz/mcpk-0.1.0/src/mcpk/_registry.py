from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mcpk._enforce import enforce_prompt_def, enforce_resource_def, enforce_tool_def
from mcpk.types import PromptDef, ResourceDef, ToolDef


class Registry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolDef, Any]] = {}
        self._resources: dict[str, tuple[ResourceDef, Any]] = {}
        self._prompts: dict[str, tuple[PromptDef, Any]] = {}

    def register_tool(self, definition: ToolDef, handler: Any) -> None:
        """Register a tool definition and handler."""
        self._validate_definition(definition, ToolDef, enforce_tool_def)
        self._tools[definition.name] = (definition, handler)

    def register_resource(self, definition: ResourceDef, handler: Any) -> None:
        """Register a resource definition and handler."""
        self._validate_definition(definition, ResourceDef, enforce_resource_def)
        self._resources[definition.uri] = (definition, handler)

    def register_prompt(self, definition: PromptDef, handler: Any) -> None:
        """Register a prompt definition and handler."""
        self._validate_definition(definition, PromptDef, enforce_prompt_def)
        self._prompts[definition.name] = (definition, handler)

    def get_tool(self, name: str) -> tuple[ToolDef, Any] | None:
        """Get a tool definition and handler by name."""
        return self._tools.get(name)

    def get_resource(self, uri: str) -> tuple[ResourceDef, Any] | None:
        """Get a resource definition and handler by URI."""
        return self._resources.get(uri)

    def get_prompt(self, name: str) -> tuple[PromptDef, Any] | None:
        """Get a prompt definition and handler by name."""
        return self._prompts.get(name)

    def all_tools(self) -> tuple[ToolDef, ...]:
        """List all registered tool definitions."""
        return tuple(sorted((defn for defn, _ in self._tools.values()), key=lambda d: d.name))

    def all_resources(self) -> tuple[ResourceDef, ...]:
        """List all registered resource definitions."""
        return tuple(sorted((defn for defn, _ in self._resources.values()), key=lambda d: d.uri))

    def all_prompts(self) -> tuple[PromptDef, ...]:
        """List all registered prompt definitions."""
        return tuple(sorted((defn for defn, _ in self._prompts.values()), key=lambda d: d.name))

    def _validate_definition[T](
        self, definition: T, expected_type: type[T], enforcer: Callable[[T], None]
    ) -> None:
        if not isinstance(definition, expected_type):
            raise TypeError(
                f"definition must be a {expected_type.__name__}, got {type(definition)}"
            )
        enforcer(definition)
