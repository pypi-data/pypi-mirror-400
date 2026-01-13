from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionScope[ContextT]:
    """Wraps user-defined context with execution metadata.

    Attributes:
        ctx: User-defined context (can be any type)
        request_id: Optional request correlation ID
        progress_token: Token for progress notifications
        extensions: Extensible metadata dict (like httpcore)
    """

    ctx: ContextT
    request_id: str | None = None
    progress_token: str | int | None = None
    extensions: dict[str, Any] | None = None


# =============================================================================
# Capability Definitions
# =============================================================================


@dataclass(frozen=True, slots=True)
class ToolAnnotationsDef:
    """Tool annotation hints.

    All fields are optional hints - not guaranteed to be accurate.
    """

    title: str | None = None
    read_only_hint: bool | None = None
    destructive_hint: bool | None = None
    idempotent_hint: bool | None = None
    open_world_hint: bool | None = None


@dataclass(frozen=True, slots=True)
class ToolDef:
    """Tool definition for registration.

    Attributes:
        name: Unique tool identifier
        input_schema: JSON Schema for input validation
        description: Human-readable description
        output_schema: Optional JSON Schema for structured output
        annotations: Optional tool hints
    """

    name: str
    input_schema: dict[str, Any]
    description: str | None = None
    output_schema: dict[str, Any] | None = None
    annotations: ToolAnnotationsDef | None = None


@dataclass(frozen=True, slots=True)
class ResourceDef:
    """Resource definition for registration.

    Attributes:
        uri: Resource URI (unique identifier)
        name: Human-readable name
        description: Optional description
        mime_type: Optional MIME type hint
    """

    uri: str
    name: str
    description: str | None = None
    mime_type: str | None = None


@dataclass(frozen=True, slots=True)
class PromptArgumentDef:
    """Prompt argument definition.

    Attributes:
        name: Argument name
        description: Optional description
        required: Whether the argument is required
    """

    name: str
    description: str | None = None
    required: bool = False


@dataclass(frozen=True, slots=True)
class PromptDef:
    """Prompt definition for registration.

    Attributes:
        name: Unique prompt identifier
        description: Optional description
        arguments: Optional tuple of argument definitions
    """

    name: str
    description: str | None = None
    arguments: tuple[PromptArgumentDef, ...] | None = None


# =============================================================================
# Content Items
# =============================================================================


@dataclass(frozen=True, slots=True)
class TextItem:
    """Text content item."""

    text: str


@dataclass(frozen=True, slots=True)
class ImageItem:
    """Image content item.

    Attributes:
        data: Raw image bytes
        mime_type: Image MIME type (e.g., "image/png")
    """

    data: bytes
    mime_type: str


@dataclass(frozen=True, slots=True)
class AudioItem:
    """Audio content item.

    Attributes:
        data: Raw audio bytes
        mime_type: Audio MIME type (e.g., "audio/wav")
    """

    data: bytes
    mime_type: str


@dataclass(frozen=True, slots=True)
class ResourceContent:
    """Resource content (text or blob).

    Either text or blob should be set, not both.

    Attributes:
        uri: Resource URI
        text: Text content (mutually exclusive with blob)
        blob: Binary content (mutually exclusive with text)
        mime_type: Optional MIME type
    """

    uri: str
    text: str | None = None
    blob: bytes | None = None
    mime_type: str | None = None


@dataclass(frozen=True, slots=True)
class EmbeddedResourceItem:
    """Embedded resource in content."""

    resource: ResourceContent


@dataclass(frozen=True, slots=True)
class ResourceLinkItem:
    """Resource link in content.

    Attributes:
        uri: Resource URI
        name: Human-readable name
        description: Optional description
        mime_type: Optional MIME type hint
    """

    uri: str
    name: str
    description: str | None = None
    mime_type: str | None = None


ContentItem = TextItem | ImageItem | AudioItem | EmbeddedResourceItem | ResourceLinkItem


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Result from tool execution.

    Attributes:
        content: Tuple of content items
        structured_content: Optional structured JSON output
        is_error: Whether this result represents an error
    """

    content: tuple[ContentItem, ...]
    structured_content: dict[str, Any] | None = None
    is_error: bool = False


@dataclass(frozen=True, slots=True)
class ResourceResult:
    """Result from resource read.

    Attributes:
        contents: Tuple of resource contents
    """

    contents: tuple[ResourceContent, ...]


@dataclass(frozen=True, slots=True)
class PromptMessage:
    """Message in a prompt result.

    Attributes:
        role: Message role ("user" or "assistant")
        content: Message content
    """

    role: str  # "user" | "assistant"
    content: ContentItem


@dataclass(frozen=True, slots=True)
class PromptResult:
    """Result from prompt get.

    Attributes:
        messages: Tuple of prompt messages
        description: Optional description
    """

    messages: tuple[PromptMessage, ...]
    description: str | None = None


# =============================================================================
# Handler Types
# =============================================================================

type ToolHandler[ContextT] = Callable[[ExecutionScope[ContextT], dict[str, Any]], ToolResult]
type ResourceHandler[ContextT] = Callable[[ExecutionScope[ContextT], str], ResourceResult]
type PromptHandler[ContextT] = Callable[[ExecutionScope[ContextT], dict[str, str]], PromptResult]
type AsyncToolHandler[ContextT] = Callable[
    [ExecutionScope[ContextT], dict[str, Any]], Awaitable[ToolResult]
]
type AsyncResourceHandler[ContextT] = Callable[
    [ExecutionScope[ContextT], str], Awaitable[ResourceResult]
]
type AsyncPromptHandler[ContextT] = Callable[
    [ExecutionScope[ContextT], dict[str, str]], Awaitable[PromptResult]
]
