"""Run Mind MCP server.

Usage:
    python -m mind.mcp

Or using MCP dev tools:
    mcp dev src/mind/mcp/server.py
"""

from mind.mcp.server import run_server

if __name__ == "__main__":
    run_server()
