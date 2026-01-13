"""Tests for renderer module - Core OdsRenderer functionality."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.builder import (
    CellSpec,
    ColumnSpec,
    RangeRef,
    RowSpec,
    SheetSpec,
    SpreadsheetBuilder,
)
from spreadsheet_dl.renderer import OdsRenderer, render_sheets

if TYPE_CHECKING:
    from pathlib import Path

    pass


pytestmark = [pytest.mark.unit, pytest.mark.rendering]


class TestOdsRenderer:
    """Tests for OdsRenderer class."""

    def test_render_empty_sheet(self, tmp_path: Path) -> None:
        """Test rendering empty sheet."""
        output = tmp_path / "empty.ods"
        sheets = [SheetSpec(name="Empty")]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()
        assert path.stat().st_size > 0

    def test_render_sheet_with_columns(self, tmp_path: Path) -> None:
        """Test rendering sheet with columns."""
        output = tmp_path / "columns.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[
                    ColumnSpec(name="Date", width="2.5cm", type="date"),
                    ColumnSpec(name="Category", width="3cm"),
                    ColumnSpec(name="Amount", width="2cm", type="currency"),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_sheet_with_rows(self, tmp_path: Path) -> None:
        """Test rendering sheet with data rows."""
        output = tmp_path / "rows.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[
                    ColumnSpec(name="A"),
                    ColumnSpec(name="B"),
                ],
                rows=[
                    RowSpec(cells=[CellSpec(value="A"), CellSpec(value="B")]),
                    RowSpec(cells=[CellSpec(value="1"), CellSpec(value="2")]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_formulas(self, tmp_path: Path) -> None:
        """Test rendering sheet with formulas."""
        output = tmp_path / "formulas.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[
                    ColumnSpec(name="Values", type="float"),
                    ColumnSpec(name="Sum", type="float"),
                ],
                rows=[
                    RowSpec(cells=[CellSpec(value=10), CellSpec()]),
                    RowSpec(cells=[CellSpec(value=20), CellSpec()]),
                    RowSpec(
                        cells=[
                            CellSpec(value="Total"),
                            CellSpec(formula="of:=SUM([.A1:A2])"),
                        ]
                    ),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_multi_sheet(self, tmp_path: Path) -> None:
        """Test rendering multiple sheets."""
        output = tmp_path / "multi.ods"
        sheets = [
            SheetSpec(name="Sheet1", columns=[ColumnSpec(name="A")]),
            SheetSpec(name="Sheet2", columns=[ColumnSpec(name="B")]),
            SheetSpec(name="Sheet3", columns=[ColumnSpec(name="C")]),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_dates(self, tmp_path: Path) -> None:
        """Test rendering dates."""
        output = tmp_path / "dates.ods"
        sheets = [
            SheetSpec(
                name="Dates",
                columns=[ColumnSpec(name="Date", type="date")],
                rows=[
                    RowSpec(cells=[CellSpec(value=date(2025, 1, 15))]),
                    RowSpec(cells=[CellSpec(value=date(2025, 1, 16))]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_datetime(self, tmp_path: Path) -> None:
        """Test rendering datetime values."""
        output = tmp_path / "datetime.ods"
        sheets = [
            SheetSpec(
                name="DateTime",
                columns=[ColumnSpec(name="Timestamp", type="date")],
                rows=[
                    RowSpec(cells=[CellSpec(value=datetime(2025, 1, 15, 10, 30))]),
                    RowSpec(cells=[CellSpec(value=datetime(2025, 1, 16, 14, 45))]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_decimals(self, tmp_path: Path) -> None:
        """Test rendering Decimal values."""
        output = tmp_path / "decimals.ods"
        sheets = [
            SheetSpec(
                name="Currency",
                columns=[ColumnSpec(name="Amount", type="currency")],
                rows=[
                    RowSpec(cells=[CellSpec(value=Decimal("123.45"))]),
                    RowSpec(cells=[CellSpec(value=Decimal("678.90"))]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_float_values(self, tmp_path: Path) -> None:
        """Test rendering float values."""
        output = tmp_path / "floats.ods"
        sheets = [
            SheetSpec(
                name="Floats",
                columns=[ColumnSpec(name="Value", type="float")],
                rows=[
                    RowSpec(cells=[CellSpec(value=123.456)]),
                    RowSpec(cells=[CellSpec(value=0.5)]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_int_values(self, tmp_path: Path) -> None:
        """Test rendering integer values."""
        output = tmp_path / "ints.ods"
        sheets = [
            SheetSpec(
                name="Integers",
                columns=[ColumnSpec(name="Value", type="number")],
                rows=[
                    RowSpec(cells=[CellSpec(value=100)]),
                    RowSpec(cells=[CellSpec(value=-50)]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_percentage_type(self, tmp_path: Path) -> None:
        """Test rendering percentage type values."""
        output = tmp_path / "percentage.ods"
        sheets = [
            SheetSpec(
                name="Percentages",
                columns=[ColumnSpec(name="Rate", type="percentage")],
                rows=[
                    RowSpec(cells=[CellSpec(value=0.25)]),
                    RowSpec(cells=[CellSpec(value=0.75)]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_int_currency(self, tmp_path: Path) -> None:
        """Test rendering integer as currency."""
        output = tmp_path / "int_currency.ods"
        sheets = [
            SheetSpec(
                name="Currency",
                columns=[ColumnSpec(name="Amount", type="currency")],
                rows=[
                    RowSpec(cells=[CellSpec(value=1000)]),
                    RowSpec(cells=[CellSpec(value=500)]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_styles(self, tmp_path: Path) -> None:
        """Test rendering with style names."""
        output = tmp_path / "styled.ods"
        sheets = [
            SheetSpec(
                name="Styled",
                columns=[ColumnSpec(name="A")],
                rows=[
                    RowSpec(
                        cells=[CellSpec(value="Header", style="header")],
                        style="header",
                    ),
                    RowSpec(
                        cells=[CellSpec(value="100", style="currency")],
                    ),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_all_default_styles(self, tmp_path: Path) -> None:
        """Test rendering with all default style names."""
        output = tmp_path / "all_styles.ods"
        sheets = [
            SheetSpec(
                name="Styles",
                columns=[ColumnSpec(name="A")],
                rows=[
                    RowSpec(cells=[CellSpec(value="Header", style="header_primary")]),
                    RowSpec(cells=[CellSpec(value="Warning", style="warning")]),
                    RowSpec(cells=[CellSpec(value="Good", style="good")]),
                    RowSpec(cells=[CellSpec(value="Success", style="cell_success")]),
                    RowSpec(cells=[CellSpec(value="Danger", style="cell_danger")]),
                    RowSpec(cells=[CellSpec(value="Total", style="total_row")]),
                    RowSpec(cells=[CellSpec(value="Normal", style="cell_normal")]),
                    RowSpec(cells=[CellSpec(value="Date", style="cell_date")]),
                    RowSpec(cells=[CellSpec(value="Currency", style="cell_currency")]),
                    RowSpec(cells=[CellSpec(value="Default", style="default")]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_unknown_style(self, tmp_path: Path) -> None:
        """Test rendering with unknown style falls back to default."""
        output = tmp_path / "unknown_style.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[ColumnSpec(name="A")],
                rows=[
                    RowSpec(cells=[CellSpec(value="Data", style="nonexistent_style")]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_row_style(self, tmp_path: Path) -> None:
        """Test rendering with row-level style."""
        output = tmp_path / "row_style.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[ColumnSpec(name="A"), ColumnSpec(name="B")],
                rows=[
                    RowSpec(
                        cells=[CellSpec(value="X"), CellSpec(value="Y")],
                        style="header",
                    ),
                    RowSpec(
                        cells=[CellSpec(value="1"), CellSpec(value="2")],
                        style="total",
                    ),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_cell_value_type(self, tmp_path: Path) -> None:
        """Test rendering with explicit cell value type."""
        output = tmp_path / "value_type.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[ColumnSpec(name="A")],
                rows=[
                    RowSpec(cells=[CellSpec(value=100, value_type="currency")]),
                    RowSpec(cells=[CellSpec(value=0.5, value_type="percentage")]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_none_value(self, tmp_path: Path) -> None:
        """Test rendering with None value."""
        output = tmp_path / "none_value.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[ColumnSpec(name="A")],
                rows=[
                    RowSpec(cells=[CellSpec(value=None)]),
                    RowSpec(cells=[CellSpec()]),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()


class TestOdsRendererCellMerging:
    """Tests for cell merge rendering."""

    def test_render_with_colspan(self, tmp_path: Path) -> None:
        """Test rendering with column span."""
        output = tmp_path / "colspan.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[
                    ColumnSpec(name="A"),
                    ColumnSpec(name="B"),
                    ColumnSpec(name="C"),
                ],
                rows=[
                    RowSpec(
                        cells=[
                            CellSpec(value="Merged", colspan=3),
                        ]
                    ),
                    RowSpec(
                        cells=[
                            CellSpec(value="1"),
                            CellSpec(value="2"),
                            CellSpec(value="3"),
                        ]
                    ),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_rowspan(self, tmp_path: Path) -> None:
        """Test rendering with row span."""
        output = tmp_path / "rowspan.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[
                    ColumnSpec(name="A"),
                    ColumnSpec(name="B"),
                ],
                rows=[
                    RowSpec(
                        cells=[
                            CellSpec(value="Merged", rowspan=2),
                            CellSpec(value="Row 1"),
                        ]
                    ),
                    RowSpec(
                        cells=[
                            CellSpec(value="Row 2"),
                        ]
                    ),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_colspan_and_rowspan(self, tmp_path: Path) -> None:
        """Test rendering with both column and row span."""
        output = tmp_path / "merged.ods"
        sheets = [
            SheetSpec(
                name="Test",
                columns=[
                    ColumnSpec(name="A"),
                    ColumnSpec(name="B"),
                    ColumnSpec(name="C"),
                ],
                rows=[
                    RowSpec(
                        cells=[
                            CellSpec(value="Big Cell", colspan=2, rowspan=2),
                            CellSpec(value="1"),
                        ]
                    ),
                    RowSpec(
                        cells=[
                            CellSpec(value="2"),
                        ]
                    ),
                    RowSpec(
                        cells=[
                            CellSpec(value="A"),
                            CellSpec(value="B"),
                            CellSpec(value="C"),
                        ]
                    ),
                ],
            ),
        ]

        renderer = OdsRenderer()
        path = renderer.render(sheets, output)

        assert path.exists()


class TestOdsRendererNamedRanges:
    """Tests for named range rendering."""

    def test_render_with_named_range(self, tmp_path: Path) -> None:
        """Test rendering with sheet-scoped named ranges (lines 531-567)."""
        from spreadsheet_dl.builder import NamedRange

        output_file = tmp_path / "named_ranges.ods"
        renderer = OdsRenderer()

        # Create sheet with data
        sheet = SheetSpec(name="Data")
        row = RowSpec()
        row.cells.append(CellSpec(value="A"))
        row.cells.append(CellSpec(value="B"))
        sheet.rows.append(row)

        # Create sheet-scoped named range
        named_range = NamedRange(
            name="DataRange",
            range=RangeRef(start="A1", end="B10", sheet="Data"),
            scope="Data",
        )

        result = renderer.render([sheet], output_file, named_ranges=[named_range])
        assert result == output_file
        assert output_file.exists()

    def test_render_with_workbook_scoped_range(self, tmp_path: Path) -> None:
        """Test rendering with workbook-scoped named range (lines 556-558)."""
        from spreadsheet_dl.builder import NamedRange

        output_file = tmp_path / "workbook_range.ods"
        renderer = OdsRenderer()

        sheet = SheetSpec(name="Sheet1")
        row = RowSpec()
        row.cells.append(CellSpec(value=1))
        row.cells.append(CellSpec(value=2))
        sheet.rows.append(row)

        # Create workbook-scoped named range (no sheet specified)
        named_range = NamedRange(
            name="GlobalRange",
            range=RangeRef(start="A1", end="C5", sheet=None),
            scope="workbook",
        )

        result = renderer.render([sheet], output_file, named_ranges=[named_range])
        assert result == output_file
        assert output_file.exists()

    def test_render_with_multiple_named_ranges(self, tmp_path: Path) -> None:
        """Test rendering with multiple named ranges (lines 540-567)."""
        from spreadsheet_dl.builder import NamedRange

        output_file = tmp_path / "multiple_ranges.ods"
        renderer = OdsRenderer()

        sheet = SheetSpec(name="Test")
        row = RowSpec()
        row.cells.append(CellSpec(value="Data"))
        sheet.rows.append(row)

        # Multiple named ranges - tests NamedExpressions reuse (lines 540-544)
        ranges = [
            NamedRange(
                name="Range1",
                range=RangeRef(start="A1", end="A10", sheet="Test"),
                scope="Test",
            ),
            NamedRange(
                name="Range2",
                range=RangeRef(start="B1", end="B10", sheet=None),
                scope="workbook",
            ),
        ]

        result = renderer.render([sheet], output_file, named_ranges=ranges)
        assert result == output_file
        assert output_file.exists()


class TestOdsRendererValueTypeMapping:
    """Tests for ODF value type mapping."""

    def test_get_odf_value_type_string(self) -> None:
        """Test string value type mapping."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type("string") == "string"

    def test_get_odf_value_type_currency(self) -> None:
        """Test currency value type mapping."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type("currency") == "currency"

    def test_get_odf_value_type_date(self) -> None:
        """Test date value type mapping."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type("date") == "date"

    def test_get_odf_value_type_percentage(self) -> None:
        """Test percentage value type mapping."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type("percentage") == "percentage"

    def test_get_odf_value_type_float(self) -> None:
        """Test float value type mapping."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type("float") == "float"

    def test_get_odf_value_type_number(self) -> None:
        """Test number value type mapping."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type("number") == "float"

    def test_get_odf_value_type_unknown(self) -> None:
        """Test unknown value type defaults to string."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type("unknown") == "string"

    def test_get_odf_value_type_none(self) -> None:
        """Test None value type defaults to string."""
        renderer = OdsRenderer()
        assert renderer._get_odf_value_type(None) == "string"


