"""Tests for mcpk.errors module."""

from __future__ import annotations

import pytest

from mcpk.errors import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    METHOD_NOT_FOUND,
    ExecutionError,
    McpkError,
    PermissionDeniedError,
    PromptNotFoundError,
    ResourceNotFoundError,
    ToolNotFoundError,
    ValidationError,
)


@pytest.mark.parametrize(
    ("message", "code", "data"),
    [
        ("test error", 100, None),
        ("another error", -32600, {"key": "value"}),
        ("with data", INTERNAL_ERROR, [1, 2, 3]),
    ],
)
def test_mcpk_error_init(message: str, code: int, data: object) -> None:
    err = McpkError(message, code, data)

    assert str(err) == message
    assert err.message == message
    assert err.code == code
    assert err.data == data


@pytest.mark.parametrize(
    "name",
    ["my_tool", "another-tool", "tool.with.dots"],
)
def test_tool_not_found_error(name: str) -> None:
    err = ToolNotFoundError(name)

    assert err.name == name
    assert err.code == METHOD_NOT_FOUND
    assert name in str(err)


@pytest.mark.parametrize(
    "uri",
    ["file:///path/to/file", "http://example.com", "custom://resource"],
)
def test_resource_not_found_error(uri: str) -> None:
    err = ResourceNotFoundError(uri)

    assert err.uri == uri
    assert err.code == METHOD_NOT_FOUND
    assert uri in str(err)


@pytest.mark.parametrize(
    "name",
    ["my_prompt", "greeting-prompt", "prompt.name"],
)
def test_prompt_not_found_error(name: str) -> None:
    err = PromptNotFoundError(name)

    assert err.name == name
    assert err.code == METHOD_NOT_FOUND
    assert name in str(err)


@pytest.mark.parametrize(
    "message",
    ["Invalid input", "Missing required field 'name'", "Type mismatch"],
)
def test_validation_error(message: str) -> None:
    err = ValidationError(message)

    assert str(err) == message
    assert err.code == INVALID_PARAMS


@pytest.mark.parametrize(
    "reason",
    ["access denied", "not authorized", "rate limited"],
)
def test_permission_denied_error(reason: str) -> None:
    err = PermissionDeniedError(reason)

    assert err.reason == reason
    assert err.code == INTERNAL_ERROR
    assert reason in str(err)


@pytest.mark.parametrize(
    ("message", "cause"),
    [
        ("Tool failed", ValueError("bad value")),
        ("Handler error", RuntimeError("unexpected")),
        ("No cause", None),
    ],
)
def test_execution_error(message: str, cause: Exception | None) -> None:
    err = ExecutionError(message, cause)

    assert str(err) == message
    assert err.code == INTERNAL_ERROR
    assert err.__cause__ is cause


def test_error_inheritance() -> None:
    assert issubclass(ToolNotFoundError, McpkError)
    assert issubclass(ResourceNotFoundError, McpkError)
    assert issubclass(PromptNotFoundError, McpkError)
    assert issubclass(ValidationError, McpkError)
    assert issubclass(PermissionDeniedError, McpkError)
    assert issubclass(ExecutionError, McpkError)
    assert issubclass(McpkError, Exception)
