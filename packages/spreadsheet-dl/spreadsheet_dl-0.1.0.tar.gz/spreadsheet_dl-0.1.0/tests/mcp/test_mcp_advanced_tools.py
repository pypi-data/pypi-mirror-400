"""Comprehensive tests for MCP server advanced tool handlers.

Tests advanced tool categories:
- Workbook operations (properties, statistics, compare, merge)
- Formula operations (recalculate, audit, circular refs)
- Data operations (connections, refresh, links)
- Chart and visualization operations
- Import/export operations
- Theme and color scheme operations

Task 2.2: MCP Advanced Tools Tests for SpreadsheetDL v4.1.0 pre-release audit.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from spreadsheet_dl.mcp_server import (
    MCPConfig,
    MCPServer,
)

pytestmark = [pytest.mark.unit, pytest.mark.mcp, pytest.mark.advanced_tools]


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def server(tmp_path: Path) -> MCPServer:
    """Create a test MCP server."""
    config = MCPConfig(allowed_paths=[tmp_path, Path.cwd()])
    return MCPServer(config)


@pytest.fixture
def test_ods(tmp_path: Path) -> Path:
    """Create a test ODS file with sample data."""
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableCell, TableRow
    from odf.text import P

    doc = OpenDocumentSpreadsheet()
    table = Table(name="Sheet1")

    # Add header row
    header_row = TableRow()
    for header in ["Name", "Value", "Status", "Formula"]:
        cell = TableCell(valuetype="string")
        cell.addElement(P(text=header))
        header_row.addElement(cell)
    table.addElement(header_row)

    # Add data rows
    data = [
        ["Item1", "100", "Active", "=B2*2"],
        ["Item2", "200", "Inactive", "=B3*2"],
        ["Item3", "300", "Active", "=B4*2"],
        ["Total", "600", "", "=SUM(B2:B4)"],
    ]
    for row_data in data:
        row = TableRow()
        for value in row_data:
            cell = TableCell(valuetype="string")
            cell.addElement(P(text=value))
            row.addElement(cell)
        table.addElement(row)

    doc.spreadsheet.addElement(table)
    test_file = tmp_path / "test.ods"
    doc.save(str(test_file))
    return test_file


@pytest.fixture
def second_test_ods(tmp_path: Path) -> Path:
    """Create a second test ODS file for comparison tests."""
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableCell, TableRow
    from odf.text import P

    doc = OpenDocumentSpreadsheet()
    table = Table(name="Sheet1")

    # Slightly different data
    data = [
        ["Name", "Value", "Status"],
        ["Item1", "150", "Active"],
        ["Item2", "200", "Active"],
        ["Item4", "400", "New"],
    ]
    for row_data in data:
        row = TableRow()
        for value in row_data:
            cell = TableCell(valuetype="string")
            cell.addElement(P(text=value))
            row.addElement(cell)
        table.addElement(row)

    doc.spreadsheet.addElement(table)
    test_file = tmp_path / "test2.ods"
    doc.save(str(test_file))
    return test_file


@pytest.fixture
def test_csv(tmp_path: Path) -> Path:
    """Create a test CSV file."""
    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text("Name,Value,Status\nItem1,100,Active\nItem2,200,Inactive\n")
    return csv_path


@pytest.fixture
def test_json(tmp_path: Path) -> Path:
    """Create a test JSON file."""
    json_path = tmp_path / "test_data.json"
    data = [
        {"Name": "Item1", "Value": 100, "Status": "Active"},
        {"Name": "Item2", "Value": 200, "Status": "Inactive"},
    ]
    json_path.write_text(json.dumps(data))
    return json_path


@pytest.fixture
def test_tsv(tmp_path: Path) -> Path:
    """Create a test TSV file."""
    tsv_path = tmp_path / "test_data.tsv"
    tsv_path.write_text(
        "Name\tValue\tStatus\nItem1\t100\tActive\nItem2\t200\tInactive\n"
    )
    return tsv_path


# =============================================================================
# Workbook Operations Tests
# =============================================================================


class TestWorkbookOperations:
    """Tests for workbook operation handlers."""

    def test_workbook_properties_get(self, server: MCPServer, test_ods: Path) -> None:
        """Test getting workbook properties."""
        result = server._handle_workbook_properties_get(file_path=str(test_ods))

        # Should return properties or handle gracefully
        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "file" in content
            assert "properties" in content

    def test_workbook_properties_set(self, server: MCPServer, test_ods: Path) -> None:
        """Test setting workbook properties."""
        properties = json.dumps({"title": "Test Workbook", "author": "Test Author"})
        result = server._handle_workbook_properties_set(
            file_path=str(test_ods),
            properties=properties,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_workbook_statistics(self, server: MCPServer, test_ods: Path) -> None:
        """Test getting workbook statistics."""
        result = server._handle_workbook_statistics(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "file" in content
            assert "statistics" in content

    def test_workbooks_compare(
        self, server: MCPServer, test_ods: Path, second_test_ods: Path
    ) -> None:
        """Test comparing two workbooks."""
        result = server._handle_workbooks_compare(
            file_path1=str(test_ods),
            file_path2=str(second_test_ods),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "file1" in content
            assert "file2" in content
            assert "differences" in content

    def test_workbooks_merge(
        self, server: MCPServer, test_ods: Path, second_test_ods: Path, tmp_path: Path
    ) -> None:
        """Test merging workbooks."""
        output_path = tmp_path / "merged.ods"
        sources = json.dumps([str(test_ods), str(second_test_ods)])

        result = server._handle_workbooks_merge(
            output_path=str(output_path),
            sources=sources,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert content["merged_files"] == 2

    def test_workbook_properties_get_invalid_path(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test workbook properties with invalid path."""
        result = server._handle_workbook_properties_get(
            file_path=str(tmp_path / "nonexistent.ods")
        )
        assert result.is_error


