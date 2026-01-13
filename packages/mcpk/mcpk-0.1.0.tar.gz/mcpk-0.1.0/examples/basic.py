"""Basic MCPK example - synchronous kernel.

This example shows the minimal setup to:
1. Create a kernel
2. Register a tool
3. Call the tool with a scope
"""

from mcpk import ExecutionScope, Kernel, TextItem, ToolDef, ToolResult

# Step 1: Create a kernel
# The kernel is generic over your context type. Here we use `None` for simplicity.
kernel: Kernel[None] = Kernel()


# Step 2: Define a tool handler
# Handlers receive the execution scope and arguments dict.
def add(scope: ExecutionScope[None], args: dict) -> ToolResult:
    a = args["a"]
    b = args["b"]
    return ToolResult(content=(TextItem(text=f"{a} + {b} = {a + b}"),))


# Step 3: Register the tool with its schema
kernel.register_tool(
    ToolDef(
        name="add",
        description="Add two numbers",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
    ),
    add,
)


# Step 4: Call the tool
# ExecutionScope wraps your app context with MCP metadata.
scope = ExecutionScope(ctx=None)
result = kernel.call_tool("add", {"a": 2, "b": 3}, scope)

print(f"Result: {result.content[0].text}")
# Output: Result: 2 + 3 = 5
