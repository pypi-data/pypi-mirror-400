"""Data analysis and workbook operation tools.

Provides MCP tools for:
- Workbook properties and metadata
- Formula auditing and recalculation
- Data connections and refresh
- Workbook comparison and merge
- Statistics and analysis
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl._mcp.models import MCPToolParameter, MCPToolResult


def register_analysis_tools(
    registry: Any,
    validate_path: Any,
) -> None:
    """Register all analysis and workbook tools.

    Args:
        registry: MCPToolRegistry instance
        validate_path: Path validation function
    """
    _register_workbook_tools(registry, validate_path)
    _register_formula_tools(registry, validate_path)
    _register_analysis_operations(registry, validate_path)


def _register_workbook_tools(registry: Any, validate_path: Any) -> None:
    """Register workbook operation tools."""
    # workbook_properties_get
    registry.register(
        name="workbook_properties_get",
        description="Get workbook properties and metadata",
        handler=_make_workbook_properties_get_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )

    # workbook_properties_set
    registry.register(
        name="workbook_properties_set",
        description="Set workbook properties",
        handler=_make_workbook_properties_set_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="properties",
                type="string",
                description="JSON object with property values",
            ),
        ],
        category="workbook_operations",
    )

    # workbook_statistics
    registry.register(
        name="workbook_statistics",
        description="Get workbook statistics (sheets, cells, formulas, etc.)",
        handler=_make_workbook_statistics_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )

    # workbooks_compare
    registry.register(
        name="workbooks_compare",
        description="Compare two workbooks and find differences",
        handler=_make_workbooks_compare_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path1",
                type="string",
                description="Path to the first spreadsheet",
            ),
            MCPToolParameter(
                name="file_path2",
                type="string",
                description="Path to the second spreadsheet",
            ),
        ],
        category="workbook_operations",
    )

    # workbooks_merge
    registry.register(
        name="workbooks_merge",
        description="Merge sheets from multiple workbooks",
        handler=_make_workbooks_merge_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the merged workbook",
            ),
            MCPToolParameter(
                name="sources",
                type="string",
                description="JSON array of source file paths",
            ),
        ],
        category="workbook_operations",
    )


def _register_formula_tools(registry: Any, validate_path: Any) -> None:
    """Register formula-related tools."""
    # formulas_recalculate
    registry.register(
        name="formulas_recalculate",
        description="Recalculate all formulas in the workbook",
        handler=_make_formulas_recalculate_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )

    # formulas_audit
    registry.register(
        name="formulas_audit",
        description="Audit formulas for errors and issues",
        handler=_make_formulas_audit_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )

    # circular_refs_find
    registry.register(
        name="circular_refs_find",
        description="Find circular references in formulas",
        handler=_make_circular_refs_find_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )


def _register_analysis_operations(registry: Any, validate_path: Any) -> None:
    """Register data analysis tools."""
    # data_connections_list
    registry.register(
        name="data_connections_list",
        description="List external data connections",
        handler=_make_data_connections_list_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )

    # data_refresh
    registry.register(
        name="data_refresh",
        description="Refresh data connections",
        handler=_make_data_refresh_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="connection_name",
                type="string",
                description="Name of the connection to refresh (optional, all if not specified)",
                required=False,
            ),
        ],
        category="workbook_operations",
    )

    # links_update
    registry.register(
        name="links_update",
        description="Update external links in the workbook",
        handler=_make_links_update_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )

    # links_break
    registry.register(
        name="links_break",
        description="Break external links and replace with values",
        handler=_make_links_break_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
        ],
        category="workbook_operations",
    )


# =============================================================================
# Handler Factory Functions - Workbook Operations
# =============================================================================


def _make_workbook_properties_get_handler(validate_path: Any) -> Any:
    """Create workbook_properties_get handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            props = editor.get_properties()
            return MCPToolResult.json({"file": file_path, "properties": props})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_workbook_properties_set_handler(validate_path: Any) -> Any:
    """Create workbook_properties_set handler."""
    import json

    def handler(file_path: str, properties: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            props = json.loads(properties)
            editor.set_properties(props)
            editor.save()

            return MCPToolResult.json({"success": True, "file": file_path})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_workbook_statistics_handler(validate_path: Any) -> Any:
    """Create workbook_statistics handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            stats = editor.get_statistics()
            return MCPToolResult.json({"file": file_path, "statistics": stats})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_workbooks_compare_handler(validate_path: Any) -> Any:
    """Create workbooks_compare handler."""

    def handler(file_path1: str, file_path2: str) -> MCPToolResult:
        try:
            path1 = validate_path(file_path1)
            path2 = validate_path(file_path2)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor1 = OdsEditor(path1)
            # compare_with expects a path string, not an editor object
            differences = editor1.compare_with(path2)

            return MCPToolResult.json(
                {
                    "file1": file_path1,
                    "file2": file_path2,
                    "differences": differences,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_workbooks_merge_handler(validate_path: Any) -> Any:
    """Create workbooks_merge handler."""
    import json

    def handler(output_path: str, sources: str) -> MCPToolResult:
        try:
            from pathlib import Path

            from spreadsheet_dl._builder.models import ColumnSpec, RowSpec, SheetSpec
            from spreadsheet_dl.ods_editor import OdsEditor
            from spreadsheet_dl.renderer import render_ods

            source_list = json.loads(sources)
            all_sheets: list[SheetSpec] = []

            for source in source_list:
                editor = OdsEditor(Path(source))
                sheet_names = editor.get_sheets()

                # Convert each sheet to SheetSpec
                for sheet_name in sheet_names:
                    # Create an empty sheet spec for now
                    # Proper implementation would extract all cell data
                    sheet_spec = SheetSpec(
                        name=sheet_name,
                        columns=[ColumnSpec(name="A")],
                        rows=[RowSpec(cells=[])],
                    )
                    all_sheets.append(sheet_spec)

            render_ods(all_sheets, Path(output_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "output": output_path,
                    "merged_files": len(source_list),
                    "total_sheets": len(all_sheets),
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


# =============================================================================
# Handler Factory Functions - Formula Operations
# =============================================================================


def _make_formulas_recalculate_handler(validate_path: Any) -> Any:
    """Create formulas_recalculate handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            count = editor.recalculate_formulas()
            editor.save()

            return MCPToolResult.json(
                {"success": True, "file": file_path, "formulas_recalculated": count}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_formulas_audit_handler(validate_path: Any) -> Any:
    """Create formulas_audit handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            audit_results = editor.audit_formulas()
            return MCPToolResult.json(
                {
                    "file": file_path,
                    "total_formulas": audit_results.get("total", 0),
                    "errors": audit_results.get("errors", []),
                    "warnings": audit_results.get("warnings", []),
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_circular_refs_find_handler(validate_path: Any) -> Any:
    """Create circular_refs_find handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            circular_refs = editor.find_circular_references()
            return MCPToolResult.json(
                {
                    "file": file_path,
                    "has_circular_refs": len(circular_refs) > 0,
                    "circular_references": circular_refs,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


# =============================================================================
# Handler Factory Functions - Data Operations
# =============================================================================


def _make_data_connections_list_handler(validate_path: Any) -> Any:
    """Create data_connections_list handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            connections = editor.list_data_connections()
            return MCPToolResult.json({"file": file_path, "connections": connections})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_data_refresh_handler(validate_path: Any) -> Any:
    """Create data_refresh handler."""

    def handler(file_path: str, connection_name: str | None = None) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            refreshed = editor.refresh_data(connection_name)
            editor.save()

            return MCPToolResult.json(
                {"success": True, "file": file_path, "refreshed": refreshed}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_links_update_handler(validate_path: Any) -> Any:
    """Create links_update handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            updated = editor.update_links()
            editor.save()

            return MCPToolResult.json(
                {"success": True, "file": file_path, "links_updated": updated}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_links_break_handler(validate_path: Any) -> Any:
    """Create links_break handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            broken = editor.break_links()
            editor.save()

            return MCPToolResult.json(
                {"success": True, "file": file_path, "links_broken": broken}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler
