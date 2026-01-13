"""Tests for mcpk._enforce module."""

from __future__ import annotations

import pytest

from mcpk._enforce import (
    enforce_prompt_def,
    enforce_prompt_result,
    enforce_resource_def,
    enforce_resource_result,
    enforce_tool_def,
    enforce_tool_result,
)
from mcpk.errors import SpecError
from mcpk.types import (
    AudioItem,
    EmbeddedResourceItem,
    ImageItem,
    PromptArgumentDef,
    PromptDef,
    PromptMessage,
    PromptResult,
    ResourceContent,
    ResourceDef,
    ResourceLinkItem,
    ResourceResult,
    TextItem,
    ToolAnnotationsDef,
    ToolDef,
    ToolResult,
)

# =============================================================================
# Tool Definition Tests
# =============================================================================


def test_enforce_tool_def_valid() -> None:
    tool = ToolDef(name="my_tool", input_schema={"type": "object"})
    enforce_tool_def(tool)  # Should not raise


def test_enforce_tool_def_empty_name() -> None:
    tool = ToolDef(name="", input_schema={"type": "object"})
    with pytest.raises(SpecError, match="Tool name must be non-empty"):
        enforce_tool_def(tool)


def test_enforce_tool_def_input_schema_not_dict() -> None:
    tool = ToolDef(name="tool", input_schema=["not", "a", "dict"])  # type: ignore[arg-type]
    with pytest.raises(SpecError, match="Tool input_schema must be a dict"):
        enforce_tool_def(tool)


def test_enforce_tool_def_input_schema_missing_type() -> None:
    tool = ToolDef(name="tool", input_schema={"properties": {}})
    with pytest.raises(SpecError, match="Tool input_schema must have 'type' key"):
        enforce_tool_def(tool)


def test_enforce_tool_def_output_schema_not_dict() -> None:
    tool = ToolDef(
        name="tool",
        input_schema={"type": "object"},
        output_schema="not a dict",  # type: ignore[arg-type]
    )
    with pytest.raises(SpecError, match="Tool output_schema must be a dict"):
        enforce_tool_def(tool)


def test_enforce_tool_def_with_valid_output_schema() -> None:
    tool = ToolDef(
        name="tool",
        input_schema={"type": "object"},
        output_schema={"type": "string"},
    )
    enforce_tool_def(tool)  # Should not raise


def test_enforce_tool_def_with_annotations() -> None:
    tool = ToolDef(
        name="tool",
        input_schema={"type": "object"},
        annotations=ToolAnnotationsDef(title="My Tool", read_only_hint=True),
    )
    enforce_tool_def(tool)  # Should not raise


# =============================================================================
# Resource Definition Tests
# =============================================================================


def test_enforce_resource_def_valid() -> None:
    resource = ResourceDef(uri="file:///test", name="Test")
    enforce_resource_def(resource)  # Should not raise


def test_enforce_resource_def_empty_uri() -> None:
    resource = ResourceDef(uri="", name="Test")
    with pytest.raises(SpecError, match="Resource URI must be non-empty"):
        enforce_resource_def(resource)


def test_enforce_resource_def_invalid_uri_format() -> None:
    resource = ResourceDef(uri="no-scheme-here", name="Test")
    with pytest.raises(SpecError, match="is not a valid URI format"):
        enforce_resource_def(resource)


def test_enforce_resource_def_empty_name() -> None:
    resource = ResourceDef(uri="file:///test", name="")
    with pytest.raises(SpecError, match="Resource name must be non-empty"):
        enforce_resource_def(resource)


def test_enforce_resource_def_invalid_mime_type() -> None:
    resource = ResourceDef(uri="file:///test", name="Test", mime_type="invalid")
    with pytest.raises(SpecError, match="is not a valid MIME type"):
        enforce_resource_def(resource)


