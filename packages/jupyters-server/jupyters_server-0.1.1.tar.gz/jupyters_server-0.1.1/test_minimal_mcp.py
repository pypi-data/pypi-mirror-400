#!/usr/bin/env python3
"""Minimal FastMCP server test."""

from mcp.server.fastmcp import FastMCP

# Create minimal server
mcp = FastMCP("test-server")

@mcp.tool()
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("Starting minimal MCP server...", flush=True)
    mcp.run()
