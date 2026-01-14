"""MCP Tool implementations.

This package contains concrete MCPTool subclasses that are automatically
discovered by the ToolRegistry.

Each tool should be in its own module and inherit from MCPTool:
    - search_tool.py -> SearchTool
    - read_note_tool.py -> ReadNoteTool
    - list_vaults_tool.py -> ListVaultsTool
    - etc.

The ToolRegistry.discover() method will automatically find and register
all MCPTool subclasses in this directory.
"""
