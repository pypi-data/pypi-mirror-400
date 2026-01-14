"""MCP server implementations for ATLAS.

Provides MCP servers that expose ATLAS memory as tools for agents.
"""

from cognitive_core.mcp.memory_server import create_memory_server

__all__ = ["create_memory_server"]
