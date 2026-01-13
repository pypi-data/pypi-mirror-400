"""Full MCPK example - all capabilities and hooks.

This example demonstrates:
- Custom application context
- All three capability types: tools, resources, prompts
- All three hooks: permission, validation, events
"""

from typing import Any, NamedTuple

from mcpk import (
    ExecutionScope,
    Kernel,
    PromptDef,
    PromptResult,
    ResourceDef,
    ResourceResult,
    TextItem,
    ToolDef,
    ToolResult,
)
from mcpk.errors import PermissionDeniedError, ValidationError
from mcpk.events import Event, PromptGetEvent, ResourceReadEvent, ToolCallEvent
from mcpk.hooks import PermissionRequest
from mcpk.types import PromptArgumentDef, PromptMessage, ResourceContent

# =============================================================================
# Step 1: Define your application context
# =============================================================================
# This can be any type - here we use a NamedTuple with user info.


class AppContext(NamedTuple):
    user_id: str
    is_admin: bool = False


# =============================================================================
# Step 2: Define hooks
# =============================================================================


# Permission hook: called before every tool/resource/prompt execution.
# Raise PermissionDeniedError to block the request.
def check_permission(scope: ExecutionScope[AppContext], req: PermissionRequest) -> None:
    app = scope.ctx  # Extract your app context
    if req.kind == "tool" and req.name == "admin_action":
        if not app.is_admin:
            raise PermissionDeniedError("Admin access required")


# Validation hook: called before tool execution for custom argument validation.
# Raise ValidationError if arguments are invalid.
def validate_args(name: str, args: dict[str, Any], schema: dict[str, Any]) -> None:
    if name == "add":
        if args.get("a", 0) < 0 or args.get("b", 0) < 0:
            raise ValidationError("Arguments must be non-negative")


# Event handler: called before/after/error for observability.
def on_event(event: Event) -> None:
    if isinstance(event, ToolCallEvent):
        print(f"  [{event.phase}] tool:{event.tool_name}")
    elif isinstance(event, ResourceReadEvent):
        print(f"  [{event.phase}] resource:{event.uri}")
    elif isinstance(event, PromptGetEvent):
        print(f"  [{event.phase}] prompt:{event.prompt_name}")


# =============================================================================
# Step 3: Create kernel with hooks
# =============================================================================

kernel: Kernel[AppContext] = Kernel(
    permission_hook=check_permission,
    validation_hook=validate_args,
    event_handler=on_event,
)


# =============================================================================
# Step 4: Register capabilities
# =============================================================================


# Tool: executable function
def add(scope: ExecutionScope[AppContext], args: dict) -> ToolResult:
    result = args["a"] + args["b"]
    return ToolResult(content=(TextItem(text=str(result)),))


kernel.register_tool(
    ToolDef(
        name="add",
        description="Add two non-negative numbers",
        input_schema={
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    ),
    add,
)


# Admin-only tool
def admin_action(scope: ExecutionScope[AppContext], args: dict) -> ToolResult:
    return ToolResult(content=(TextItem(text="Admin action completed"),))


kernel.register_tool(
    ToolDef(name="admin_action", description="Admin only", input_schema={"type": "object"}),
    admin_action,
)


# Resource: readable data source
def read_user(scope: ExecutionScope[AppContext], uri: str) -> ResourceResult:
    app = scope.ctx
    return ResourceResult(contents=(ResourceContent(uri=uri, text=f"User: {app.user_id}"),))


kernel.register_resource(
    ResourceDef(uri="user://current", name="Current User"),
    read_user,
)


# Prompt: message template
def greeting_prompt(scope: ExecutionScope[AppContext], args: dict) -> PromptResult:
    name = args.get("name", "friend")
    return PromptResult(
        messages=(PromptMessage(role="user", content=TextItem(text=f"Say hello to {name}")),)
    )


kernel.register_prompt(
    PromptDef(
        name="greeting",
        description="Generate a greeting",
        arguments=(PromptArgumentDef(name="name", description="Name to greet"),),
    ),
    greeting_prompt,
)


# =============================================================================
# Step 5: Execute with scope
# =============================================================================

if __name__ == "__main__":
    # Create scopes for different users
    user_scope = ExecutionScope(ctx=AppContext(user_id="alice", is_admin=False))
    admin_scope = ExecutionScope(ctx=AppContext(user_id="bob", is_admin=True))

    print("=== Tool call ===")
    result = kernel.call_tool("add", {"a": 2, "b": 3}, user_scope)
    print(f"Result: {result.content[0].text}\n")

    print("=== Validation error (negative numbers) ===")
    try:
        kernel.call_tool("add", {"a": -1, "b": 3}, user_scope)
    except ValidationError as e:
        print(f"Caught: {e}\n")

    print("=== Permission denied (non-admin) ===")
    try:
        kernel.call_tool("admin_action", {}, user_scope)
    except PermissionDeniedError as e:
        print(f"Caught: {e}\n")

    print("=== Permission granted (admin) ===")
    result = kernel.call_tool("admin_action", {}, admin_scope)
    print(f"Result: {result.content[0].text}\n")

    print("=== Resource read ===")
    result = kernel.read_resource("user://current", user_scope)
    print(f"Result: {result.contents[0].text}\n")

    print("=== Prompt get ===")
    result = kernel.get_prompt("greeting", {"name": "World"}, user_scope)
    print(f"Result: {result.messages[0].content.text}")
