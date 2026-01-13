"""
Comprehensive tests for HTML import functionality.

Implements tests for : HTML import from HTML tables

Tests:
    - Simple table import
    - Tables with/without headers
    - colspan/rowspan handling
    - Multiple tables
    - CSS selector filtering
    - Type detection (int, float, date)
    - Whitespace handling
    - Empty row handling
    - Round-trip export/import
    - Edge cases and error handling
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

import pytest

bs4 = pytest.importorskip("bs4", reason="HTML import requires beautifulsoup4")
lxml = pytest.importorskip("lxml", reason="HTML import requires lxml")

from spreadsheet_dl.adapters import HtmlAdapter, HTMLImportOptions  # noqa: E402
from spreadsheet_dl.builder import (  # noqa: E402
    CellSpec,
    ColumnSpec,
    RowSpec,
    SheetSpec,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit, pytest.mark.requires_html]


# ==============================================================================
# Basic HTML Import Tests
# ==============================================================================


class TestHtmlImportBasic:
    """Basic HTML import functionality tests."""

    def test_import_simple_table(self, tmp_path: Path) -> None:
        """Test HTML import with simple table."""
        html_file = tmp_path / "simple.html"
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <h2>Employee Data</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Salary</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Alice</td>
                        <td>30</td>
                        <td>75000.50</td>
                    </tr>
                    <tr>
                        <td>Bob</td>
                        <td>25</td>
                        <td>65000.00</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert len(sheets) == 1
        sheet = sheets[0]
        assert sheet.name == "Employee Data"
        assert len(sheet.columns) == 3
        assert sheet.columns[0].name == "Name"
        assert sheet.columns[1].name == "Age"
        assert sheet.columns[2].name == "Salary"
        assert len(sheet.rows) == 2
        assert sheet.rows[0].cells[0].value == "Alice"
        assert sheet.rows[0].cells[1].value == 30  # Auto-detected as int
        assert sheet.rows[0].cells[2].value == 75000.50  # Auto-detected as float

    def test_import_no_thead(self, tmp_path: Path) -> None:
        """Test HTML import with table without thead."""
        html_file = tmp_path / "no_thead.html"
        html_content = """
        <table>
            <tr>
                <th>Product</th>
                <th>Price</th>
            </tr>
            <tr>
                <td>Widget</td>
                <td>19.99</td>
            </tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert len(sheets) == 1
        assert len(sheets[0].columns) == 2
        assert sheets[0].columns[0].name == "Product"
        assert len(sheets[0].rows) == 1

    def test_import_multiple_tables(self, tmp_path: Path) -> None:
        """Test HTML import with multiple tables."""
        html_file = tmp_path / "multi.html"
        html_content = """
        <html>
        <body>
            <h2>Table 1</h2>
            <table>
                <tr><th>A</th></tr>
                <tr><td>1</td></tr>
            </table>
            <h2>Table 2</h2>
            <table>
                <tr><th>B</th></tr>
                <tr><td>2</td></tr>
            </table>
        </body>
        </html>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert len(sheets) == 2
        assert sheets[0].name == "Table 1"
        assert sheets[1].name == "Table 2"

    def test_import_caption_as_name(self, tmp_path: Path) -> None:
        """Test HTML import uses caption as sheet name."""
        html_file = tmp_path / "caption.html"
        html_content = """
        <table>
            <caption>Sales Data</caption>
            <tr><th>Product</th></tr>
            <tr><td>Widget</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert sheets[0].name == "Sales Data"

    def test_import_sanitize_sheet_name(self, tmp_path: Path) -> None:
        """Test HTML import sanitizes invalid sheet names."""
        html_file = tmp_path / "sanitize.html"
        html_content = """
        <h2>Name with <invalid> characters! & symbols</h2>
        <table>
            <tr><th>A</th></tr>
            <tr><td>1</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        # Should sanitize to valid sheet name
        assert "<" not in sheets[0].name
        assert ">" not in sheets[0].name
        assert "Name with" in sheets[0].name


# ==============================================================================
# Colspan/Rowspan Tests
# ==============================================================================


class TestHtmlImportSpans:
    """Tests for colspan/rowspan handling."""

    def test_import_colspan(self, tmp_path: Path) -> None:
        """Test HTML import handles colspan."""
        html_file = tmp_path / "colspan.html"
        html_content = """
        <table>
            <tr>
                <th colspan="2">Merged Header</th>
                <th>C</th>
            </tr>
            <tr>
                <td>A1</td>
                <td>B1</td>
                <td>C1</td>
            </tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert len(sheets) == 1
        sheet = sheets[0]
        # Colspan creates multiple columns
        assert len(sheet.columns) == 3
        assert sheet.columns[0].name == "Merged Header"
        assert sheet.columns[1].name == ""  # Empty from colspan
        assert sheet.columns[2].name == "C"

    def test_import_rowspan(self, tmp_path: Path) -> None:
        """Test HTML import handles rowspan."""
        html_file = tmp_path / "rowspan.html"
        html_content = """
        <table>
            <tr>
                <th>A</th>
                <th>B</th>
            </tr>
            <tr>
                <td rowspan="2">Merged</td>
                <td>B1</td>
            </tr>
            <tr>
                <td>B2</td>
            </tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert len(sheets) == 1
        sheet = sheets[0]
        assert len(sheet.rows) == 2
        # First data row has "Merged" and "B1"
        assert sheet.rows[0].cells[0].value == "Merged"
        assert sheet.rows[0].cells[1].value == "B1"
        # Second data row has None (spanned) and "B2"
        assert sheet.rows[1].cells[0].value is None
        assert sheet.rows[1].cells[1].value == "B2"

    def test_import_complex_spans(self, tmp_path: Path) -> None:
        """Test HTML import handles complex colspan+rowspan combinations."""
        html_file = tmp_path / "complex_spans.html"
        html_content = """
        <table>
            <tr>
                <th>A</th>
                <th colspan="2" rowspan="2">Merged</th>
            </tr>
            <tr>
                <th>B</th>
            </tr>
            <tr>
                <td>A1</td>
                <td>B1</td>
                <td>C1</td>
            </tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert len(sheets) == 1
        # Should handle complex spans without crashing
        assert sheets[0].columns is not None


