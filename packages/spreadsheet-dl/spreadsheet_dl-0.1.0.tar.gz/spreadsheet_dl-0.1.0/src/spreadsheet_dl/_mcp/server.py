"""MCP Server core implementation.

This module contains the MCPServer class which provides the MCP protocol
implementation. Tool handlers are organized into modular category files
in the tools/ subpackage for maintainability.

The server supports:
- Cell, row, column, and sheet operations
- Style and formatting tools
- Chart and visualization tools
- Data analysis and workbook operations
- Import/export for multiple formats
- Template and print operations
"""

from __future__ import annotations

import contextlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spreadsheet_dl._mcp.config import MCPConfig, MCPVersion
from spreadsheet_dl._mcp.exceptions import MCPSecurityError
from spreadsheet_dl._mcp.registry import MCPToolRegistry
from spreadsheet_dl._mcp.tools import register_all_tools
from spreadsheet_dl.exceptions import FileError

if TYPE_CHECKING:
    from spreadsheet_dl._mcp.models import MCPToolResult


class MCPServer:
    """MCP server for spreadsheet-dl.

    Exposes spreadsheet manipulation and budget analysis tools via MCP protocol,
    enabling natural language interaction with Claude Desktop and
    other MCP-compatible clients.

    Tool Categories:
        Cell Operations:
            - cell_get, cell_set, cell_clear
            - cell_copy, cell_move
            - cell_batch_get, cell_batch_set
            - cell_find, cell_replace
            - cell_merge, cell_unmerge

        Structure Operations:
            - row_insert, row_delete, row_hide
            - column_insert, column_delete, column_hide
            - freeze_set, freeze_clear
            - sheet_create, sheet_delete, sheet_copy

        Style Operations:
            - style_list, style_get, style_create
            - style_update, style_delete, style_apply
            - format_cells, format_number
            - format_font, format_fill, format_border

        Theme Operations:
            - theme_list, theme_get, theme_create
            - theme_apply, color_scheme_generate

        Advanced Tools:
            - chart_create, chart_update
            - validation_create, cf_create
            - named_range_create, table_create
            - query_select, query_find

        Analysis Tools:
            - workbook_properties_get, workbook_properties_set
            - workbook_statistics, workbooks_compare, workbooks_merge
            - formulas_recalculate, formulas_audit, circular_refs_find

        Import/Export:
            - csv_import, csv_export
            - tsv_import, tsv_export
            - json_import, json_export
            - xlsx_import, xlsx_export
            - html_export, pdf_export
            - batch_import, batch_export

        Template Operations:
            - template_list, template_get, template_apply
            - page_setup, print_area_set, print_titles_set
            - header_footer_set, page_breaks_insert

    Example:
        >>> server = MCPServer()
        >>> server.run()  # Starts stdio-based MCP server
    """

    def __init__(
        self,
        config: MCPConfig | None = None,
    ) -> None:
        """Initialize MCP server.

        Args:
            config: Server configuration. Uses defaults if not provided.
        """
        self.config = config or MCPConfig()
        self.logger = logging.getLogger("spreadsheet-dl-mcp")
        self._registry = MCPToolRegistry()
        self._request_count = 0
        self._last_reset = datetime.now()
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all available tools from modular tool packages."""
        register_all_tools(self._registry, self._validate_path)

    @property
    def _tools(self) -> dict[str, Any]:
        """Get registered tools from registry."""
        return self._registry._tools

    def _validate_path(self, file_path: str) -> Path:
        """Validate and resolve a file path.

        Args:
            file_path: Path to validate.

        Returns:
            Resolved Path object.

        Raises:
            MCPSecurityError: If path is not allowed.
            FileError: If file does not exist.
        """
        path = Path(file_path)
        resolved = path.resolve()

        # Check allowed paths
        allowed = len(self.config.allowed_paths) == 0  # Empty = all allowed

        for allowed_path in self.config.allowed_paths:
            with contextlib.suppress(ValueError):
                resolved.relative_to(allowed_path.resolve())
                allowed = True
                continue

        if not allowed:
            raise MCPSecurityError(
                f"Path not allowed: {path}. "
                f"Allowed paths: {[str(p) for p in self.config.allowed_paths]}"
            )

        if not resolved.exists():
            raise FileError(f"File not found: {resolved}")

        return resolved

    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded."""
        now = datetime.now()
        if (now - self._last_reset).seconds >= 60:
            self._request_count = 0
            self._last_reset = now

        self._request_count += 1
        return self._request_count <= self.config.rate_limit_per_minute

    def _log_audit(
        self,
        tool: str,
        params: dict[str, Any],
        result: MCPToolResult,
    ) -> None:
        """Log tool invocation for audit."""
        if not self.config.enable_audit_log:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "params": {k: str(v) for k, v in params.items()},
            "success": not getattr(result, "is_error", False),
        }

        self.logger.info(json.dumps(entry))

        if self.config.audit_log_path:
            with open(self.config.audit_log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def _call_tool(self, tool_name: str, **kwargs: Any) -> MCPToolResult:
        """Call a tool by name with arguments.

        Args:
            tool_name: Name of the tool to call.
            **kwargs: Tool arguments.

        Returns:
            MCPToolResult from the tool handler.

        Raises:
            KeyError: If tool is not found.
            ValueError: If tool has no handler.
        """
        if tool_name not in self._tools:
            raise KeyError(f"Unknown tool: {tool_name}")

        tool = self._tools[tool_name]
        if tool.handler is None:
            raise ValueError(f"Tool has no handler: {tool_name}")

        return tool.handler(**kwargs)  # type: ignore[no-any-return]

    # =========================================================================
    # Convenience Methods for Direct Tool Access (used by tests)
    # =========================================================================

    def _handle_cell_get(self, file_path: str, sheet: str, cell: str) -> MCPToolResult:
        """Get cell value."""
        return self._call_tool("cell_get", file_path=file_path, sheet=sheet, cell=cell)

    def _handle_cell_set(
        self, file_path: str, sheet: str, cell: str, value: str
    ) -> MCPToolResult:
        """Set cell value."""
        return self._call_tool(
            "cell_set", file_path=file_path, sheet=sheet, cell=cell, value=value
        )

    def _handle_cell_clear(
        self, file_path: str, sheet: str, cell: str
    ) -> MCPToolResult:
        """Clear cell value."""
        return self._call_tool(
            "cell_clear", file_path=file_path, sheet=sheet, cell=cell
        )

    def _handle_cell_copy(
        self, file_path: str, sheet: str, source: str, destination: str
    ) -> MCPToolResult:
        """Copy cell."""
        return self._call_tool(
            "cell_copy",
            file_path=file_path,
            sheet=sheet,
            source=source,
            destination=destination,
        )

    def _handle_cell_move(
        self, file_path: str, sheet: str, source: str, destination: str
    ) -> MCPToolResult:
        """Move cell."""
        return self._call_tool(
            "cell_move",
            file_path=file_path,
            sheet=sheet,
            source=source,
            destination=destination,
        )

    def _handle_cell_batch_get(
        self, file_path: str, sheet: str, cells: str
    ) -> MCPToolResult:
        """Get multiple cell values."""
        return self._call_tool(
            "cell_batch_get", file_path=file_path, sheet=sheet, cells=cells
        )

    def _handle_cell_batch_set(
        self, file_path: str, sheet: str, updates: str
    ) -> MCPToolResult:
        """Set multiple cell values."""
        return self._call_tool(
            "cell_batch_set", file_path=file_path, sheet=sheet, updates=updates
        )

    def _handle_cell_find(
        self, file_path: str, sheet: str, pattern: str, match_case: bool = False
    ) -> MCPToolResult:
        """Find cells matching pattern."""
        return self._call_tool(
            "cell_find",
            file_path=file_path,
            sheet=sheet,
            pattern=pattern,
            match_case=match_case,
        )

    def _handle_cell_replace(
        self,
        file_path: str,
        sheet: str,
        find: str,
        replace: str,
    ) -> MCPToolResult:
        """Replace values in cells."""
        return self._call_tool(
            "cell_replace",
            file_path=file_path,
            sheet=sheet,
            find=find,
            replace=replace,
        )

    def _handle_cell_merge(
        self, file_path: str, sheet: str, range: str
    ) -> MCPToolResult:
        """Merge cells."""
        return self._call_tool(
            "cell_merge", file_path=file_path, sheet=sheet, range=range
        )

    def _handle_cell_unmerge(
        self, file_path: str, sheet: str, range: str
    ) -> MCPToolResult:
        """Unmerge cells."""
        return self._call_tool(
            "cell_unmerge", file_path=file_path, sheet=sheet, range=range
        )

    def _handle_row_insert(
        self, file_path: str, sheet: str, row: int, count: int = 1
    ) -> MCPToolResult:
        """Insert rows."""
        return self._call_tool(
            "row_insert", file_path=file_path, sheet=sheet, row=row, count=count
        )

    def _handle_row_delete(
        self, file_path: str, sheet: str, row: int, count: int = 1
    ) -> MCPToolResult:
        """Delete rows."""
        return self._call_tool(
            "row_delete", file_path=file_path, sheet=sheet, row=row, count=count
        )

    def _handle_row_hide(
        self, file_path: str, sheet: str, row: int, hidden: bool
    ) -> MCPToolResult:
        """Hide/show row."""
        return self._call_tool(
            "row_hide", file_path=file_path, sheet=sheet, row=row, hidden=hidden
        )

    def _handle_column_insert(
        self, file_path: str, sheet: str, column: str, count: int = 1
    ) -> MCPToolResult:
        """Insert columns."""
        return self._call_tool(
            "column_insert",
            file_path=file_path,
            sheet=sheet,
            column=column,
            count=count,
        )

    def _handle_column_delete(
        self, file_path: str, sheet: str, column: str, count: int = 1
    ) -> MCPToolResult:
        """Delete columns."""
        return self._call_tool(
            "column_delete",
            file_path=file_path,
            sheet=sheet,
            column=column,
            count=count,
        )

    def _handle_column_hide(
        self, file_path: str, sheet: str, column: str, hidden: bool
    ) -> MCPToolResult:
        """Hide/show column."""
        return self._call_tool(
            "column_hide",
            file_path=file_path,
            sheet=sheet,
            column=column,
            hidden=hidden,
        )

    def _handle_sheet_create(self, file_path: str, sheet: str) -> MCPToolResult:
        """Create sheet."""
        return self._call_tool("sheet_create", file_path=file_path, sheet=sheet)

    def _handle_sheet_delete(self, file_path: str, sheet: str) -> MCPToolResult:
        """Delete sheet."""
        return self._call_tool("sheet_delete", file_path=file_path, sheet=sheet)

    def _handle_sheet_copy(
        self, file_path: str, sheet: str, new_name: str
    ) -> MCPToolResult:
        """Copy sheet."""
        return self._call_tool(
            "sheet_copy", file_path=file_path, sheet=sheet, new_name=new_name
        )

    def _handle_freeze_set(
        self, file_path: str, sheet: str, cell: str
    ) -> MCPToolResult:
        """Set freeze panes."""
        return self._call_tool(
            "freeze_set", file_path=file_path, sheet=sheet, cell=cell
        )

    def _handle_freeze_clear(self, file_path: str, sheet: str) -> MCPToolResult:
        """Clear freeze panes."""
        return self._call_tool("freeze_clear", file_path=file_path, sheet=sheet)

    def _handle_style_list(self, file_path: str) -> MCPToolResult:
        """List styles."""
        return self._call_tool("style_list", file_path=file_path)

    def _handle_style_get(self, file_path: str, style_name: str) -> MCPToolResult:
        """Get style."""
        return self._call_tool("style_get", file_path=file_path, style_name=style_name)

    def _handle_style_create(
        self, file_path: str, style_name: str, properties: str
    ) -> MCPToolResult:
        """Create style."""
        return self._call_tool(
            "style_create",
            file_path=file_path,
            style_name=style_name,
            properties=properties,
        )

    def _handle_style_update(
        self, file_path: str, style_name: str, properties: str
    ) -> MCPToolResult:
        """Update style."""
        return self._call_tool(
            "style_update",
            file_path=file_path,
            style_name=style_name,
            properties=properties,
        )

    def _handle_style_delete(self, file_path: str, style_name: str) -> MCPToolResult:
        """Delete style."""
        return self._call_tool(
            "style_delete", file_path=file_path, style_name=style_name
        )

    def _handle_style_apply(
        self, file_path: str, sheet: str, range: str, style_name: str
    ) -> MCPToolResult:
        """Apply style."""
        return self._call_tool(
            "style_apply",
            file_path=file_path,
            sheet=sheet,
            range=range,
            style_name=style_name,
        )

    def _handle_format_cells(
        self, file_path: str, sheet: str, range: str, format: str
    ) -> MCPToolResult:
        """Format cells."""
        return self._call_tool(
            "format_cells",
            file_path=file_path,
            sheet=sheet,
            range=range,
            format=format,
        )

    def _handle_format_number(
        self, file_path: str, sheet: str, range: str, format_code: str
    ) -> MCPToolResult:
        """Format number."""
        return self._call_tool(
            "format_number",
            file_path=file_path,
            sheet=sheet,
            range=range,
            format_code=format_code,
        )

    def _handle_format_font(
        self, file_path: str, sheet: str, range: str, font: str
    ) -> MCPToolResult:
        """Format font."""
        return self._call_tool(
            "format_font", file_path=file_path, sheet=sheet, range=range, font=font
        )

    def _handle_format_fill(
        self, file_path: str, sheet: str, range: str, color: str
    ) -> MCPToolResult:
        """Format fill."""
        return self._call_tool(
            "format_fill", file_path=file_path, sheet=sheet, range=range, color=color
        )

    def _handle_format_border(
        self, file_path: str, sheet: str, range: str, border: str
    ) -> MCPToolResult:
        """Format border."""
        return self._call_tool(
            "format_border",
            file_path=file_path,
            sheet=sheet,
            range=range,
            border=border,
        )

    def _handle_theme_list(self, file_path: str) -> MCPToolResult:
        """List themes."""
        return self._call_tool("theme_list", file_path=file_path)

    def _handle_theme_get(self, file_path: str, theme_name: str) -> MCPToolResult:
        """Get theme."""
        return self._call_tool("theme_get", file_path=file_path, theme_name=theme_name)

    def _handle_theme_create(
        self, file_path: str, theme_name: str, properties: str
    ) -> MCPToolResult:
        """Create theme."""
        return self._call_tool(
            "theme_create",
            file_path=file_path,
            theme_name=theme_name,
            properties=properties,
        )

    def _handle_theme_apply(self, file_path: str, theme_name: str) -> MCPToolResult:
        """Apply theme."""
        return self._call_tool(
            "theme_apply", file_path=file_path, theme_name=theme_name
        )

    def _handle_color_scheme_generate(
        self, base_color: str, scheme_type: str = "monochromatic"
    ) -> MCPToolResult:
        """Generate color scheme."""
        return self._call_tool(
            "color_scheme_generate", base_color=base_color, scheme_type=scheme_type
        )

    def _handle_page_setup(
        self, file_path: str, sheet: str, settings: str
    ) -> MCPToolResult:
        """Configure page setup."""
        return self._call_tool(
            "page_setup", file_path=file_path, sheet=sheet, settings=settings
        )

    def _handle_print_area_set(
        self, file_path: str, sheet: str, range: str
    ) -> MCPToolResult:
        """Set print area."""
        return self._call_tool(
            "print_area_set", file_path=file_path, sheet=sheet, range=range
        )

    def _handle_print_titles_set(
        self,
        file_path: str,
        sheet: str,
        rows: str | None = None,
        columns: str | None = None,
    ) -> MCPToolResult:
        """Set print titles."""
        return self._call_tool(
            "print_titles_set",
            file_path=file_path,
            sheet=sheet,
            rows=rows,
            columns=columns,
        )

    def _handle_header_footer_set(
        self,
        file_path: str,
        sheet: str,
        header: str | None = None,
        footer: str | None = None,
    ) -> MCPToolResult:
        """Set header/footer."""
        return self._call_tool(
            "header_footer_set",
            file_path=file_path,
            sheet=sheet,
            header=header,
            footer=footer,
        )

    def _handle_page_breaks_insert(
        self,
        file_path: str,
        sheet: str,
        row: int | None = None,
        column: str | None = None,
    ) -> MCPToolResult:
        """Insert page break."""
        return self._call_tool(
            "page_breaks_insert",
            file_path=file_path,
            sheet=sheet,
            row=row,
            column=column,
        )

    def _handle_template_list(self, file_path: str) -> MCPToolResult:
        """List templates."""
        return self._call_tool("template_list", file_path=file_path)

    def _handle_template_get(self, file_path: str, template_name: str) -> MCPToolResult:
        """Get template."""
        return self._call_tool(
            "template_get", file_path=file_path, template_name=template_name
        )

    def _handle_template_apply(
        self, output_path: str, template_name: str, data: str | None = None
    ) -> MCPToolResult:
        """Apply template."""
        return self._call_tool(
            "template_apply",
            output_path=output_path,
            template_name=template_name,
            data=data,
        )

    # =========================================================================
    # Advanced Operation Handlers (Chart, Validation, Query)
    # =========================================================================

    def _handle_chart_create(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Create a chart."""
        return self._call_tool(
            "chart_create", file_path=file_path, sheet=sheet, **kwargs
        )

    def _handle_chart_update(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Update a chart."""
        return self._call_tool(
            "chart_update", file_path=file_path, sheet=sheet, **kwargs
        )

    def _handle_validation_create(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Create data validation."""
        return self._call_tool(
            "validation_create", file_path=file_path, sheet=sheet, **kwargs
        )

    def _handle_cf_create(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Create conditional formatting."""
        return self._call_tool("cf_create", file_path=file_path, sheet=sheet, **kwargs)

    def _handle_named_range_create(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Create a named range."""
        return self._call_tool(
            "named_range_create", file_path=file_path, sheet=sheet, **kwargs
        )

    def _handle_table_create(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Create a table."""
        return self._call_tool(
            "table_create", file_path=file_path, sheet=sheet, **kwargs
        )

    def _handle_query_select(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Execute a query select."""
        return self._call_tool(
            "query_select", file_path=file_path, sheet=sheet, **kwargs
        )

    def _handle_query_find(
        self, file_path: str, sheet: str, **kwargs: Any
    ) -> MCPToolResult:
        """Execute a query find."""
        return self._call_tool("query_find", file_path=file_path, sheet=sheet, **kwargs)

    # =========================================================================
    # Workbook Operations
    # =========================================================================

    def _handle_workbook_properties_get(self, file_path: str) -> MCPToolResult:
        """Get workbook properties."""
        return self._call_tool("workbook_properties_get", file_path=file_path)

    def _handle_workbook_properties_set(
        self, file_path: str, properties: str
    ) -> MCPToolResult:
        """Set workbook properties."""
        return self._call_tool(
            "workbook_properties_set", file_path=file_path, properties=properties
        )

    def _handle_workbook_statistics(self, file_path: str) -> MCPToolResult:
        """Get workbook statistics."""
        return self._call_tool("workbook_statistics", file_path=file_path)

    def _handle_workbooks_compare(
        self, file_path1: str, file_path2: str
    ) -> MCPToolResult:
        """Compare two workbooks."""
        return self._call_tool(
            "workbooks_compare", file_path1=file_path1, file_path2=file_path2
        )

    def _handle_workbooks_merge(self, output_path: str, sources: str) -> MCPToolResult:
        """Merge multiple workbooks."""
        return self._call_tool(
            "workbooks_merge", output_path=output_path, sources=sources
        )

    # =========================================================================
    # Formula Operations
    # =========================================================================

    def _handle_formulas_recalculate(self, file_path: str) -> MCPToolResult:
        """Recalculate all formulas in workbook."""
        return self._call_tool("formulas_recalculate", file_path=file_path)

    def _handle_formulas_audit(
        self, file_path: str, sheet: str = "", cell: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Audit formula dependencies."""
        # formulas_audit only accepts file_path
        return self._call_tool("formulas_audit", file_path=file_path)

    def _handle_circular_refs_find(self, file_path: str) -> MCPToolResult:
        """Find circular references in formulas."""
        return self._call_tool("circular_refs_find", file_path=file_path)

    # =========================================================================
    # Data Operations
    # =========================================================================

    def _handle_data_connections_list(self, file_path: str) -> MCPToolResult:
        """List data connections."""
        return self._call_tool("data_connections_list", file_path=file_path)

    def _handle_data_refresh(
        self, file_path: str, connection_name: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Refresh data connection."""
        return self._call_tool(
            "data_refresh",
            file_path=file_path,
            connection_name=connection_name,
            **kwargs,
        )

    def _handle_links_update(self, file_path: str) -> MCPToolResult:
        """Update external links."""
        return self._call_tool("links_update", file_path=file_path)

    def _handle_links_break(self, file_path: str) -> MCPToolResult:
        """Break external links."""
        return self._call_tool("links_break", file_path=file_path)

    # =========================================================================
    # Import/Export Operations
    # =========================================================================

    def _handle_csv_import(
        self, file_path: str, csv_path: str = "", sheet: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Import CSV data."""
        return self._call_tool(
            "csv_import", file_path=file_path, csv_path=csv_path, sheet=sheet, **kwargs
        )

    def _handle_csv_export(
        self, file_path: str, output_path: str = "", sheet: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Export to CSV."""
        return self._call_tool(
            "csv_export",
            file_path=file_path,
            output_path=output_path,
            sheet=sheet,
            **kwargs,
        )

    def _handle_tsv_import(
        self, file_path: str, tsv_path: str = "", sheet: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Import TSV data."""
        return self._call_tool(
            "tsv_import", file_path=file_path, tsv_path=tsv_path, sheet=sheet, **kwargs
        )

    def _handle_tsv_export(
        self, file_path: str, output_path: str = "", sheet: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Export to TSV."""
        return self._call_tool(
            "tsv_export",
            file_path=file_path,
            output_path=output_path,
            sheet=sheet,
            **kwargs,
        )

    def _handle_json_import(
        self, file_path: str, json_path: str = "", sheet: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Import JSON data."""
        return self._call_tool(
            "json_import",
            file_path=file_path,
            json_path=json_path,
            sheet=sheet,
            **kwargs,
        )

    def _handle_json_export(
        self, file_path: str, output_path: str = "", sheet: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Export to JSON."""
        return self._call_tool(
            "json_export",
            file_path=file_path,
            output_path=output_path,
            sheet=sheet,
            **kwargs,
        )

    def _handle_xlsx_export(
        self, file_path: str, output_path: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Export to XLSX."""
        return self._call_tool(
            "xlsx_export", file_path=file_path, output_path=output_path, **kwargs
        )

    def _handle_html_export(
        self, file_path: str, output_path: str = "", sheet: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Export to HTML."""
        return self._call_tool(
            "html_export",
            file_path=file_path,
            output_path=output_path,
            sheet=sheet,
            **kwargs,
        )

    def _handle_pdf_export(
        self, file_path: str, output_path: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Export to PDF."""
        return self._call_tool(
            "pdf_export", file_path=file_path, output_path=output_path, **kwargs
        )

    def _handle_batch_import(
        self, file_path: str, sources: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Batch import from multiple sources."""
        return self._call_tool(
            "batch_import", file_path=file_path, sources=sources, **kwargs
        )

    def _handle_batch_export(
        self, file_path: str, format: str = "", output_dir: str = "", **kwargs: Any
    ) -> MCPToolResult:
        """Batch export to multiple formats."""
        return self._call_tool(
            "batch_export",
            file_path=file_path,
            format=format,
            output_dir=output_dir,
            **kwargs,
        )

    def _handle_format_auto_detect(self, file_path: str) -> MCPToolResult:
        """Auto-detect file format."""
        return self._call_tool("format_auto_detect", file_path=file_path)

    # =========================================================================
    # MCP Protocol Methods
    # =========================================================================

    def handle_message(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Handle an incoming MCP message.

        Args:
            message: JSON-RPC message.

        Returns:
            JSON-RPC response or None for notifications.
        """
        msg_id = message.get("id")
        method = message.get("method", "")
        params = message.get("params", {})

        try:
            # Rate limiting
            if not self._check_rate_limit():
                return self._error_response(
                    msg_id,
                    -32000,
                    "Rate limit exceeded",
                )

            # Route method
            if method == "initialize":
                return self._handle_initialize(msg_id, params)
            elif method == "tools/list":
                return self._handle_tools_list(msg_id)
            elif method == "tools/call":
                return self._handle_tools_call(msg_id, params)
            elif method == "notifications/initialized":
                return None  # No response for notifications
            else:
                return self._error_response(
                    msg_id,
                    -32601,
                    f"Method not found: {method}",
                )

        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            return self._error_response(msg_id, -32603, str(e))

    def _handle_initialize(
        self,
        msg_id: Any,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": MCPVersion.V1.value,
                "serverInfo": {
                    "name": self.config.name,
                    "version": self.config.version,
                },
                "capabilities": {
                    "tools": {},
                    "logging": {},
                },
            },
        }

    def _handle_tools_list(self, msg_id: Any) -> dict[str, Any]:
        """Handle tools/list request."""
        tools = [tool.to_schema() for tool in self._tools.values()]
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": tools},
        }

    def _handle_tools_call(
        self,
        msg_id: Any,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self._tools:
            return self._error_response(
                msg_id,
                -32602,
                f"Unknown tool: {tool_name}",
            )

        tool = self._tools[tool_name]
        if tool.handler is None:
            return self._error_response(
                msg_id,
                -32603,
                f"Tool has no handler: {tool_name}",
            )

        # Execute tool
        result = tool.handler(**arguments)

        # Audit log
        self._log_audit(tool_name, arguments, result)

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": result.content,
                "isError": result.is_error,
            },
        }

    def _error_response(
        self,
        msg_id: Any,
        code: int,
        message: str,
    ) -> dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message,
            },
        }

    def run(self) -> None:
        """Run the MCP server in stdio mode.

        Reads JSON-RPC messages from stdin and writes responses to stdout.
        """
        self.logger.info(f"Starting MCP server: {self.config.name}")

        while True:
            try:
                # Read message length
                line = sys.stdin.readline()
                if not line:
                    break

                # Parse JSON-RPC message
                message = json.loads(line)

                # Handle message
                response = self.handle_message(message)

                # Send response (if not a notification)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON: {e}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Server error: {e}")
                break

        self.logger.info("MCP server stopped")


def create_mcp_server(
    allowed_paths: list[str | Path] | None = None,
) -> MCPServer:
    """Create an MCP server with optional path restrictions.

    Args:
        allowed_paths: List of paths the server can access.

    Returns:
        Configured MCPServer instance.
    """
    config = MCPConfig(
        allowed_paths=[Path(p) for p in allowed_paths] if allowed_paths else [],
    )
    return MCPServer(config)


def main() -> None:
    """Entry point for MCP server CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="SpreadsheetDL MCP Server",
    )
    parser.add_argument(
        "--allowed-paths",
        nargs="*",
        help="Allowed file paths",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    # Create and run server
    server = create_mcp_server(args.allowed_paths)
    server.run()


if __name__ == "__main__":
    main()

__all__ = ["MCPServer", "create_mcp_server", "main"]
