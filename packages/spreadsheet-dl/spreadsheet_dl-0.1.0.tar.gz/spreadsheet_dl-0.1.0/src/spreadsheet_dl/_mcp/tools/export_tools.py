"""Import/export operation tools.

Provides MCP tools for:
- CSV import/export
- TSV import/export
- JSON import/export
- XLSX import/export
- XML import/export
- HTML export
- PDF export
- Batch import/export
- Format auto-detection
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from spreadsheet_dl._mcp.models import MCPToolParameter, MCPToolResult


def register_export_tools(
    registry: Any,
    validate_path: Any,
) -> None:
    """Register all import/export tools.

    Args:
        registry: MCPToolRegistry instance
        validate_path: Path validation function
    """
    _register_import_tools(registry, validate_path)
    _register_export_operations(registry, validate_path)
    _register_batch_tools(registry, validate_path)


def _register_import_tools(registry: Any, validate_path: Any) -> None:
    """Register import tools."""
    # csv_import
    registry.register(
        name="csv_import",
        description="Import data from a CSV file",
        handler=_make_csv_import_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file to create",
            ),
            MCPToolParameter(
                name="csv_path",
                type="string",
                description="Path to the CSV file to import",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Target sheet name",
                required=False,
            ),
            MCPToolParameter(
                name="delimiter",
                type="string",
                description="Field delimiter (default: comma)",
                required=False,
            ),
        ],
        category="import_export",
    )

    # tsv_import
    registry.register(
        name="tsv_import",
        description="Import data from a TSV file",
        handler=_make_tsv_import_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file to create",
            ),
            MCPToolParameter(
                name="tsv_path",
                type="string",
                description="Path to the TSV file to import",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Target sheet name",
                required=False,
            ),
        ],
        category="import_export",
    )

    # json_import
    registry.register(
        name="json_import",
        description="Import data from a JSON file",
        handler=_make_json_import_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file to create",
            ),
            MCPToolParameter(
                name="json_path",
                type="string",
                description="Path to the JSON file to import",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Target sheet name",
                required=False,
            ),
        ],
        category="import_export",
    )

    # xlsx_import
    registry.register(
        name="xlsx_import",
        description="Import data from an XLSX file",
        handler=_make_xlsx_import_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the ODS file to create",
            ),
            MCPToolParameter(
                name="xlsx_path",
                type="string",
                description="Path to the XLSX file to import",
            ),
        ],
        category="import_export",
    )

    # format_auto_detect
    registry.register(
        name="format_auto_detect",
        description="Automatically detect the format of a file",
        handler=_make_format_auto_detect_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the file to analyze",
            ),
        ],
        category="import_export",
    )


def _register_export_operations(registry: Any, validate_path: Any) -> None:
    """Register export tools."""
    # csv_export
    registry.register(
        name="csv_export",
        description="Export data to CSV format",
        handler=_make_csv_export_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the output CSV file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet to export",
                required=False,
            ),
            MCPToolParameter(
                name="delimiter",
                type="string",
                description="Field delimiter (default: comma)",
                required=False,
            ),
        ],
        category="import_export",
    )

    # tsv_export
    registry.register(
        name="tsv_export",
        description="Export data to TSV format",
        handler=_make_tsv_export_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the output TSV file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet to export",
                required=False,
            ),
        ],
        category="import_export",
    )

    # json_export
    registry.register(
        name="json_export",
        description="Export data to JSON format",
        handler=_make_json_export_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the output JSON file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet to export",
                required=False,
            ),
        ],
        category="import_export",
    )

    # xlsx_export
    registry.register(
        name="xlsx_export",
        description="Export to XLSX format",
        handler=_make_xlsx_export_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the output XLSX file",
            ),
        ],
        category="import_export",
    )

    # html_export
    registry.register(
        name="html_export",
        description="Export to HTML format",
        handler=_make_html_export_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the output HTML file",
            ),
            MCPToolParameter(
                name="sheet",
                type="string",
                description="Sheet to export",
                required=False,
            ),
        ],
        category="import_export",
    )

    # pdf_export
    registry.register(
        name="pdf_export",
        description="Export to PDF format",
        handler=_make_pdf_export_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="output_path",
                type="string",
                description="Path for the output PDF file",
            ),
            MCPToolParameter(
                name="options",
                type="string",
                description="JSON object with PDF options",
                required=False,
            ),
        ],
        category="import_export",
    )


def _register_batch_tools(registry: Any, validate_path: Any) -> None:
    """Register batch import/export tools."""
    # batch_import
    registry.register(
        name="batch_import",
        description="Import multiple files in batch",
        handler=_make_batch_import_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the target spreadsheet file",
            ),
            MCPToolParameter(
                name="sources",
                type="string",
                description="JSON array of source file paths",
            ),
        ],
        category="import_export",
    )

    # batch_export
    registry.register(
        name="batch_export",
        description="Export sheets to multiple files",
        handler=_make_batch_export_handler(validate_path),
        parameters=[
            MCPToolParameter(
                name="file_path",
                type="string",
                description="Path to the spreadsheet file",
            ),
            MCPToolParameter(
                name="output_dir",
                type="string",
                description="Output directory for exported files",
            ),
            MCPToolParameter(
                name="format",
                type="string",
                description="Export format (csv, json, xlsx)",
            ),
        ],
        category="import_export",
    )


# =============================================================================
# Handler Factory Functions
# =============================================================================


def _make_csv_import_handler(validate_path: Any) -> Any:
    """Create csv_import handler."""

    def handler(
        file_path: str,
        csv_path: str,
        sheet: str | None = None,
        delimiter: str = ",",
    ) -> MCPToolResult:
        try:
            from pathlib import Path

            from spreadsheet_dl.adapters import CsvAdapter

            adapter = CsvAdapter()
            sheets = adapter.load(Path(csv_path), delimiter=delimiter)

            if sheet and sheets:
                sheets[0] = replace(sheets[0], name=sheet)

            # Save to target file
            from spreadsheet_dl.renderer import render_ods

            render_ods(sheets, Path(file_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "imported_from": csv_path,
                    "created_file": file_path,
                    "sheets": [s.name for s in sheets],
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_tsv_import_handler(validate_path: Any) -> Any:
    """Create tsv_import handler."""

    def handler(
        file_path: str,
        tsv_path: str,
        sheet: str | None = None,
    ) -> MCPToolResult:
        try:
            from pathlib import Path

            from spreadsheet_dl.adapters import TsvAdapter

            adapter = TsvAdapter()
            sheets = adapter.load(Path(tsv_path))

            if sheet and sheets:
                sheets[0] = replace(sheets[0], name=sheet)

            from spreadsheet_dl.renderer import render_ods

            render_ods(sheets, Path(file_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "imported_from": tsv_path,
                    "created_file": file_path,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_json_import_handler(validate_path: Any) -> Any:
    """Create json_import handler."""

    def handler(
        file_path: str,
        json_path: str,
        sheet: str | None = None,
    ) -> MCPToolResult:
        try:
            from pathlib import Path

            from spreadsheet_dl.adapters import JsonAdapter

            adapter = JsonAdapter()
            sheets = adapter.load(Path(json_path))

            if sheet and sheets:
                sheets[0] = replace(sheets[0], name=sheet)

            from spreadsheet_dl.renderer import render_ods

            render_ods(sheets, Path(file_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "imported_from": json_path,
                    "created_file": file_path,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_xlsx_import_handler(validate_path: Any) -> Any:
    """Create xlsx_import handler."""

    def handler(file_path: str, xlsx_path: str) -> MCPToolResult:
        try:
            from pathlib import Path

            from spreadsheet_dl.adapters import XlsxAdapter
            from spreadsheet_dl.renderer import render_ods

            adapter = XlsxAdapter()
            sheets = adapter.load(Path(xlsx_path))

            render_ods(sheets, Path(file_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "imported_from": xlsx_path,
                    "created_file": file_path,
                    "sheets": [s.name for s in sheets],
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_format_auto_detect_handler(validate_path: Any) -> Any:
    """Create format_auto_detect handler."""

    def handler(file_path: str) -> MCPToolResult:
        try:
            from pathlib import Path

            path = Path(file_path)
            suffix = path.suffix.lower()

            format_map = {
                ".csv": "csv",
                ".tsv": "tsv",
                ".json": "json",
                ".xlsx": "xlsx",
                ".xls": "xls",
                ".ods": "ods",
                ".xml": "xml",
                ".html": "html",
                ".htm": "html",
            }

            detected = format_map.get(suffix, "unknown")

            return MCPToolResult.json(
                {
                    "file": file_path,
                    "extension": suffix,
                    "detected_format": detected,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_csv_export_handler(validate_path: Any) -> Any:
    """Create csv_export handler."""

    def handler(
        file_path: str,
        output_path: str,
        sheet: str | None = None,
        delimiter: str = ",",
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from pathlib import Path

            from spreadsheet_dl.adapters import CsvAdapter, OdsAdapter

            # Load ODS file to get SheetSpec objects
            ods_adapter = OdsAdapter()
            sheets = ods_adapter.load(path)

            if sheet:
                sheets = [s for s in sheets if s.name == sheet]

            adapter = CsvAdapter()
            adapter.save(sheets, Path(output_path), delimiter=delimiter)

            return MCPToolResult.json(
                {
                    "success": True,
                    "exported_to": output_path,
                    "sheets_exported": len(sheets),
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_tsv_export_handler(validate_path: Any) -> Any:
    """Create tsv_export handler."""

    def handler(
        file_path: str,
        output_path: str,
        sheet: str | None = None,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from pathlib import Path

            from spreadsheet_dl.adapters import OdsAdapter, TsvAdapter

            # Load ODS file to get SheetSpec objects
            ods_adapter = OdsAdapter()
            sheets = ods_adapter.load(path)

            if sheet:
                sheets = [s for s in sheets if s.name == sheet]

            adapter = TsvAdapter()
            adapter.save(sheets, Path(output_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "exported_to": output_path,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_json_export_handler(validate_path: Any) -> Any:
    """Create json_export handler."""

    def handler(
        file_path: str,
        output_path: str,
        sheet: str | None = None,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from pathlib import Path

            from spreadsheet_dl.adapters import JsonAdapter, OdsAdapter

            # Load ODS file to get SheetSpec objects
            ods_adapter = OdsAdapter()
            sheets = ods_adapter.load(path)

            if sheet:
                sheets = [s for s in sheets if s.name == sheet]

            adapter = JsonAdapter()
            adapter.save(sheets, Path(output_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "exported_to": output_path,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_xlsx_export_handler(validate_path: Any) -> Any:
    """Create xlsx_export handler."""

    def handler(file_path: str, output_path: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from pathlib import Path

            from spreadsheet_dl.adapters import OdsAdapter
            from spreadsheet_dl.xlsx_renderer import render_xlsx

            # Load ODS file to get SheetSpec objects
            ods_adapter = OdsAdapter()
            sheets = ods_adapter.load(path)

            render_xlsx(sheets, Path(output_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "exported_to": output_path,
                    "sheets_exported": len(sheets),
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_html_export_handler(validate_path: Any) -> Any:
    """Create html_export handler."""

    def handler(
        file_path: str,
        output_path: str,
        sheet: str | None = None,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from pathlib import Path

            from spreadsheet_dl.adapters import HtmlAdapter, OdsAdapter

            # Load ODS file to get SheetSpec objects
            ods_adapter = OdsAdapter()
            sheets = ods_adapter.load(path)

            if sheet:
                sheets = [s for s in sheets if s.name == sheet]

            adapter = HtmlAdapter()
            adapter.save(sheets, Path(output_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "exported_to": output_path,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_pdf_export_handler(validate_path: Any) -> Any:
    """Create pdf_export handler."""
    import json

    def handler(
        file_path: str,
        output_path: str,
        options: str | None = None,
    ) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from pathlib import Path

            from spreadsheet_dl.ods_editor import OdsEditor

            editor = OdsEditor(path)
            opts = json.loads(options) if options else {}

            editor.export_to_pdf(Path(output_path), **opts)  # type: ignore[attr-defined]

            return MCPToolResult.json(
                {
                    "success": True,
                    "exported_to": output_path,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_batch_import_handler(validate_path: Any) -> Any:
    """Create batch_import handler."""
    import json

    def handler(file_path: str, sources: str) -> MCPToolResult:
        try:
            from pathlib import Path

            from spreadsheet_dl.adapters import AdapterRegistry
            from spreadsheet_dl.renderer import render_ods

            source_list = json.loads(sources)
            all_sheets = []

            registry = AdapterRegistry()

            for source in source_list:
                source_path = Path(source)
                sheets = registry.import_file(source_path)
                all_sheets.extend(sheets)

            render_ods(all_sheets, Path(file_path))

            return MCPToolResult.json(
                {
                    "success": True,
                    "imported_files": len(source_list),
                    "total_sheets": len(all_sheets),
                    "created_file": file_path,
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler


def _make_batch_export_handler(validate_path: Any) -> Any:
    """Create batch_export handler."""

    def handler(file_path: str, output_dir: str, format: str) -> MCPToolResult:
        try:
            path = validate_path(file_path)
            from pathlib import Path

            from spreadsheet_dl.adapters import AdapterRegistry, OdsAdapter

            # Load ODS file to get SheetSpec objects
            ods_adapter = OdsAdapter()
            sheets = ods_adapter.load(path)

            registry = AdapterRegistry()
            adapter = registry.get_adapter(format)

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            exported = []
            for sheet in sheets:
                sheet_file = output_path / f"{sheet.name}.{format}"
                adapter.save([sheet], sheet_file)
                exported.append(str(sheet_file))

            return MCPToolResult.json(
                {
                    "success": True,
                    "exported_files": exported,
                    "total": len(exported),
                }
            )
        except Exception as e:
            return MCPToolResult.error(str(e))

    return handler
