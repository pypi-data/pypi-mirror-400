"""Tests for MCP auto-registration system."""

import pytest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, AsyncMock, patch

from obsidian_kb.mcp.base import MCPTool, InputSchema
from obsidian_kb.mcp.registry import ToolRegistry, get_tool_registry, reset_tool_registry
from obsidian_kb.types import MCPValidationError


# Test fixtures - Sample tool implementations for testing

class SampleTool(MCPTool):
    """A simple test tool."""

    @property
    def name(self) -> str:
        return "sample_tool"

    @property
    def description(self) -> str:
        return "A sample tool for testing"

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A message to echo",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of times to repeat",
                },
            },
            "required": ["message"],
            "additionalProperties": False,
        }

    async def execute(self, message: str, count: int = 1, **kwargs: Any) -> str:
        return f"{message} " * count


class AnotherTool(MCPTool):
    """Another test tool."""

    @property
    def name(self) -> str:
        return "another_tool"

    @property
    def description(self) -> str:
        return "Another tool for testing"

    @property
    def input_schema(self) -> InputSchema:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> str:
        return "Hello from another tool"


class TestMCPTool:
    """Tests for MCPTool base class."""

    def test_tool_properties(self):
        """Test that tool properties are accessible."""
        tool = SampleTool()

        assert tool.name == "sample_tool"
        assert "sample tool" in tool.description.lower()
        assert tool.input_schema["type"] == "object"
        assert "message" in tool.input_schema["properties"]

    @pytest.mark.asyncio
    async def test_execute_with_required_param(self):
        """Test executing tool with required parameter."""
        tool = SampleTool()
        result = await tool.execute(message="Hello")
        assert result == "Hello "

    @pytest.mark.asyncio
    async def test_execute_with_optional_param(self):
        """Test executing tool with optional parameter."""
        tool = SampleTool()
        result = await tool.execute(message="Hi", count=3)
        assert result == "Hi Hi Hi "

    def test_validate_input_missing_required(self):
        """Test validation fails for missing required param."""
        tool = SampleTool()

        with pytest.raises(MCPValidationError) as exc_info:
            tool.validate_input()

        assert exc_info.value.param_name == "message"
        assert exc_info.value.tool_name == "sample_tool"

    def test_validate_input_wrong_type(self):
        """Test validation fails for wrong type."""
        tool = SampleTool()

        with pytest.raises(MCPValidationError) as exc_info:
            tool.validate_input(message="hello", count="not an int")

        assert exc_info.value.param_name == "count"

    def test_validate_input_success(self):
        """Test validation succeeds with correct params."""
        tool = SampleTool()
        # Should not raise
        tool.validate_input(message="hello")
        tool.validate_input(message="hello", count=5)

    def test_repr(self):
        """Test string representation."""
        tool = SampleTool()
        assert "SampleTool" in repr(tool)
        assert "sample_tool" in repr(tool)


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def setup_method(self):
        """Reset global registry before each test."""
        reset_tool_registry()

    def test_register_single_tool(self):
        """Test registering a single tool."""
        registry = ToolRegistry()
        tool = SampleTool()

        registry.register(tool)

        assert len(registry) == 1
        assert "sample_tool" in registry
        assert registry.get("sample_tool") is tool

    def test_register_multiple_tools(self):
        """Test registering multiple tools."""
        registry = ToolRegistry()
        tool1 = SampleTool()
        tool2 = AnotherTool()

        registry.register(tool1)
        registry.register(tool2)

        assert len(registry) == 2
        assert registry.get("sample_tool") is tool1
        assert registry.get("another_tool") is tool2

    def test_register_duplicate_raises(self):
        """Test that registering duplicate tool raises error."""
        registry = ToolRegistry()
        tool1 = SampleTool()
        tool2 = SampleTool()

        registry.register(tool1)

        with pytest.raises(ValueError) as exc_info:
            registry.register(tool2)

        assert "already registered" in str(exc_info.value)

    def test_get_nonexistent_returns_none(self):
        """Test getting non-existent tool returns None."""
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_get_all(self):
        """Test getting all registered tools."""
        registry = ToolRegistry()
        tool1 = SampleTool()
        tool2 = AnotherTool()

        registry.register(tool1)
        registry.register(tool2)

        all_tools = registry.get_all()

        assert len(all_tools) == 2
        assert tool1 in all_tools
        assert tool2 in all_tools

    def test_clear(self):
        """Test clearing the registry."""
        registry = ToolRegistry()
        registry.register(SampleTool())
        registry.register(AnotherTool())

        assert len(registry) == 2

        registry.clear()

        assert len(registry) == 0

    def test_iter(self):
        """Test iterating over tool names."""
        registry = ToolRegistry()
        registry.register(SampleTool())
        registry.register(AnotherTool())

        names = list(registry)

        assert "sample_tool" in names
        assert "another_tool" in names

    def test_repr(self):
        """Test string representation."""
        registry = ToolRegistry()
        registry.register(SampleTool())

        assert "ToolRegistry" in repr(registry)
        assert "sample_tool" in repr(registry)


