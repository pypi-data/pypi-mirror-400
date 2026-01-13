"""MCPK - A transport-agnostic kernel for MCP servers."""

from mcpk.kernel import AsyncKernel, Kernel
from mcpk.types import (
    AudioItem,
    ContentItem,
    EmbeddedResourceItem,
    ExecutionScope,
    ImageItem,
    PromptDef,
    PromptResult,
    ResourceDef,
    ResourceLinkItem,
    ResourceResult,
    TextItem,
    ToolDef,
    ToolResult,
)

__all__ = [
    # Kernels
    "Kernel",
    "AsyncKernel",
    # Scope
    "ExecutionScope",
    # Definitions
    "ToolDef",
    "ResourceDef",
    "PromptDef",
    # Results
    "ToolResult",
    "ResourceResult",
    "PromptResult",
    # Common content
    "ContentItem",
    "TextItem",
    "ImageItem",
    "AudioItem",
    "EmbeddedResourceItem",
    "ResourceLinkItem",
]