# ==============================================================================
# Type Detection Tests
# ==============================================================================


class TestHtmlImportTypeDetection:
    """Tests for automatic type detection."""

    def test_import_type_detection_int(self, tmp_path: Path) -> None:
        """Test HTML import detects integers."""
        html_file = tmp_path / "types.html"
        html_content = """
        <table>
            <tr><th>Number</th></tr>
            <tr><td>42</td></tr>
            <tr><td>-17</td></tr>
            <tr><td>0</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert sheets[0].rows[0].cells[0].value == 42
        assert isinstance(sheets[0].rows[0].cells[0].value, int)
        assert sheets[0].rows[1].cells[0].value == -17
        assert sheets[0].rows[2].cells[0].value == 0

    def test_import_type_detection_float(self, tmp_path: Path) -> None:
        """Test HTML import detects floats."""
        html_file = tmp_path / "types.html"
        html_content = """
        <table>
            <tr><th>Decimal</th></tr>
            <tr><td>3.14</td></tr>
            <tr><td>1.5e2</td></tr>
            <tr><td>-0.5</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        assert sheets[0].rows[0].cells[0].value == 3.14
        assert isinstance(sheets[0].rows[0].cells[0].value, float)
        assert sheets[0].rows[1].cells[0].value == 150.0
        assert sheets[0].rows[2].cells[0].value == -0.5

    def test_import_type_detection_date(self, tmp_path: Path) -> None:
        """Test HTML import detects dates."""
        html_file = tmp_path / "types.html"
        html_content = """
        <table>
            <tr><th>Date</th></tr>
            <tr><td>2025-01-15</td></tr>
            <tr><td>01/15/2025</td></tr>
            <tr><td>01-15-2025</td></tr>
            <tr><td>2025/01/15</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        # All should be detected as dates
        for row in sheets[0].rows:
            assert isinstance(row.cells[0].value, date)
            assert row.cells[0].value == date(2025, 1, 15)

    def test_import_no_type_detection(self, tmp_path: Path) -> None:
        """Test HTML import without type detection."""
        html_file = tmp_path / "types.html"
        html_content = """
        <table>
            <tr><th>Value</th></tr>
            <tr><td>42</td></tr>
            <tr><td>3.14</td></tr>
            <tr><td>2025-01-15</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(detect_types=False)
        sheets = adapter.import_file(html_file, options)

        # Should all be strings
        assert sheets[0].rows[0].cells[0].value == "42"
        assert isinstance(sheets[0].rows[0].cells[0].value, str)
        assert sheets[0].rows[1].cells[0].value == "3.14"
        assert sheets[0].rows[2].cells[0].value == "2025-01-15"