def test_enforce_resource_def_valid_mime_type() -> None:
    resource = ResourceDef(uri="file:///test", name="Test", mime_type="text/plain")
    enforce_resource_def(resource)  # Should not raise


# =============================================================================
# Prompt Definition Tests
# =============================================================================


def test_enforce_prompt_def_valid() -> None:
    prompt = PromptDef(name="greeting")
    enforce_prompt_def(prompt)  # Should not raise


def test_enforce_prompt_def_empty_name() -> None:
    prompt = PromptDef(name="")
    with pytest.raises(SpecError, match="Prompt name must be non-empty"):
        enforce_prompt_def(prompt)


def test_enforce_prompt_def_with_valid_arguments() -> None:
    prompt = PromptDef(
        name="greeting",
        arguments=(PromptArgumentDef(name="topic", required=True),),
    )
    enforce_prompt_def(prompt)  # Should not raise


def test_enforce_prompt_def_argument_empty_name() -> None:
    prompt = PromptDef(
        name="greeting",
        arguments=(PromptArgumentDef(name="", required=True),),
    )
    with pytest.raises(SpecError, match="Prompt argument name must be non-empty"):
        enforce_prompt_def(prompt)


# =============================================================================
# Tool Result Tests
# =============================================================================


def test_enforce_tool_result_valid() -> None:
    result = ToolResult(content=(TextItem(text="ok"),))
    enforce_tool_result(result)  # Should not raise


def test_enforce_tool_result_empty_content() -> None:
    result = ToolResult(content=())
    with pytest.raises(SpecError, match="Tool result content must be non-empty"):
        enforce_tool_result(result)


def test_enforce_tool_result_with_image() -> None:
    result = ToolResult(content=(ImageItem(data=b"PNG", mime_type="image/png"),))
    enforce_tool_result(result)  # Should not raise


def test_enforce_tool_result_with_audio() -> None:
    result = ToolResult(content=(AudioItem(data=b"audio", mime_type="audio/wav"),))
    enforce_tool_result(result)  # Should not raise


def test_enforce_tool_result_with_embedded_resource() -> None:
    result = ToolResult(
        content=(
            EmbeddedResourceItem(
                resource=ResourceContent(uri="file:///test", text="content")
            ),
        )
    )
    enforce_tool_result(result)  # Should not raise


def test_enforce_tool_result_with_resource_link() -> None:
    result = ToolResult(
        content=(ResourceLinkItem(uri="file:///link", name="Link"),)
    )
    enforce_tool_result(result)  # Should not raise


# =============================================================================
# Resource Result Tests
# =============================================================================


def test_enforce_resource_result_valid() -> None:
    result = ResourceResult(contents=(ResourceContent(uri="file:///test", text="data"),))
    enforce_resource_result(result)  # Should not raise


def test_enforce_resource_result_empty_contents() -> None:
    result = ResourceResult(contents=())
    with pytest.raises(SpecError, match="Resource result contents must be non-empty"):
        enforce_resource_result(result)


def test_enforce_resource_result_with_blob() -> None:
    result = ResourceResult(contents=(ResourceContent(uri="file:///bin", blob=b"data"),))
    enforce_resource_result(result)  # Should not raise


# =============================================================================
# Prompt Result Tests
# =============================================================================


def test_enforce_prompt_result_valid() -> None:
    result = PromptResult(
        messages=(PromptMessage(role="user", content=TextItem(text="hi")),)
    )
    enforce_prompt_result(result)  # Should not raise


def test_enforce_prompt_result_empty_messages() -> None:
    result = PromptResult(messages=())
    with pytest.raises(SpecError, match="Prompt result messages must be non-empty"):
        enforce_prompt_result(result)


def test_enforce_prompt_result_assistant_role() -> None:
    result = PromptResult(
        messages=(PromptMessage(role="assistant", content=TextItem(text="hello")),)
    )
    enforce_prompt_result(result)  # Should not raise