class TestToolRegistryDiscover:
    """Tests for ToolRegistry.discover() method."""

    def setup_method(self):
        """Reset global registry before each test."""
        reset_tool_registry()

    def test_discover_nonexistent_path(self):
        """Test discover with non-existent path returns 0."""
        registry = ToolRegistry()
        count = registry.discover(Path("/nonexistent/path"))
        assert count == 0

    def test_discover_file_not_directory(self, tmp_path):
        """Test discover with file instead of directory returns 0."""
        registry = ToolRegistry()
        file_path = tmp_path / "file.py"
        file_path.touch()

        count = registry.discover(file_path)
        assert count == 0

    def test_discover_empty_directory(self, tmp_path):
        """Test discover with empty directory returns 0."""
        registry = ToolRegistry()
        count = registry.discover(tmp_path)
        assert count == 0

    def test_discover_from_tools_directory(self):
        """Test discover finds tools in mcp/tools/ directory."""
        registry = ToolRegistry()
        tools_path = Path(__file__).parent.parent / "src/obsidian_kb/mcp/tools"

        if tools_path.exists():
            count = registry.discover(tools_path)
            # Should discover our test tools
            assert count >= 1

            # Check that at least some known tools are registered
            assert len(registry) > 0


class TestToolRegistryRegisterAll:
    """Tests for ToolRegistry.register_all() method."""

    def test_register_all_with_mock_mcp(self):
        """Test register_all calls mcp.tool() for each tool."""
        registry = ToolRegistry()
        registry.register(SampleTool())
        registry.register(AnotherTool())

        # Create mock FastMCP
        mock_mcp = MagicMock()
        mock_tool_decorator = MagicMock(return_value=lambda x: x)
        mock_mcp.tool.return_value = mock_tool_decorator

        count = registry.register_all(mock_mcp)

        assert count == 2
        assert mock_mcp.tool.call_count == 2


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def setup_method(self):
        """Reset global registry before each test."""
        reset_tool_registry()

    def test_get_tool_registry_singleton(self):
        """Test get_tool_registry returns singleton."""
        registry1 = get_tool_registry()
        registry2 = get_tool_registry()

        assert registry1 is registry2

    def test_reset_tool_registry(self):
        """Test reset_tool_registry creates new instance."""
        registry1 = get_tool_registry()
        registry1.register(SampleTool())

        reset_tool_registry()

        registry2 = get_tool_registry()
        assert registry1 is not registry2
        assert len(registry2) == 0


class TestToolExecution:
    """Tests for tool execution with validation."""

    @pytest.mark.asyncio
    async def test_tool_validates_before_execute(self):
        """Test that validation happens before execution."""
        tool = SampleTool()

        # Mock execute to track if it's called
        original_execute = tool.execute
        execute_called = []

        async def mock_execute(**kwargs):
            execute_called.append(True)
            return await original_execute(**kwargs)

        tool.execute = mock_execute

        # Validate should fail before execute is called
        try:
            tool.validate_input()  # Missing required param
            await tool.execute()
        except MCPValidationError:
            pass

        # Execute should not have been called due to validation failure
        assert len(execute_called) == 0

    @pytest.mark.asyncio
    async def test_tool_register_creates_handler(self):
        """Test that register creates a proper handler function."""
        tool = SampleTool()

        # Create mock FastMCP
        mock_mcp = MagicMock()
        registered_handler = None

        def capture_handler(func):
            nonlocal registered_handler
            registered_handler = func
            return func

        mock_mcp.tool.return_value = capture_handler

        tool.register(mock_mcp)

        assert registered_handler is not None
        assert registered_handler.__name__ == "sample_tool"
        assert "sample tool" in registered_handler.__doc__.lower()

    @pytest.mark.asyncio
    async def test_registered_handler_executes(self):
        """Test that registered handler executes correctly."""
        tool = SampleTool()

        # Create mock FastMCP and capture handler
        mock_mcp = MagicMock()
        registered_handler = None

        def capture_handler(func):
            nonlocal registered_handler
            registered_handler = func
            return func

        mock_mcp.tool.return_value = capture_handler

        tool.register(mock_mcp)

        # Execute through the handler
        result = await registered_handler(message="Test")
        assert "Test" in result

    @pytest.mark.asyncio
    async def test_registered_handler_validates(self):
        """Test that registered handler validates input."""
        tool = SampleTool()

        # Create mock FastMCP and capture handler
        mock_mcp = MagicMock()
        registered_handler = None

        def capture_handler(func):
            nonlocal registered_handler
            registered_handler = func
            return func

        mock_mcp.tool.return_value = capture_handler

        tool.register(mock_mcp)

        # Execute with missing required param - should return error message
        result = await registered_handler()
        assert "message" in result.lower() or "Invalid" in result