class TestOdsRendererDisplayText:
    """Tests for display text generation."""

    def test_display_text_none(self) -> None:
        """Test display text for None value."""
        renderer = OdsRenderer()
        assert renderer._get_display_text(None, None) == ""

    def test_display_text_date(self) -> None:
        """Test display text for date value."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(date(2025, 1, 15), "date")
        assert result == "2025-01-15"

    def test_display_text_datetime(self) -> None:
        """Test display text for datetime value."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(datetime(2025, 1, 15, 10, 30), "date")
        assert result == "2025-01-15"

    def test_display_text_decimal_currency(self) -> None:
        """Test display text for Decimal as currency."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(Decimal("123.45"), "currency")
        assert result == "$123.45"

    def test_display_text_float_currency(self) -> None:
        """Test display text for float as currency."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(123.45, "currency")
        assert result == "$123.45"

    def test_display_text_decimal_percentage(self) -> None:
        """Test display text for Decimal as percentage."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(Decimal("0.25"), "percentage")
        assert result == "25.0%"

    def test_display_text_float_percentage(self) -> None:
        """Test display text for float as percentage."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(0.25, "percentage")
        assert result == "25.0%"

    def test_display_text_decimal_default(self) -> None:
        """Test display text for Decimal without type."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(Decimal("123.45"), None)
        assert result == "123.45"

    def test_display_text_int_currency(self) -> None:
        """Test display text for int as currency."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(1000, "currency")
        assert result == "$1,000"

    def test_display_text_int_default(self) -> None:
        """Test display text for int without type."""
        renderer = OdsRenderer()
        result = renderer._get_display_text(1000, None)
        assert result == "1000"

    def test_display_text_string(self) -> None:
        """Test display text for string value."""
        renderer = OdsRenderer()
        result = renderer._get_display_text("Hello World", None)
        assert result == "Hello World"


class TestOdsRendererValueAttrs:
    """Tests for value attribute generation."""

    def test_value_attrs_none(self) -> None:
        """Test value attrs for None."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(None, None)
        assert attrs == {}

    def test_value_attrs_date(self) -> None:
        """Test value attrs for date."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(date(2025, 1, 15), None)
        assert attrs["valuetype"] == "date"
        assert attrs["datevalue"] == "2025-01-15"

    def test_value_attrs_datetime(self) -> None:
        """Test value attrs for datetime."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(datetime(2025, 1, 15, 10, 30), None)
        assert attrs["valuetype"] == "date"
        # datetime is checked first, so value.date().isoformat() is called (date only)
        assert attrs["datevalue"] == "2025-01-15"

    def test_value_attrs_decimal_currency(self) -> None:
        """Test value attrs for Decimal as currency."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(Decimal("123.45"), "currency")
        assert attrs["valuetype"] == "currency"
        assert attrs["value"] == "123.45"

    def test_value_attrs_decimal_float(self) -> None:
        """Test value attrs for Decimal as float."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(Decimal("123.45"), "float")
        assert attrs["valuetype"] == "float"
        assert attrs["value"] == "123.45"

    def test_value_attrs_int_currency(self) -> None:
        """Test value attrs for int as currency."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(100, "currency")
        assert attrs["valuetype"] == "currency"
        assert attrs["value"] == "100"

    def test_value_attrs_int_percentage(self) -> None:
        """Test value attrs for int as percentage."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(50, "percentage")
        assert attrs["valuetype"] == "percentage"
        assert attrs["value"] == "50"

    def test_value_attrs_float_default(self) -> None:
        """Test value attrs for float without type."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs(123.45, None)
        assert attrs["valuetype"] == "float"
        assert attrs["value"] == "123.45"

    def test_value_attrs_string(self) -> None:
        """Test value attrs for string."""
        renderer = OdsRenderer()
        attrs = renderer._get_value_attrs("Hello", None)
        assert attrs["valuetype"] == "string"


