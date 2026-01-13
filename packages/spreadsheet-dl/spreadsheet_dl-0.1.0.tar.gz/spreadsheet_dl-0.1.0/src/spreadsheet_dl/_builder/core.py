"""Main SpreadsheetBuilder class for fluent spreadsheet construction.

    - PHASE0-004: Perfect Builder API (v4.0.0)

Provides a chainable API for building multi-sheet spreadsheets
with theme support, including workbook properties, sheet freezing,
protection, conditional formats, validations, and charts.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from spreadsheet_dl._builder.exceptions import (
    EmptySheetError,
    NoRowSelectedError,
    NoSheetSelectedError,
)
from spreadsheet_dl._builder.formulas import FormulaBuilder
from spreadsheet_dl._builder.models import (
    CellSpec,
    ColumnSpec,
    RowSpec,
    SheetSpec,
    WorkbookProperties,
)
from spreadsheet_dl._builder.references import NamedRange, RangeRef

if TYPE_CHECKING:
    from collections.abc import Sequence

    from spreadsheet_dl.charts import ChartSpec
    from spreadsheet_dl.schema.styles import Theme


class SpreadsheetBuilder:
    r"""Fluent builder for creating spreadsheets.

    Implements PHASE0-004: Perfect Builder API (v4.0.0)

    Provides a chainable API for building multi-sheet spreadsheets
    with theme support, including:
    - Workbook-level properties
    - Sheet freezing and protection
    - Alternating row styles
    - Total row formulas
    - Conditional formats and validations
    - Charts

    v4.0.0 Improvements:
    - Enhanced error messages with actionable guidance
    - Better edge case handling
    - Consistent method signatures
    - Improved validation

    Examples:
        builder = SpreadsheetBuilder(theme="corporate")

        builder.workbook_properties(
            title="Monthly Budget",
            author="Finance Team",
        )

        builder.sheet("Budget") \\
            .column("Category", width="150pt", style="text") \\
            .column("Budget", width="100pt", type="currency") \\
            .column("Actual", width="100pt", type="currency") \\
            .freeze(rows=1) \\
            .header_row(style="header") \\
            .data_rows(20, alternate_styles=["row_even", "row_odd"]) \\
            .total_row(style="total", formulas=["Total", "=SUM(B2:B21)", "=SUM(C2:C21)"])

        # Add a chart
        from spreadsheet_dl.charts import ChartBuilder
        chart = ChartBuilder() \\
            .column_chart() \\
            .title("Budget vs Actual") \\
            .series("Budget", "Budget.B2:B21") \\
            .series("Actual", "Budget.C2:C21") \\
            .build()
        builder.chart(chart)

        builder.save("budget.ods")
    """

    def __init__(
        self,
        theme: str | Theme | None = "default",
        theme_dir: Path | str | None = None,
    ) -> None:
        """Initialize builder with theme.

        Args:
            theme: Theme name, Theme object, or None for no theme
            theme_dir: Directory containing theme files
        """
        self._theme: Theme | None = None
        self._theme_name: str | None = None

        if theme is not None:
            if isinstance(theme, str):
                self._theme_name = theme
            else:
                self._theme = theme

        self._theme_dir = Path(theme_dir) if theme_dir else None
        self._sheets: list[SheetSpec] = []
        self._current_sheet: SheetSpec | None = None
        self._current_row: RowSpec | None = None
        self._workbook_properties = WorkbookProperties()
        self._named_ranges: list[NamedRange] = []

    def _get_theme(self) -> Theme | None:
        """Get or load the theme."""
        if self._theme is None and self._theme_name is not None:
            from spreadsheet_dl.schema.loader import ThemeLoader

            loader = ThemeLoader(self._theme_dir)
            self._theme = loader.load(self._theme_name)
        return self._theme

    # =========================================================================
    # Workbook-Level Properties
    # =========================================================================

    def workbook_properties(
        self,
        *,
        title: str | None = None,
        author: str | None = None,
        subject: str | None = None,
        description: str | None = None,
        keywords: list[str] | None = None,
        **custom: str,
    ) -> Self:
        """Set workbook-level properties.

        Args:
            title: Document title
            author: Document author
            subject: Document subject
            description: Document description
            keywords: Document keywords
            **custom: Custom properties

        Returns:
            Self for chaining
        """
        if title:
            self._workbook_properties.title = title
        if author:
            self._workbook_properties.author = author
        if subject:
            self._workbook_properties.subject = subject
        if description:
            self._workbook_properties.description = description
        if keywords:
            self._workbook_properties.keywords = keywords
        for key, value in custom.items():
            self._workbook_properties.custom[key] = value
        return self

    def named_range(
        self,
        name: str,
        start: str,
        end: str,
        sheet: str | None = None,
    ) -> Self:
        """Define a named range.

        Args:
            name: Range name
            start: Start cell reference
            end: End cell reference
            sheet: Sheet name (None for current sheet)

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet active and sheet parameter is None
        """
        sheet_name = sheet or (
            self._current_sheet.name if self._current_sheet else None
        )
        if sheet_name is None:
            raise NoSheetSelectedError(
                "add named range without explicit sheet parameter"
            )
        self._named_ranges.append(
            NamedRange(
                name=name,
                range=RangeRef(start, end, sheet_name),
                scope="workbook" if sheet is None else sheet_name,
            )
        )
        return self

    # =========================================================================
    # Sheet Operations
    # =========================================================================

    def sheet(self, name: str) -> Self:
        """Start a new sheet.

        Args:
            name: Sheet name

        Returns:
            Self for chaining
        """
        self._current_sheet = SheetSpec(name=name)
        self._sheets.append(self._current_sheet)
        self._current_row = None
        return self

    def freeze(self, *, rows: int = 0, cols: int = 0) -> Self:
        """Freeze rows and/or columns.

        Args:
            rows: Number of rows to freeze
            cols: Number of columns to freeze

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("freeze rows/columns")
        self._current_sheet.freeze_rows = rows
        self._current_sheet.freeze_cols = cols
        return self

    def print_area(self, range_ref: str) -> Self:
        """Set print area.

        Args:
            range_ref: Range reference (e.g., "A1:D50")

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("set print area")
        self._current_sheet.print_area = range_ref
        return self

    def protect(
        self,
        *,
        password: str | None = None,
        edit_cells: bool = False,
        edit_objects: bool = False,
    ) -> Self:
        """Enable sheet protection.

        Args:
            password: Protection password
            edit_cells: Allow editing unlocked cells
            edit_objects: Allow editing objects

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("enable protection")
        self._current_sheet.protection = {
            "enabled": True,
            "password": password,
            "edit_cells": edit_cells,
            "edit_objects": edit_objects,
        }
        return self

    # =========================================================================
    # Column Operations
    # =========================================================================

    def column(
        self,
        name: str,
        *,
        width: str = "2.5cm",
        type: str = "string",
        style: str | None = None,
        validation: str | None = None,
        hidden: bool = False,
    ) -> Self:
        """Add a column to current sheet.

        Args:
            name: Column header name
            width: Column width (e.g., "2.5cm", "100px", "100pt")
            type: Value type (string, currency, date, percentage)
            style: Default style for cells
            validation: Data validation reference
            hidden: Whether column is hidden

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add column")

        self._current_sheet.columns.append(
            ColumnSpec(
                name=name,
                width=width,
                type=type,
                style=style,
                validation=validation,
                hidden=hidden,
            )
        )
        return self

    # =========================================================================
    # Row Operations
    # =========================================================================

    def header_row(self, *, style: str = "header_primary") -> Self:
        """Add header row with column names.

        Args:
            style: Style for header cells

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add header row")

        row = RowSpec(style=style)
        for col in self._current_sheet.columns:
            row.cells.append(CellSpec(value=col.name, style=style))

        self._current_sheet.rows.append(row)
        self._current_row = None
        return self

    def row(self, *, style: str | None = None, height: str | None = None) -> Self:
        """Start a new row.

        Args:
            style: Default style for cells in this row
            height: Row height (e.g., "20pt")

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add row")

        self._current_row = RowSpec(style=style, height=height)
        self._current_sheet.rows.append(self._current_row)
        return self

    def data_rows(
        self,
        count: int,
        *,
        style: str | None = None,
        alternate_styles: list[str] | None = None,
    ) -> Self:
        """Add empty data entry rows with optional alternating styles.

        Args:
            count: Number of rows to add
            style: Style for cells (used if alternate_styles not provided)
            alternate_styles: List of styles to alternate (e.g., ["row_even", "row_odd"])

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
            ValueError: If count is less than 1
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add data rows")

        if count < 1:
            raise ValueError(
                f"count must be >= 1, got {count}. "
                "Fix: Specify a positive number of rows to add."
            )

        col_count = len(self._current_sheet.columns)
        for i in range(count):
            # Determine row style
            row_style: str | None
            if alternate_styles:
                row_style = alternate_styles[i % len(alternate_styles)]
            else:
                row_style = style

            row = RowSpec(style=row_style)
            row.cells = [CellSpec(style=row_style) for _ in range(col_count)]
            self._current_sheet.rows.append(row)

        self._current_row = None
        return self

    def total_row(
        self,
        *,
        style: str | None = "total",
        values: Sequence[str | None] | None = None,
        formulas: Sequence[str | None] | None = None,
    ) -> Self:
        """Add a total/summary row.

        Args:
            style: Style for total row cells
            values: List of static values (None for empty)
            formulas: List of formula strings (None for empty)

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add total row")

        row = RowSpec(style=style)

        if values:
            for value in values:
                row.cells.append(CellSpec(value=value, style=style))
        elif formulas:
            for formula in formulas:
                if (
                    formula
                    and not formula.startswith("=")
                    and not formula.startswith("of:")
                ):
                    # Treat as value, not formula
                    row.cells.append(CellSpec(value=formula, style=style))
                else:
                    row.cells.append(CellSpec(formula=formula, style=style))
        else:
            # Empty total row
            col_count = len(self._current_sheet.columns)
            row.cells = [CellSpec(style=style) for _ in range(col_count)]

        self._current_sheet.rows.append(row)
        self._current_row = None
        return self

    def formula_row(
        self,
        formulas: Sequence[str | None],
        *,
        style: str | None = None,
    ) -> Self:
        """Add a row with formulas.

        Args:
            formulas: List of formula strings (None for empty cells)
            style: Style for cells

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add formula row")

        row = RowSpec(style=style)
        for formula in formulas:
            row.cells.append(CellSpec(formula=formula, style=style))

        self._current_sheet.rows.append(row)
        self._current_row = None
        return self

    # =========================================================================
    # Cell Operations
    # =========================================================================

    def cell(
        self,
        value: Any = None,
        *,
        formula: str | None = None,
        style: str | None = None,
        colspan: int = 1,
        rowspan: int = 1,
        value_type: str | None = None,
    ) -> Self:
        """Add a cell to current row.

        Args:
            value: Cell value
            formula: ODF formula
            style: Style name
            colspan: Columns to span
            rowspan: Rows to span
            value_type: ODF value type

        Returns:
            Self for chaining

        Raises:
            NoRowSelectedError: If no row is currently active
        """
        if self._current_row is None:
            raise NoRowSelectedError("add cell")

        self._current_row.cells.append(
            CellSpec(
                value=value,
                formula=formula,
                style=style,
                colspan=colspan,
                rowspan=rowspan,
                value_type=value_type,
            )
        )
        return self

    def cells(self, *values: Any, style: str | None = None) -> Self:
        """Add multiple cells to current row.

        Args:
            *values: Cell values
            style: Style for all cells

        Returns:
            Self for chaining

        Raises:
            NoRowSelectedError: If no row is currently active
        """
        if self._current_row is None:
            raise NoRowSelectedError("add cells")

        for value in values:
            self._current_row.cells.append(CellSpec(value=value, style=style))
        return self

    # =========================================================================
    # Conditional Format and Validation
    # =========================================================================

    def conditional_format(self, format_ref: str) -> Self:
        """Add a conditional format reference to current sheet.

        Args:
            format_ref: Conditional format reference name

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add conditional format")
        self._current_sheet.conditional_formats.append(format_ref)
        return self

    def validation(self, validation_ref: str) -> Self:
        """Add a data validation reference to current sheet.

        Args:
            validation_ref: Validation reference name

        Returns:
            Self for chaining

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add validation")
        self._current_sheet.validations.append(validation_ref)
        return self

    # =========================================================================
    # Charts
    # =========================================================================

    def chart(self, chart_spec: ChartSpec) -> Self:
        r"""Add a chart to current sheet.

        Args:
            chart_spec: ChartSpec from ChartBuilder.build()

        Returns:
            Self for chaining

        Examples:
            from spreadsheet_dl.charts import ChartBuilder

            chart = ChartBuilder() \\
                .column_chart() \\
                .title("Budget vs Actual") \\
                .series("Budget", "B2:B20") \\
                .series("Actual", "C2:C20") \\
                .build()

            builder.sheet("Summary").chart(chart)

        Raises:
            NoSheetSelectedError: If no sheet is currently active
        """
        if self._current_sheet is None:
            raise NoSheetSelectedError("add chart")
        self._current_sheet.charts.append(chart_spec)
        return self

    # =========================================================================
    # Build and Save
    # =========================================================================

    def build(self) -> list[SheetSpec]:
        """Return the built sheet specifications.

        Returns:
            List of SheetSpec objects

        Raises:
            EmptySheetError: If any sheet is empty or invalid
        """
        # Validate all sheets
        for sheet in self._sheets:
            if len(sheet.columns) == 0 and len(sheet.rows) == 0:
                raise EmptySheetError(sheet.name, "no columns or rows defined")

        return self._sheets

    def get_properties(self) -> WorkbookProperties:
        """Get workbook properties.

        Returns:
            WorkbookProperties object
        """
        return self._workbook_properties

    def get_named_ranges(self) -> list[NamedRange]:
        """Get named ranges.

        Returns:
            List of NamedRange objects
        """
        return self._named_ranges

    def save(self, path: Path | str) -> Path:
        """Generate and save the ODS file.

        Exports all sheets, named ranges, and styling to ODS format.

        Args:
            path: Output file path

        Returns:
            Path to saved file

        Raises:
            EmptySheetError: If any sheet is empty or invalid
        """
        # Validate before rendering
        self.build()

        from spreadsheet_dl.renderer import OdsRenderer

        renderer = OdsRenderer(self._get_theme())
        return renderer.render(self._sheets, Path(path), self._named_ranges)

    def export(self, path: Path | str, format: str = "xlsx") -> Path:
        """Export spreadsheet to various formats.

        Supports XLSX, ODS, and other formats based on file extension.

        Args:
            path: Output file path
            format: Export format (default: xlsx, auto-detected from extension)

        Returns:
            Path to exported file

        Raises:
            EmptySheetError: If any sheet is empty or invalid
            ImportError: If required export library is not installed
        """
        # Validate before rendering
        self.build()

        output_path = Path(path)

        # Auto-detect format from extension if not explicitly set
        if output_path.suffix:
            ext = output_path.suffix.lower().lstrip(".")
            if ext in ("xlsx", "ods", "csv"):
                format = ext

        # Export based on format
        if format == "xlsx":
            from spreadsheet_dl.xlsx_renderer import XlsxRenderer

            renderer = XlsxRenderer(self._get_theme())
            return renderer.render(self._sheets, output_path, self._named_ranges)
        elif format == "ods":
            # Use save for ODS
            return self.save(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# ============================================================================
# Convenience Functions
# ============================================================================


def create_spreadsheet(theme: str = "default") -> SpreadsheetBuilder:
    """Create a new spreadsheet builder.

    Args:
        theme: Theme name to use

    Returns:
        SpreadsheetBuilder instance
    """
    return SpreadsheetBuilder(theme=theme)


def formula() -> FormulaBuilder:
    """Create a formula builder.

    Returns:
        FormulaBuilder instance
    """
    return FormulaBuilder()
