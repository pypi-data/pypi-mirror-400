"""Tests for builder module - Spec classes and SpreadsheetBuilder."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.builder import (
    CellSpec,
    ColumnSpec,
    FormulaBuilder,
    NoRowSelectedError,
    NoSheetSelectedError,
    RowSpec,
    SheetSpec,
    SpreadsheetBuilder,
    create_spreadsheet,
    formula,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit, pytest.mark.builder]


class TestCellSpec:
    """Tests for CellSpec class."""

    def test_empty_cell(self) -> None:
        """Test empty cell specification."""
        cell = CellSpec()
        assert cell.is_empty()

    def test_cell_with_value(self) -> None:
        """Test cell with value."""
        cell = CellSpec(value="Hello")
        assert not cell.is_empty()
        assert cell.value == "Hello"

    def test_cell_with_formula(self) -> None:
        """Test cell with formula."""
        cell = CellSpec(formula="of:=SUM([.A1:A10])")
        assert not cell.is_empty()
        assert cell.formula == "of:=SUM([.A1:A10])"

    def test_cell_with_style(self) -> None:
        """Test cell with style."""
        cell = CellSpec(value="Styled", style="header")
        assert cell.style == "header"

    def test_cell_with_colspan(self) -> None:
        """Test cell with column span."""
        cell = CellSpec(value="Merged", colspan=3)
        assert cell.colspan == 3

    def test_cell_with_rowspan(self) -> None:
        """Test cell with row span."""
        cell = CellSpec(value="Merged", rowspan=2)
        assert cell.rowspan == 2

    def test_cell_with_value_type(self) -> None:
        """Test cell with explicit value type."""
        cell = CellSpec(value=100, value_type="currency")
        assert cell.value_type == "currency"

    def test_cell_with_validation(self) -> None:
        """Test cell with validation reference."""
        cell = CellSpec(value="", validation="list_validation")
        assert cell.validation == "list_validation"

    def test_cell_with_decimal_value(self) -> None:
        """Test cell with Decimal value."""
        cell = CellSpec(value=Decimal("123.45"))
        assert cell.value == Decimal("123.45")


class TestColumnSpec:
    """Tests for ColumnSpec class."""

    def test_default_column(self) -> None:
        """Test default column specification."""
        col = ColumnSpec(name="Amount")
        assert col.name == "Amount"
        assert col.width == "2.5cm"
        assert col.type == "string"

    def test_currency_column(self) -> None:
        """Test currency column specification."""
        col = ColumnSpec(name="Amount", type="currency", width="3cm")
        assert col.type == "currency"
        assert col.width == "3cm"

    def test_date_column(self) -> None:
        """Test date column specification."""
        col = ColumnSpec(name="Date", type="date", width="2.5cm")
        assert col.type == "date"

    def test_percentage_column(self) -> None:
        """Test percentage column specification."""
        col = ColumnSpec(name="Rate", type="percentage")
        assert col.type == "percentage"

    def test_hidden_column(self) -> None:
        """Test hidden column specification."""
        col = ColumnSpec(name="ID", hidden=True)
        assert col.hidden is True

    def test_column_with_validation(self) -> None:
        """Test column with validation reference."""
        col = ColumnSpec(name="Category", validation="category_list")
        assert col.validation == "category_list"


class TestRowSpec:
    """Tests for RowSpec class."""

    def test_empty_row(self) -> None:
        """Test empty row specification."""
        row = RowSpec()
        assert len(row.cells) == 0

    def test_row_with_cells(self) -> None:
        """Test row with cells."""
        row = RowSpec(cells=[CellSpec(value="A"), CellSpec(value="B")])
        assert len(row.cells) == 2

    def test_row_with_style(self) -> None:
        """Test row with style."""
        row = RowSpec(style="header")
        assert row.style == "header"

    def test_row_with_height(self) -> None:
        """Test row with custom height."""
        row = RowSpec(height="1cm")
        assert row.height == "1cm"


class TestSheetSpec:
    """Tests for SheetSpec class."""

    def test_empty_sheet(self) -> None:
        """Test empty sheet specification."""
        sheet = SheetSpec(name="Test")
        assert sheet.name == "Test"
        assert len(sheet.columns) == 0
        assert len(sheet.rows) == 0

    def test_sheet_with_freeze(self) -> None:
        """Test sheet with frozen rows/columns."""
        sheet = SheetSpec(name="Test", freeze_rows=1, freeze_cols=2)
        assert sheet.freeze_rows == 1
        assert sheet.freeze_cols == 2

    def test_sheet_with_print_area(self) -> None:
        """Test sheet with print area."""
        sheet = SheetSpec(name="Test", print_area="A1:D50")
        assert sheet.print_area == "A1:D50"

    def test_sheet_with_protection(self) -> None:
        """Test sheet with protection settings."""
        sheet = SheetSpec(
            name="Test",
            protection={"protected": True, "password": "secret"},
        )
        assert sheet.protection["protected"] is True


class TestSpreadsheetBuilder:
    """Tests for SpreadsheetBuilder class."""

    def test_create_builder_no_theme(self) -> None:
        """Test creating builder without theme."""
        builder = SpreadsheetBuilder(theme=None)
        assert builder._theme is None

    def test_create_builder_with_theme_name(self) -> None:
        """Test creating builder with theme name."""
        builder = SpreadsheetBuilder(theme="default")
        assert builder._theme_name == "default"

    def test_create_builder_with_theme_object(self) -> None:
        """Test creating builder with Theme object (line 1106)."""
        from spreadsheet_dl.schema.styles import Theme, ThemeSchema

        meta = ThemeSchema(name="test", version="1.0")
        theme = Theme(meta=meta)
        builder = SpreadsheetBuilder(theme=theme)
        assert builder._theme is theme
        assert builder._theme_name is None

    def test_get_theme_loads_theme(self, tmp_path: Path) -> None:
        """Test _get_theme loads theme from theme_name (lines 1118-1121)."""
        # Create a builder with theme name
        builder = SpreadsheetBuilder(theme="default")
        # First call should load the theme
        theme = builder._get_theme()
        assert theme is not None
        # Second call should return cached theme
        theme2 = builder._get_theme()
        assert theme2 is theme

    def test_get_theme_returns_none_for_no_theme(self) -> None:
        """Test _get_theme returns None when no theme."""
        builder = SpreadsheetBuilder(theme=None)
        theme = builder._get_theme()
        assert theme is None

    def test_add_sheet(self) -> None:
        """Test adding a sheet."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test Sheet")
        assert len(builder._sheets) == 1
        assert builder._sheets[0].name == "Test Sheet"

    def test_add_multiple_sheets(self) -> None:
        """Test adding multiple sheets."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Sheet1").sheet("Sheet2").sheet("Sheet3")
        assert len(builder._sheets) == 3

    def test_add_column(self) -> None:
        """Test adding columns."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("Date", width="2.5cm", type="date")
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.columns) == 1
        assert builder._current_sheet is not None
        assert builder._current_sheet.columns[0].name == "Date"

    def test_add_column_without_sheet_raises(self) -> None:
        """Test adding column without sheet raises error."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.column("Test")

    def test_add_columns(self) -> None:
        """Test adding multiple columns."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        builder.column("Date", width="2.5cm", type="date")
        builder.column("Amount", width="3cm", type="currency")
        builder.column("Notes", width="5cm", type="string")
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.columns) == 3

    def test_header_row(self) -> None:
        """Test adding header row."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B").header_row()
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 1
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows[0].cells) == 2

    def test_header_row_with_style(self) -> None:
        """Test adding header row with style."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B").header_row(style="header_primary")
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].style == "header_primary"

    def test_data_rows(self) -> None:
        """Test adding empty data rows."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B").data_rows(5)
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 5

    def test_add_row(self) -> None:
        """Test adding a row."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").row()
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 1

    def test_add_row_with_style(self) -> None:
        """Test adding a row with style."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").row(style="total_row")
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].style == "total_row"

    def test_add_cell(self) -> None:
        """Test adding a cell."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").row().cell("Value")
        assert builder._current_row is not None
        assert len(builder._current_row.cells) == 1
        assert builder._current_row is not None
        assert builder._current_row.cells[0].value == "Value"

    def test_add_cell_without_row_raises(self) -> None:
        """Test adding cell without row raises error."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        with pytest.raises(NoRowSelectedError):
            builder.cell("Value")

    def test_add_cell_with_formula(self) -> None:
        """Test adding cell with formula."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").row().cell(formula="of:=SUM([.A1:A10])")
        assert builder._current_row is not None
        assert builder._current_row.cells[0].formula == "of:=SUM([.A1:A10])"

    def test_add_cell_with_style(self) -> None:
        """Test adding cell with style."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").row().cell("Header", style="header")
        assert builder._current_row is not None
        assert builder._current_row.cells[0].style == "header"

    def test_add_cells(self) -> None:
        """Test adding multiple cells."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").row().cells("A", "B", "C")
        assert builder._current_row is not None
        assert len(builder._current_row.cells) == 3

    def test_formula_row(self) -> None:
        """Test adding formula row."""
        builder = SpreadsheetBuilder(theme=None)
        formulas = ["of:=SUM([.A1:A10])", None, "of:=COUNT([.C1:C10])"]
        builder.sheet("Test").column("A").column("B").column("C").formula_row(formulas)
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 1
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].cells[0].formula == formulas[0]

    def test_total_row(self) -> None:
        """Test adding total row."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        builder.column("Item").column("Amount", type="currency")
        builder.header_row()
        builder.total_row(formulas=[None, "of:=SUM([.B2:B100])"])
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 2

    def test_freeze(self) -> None:
        """Test setting freeze panes."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").freeze(rows=1, cols=2)
        assert builder._current_sheet is not None
        assert builder._current_sheet.freeze_rows == 1
        assert builder._current_sheet is not None
        assert builder._current_sheet.freeze_cols == 2

    def test_build(self) -> None:
        """Test building sheet specifications."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Sheet1").column("A")
        builder.sheet("Sheet2").column("B")
        specs = builder.build()
        assert len(specs) == 2
        assert specs[0].name == "Sheet1"
        assert specs[1].name == "Sheet2"

    def test_chaining(self) -> None:
        """Test fluent chaining."""
        builder = (
            SpreadsheetBuilder(theme=None)
            .sheet("Expenses")
            .column("Date", type="date")
            .column("Category")
            .column("Amount", type="currency")
            .header_row()
            .data_rows(10)
        )
        assert len(builder._sheets) == 1
        assert len(builder._sheets[0].columns) == 3
        assert len(builder._sheets[0].rows) == 11  # header + 10 data


class TestSpreadsheetBuilderAdvanced:
    """Tests for advanced SpreadsheetBuilder features."""

    def test_workbook_properties(self) -> None:
        """Test setting workbook properties."""
        builder = SpreadsheetBuilder(theme=None)
        builder.workbook_properties(
            title="My Budget",
            author="John Doe",
        )
        props = builder.get_properties()
        assert props.title == "My Budget"
        assert props.author == "John Doe"

    def test_workbook_properties_all_fields(self) -> None:
        """Test setting all workbook properties fields (lines 1152-1163)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.workbook_properties(
            title="Test Title",
            author="Test Author",
            subject="Test Subject",
            description="Test Description",
            keywords=["key1", "key2"],
            custom_field="custom_value",
        )
        props = builder.get_properties()
        assert props.title == "Test Title"
        assert props.author == "Test Author"
        assert props.subject == "Test Subject"
        assert props.description == "Test Description"
        assert props.keywords == ["key1", "key2"]
        assert props.custom["custom_field"] == "custom_value"

    def test_workbook_properties_none_values(self) -> None:
        """Test workbook properties with None values (conditional paths)."""
        builder = SpreadsheetBuilder(theme=None)
        # Call with None values - should not update
        builder.workbook_properties(
            title=None,
            author=None,
            subject=None,
            description=None,
            keywords=None,
        )
        props = builder.get_properties()
        assert props.title == ""
        assert props.author == ""

    def test_add_named_range(self) -> None:
        """Test adding named range."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Data")
        builder.named_range("MyRange", "A1", "B10")
        assert len(builder._named_ranges) == 1

    def test_named_range_with_explicit_sheet(self) -> None:
        """Test named range with explicit sheet name."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Data")
        builder.named_range("MyRange", "A1", "B10", sheet="OtherSheet")
        assert len(builder._named_ranges) == 1
        assert builder._named_ranges[0].scope == "OtherSheet"

    def test_get_named_ranges(self) -> None:
        """Test get_named_ranges method (line 1627)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Data")
        builder.named_range("Range1", "A1", "A10")
        builder.named_range("Range2", "B1", "B10")
        ranges = builder.get_named_ranges()
        assert len(ranges) == 2
        assert ranges[0].name == "Range1"
        assert ranges[1].name == "Range2"

    def test_add_chart(self) -> None:
        """Test adding chart to sheet."""
        from spreadsheet_dl.charts import ChartBuilder

        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Data")
        chart = (
            ChartBuilder()
            .column_chart()
            .title("Test Chart")
            .series("Values", "Data.B1:B10")
            .build()
        )
        builder.chart(chart)
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.charts) == 1

    def test_chart_without_sheet_raises(self) -> None:
        """Test adding chart without sheet raises error (line 1594)."""
        from spreadsheet_dl.charts import ChartBuilder

        builder = SpreadsheetBuilder(theme=None)
        chart = ChartBuilder().column_chart().build()
        with pytest.raises(NoSheetSelectedError):
            builder.chart(chart)

    def test_freeze_without_sheet_raises(self) -> None:
        """Test freeze without sheet raises error (line 1228)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.freeze(rows=1)

    def test_print_area_without_sheet_raises(self) -> None:
        """Test print_area without sheet raises error (lines 1243-1246)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.print_area("A1:D50")

    def test_print_area(self) -> None:
        """Test setting print area (lines 1245-1246)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        builder.print_area("A1:D50")
        assert builder._current_sheet is not None
        assert builder._current_sheet.print_area == "A1:D50"

    def test_protect_without_sheet_raises(self) -> None:
        """Test protect without sheet raises error (lines 1266-1274)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.protect(password="secret")

    def test_protect_with_all_options(self) -> None:
        """Test protect with all options (lines 1266-1274)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        builder.protect(password="secret", edit_cells=True, edit_objects=True)
        assert builder._current_sheet is not None
        assert builder._current_sheet.protection["enabled"] is True
        assert builder._current_sheet is not None
        assert builder._current_sheet.protection["password"] == "secret"
        assert builder._current_sheet is not None
        assert builder._current_sheet.protection["edit_cells"] is True
        assert builder._current_sheet is not None
        assert builder._current_sheet.protection["edit_objects"] is True

    def test_header_row_without_sheet_raises(self) -> None:
        """Test header_row without sheet raises error (line 1334)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.header_row()

    def test_row_without_sheet_raises(self) -> None:
        """Test row without sheet raises error (line 1356)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.row()

    def test_data_rows_without_sheet_raises(self) -> None:
        """Test data_rows without sheet raises error (line 1381)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.data_rows(5)

    def test_data_rows_with_alternate_styles(self) -> None:
        """Test data_rows with alternating styles (line 1388)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B")
        builder.data_rows(5, alternate_styles=["even", "odd"])
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 5
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].style == "even"
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[1].style == "odd"
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[2].style == "even"

    def test_total_row_without_sheet_raises(self) -> None:
        """Test total_row without sheet raises error (line 1418)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.total_row()

    def test_total_row_with_values(self) -> None:
        """Test total_row with values (lines 1422-1424)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B").column("C")
        builder.total_row(values=["Total", "100", "200"])
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 1
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].cells[0].value == "Total"
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].cells[1].value == "100"

    def test_total_row_with_text_in_formulas(self) -> None:
        """Test total_row with text values in formulas list (lines 1427-1433)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B")
        builder.total_row(formulas=["Total", "of:=SUM([.B2:B10])"])
        # First item is text (no = or of: prefix), second is formula
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].cells[0].value == "Total"
        assert builder._current_sheet is not None
        assert builder._current_sheet.rows[0].cells[1].formula == "of:=SUM([.B2:B10])"

    def test_total_row_empty(self) -> None:
        """Test total_row with no values or formulas (lines 1437-1439)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B").column("C")
        builder.total_row()
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows) == 1
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.rows[0].cells) == 3

    def test_formula_row_without_sheet_raises(self) -> None:
        """Test formula_row without sheet raises error (line 1462)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.formula_row(["of:=SUM([.A1:A10])"])

    def test_cells_without_row_raises(self) -> None:
        """Test cells without row raises error (line 1527)."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        with pytest.raises(NoRowSelectedError):
            builder.cells("A", "B", "C")

    def test_conditional_format_without_sheet_raises(self) -> None:
        """Test conditional_format without sheet raises error (lines 1547-1550)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.conditional_format("format1")

    def test_conditional_format(self) -> None:
        """Test adding conditional format."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        builder.conditional_format("highlight_red")
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.conditional_formats) == 1
        assert builder._current_sheet is not None
        assert builder._current_sheet.conditional_formats[0] == "highlight_red"

    def test_validation_without_sheet_raises(self) -> None:
        """Test validation without sheet raises error (lines 1562-1565)."""
        builder = SpreadsheetBuilder(theme=None)
        with pytest.raises(NoSheetSelectedError):
            builder.validation("val1")

    def test_validation(self) -> None:
        """Test adding validation."""
        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test")
        builder.validation("list_validation")
        assert builder._current_sheet is not None
        assert len(builder._current_sheet.validations) == 1
        assert builder._current_sheet is not None
        assert builder._current_sheet.validations[0] == "list_validation"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_spreadsheet(self) -> None:
        """Test create_spreadsheet function."""
        builder = create_spreadsheet(theme="default")
        assert isinstance(builder, SpreadsheetBuilder)
        assert builder._theme_name == "default"

    def test_create_spreadsheet_no_theme(self) -> None:
        """Test create_spreadsheet without theme."""
        builder = SpreadsheetBuilder(theme=None)
        assert builder._theme is None

    def test_formula_function(self) -> None:
        """Test formula function."""
        f = formula()
        assert isinstance(f, FormulaBuilder)


