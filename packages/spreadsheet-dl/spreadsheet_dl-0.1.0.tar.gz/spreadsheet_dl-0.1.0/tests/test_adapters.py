"""
Comprehensive tests for adapters module.

Tests:
    - All format adapters (CSV, TSV, JSON, HTML, ODS)
    - AdapterRegistry functionality
    - Export/import round-trip fidelity
    - Error handling and edge cases
    - File operations

Implements comprehensive coverage for Format adapters
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest

from spreadsheet_dl.adapters import (
    AdapterOptions,
    AdapterRegistry,
    CsvAdapter,
    ExportFormat,
    FormatAdapter,
    HtmlAdapter,
    ImportFormat,
    JsonAdapter,
    OdsAdapter,
    TsvAdapter,
    export_to,
    import_from,
)
from spreadsheet_dl.builder import CellSpec, ColumnSpec, RowSpec, SheetSpec

if TYPE_CHECKING:
    from pathlib import Path

# ==============================================================================
# Fixtures
# ==============================================================================


pytestmark = [pytest.mark.unit, pytest.mark.rendering]


@pytest.fixture
def sample_sheet() -> SheetSpec:
    """Create a sample sheet for testing."""
    return SheetSpec(
        name="TestSheet",
        columns=[
            ColumnSpec(name="Name"),
            ColumnSpec(name="Age"),
            ColumnSpec(name="Salary"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="Alice"),
                    CellSpec(value=30),
                    CellSpec(value=Decimal("75000.50")),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="Bob"),
                    CellSpec(value=25),
                    CellSpec(value=Decimal("65000.00")),
                ]
            ),
        ],
    )


@pytest.fixture
def empty_sheet() -> SheetSpec:
    """Create an empty sheet for testing."""
    return SheetSpec(name="EmptySheet", columns=[], rows=[])


@pytest.fixture
def multi_type_sheet() -> SheetSpec:
    """Create a sheet with various data types."""
    return SheetSpec(
        name="MultiType",
        columns=[
            ColumnSpec(name="Text"),
            ColumnSpec(name="Number"),
            ColumnSpec(name="Date"),
            ColumnSpec(name="Decimal"),
        ],
        rows=[
            RowSpec(
                cells=[
                    CellSpec(value="test"),
                    CellSpec(value=42),
                    CellSpec(value=date(2025, 1, 15)),
                    CellSpec(value=Decimal("123.45")),
                ]
            ),
            RowSpec(
                cells=[
                    CellSpec(value="hello"),
                    CellSpec(value=100),
                    CellSpec(value=datetime(2025, 2, 20, 10, 30)),
                    CellSpec(value=Decimal("999.99")),
                ]
            ),
        ],
    )


# ==============================================================================
# CsvAdapter Tests
# ==============================================================================


class TestCsvAdapter:
    """Tests for CSV format adapter."""

    def test_format_name(self) -> None:
        """Test CSV adapter format name."""
        adapter = CsvAdapter()
        assert adapter.format_name == "Comma-Separated Values"

    def test_file_extension(self) -> None:
        """Test CSV adapter file extension."""
        adapter = CsvAdapter()
        assert adapter.file_extension == ".csv"

    def test_export_basic(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test basic CSV export."""
        adapter = CsvAdapter()
        output_path = tmp_path / "test.csv"
        result = adapter.export([sample_sheet], output_path)

        assert result == output_path
        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert "Name,Age,Salary" in content
        assert "Alice,30,75000.50" in content
        assert "Bob,25,65000.00" in content

    def test_export_no_headers(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test CSV export without headers."""
        adapter = CsvAdapter()
        output_path = tmp_path / "no_headers.csv"
        options = AdapterOptions(include_headers=False)
        adapter.export([sample_sheet], output_path, options)

        content = output_path.read_text()
        assert "Name,Age,Salary" not in content
        assert "Alice,30,75000.50" in content

    def test_export_empty_sheet(self, tmp_path: Path, empty_sheet: SheetSpec) -> None:
        """Test CSV export with empty sheet."""
        adapter = CsvAdapter()
        output_path = tmp_path / "empty.csv"
        adapter.export([empty_sheet], output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert content == ""

    def test_export_custom_delimiter(
        self, tmp_path: Path, sample_sheet: SheetSpec
    ) -> None:
        """Test CSV export with custom delimiter."""
        adapter = CsvAdapter()
        output_path = tmp_path / "custom_delim.csv"
        options = AdapterOptions(delimiter="|")
        adapter.export([sample_sheet], output_path, options)

        content = output_path.read_text()
        assert "Name|Age|Salary" in content

    def test_export_multi_type(
        self, tmp_path: Path, multi_type_sheet: SheetSpec
    ) -> None:
        """Test CSV export with multiple data types."""
        adapter = CsvAdapter()
        output_path = tmp_path / "multi_type.csv"
        adapter.export([multi_type_sheet], output_path)

        content = output_path.read_text()
        assert "2025-01-15" in content
        assert "123.45" in content

    def test_export_select_specific_sheet_by_name(self, tmp_path: Path) -> None:
        """Test CSV export selecting specific sheet by name from options.

        Coverage: Lines 232-235 - CSV export with sheet_names filter
        """
        sheets = [
            SheetSpec(
                name="First",
                columns=[ColumnSpec(name="A")],
                rows=[RowSpec(cells=[CellSpec(value="first_data")])],
            ),
            SheetSpec(
                name="Second",
                columns=[ColumnSpec(name="B")],
                rows=[RowSpec(cells=[CellSpec(value="second_data")])],
            ),
            SheetSpec(
                name="Third",
                columns=[ColumnSpec(name="C")],
                rows=[RowSpec(cells=[CellSpec(value="third_data")])],
            ),
        ]

        adapter = CsvAdapter()
        output_path = tmp_path / "selected_sheet.csv"
        options = AdapterOptions(sheet_names=["Second"])
        adapter.export(sheets, output_path, options)

        content = output_path.read_text()
        # Should export the "Second" sheet
        assert "B" in content
        assert "second_data" in content
        # Should NOT contain data from other sheets
        assert "first_data" not in content
        assert "third_data" not in content

    def test_export_sheet_name_not_found(self, tmp_path: Path) -> None:
        """Test CSV export when requested sheet name not found.

        Coverage: Line 232->237 branch - loop completes without break
        """
        sheets = [
            SheetSpec(
                name="First",
                columns=[ColumnSpec(name="A")],
                rows=[RowSpec(cells=[CellSpec(value="first_data")])],
            ),
            SheetSpec(
                name="Second",
                columns=[ColumnSpec(name="B")],
                rows=[RowSpec(cells=[CellSpec(value="second_data")])],
            ),
        ]

        adapter = CsvAdapter()
        output_path = tmp_path / "not_found.csv"
        # Request a sheet name that doesn't exist
        options = AdapterOptions(sheet_names=["NonExistent"])
        adapter.export(sheets, output_path, options)

        content = output_path.read_text()
        # Should fall back to first sheet when named sheet not found
        assert "A" in content
        assert "first_data" in content

    def test_import_basic(self, tmp_path: Path) -> None:
        """Test basic CSV import."""
        csv_file = tmp_path / "import.csv"
        csv_file.write_text("Name,Age,City\nAlice,30,NYC\nBob,25,LA\n")

        adapter = CsvAdapter()
        sheets = adapter.import_file(csv_file)

        assert len(sheets) == 1
        sheet = sheets[0]
        assert sheet.name == "import"
        assert len(sheet.columns) == 3
        assert sheet.columns[0].name == "Name"
        assert len(sheet.rows) == 2
        assert sheet.rows[0].cells[0].value == "Alice"

    def test_import_no_headers(self, tmp_path: Path) -> None:
        """Test CSV import without headers."""
        csv_file = tmp_path / "no_headers.csv"
        csv_file.write_text("Alice,30,NYC\nBob,25,LA\n")

        adapter = CsvAdapter()
        options = AdapterOptions(include_headers=False)
        sheets = adapter.import_file(csv_file, options)

        assert len(sheets) == 1
        sheet = sheets[0]
        assert len(sheet.columns) == 3
        assert sheet.columns[0].name == "Column1"
        assert len(sheet.rows) == 2

    def test_import_empty_file(self, tmp_path: Path) -> None:
        """Test CSV import with empty file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        adapter = CsvAdapter()
        sheets = adapter.import_file(csv_file)

        assert len(sheets) == 1
        assert len(sheets[0].rows) == 0

    def test_round_trip(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test CSV export/import round-trip."""
        adapter = CsvAdapter()
        csv_file = tmp_path / "round_trip.csv"

        # Export
        adapter.export([sample_sheet], csv_file)

        # Import
        sheets = adapter.import_file(csv_file)

        assert len(sheets) == 1
        sheet = sheets[0]
        assert len(sheet.columns) == 3
        assert len(sheet.rows) == 2
        assert sheet.rows[0].cells[0].value == "Alice"


# ==============================================================================
# TsvAdapter Tests
# ==============================================================================


class TestTsvAdapter:
    """Tests for TSV format adapter."""

    def test_format_name(self) -> None:
        """Test TSV adapter format name."""
        adapter = TsvAdapter()
        assert adapter.format_name == "Tab-Separated Values"

    def test_file_extension(self) -> None:
        """Test TSV adapter file extension."""
        adapter = TsvAdapter()
        assert adapter.file_extension == ".tsv"

    def test_export_uses_tabs(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test TSV export uses tab delimiters."""
        adapter = TsvAdapter()
        output_path = tmp_path / "test.tsv"
        adapter.export([sample_sheet], output_path)

        content = output_path.read_text()
        assert "Name\tAge\tSalary" in content
        assert "Alice\t30\t75000.50" in content

    def test_import_tabs(self, tmp_path: Path) -> None:
        """Test TSV import with tab delimiters."""
        tsv_file = tmp_path / "import.tsv"
        tsv_file.write_text("Name\tAge\tCity\nAlice\t30\tNYC\n")

        adapter = TsvAdapter()
        sheets = adapter.import_file(tsv_file)

        assert len(sheets) == 1
        assert sheets[0].rows[0].cells[0].value == "Alice"


# ==============================================================================
# JsonAdapter Tests
# ==============================================================================


class TestJsonAdapter:
    """Tests for JSON format adapter."""

    def test_format_name(self) -> None:
        """Test JSON adapter format name."""
        adapter = JsonAdapter()
        assert adapter.format_name == "JSON Data"

    def test_file_extension(self) -> None:
        """Test JSON adapter file extension."""
        adapter = JsonAdapter()
        assert adapter.file_extension == ".json"

    def test_export(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test JSON export."""
        adapter = JsonAdapter()
        output_path = tmp_path / "test.json"
        result = adapter.export([sample_sheet], output_path)

        assert result == output_path
        assert output_path.exists()

    def test_import(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test JSON import."""
        adapter = JsonAdapter()
        json_file = tmp_path / "test.json"

        # Export first
        adapter.export([sample_sheet], json_file)

        # Import
        sheets = adapter.import_file(json_file)

        assert len(sheets) == 1
        assert sheets[0].name == "TestSheet"

    def test_import_empty_data(self, tmp_path: Path) -> None:
        """Test JSON import with empty/falsy data returns empty list.

        Coverage: Line 394 - JsonAdapter.import_file returning empty list
        """
        adapter = JsonAdapter()
        json_file = tmp_path / "empty.json"

        # Write an empty array (falsy data)
        json_file.write_text("[]")

        sheets = adapter.import_file(json_file)
        assert sheets == []

    def test_import_single_dict_returns_list(self, tmp_path: Path) -> None:
        """Test JSON import with single dict (not list) wraps in list.

        Coverage: Line 394 - JsonAdapter.import_file single dict case
        """
        adapter = JsonAdapter()
        json_file = tmp_path / "single.json"

        # Write a single sheet as dict (not list)
        json_file.write_text(
            '{"_type": "SheetSpec", "name": "Single", "columns": [], "rows": [], '
            '"freeze_rows": 0, "freeze_cols": 0, "print_area": null, "protection": {}, '
            '"conditional_formats": [], "validations": [], "charts": []}'
        )

        sheets = adapter.import_file(json_file)
        # Should wrap the single result in a list
        assert len(sheets) == 1
        assert sheets[0].name == "Single"

    def test_round_trip_fidelity(
        self, tmp_path: Path, multi_type_sheet: SheetSpec
    ) -> None:
        """Test JSON round-trip preserves all data types."""
        adapter = JsonAdapter()
        json_file = tmp_path / "multi_type.json"

        # Export
        adapter.export([multi_type_sheet], json_file)

        # Import
        sheets = adapter.import_file(json_file)

        assert len(sheets) == 1
        sheet = sheets[0]
        assert sheet.name == "MultiType"
        assert len(sheet.rows) == 2


# ==============================================================================
# HtmlAdapter Tests
# ==============================================================================


class TestHtmlAdapter:
    """Tests for HTML format adapter."""

    def test_format_name(self) -> None:
        """Test HTML adapter format name."""
        adapter = HtmlAdapter()
        assert adapter.format_name == "HTML Table"

    def test_file_extension(self) -> None:
        """Test HTML adapter file extension."""
        adapter = HtmlAdapter()
        assert adapter.file_extension == ".html"

    def test_export_basic(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test basic HTML export."""
        adapter = HtmlAdapter()
        output_path = tmp_path / "test.html"
        adapter.export([sample_sheet], output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "<table>" in content
        assert "<th>Name</th>" in content
        assert "<td>Alice</td>" in content

    def test_export_no_headers(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test HTML export without headers."""
        adapter = HtmlAdapter()
        output_path = tmp_path / "no_headers.html"
        options = AdapterOptions(include_headers=False)
        adapter.export([sample_sheet], output_path, options)

        content = output_path.read_text()
        assert "<thead>" not in content
        assert "<tbody>" in content

    def test_export_escapes_html(self, tmp_path: Path) -> None:
        """Test HTML export escapes special characters."""
        sheet = SheetSpec(
            name="Test",
            columns=[ColumnSpec(name="Data")],
            rows=[
                RowSpec(cells=[CellSpec(value="<script>alert('xss')</script>")]),
                RowSpec(cells=[CellSpec(value="A & B")]),
            ],
        )

        adapter = HtmlAdapter()
        output_path = tmp_path / "escaped.html"
        adapter.export([sheet], output_path)

        content = output_path.read_text()
        assert "&lt;script&gt;" in content
        assert "&amp;" in content
        assert "<script>" not in content

    def test_export_multiple_sheets(self, tmp_path: Path) -> None:
        """Test HTML export with multiple sheets."""
        sheets = [
            SheetSpec(name="Sheet1", columns=[ColumnSpec(name="A")], rows=[]),
            SheetSpec(name="Sheet2", columns=[ColumnSpec(name="B")], rows=[]),
        ]

        adapter = HtmlAdapter()
        output_path = tmp_path / "multi_sheet.html"
        adapter.export(sheets, output_path)

        content = output_path.read_text()
        assert "<h2>Sheet1</h2>" in content
        assert "<h2>Sheet2</h2>" in content

    def test_export_datetime_value(self, tmp_path: Path) -> None:
        """Test HTML export with datetime values.

        Coverage: Lines 495-497 - HtmlAdapter._format_value datetime/Decimal handling
        """
        sheet = SheetSpec(
            name="DateTimeTest",
            columns=[ColumnSpec(name="DateTime"), ColumnSpec(name="Amount")],
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(value=datetime(2025, 6, 15, 14, 30, 0)),
                        CellSpec(value=Decimal("12345.67")),
                    ]
                ),
            ],
        )

        adapter = HtmlAdapter()
        output_path = tmp_path / "datetime.html"
        adapter.export([sheet], output_path)

        content = output_path.read_text()
        # datetime should be formatted to date string
        assert "2025-06-15" in content
        # Decimal should be formatted with decimal places
        assert "12345.67" in content

    def test_export_with_none_values(self, tmp_path: Path) -> None:
        """Test HTML export handles None values correctly.

        Coverage: Line 493 - HtmlAdapter._format_value None handling
        """
        sheet = SheetSpec(
            name="Test",
            rows=[
                RowSpec(
                    cells=[
                        CellSpec(value=None),  # This triggers line 493
                        CellSpec(value="Text"),
                    ]
                )
            ],
        )

        adapter = HtmlAdapter()
        output_path = tmp_path / "test.html"
        adapter.export([sheet], output_path)

        content = output_path.read_text()
        assert "<td></td>" in content  # None becomes empty cell


# ==============================================================================
# OdsAdapter Tests
# ==============================================================================


class TestOdsAdapter:
    """Tests for ODS format adapter."""

    def test_format_name(self) -> None:
        """Test ODS adapter format name."""
        adapter = OdsAdapter()
        assert adapter.format_name == "OpenDocument Spreadsheet"

    def test_file_extension(self) -> None:
        """Test ODS adapter file extension."""
        adapter = OdsAdapter()
        assert adapter.file_extension == ".ods"

    def test_export(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test ODS export."""
        adapter = OdsAdapter()
        output_path = tmp_path / "test.ods"
        result = adapter.export([sample_sheet], output_path)

        assert result == output_path
        assert output_path.exists()

    def test_import(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test ODS import."""
        adapter = OdsAdapter()
        ods_file = tmp_path / "test.ods"

        # Export first
        adapter.export([sample_sheet], ods_file)

        # Import
        sheets = adapter.import_file(ods_file)

        assert len(sheets) >= 1
        assert sheets[0].name == "TestSheet"


# ==============================================================================
# AdapterRegistry Tests
# ==============================================================================


class TestAdapterRegistry:
    """Tests for AdapterRegistry."""

    def test_get_adapter_csv(self) -> None:
        """Test getting CSV adapter from registry."""
        adapter = AdapterRegistry.get_adapter(ExportFormat.CSV)
        assert isinstance(adapter, CsvAdapter)

    def test_get_adapter_tsv(self) -> None:
        """Test getting TSV adapter from registry."""
        adapter = AdapterRegistry.get_adapter(ExportFormat.TSV)
        assert isinstance(adapter, TsvAdapter)

    def test_get_adapter_json(self) -> None:
        """Test getting JSON adapter from registry."""
        adapter = AdapterRegistry.get_adapter(ExportFormat.JSON)
        assert isinstance(adapter, JsonAdapter)

    def test_get_adapter_html(self) -> None:
        """Test getting HTML adapter from registry."""
        adapter = AdapterRegistry.get_adapter(ExportFormat.HTML)
        assert isinstance(adapter, HtmlAdapter)

    def test_get_adapter_ods(self) -> None:
        """Test getting ODS adapter from registry."""
        adapter = AdapterRegistry.get_adapter(ExportFormat.ODS)
        assert isinstance(adapter, OdsAdapter)

    def test_get_adapter_invalid_format(self) -> None:
        """Test getting adapter for invalid format raises error."""
        # Use PDF which is defined but not implemented
        with pytest.raises(ValueError, match="Unsupported format"):
            AdapterRegistry.get_adapter(ExportFormat.PDF)

    def test_list_formats(self) -> None:
        """Test listing available formats."""
        formats = AdapterRegistry.list_formats()
        assert ExportFormat.CSV in formats
        assert ExportFormat.TSV in formats
        assert ExportFormat.JSON in formats
        assert ExportFormat.HTML in formats
        assert ExportFormat.ODS in formats

    def test_export_csv(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test registry export to CSV."""
        output_path = tmp_path / "registry.csv"
        result = AdapterRegistry.export([sample_sheet], output_path, ExportFormat.CSV)
        assert result == output_path
        assert output_path.exists()

    def test_export_auto_detect_csv(
        self, tmp_path: Path, sample_sheet: SheetSpec
    ) -> None:
        """Test registry auto-detects CSV from extension."""
        output_path = tmp_path / "auto.csv"
        result = AdapterRegistry.export([sample_sheet], output_path)
        assert result == output_path
        assert output_path.exists()

    def test_export_auto_detect_json(
        self, tmp_path: Path, sample_sheet: SheetSpec
    ) -> None:
        """Test registry auto-detects JSON from extension."""
        output_path = tmp_path / "auto.json"
        result = AdapterRegistry.export([sample_sheet], output_path)
        assert result == output_path
        assert output_path.exists()

    def test_export_auto_detect_html(
        self, tmp_path: Path, sample_sheet: SheetSpec
    ) -> None:
        """Test registry auto-detects HTML from extension."""
        output_path = tmp_path / "auto.html"
        result = AdapterRegistry.export([sample_sheet], output_path)
        assert result == output_path
        assert output_path.exists()

    def test_import_csv(self, tmp_path: Path) -> None:
        """Test registry import from CSV."""
        csv_file = tmp_path / "import.csv"
        csv_file.write_text("A,B,C\n1,2,3\n")

        sheets = AdapterRegistry.import_file(csv_file)
        assert len(sheets) == 1

    def test_import_auto_detect(self, tmp_path: Path) -> None:
        """Test registry auto-detects format from extension."""
        csv_file = tmp_path / "auto.csv"
        csv_file.write_text("A,B\n1,2\n")

        sheets = AdapterRegistry.import_file(csv_file)
        assert len(sheets) == 1

    def test_import_with_explicit_format(self, tmp_path: Path) -> None:
        """Test registry import with explicit format parameter.

        Coverage: Line 637 - AdapterRegistry.import_file with explicit format
        """
        csv_file = tmp_path / "data.txt"  # Unusual extension
        csv_file.write_text("A,B\n1,2\n")

        # Explicitly specify CSV format
        sheets = AdapterRegistry.import_file(csv_file, format=ImportFormat.CSV)
        assert len(sheets) == 1
        assert sheets[0].columns[0].name == "A"

    def test_register_custom_adapter(self) -> None:
        """Test registering a custom adapter actually registers it.

        Coverage: Line 561 - AdapterRegistry.register_adapter
        """

        class TestCustomAdapter(FormatAdapter):
            @property
            def format_name(self) -> str:
                return "Test Custom"

            @property
            def file_extension(self) -> str:
                return ".testcustom"

            def export(self, sheets: Any, output_path: Any, options: Any = None) -> Any:
                return output_path

            def import_file(self, input_path: Any, options: Any = None) -> Any:
                return []

        # Store original adapters to restore later
        original_adapters = dict(AdapterRegistry._adapters)

        try:
            # Register the custom adapter
            AdapterRegistry.register_adapter(ExportFormat.PDF, TestCustomAdapter)

            # Verify it was registered
            adapter = AdapterRegistry.get_adapter(ExportFormat.PDF)
            assert isinstance(adapter, TestCustomAdapter)
            assert adapter.format_name == "Test Custom"
        finally:
            # Restore original adapters
            AdapterRegistry._adapters = original_adapters


# ==============================================================================
# Convenience Functions Tests
# ==============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_export_to_csv(self, tmp_path: Path, sample_sheet: SheetSpec) -> None:
        """Test export_to function with CSV."""
        output_path = tmp_path / "convenience.csv"
        result = export_to([sample_sheet], output_path, "csv")
        assert result == output_path
        assert output_path.exists()

    def test_export_to_with_options(
        self, tmp_path: Path, sample_sheet: SheetSpec
    ) -> None:
        """Test export_to with custom options."""
        output_path = tmp_path / "options.csv"
        result = export_to([sample_sheet], output_path, "csv", include_headers=False)
        assert result == output_path

        content = output_path.read_text()
        assert "Name,Age,Salary" not in content

    def test_export_to_auto_detect(
        self, tmp_path: Path, sample_sheet: SheetSpec
    ) -> None:
        """Test export_to auto-detects format."""
        output_path = tmp_path / "auto.json"
        result = export_to([sample_sheet], output_path)
        assert result == output_path
        assert output_path.exists()

    def test_import_from_csv(self, tmp_path: Path) -> None:
        """Test import_from function with CSV."""
        csv_file = tmp_path / "import.csv"
        csv_file.write_text("A,B\n1,2\n")

        sheets = import_from(csv_file, "csv")
        assert len(sheets) == 1

    def test_import_from_with_options(self, tmp_path: Path) -> None:
        """Test import_from with custom options."""
        csv_file = tmp_path / "no_headers.csv"
        csv_file.write_text("1,2\n3,4\n")

        sheets = import_from(csv_file, "csv", include_headers=False)
        assert len(sheets) == 1
        assert len(sheets[0].rows) == 2

    def test_import_from_auto_detect(self, tmp_path: Path) -> None:
        """Test import_from auto-detects format."""
        tsv_file = tmp_path / "auto.tsv"
        tsv_file.write_text("A\tB\n1\t2\n")

        sheets = import_from(tsv_file)
        assert len(sheets) == 1


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_export_empty_sheets_list(self, tmp_path: Path) -> None:
        """Test exporting empty sheets list."""
        adapter = CsvAdapter()
        output_path = tmp_path / "empty_list.csv"
        adapter.export([], output_path)

        assert output_path.exists()
        assert output_path.read_text() == ""

    def test_export_none_values(self, tmp_path: Path) -> None:
        """Test exporting cells with None values."""
        sheet = SheetSpec(
            name="NoneTest",
            columns=[ColumnSpec(name="A"), ColumnSpec(name="B")],
            rows=[
                RowSpec(cells=[CellSpec(value=None), CellSpec(value="text")]),
                RowSpec(cells=[CellSpec(value=123), CellSpec(value=None)]),
            ],
        )

        adapter = CsvAdapter()
        output_path = tmp_path / "none_values.csv"
        adapter.export([sheet], output_path)

        content = output_path.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3  # Header + 2 data rows

    def test_export_special_characters(self, tmp_path: Path) -> None:
        """Test exporting cells with special characters."""
        sheet = SheetSpec(
            name="SpecialChars",
            columns=[ColumnSpec(name="Data")],
            rows=[
                RowSpec(cells=[CellSpec(value="Line1\nLine2")]),
                RowSpec(cells=[CellSpec(value='Quote"Test')]),
                RowSpec(cells=[CellSpec(value="Comma,Test")]),
            ],
        )

        adapter = CsvAdapter()
        output_path = tmp_path / "special.csv"
        adapter.export([sheet], output_path)

        assert output_path.exists()

    def test_import_malformed_csv(self, tmp_path: Path) -> None:
        """Test importing malformed CSV handles gracefully."""
        csv_file = tmp_path / "malformed.csv"
        csv_file.write_text("A,B,C\n1,2\n3,4,5,6\n")

        adapter = CsvAdapter()
        sheets = adapter.import_file(csv_file)

        # Should still import, handling inconsistent column counts
        assert len(sheets) == 1

    def test_sheet_names_filter(self, tmp_path: Path) -> None:
        """Test filtering sheets by name during export."""
        sheets = [
            SheetSpec(name="Keep", columns=[ColumnSpec(name="A")], rows=[]),
            SheetSpec(name="Skip", columns=[ColumnSpec(name="B")], rows=[]),
        ]

        adapter = HtmlAdapter()
        output_path = tmp_path / "filtered.html"
        options = AdapterOptions(sheet_names=["Keep"])
        adapter.export(sheets, output_path, options)

        content = output_path.read_text()
        assert "Keep" in content
        assert "Skip" not in content


# ==============================================================================
# Abstract FormatAdapter Tests (for coverage of abstract methods)
# ==============================================================================


class TestFormatAdapterAbstract:
    """Tests for abstract FormatAdapter interface.

    Coverage: Lines 90, 96, 116, 134 - Abstract method ... statements
    Note: These are abstract method declarations that get covered by subclass tests.
    """

    def test_format_adapter_cannot_instantiate(self) -> None:
        """Test that FormatAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError, match="abstract"):
            FormatAdapter()  # type: ignore[abstract]

    def test_all_subclasses_implement_interface(self) -> None:
        """Test all subclasses properly implement the interface."""
        subclasses = [CsvAdapter, TsvAdapter, JsonAdapter, HtmlAdapter, OdsAdapter]

        for subclass in subclasses:
            adapter = subclass()  # type: ignore[abstract]
            # All these should work without raising
            assert isinstance(adapter.format_name, str)
            assert isinstance(adapter.file_extension, str)
            assert adapter.file_extension.startswith(".")
