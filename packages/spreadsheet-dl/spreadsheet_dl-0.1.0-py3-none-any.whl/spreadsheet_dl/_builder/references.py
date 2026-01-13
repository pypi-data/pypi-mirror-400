"""Cell and range reference classes for formula construction.

Provides classes for constructing ODF-compliant cell and range references
used in spreadsheet formulas. Supports absolute/relative references,
cross-sheet references, and named ranges.

Key Classes:
    CellRef: Single cell reference with absolute/relative support
    RangeRef: Range reference for contiguous cells
    SheetRef: Sheet reference for cross-sheet formulas
    NamedRange: Named range definition

Examples:
    Create cell references::

        >>> ref = CellRef("A1")
        >>> str(ref)
        'A1'
        >>> str(ref.absolute())
        '$A$1'

    Create range references::

        >>> rng = RangeRef("A1", "A10")
        >>> str(rng)
        '[.A1:A10]'

    Cross-sheet references::

        >>> sheet = SheetRef("Data")
        >>> sheet.cell("B5")
        '[Data.B5]'

.. versionadded:: 4.0.0
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CellRef:
    """Cell reference for formulas.

    Represents a single cell reference that can be used in formulas.
    Supports both relative and absolute references. Use absolute references
    when the reference should not change during copy/paste operations.

    Attributes:
        ref: Cell reference string (e.g., "A2", "B10").
        absolute_col: If True, column is absolute ($A). Default False.
        absolute_row: If True, row is absolute ($2). Default False.

    Examples:
        Basic relative reference::

            >>> ref = CellRef("A1")
            >>> str(ref)
            'A1'

        Create absolute reference::

            >>> ref = CellRef("A1").absolute()
            >>> str(ref)
            '$A$1'

        Mixed references::

            >>> ref = CellRef("A1").abs_col()  # Absolute column only
            >>> str(ref)
            '$A1'
            >>> ref = CellRef("A1").abs_row()  # Absolute row only
            >>> str(ref)
            'A$1'

        Using with FormulaBuilder::

            >>> from spreadsheet_dl import formula
            >>> f = formula()
            >>> cell = f.cell("B5")
            >>> str(cell)
            'B5'

    See Also:
        RangeRef: For referencing multiple cells.
        SheetRef: For cross-sheet references.
        FormulaBuilder: For building complete formulas.

    .. versionadded:: 4.0.0
    """

    ref: str
    absolute_col: bool = False
    absolute_row: bool = False

    def __str__(self) -> str:
        """Convert to ODF cell reference string.

        Parses the cell reference and applies absolute markers ($)
        as specified.

        Returns:
            ODF-formatted cell reference string.

        Examples:
            >>> str(CellRef("B5"))
            'B5'
            >>> str(CellRef("B5", absolute_col=True))
            '$B5'
            >>> str(CellRef("B5", absolute_row=True))
            'B$5'
            >>> str(CellRef("B5", absolute_col=True, absolute_row=True))
            '$B$5'
        """
        # Parse column and row from ref
        col = ""
        row = ""
        for i, c in enumerate(self.ref):
            if c.isalpha():
                col += c
            else:
                row = self.ref[i:]
                break

        # Build reference
        result = ""
        if self.absolute_col:
            result += f"${col}"
        else:
            result += col
        if self.absolute_row:
            result += f"${row}"
        else:
            result += row

        return result

    def absolute(self) -> CellRef:
        """Return absolute reference ($A$1).

        Creates a new CellRef with both column and row marked as absolute.
        Absolute references don't change during copy/paste operations.

        Returns:
            New CellRef with absolute_col=True and absolute_row=True.

        Examples:
            >>> ref = CellRef("A1").absolute()
            >>> str(ref)
            '$A$1'
            >>> ref.absolute_col
            True
            >>> ref.absolute_row
            True
        """
        return CellRef(self.ref, absolute_col=True, absolute_row=True)

    def abs_col(self) -> CellRef:
        """Return reference with absolute column ($A1).

        Creates a new CellRef with only the column marked as absolute.
        Useful when the column should stay fixed but row can change.

        Returns:
            New CellRef with absolute_col=True and absolute_row=False.

        Examples:
            >>> ref = CellRef("A1").abs_col()
            >>> str(ref)
            '$A1'
        """
        return CellRef(self.ref, absolute_col=True, absolute_row=False)

    def abs_row(self) -> CellRef:
        """Return reference with absolute row (A$1).

        Creates a new CellRef with only the row marked as absolute.
        Useful when the row should stay fixed but column can change.

        Returns:
            New CellRef with absolute_col=False and absolute_row=True.

        Examples:
            >>> ref = CellRef("A1").abs_row()
            >>> str(ref)
            'A$1'
        """
        return CellRef(self.ref, absolute_col=False, absolute_row=True)


@dataclass
class RangeRef:
    """Range reference for formulas.

    Represents a contiguous range of cells for use in formulas.
    Supports both same-sheet and cross-sheet ranges.

    Attributes:
        start: Start cell reference (e.g., "A2").
        end: End cell reference (e.g., "A100").
        sheet: Optional sheet name for cross-sheet references. None for same sheet.

    Examples:
        Same-sheet range::

            >>> rng = RangeRef("A2", "A100")
            >>> str(rng)
            '[.A2:A100]'

        Cross-sheet range::

            >>> rng = RangeRef("B1", "B50", sheet="Data")
            >>> str(rng)
            '[Data.$B1:B50]'

        Sheet name with spaces::

            >>> rng = RangeRef("A1", "C10", sheet="Monthly Data")
            >>> str(rng)
            "['Monthly Data'.$A1:C10]"

        Using with FormulaBuilder::

            >>> from spreadsheet_dl import formula
            >>> f = formula()
            >>> rng = f.range("A2", "A100")
            >>> f.sum(rng)
            'of:=SUM([.A2:A100])'

    See Also:
        CellRef: For single cell references.
        SheetRef: For creating multiple references to the same sheet.
        NamedRange: For defining reusable named ranges.

    .. versionadded:: 4.0.0
    """

    start: str
    end: str
    sheet: str | None = None

    def __str__(self) -> str:
        """Convert to ODF range reference string.

        Formats the range for use in ODF formulas. Cross-sheet references
        include the sheet name prefix, with proper quoting for names
        containing spaces or special characters.

        Returns:
            ODF-formatted range reference string.

        Examples:
            >>> str(RangeRef("A1", "A10"))
            '[.A1:A10]'
            >>> str(RangeRef("A1", "A10", sheet="Summary"))
            '[Summary.$A1:A10]'
        """
        range_str = f"{self.start}:{self.end}"
        if self.sheet:
            # Quote sheet names that need it
            if " " in self.sheet or "'" in self.sheet:
                sheet_name = f"'{self.sheet}'"
            else:
                sheet_name = self.sheet
            return f"[{sheet_name}.${range_str}]"
        return f"[.{range_str}]"


@dataclass
class NamedRange:
    """Named range for use in formulas.

    Defines a reusable named range that can be referenced by name
    in formulas. Named ranges make formulas more readable and easier
    to maintain.

    Attributes:
        name: Range name (e.g., "SalesData", "TaxRate").
        range: The RangeRef this name refers to.
        scope: Scope of the name - "workbook" for global or sheet name for local.

    Examples:
        Workbook-scoped named range::

            >>> rng = RangeRef("B2", "B100", sheet="Sales")
            >>> named = NamedRange("SalesData", rng)
            >>> named.name
            'SalesData'
            >>> named.scope
            'workbook'

        Sheet-scoped named range::

            >>> rng = RangeRef("A1", "A1")
            >>> named = NamedRange("TaxRate", rng, scope="Settings")
            >>> named.scope
            'Settings'

        Using with SpreadsheetBuilder::

            >>> from spreadsheet_dl import SpreadsheetBuilder
            >>> builder = SpreadsheetBuilder()
            >>> builder.sheet("Data").named_range("Revenue", "B2", "B50")  # doctest: +ELLIPSIS
            <spreadsheet_dl._builder.core.SpreadsheetBuilder object at 0x...>

    Note:
        Named range names must follow ODF naming rules: start with a letter
        or underscore, contain only letters, numbers, underscores, and periods.

    See Also:
        RangeRef: The range reference type.
        SpreadsheetBuilder.named_range: Method to define named ranges.

    .. versionadded:: 4.0.0
    """

    name: str
    range: RangeRef
    scope: str = "workbook"


@dataclass
class SheetRef:
    """Sheet reference for cross-sheet formulas.

    Provides a convenient way to create multiple references to cells
    and ranges within a specific sheet. Useful when building formulas
    that reference data from other sheets.

    Attributes:
        name: Sheet name to reference.

    Examples:
        Create sheet reference::

            >>> sheet = SheetRef("Data")
            >>> sheet.name
            'Data'

        Reference a cell in the sheet::

            >>> sheet = SheetRef("Summary")
            >>> sheet.cell("B5")
            '[Summary.B5]'

        Reference a range in the sheet::

            >>> sheet = SheetRef("Data")
            >>> rng = sheet.range("A2", "A100")
            >>> str(rng)
            '[Data.$A2:A100]'

        Reference entire column::

            >>> sheet = SheetRef("Totals")
            >>> col_range = sheet.col("B")
            >>> str(col_range)
            '[Totals.$$B:$B]'

        Sheet name with spaces::

            >>> sheet = SheetRef("Monthly Report")
            >>> sheet.cell("A1")
            "['Monthly Report'.A1]"

    See Also:
        CellRef: For single cell references.
        RangeRef: For range references.
        FormulaBuilder.sheet: Create sheet references in formulas.

    .. versionadded:: 4.0.0
    """

    name: str

    def col(self, col: str) -> RangeRef:
        """Reference to entire column.

        Creates a range reference covering an entire column in this sheet.

        Args:
            col: Column letter(s) (e.g., "A", "B", "AA").

        Returns:
            RangeRef covering the entire column.

        Examples:
            >>> sheet = SheetRef("Data")
            >>> rng = sheet.col("B")
            >>> rng.sheet
            'Data'
        """
        return RangeRef(f"${col}", f"${col}", self.name)

    def range(self, start: str, end: str) -> RangeRef:
        """Range within this sheet.

        Creates a range reference for a specific area in this sheet.

        Args:
            start: Start cell reference (e.g., "A1").
            end: End cell reference (e.g., "C10").

        Returns:
            RangeRef for the specified range in this sheet.

        Examples:
            >>> sheet = SheetRef("Sales")
            >>> rng = sheet.range("B2", "B100")
            >>> str(rng)
            '[Sales.$B2:B100]'
        """
        return RangeRef(start, end, self.name)

    def cell(self, ref: str) -> str:
        """Cell reference within this sheet.

        Creates a formatted cell reference string for use in formulas.
        Handles quoting of sheet names with spaces or special characters.

        Args:
            ref: Cell reference (e.g., "A1", "B5").

        Returns:
            ODF-formatted cross-sheet cell reference string.

        Examples:
            >>> SheetRef("Data").cell("B5")
            '[Data.B5]'
            >>> SheetRef("My Data").cell("A1")
            "['My Data'.A1]"
        """
        if " " in self.name or "'" in self.name:
            sheet_name = f"'{self.name}'"
        else:
            sheet_name = self.name
        return f"[{sheet_name}.{ref}]"