def test_enforce_prompt_result_invalid_role() -> None:
    result = PromptResult(
        messages=(PromptMessage(role="system", content=TextItem(text="hi")),)  # type: ignore[arg-type]
    )
    with pytest.raises(SpecError, match="must be 'user' or 'assistant'"):
        enforce_prompt_result(result)


# =============================================================================
# Text Item Tests
# =============================================================================


def test_enforce_text_item_not_string() -> None:
    result = ToolResult(content=(TextItem(text=123),))  # type: ignore[arg-type]
    with pytest.raises(SpecError, match="TextItem.text must be a string"):
        enforce_tool_result(result)


# =============================================================================
# Image Item Tests
# =============================================================================


def test_enforce_image_item_data_not_bytes() -> None:
    result = ToolResult(content=(ImageItem(data="not bytes", mime_type="image/png"),))  # type: ignore[arg-type]
    with pytest.raises(SpecError, match="ImageItem.data must be bytes"):
        enforce_tool_result(result)


def test_enforce_image_item_invalid_mime() -> None:
    result = ToolResult(content=(ImageItem(data=b"data", mime_type="invalid"),))
    with pytest.raises(SpecError, match="is not a valid MIME type"):
        enforce_tool_result(result)


def test_enforce_image_item_wrong_mime_prefix() -> None:
    result = ToolResult(content=(ImageItem(data=b"data", mime_type="audio/mp3"),))
    with pytest.raises(SpecError, match="must start with 'image/'"):
        enforce_tool_result(result)


# =============================================================================
# Audio Item Tests
# =============================================================================


def test_enforce_audio_item_data_not_bytes() -> None:
    result = ToolResult(content=(AudioItem(data="not bytes", mime_type="audio/wav"),))  # type: ignore[arg-type]
    with pytest.raises(SpecError, match="AudioItem.data must be bytes"):
        enforce_tool_result(result)


def test_enforce_audio_item_invalid_mime() -> None:
    result = ToolResult(content=(AudioItem(data=b"data", mime_type="invalid"),))
    with pytest.raises(SpecError, match="is not a valid MIME type"):
        enforce_tool_result(result)


def test_enforce_audio_item_wrong_mime_prefix() -> None:
    result = ToolResult(content=(AudioItem(data=b"data", mime_type="image/png"),))
    with pytest.raises(SpecError, match="must start with 'audio/'"):
        enforce_tool_result(result)


# =============================================================================
# Resource Link Item Tests
# =============================================================================


def test_enforce_resource_link_empty_uri() -> None:
    result = ToolResult(content=(ResourceLinkItem(uri="", name="Link"),))
    with pytest.raises(SpecError, match="ResourceLinkItem.uri must be non-empty"):
        enforce_tool_result(result)


def test_enforce_resource_link_invalid_uri() -> None:
    result = ToolResult(content=(ResourceLinkItem(uri="no-scheme", name="Link"),))
    with pytest.raises(SpecError, match="is not a valid URI format"):
        enforce_tool_result(result)


def test_enforce_resource_link_empty_name() -> None:
    result = ToolResult(content=(ResourceLinkItem(uri="file:///test", name=""),))
    with pytest.raises(SpecError, match="ResourceLinkItem.name must be non-empty"):
        enforce_tool_result(result)


def test_enforce_resource_link_invalid_mime() -> None:
    result = ToolResult(
        content=(ResourceLinkItem(uri="file:///test", name="Link", mime_type="bad"),)
    )
    with pytest.raises(SpecError, match="is not a valid MIME type"):
        enforce_tool_result(result)


def test_enforce_resource_link_valid_mime() -> None:
    result = ToolResult(
        content=(
            ResourceLinkItem(uri="file:///test", name="Link", mime_type="text/html"),
        )
    )
    enforce_tool_result(result)  # Should not raise


# =============================================================================
# Resource Content Tests
# =============================================================================


