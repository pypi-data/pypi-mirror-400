"""Basic MCPK example - asynchronous kernel.

Same as basic.py but using AsyncKernel for async handlers.
"""

import asyncio

from mcpk import AsyncKernel, ExecutionScope, TextItem, ToolDef, ToolResult

# Step 1: Create an async kernel
kernel: AsyncKernel[None] = AsyncKernel()


# Step 2: Define an async tool handler
# You can await async operations here (db calls, http requests, etc.)
async def add(scope: ExecutionScope[None], args: dict) -> ToolResult:
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


# Step 4: Call the tool (awaitable)
async def main() -> None:
    scope = ExecutionScope(ctx=None)
    result = await kernel.call_tool("add", {"a": 2, "b": 3}, scope)
    print(f"Result: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