# Check if pyyaml is available
try:
    import yaml  # noqa: F401

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestOdsRendererWithTheme:
    """Tests for OdsRenderer with theme support."""

    def test_render_with_theme(self, tmp_path: Path) -> None:
        """Test rendering with theme."""
        from spreadsheet_dl.schema.loader import ThemeLoader

        output = tmp_path / "themed.ods"
        loader = ThemeLoader()
        theme = loader.load("default")

        sheets = [
            SheetSpec(
                name="Themed",
                columns=[ColumnSpec(name="A")],
                rows=[
                    RowSpec(
                        cells=[CellSpec(value="Header", style="header_primary")],
                    ),
                ],
            ),
        ]

        renderer = OdsRenderer(theme=theme)
        path = renderer.render(sheets, output)

        assert path.exists()

    def test_render_with_theme_styles_applied(self, tmp_path: Path) -> None:
        """Test that theme styles are applied correctly."""
        from spreadsheet_dl.schema.loader import ThemeLoader

        output = tmp_path / "themed_styles.ods"
        loader = ThemeLoader()
        theme = loader.load("default")

        sheets = [
            SheetSpec(
                name="Themed",
                columns=[ColumnSpec(name="A")],
                rows=[
                    RowSpec(cells=[CellSpec(value="Header", style="header_primary")]),
                    RowSpec(cells=[CellSpec(value="Warning", style="cell_warning")]),
                    RowSpec(cells=[CellSpec(value="Success", style="cell_success")]),
                ],
            ),
        ]

        renderer = OdsRenderer(theme=theme)
        path = renderer.render(sheets, output)

        assert path.exists()


class TestRenderSheetsFunction:
    """Tests for render_sheets convenience function."""

    def test_render_sheets_basic(self, tmp_path: Path) -> None:
        """Test render_sheets convenience function."""
        output = tmp_path / "basic.ods"
        sheets = [SheetSpec(name="Test", columns=[ColumnSpec(name="A")])]

        path = render_sheets(sheets, output)

        assert path.exists()

    def test_render_sheets_with_string_path(self, tmp_path: Path) -> None:
        """Test render_sheets with string path."""
        output = str(tmp_path / "string_path.ods")
        sheets = [SheetSpec(name="Test")]

        path = render_sheets(sheets, output)

        assert path.exists()

    def test_render_sheets_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Test that render_sheets creates parent directories."""
        output = tmp_path / "nested" / "dir" / "file.ods"
        sheets = [SheetSpec(name="Test")]

        path = render_sheets(sheets, output)

        assert path.exists()
        assert path.parent.exists()

    def test_render_sheets_with_named_ranges(self, tmp_path: Path) -> None:
        """Test render_sheets with named ranges."""
        from spreadsheet_dl.builder import NamedRange, RangeRef

        output = tmp_path / "named_ranges.ods"
        sheets = [
            SheetSpec(
                name="Data",
                columns=[ColumnSpec(name="Values")],
                rows=[
                    RowSpec(cells=[CellSpec(value=100)]),
                    RowSpec(cells=[CellSpec(value=200)]),
                    RowSpec(cells=[CellSpec(value=300)]),
                ],
            ),
        ]
        named_ranges = [
            NamedRange(
                name="DataRange",
                range=RangeRef(start="A1", end="A3", sheet="Data"),
            ),
        ]

        path = render_sheets(sheets, output, named_ranges=named_ranges)

        assert path.exists()
        assert path.stat().st_size > 0

        # Verify named range was written by checking ODS content
        import zipfile

        with zipfile.ZipFile(path, "r") as zf:
            content = zf.read("content.xml").decode("utf-8")
            assert "named-expressions" in content
            assert "DataRange" in content


class TestRendererIntegration:
    """Integration tests for renderer with builder."""

    def test_builder_save_uses_renderer(self, tmp_path: Path) -> None:
        """Test that SpreadsheetBuilder.save uses renderer."""
        output = tmp_path / "builder_save.ods"

        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B").header_row().data_rows(10)

        path = builder.save(output)

        assert path.exists()
        assert path.stat().st_size > 0

    def test_complete_budget_workflow(self, tmp_path: Path) -> None:
        """Test complete budget spreadsheet workflow."""
        output = tmp_path / "complete_budget.ods"

        builder = SpreadsheetBuilder(theme=None)

        # Expense Log sheet
        builder.sheet("Expense Log").column("Date", width="2.5cm", type="date").column(
            "Category", width="3cm"
        ).column("Description", width="4cm").column(
            "Amount", width="2.5cm", type="currency"
        ).column("Notes", width="4cm").header_row(style="header").data_rows(50)

        # Budget sheet
        builder.sheet("Budget").column("Category", width="3cm").column(
            "Monthly Budget", width="3cm", type="currency"
        ).header_row(style="header")

        # Add sample budget rows
        categories = ["Groceries", "Utilities", "Entertainment"]
        for cat in categories:
            builder.row().cell(cat).cell(Decimal("500"))

        path = builder.save(output)

        assert path.exists()
        assert path.stat().st_size > 0


# =============================================================================
# Chart Rendering Tests
# =============================================================================