def test_enforce_resource_content_empty_uri() -> None:
    result = ResourceResult(contents=(ResourceContent(uri="", text="data"),))
    with pytest.raises(SpecError, match="ResourceContent.uri must be non-empty"):
        enforce_resource_result(result)


def test_enforce_resource_content_invalid_uri() -> None:
    result = ResourceResult(contents=(ResourceContent(uri="bad-uri", text="data"),))
    with pytest.raises(SpecError, match="is not a valid URI format"):
        enforce_resource_result(result)


def test_enforce_resource_content_neither_text_nor_blob() -> None:
    result = ResourceResult(contents=(ResourceContent(uri="file:///test"),))
    with pytest.raises(SpecError, match="must have either text or blob"):
        enforce_resource_result(result)


def test_enforce_resource_content_both_text_and_blob() -> None:
    result = ResourceResult(
        contents=(ResourceContent(uri="file:///test", text="data", blob=b"data"),)
    )
    with pytest.raises(SpecError, match="must have either text or blob, not both"):
        enforce_resource_result(result)


def test_enforce_resource_content_invalid_mime() -> None:
    result = ResourceResult(
        contents=(ResourceContent(uri="file:///test", text="data", mime_type="bad"),)
    )
    with pytest.raises(SpecError, match="is not a valid MIME type"):
        enforce_resource_result(result)


def test_enforce_resource_content_valid_mime() -> None:
    result = ResourceResult(
        contents=(
            ResourceContent(uri="file:///test", text="data", mime_type="text/plain"),
        )
    )
    enforce_resource_result(result)  # Should not raise


# =============================================================================
# Embedded Resource Tests
# =============================================================================


def test_enforce_embedded_resource_invalid_content() -> None:
    result = ToolResult(
        content=(
            EmbeddedResourceItem(resource=ResourceContent(uri="", text="data")),
        )
    )
    with pytest.raises(SpecError, match="ResourceContent.uri must be non-empty"):
        enforce_tool_result(result)


# =============================================================================
# URI Validation Tests
# =============================================================================


@pytest.mark.parametrize(
    "uri",
    [
        "file:///path/to/file",
        "http://example.com",
        "https://example.com/path",
        "custom://resource",
        "a:b",  # Minimal valid URI
        "scheme+sub.type-2:content",
    ],
)
def test_valid_uri_formats(uri: str) -> None:
    resource = ResourceDef(uri=uri, name="Test")
    enforce_resource_def(resource)  # Should not raise


@pytest.mark.parametrize(
    "uri",
    [
        "no-scheme",
        "/path/only",
        "://missing-scheme",
        "1scheme:invalid",  # Must start with letter
        "",
    ],
)
def test_invalid_uri_formats(uri: str) -> None:
    if not uri:
        return  # Empty URI tested separately
    resource = ResourceDef(uri=uri, name="Test")
    with pytest.raises(SpecError, match="is not a valid URI format"):
        enforce_resource_def(resource)


# =============================================================================
# MIME Type Validation Tests
# =============================================================================


@pytest.mark.parametrize(
    "mime",
    [
        "text/plain",
        "application/json",
        "image/png",
        "audio/wav",
        "text/html; charset=utf-8",
        "application/octet-stream",
    ],
)
def test_valid_mime_types(mime: str) -> None:
    resource = ResourceDef(uri="file:///test", name="Test", mime_type=mime)
    enforce_resource_def(resource)  # Should not raise


@pytest.mark.parametrize(
    "mime",
    [
        "invalid",
        "no-slash",
        "/missing-type",
        "missing-subtype/",
        "",
    ],
)
def test_invalid_mime_types(mime: str) -> None:
    if not mime:
        return  # Empty mime tested as None
    resource = ResourceDef(uri="file:///test", name="Test", mime_type=mime)
    with pytest.raises(SpecError, match="is not a valid MIME type"):
        enforce_resource_def(resource)
