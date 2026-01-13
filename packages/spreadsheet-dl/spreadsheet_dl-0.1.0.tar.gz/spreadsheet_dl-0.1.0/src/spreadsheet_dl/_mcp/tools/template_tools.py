"""Template operation tools.

Provides MCP tools for:
- Template listing and retrieval
- Template application
- Print/page setup

Note: Print operations are not yet implemented in OdsEditor.
These tools return appropriate error messages indicating unavailable functionality.
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl._mcp.models import MCPToolParameter, MCPToolResult


def register_template_tools(
    registry: Any,
    validate_path: Any,
) -> None:
    """Register all template and print tools.

    Args:
        registry: MCPToolRegistry instance
        validate_path: Path validation function
    """
    _register_template_operations(registry, validate_path)
    _register_print_operations(registry, validate_path)


def _register_template_operations(registry: Any, validate_path: Any) -> None:
    """Register template operation tools."""
    # template_list
    registry.register(
        name="template_list",
        description="List available spreadsheet templates",
        handler=_make_template_list_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="template_operations",
    )

    # template_get
    registry.register(
        name="template_get",
        description="Get details of a specific template",
        handler=_make_template_get_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="template_name",
                type="string",
                description="Name of the template",
            ),
        ],
        category="template_operations",
    )

    # template_apply
    registry.register(
        name="template_apply",
        description="Apply a template to create a new document",
        handler=_make_template_apply_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the output file",
            ),
            MCPToolParameter(
                name="template_name",
                type="string",
                description="Name of the template to apply",
            ),
            MCPToolParameter(
                name="data",
                type="string",
                description="JSON object with template data",
                required=False,
            ),
        ],
        category="template_operations",
    )


def _register_print_operations(registry: Any, validate_path: Any) -> None:
    """Register print and page setup tools."""
    # page_setup
    registry.register(
        name="page_setup",
        description="Configure page setup for printing",
        handler=_make_page_setup_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="settings",
                type="string",
                description="JSON object with page setup options",
            ),
        ],
        category="print_layout",
    )

    # print_area_set
    registry.register(
        name="print_area_set",
        description="Set the print area for a sheet",
        handler=_make_print_area_set_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell range for print area",
            ),
        ],
        category="print_layout",
    )

    # print_titles_set
    registry.register(
        name="print_titles_set",
        description="Set rows/columns to repeat on each page",
        handler=_make_print_titles_set_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="rows",
                type="string",
                description="Rows to repeat (e.g., '1:2')",
                required=False,
            ),
            MCPToolParameter(
                name="columns",
                type="string",
                description="Columns to repeat (e.g., 'A:B')",
                required=False,
            ),
        ],
        category="print_layout",
    )

    # header_footer_set
    registry.register(
        name="header_footer_set",
        description="Set page headers and footers",
        handler=_make_header_footer_set_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="header",
                type="string",
                description="Header text (use &L, &C, &R for left/center/right)",
                required=False,
            ),
            MCPToolParameter(
                name="footer",
                type="string",
                description="Footer text",
                required=False,
            ),
        ],
        category="print_layout",
    )

    # page_breaks_insert
    registry.register(
        name="page_breaks_insert",
        description="Insert manual page breaks",
        handler=_make_page_breaks_insert_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="row",
                type="integer",
                description="Row for horizontal break",
                required=False,
            ),
            MCPToolParameter(
                name="column",
                type="string",
                description="Column for vertical break",
                required=False,
            ),
        ],
        category="print_layout",
    )


# =============================================================================
# Handler Factory Functions - Template Operations
# =============================================================================


def _make_template_list_handler(validate_path: Any) -> Any:
    """Create template_list handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            from spreadsheet_dl.templates import (  # type: ignore[import-not-found]
                list_templates,
            )

            templates = list_templates()

            return MCPToolResult.json({"templates": templates})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_template_get_handler(validate_path: Any) -> Any:
    """Create template_get handler."""

    def handler(file_path: str, template_name: str) -> MCPToolResult:
        try:
            from spreadsheet_dl.templates import get_template

            template = get_template(template_name)

            return MCPToolResult.json(
                {
                    "template_name": template_name,
                    "description": template.description,
                    "variables": template.variables,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_template_apply_handler(validate_path: Any) -> Any:
    """Create template_apply handler."""
    import json

    def handler(
        output_path: str,
        template_name: str,
        data: str | None = None,
    ) -> MCPToolResult:
        try:
            from pathlib import Path

            from spreadsheet_dl.templates import apply_template

            template_data = json.loads(data) if data else {}
            result_path = apply_template(
                template_name,
                Path(output_path),
                template_data,
            )

            return MCPToolResult.json(
                {
                    "success": True,
                    "template": template_name,
                    "output": str(result_path),
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


# =============================================================================
# Handler Factory Functions - Print Operations
# =============================================================================


def _make_page_setup_handler(validate_path: Any) -> Any:
    """Create page_setup handler."""

    def handler(file_path: str, sheet: str, settings: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_page_setup method
            return MCPToolResult.error(
                "Page setup not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for page layout configuration."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_print_area_set_handler(validate_path: Any) -> Any:
    """Create print_area_set handler."""

    def handler(file_path: str, sheet: str, range: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_print_area method
            return MCPToolResult.error(
                "Print area configuration not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for print area configuration."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_print_titles_set_handler(validate_path: Any) -> Any:
    """Create print_titles_set handler."""

    def handler(
        file_path: str,
        sheet: str,
        rows: str | None = None,
        columns: str | None = None,
    ) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_print_titles method
            return MCPToolResult.error(
                "Print titles not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for print title configuration."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_header_footer_set_handler(validate_path: Any) -> Any:
    """Create header_footer_set handler."""

    def handler(
        file_path: str,
        sheet: str,
        header: str | None = None,
        footer: str | None = None,
    ) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_header_footer method
            return MCPToolResult.error(
                "Header/footer configuration not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for header/footer configuration."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_page_breaks_insert_handler(validate_path: Any) -> Any:
    """Create page_breaks_insert handler."""

    def handler(
        file_path: str,
        sheet: str,
        row: int | None = None,
        column: str | None = None,
    ) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have insert_page_break method
            return MCPToolResult.error(
                "Page break insertion not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for page break configuration."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler
