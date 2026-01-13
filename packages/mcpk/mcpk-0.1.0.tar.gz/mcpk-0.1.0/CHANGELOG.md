# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-06

### Added

- `Kernel` and `AsyncKernel` for synchronous and asynchronous MCP server implementations
- Tool registration and execution with `ToolDef`, `ToolResult`, and `call_tool()`
- Resource registration and reading with `ResourceDef`, `ResourceResult`, and `read_resource()`
- Prompt registration and retrieval with `PromptDef`, `PromptResult`, and `get_prompt()`
- Content types: `TextItem`, `ImageItem`, `AudioItem`, `EmbeddedResourceItem`, `ResourceLinkItem`
- Generic `ExecutionScope[ContextT]` for type-safe request context
- Permission hooks for access control (`PermissionHook`, `AsyncPermissionHook`)
- Validation hooks for custom argument validation (`ValidationHook`, `AsyncValidationHook`)
- Event handlers for observability (`ToolCallEvent`, `ResourceReadEvent`, `PromptGetEvent`, `ProgressEvent`, `LogEvent`)
- `emit_progress()` and `emit_log()` for handler-initiated events
- Strict mode (`strict=True`) for JSON Schema validation of tool schemas and arguments
- MCP specification compliance enforcement with `SpecError`
- Error hierarchy with JSON-RPC compatible error codes

[0.1.0]: https://github.com/ahopkins/mcpk/releases/tag/v0.1.0
