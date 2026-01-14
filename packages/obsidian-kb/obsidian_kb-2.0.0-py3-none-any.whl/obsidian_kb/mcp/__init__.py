"""MCP Auto-registration system.

This module provides automatic discovery and registration of MCP tools.

Usage:
    from obsidian_kb.mcp import ToolRegistry

    # Discover all tools in mcp/tools/ directory
    registry = ToolRegistry()
    registry.discover()

    # Register all tools with FastMCP instance
    registry.register_all(mcp)
"""

from obsidian_kb.mcp.base import MCPTool
from obsidian_kb.mcp.registry import ToolRegistry

__all__ = [
    "MCPTool",
    "ToolRegistry",
]
