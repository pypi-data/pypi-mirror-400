"""Base class for MCP tools with auto-registration support.

This module provides the MCPTool abstract base class that all MCP tools should inherit from.
It enables automatic discovery and registration of tools without manual enumeration.
"""

import inspect
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypedDict

from obsidian_kb.types import MCPToolError, MCPValidationError

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def _json_type_to_python(json_type: str | None) -> type:
    """Convert JSON Schema type to Python type annotation."""
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return type_mapping.get(json_type or "string", Any)


class InputSchema(TypedDict, total=False):
    """JSON Schema for tool input validation.

    Attributes:
        type: Always "object" for MCP tools
        properties: Dict of parameter names to their schema definitions
        required: List of required parameter names
        additionalProperties: Whether to allow extra properties (default: False)
    """

    type: str
    properties: dict[str, dict[str, Any]]
    required: list[str]
    additionalProperties: bool


class MCPTool(ABC):
    """Abstract base class for MCP tools.

    Inherit from this class to create auto-registerable MCP tools.

    Example:
        class SearchTool(MCPTool):
            @property
            def name(self) -> str:
                return "search_vault"

            @property
            def description(self) -> str:
                return "Search in Obsidian vault"

            @property
            def input_schema(self) -> InputSchema:
                return {
                    "type": "object",
                    "properties": {
                        "vault_name": {"type": "string", "description": "Vault name"},
                        "query": {"type": "string", "description": "Search query"},
                    },
                    "required": ["vault_name", "query"],
                }

            async def execute(self, vault_name: str, query: str, **kwargs) -> str:
                # Implementation
                return "Search results..."
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name as it will appear in MCP.

        Should be snake_case and descriptive.
        """
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the tool.

        This will be shown to the LLM as the tool's docstring.
        Should clearly explain what the tool does and when to use it.
        """
        ...

    @property
    @abstractmethod
    def input_schema(self) -> InputSchema:
        """JSON Schema defining the tool's input parameters.

        Must be a valid JSON Schema object with:
        - type: "object"
        - properties: Dict of parameter definitions
        - required: List of required parameter names
        """
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """Execute the tool with the given parameters.

        Args:
            **kwargs: Parameters matching the input_schema

        Returns:
            String result in Markdown format

        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If parameters are invalid
        """
        ...

    def validate_input(self, **kwargs: Any) -> None:
        """Validate input parameters against the schema.

        Args:
            **kwargs: Parameters to validate

        Raises:
            MCPValidationError: If validation fails
        """
        schema = self.input_schema
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required parameters
        for param_name in required:
            if param_name not in kwargs or kwargs[param_name] is None:
                raise MCPValidationError(
                    message=f"Parameter '{param_name}' is required",
                    tool_name=self.name,
                    param_name=param_name,
                )

        # Validate types
        for param_name, param_value in kwargs.items():
            if param_name not in properties:
                if not schema.get("additionalProperties", False):
                    raise MCPValidationError(
                        message=f"Unknown parameter '{param_name}'",
                        tool_name=self.name,
                        param_name=param_name,
                        param_value=param_value,
                    )
                continue

            param_schema = properties[param_name]
            expected_type = param_schema.get("type")

            if param_value is None:
                continue  # None values are allowed for optional params

            if not self._validate_type(param_value, expected_type):
                raise MCPValidationError(
                    message=f"Expected type {expected_type}, got {type(param_value).__name__}",
                    tool_name=self.name,
                    param_name=param_name,
                    param_value=param_value,
                )

    def _validate_type(self, value: Any, expected_type: str | None) -> bool:
        """Validate a value against an expected JSON Schema type.

        Args:
            value: The value to validate
            expected_type: JSON Schema type string

        Returns:
            True if valid, False otherwise
        """
        if expected_type is None:
            return True

        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, allow

        return isinstance(value, expected_python_type)

    def register(self, mcp: "FastMCP") -> None:
        """Register this tool with a FastMCP instance.

        Creates a wrapper function with proper signature and registers it
        using the @mcp.tool() decorator pattern.

        Args:
            mcp: FastMCP instance to register with
        """
        tool_instance = self
        schema = self.input_schema
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        # Build function parameters from input_schema
        parameters: list[inspect.Parameter] = []
        for param_name, param_spec in properties.items():
            param_type = _json_type_to_python(param_spec.get("type"))
            if param_name in required:
                param = inspect.Parameter(
                    param_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=param_type,
                )
            else:
                # Optional param with default None
                param = inspect.Parameter(
                    param_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=param_type | None,
                )
            parameters.append(param)

        # Create the handler function
        async def tool_handler(*args: Any, **kwargs: Any) -> str:
            """Auto-generated handler."""
            # Merge positional args with kwargs based on parameter order
            merged_kwargs = kwargs.copy()
            for i, param in enumerate(parameters):
                if i < len(args):
                    merged_kwargs[param.name] = args[i]

            try:
                tool_instance.validate_input(**merged_kwargs)
                return await tool_instance.execute(**merged_kwargs)
            except MCPToolError as e:
                logger.warning(f"Tool {tool_instance.name} error: {e.message}")
                return e.to_user_response()
            except Exception as e:
                logger.error(
                    f"Tool {tool_instance.name} unexpected error: {e}", exc_info=True
                )
                return f"❌ Internal error: {e}"

        # Set proper signature and metadata
        tool_handler.__name__ = self.name
        tool_handler.__doc__ = self.description
        tool_handler.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
            parameters=parameters,
            return_annotation=str,
        )

        # Set __annotations__ for Pydantic compatibility
        annotations: dict[str, type] = {}
        for param in parameters:
            annotations[param.name] = param.annotation
        annotations["return"] = str
        tool_handler.__annotations__ = annotations

        # Register with FastMCP
        mcp.tool()(tool_handler)

        logger.debug(f"Registered MCP tool: {self.name}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
