"""Spreadsheet cell and structure operation tools.

Provides MCP tools for:
- Cell operations (get, set, clear, copy, move, batch, find, replace, merge)
- Row operations (insert, delete, hide)
- Column operations (insert, delete, hide)
- Sheet operations (create, delete, copy)
- Freeze pane operations

Note: Many structure operations are not yet implemented in OdsEditor.
These tools return appropriate error messages indicating unavailable functionality.
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl._mcp.models import MCPToolParameter, MCPToolResult


def register_spreadsheet_tools(
    registry: Any,
    validate_path: Any,
) -> None:
    """Register all spreadsheet operation tools.

    Args:
        registry: MCPToolRegistry instance
        validate_path: Path validation function
    """
    _register_cell_tools(registry, validate_path)
    _register_row_tools(registry, validate_path)
    _register_column_tools(registry, validate_path)
    _register_sheet_tools(registry, validate_path)
    _register_freeze_tools(registry, validate_path)


def _register_cell_tools(registry: Any, validate_path: Any) -> None:
    """Register cell operation tools."""
    # cell_get
    registry.register(
        name="cell_get",
        description="Get the value of a specific cell",
        handler=_make_cell_get_handler(validate_path),
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
                name="cell",
                type="string",
                description="Cell reference (e.g., 'A1', 'B5')",
            ),
        ],
        category="cell_operations",
    )

    # cell_set
    registry.register(
        name="cell_set",
        description="Set the value of a specific cell",
        handler=_make_cell_set_handler(validate_path),
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
                name="cell",
                type="string",
                description="Cell reference (e.g., 'A1', 'B5')",
            ),
            MCPToolParameter(
                name="value",
                type="string",
                description="Value to set",
            ),
        ],
        category="cell_operations",
    )

    # cell_clear
    registry.register(
        name="cell_clear",
        description="Clear the value and formatting of a cell",
        handler=_make_cell_clear_handler(validate_path),
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
                name="cell",
                type="string",
                description="Cell reference (e.g., 'A1', 'B5')",
            ),
        ],
        category="cell_operations",
    )

    # cell_copy
    registry.register(
        name="cell_copy",
        description="Copy a cell or range to another location",
        handler=_make_cell_copy_handler(validate_path),
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
                name="source",
                type="string",
                description="Source cell or range (e.g., 'A1' or 'A1:B5')",
            ),
            MCPToolParameter(
                name="destination",
                type="string",
                description="Destination cell (e.g., 'C1')",
            ),
        ],
        category="cell_operations",
    )

    # cell_move
    registry.register(
        name="cell_move",
        description="Move a cell or range to another location",
        handler=_make_cell_move_handler(validate_path),
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
                name="source",
                type="string",
                description="Source cell or range",
            ),
            MCPToolParameter(
                name="destination",
                type="string",
                description="Destination cell",
            ),
        ],
        category="cell_operations",
    )

    # cell_batch_get
    registry.register(
        name="cell_batch_get",
        description="Get values of multiple cells in a single operation",
        handler=_make_cell_batch_get_handler(validate_path),
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
                name="cells",
                type="string",
                description="Comma-separated cell references or range (e.g., 'A1,B2,C3' or 'A1:C10')",
            ),
        ],
        category="cell_operations",
    )

    # cell_batch_set
    registry.register(
        name="cell_batch_set",
        description="Set values of multiple cells in a single operation",
        handler=_make_cell_batch_set_handler(validate_path),
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
                name="updates",
                type="string",
                description='JSON object mapping cell refs to values (e.g., \'{"A1": 1, "B1": 2}\')',
            ),
        ],
        category="cell_operations",
    )

    # cell_find
    registry.register(
        name="cell_find",
        description="Find cells containing a specific value or pattern",
        handler=_make_cell_find_handler(validate_path),
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
                name="pattern",
                type="string",
                description="Value or regex pattern to find",
            ),
            MCPToolParameter(
                name="match_case",
                type="boolean",
                description="Whether to match case (default: false)",
                required=False,
            ),
        ],
        category="cell_operations",
    )

    # cell_replace
    registry.register(
        name="cell_replace",
        description="Replace values in cells matching a pattern",
        handler=_make_cell_replace_handler(validate_path),
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
                name="find",
                type="string",
                description="Value or pattern to find",
            ),
            MCPToolParameter(
                name="replace",
                type="string",
                description="Replacement value",
            ),
        ],
        category="cell_operations",
    )

    # cell_merge
    registry.register(
        name="cell_merge",
        description="Merge a range of cells",
        handler=_make_cell_merge_handler(validate_path),
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
                description="Cell range to merge (e.g., 'A1:C3')",
            ),
        ],
        category="cell_operations",
    )

    # cell_unmerge
    registry.register(
        name="cell_unmerge",
        description="Unmerge a previously merged cell range",
        handler=_make_cell_unmerge_handler(validate_path),
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
                description="Cell range to unmerge",
            ),
        ],
        category="cell_operations",
    )


def _register_row_tools(registry: Any, validate_path: Any) -> None:
    """Register row operation tools."""
    # row_insert
    registry.register(
        name="row_insert",
        description="Insert one or more rows at the specified position",
        handler=_make_row_insert_handler(validate_path),
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
                description="Row number where to insert (1-based)",
            ),
            MCPToolParameter(
                name="count",
                type="integer",
                description="Number of rows to insert",
                required=False,
            ),
        ],
        category="structure_operations",
    )

    # row_delete
    registry.register(
        name="row_delete",
        description="Delete one or more rows",
        handler=_make_row_delete_handler(validate_path),
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
                description="Row number to delete (1-based)",
            ),
            MCPToolParameter(
                name="count",
                type="integer",
                description="Number of rows to delete",
                required=False,
            ),
        ],
        category="structure_operations",
    )

    # row_hide
    registry.register(
        name="row_hide",
        description="Hide or unhide rows",
        handler=_make_row_hide_handler(validate_path),
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
                description="Row number (1-based)",
            ),
            MCPToolParameter(
                name="hidden",
                type="boolean",
                description="Whether to hide (true) or show (false)",
            ),
        ],
        category="structure_operations",
    )


def _register_column_tools(registry: Any, validate_path: Any) -> None:
    """Register column operation tools."""
    # column_insert
    registry.register(
        name="column_insert",
        description="Insert one or more columns at the specified position",
        handler=_make_column_insert_handler(validate_path),
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
                name="column",
                type="string",
                description="Column letter where to insert (e.g., 'A', 'B')",
            ),
            MCPToolParameter(
                name="count",
                type="integer",
                description="Number of columns to insert",
                required=False,
            ),
        ],
        category="structure_operations",
    )

    # column_delete
    registry.register(
        name="column_delete",
        description="Delete one or more columns",
        handler=_make_column_delete_handler(validate_path),
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
                name="column",
                type="string",
                description="Column letter to delete",
            ),
            MCPToolParameter(
                name="count",
                type="integer",
                description="Number of columns to delete",
                required=False,
            ),
        ],
        category="structure_operations",
    )

    # column_hide
    registry.register(
        name="column_hide",
        description="Hide or unhide columns",
        handler=_make_column_hide_handler(validate_path),
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
                name="column",
                type="string",
                description="Column letter",
            ),
            MCPToolParameter(
                name="hidden",
                type="boolean",
                description="Whether to hide (true) or show (false)",
            ),
        ],
        category="structure_operations",
    )


def _register_sheet_tools(registry: Any, validate_path: Any) -> None:
    """Register sheet operation tools."""
    # sheet_create
    registry.register(
        name="sheet_create",
        description="Create a new sheet in the workbook",
        handler=_make_sheet_create_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Name for the new sheet",
            ),
        ],
        category="structure_operations",
    )

    # sheet_delete
    registry.register(
        name="sheet_delete",
        description="Delete a sheet from the workbook",
        handler=_make_sheet_delete_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Name of the sheet to delete",
            ),
        ],
        category="structure_operations",
    )

    # sheet_copy
    registry.register(
        name="sheet_copy",
        description="Copy a sheet within the workbook",
        handler=_make_sheet_copy_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Name of the sheet to copy",
            ),
            MCPToolParameter(
                name="new_name",
                type="string",
                description="Name for the copy",
            ),
        ],
        category="structure_operations",
    )


def _register_freeze_tools(registry: Any, validate_path: Any) -> None:
    """Register freeze pane tools."""
    # freeze_set
    registry.register(
        name="freeze_set",
        description="Set freeze panes at the specified cell",
        handler=_make_freeze_set_handler(validate_path),
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
                name="cell",
                type="string",
                description="Cell reference for freeze position (e.g., 'B2' freezes row 1 and column A)",
            ),
        ],
        category="structure_operations",
    )

    # freeze_clear
    registry.register(
        name="freeze_clear",
        description="Remove freeze panes from a sheet",
        handler=_make_freeze_clear_handler(validate_path),
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
        ],
        category="structure_operations",
    )


# =============================================================================
# Handler Factory Functions
# =============================================================================


def _make_cell_get_handler(validate_path: Any) -> Any:
    """Create cell_get handler with path validation."""

    def handler(file_path: str, sheet: str, cell: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            value = editor.get_cell_value(sheet, cell)
            return MCPToolResult.json({"cell": cell, "sheet": sheet, "value": value})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_set_handler(validate_path: Any) -> Any:
    """Create cell_set handler with path validation."""

    def handler(file_path: str, sheet: str, cell: str, value: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            editor.set_cell_value(sheet, cell, value)
            editor.save()
            return MCPToolResult.json(
                {"success": True, "cell": cell, "sheet": sheet, "value": value}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_clear_handler(validate_path: Any) -> Any:
    """Create cell_clear handler with path validation."""

    def handler(file_path: str, sheet: str, cell: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            editor.clear_cell(sheet, cell)
            editor.save()
            return MCPToolResult.json({"success": True, "cell": cell, "sheet": sheet})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_copy_handler(validate_path: Any) -> Any:
    """Create cell_copy handler with path validation."""

    def handler(
        file_path: str, sheet: str, source: str, destination: str
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            editor.copy_cells(sheet, source, destination)
            editor.save()
            return MCPToolResult.json(
                {
                    "success": True,
                    "source": source,
                    "destination": destination,
                    "sheet": sheet,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_move_handler(validate_path: Any) -> Any:
    """Create cell_move handler with path validation."""

    def handler(
        file_path: str, sheet: str, source: str, destination: str
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            editor.move_cells(sheet, source, destination)
            editor.save()
            return MCPToolResult.json(
                {
                    "success": True,
                    "source": source,
                    "destination": destination,
                    "sheet": sheet,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_batch_get_handler(validate_path: Any) -> Any:
    """Create cell_batch_get handler with path validation."""

    def handler(file_path: str, sheet: str, cells: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)

            # Parse cells (comma-separated or range)
            if ":" in cells:
                # OdsEditor doesn't have get_range_values, iterate manually
                # Parse range and get individual cells
                from spreadsheet_dl.ods_editor import OdsEditor as OE

                start_ref, end_ref = cells.split(":", 1)
                start_row, start_col = OE._parse_cell_reference(start_ref)
                end_row, end_col = OE._parse_cell_reference(end_ref)

                values = {}
                for row in range(start_row, end_row + 1):
                    for col in range(start_col, end_col + 1):
                        col_letter = OE._col_index_to_letter(col)
                        cell_ref = f"{col_letter}{row + 1}"
                        values[cell_ref] = editor.get_cell_value(sheet, cell_ref)
            else:
                cell_list = [c.strip() for c in cells.split(",")]
                values = {c: editor.get_cell_value(sheet, c) for c in cell_list}

            return MCPToolResult.json({"sheet": sheet, "values": values})
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_batch_set_handler(validate_path: Any) -> Any:
    """Create cell_batch_set handler with path validation."""
    import json

    def handler(file_path: str, sheet: str, updates: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            update_dict = json.loads(updates)

            for cell, value in update_dict.items():
                editor.set_cell_value(sheet, cell, value)

            editor.save()
            return MCPToolResult.json(
                {"success": True, "sheet": sheet, "updated_cells": len(update_dict)}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_find_handler(validate_path: Any) -> Any:
    """Create cell_find handler with path validation."""

    def handler(
        file_path: str, sheet: str, pattern: str, match_case: bool = False
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            # OdsEditor.find_cells uses match_case parameter, not use_regex
            matches = editor.find_cells(sheet, pattern, match_case=match_case)
            return MCPToolResult.json(
                {"sheet": sheet, "pattern": pattern, "matches": matches}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_replace_handler(validate_path: Any) -> Any:
    """Create cell_replace handler with path validation."""

    def handler(file_path: str, sheet: str, find: str, replace: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            count = editor.replace_cells(sheet, find, replace)
            editor.save()
            return MCPToolResult.json(
                {
                    "success": True,
                    "sheet": sheet,
                    "find": find,
                    "replace": replace,
                    "count": count,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_merge_handler(validate_path: Any) -> Any:
    """Create cell_merge handler with path validation."""

    def handler(file_path: str, sheet: str, range: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have merge_cells method
            return MCPToolResult.error(
                "Cell merging not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for cell merge operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cell_unmerge_handler(validate_path: Any) -> Any:
    """Create cell_unmerge handler with path validation."""

    def handler(file_path: str, sheet: str, range: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have unmerge_cells method
            return MCPToolResult.error(
                "Cell unmerging not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for cell merge operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_row_insert_handler(validate_path: Any) -> Any:
    """Create row_insert handler with path validation."""

    def handler(file_path: str, sheet: str, row: int, count: int = 1) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have insert_rows method
            return MCPToolResult.error(
                "Row insertion not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for row operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_row_delete_handler(validate_path: Any) -> Any:
    """Create row_delete handler with path validation."""

    def handler(file_path: str, sheet: str, row: int, count: int = 1) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have delete_rows method
            return MCPToolResult.error(
                "Row deletion not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for row operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_row_hide_handler(validate_path: Any) -> Any:
    """Create row_hide handler with path validation."""

    def handler(file_path: str, sheet: str, row: int, hidden: bool) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_row_hidden method
            return MCPToolResult.error(
                "Row visibility control not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for row operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_column_insert_handler(validate_path: Any) -> Any:
    """Create column_insert handler with path validation."""

    def handler(
        file_path: str, sheet: str, column: str, count: int = 1
    ) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have insert_columns method
            return MCPToolResult.error(
                "Column insertion not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for column operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_column_delete_handler(validate_path: Any) -> Any:
    """Create column_delete handler with path validation."""

    def handler(
        file_path: str, sheet: str, column: str, count: int = 1
    ) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have delete_columns method
            return MCPToolResult.error(
                "Column deletion not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for column operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_column_hide_handler(validate_path: Any) -> Any:
    """Create column_hide handler with path validation."""

    def handler(file_path: str, sheet: str, column: str, hidden: bool) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_column_hidden method
            return MCPToolResult.error(
                "Column visibility control not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for column operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_sheet_create_handler(validate_path: Any) -> Any:
    """Create sheet_create handler with path validation."""

    def handler(file_path: str, sheet: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have create_sheet method
            return MCPToolResult.error(
                "Sheet creation not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for sheet operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_sheet_delete_handler(validate_path: Any) -> Any:
    """Create sheet_delete handler with path validation."""

    def handler(file_path: str, sheet: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have delete_sheet method
            return MCPToolResult.error(
                "Sheet deletion not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for sheet operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_sheet_copy_handler(validate_path: Any) -> Any:
    """Create sheet_copy handler with path validation."""

    def handler(file_path: str, sheet: str, new_name: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have copy_sheet method
            return MCPToolResult.error(
                "Sheet copying not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for sheet operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_freeze_set_handler(validate_path: Any) -> Any:
    """Create freeze_set handler with path validation."""

    def handler(file_path: str, sheet: str, cell: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have set_freeze_panes method
            return MCPToolResult.error(
                "Freeze panes not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for freeze pane operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_freeze_clear_handler(validate_path: Any) -> Any:
    """Create freeze_clear handler with path validation."""

    def handler(file_path: str, sheet: str) -> MCPToolResult:
        try:
            validate_path(file_path)
            # OdsEditor doesn't have clear_freeze_panes method
            return MCPToolResult.error(
                "Freeze panes not yet implemented for ODS files. "
                "Use SpreadsheetBuilder for freeze pane operations."
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler
