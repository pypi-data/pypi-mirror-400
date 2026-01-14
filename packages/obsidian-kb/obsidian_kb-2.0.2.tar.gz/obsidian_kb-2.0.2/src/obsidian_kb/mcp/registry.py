"""Tool Registry with automatic discovery of MCP tools.

This module provides the ToolRegistry class that can automatically discover
and register all MCPTool subclasses in a given directory.
"""

import importlib
import importlib.util
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from obsidian_kb.mcp.base import MCPTool

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for MCP tools with automatic discovery.

    The registry can scan a directory for Python modules, find all classes
    that inherit from MCPTool, and register them with a FastMCP instance.

    Example:
        registry = ToolRegistry()

        # Discover tools in the default location (mcp/tools/)
        registry.discover()

        # Or discover from a custom path
        registry.discover(Path("/path/to/tools"))

        # Register all discovered tools
        registry.register_all(mcp)

        # Get specific tool
        search_tool = registry.get("search_vault")
    """

    def __init__(self) -> None:
        """Initialize an empty tool registry."""
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        """Register a single tool instance.

        Args:
            tool: MCPTool instance to register

        Raises:
            ValueError: If a tool with the same name is already registered
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                f"Existing: {self._tools[tool.name]}, New: {tool}"
            )

        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name} ({tool.__class__.__name__})")

    def get(self, name: str) -> MCPTool | None:
        """Get a registered tool by name.

        Args:
            name: Tool name

        Returns:
            MCPTool instance or None if not found
        """
        return self._tools.get(name)

    def get_all(self) -> list[MCPTool]:
        """Get all registered tools.

        Returns:
            List of all MCPTool instances
        """
        return list(self._tools.values())

    def discover(self, tools_path: Path | None = None) -> int:
        """Discover and register all MCPTool subclasses in a directory.

        Scans the specified directory (or default mcp/tools/) for Python
        modules, imports them, and registers any MCPTool subclass found.

        Args:
            tools_path: Path to directory containing tool modules.
                        Defaults to mcp/tools/ relative to this module.

        Returns:
            Number of tools discovered and registered

        Example:
            registry = ToolRegistry()
            count = registry.discover()
            print(f"Discovered {count} tools")
        """
        if tools_path is None:
            # Default to mcp/tools/ relative to this file
            tools_path = Path(__file__).parent / "tools"

        if not tools_path.exists():
            logger.warning(f"Tools directory does not exist: {tools_path}")
            return 0

        if not tools_path.is_dir():
            logger.warning(f"Tools path is not a directory: {tools_path}")
            return 0

        discovered_count = 0

        # Scan all Python files in the tools directory
        for module_path in tools_path.glob("*.py"):
            if module_path.name.startswith("_"):
                continue  # Skip __init__.py and private modules

            try:
                tools = self._discover_in_module(module_path)
                for tool in tools:
                    try:
                        self.register(tool)
                        discovered_count += 1
                    except ValueError as e:
                        logger.warning(f"Failed to register tool: {e}")

            except Exception as e:
                logger.error(f"Failed to import module {module_path}: {e}", exc_info=True)

        logger.info(f"Discovered {discovered_count} MCP tools from {tools_path}")
        return discovered_count

    def _discover_in_module(self, module_path: Path) -> list[MCPTool]:
        """Discover MCPTool subclasses in a single module.

        Args:
            module_path: Path to Python module file

        Returns:
            List of instantiated MCPTool subclasses
        """
        # Create a module spec from the file path
        module_name = f"obsidian_kb.mcp.tools.{module_path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load spec for {module_path}")
            return []

        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.error(f"Error executing module {module_path}: {e}", exc_info=True)
            return []

        tools: list[MCPTool] = []

        # Find all classes that inherit from MCPTool
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue

            attr = getattr(module, attr_name)

            # Check if it's a class that inherits from MCPTool
            if not isinstance(attr, type):
                continue

            if not issubclass(attr, MCPTool):
                continue

            if attr is MCPTool:
                continue  # Skip the base class itself

            # Try to instantiate the tool
            try:
                tool_instance = attr()
                tools.append(tool_instance)
                logger.debug(f"Discovered tool class: {attr_name} -> {tool_instance.name}")
            except Exception as e:
                logger.error(f"Failed to instantiate {attr_name}: {e}", exc_info=True)

        return tools

    def register_all(self, mcp: "FastMCP") -> int:
        """Register all discovered tools with a FastMCP instance.

        Args:
            mcp: FastMCP instance to register tools with

        Returns:
            Number of tools registered
        """
        for tool in self._tools.values():
            tool.register(mcp)

        logger.info(f"Registered {len(self._tools)} tools with FastMCP")
        return len(self._tools)

    def clear(self) -> None:
        """Remove all registered tools."""
        self._tools.clear()

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if a tool with the given name is registered."""
        return name in self._tools

    def __iter__(self):
        """Iterate over tool names."""
        return iter(self._tools)

    def __repr__(self) -> str:
        tool_names = ", ".join(self._tools.keys())
        return f"<ToolRegistry(tools=[{tool_names}])>"


# Global registry instance for convenience
_global_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance.

    Creates a new registry if one doesn't exist.

    Returns:
        Global ToolRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def reset_tool_registry() -> None:
    """Reset the global tool registry.

    Useful for testing.
    """
    global _global_registry
    _global_registry = None
