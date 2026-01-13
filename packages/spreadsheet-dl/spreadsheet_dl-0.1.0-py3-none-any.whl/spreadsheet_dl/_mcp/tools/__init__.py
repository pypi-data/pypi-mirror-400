"""MCP tool handlers organized by category.

This package provides modular tool registration for the MCP server.
Tools are organized by category:

- spreadsheet_tools: Cell, row, column, sheet, and freeze operations
- style_tools: Style, formatting, and theme operations
- chart_tools: Chart, conditional formatting, validation, named ranges
- analysis_tools: Workbook operations, formula auditing, data analysis
- export_tools: Import/export for various formats
- template_tools: Template and print layout operations

Usage:
    from spreadsheet_dl._mcp.tools import register_all_tools

    def _register_tools(self):
        register_all_tools(self._registry, self._validate_path)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from spreadsheet_dl._mcp.tools.analysis_tools import register_analysis_tools
from spreadsheet_dl._mcp.tools.chart_tools import register_chart_tools
from spreadsheet_dl._mcp.tools.export_tools import register_export_tools
from spreadsheet_dl._mcp.tools.spreadsheet_tools import register_spreadsheet_tools
from spreadsheet_dl._mcp.tools.style_tools import register_style_tools
from spreadsheet_dl._mcp.tools.template_tools import register_template_tools

if TYPE_CHECKING:
    from spreadsheet_dl._mcp.registry import MCPToolRegistry

__all__ = [
    "register_all_tools",
    "register_analysis_tools",
    "register_chart_tools",
    "register_export_tools",
    "register_spreadsheet_tools",
    "register_style_tools",
    "register_template_tools",
]


def register_all_tools(
    registry: MCPToolRegistry,
    validate_path: Any,
) -> None:
    """Register all MCP tools from all category modules.

    This is the main entry point for tool registration, called by MCPServer
    during initialization. It delegates to each category-specific registration
    function.

    Args:
        registry: MCPToolRegistry instance to register tools with
        validate_path: Path validation function from MCPServer

    Example:
        >>> from spreadsheet_dl._mcp.tools import register_all_tools
        >>> register_all_tools(self._registry, self._validate_path)
    """
    # Spreadsheet operations (cell, row, column, sheet, freeze)
    register_spreadsheet_tools(registry, validate_path)

    # Style and formatting operations
    register_style_tools(registry, validate_path)

    # Chart and advanced visualization
    register_chart_tools(registry, validate_path)

    # Analysis and workbook operations
    register_analysis_tools(registry, validate_path)

    # Import/export operations
    register_export_tools(registry, validate_path)

    # Template and print operations
    register_template_tools(registry, validate_path)
