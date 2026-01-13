"""Tests for mcpk.hooks module."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any, Literal

import pytest

from mcpk.hooks import PermissionRequest


@pytest.mark.parametrize(
    "kind",
    ["tool", "resource", "prompt"],
)
def test_permission_request_kinds(kind: Literal["tool", "resource", "prompt"]) -> None:
    req = PermissionRequest(kind=kind, name="test")

    assert req.kind == kind
    assert req.name == "test"
    assert req.arguments is None


@pytest.mark.parametrize(
    ("kind", "name", "arguments"),
    [
        ("tool", "my_tool", {"x": 1, "y": 2}),
        ("prompt", "greeting", {"name": "Alice"}),
        ("resource", "file:///path", None),
        ("tool", "no_args", {}),
    ],
)
def test_permission_request_with_arguments(
    kind: Literal["tool", "resource", "prompt"],
    name: str,
    arguments: dict[str, Any] | None,
) -> None:
    req = PermissionRequest(kind=kind, name=name, arguments=arguments)

    assert req.kind == kind
    assert req.name == name
    assert req.arguments == arguments


def test_permission_request_is_frozen() -> None:
    req = PermissionRequest(kind="tool", name="test")

    with pytest.raises(FrozenInstanceError):
        req.kind = "resource"  # type: ignore[misc]


def test_permission_request_equality() -> None:
    req1 = PermissionRequest(kind="tool", name="test", arguments={"x": 1})
    req2 = PermissionRequest(kind="tool", name="test", arguments={"x": 1})
    req3 = PermissionRequest(kind="tool", name="test", arguments={"x": 2})

    assert req1 == req2
    assert req1 != req3
