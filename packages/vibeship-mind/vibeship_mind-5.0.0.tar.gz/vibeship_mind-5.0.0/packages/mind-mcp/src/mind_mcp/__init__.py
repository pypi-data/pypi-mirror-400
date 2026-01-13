"""Mind MCP - Decision Intelligence for AI Agents.

Usage:
    uvx mind-mcp              # Connect to Mind Cloud (recommended)
    uvx mind-mcp --local      # Connect to local Mind instance
    uvx mind-mcp --setup      # Configure API key

Add to Claude Desktop config:
    {
        "mcpServers": {
            "mind": {
                "command": "uvx",
                "args": ["mind-mcp"]
            }
        }
    }
"""

from .server import run_server, main

__version__ = "0.1.0"
__all__ = ["run_server", "main"]
