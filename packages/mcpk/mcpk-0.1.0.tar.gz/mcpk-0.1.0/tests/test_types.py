"""Tests for mcpk.types module."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from mcpk.types import (
    AudioItem,
    EmbeddedResourceItem,
    ExecutionScope,
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
# ExecutionScope Tests
# =============================================================================


@pytest.mark.parametrize(
    ("ctx", "request_id", "progress_token", "extensions"),
    [
        ("simple_ctx", None, None, None),
        ({"user": "alice"}, "req-123", "prog-456", {"meta": "data"}),
        (123, "req", 789, {}),
        (None, None, 0, None),
    ],
)
def test_execution_scope_init(
    ctx: Any,
    request_id: str | None,
    progress_token: str | int | None,
    extensions: dict[str, Any] | None,
) -> None:
    scope = ExecutionScope(
        ctx=ctx,
        request_id=request_id,
        progress_token=progress_token,
        extensions=extensions,
    )

    assert scope.ctx == ctx
    assert scope.request_id == request_id
    assert scope.progress_token == progress_token
    assert scope.extensions == extensions


def test_execution_scope_frozen() -> None:
    scope = ExecutionScope(ctx="test")

    with pytest.raises(FrozenInstanceError):
        scope.ctx = "new"  # type: ignore[misc]


def test_execution_scope_defaults() -> None:
    scope = ExecutionScope(ctx="test")

    assert scope.request_id is None
    assert scope.progress_token is None
    assert scope.extensions is None


# =============================================================================
# ToolAnnotationsDef Tests
# =============================================================================


@pytest.mark.parametrize(
    ("title", "read_only", "destructive", "idempotent", "open_world"),
    [
        (None, None, None, None, None),
        ("My Tool", True, False, True, False),
        ("Dangerous", False, True, False, True),
    ],
)
def test_tool_annotations_def(
    title: str | None,
    read_only: bool | None,
    destructive: bool | None,
    idempotent: bool | None,
    open_world: bool | None,
) -> None:
    ann = ToolAnnotationsDef(
        title=title,
        read_only_hint=read_only,
        destructive_hint=destructive,
        idempotent_hint=idempotent,
        open_world_hint=open_world,
    )

    assert ann.title == title
    assert ann.read_only_hint == read_only
    assert ann.destructive_hint == destructive
    assert ann.idempotent_hint == idempotent
    assert ann.open_world_hint == open_world


# =============================================================================
# ToolDef Tests
# =============================================================================


@pytest.mark.parametrize(
    ("name", "input_schema", "description", "output_schema"),
    [
        ("simple_tool", {"type": "object"}, None, None),
        (
            "complex_tool",
            {"type": "object", "properties": {"x": {"type": "integer"}}},
            "A complex tool",
            {"type": "string"},
        ),
    ],
)
def test_tool_def(
    name: str,
    input_schema: dict[str, Any],
    description: str | None,
    output_schema: dict[str, Any] | None,
) -> None:
    tool = ToolDef(
        name=name,
        input_schema=input_schema,
        description=description,
        output_schema=output_schema,
    )

    assert tool.name == name
    assert tool.input_schema == input_schema
    assert tool.description == description
    assert tool.output_schema == output_schema
    assert tool.annotations is None


def test_tool_def_with_annotations() -> None:
    ann = ToolAnnotationsDef(title="Test", read_only_hint=True)
    tool = ToolDef(
        name="annotated",
        input_schema={"type": "object"},
        annotations=ann,
    )

    assert tool.annotations == ann


# =============================================================================
# ResourceDef Tests
# =============================================================================


@pytest.mark.parametrize(
    ("uri", "name", "description", "mime_type"),
    [
        ("file:///test", "Test File", None, None),
        ("http://api.com/data", "API Data", "JSON data source", "application/json"),
        ("custom://resource", "Custom", "Custom resource", "text/plain"),
    ],
)
def test_resource_def(
    uri: str,
    name: str,
    description: str | None,
    mime_type: str | None,
) -> None:
    resource = ResourceDef(
        uri=uri,
        name=name,
        description=description,
        mime_type=mime_type,
    )

    assert resource.uri == uri
    assert resource.name == name
    assert resource.description == description
    assert resource.mime_type == mime_type


# =============================================================================
# PromptArgumentDef Tests
# =============================================================================


@pytest.mark.parametrize(
    ("name", "description", "required"),
    [
        ("arg1", None, False),
        ("required_arg", "A required argument", True),
        ("optional", "Optional arg", False),
    ],
)
def test_prompt_argument_def(
    name: str,
    description: str | None,
    required: bool,
) -> None:
    arg = PromptArgumentDef(name=name, description=description, required=required)

    assert arg.name == name
    assert arg.description == description
    assert arg.required == required


# =============================================================================
# PromptDef Tests
# =============================================================================


@pytest.mark.parametrize(
    ("name", "description"),
    [
        ("simple_prompt", None),
        ("described_prompt", "A helpful prompt"),
    ],
)
def test_prompt_def(name: str, description: str | None) -> None:
    prompt = PromptDef(name=name, description=description)

    assert prompt.name == name
    assert prompt.description == description
    assert prompt.arguments is None


def test_prompt_def_with_arguments() -> None:
    args = (
        PromptArgumentDef(name="topic", required=True),
        PromptArgumentDef(name="style", required=False),
    )
    prompt = PromptDef(name="writer", arguments=args)

    assert prompt.arguments == args


# =============================================================================
# Content Items Tests
# =============================================================================


@pytest.mark.parametrize(
    "text",
    ["Hello", "Multi\nline\ntext", ""],
)
def test_text_item(text: str) -> None:
    item = TextItem(text=text)
    assert item.text == text


@pytest.mark.parametrize(
    ("data", "mime_type"),
    [
        (b"\x89PNG\r\n", "image/png"),
        (b"\xff\xd8\xff", "image/jpeg"),
        (b"GIF89a", "image/gif"),
    ],
)
def test_image_item(data: bytes, mime_type: str) -> None:
    item = ImageItem(data=data, mime_type=mime_type)

    assert item.data == data
    assert item.mime_type == mime_type


@pytest.mark.parametrize(
    ("data", "mime_type"),
    [
        (b"RIFF", "audio/wav"),
        (b"\xff\xfb", "audio/mp3"),
        (b"OggS", "audio/ogg"),
    ],
)
def test_audio_item(data: bytes, mime_type: str) -> None:
    item = AudioItem(data=data, mime_type=mime_type)

    assert item.data == data
    assert item.mime_type == mime_type


@pytest.mark.parametrize(
    ("uri", "text", "blob", "mime_type"),
    [
        ("file:///test.txt", "content", None, "text/plain"),
        ("file:///test.bin", None, b"binary", "application/octet-stream"),
        ("file:///nomine", "data", None, None),
    ],
)
def test_resource_content(
    uri: str,
    text: str | None,
    blob: bytes | None,
    mime_type: str | None,
) -> None:
    content = ResourceContent(uri=uri, text=text, blob=blob, mime_type=mime_type)

    assert content.uri == uri
    assert content.text == text
    assert content.blob == blob
    assert content.mime_type == mime_type


def test_embedded_resource_item() -> None:
    resource = ResourceContent(uri="test://uri", text="content")
    item = EmbeddedResourceItem(resource=resource)

    assert item.resource == resource


@pytest.mark.parametrize(
    ("uri", "name", "description", "mime_type"),
    [
        ("file:///link", "Link", None, None),
        ("http://example.com", "Example", "A link", "text/html"),
    ],
)
def test_resource_link_item(
    uri: str,
    name: str,
    description: str | None,
    mime_type: str | None,
) -> None:
    item = ResourceLinkItem(uri=uri, name=name, description=description, mime_type=mime_type)

    assert item.uri == uri
    assert item.name == name
    assert item.description == description
    assert item.mime_type == mime_type


# =============================================================================
# Result Types Tests
# =============================================================================


@pytest.mark.parametrize(
    ("content", "structured_content", "is_error"),
    [
        ((TextItem(text="result"),), None, False),
        ((TextItem(text="error"),), None, True),
        ((TextItem(text="data"),), {"key": "value"}, False),
        ((), None, False),
    ],
)
def test_tool_result(
    content: tuple[TextItem, ...],
    structured_content: dict[str, Any] | None,
    is_error: bool,
) -> None:
    result = ToolResult(
        content=content,
        structured_content=structured_content,
        is_error=is_error,
    )

    assert result.content == content
    assert result.structured_content == structured_content
    assert result.is_error == is_error


def test_resource_result() -> None:
    contents = (
        ResourceContent(uri="file:///a", text="a"),
        ResourceContent(uri="file:///b", text="b"),
    )
    result = ResourceResult(contents=contents)

    assert result.contents == contents


@pytest.mark.parametrize(
    ("role", "content"),
    [
        ("user", TextItem(text="Hello")),
        ("assistant", TextItem(text="Hi there")),
    ],
)
def test_prompt_message(role: str, content: TextItem) -> None:
    msg = PromptMessage(role=role, content=content)

    assert msg.role == role
    assert msg.content == content


def test_prompt_result() -> None:
    messages = (
        PromptMessage(role="user", content=TextItem(text="Question")),
        PromptMessage(role="assistant", content=TextItem(text="Answer")),
    )
    result = PromptResult(messages=messages, description="A Q&A")

    assert result.messages == messages
    assert result.description == "A Q&A"


def test_prompt_result_no_description() -> None:
    messages = (PromptMessage(role="user", content=TextItem(text="Hi")),)
    result = PromptResult(messages=messages)

    assert result.description is None
