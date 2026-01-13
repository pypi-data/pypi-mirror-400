"""MCP tool registry.

Part of the modular MCP server implementation.
Provides decorator-based tool registration and discovery.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from spreadsheet_dl._mcp.models import MCPTool, MCPToolParameter, MCPToolResult

if TYPE_CHECKING:
    from collections.abc import Callable


class MCPToolRegistry:
    """Registry for MCP tools with decorator-based registration.

        - MCPToolRegistry with decorator registration
        - Tool discovery system

    Features:
        - Decorator-based tool registration
        - Automatic tool discovery
        - Tool metadata management
        - Category-based organization

    Example:
        >>> registry = MCPToolRegistry()  # doctest: +SKIP
        >>> @registry.tool("cell_get", "Get cell value")  # doctest: +SKIP
        >>> def get_cell(sheet: str, cell: str) -> str:  # doctest: +SKIP
        ...     return "value"
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, MCPTool] = {}
        self._categories: dict[str, list[str]] = {}

    def tool(
        self,
        name: str,
        description: str,
        category: str = "general",
        parameters: list[MCPToolParameter] | None = None,
    ) -> Callable[[Callable[..., MCPToolResult]], Callable[..., MCPToolResult]]:
        """Decorator to register a tool.

        Args:
            name: Tool name (unique identifier)
            description: Human-readable description
            category: Tool category for organization
            parameters: List of tool parameters

        Returns:
            Decorated function
        """

        def decorator(
            func: Callable[..., MCPToolResult],
        ) -> Callable[..., MCPToolResult]:
            # Create tool with handler
            tool = MCPTool(
                name=name,
                description=description,
                parameters=parameters or [],
                handler=func,
            )

            # Register tool
            self._tools[name] = tool

            # Add to category
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(name)

            return func

        return decorator

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[..., MCPToolResult],
        parameters: list[MCPToolParameter] | None = None,
        category: str = "general",
    ) -> None:
        """Register a tool programmatically.

        Args:
            name: Tool name
            description: Tool description
            handler: Tool handler function
            parameters: Tool parameters
            category: Tool category
        """
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters or [],
            handler=handler,
        )
        self._tools[name] = tool

        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)

    def get_tool(self, name: str) -> MCPTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_all_tools(self) -> dict[str, MCPTool]:
        """Get all registered tools."""
        return self._tools.copy()

    def get_tools_by_category(self, category: str) -> list[MCPTool]:
        """Get all tools in a category."""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]

    def get_categories(self) -> list[str]:
        """Get all available categories."""
        return list(self._categories.keys())

    def list_tools(self) -> list[dict[str, Any]]:
        """List all tools with metadata.

        Returns:
            List of tool schemas
        """
        return [tool.to_schema() for tool in self._tools.values()]

    def get_tool_count(self) -> int:
        """Get total number of registered tools."""
        return len(self._tools)
