"""Data models for spreadsheet specifications.

Provides dataclasses for specifying spreadsheet structure. These models
form the core data structures used by SpreadsheetBuilder to define
cell, row, column, sheet, and workbook specifications.

Key Classes:
    CellSpec: Individual cell specification with value, formula, style
    RowSpec: Row specification with cells and formatting
    ColumnSpec: Column specification with width, type, validation
    SheetSpec: Sheet specification with columns, rows, charts
    WorkbookProperties: Workbook-level metadata and properties

All dataclasses use slots for memory efficiency in large spreadsheets.

Examples:
    Create a cell specification::

        >>> cell = CellSpec(value="Hello", style="header")
        >>> cell.is_empty()
        False

    Create a column specification::

        >>> col = ColumnSpec(name="Amount", width="100pt", type="currency")
        >>> col.name
        'Amount'

    Create a sheet specification::

        >>> sheet = SheetSpec(name="Budget")
        >>> sheet.columns.append(ColumnSpec(name="Item", width="2cm"))
        >>> len(sheet.columns)
        1

.. versionadded:: 4.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CellSpec:
    """Specification for a single cell.

    Uses __slots__ for memory efficiency when creating large spreadsheets.
    Supports values, formulas, styles, and cell merging.

    Attributes:
        value: Cell value (string, number, date, etc.)
        formula: ODF formula string (e.g., "of:=SUM([.A1:A10])")
        style: Style name from theme (e.g., "header", "currency")
        colspan: Number of columns to span (must be >= 1)
        rowspan: Number of rows to span (must be >= 1)
        value_type: ODF value type (string, currency, date, float, percentage)
        validation: Data validation reference name
        conditional_format: Conditional format reference name

    Examples:
        Basic cell with value::

            >>> cell = CellSpec(value=100.50, style="currency")
            >>> cell.value
            100.5

        Cell with formula::

            >>> cell = CellSpec(formula="of:=SUM([.B2:B10])", style="total")
            >>> cell.formula
            'of:=SUM([.B2:B10])'

        Merged cell (spans 2 columns)::

            >>> cell = CellSpec(value="Title", colspan=2, style="header")
            >>> cell.colspan
            2

    Raises:
        ValueError: If colspan or rowspan is less than 1.

    See Also:
        RowSpec: Container for multiple cells.
        ColumnSpec: Column-level formatting.

    .. versionadded:: 4.0.0
    """

    value: Any = None
    formula: str | None = None
    style: str | None = None
    colspan: int = 1
    rowspan: int = 1
    value_type: str | None = None
    validation: str | None = None
    conditional_format: str | None = None

    def __post_init__(self) -> None:
        """Validate cell specification after initialization.

        Raises:
            ValueError: If colspan is less than 1.
            ValueError: If rowspan is less than 1.
        """
        if self.colspan < 1:
            raise ValueError(
                f"colspan must be >= 1, got {self.colspan}. "
                "Fix: Use colspan=1 (default) or higher."
            )
        if self.rowspan < 1:
            raise ValueError(
                f"rowspan must be >= 1, got {self.rowspan}. "
                "Fix: Use rowspan=1 (default) or higher."
            )

    def is_empty(self) -> bool:
        """Check if cell has no content.

        A cell is considered empty if it has no value and no formula.
        Style-only cells are considered empty.

        Returns:
            True if cell has no value and no formula, False otherwise.

        Examples:
            >>> CellSpec().is_empty()
            True
            >>> CellSpec(value=0).is_empty()
            False
            >>> CellSpec(formula="of:=A1+B1").is_empty()
            False
        """
        return self.value is None and self.formula is None


@dataclass(slots=True)
class RowSpec:
    """Specification for a row.

    Uses __slots__ for memory efficiency. Contains cells and optional
    row-level formatting.

    Attributes:
        cells: List of cell specifications in column order.
        style: Default style for cells in this row (can be overridden per-cell).
        height: Row height (e.g., "20pt", "1cm"). None for default.

    Examples:
        Create a row with cells::

            >>> row = RowSpec(style="data_row")
            >>> row.cells.append(CellSpec(value="Item 1"))
            >>> row.cells.append(CellSpec(value=100))
            >>> len(row.cells)
            2

        Create a row with custom height::

            >>> row = RowSpec(height="25pt", style="header")
            >>> row.height
            '25pt'

    See Also:
        CellSpec: Individual cell specification.
        SheetSpec: Container for rows.

    .. versionadded:: 4.0.0
    """

    cells: list[CellSpec] = field(default_factory=list)
    style: str | None = None
    height: str | None = None


@dataclass(slots=True)
class ColumnSpec:
    """Specification for a column.

    Uses __slots__ for memory efficiency. Defines column header,
    width, default type, and optional data validation.

    Attributes:
        name: Column header name (displayed in header row).
        width: Column width (e.g., "2.5cm", "100px", "100pt").
        type: Value type for cells (string, currency, date, percentage, float).
        style: Default style for cells in this column.
        validation: Data validation reference name.
        hidden: Whether column is hidden from view.
        sparkline: Optional sparkline specification for the column.

    Examples:
        Basic column::

            >>> col = ColumnSpec(name="Description", width="3cm")
            >>> col.name
            'Description'

        Currency column with validation::

            >>> col = ColumnSpec(
            ...     name="Amount",
            ...     width="100pt",
            ...     type="currency",
            ...     validation="positive_number"
            ... )
            >>> col.type
            'currency'

        Hidden column::

            >>> col = ColumnSpec(name="ID", hidden=True)
            >>> col.hidden
            True

    Note:
        Width can be specified in various units: cm, mm, in, pt, px.
        The renderer will convert to the appropriate format.

    See Also:
        SheetSpec: Container for columns.
        CellSpec: Individual cell values.

    .. versionadded:: 4.0.0
    """

    name: str
    width: str = "2.5cm"
    type: str = "string"
    style: str | None = None
    validation: str | None = None
    hidden: bool = False
    sparkline: Any = None  # Sparkline from charts module


@dataclass(slots=True)
class SheetSpec:
    """Specification for a sheet.

    Uses __slots__ for memory efficiency. Contains all columns, rows,
    formatting options, and charts for a single sheet.

    Attributes:
        name: Sheet name (displayed on tab).
        columns: Column specifications in order.
        rows: Row specifications in order.
        freeze_rows: Number of rows to freeze at top (0 for none).
        freeze_cols: Number of columns to freeze at left (0 for none).
        print_area: Print area range (e.g., "A1:D50"). None for default.
        protection: Sheet protection settings dictionary.
        conditional_formats: List of conditional format reference names.
        validations: List of data validation reference names.
        charts: List of chart specifications (ChartSpec objects).

    Examples:
        Create a basic sheet::

            >>> sheet = SheetSpec(name="Monthly Budget")
            >>> sheet.columns.append(ColumnSpec(name="Category"))
            >>> sheet.columns.append(ColumnSpec(name="Amount", type="currency"))
            >>> len(sheet.columns)
            2

        Sheet with frozen header::

            >>> sheet = SheetSpec(name="Data", freeze_rows=1)
            >>> sheet.freeze_rows
            1

        Sheet with protection::

            >>> sheet = SheetSpec(name="Locked")
            >>> sheet.protection = {
            ...     "enabled": True,
            ...     "password": "your-password-here",
            ...     "edit_cells": False
            ... }
            >>> sheet.protection["enabled"]
            True

    Note:
        The charts attribute accepts ChartSpec objects from the charts module.
        Import ChartBuilder to create chart specifications.

    See Also:
        ColumnSpec: Column configuration.
        RowSpec: Row data.
        WorkbookProperties: Workbook metadata.

    .. versionadded:: 4.0.0
    """

    name: str
    columns: list[ColumnSpec] = field(default_factory=list)
    rows: list[RowSpec] = field(default_factory=list)
    freeze_rows: int = 0
    freeze_cols: int = 0
    print_area: str | None = None
    protection: dict[str, Any] = field(default_factory=dict)
    conditional_formats: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)
    charts: list[Any] = field(default_factory=list)  # List of ChartSpec


@dataclass
class WorkbookProperties:
    """Workbook-level properties.

    Stores document metadata that appears in file properties and
    can be used for organization and search.

    Attributes:
        title: Document title (appears in file properties).
        author: Document author name.
        subject: Document subject or summary.
        description: Detailed document description.
        keywords: List of keywords for categorization.
        created: Creation date string (ISO 8601 format).
        modified: Last modified date string (ISO 8601 format).
        custom: Dictionary of custom properties (key-value pairs).

    Examples:
        Basic workbook properties::

            >>> props = WorkbookProperties(
            ...     title="Q1 Budget Report",
            ...     author="Finance Team"
            ... )
            >>> props.title
            'Q1 Budget Report'

        With keywords and custom properties::

            >>> props = WorkbookProperties(
            ...     title="Sales Data",
            ...     keywords=["sales", "quarterly", "2024"]
            ... )
            >>> props.keywords
            ['sales', 'quarterly', '2024']

    Note:
        Date strings should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
        The renderer will format dates appropriately for the output format.

    See Also:
        SheetSpec: Sheet-level configuration.

    .. versionadded:: 4.0.0
    """

    title: str = ""
    author: str = ""
    subject: str = ""
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    created: str | None = None
    modified: str | None = None
    custom: dict[str, str] = field(default_factory=dict)
