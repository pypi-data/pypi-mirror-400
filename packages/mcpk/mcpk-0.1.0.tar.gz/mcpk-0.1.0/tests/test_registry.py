"""Tests for mcpk._registry module."""

from __future__ import annotations

from typing import Any

import pytest

from mcpk._registry import Registry
from mcpk.errors import SpecError
from mcpk.types import (
    ExecutionScope,
    PromptArgumentDef,
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


def make_tool_handler() -> Any:
    def handler(scope: ExecutionScope[Any], args: dict[str, Any]) -> ToolResult:
        return ToolResult(content=(TextItem(text="ok"),))

    return handler


def make_resource_handler() -> Any:
    def handler(scope: ExecutionScope[Any], uri: str) -> ResourceResult:
        return ResourceResult(contents=(ResourceContent(uri=uri, text="content"),))

    return handler


def make_prompt_handler() -> Any:
    def handler(scope: ExecutionScope[Any], args: dict[str, str]) -> PromptResult:
        return PromptResult(messages=(PromptMessage(role="user", content=TextItem(text="hi")),))

    return handler


# =============================================================================
# Tool Registration Tests
# =============================================================================


def test_register_tool_success() -> None:
    registry = Registry()
    tool_def = ToolDef(name="my_tool", input_schema={"type": "object"})
    handler = make_tool_handler()

    registry.register_tool(tool_def, handler)

    result = registry.get_tool("my_tool")
    assert result is not None
    assert result[0] == tool_def
    assert result[1] is handler


def test_register_tool_requires_tool_def() -> None:
    registry = Registry()

    with pytest.raises(TypeError, match="must be a ToolDef"):
        registry.register_tool({"name": "fake"}, make_tool_handler())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("name1", "name2"),
    [
        ("tool_a", "tool_b"),
        ("first", "second"),
    ],
)
def test_register_multiple_tools(name1: str, name2: str) -> None:
    registry = Registry()
    tool1 = ToolDef(name=name1, input_schema={"type": "object"})
    tool2 = ToolDef(name=name2, input_schema={"type": "object"})

    registry.register_tool(tool1, make_tool_handler())
    registry.register_tool(tool2, make_tool_handler())

    assert registry.get_tool(name1) is not None
    assert registry.get_tool(name2) is not None


def test_register_tool_overwrites_existing() -> None:
    registry = Registry()
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})
    handler1 = make_tool_handler()
    handler2 = make_tool_handler()

    registry.register_tool(tool_def, handler1)
    registry.register_tool(tool_def, handler2)

    result = registry.get_tool("tool")
    assert result is not None
    assert result[1] is handler2


def test_get_tool_not_found() -> None:
    registry = Registry()

    assert registry.get_tool("nonexistent") is None


def test_all_tools_empty() -> None:
    registry = Registry()

    assert registry.all_tools() == ()


def test_all_tools_sorted_by_name() -> None:
    registry = Registry()
    tool_z = ToolDef(name="zebra", input_schema={"type": "object"})
    tool_a = ToolDef(name="aardvark", input_schema={"type": "object"})
    tool_m = ToolDef(name="monkey", input_schema={"type": "object"})

    registry.register_tool(tool_z, make_tool_handler())
    registry.register_tool(tool_a, make_tool_handler())
    registry.register_tool(tool_m, make_tool_handler())

    tools = registry.all_tools()
    names = [t.name for t in tools]
    assert names == ["aardvark", "monkey", "zebra"]


# =============================================================================
# Resource Registration Tests
# =============================================================================


def test_register_resource_success() -> None:
    registry = Registry()
    resource_def = ResourceDef(uri="file:///test", name="Test")
    handler = make_resource_handler()

    registry.register_resource(resource_def, handler)

    result = registry.get_resource("file:///test")
    assert result is not None
    assert result[0] == resource_def
    assert result[1] is handler


def test_register_resource_requires_resource_def() -> None:
    registry = Registry()

    with pytest.raises(TypeError, match="must be a ResourceDef"):
        registry.register_resource({"uri": "fake"}, make_resource_handler())  # type: ignore[arg-type]


def test_get_resource_not_found() -> None:
    registry = Registry()

    assert registry.get_resource("file:///nonexistent") is None


def test_all_resources_sorted_by_uri() -> None:
    registry = Registry()
    res_z = ResourceDef(uri="z://last", name="Last")
    res_a = ResourceDef(uri="a://first", name="First")

    registry.register_resource(res_z, make_resource_handler())
    registry.register_resource(res_a, make_resource_handler())

    resources = registry.all_resources()
    uris = [r.uri for r in resources]
    assert uris == ["a://first", "z://last"]


# =============================================================================
# Prompt Registration Tests
# =============================================================================


def test_register_prompt_success() -> None:
    registry = Registry()
    prompt_def = PromptDef(name="greeting")
    handler = make_prompt_handler()

    registry.register_prompt(prompt_def, handler)

    result = registry.get_prompt("greeting")
    assert result is not None
    assert result[0] == prompt_def
    assert result[1] is handler


def test_register_prompt_requires_prompt_def() -> None:
    registry = Registry()

    with pytest.raises(TypeError, match="must be a PromptDef"):
        registry.register_prompt({"name": "fake"}, make_prompt_handler())  # type: ignore[arg-type]


def test_register_prompt_with_arguments() -> None:
    registry = Registry()
    args = (
        PromptArgumentDef(name="topic", required=True),
        PromptArgumentDef(name="style", description="Writing style"),
    )
    prompt_def = PromptDef(name="writer", arguments=args)

    registry.register_prompt(prompt_def, make_prompt_handler())

    result = registry.get_prompt("writer")
    assert result is not None
    assert result[0].arguments == args


def test_get_prompt_not_found() -> None:
    registry = Registry()

    assert registry.get_prompt("nonexistent") is None


def test_all_prompts_sorted_by_name() -> None:
    registry = Registry()
    prompt_z = PromptDef(name="zulu")
    prompt_a = PromptDef(name="alpha")

    registry.register_prompt(prompt_z, make_prompt_handler())
    registry.register_prompt(prompt_a, make_prompt_handler())

    prompts = registry.all_prompts()
    names = [p.name for p in prompts]
    assert names == ["alpha", "zulu"]


# =============================================================================
# Registry Isolation Tests
# =============================================================================


def test_registries_are_independent() -> None:
    registry1 = Registry()
    registry2 = Registry()
    tool_def = ToolDef(name="tool", input_schema={"type": "object"})

    registry1.register_tool(tool_def, make_tool_handler())

    assert registry1.get_tool("tool") is not None
    assert registry2.get_tool("tool") is None


# =============================================================================
# Validation Error Tests
# =============================================================================


def test_register_tool_invalid_schema_raises_spec_error() -> None:
    registry = Registry()
    # input_schema must be a dict, not a list
    tool_def = ToolDef(name="bad_tool", input_schema=["not", "a", "dict"])  # type: ignore[arg-type]

    with pytest.raises(SpecError):
        registry.register_tool(tool_def, make_tool_handler())