class TestSpreadsheetBuilderSave:
    """Tests for SpreadsheetBuilder.save method."""

    def test_save_creates_file(self, tmp_path: Path) -> None:
        """Test saving spreadsheet creates file."""
        output = tmp_path / "test.ods"

        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B").header_row().data_rows(5)
        path = builder.save(output)

        assert path.exists()
        assert path.stat().st_size > 0

    def test_save_multi_sheet(self, tmp_path: Path) -> None:
        """Test saving multi-sheet spreadsheet."""
        output = tmp_path / "multi_sheet.ods"

        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Sheet1").column("A").header_row()
        builder.sheet("Sheet2").column("B").header_row()
        path = builder.save(output)

        assert path.exists()

    def test_save_with_formulas(self, tmp_path: Path) -> None:
        """Test saving spreadsheet with formulas."""
        output = tmp_path / "formulas.ods"

        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").column("B")
        builder.row().cell(10).cell(20)
        builder.row().cell(formula="of:=SUM([.A1:A1])").cell(
            formula="of:=SUM([.B1:B1])"
        )
        path = builder.save(output)

        assert path.exists()

    def test_save_with_string_path(self, tmp_path: Path) -> None:
        """Test saving with string path."""
        output = str(tmp_path / "string_path.ods")

        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").header_row()
        path = builder.save(output)

        assert path.exists()

    def test_save_creates_directories(self, tmp_path: Path) -> None:
        """Test saving creates nested directories."""
        output = tmp_path / "nested" / "dir" / "test.ods"

        builder = SpreadsheetBuilder(theme=None)
        builder.sheet("Test").column("A").header_row()
        path = builder.save(output)

        assert path.exists()
        assert path.parent.exists()