class TestConcreteTools:
    """Tests for concrete tool implementations."""

    def test_list_vaults_tool_properties(self):
        """Test ListVaultsTool properties."""
        from obsidian_kb.mcp.tools.list_vaults_tool import ListVaultsTool

        tool = ListVaultsTool()

        assert tool.name == "list_vaults"
        assert "vault" in tool.description.lower()
        assert tool.input_schema["type"] == "object"

    def test_vault_stats_tool_properties(self):
        """Test VaultStatsTool properties."""
        from obsidian_kb.mcp.tools.vault_stats_tool import VaultStatsTool

        tool = VaultStatsTool()

        assert tool.name == "vault_stats"
        assert "vault_name" in tool.input_schema["properties"]
        assert "vault_name" in tool.input_schema["required"]

    def test_search_help_tool_properties(self):
        """Test SearchHelpTool properties."""
        from obsidian_kb.mcp.tools.search_help_tool import SearchHelpTool

        tool = SearchHelpTool()

        assert tool.name == "search_help"
        assert tool.input_schema["required"] == []

    @pytest.mark.asyncio
    async def test_search_help_tool_execute(self):
        """Test SearchHelpTool returns help text."""
        from obsidian_kb.mcp.tools.search_help_tool import SearchHelpTool

        tool = SearchHelpTool()
        result = await tool.execute()

        assert "поиск" in result.lower() or "search" in result.lower()
        assert "tags:" in result
        assert "type:" in result

    def test_system_health_tool_properties(self):
        """Test SystemHealthTool properties."""
        from obsidian_kb.mcp.tools.system_health_tool import SystemHealthTool

        tool = SystemHealthTool()

        assert tool.name == "system_health"
        assert "диагностик" in tool.description.lower()

    def test_list_tags_tool_properties(self):
        """Test ListTagsTool properties."""
        from obsidian_kb.mcp.tools.list_tags_tool import ListTagsTool

        tool = ListTagsTool()

        assert tool.name == "list_tags"
        assert "vault_name" in tool.input_schema["required"]
        assert "limit" in tool.input_schema["properties"]

    def test_list_configured_vaults_tool_properties(self):
        """Test ListConfiguredVaultsTool properties."""
        from obsidian_kb.mcp.tools.list_configured_vaults_tool import ListConfiguredVaultsTool

        tool = ListConfiguredVaultsTool()

        assert tool.name == "list_configured_vaults"
        assert tool.input_schema["required"] == []


class TestInputSchemaValidation:
    """Tests for input schema validation edge cases."""

    def test_validate_unknown_param_with_additional_properties_false(self):
        """Test validation fails for unknown param when additionalProperties is false."""
        tool = SampleTool()

        with pytest.raises(MCPValidationError):
            tool.validate_input(message="hello", unknown_param="value")

    def test_validate_allows_none_for_optional(self):
        """Test validation allows None for optional parameters."""
        tool = SampleTool()
        # Should not raise
        tool.validate_input(message="hello", count=None)

    def test_validate_array_type(self):
        """Test validation of array type."""

        class ArrayTool(MCPTool):
            @property
            def name(self) -> str:
                return "array_tool"

            @property
            def description(self) -> str:
                return "Tool with array param"

            @property
            def input_schema(self) -> InputSchema:
                return {
                    "type": "object",
                    "properties": {
                        "items": {"type": "array"},
                    },
                    "required": ["items"],
                }

            async def execute(self, items: list, **kwargs) -> str:
                return str(items)

        tool = ArrayTool()

        # Should pass with list
        tool.validate_input(items=[1, 2, 3])

        # Should fail with non-list
        with pytest.raises(MCPValidationError):
            tool.validate_input(items="not a list")

    def test_validate_boolean_type(self):
        """Test validation of boolean type."""

        class BoolTool(MCPTool):
            @property
            def name(self) -> str:
                return "bool_tool"

            @property
            def description(self) -> str:
                return "Tool with bool param"

            @property
            def input_schema(self) -> InputSchema:
                return {
                    "type": "object",
                    "properties": {
                        "flag": {"type": "boolean"},
                    },
                    "required": ["flag"],
                }

            async def execute(self, flag: bool, **kwargs) -> str:
                return str(flag)

        tool = BoolTool()

        # Should pass with bool
        tool.validate_input(flag=True)
        tool.validate_input(flag=False)

        # Should fail with non-bool
        with pytest.raises(MCPValidationError):
            tool.validate_input(flag="true")