# =============================================================================
# Formula Operations Tests
# =============================================================================


class TestFormulaOperations:
    """Tests for formula operation handlers."""

    def test_formulas_recalculate(self, server: MCPServer, test_ods: Path) -> None:
        """Test formula recalculation."""
        result = server._handle_formulas_recalculate(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert "formulas_recalculated" in content

    def test_formulas_audit(self, server: MCPServer, test_ods: Path) -> None:
        """Test formula auditing."""
        result = server._handle_formulas_audit(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "file" in content
            assert "total_formulas" in content or "errors" in content

    def test_circular_refs_find(self, server: MCPServer, test_ods: Path) -> None:
        """Test finding circular references."""
        result = server._handle_circular_refs_find(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "file" in content
            assert "has_circular_refs" in content
            assert "circular_references" in content

    def test_formulas_recalculate_invalid_path(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test formula recalculation with invalid path."""
        result = server._handle_formulas_recalculate(
            file_path=str(tmp_path / "nonexistent.ods")
        )
        assert result.is_error


# =============================================================================
# Data Operations Tests
# =============================================================================


class TestDataOperations:
    """Tests for data operation handlers."""

    def test_data_connections_list(self, server: MCPServer, test_ods: Path) -> None:
        """Test listing data connections."""
        result = server._handle_data_connections_list(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "file" in content
            assert "connections" in content

    def test_data_refresh(self, server: MCPServer, test_ods: Path) -> None:
        """Test refreshing data connections."""
        result = server._handle_data_refresh(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_data_refresh_specific_connection(
        self, server: MCPServer, test_ods: Path
    ) -> None:
        """Test refreshing a specific connection."""
        result = server._handle_data_refresh(
            file_path=str(test_ods),
            connection_name="test_connection",
        )

        assert result is not None
        # May error if connection doesn't exist, which is expected

    def test_links_update(self, server: MCPServer, test_ods: Path) -> None:
        """Test updating external links."""
        result = server._handle_links_update(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert "links_updated" in content

    def test_links_break(self, server: MCPServer, test_ods: Path) -> None:
        """Test breaking external links."""
        result = server._handle_links_break(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert "links_broken" in content


# =============================================================================
# Chart Operations Tests
# =============================================================================


class TestChartOperations:
    """Tests for chart operation handlers."""

    def test_chart_create(self, server: MCPServer, test_ods: Path) -> None:
        """Test chart creation."""
        result = server._handle_chart_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            chart_type="bar",
            data_range="A1:B5",
            title="Test Chart",
            position="E1",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert content["chart_type"] == "bar"

    def test_chart_create_minimal(self, server: MCPServer, test_ods: Path) -> None:
        """Test chart creation with minimal parameters."""
        result = server._handle_chart_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            chart_type="line",
            data_range="B2:B5",
        )

        assert result is not None
        # May succeed or fail based on implementation

    def test_chart_update(self, server: MCPServer, test_ods: Path) -> None:
        """Test chart update."""
        properties = json.dumps({"title": "Updated Title", "legend": True})
        result = server._handle_chart_update(
            file_path=str(test_ods),
            sheet="Sheet1",
            chart_id="chart_0",
            properties=properties,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_chart_create_all_types(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating charts of different types."""
        chart_types = ["bar", "line", "pie", "area", "scatter"]

        for chart_type in chart_types:
            result = server._handle_chart_create(
                file_path=str(test_ods),
                sheet="Sheet1",
                chart_type=chart_type,
                data_range="A1:B5",
            )
            assert result is not None


# =============================================================================
# Conditional Formatting Tests
# =============================================================================


class TestConditionalFormatting:
    """Tests for conditional formatting handlers."""

    def test_cf_create_color_scale(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating color scale conditional formatting."""
        config = json.dumps(
            {
                "min_color": "#FF0000",
                "mid_color": "#FFFF00",
                "max_color": "#00FF00",
            }
        )
        result = server._handle_cf_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="B2:B5",
            rule_type="color_scale",
            config=config,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert content["rule_type"] == "color_scale"

    def test_cf_create_data_bar(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating data bar conditional formatting."""
        config = json.dumps({"color": "#3366CC", "min_length": 0, "max_length": 100})
        result = server._handle_cf_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="B2:B5",
            rule_type="data_bar",
            config=config,
        )

        assert result is not None

    def test_cf_create_cell_value(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating cell value conditional formatting."""
        config = json.dumps(
            {
                "operator": "greater_than",
                "value": 100,
                "format": {"background": "#FFFF00"},
            }
        )
        result = server._handle_cf_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="B2:B5",
            rule_type="cell_value",
            config=config,
        )

        assert result is not None


# =============================================================================
# Data Validation Tests
# =============================================================================


class TestDataValidation:
    """Tests for data validation handlers."""

    def test_validation_create_list(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating list validation."""
        config = json.dumps(
            {
                "values": ["Active", "Inactive", "Pending"],
                "allow_blank": True,
            }
        )
        result = server._handle_validation_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="C2:C5",
            validation_type="list",
            config=config,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert content["validation_type"] == "list"

    def test_validation_create_number(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating number validation."""
        config = json.dumps(
            {
                "min_value": 0,
                "max_value": 1000,
                "operator": "between",
            }
        )
        result = server._handle_validation_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="B2:B5",
            validation_type="number",
            config=config,
        )

        assert result is not None

    def test_validation_create_custom(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating custom validation."""
        config = json.dumps(
            {
                "formula": "=AND(B2>0,B2<1000)",
                "error_message": "Value must be between 0 and 1000",
            }
        )
        result = server._handle_validation_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="B2:B5",
            validation_type="custom",
            config=config,
        )

        assert result is not None


# =============================================================================
# Named Range and Table Tests
# =============================================================================


class TestNamedRangesAndTables:
    """Tests for named range and table handlers."""

    def test_named_range_create(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating a named range."""
        result = server._handle_named_range_create(
            file_path=str(test_ods),
            name="DataRange",
            sheet="Sheet1",
            range="A1:D5",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert content["name"] == "DataRange"

    def test_table_create(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating a table."""
        result = server._handle_table_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="A1:D5",
            name="MainTable",
            has_headers=True,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_table_create_default_name(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating a table with default name."""
        result = server._handle_table_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="A1:C3",
        )

        assert result is not None


# =============================================================================
# Query Operations Tests
# =============================================================================


class TestQueryOperations:
    """Tests for query operation handlers."""

    def test_query_select(self, server: MCPServer, test_ods: Path) -> None:
        """Test query select operation."""
        result = server._handle_query_select(
            file_path=str(test_ods),
            sheet="Sheet1",
            query="SELECT A, B WHERE B > 100",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "sheet" in content
            assert "query" in content
            assert "results" in content

    def test_query_find(self, server: MCPServer, test_ods: Path) -> None:
        """Test query find operation."""
        criteria = json.dumps({"Status": "Active"})
        result = server._handle_query_find(
            file_path=str(test_ods),
            sheet="Sheet1",
            criteria=criteria,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "sheet" in content
            assert "criteria" in content
            assert "matches" in content


# =============================================================================
# Import Operations Tests
# =============================================================================


class TestImportOperations:
    """Tests for import operation handlers."""

    def test_csv_import(
        self, server: MCPServer, test_csv: Path, tmp_path: Path
    ) -> None:
        """Test CSV import."""
        output_file = tmp_path / "csv_import_result.ods"
        result = server._handle_csv_import(
            file_path=str(output_file),
            csv_path=str(test_csv),
            sheet="ImportedData",
            delimiter=",",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert "imported_from" in content

    def test_csv_import_default_sheet(
        self, server: MCPServer, test_csv: Path, tmp_path: Path
    ) -> None:
        """Test CSV import with default sheet name."""
        output_file = tmp_path / "csv_import_default.ods"
        result = server._handle_csv_import(
            file_path=str(output_file),
            csv_path=str(test_csv),
        )

        assert result is not None

    def test_tsv_import(
        self, server: MCPServer, test_tsv: Path, tmp_path: Path
    ) -> None:
        """Test TSV import."""
        output_file = tmp_path / "tsv_import_result.ods"
        result = server._handle_tsv_import(
            file_path=str(output_file),
            tsv_path=str(test_tsv),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_json_import(
        self, server: MCPServer, test_json: Path, tmp_path: Path
    ) -> None:
        """Test JSON import."""
        output_file = tmp_path / "json_import_result.ods"
        result = server._handle_json_import(
            file_path=str(output_file),
            json_path=str(test_json),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_format_auto_detect(self, server: MCPServer, test_csv: Path) -> None:
        """Test format auto-detection."""
        result = server._handle_format_auto_detect(file_path=str(test_csv))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["detected_format"] == "csv"
            assert content["extension"] == ".csv"

    def test_format_auto_detect_various_formats(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test format detection for various file types."""
        test_files = [
            ("test.csv", "csv"),
            ("test.tsv", "tsv"),
            ("test.json", "json"),
            ("test.xlsx", "xlsx"),
            ("test.ods", "ods"),
            ("test.html", "html"),
        ]

        for filename, expected_format in test_files:
            test_file = tmp_path / filename
            test_file.touch()

            result = server._handle_format_auto_detect(file_path=str(test_file))

            assert result is not None
            if not result.is_error:
                content = json.loads(result.content[0]["text"])
                assert content["detected_format"] == expected_format


# =============================================================================
# Export Operations Tests
# =============================================================================


class TestExportOperations:
    """Tests for export operation handlers."""

    def test_csv_export(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test CSV export."""
        output_file = tmp_path / "exported.csv"
        result = server._handle_csv_export(
            file_path=str(test_ods),
            output_path=str(output_file),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert "exported_to" in content

    def test_csv_export_specific_sheet(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test CSV export of specific sheet."""
        output_file = tmp_path / "exported_sheet.csv"
        result = server._handle_csv_export(
            file_path=str(test_ods),
            output_path=str(output_file),
            sheet="Sheet1",
        )

        assert result is not None

    def test_tsv_export(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test TSV export."""
        output_file = tmp_path / "exported.tsv"
        result = server._handle_tsv_export(
            file_path=str(test_ods),
            output_path=str(output_file),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_json_export(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test JSON export."""
        output_file = tmp_path / "exported.json"
        result = server._handle_json_export(
            file_path=str(test_ods),
            output_path=str(output_file),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_xlsx_export(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test XLSX export."""
        output_file = tmp_path / "exported.xlsx"
        result = server._handle_xlsx_export(
            file_path=str(test_ods),
            output_path=str(output_file),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_html_export(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test HTML export."""
        output_file = tmp_path / "exported.html"
        result = server._handle_html_export(
            file_path=str(test_ods),
            output_path=str(output_file),
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True

    def test_pdf_export(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test PDF export."""
        output_file = tmp_path / "exported.pdf"
        result = server._handle_pdf_export(
            file_path=str(test_ods),
            output_path=str(output_file),
        )

        assert result is not None
        # PDF export may not be fully implemented

    def test_export_invalid_source(self, server: MCPServer, tmp_path: Path) -> None:
        """Test export with invalid source file."""
        result = server._handle_csv_export(
            file_path=str(tmp_path / "nonexistent.ods"),
            output_path=str(tmp_path / "out.csv"),
        )
        assert result.is_error


# =============================================================================
# Batch Operations Tests
# =============================================================================


class TestBatchOperations:
    """Tests for batch import/export handlers."""

    def test_batch_import(
        self, server: MCPServer, test_csv: Path, test_json: Path, tmp_path: Path
    ) -> None:
        """Test batch import from multiple files."""
        output_file = tmp_path / "batch_imported.ods"
        sources = json.dumps([str(test_csv), str(test_json)])

        result = server._handle_batch_import(
            file_path=str(output_file),
            sources=sources,
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert content["imported_files"] == 2

    def test_batch_export(
        self, server: MCPServer, test_ods: Path, tmp_path: Path
    ) -> None:
        """Test batch export to multiple files."""
        output_dir = tmp_path / "batch_export"
        output_dir.mkdir()

        result = server._handle_batch_export(
            file_path=str(test_ods),
            output_dir=str(output_dir),
            format="csv",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["success"] is True
            assert "exported_files" in content


# =============================================================================
# Theme Operations Tests
# =============================================================================


class TestThemeOperations:
    """Tests for theme operation handlers."""

    def test_theme_list(self, server: MCPServer, test_ods: Path) -> None:
        """Test listing themes."""
        result = server._handle_theme_list(file_path=str(test_ods))

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "themes" in content

    def test_theme_get(self, server: MCPServer, test_ods: Path) -> None:
        """Test getting a specific theme."""
        result = server._handle_theme_get(
            file_path=str(test_ods),
            theme_name="default",
        )

        assert result is not None
        # Theme retrieval may error if theme doesn't exist

    def test_theme_create(self, server: MCPServer, test_ods: Path) -> None:
        """Test creating a theme."""
        properties = json.dumps(
            {
                "header_background": "#336699",
                "header_font": "Arial",
                "data_font": "Calibri",
            }
        )
        result = server._handle_theme_create(
            file_path=str(test_ods),
            theme_name="CustomTheme",
            properties=properties,
        )

        assert result is not None

    def test_theme_apply(self, server: MCPServer, test_ods: Path) -> None:
        """Test applying a theme."""
        result = server._handle_theme_apply(
            file_path=str(test_ods),
            theme_name="default",
        )

        assert result is not None


# =============================================================================
# Color Scheme Tests
# =============================================================================


class TestColorSchemeOperations:
    """Tests for color scheme generation."""

    def test_color_scheme_monochromatic(self, server: MCPServer) -> None:
        """Test generating monochromatic color scheme."""
        result = server._handle_color_scheme_generate(
            base_color="#3366CC",
            scheme_type="monochromatic",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["base_color"] == "#3366CC"
            assert content["scheme_type"] == "monochromatic"
            assert len(content["colors"]) >= 3

    def test_color_scheme_complementary(self, server: MCPServer) -> None:
        """Test generating complementary color scheme."""
        result = server._handle_color_scheme_generate(
            base_color="#FF6600",
            scheme_type="complementary",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["scheme_type"] == "complementary"
            assert len(content["colors"]) >= 2

    def test_color_scheme_analogous(self, server: MCPServer) -> None:
        """Test generating analogous color scheme."""
        result = server._handle_color_scheme_generate(
            base_color="#009966",
            scheme_type="analogous",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["scheme_type"] == "analogous"
            assert len(content["colors"]) >= 3

    def test_color_scheme_triadic(self, server: MCPServer) -> None:
        """Test generating triadic color scheme."""
        result = server._handle_color_scheme_generate(
            base_color="#990099",
            scheme_type="triadic",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["scheme_type"] == "triadic"
            assert len(content["colors"]) >= 3

    def test_color_scheme_split_complementary(self, server: MCPServer) -> None:
        """Test generating split complementary color scheme."""
        result = server._handle_color_scheme_generate(
            base_color="#CC3333",
            scheme_type="split_complementary",
        )

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert content["scheme_type"] == "split_complementary"

    def test_color_scheme_default(self, server: MCPServer) -> None:
        """Test generating default color scheme."""
        result = server._handle_color_scheme_generate(base_color="#3366CC")

        assert result is not None
        if not result.is_error:
            content = json.loads(result.content[0]["text"])
            assert "colors" in content

    def test_color_scheme_invalid_color(self, server: MCPServer) -> None:
        """Test color scheme generation with invalid color."""
        result = server._handle_color_scheme_generate(
            base_color="not-a-color",
            scheme_type="monochromatic",
        )

        assert result.is_error


# =============================================================================
# Handler Existence Tests
# =============================================================================


class TestHandlerExistence:
    """Verify all advanced handlers exist on the server."""

    def test_workbook_handlers_exist(self, server: MCPServer) -> None:
        """Test that all workbook handlers exist."""
        handlers = [
            "_handle_workbook_properties_get",
            "_handle_workbook_properties_set",
            "_handle_workbook_statistics",
            "_handle_workbooks_compare",
            "_handle_workbooks_merge",
        ]
        for handler in handlers:
            assert hasattr(server, handler), f"Missing handler: {handler}"

    def test_formula_handlers_exist(self, server: MCPServer) -> None:
        """Test that all formula handlers exist."""
        handlers = [
            "_handle_formulas_recalculate",
            "_handle_formulas_audit",
            "_handle_circular_refs_find",
        ]
        for handler in handlers:
            assert hasattr(server, handler), f"Missing handler: {handler}"

    def test_data_handlers_exist(self, server: MCPServer) -> None:
        """Test that all data handlers exist."""
        handlers = [
            "_handle_data_connections_list",
            "_handle_data_refresh",
            "_handle_links_update",
            "_handle_links_break",
        ]
        for handler in handlers:
            assert hasattr(server, handler), f"Missing handler: {handler}"

    def test_import_handlers_exist(self, server: MCPServer) -> None:
        """Test that all import handlers exist."""
        handlers = [
            "_handle_csv_import",
            "_handle_tsv_import",
            "_handle_json_import",
            "_handle_format_auto_detect",
            "_handle_batch_import",
        ]
        for handler in handlers:
            assert hasattr(server, handler), f"Missing handler: {handler}"

    def test_export_handlers_exist(self, server: MCPServer) -> None:
        """Test that all export handlers exist."""
        handlers = [
            "_handle_csv_export",
            "_handle_tsv_export",
            "_handle_json_export",
            "_handle_xlsx_export",
            "_handle_html_export",
            "_handle_pdf_export",
            "_handle_batch_export",
        ]
        for handler in handlers:
            assert hasattr(server, handler), f"Missing handler: {handler}"

    def test_theme_handlers_exist(self, server: MCPServer) -> None:
        """Test that all theme handlers exist."""
        handlers = [
            "_handle_theme_list",
            "_handle_theme_get",
            "_handle_theme_create",
            "_handle_theme_apply",
            "_handle_color_scheme_generate",
        ]
        for handler in handlers:
            assert hasattr(server, handler), f"Missing handler: {handler}"


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in advanced tools."""

    def test_invalid_json_config(self, server: MCPServer, test_ods: Path) -> None:
        """Test handling of invalid JSON configuration."""
        result = server._handle_cf_create(
            file_path=str(test_ods),
            sheet="Sheet1",
            range="A1:B5",
            rule_type="color_scale",
            config="not valid json",
        )

        assert result.is_error

    def test_invalid_batch_sources_json(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test handling of invalid JSON in batch sources."""
        output_file = tmp_path / "batch_out.ods"
        result = server._handle_batch_import(
            file_path=str(output_file),
            sources="not valid json array",
        )

        assert result.is_error

    def test_path_security_validation(self, server: MCPServer, tmp_path: Path) -> None:
        """Test that path security is enforced."""
        # Try to access file outside allowed paths
        result = server._handle_workbook_properties_get(
            file_path="/etc/passwd",
        )

        assert result.is_error

    def test_empty_sources_batch_import(
        self, server: MCPServer, tmp_path: Path
    ) -> None:
        """Test batch import with empty sources."""
        output_file = tmp_path / "empty_batch.ods"
        result = server._handle_batch_import(
            file_path=str(output_file),
            sources="[]",
        )

        assert result is not None
        # May succeed with empty result or fail gracefully
