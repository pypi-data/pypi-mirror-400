"""Optional JSON Schema validation for MCPK.

Requires: pip install mcpk[validation]
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from mcpk.errors import ValidationError

# Optional dependency: jsonschema may not be installed
try:
    import jsonschema
    from jsonschema import Draft202012Validator

    HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    # Intentional pattern for optional deps - HAS_JSONSCHEMA is defined in both branches
    HAS_JSONSCHEMA = False  # pyright: ignore[reportConstantRedefinition]

type ValidationHook = Callable[[str, dict[str, Any], dict[str, Any]], None]
type AsyncValidationHook = Callable[[str, dict[str, Any], dict[str, Any]], Awaitable[None]]


def check_schema(schema: dict[str, Any]) -> None:
    """Validate that a schema is a valid JSON Schema.

    Raises:
        ValidationError: If schema is invalid
        ImportError: If jsonschema is not installed
    """
    require_jsonschema()

    try:
        Draft202012Validator.check_schema(schema)  # pyright: ignore[reportPossiblyUnboundVariable]
    except jsonschema.SchemaError as e:  # pyright: ignore[reportPossiblyUnboundVariable]
        raise ValidationError(f"Invalid JSON Schema: {e.message}") from e


def validate_arguments(arguments: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate arguments against a JSON Schema.

    Raises:
        ValidationError: If arguments don't match schema
        ImportError: If jsonschema is not installed
    """
    require_jsonschema()

    try:
        jsonschema.validate(arguments, schema)  # pyright: ignore[reportPossiblyUnboundVariable]
    except jsonschema.ValidationError as e:  # pyright: ignore[reportPossiblyUnboundVariable]
        raise ValidationError(f"Invalid arguments: {e.message}") from e


def make_validation_hook() -> Any:
    """Create a validation hook that validates tool arguments.

    Returns a hook suitable for passing to Kernel(validation_hook=...).

    Raises:
        ImportError: If jsonschema is not installed
    """
    require_jsonschema()

    def hook(name: str, arguments: dict[str, Any], schema: dict[str, Any]) -> None:
        validate_arguments(arguments, schema)

    return hook


def make_async_validation_hook() -> Any:
    """Create an async validation hook that validates tool arguments.

    Returns a hook suitable for passing to AsyncKernel(validation_hook=...).

    Raises:
        ImportError: If jsonschema is not installed
    """
    require_jsonschema()

    async def hook(name: str, arguments: dict[str, Any], schema: dict[str, Any]) -> None:
        validate_arguments(arguments, schema)

    return hook


def chain_validation_hooks(first: ValidationHook, second: ValidationHook) -> ValidationHook:
    """Chain two validation hooks, running first then second."""

    def combined(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        first(name, args, schema)
        second(name, args, schema)

    return combined


def chain_async_validation_hooks(
    first: AsyncValidationHook, second: AsyncValidationHook
) -> AsyncValidationHook:
    """Chain two async validation hooks, running first then second."""

    async def combined(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
        await first(name, args, schema)
        await second(name, args, schema)

    return combined

def require_jsonschema() -> None:
    if HAS_JSONSCHEMA:
        return
    raise ImportError(
        "jsonschema is required for schema validation. "
        "Install with: pip install mcpk[validation]"
    )