# ==============================================================================
# Options Tests
# ==============================================================================


class TestHtmlImportOptions:
    """Tests for HTMLImportOptions configuration."""

    def test_import_css_selector(self, tmp_path: Path) -> None:
        """Test HTML import with CSS selector."""
        html_file = tmp_path / "selector.html"
        html_content = """
        <table class="data">
            <tr><th>Data</th></tr>
            <tr><td>1</td></tr>
        </table>
        <table class="other">
            <tr><th>Other</th></tr>
            <tr><td>2</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(table_selector="table.data")
        sheets = adapter.import_file(html_file, options)

        assert len(sheets) == 1
        assert sheets[0].rows[0].cells[0].value == 1

    def test_import_skip_empty_rows(self, tmp_path: Path) -> None:
        """Test HTML import skips empty rows."""
        html_file = tmp_path / "empty.html"
        html_content = """
        <table>
            <tr><th>A</th></tr>
            <tr><td>1</td></tr>
            <tr><td></td></tr>
            <tr><td>2</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(skip_empty_rows=True)
        sheets = adapter.import_file(html_file, options)

        assert len(sheets[0].rows) == 2  # Empty row skipped

    def test_import_no_skip_empty_rows(self, tmp_path: Path) -> None:
        """Test HTML import keeps empty rows when configured."""
        html_file = tmp_path / "empty.html"
        html_content = """
        <table>
            <tr><th>A</th></tr>
            <tr><td>1</td></tr>
            <tr><td></td></tr>
            <tr><td>2</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(skip_empty_rows=False)
        sheets = adapter.import_file(html_file, options)

        assert len(sheets[0].rows) == 3  # Empty row kept

    def test_import_trim_whitespace(self, tmp_path: Path) -> None:
        """Test HTML import trims whitespace."""
        html_file = tmp_path / "whitespace.html"
        html_content = """
        <table>
            <tr><th>  Heading  </th></tr>
            <tr><td>  Value  </td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(trim_whitespace=True)
        sheets = adapter.import_file(html_file, options)

        assert sheets[0].columns[0].name == "Heading"
        assert sheets[0].rows[0].cells[0].value == "Value"

    def test_import_no_header(self, tmp_path: Path) -> None:
        """Test HTML import with no header row."""
        html_file = tmp_path / "no_header.html"
        html_content = """
        <table>
            <tr><td>A1</td><td>B1</td></tr>
            <tr><td>A2</td><td>B2</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(header_row=False)
        sheets = adapter.import_file(html_file, options)

        # Should generate column names
        assert sheets[0].columns[0].name == "Column_1"
        assert sheets[0].columns[1].name == "Column_2"
        # All rows should be data
        assert len(sheets[0].rows) == 2

    def test_import_force_header(self, tmp_path: Path) -> None:
        """Test HTML import forcing first row as header."""
        html_file = tmp_path / "force_header.html"
        html_content = """
        <table>
            <tr><td>Name</td><td>Age</td></tr>
            <tr><td>Alice</td><td>30</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(header_row=True)
        sheets = adapter.import_file(html_file, options)

        assert sheets[0].columns[0].name == "Name"
        assert sheets[0].columns[1].name == "Age"
        assert len(sheets[0].rows) == 1

    def test_import_sheet_names_filter(self, tmp_path: Path) -> None:
        """Test HTML import with sheet_names filter."""
        html_file = tmp_path / "filter.html"
        html_content = """
        <h2>Keep This</h2>
        <table>
            <tr><th>A</th></tr>
            <tr><td>1</td></tr>
        </table>
        <h2>Skip This</h2>
        <table>
            <tr><th>B</th></tr>
            <tr><td>2</td></tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        options = HTMLImportOptions(sheet_names=["Keep This"])
        sheets = adapter.import_file(html_file, options)

        assert len(sheets) == 1
        assert sheets[0].name == "Keep This"


# ==============================================================================
# Edge Cases and Error Tests
# ==============================================================================


class TestHtmlImportEdgeCases:
    """Tests for edge cases and error handling."""

    def test_import_no_tables_error(self, tmp_path: Path) -> None:
        """Test HTML import raises error when no tables found."""
        html_file = tmp_path / "no_table.html"
        html_file.write_text("<html><body><p>No tables here</p></body></html>")

        adapter = HtmlAdapter()
        with pytest.raises(ValueError, match="No HTML tables found"):
            adapter.import_file(html_file)

    def test_import_missing_dependency(self, tmp_path: Path, monkeypatch: Any) -> None:
        """Test HTML import raises ImportError when dependencies missing."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<table></table>")

        # Mock missing bs4
        import builtins

        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if name == "bs4":
                raise ImportError("No module named 'bs4'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        adapter = HtmlAdapter()
        with pytest.raises(ImportError, match="HTML import requires beautifulsoup4"):
            adapter.import_file(html_file)

    def test_import_empty_table(self, tmp_path: Path) -> None:
        """Test HTML import with empty table."""
        html_file = tmp_path / "empty_table.html"
        html_content = """
        <table>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        # Empty table should be skipped
        assert len(sheets) == 0

    def test_import_tbody_tfoot(self, tmp_path: Path) -> None:
        """Test HTML import with tbody and tfoot sections."""
        html_file = tmp_path / "sections.html"
        html_content = """
        <table>
            <thead>
                <tr><th>Item</th><th>Amount</th></tr>
            </thead>
            <tbody>
                <tr><td>A</td><td>10</td></tr>
                <tr><td>B</td><td>20</td></tr>
            </tbody>
            <tfoot>
                <tr><td>Total</td><td>30</td></tr>
            </tfoot>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        # Should include tbody and tfoot rows
        assert len(sheets[0].rows) == 3
        assert sheets[0].rows[2].cells[0].value == "Total"

    def test_import_nested_tables(self, tmp_path: Path) -> None:
        """Test HTML import finds all tables including nested."""
        html_file = tmp_path / "nested.html"
        html_content = """
        <table>
            <tr><th>Outer</th></tr>
            <tr>
                <td>
                    <table>
                        <tr><th>Inner</th></tr>
                        <tr><td>Value</td></tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        html_file.write_text(html_content)

        adapter = HtmlAdapter()
        sheets = adapter.import_file(html_file)

        # BeautifulSoup find_all will find both tables
        assert len(sheets) >= 1


# ==============================================================================
# Round-Trip Tests
# ==============================================================================


class TestHtmlImportRoundTrip:
    """Tests for HTML export/import round-trips."""

    def test_import_round_trip(self, tmp_path: Path) -> None:
        """Test HTML export/import round-trip."""
        # Create sample sheet
        sample_sheet = SheetSpec(
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
                        CellSpec(value=75000.50),
                    ]
                ),
                RowSpec(
                    cells=[
                        CellSpec(value="Bob"),
                        CellSpec(value=25),
                        CellSpec(value=65000.00),
                    ]
                ),
            ],
        )

        adapter = HtmlAdapter()
        html_file = tmp_path / "round_trip.html"

        # Export
        adapter.export([sample_sheet], html_file)

        # Import
        sheets = adapter.import_file(html_file)

        assert len(sheets) == 1
        imported = sheets[0]
        assert imported.name == "TestSheet"
        assert len(imported.columns) == 3
        assert imported.columns[0].name == "Name"
        assert len(imported.rows) == 2
        assert imported.rows[0].cells[0].value == "Alice"
        # Note: Values may be typed differently after round-trip
        assert imported.rows[0].cells[1].value == 30
        assert imported.rows[0].cells[2].value == 75000.50

    def test_import_round_trip_preserves_structure(self, tmp_path: Path) -> None:
        """Test round-trip preserves table structure."""
        original = SheetSpec(
            name="Data",
            columns=[ColumnSpec(name="A"), ColumnSpec(name="B")],
            rows=[
                RowSpec(cells=[CellSpec(value=1), CellSpec(value=2)]),
                RowSpec(cells=[CellSpec(value=3), CellSpec(value=4)]),
            ],
        )

        adapter = HtmlAdapter()
        html_file = tmp_path / "structure.html"

        adapter.export([original], html_file)
        imported = adapter.import_file(html_file)

        assert len(imported) == 1
        assert len(imported[0].columns) == len(original.columns)
        assert len(imported[0].rows) == len(original.rows)
