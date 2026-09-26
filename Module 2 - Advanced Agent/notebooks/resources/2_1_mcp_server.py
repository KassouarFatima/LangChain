"""Local MCP server for Module 2, lesson 2.1 (Advanced Agents).

The notebook launches this file as a subprocess over the stdio transport:

    python resources/2_1_mcp_server.py

It exposes the three kinds of content an MCP server can give an agent:

1. a **tool**      -> something the agent can call during a conversation,
2. a **resource**  -> data the agent can read (a URI),
3. a **prompt**    -> a reusable system prompt the agent can load (named "prompt").

Everything is plain Python: no LangChain import here, only the MCP SDK.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-local-demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together. Use it for any arithmetic the user asks for."""
    return a + b


@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """A text resource: data the agent can read, not a function to call."""
    return f"Hello {name}! This is a resource exposed by the local MCP server."


@mcp.prompt()
def prompt() -> str:
    """A reusable system prompt loaded from the MCP server by name: 'prompt'."""
    return (
        "You are a helpful assistant. Keep answers short and clear, "
        "and only use the tools you have when they are needed."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")