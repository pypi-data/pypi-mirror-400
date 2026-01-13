"""MCPK error types.

All errors inherit from McpkError which provides JSON-RPC compatible
error codes for protocol-level error responses.
"""

from __future__ import annotations

from typing import Any

# JSON-RPC error codes (from MCP spec)
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class McpkError(Exception):
    def __init__(self, message: str, code: int, data: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


class ToolNotFoundError(McpkError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Tool not found: {name}", METHOD_NOT_FOUND)
        self.name = name


class ResourceNotFoundError(McpkError):
    def __init__(self, uri: str) -> None:
        super().__init__(f"Resource not found: {uri}", METHOD_NOT_FOUND)
        self.uri = uri


class PromptNotFoundError(McpkError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Prompt not found: {name}", METHOD_NOT_FOUND)
        self.name = name


class ValidationError(McpkError):
    def __init__(self, message: str) -> None:
        super().__init__(message, INVALID_PARAMS)


class PermissionDeniedError(McpkError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Permission denied: {reason}", INTERNAL_ERROR)
        self.reason = reason


class ExecutionError(McpkError):
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__(message, INTERNAL_ERROR)
        self.__cause__ = cause


class SpecError(McpkError):
    """MCP specification compliance error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, INVALID_PARAMS)
