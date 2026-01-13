"""MCPK hook types.

Hooks allow adapters to inject custom behavior for permissions and validation.
Permission hooks raise PermissionDeniedError to deny access.
Validation hooks raise ValidationError for invalid input.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from mcpk.types import ExecutionScope

type Kind = Literal["tool", "resource", "prompt"]


@dataclass(frozen=True, slots=True)
class PermissionRequest:
    """Details about what permission is being requested.

    Attributes:
        kind: Type of capability being accessed
        name: Tool name, resource URI, or prompt name
        arguments: Arguments for tools/prompts (None for resources)
    """

    kind: Kind
    name: str
    arguments: dict[str, Any] | None = None


type PermissionHook[ContextT] = Callable[[ExecutionScope[ContextT], PermissionRequest], None]
type AsyncPermissionHook[ContextT] = Callable[
    [ExecutionScope[ContextT], PermissionRequest], Awaitable[None]
]

# Sync validation hook - raises ValidationError if validation fails
# Args: (tool_name, arguments, input_schema)
ValidationHook = Callable[[str, dict[str, Any], dict[str, Any]], None]
AsyncValidationHook = Callable[[str, dict[str, Any], dict[str, Any]], Awaitable[None]]
