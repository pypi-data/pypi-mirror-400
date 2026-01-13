"""MCP specification compliance enforcement."""

from __future__ import annotations

import re

from mcpk.errors import SpecError
from mcpk.types import (
    AudioItem,
    ContentItem,
    EmbeddedResourceItem,
    ImageItem,
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

# URI must have scheme://... or scheme:...
_URI_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:.+$")

# MIME type must be type/subtype (with optional parameters)
_MIME_PATTERN = re.compile(r"^[a-zA-Z0-9!#$&.+-^_]+/[a-zA-Z0-9!#$&.+-^_]+(;.*)?$")


# =============================================================================
# Definition Enforcement
# =============================================================================


def enforce_tool_def(tool: ToolDef) -> None:
    """Enforce tool definition is MCP spec compliant."""
    if not tool.name:
        raise SpecError("Tool name must be non-empty")

    # Runtime check for callers ignoring type hints (e.g. passing a list)
    if not isinstance(tool.input_schema, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise SpecError("Tool input_schema must be a dict")

    if "type" not in tool.input_schema:
        raise SpecError("Tool input_schema must have 'type' key")

    # Runtime check for callers ignoring type hints
    if tool.output_schema is not None and not isinstance(tool.output_schema, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise SpecError("Tool output_schema must be a dict if provided")

    if tool.annotations is not None:
        _enforce_tool_annotations(tool.annotations)


def enforce_resource_def(resource: ResourceDef) -> None:
    """Enforce resource definition is MCP spec compliant."""
    if not resource.uri:
        raise SpecError("Resource URI must be non-empty")

    if not _is_valid_uri(resource.uri):
        raise SpecError(f"Resource URI '{resource.uri}' is not a valid URI format")

    if not resource.name:
        raise SpecError("Resource name must be non-empty")

    if resource.mime_type is not None and not _is_valid_mime_type(resource.mime_type):
        raise SpecError(f"Resource mime_type '{resource.mime_type}' is not a valid MIME type")


def enforce_prompt_def(prompt: PromptDef) -> None:
    """Enforce prompt definition is MCP spec compliant."""
    if not prompt.name:
        raise SpecError("Prompt name must be non-empty")

    if prompt.arguments is None:
        return

    for arg in prompt.arguments:
        if arg.name:
            continue
        raise SpecError("Prompt argument name must be non-empty")


# =============================================================================
# Result Enforcement
# =============================================================================


def enforce_tool_result(result: ToolResult) -> None:
    """Enforce tool result is MCP spec compliant."""
    if not result.content:
        raise SpecError("Tool result content must be non-empty")

    for item in result.content:
        _enforce_content_item(item)


def enforce_resource_result(result: ResourceResult) -> None:
    """Enforce resource result is MCP spec compliant."""
    if not result.contents:
        raise SpecError("Resource result contents must be non-empty")

    for content in result.contents:
        _enforce_resource_content(content)


def enforce_prompt_result(result: PromptResult) -> None:
    """Enforce prompt result is MCP spec compliant."""
    if not result.messages:
        raise SpecError("Prompt result messages must be non-empty")

    for message in result.messages:
        _enforce_prompt_message(message)


# =============================================================================
# Content Item Enforcement
# =============================================================================


def _enforce_content_item(item: ContentItem) -> None:
    """Enforce content item is MCP spec compliant."""
    if isinstance(item, TextItem):
        _enforce_text_item(item)
    elif isinstance(item, ImageItem):
        _enforce_image_item(item)
    elif isinstance(item, AudioItem):
        _enforce_audio_item(item)
    elif isinstance(item, EmbeddedResourceItem):
        _enforce_embedded_resource(item)
    elif isinstance(item, ResourceLinkItem):  # pyright: ignore[reportUnnecessaryIsInstance] - exhaustiveness check
        _enforce_resource_link(item)
    else:
        raise SpecError(f"Unknown content item type: {type(item).__name__}")  # pragma: no cover


def _enforce_text_item(item: TextItem) -> None:
    """Enforce text item is MCP spec compliant."""
    # Runtime check for callers ignoring type hints
    if not isinstance(item.text, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise SpecError("TextItem.text must be a string")


def _enforce_image_item(item: ImageItem) -> None:
    """Enforce image item is MCP spec compliant."""
    # Runtime check for callers ignoring type hints
    if not isinstance(item.data, bytes):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise SpecError("ImageItem.data must be bytes")

    if not _is_valid_mime_type(item.mime_type):
        raise SpecError(f"ImageItem.mime_type '{item.mime_type}' is not a valid MIME type")

    if not item.mime_type.startswith("image/"):
        raise SpecError(f"ImageItem.mime_type must start with 'image/', got '{item.mime_type}'")


def _enforce_audio_item(item: AudioItem) -> None:
    """Enforce audio item is MCP spec compliant."""
    # Runtime check for callers ignoring type hints
    if not isinstance(item.data, bytes):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise SpecError("AudioItem.data must be bytes")

    if not _is_valid_mime_type(item.mime_type):
        raise SpecError(f"AudioItem.mime_type '{item.mime_type}' is not a valid MIME type")

    if not item.mime_type.startswith("audio/"):
        raise SpecError(f"AudioItem.mime_type must start with 'audio/', got '{item.mime_type}'")


def _enforce_embedded_resource(item: EmbeddedResourceItem) -> None:
    """Enforce embedded resource item is MCP spec compliant."""
    _enforce_resource_content(item.resource)


def _enforce_resource_link(item: ResourceLinkItem) -> None:
    """Enforce resource link item is MCP spec compliant."""
    if not item.uri:
        raise SpecError("ResourceLinkItem.uri must be non-empty")

    if not _is_valid_uri(item.uri):
        raise SpecError(f"ResourceLinkItem.uri '{item.uri}' is not a valid URI format")

    if not item.name:
        raise SpecError("ResourceLinkItem.name must be non-empty")

    if item.mime_type is not None and not _is_valid_mime_type(item.mime_type):
        raise SpecError(f"ResourceLinkItem.mime_type '{item.mime_type}' is not a valid MIME type")


def _enforce_resource_content(content: ResourceContent) -> None:
    """Enforce resource content is MCP spec compliant."""
    if not content.uri:
        raise SpecError("ResourceContent.uri must be non-empty")

    if not _is_valid_uri(content.uri):
        raise SpecError(f"ResourceContent.uri '{content.uri}' is not a valid URI format")

    has_text = content.text is not None
    has_blob = content.blob is not None

    if not has_text and not has_blob:
        raise SpecError("ResourceContent must have either text or blob")

    if has_text and has_blob:
        raise SpecError("ResourceContent must have either text or blob, not both")

    if content.mime_type is not None and not _is_valid_mime_type(content.mime_type):
        raise SpecError(f"ResourceContent.mime_type '{content.mime_type}' is not a valid MIME type")


def _enforce_prompt_message(message: PromptMessage) -> None:
    """Enforce prompt message is MCP spec compliant."""
    if message.role not in ("user", "assistant"):
        raise SpecError(f"PromptMessage.role must be 'user' or 'assistant', got '{message.role}'")

    _enforce_content_item(message.content)


def _enforce_tool_annotations(annotations: ToolAnnotationsDef) -> None:
    """Enforce tool annotations is MCP spec compliant."""
    # All fields are optional booleans/strings, dataclass ensures types
    pass


def _is_valid_uri(uri: str) -> bool:
    """Check if string is a valid URI format."""
    return bool(_URI_PATTERN.match(uri))


def _is_valid_mime_type(mime: str) -> bool:
    """Check if string is a valid MIME type format."""
    return bool(_MIME_PATTERN.match(mime))
