"""Builder-specific exceptions with actionable error messages.

All builder exceptions inherit from BuilderError which provides
enhanced error messages with actionable guidance for developers.
Each exception includes context about what went wrong and how to fix it.

Exception Hierarchy:
    SpreadsheetDLError (base)
        BuilderError
            NoSheetSelectedError
            NoRowSelectedError
            InvalidRangeError
            EmptySheetError
            CircularReferenceError

Examples:
    Handling builder errors::

        >>> from spreadsheet_dl import SpreadsheetBuilder
        >>> from spreadsheet_dl._builder.exceptions import NoSheetSelectedError
        >>> builder = SpreadsheetBuilder()
        >>> try:
        ...     builder.column("Name")  # No sheet selected
        ... except NoSheetSelectedError as e:
        ...     print("Need to call .sheet() first")
        Need to call .sheet() first

.. versionadded:: 4.0.0
"""

from __future__ import annotations

from spreadsheet_dl.exceptions import SpreadsheetDLError


class BuilderError(SpreadsheetDLError):
    """Base exception for builder errors with actionable messages.

    All builder-specific exceptions inherit from this class.
    Error messages include guidance on how to fix the issue.

    Examples:
        Catching all builder errors::

            >>> from spreadsheet_dl._builder.exceptions import BuilderError
            >>> try:
            ...     # Some builder operation
            ...     pass
            ... except BuilderError as e:
            ...     print(f"Builder error: {e}")

    See Also:
        SpreadsheetDLError: Base exception for all SpreadsheetDL errors.

    .. versionadded:: 4.0.0
    """

    pass  # Base class - subclasses provide specific error messages


class NoSheetSelectedError(BuilderError):
    """Raised when sheet operation attempted without active sheet.

    This error occurs when you try to add columns, rows, or other
    sheet elements before creating or selecting a sheet.

    Attributes:
        operation: The operation that was attempted.

    Examples:
        This error occurs when calling column without sheet::

            >>> from spreadsheet_dl import SpreadsheetBuilder
            >>> builder = SpreadsheetBuilder()
            >>> builder.column("Name")  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            NoSheetSelectedError: Cannot add column: no sheet is currently selected.
            Fix: Call .sheet('SheetName') first to create or select a sheet.

        Correct usage::

            >>> builder = SpreadsheetBuilder()
            >>> builder.sheet("Data").column("Name")  # Works!
            <spreadsheet_dl._builder.core.SpreadsheetBuilder ...>

    See Also:
        SpreadsheetBuilder.sheet: Method to create/select a sheet.

    .. versionadded:: 4.0.0
    """

    def __init__(self, operation: str) -> None:
        """Initialize with operation context.

        Args:
            operation: The operation that was attempted (e.g., "add column").
        """
        super().__init__(
            f"Cannot {operation}: no sheet is currently selected.\n"
            f"Fix: Call .sheet('SheetName') first to create or select a sheet."
        )


class NoRowSelectedError(BuilderError):
    """Raised when row operation attempted without active row.

    This error occurs when you try to add cells to a row before
    creating a row with .row(), .header_row(), or .data_rows().

    Attributes:
        operation: The operation that was attempted.

    Examples:
        This error occurs when calling cell without row::

            >>> from spreadsheet_dl import SpreadsheetBuilder
            >>> builder = SpreadsheetBuilder()
            >>> builder.sheet("Data").cell("value")  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            NoRowSelectedError: Cannot add cell: no row is currently active.
            Fix: Call .row() first to create a new row, or use .header_row() or .data_rows().

        Correct usage::

            >>> builder = SpreadsheetBuilder()
            >>> builder.sheet("Data").row().cell("value")  # Works!
            <spreadsheet_dl._builder.core.SpreadsheetBuilder ...>

    See Also:
        SpreadsheetBuilder.row: Method to start a new row.
        SpreadsheetBuilder.header_row: Method to add header row.
        SpreadsheetBuilder.data_rows: Method to add multiple data rows.

    .. versionadded:: 4.0.0
    """

    def __init__(self, operation: str) -> None:
        """Initialize with operation context.

        Args:
            operation: The operation that was attempted (e.g., "add cell").
        """
        super().__init__(
            f"Cannot {operation}: no row is currently active.\n"
            f"Fix: Call .row() first to create a new row, or use .header_row() or .data_rows()."
        )


class InvalidRangeError(BuilderError):
    """Raised when an invalid range is provided.

    This error occurs when a range reference doesn't follow the
    expected format (e.g., "A1:B10" or "Sheet1.A1:B10").

    Attributes:
        range_ref: The invalid range reference string.
        reason: Explanation of why the range is invalid.

    Examples:
        Invalid range format::

            >>> from spreadsheet_dl._builder.exceptions import InvalidRangeError
            >>> raise InvalidRangeError("XYZ", "not a valid cell reference")  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            InvalidRangeError: Error [FT-GEN-002]: Invalid range 'XYZ': not a valid cell reference
            Fix: Use a valid range format like 'A1:B10' or 'Sheet1.A1:B10'.

            Documentation: https://github.com/lair-click-bats/spreadsheet-dl/blob/main/docs/error-codes.md#ft-gen-002

    See Also:
        RangeRef: Valid range reference class.

    .. versionadded:: 4.0.0
    """

    def __init__(self, range_ref: str, reason: str) -> None:
        """Initialize with range and reason.

        Args:
            range_ref: The invalid range reference string.
            reason: Explanation of why it's invalid.
        """
        super().__init__(
            f"Invalid range '{range_ref}': {reason}\n"
            f"Fix: Use a valid range format like 'A1:B10' or 'Sheet1.A1:B10'."
        )


class EmptySheetError(BuilderError):
    """Raised when attempting to build with empty/invalid sheet.

    This error occurs during build() or save() if a sheet has no
    columns or rows defined.

    Attributes:
        sheet_name: Name of the problematic sheet.
        reason: Explanation of what's wrong with the sheet.

    Examples:
        Empty sheet during build::

            >>> from spreadsheet_dl import SpreadsheetBuilder
            >>> builder = SpreadsheetBuilder()
            >>> builder.sheet("Empty")
            <spreadsheet_dl._builder.core.SpreadsheetBuilder ...>
            >>> builder.build()  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
                ...
            EmptySheetError: Sheet 'Empty' cannot be built: no columns or rows defined
            Fix: Add columns and rows to the sheet, or remove it from the builder.

        Correct usage - add content before building::

            >>> builder = SpreadsheetBuilder()
            >>> builder.sheet("Data").column("Name").header_row()
            <spreadsheet_dl._builder.core.SpreadsheetBuilder ...>
            >>> sheets = builder.build()  # Works!

    See Also:
        SpreadsheetBuilder.build: Method that validates sheets.
        SpreadsheetBuilder.save: Method that builds and saves.

    .. versionadded:: 4.0.0
    """

    def __init__(self, sheet_name: str, reason: str) -> None:
        """Initialize with sheet context.

        Args:
            sheet_name: Name of the problematic sheet.
            reason: What's wrong with the sheet.
        """
        super().__init__(
            f"Sheet '{sheet_name}' cannot be built: {reason}\n"
            f"Fix: Add columns and rows to the sheet, or remove it from the builder."
        )


class CircularReferenceError(BuilderError):
    """Error raised when circular references are detected in formulas.

    Circular references occur when a cell's formula refers back to itself,
    either directly or through a chain of other cells. This creates an
    infinite loop that cannot be calculated.

    Attributes:
        cell: The cell that contains the circular reference.
        cycle: List of cells forming the circular dependency chain.

    Examples:
        Direct circular reference (A1 refers to A1)::

            >>> from spreadsheet_dl._builder.exceptions import CircularReferenceError
            >>> raise CircularReferenceError("A1", ["A1", "A1"])  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            CircularReferenceError: Error [FT-GEN-001]: Circular reference detected at A1: A1 -> A1
            Fix: Remove the circular dependency by breaking the reference chain.

            Documentation: https://github.com/lair-click-bats/spreadsheet-dl/blob/main/docs/error-codes.md#ft-gen-001

        Indirect circular reference (A1 -> B1 -> C1 -> A1)::

            >>> raise CircularReferenceError("A1", ["A1", "B1", "C1", "A1"])  # doctest: +SKIP
            Traceback (most recent call last):
                ...
            CircularReferenceError: Error [FT-GEN-001]: Circular reference detected at A1: A1 -> B1 -> C1 -> A1
            Fix: Remove the circular dependency by breaking the reference chain.

            Documentation: https://github.com/lair-click-bats/spreadsheet-dl/blob/main/docs/error-codes.md#ft-gen-001

    See Also:
        FormulaDependencyGraph: Used to detect circular references.
        FormulaBuilder: For building formulas safely.

    .. versionadded:: 4.0.0
    """

    def __init__(self, cell: str, cycle: list[str]) -> None:
        """Initialize with cell and cycle information.

        Args:
            cell: The cell where the circular reference was detected.
            cycle: List of cells forming the circular dependency chain.
        """
        self.cell = cell
        self.cycle = cycle
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with cycle visualization.

        Returns:
            Formatted error message showing the reference chain.
        """
        cycle_str = " -> ".join(self.cycle)
        return (
            f"Circular reference detected at {self.cell}: {cycle_str}\n"
            f"Fix: Remove the circular dependency by breaking the reference chain."
        )


class FormulaError(BuilderError):
    """Raised when a formula contains invalid or unsafe content.

    This includes:
    - Invalid cell references
    - Formula injection attempts
    - Malformed formula syntax
    """

    error_code = "FT-BUILD-0303"
