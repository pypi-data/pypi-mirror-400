"""Chart and advanced visualization tools.

Provides MCP tools for:
- Chart creation and updates
- Conditional formatting
- Data validation
- Named ranges
- Tables
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl._mcp.models import MCPToolParameter, MCPToolResult


def register_chart_tools(
    registry: Any,
    validate_path: Any,
) -> None:
    """Register all chart and advanced tools.

    Args:
        registry: MCPToolRegistry instance
        validate_path: Path validation function
    """
    _register_chart_operations(registry, validate_path)
    _register_conditional_format_tools(registry, validate_path)
    _register_validation_tools(registry, validate_path)
    _register_named_range_tools(registry, validate_path)


def _register_chart_operations(registry: Any, validate_path: Any) -> None:
    """Register chart operation tools."""
    # chart_create
    registry.register(
        name="chart_create",
        description="Create a chart in the spreadsheet",
        handler=_make_chart_create_handler(validate_path),
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
                name="chart_type",
                type="string",
                description="Type of chart (bar, line, pie, area, scatter)",
            ),
            MCPToolParameter(
                name="data_range",
                type="string",
                description="Data range for the chart (e.g., 'A1:B10')",
            ),
            MCPToolParameter(
                name="title",
                type="string",
                description="Chart title",
                required=False,
            ),
            MCPToolParameter(
                name="position",
                type="string",
                description="Position for the chart (e.g., 'E1')",
                required=False,
            ),
        ],
        category="advanced_operations",
    )

    # chart_update
    registry.register(
        name="chart_update",
        description="Update an existing chart",
        handler=_make_chart_update_handler(validate_path),
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
                name="chart_id",
                type="string",
                description="Identifier or position of the chart",
            ),
            MCPToolParameter(
                name="properties",
                type="string",
                description="JSON object with updated properties",
            ),
        ],
        category="advanced_operations",
    )


def _register_conditional_format_tools(registry: Any, validate_path: Any) -> None:
    """Register conditional formatting tools."""
    # cf_create
    registry.register(
        name="cf_create",
        description="Create conditional formatting rule",
        handler=_make_cf_create_handler(validate_path),
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
                description="Cell range to apply formatting",
            ),
            MCPToolParameter(
                name="rule_type",
                type="string",
                description="Rule type (color_scale, data_bar, icon_set, cell_value, formula)",
            ),
            MCPToolParameter(
                name="config",
                type="string",
                description="JSON configuration for the rule",
            ),
        ],
        category="advanced_operations",
    )


def _register_validation_tools(registry: Any, validate_path: Any) -> None:
    """Register data validation tools."""
    # validation_create
    registry.register(
        name="validation_create",
        description="Create data validation rule",
        handler=_make_validation_create_handler(validate_path),
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
                description="Cell range to validate",
            ),
            MCPToolParameter(
                name="validation_type",
                type="string",
                description="Validation type (list, number, date, text_length, custom)",
            ),
            MCPToolParameter(
                name="config",
                type="string",
                description="JSON configuration for validation",
            ),
        ],
        category="advanced_operations",
    )


def _register_named_range_tools(registry: Any, validate_path: Any) -> None:
    """Register named range and table tools."""
    # named_range_create
    registry.register(
        name="named_range_create",
        description="Create a named range",
        handler=_make_named_range_create_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="name",
                type="string",
                description="Name for the range",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet name",
            ),
            MCPToolParameter(
                name="range",
                type="string",
                description="Cell range (e.g., 'A1:B10')",
            ),
        ],
        category="advanced_operations",
    )

    # table_create
    registry.register(
        name="table_create",
        description="Create a table from a range",
        handler=_make_table_create_handler(validate_path),
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
                description="Cell range for the table",
            ),
            MCPToolParameter(
                name="name",
                type="string",
                description="Table name",
                required=False,
            ),
            MCPToolParameter(
                name="has_headers",
                type="boolean",
                description="Whether the first row contains headers",
                required=False,
            ),
        ],
        category="advanced_operations",
    )

    # query_select
    registry.register(
        name="query_select",
        description="Query data using SQL-like syntax",
        handler=_make_query_select_handler(validate_path),
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
                name="query",
                type="string",
                description="Query string (e.g., 'SELECT A, B WHERE C > 10')",
            ),
        ],
        category="advanced_operations",
    )

    # query_find
    registry.register(
        name="query_find",
        description="Find rows matching criteria",
        handler=_make_query_find_handler(validate_path),
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
                name="criteria",
                type="string",
                description="JSON object with search criteria",
            ),
        ],
        category="advanced_operations",
    )


# =============================================================================
# Handler Factory Functions
# =============================================================================


def _make_chart_create_handler(validate_path: Any) -> Any:
    """Create chart_create handler."""

    def handler(
        file_path: str,
        sheet: str,
        chart_type: str,
        data_range: str,
        title: str | None = None,
        position: str | None = None,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            chart_spec = {
                "type": chart_type,
                "data_range": data_range,
                "title": title,
                "position": position or "E1",
            }
            chart_id = editor.create_chart(sheet, chart_spec)
            editor.save()

            return MCPToolResult.json(
                {
                    "success": True,
                    "sheet": sheet,
                    "chart_type": chart_type,
                    "chart_id": chart_id,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_chart_update_handler(validate_path: Any) -> Any:
    """Create chart_update handler."""
    import json

    def handler(
        file_path: str,
        sheet: str,
        chart_id: str,
        properties: str,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            props = json.loads(properties)
            editor.update_chart(sheet, chart_id, props)
            editor.save()

            return MCPToolResult.json(
                {"success": True, "sheet": sheet, "chart_id": chart_id}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_cf_create_handler(validate_path: Any) -> Any:
    """Create cf_create handler."""
    import json

    def handler(
        file_path: str,
        sheet: str,
        range: str,
        rule_type: str,
        config: str,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            cfg = json.loads(config)
            cf_spec = {
                "range": range,
                "rule_type": rule_type,
                "config": cfg,
            }
            editor.add_conditional_format(sheet, cf_spec)
            editor.save()

            return MCPToolResult.json(
                {
                    "success": True,
                    "sheet": sheet,
                    "range": range,
                    "rule_type": rule_type,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_validation_create_handler(validate_path: Any) -> Any:
    """Create validation_create handler."""
    import json

    def handler(
        file_path: str,
        sheet: str,
        range: str,
        validation_type: str,
        config: str,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            cfg = json.loads(config)
            validation_spec = {
                "range": range,
                "type": validation_type,
                "config": cfg,
            }
            editor.add_data_validation(sheet, validation_spec)
            editor.save()

            return MCPToolResult.json(
                {
                    "success": True,
                    "sheet": sheet,
                    "range": range,
                    "validation_type": validation_type,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_named_range_create_handler(validate_path: Any) -> Any:
    """Create named_range_create handler."""

    def handler(
        file_path: str,
        name: str,
        sheet: str,
        range: str,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            editor.create_named_range(name, range, sheet)
            editor.save()

            return MCPToolResult.json(
                {
                    "success": True,
                    "name": name,
                    "sheet": sheet,
                    "range": range,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_table_create_handler(validate_path: Any) -> Any:
    """Create table_create handler."""

    def handler(
        file_path: str,
        sheet: str,
        range: str,
        name: str | None = None,
        has_headers: bool = True,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            # create_table expects: sheet_name, range_ref, name, style
            # Build fully qualified range reference
            range_ref = f"{sheet}.{range}"
            table_name = editor.create_table(
                sheet_name=sheet,
                range_ref=range_ref,
                name=name or "Table1",
                style=None,
            )
            editor.save()

            return MCPToolResult.json(
                {
                    "success": True,
                    "sheet": sheet,
                    "range": range,
                    "table_name": table_name,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_query_select_handler(validate_path: Any) -> Any:
    """Create query_select handler."""

    def handler(file_path: str, sheet: str, query: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            results = editor.query_data(sheet, query)

            return MCPToolResult.json(
                {"sheet": sheet, "query": query, "results": results}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_query_find_handler(validate_path: Any) -> Any:
    """Create query_find handler."""
    import json

    def handler(file_path: str, sheet: str, criteria: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            crit = json.loads(criteria)
            matches = editor.find_rows(sheet, crit)

            return MCPToolResult.json(
                {"sheet": sheet, "criteria": crit, "matches": matches}
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler
