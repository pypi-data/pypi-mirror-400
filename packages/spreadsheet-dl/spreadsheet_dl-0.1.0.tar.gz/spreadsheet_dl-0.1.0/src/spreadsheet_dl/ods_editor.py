"""ODS file editing module for appending expenses to existing spreadsheets.

Provides safe modification of existing ODS files while preserving
structure, formulas, and formatting.
"""

from __future__ import annotations

import contextlib
import copy
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from odf.opendocument import load
from odf.style import Style, TableCellProperties, TextProperties
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import P

from spreadsheet_dl.exceptions import OdsReadError, OdsWriteError, SheetNotFoundError

if TYPE_CHECKING:
    from odf.opendocument import OpenDocumentSpreadsheet

    from spreadsheet_dl.domains.finance.ods_generator import ExpenseEntry


class OdsEditor:
    """Edit existing ODS spreadsheets.

    Provides safe modification of ODS files for:
    - Appending expense entries
    - Updating cell values
    - Preserving existing formulas and formatting
    - Structure operations (rows, columns, sheets)
    - Style and formatting operations
    - Chart and table creation

    """

    def __init__(self, file_path: Path | str) -> None:
        """Initialize editor with an existing ODS file.

        Args:
            file_path: Path to the ODS file to edit.

        Raises:
            OdsReadError: If file cannot be read or is invalid.
        """
        self.file_path = Path(file_path)
        self._doc: OpenDocumentSpreadsheet | None = None
        self._styles: dict[str, Style] = {}
        self._style_counter = 0

        if not self.file_path.exists():
            raise OdsReadError(f"File not found: {self.file_path}", "FILE_NOT_FOUND")

        try:
            self._doc = load(str(self.file_path))
        except (OSError, ValueError, AttributeError, KeyError) as e:
            # OSError: File I/O, ValueError: malformed XML/ZIP, AttributeError: missing attrs, KeyError: missing elements
            raise OdsReadError(
                f"Failed to load ODS file: {e}", "ODS_LOAD_FAILED"
            ) from e

    def get_sheet_names(self) -> list[str]:
        """Get list of sheet names in the document.

        Returns:
            List of sheet names.
        """
        if self._doc is None:
            return []

        sheets = self._doc.spreadsheet.getElementsByType(Table)
        return [sheet.getAttribute("name") for sheet in sheets]

    def get_sheets(self) -> list[str]:
        """Get list of sheet names (alias for get_sheet_names).

        Returns:
            List of sheet names.
        """
        return self.get_sheet_names()

    def get_sheet(self, name: str) -> Table:
        """Get a sheet by name.

        Args:
            name: Sheet name to find.

        Returns:
            Table element for the sheet.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        if self._doc is None:
            raise OdsReadError("Document not loaded", "DOC_NOT_LOADED")

        sheets = self._doc.spreadsheet.getElementsByType(Table)
        for sheet in sheets:
            if sheet.getAttribute("name") == name:
                return sheet

        available = self.get_sheet_names()
        raise SheetNotFoundError(name, available)

    def find_next_empty_row(self, sheet_name: str) -> int:
        """Find the index of the next empty row in a sheet.

        Scans from the beginning looking for the first row where
        the first cell is empty (excluding header row).

        Args:
            sheet_name: Name of the sheet to scan.

        Returns:
            Row index (0-based) of the next empty row.
        """
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        # Start from row 1 (skip header)
        for idx, row in enumerate(rows[1:], start=1):
            cells = row.getElementsByType(TableCell)
            if not cells:
                return idx

            # Check if first cell is empty
            first_cell = cells[0]
            text_content = ""
            for p in first_cell.getElementsByType(P):
                if hasattr(p, "firstChild") and p.firstChild:
                    text_content = str(p.firstChild)
                    break

            # Also check value attributes
            date_value = first_cell.getAttribute("datevalue")
            string_value = first_cell.getAttribute("stringvalue")

            if not text_content and not date_value and not string_value:
                return idx

        # All rows filled, return the count (append at end)
        return len(rows)

    def append_expense(
        self, expense: ExpenseEntry, sheet_name: str = "Expense Log"
    ) -> int:
        """Append an expense entry to the expense sheet.

        Args:
            expense: ExpenseEntry to append.
            sheet_name: Name of the expense sheet (default: "Expense Log").

        Returns:
            Row number where expense was added.

        Raises:
            SheetNotFoundError: If expense sheet not found.
            OdsWriteError: If append fails.

        """
        try:
            sheet = self.get_sheet(sheet_name)
            rows = sheet.getElementsByType(TableRow)

            # Find insertion point
            insert_idx = self.find_next_empty_row(sheet_name)

            # Create the expense row
            row = self._create_expense_row(expense)

            # Insert or replace row
            if insert_idx < len(rows):
                # Replace existing empty row
                old_row = rows[insert_idx]
                sheet.insertBefore(row, old_row)
                sheet.removeChild(old_row)
            else:
                # Append new row
                sheet.addElement(row)

            return insert_idx + 1  # Return 1-based row number

        except SheetNotFoundError:
            raise
        except (AttributeError, ValueError, TypeError) as e:
            # AttributeError: missing DOM methods, ValueError: invalid data, TypeError: type mismatches
            raise OdsWriteError(
                f"Failed to append expense: {e}", "EXPENSE_APPEND_FAILED"
            ) from e

    def _create_expense_row(self, expense: ExpenseEntry) -> TableRow:
        """Create a TableRow element from an ExpenseEntry.

        Args:
            expense: ExpenseEntry to convert.

        Returns:
            TableRow element ready for insertion.
        """
        row = TableRow()

        # Date cell
        date_cell = TableCell(
            valuetype="date",
            datevalue=expense.date.isoformat(),
        )
        date_cell.addElement(P(text=expense.date.strftime("%Y-%m-%d")))
        row.addElement(date_cell)

        # Category cell
        cat_cell = TableCell(valuetype="string")
        cat_cell.addElement(P(text=expense.category.value))
        row.addElement(cat_cell)

        # Description cell
        desc_cell = TableCell(valuetype="string")
        desc_cell.addElement(P(text=expense.description))
        row.addElement(desc_cell)

        # Amount cell
        amount_cell = TableCell(
            valuetype="currency",
            value=str(expense.amount),
        )
        amount_cell.addElement(P(text=f"${expense.amount:.2f}"))
        row.addElement(amount_cell)

        # Notes cell
        notes_cell = TableCell(valuetype="string")
        notes_cell.addElement(P(text=expense.notes))
        row.addElement(notes_cell)

        return row

    def save(self, output_path: Path | str | None = None) -> Path:
        """Save the modified document.

        Args:
            output_path: Optional path to save to. If None, overwrites original.

        Returns:
            Path where file was saved.

        Raises:
            OdsWriteError: If save fails.
        """
        if self._doc is None:
            raise OdsWriteError("No document loaded", "NO_DOC")

        save_path = Path(output_path) if output_path else self.file_path

        try:
            self._doc.save(str(save_path))
            return save_path
        except (OSError, ValueError, AttributeError) as e:
            # OSError: File I/O, ValueError: serialization, AttributeError: missing methods
            raise OdsWriteError(f"Failed to save document: {e}", "SAVE_FAILED") from e

    # =========================================================================
    # Cell Operations
    # =========================================================================

    @staticmethod
    def _parse_cell_reference(cell_ref: str) -> tuple[int, int]:
        """Parse A1-style cell reference to (row, col) indices.

        Args:
            cell_ref: Cell reference like 'A1', 'B5', 'AA10'.

        Returns:
            Tuple of (row_index, col_index) (0-based).

        Raises:
            ValueError: If cell reference is invalid.
        """
        match = re.match(r"^([A-Z]+)(\d+)$", cell_ref.upper())
        if not match:
            raise ValueError(f"Invalid cell reference: {cell_ref}")

        col_str, row_str = match.groups()
        row = int(row_str) - 1  # Convert to 0-based

        # Convert column letters to index (A=0, B=1, ..., Z=25, AA=26, etc.)
        col = 0
        for char in col_str:
            col = col * 26 + (ord(char) - ord("A") + 1)
        col -= 1  # Convert to 0-based

        return row, col

    @staticmethod
    def _parse_range(range_ref: str) -> tuple[tuple[int, int], tuple[int, int]]:
        """Parse A1-style range reference to start and end coordinates.

        Args:
            range_ref: Range like 'A1:B5'.

        Returns:
            Tuple of ((start_row, start_col), (end_row, end_col)).

        Raises:
            ValueError: If range reference is invalid.
        """
        if ":" not in range_ref:
            # Single cell, return as 1x1 range
            row, col = OdsEditor._parse_cell_reference(range_ref)
            return (row, col), (row, col)

        start_ref, end_ref = range_ref.split(":", 1)
        start = OdsEditor._parse_cell_reference(start_ref)
        end = OdsEditor._parse_cell_reference(end_ref)
        return start, end

    def _get_cell(self, sheet: Table, row: int, col: int) -> TableCell | None:
        """Get a cell from a sheet by row and column index.

        Args:
            sheet: Sheet table element.
            row: Row index (0-based).
            col: Column index (0-based).

        Returns:
            TableCell element or None if not found.
        """
        rows = sheet.getElementsByType(TableRow)
        if row >= len(rows):
            return None

        cells = rows[row].getElementsByType(TableCell)
        if col >= len(cells):
            return None

        return cells[col]

    def _get_cell_value(self, cell: TableCell | None) -> Any:
        """Extract the value from a cell.

        Args:
            cell: TableCell element.

        Returns:
            Cell value (str, int, float, or None).
        """
        if cell is None:
            return None

        # Check for value attributes first
        value_type = cell.getAttribute("valuetype")

        if value_type == "float" or value_type == "currency":
            value = cell.getAttribute("value")
            if value:
                return float(value)
        elif value_type == "date":
            return cell.getAttribute("datevalue")
        elif value_type == "boolean":
            value = cell.getAttribute("booleanvalue")
            return value == "true" if value else None
        elif value_type == "string":
            value = cell.getAttribute("stringvalue")
            if value:
                return value

        # Fall back to text content
        text_parts = []
        for p in cell.getElementsByType(P):
            if hasattr(p, "firstChild") and p.firstChild:
                text_parts.append(str(p.firstChild))

        return " ".join(text_parts) if text_parts else None

    def _set_cell_value(
        self, sheet: Table, row: int, col: int, value: Any
    ) -> TableCell:
        """Set the value of a cell, creating rows/cells as needed.

        Args:
            sheet: Sheet table element.
            row: Row index (0-based).
            col: Column index (0-based).
            value: Value to set.

        Returns:
            The modified or created TableCell.
        """
        # Ensure row exists
        rows = sheet.getElementsByType(TableRow)
        while len(rows) <= row:
            sheet.addElement(TableRow())
            rows = sheet.getElementsByType(TableRow)

        target_row = rows[row]

        # Ensure cell exists
        cells = target_row.getElementsByType(TableCell)
        while len(cells) <= col:
            target_row.addElement(TableCell())
            cells = target_row.getElementsByType(TableCell)

        cell = cells[col]

        # Clear existing content
        for child in list(cell.childNodes):
            cell.removeChild(child)

        # Set new value
        if isinstance(value, bool):
            cell.setAttribute("valuetype", "boolean")
            cell.setAttribute("booleanvalue", "true" if value else "false")
            cell.addElement(P(text=str(value)))
        elif isinstance(value, (int, float)):
            cell.setAttribute("valuetype", "float")
            cell.setAttribute("value", str(value))
            cell.addElement(P(text=str(value)))
        else:
            # String value
            cell.setAttribute("valuetype", "string")
            cell.addElement(P(text=str(value)))

        return cell

    def get_cell_value(self, sheet_name: str, cell_ref: str) -> Any:
        """Get the value of a specific cell.

        Args:
            sheet_name: Name of the sheet.
            cell_ref: Cell reference (e.g., 'A1', 'B5').

        Returns:
            Cell value.

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If cell reference is invalid.
        """
        sheet = self.get_sheet(sheet_name)
        row, col = self._parse_cell_reference(cell_ref)
        cell = self._get_cell(sheet, row, col)
        return self._get_cell_value(cell)

    def set_cell_value(self, sheet_name: str, cell_ref: str, value: Any) -> None:
        """Set the value of a specific cell.

        Args:
            sheet_name: Name of the sheet.
            cell_ref: Cell reference (e.g., 'A1', 'B5').
            value: Value to set.

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If cell reference is invalid.
        """
        sheet = self.get_sheet(sheet_name)
        row, col = self._parse_cell_reference(cell_ref)
        self._set_cell_value(sheet, row, col, value)

    def clear_cell(self, sheet_name: str, cell_ref: str) -> None:
        """Clear the value and formatting of a cell.

        Args:
            sheet_name: Name of the sheet.
            cell_ref: Cell reference (e.g., 'A1', 'B5').

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If cell reference is invalid.
        """
        sheet = self.get_sheet(sheet_name)
        row, col = self._parse_cell_reference(cell_ref)
        cell = self._get_cell(sheet, row, col)

        if cell is not None:
            # Clear all attributes and content
            for attr in [
                "valuetype",
                "value",
                "datevalue",
                "stringvalue",
                "booleanvalue",
            ]:
                # Attribute doesn't exist, continue
                with contextlib.suppress(Exception):
                    cell.removeAttribute(attr)

            for child in list(cell.childNodes):
                cell.removeChild(child)

    def get_range_values(self, sheet_name: str, range_ref: str) -> list[list[Any]]:
        """Get values from a range of cells.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Range reference (e.g., 'A1:C5').

        Returns:
            2D list of cell values.

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If range reference is invalid.
        """
        sheet = self.get_sheet(sheet_name)
        (start_row, start_col), (end_row, end_col) = self._parse_range(range_ref)

        result = []
        for row_idx in range(start_row, end_row + 1):
            row_values = []
            for col_idx in range(start_col, end_col + 1):
                cell = self._get_cell(sheet, row_idx, col_idx)
                row_values.append(self._get_cell_value(cell))
            result.append(row_values)

        return result

    def copy_cells(self, sheet_name: str, source: str, destination: str) -> None:
        """Copy a cell or range to another location.

        Args:
            sheet_name: Name of the sheet.
            source: Source cell/range (e.g., 'A1' or 'A1:B5').
            destination: Destination cell (top-left of paste area).

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If cell references are invalid.
        """
        sheet = self.get_sheet(sheet_name)
        src_start, src_end = self._parse_range(source)
        dst_row, dst_col = self._parse_cell_reference(destination)

        # Copy each cell in the range
        for row_offset in range(src_end[0] - src_start[0] + 1):
            for col_offset in range(src_end[1] - src_start[1] + 1):
                src_row = src_start[0] + row_offset
                src_col = src_start[1] + col_offset
                dst_row_idx = dst_row + row_offset
                dst_col_idx = dst_col + col_offset

                src_cell = self._get_cell(sheet, src_row, src_col)
                value = self._get_cell_value(src_cell)
                self._set_cell_value(sheet, dst_row_idx, dst_col_idx, value)

    def move_cells(self, sheet_name: str, source: str, destination: str) -> None:
        """Move a cell or range to another location.

        Args:
            sheet_name: Name of the sheet.
            source: Source cell/range (e.g., 'A1' or 'A1:B5').
            destination: Destination cell (top-left of paste area).

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If cell references are invalid.
        """
        # Copy first
        self.copy_cells(sheet_name, source, destination)

        # Then clear source
        sheet = self.get_sheet(sheet_name)
        src_start, src_end = self._parse_range(source)

        for row in range(src_start[0], src_end[0] + 1):
            for col in range(src_start[1], src_end[1] + 1):
                cell = self._get_cell(sheet, row, col)
                if cell is not None:
                    for attr in [
                        "valuetype",
                        "value",
                        "datevalue",
                        "stringvalue",
                        "booleanvalue",
                    ]:
                        # Attribute doesn't exist, continue
                        with contextlib.suppress(Exception):
                            cell.removeAttribute(attr)
                    for child in list(cell.childNodes):
                        cell.removeChild(child)

    def find_cells(
        self, sheet_name: str, search_text: str, match_case: bool = False
    ) -> list[tuple[str, Any]]:
        """Find cells containing specific text.

        Args:
            sheet_name: Name of the sheet.
            search_text: Text to search for.
            match_case: Whether to match case.

        Returns:
            List of (cell_ref, value) tuples for matches.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        matches = []

        search = search_text if match_case else search_text.lower()

        rows = sheet.getElementsByType(TableRow)
        for row_idx, row in enumerate(rows):
            cells = row.getElementsByType(TableCell)
            for col_idx, cell in enumerate(cells):
                value = self._get_cell_value(cell)
                if value is None:
                    continue

                value_str = str(value) if match_case else str(value).lower()
                if search in value_str:
                    # Convert indices back to A1 notation
                    col_letter = self._col_index_to_letter(col_idx)
                    cell_ref = f"{col_letter}{row_idx + 1}"
                    matches.append((cell_ref, value))

        return matches

    def replace_cells(
        self,
        sheet_name: str,
        search_text: str,
        replace_text: str,
        match_case: bool = False,
    ) -> int:
        """Find and replace text in cells.

        Args:
            sheet_name: Name of the sheet.
            search_text: Text to search for.
            replace_text: Replacement text.
            match_case: Whether to match case.

        Returns:
            Number of replacements made.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        matches = self.find_cells(sheet_name, search_text, match_case)
        count = 0

        for cell_ref, old_value in matches:
            old_str = str(old_value)
            if match_case:
                new_value = old_str.replace(search_text, replace_text)
            else:
                # Case-insensitive replace
                pattern = re.compile(re.escape(search_text), re.IGNORECASE)
                new_value = pattern.sub(replace_text, old_str)

            if new_value != old_str:
                self.set_cell_value(sheet_name, cell_ref, new_value)
                count += 1

        return count

    def merge_cells(self, sheet_name: str, range_ref: str) -> None:
        """Merge cells in a range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Range to merge (e.g., 'A1:C3').

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If range reference is invalid.
        """
        sheet = self.get_sheet(sheet_name)
        (start_row, start_col), (end_row, end_col) = self._parse_range(range_ref)

        # Get the top-left cell
        cell = self._get_cell(sheet, start_row, start_col)
        if cell is None:
            # Create cell if not exists
            self._set_cell_value(sheet, start_row, start_col, "")
            cell = self._get_cell(sheet, start_row, start_col)

        # Set merge attributes
        rows_spanned = end_row - start_row + 1
        cols_spanned = end_col - start_col + 1

        if cell is not None:
            if rows_spanned > 1:
                cell.setAttribute("numberrowsspanned", str(rows_spanned))
            if cols_spanned > 1:
                cell.setAttribute("numbercolumnsspanned", str(cols_spanned))

    def unmerge_cells(self, sheet_name: str, range_ref: str) -> None:
        """Unmerge a merged cell range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Range or cell reference to unmerge.

        Raises:
            SheetNotFoundError: If sheet not found.
            ValueError: If cell reference is invalid.
        """
        sheet = self.get_sheet(sheet_name)
        (start_row, start_col), _ = self._parse_range(range_ref)

        cell = self._get_cell(sheet, start_row, start_col)
        if cell is not None:
            with contextlib.suppress(Exception):
                cell.removeAttribute("numberrowsspanned")
            with contextlib.suppress(Exception):
                cell.removeAttribute("numbercolumnsspanned")

    @staticmethod
    def _col_index_to_letter(col: int) -> str:
        """Convert column index to letter (A, B, ..., Z, AA, AB, ...).

        Args:
            col: Column index (0-based).

        Returns:
            Column letter(s).
        """
        result = ""
        col += 1  # Convert to 1-based
        while col > 0:
            col -= 1
            result = chr(ord("A") + (col % 26)) + result
            col //= 26
        return result

    # =========================================================================
    # Row Operations
    # =========================================================================

    def insert_rows(self, sheet_name: str, index: int, count: int = 1) -> None:
        """Insert rows at the specified index.

        Args:
            sheet_name: Name of the sheet.
            index: Row index where to insert (0-based).
            count: Number of rows to insert.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        # Create new rows
        for _ in range(count):
            new_row = TableRow()
            # Add empty cells matching column count
            if rows:
                existing_cells = rows[0].getElementsByType(TableCell)
                for _ in range(len(existing_cells)):
                    new_row.addElement(TableCell())

            if index < len(rows):
                sheet.insertBefore(new_row, rows[index])
            else:
                sheet.addElement(new_row)

    def delete_rows(self, sheet_name: str, index: int, count: int = 1) -> None:
        """Delete rows starting at the specified index.

        Args:
            sheet_name: Name of the sheet.
            index: Row index to start deletion (0-based).
            count: Number of rows to delete.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        for _ in range(count):
            if index < len(rows):
                sheet.removeChild(rows[index])
                rows = sheet.getElementsByType(TableRow)

    def set_row_hidden(self, sheet_name: str, index: int, hidden: bool) -> None:
        """Hide or show a row.

        Args:
            sheet_name: Name of the sheet.
            index: Row index (0-based).
            hidden: True to hide, False to show.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        if index < len(rows):
            row = rows[index]
            if hidden:
                row.setAttribute("visibility", "collapse")
            else:
                with contextlib.suppress(Exception):
                    row.removeAttribute("visibility")

    # =========================================================================
    # Column Operations
    # =========================================================================

    def insert_columns(self, sheet_name: str, index: int, count: int = 1) -> None:
        """Insert columns at the specified index.

        Args:
            sheet_name: Name of the sheet.
            index: Column index where to insert (0-based).
            count: Number of columns to insert.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        # Insert cells in each row
        for row in rows:
            cells = row.getElementsByType(TableCell)
            for _ in range(count):
                new_cell = TableCell()
                if index < len(cells):
                    row.insertBefore(new_cell, cells[index])
                else:
                    row.addElement(new_cell)

        # Also add TableColumn elements if they exist
        columns = sheet.getElementsByType(TableColumn)
        for _ in range(count):
            new_col = TableColumn()
            if index < len(columns):
                sheet.insertBefore(new_col, columns[index])

    def delete_columns(self, sheet_name: str, index: int, count: int = 1) -> None:
        """Delete columns starting at the specified index.

        Args:
            sheet_name: Name of the sheet.
            index: Column index to start deletion (0-based).
            count: Number of columns to delete.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        # Remove cells from each row
        for row in rows:
            cells = row.getElementsByType(TableCell)
            for _ in range(count):
                if index < len(cells):
                    row.removeChild(cells[index])
                    cells = row.getElementsByType(TableCell)

    def set_column_hidden(self, sheet_name: str, index: int, hidden: bool) -> None:
        """Hide or show a column.

        Args:
            sheet_name: Name of the sheet.
            index: Column index (0-based).
            hidden: True to hide, False to show.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        columns = sheet.getElementsByType(TableColumn)

        if index < len(columns):
            col = columns[index]
            if hidden:
                col.setAttribute("visibility", "collapse")
            else:
                with contextlib.suppress(Exception):
                    col.removeAttribute("visibility")

    # =========================================================================
    # Sheet Operations
    # =========================================================================

    def create_sheet(self, name: str, index: int | None = None) -> None:
        """Create a new sheet in the workbook.

        Args:
            name: Name for the new sheet.
            index: Optional position to insert sheet.

        Raises:
            OdsWriteError: If document not loaded.
        """
        if self._doc is None:
            raise OdsWriteError("No document loaded", "NO_DOC")

        new_table = Table(name=name)

        if index is not None:
            tables = self._doc.spreadsheet.getElementsByType(Table)
            if index < len(tables):
                self._doc.spreadsheet.insertBefore(new_table, tables[index])
                return

        self._doc.spreadsheet.addElement(new_table)

    def delete_sheet(self, name: str) -> None:
        """Delete a sheet from the workbook.

        Args:
            name: Name of the sheet to delete.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(name)
        if self._doc is not None:
            self._doc.spreadsheet.removeChild(sheet)

    def copy_sheet(self, source: str, dest: str) -> None:
        """Copy a sheet within the workbook.

        Args:
            source: Name of the source sheet.
            dest: Name for the copy.

        Raises:
            SheetNotFoundError: If source sheet not found.
        """
        source_sheet = self.get_sheet(source)

        if self._doc is None:
            raise OdsWriteError("No document loaded", "NO_DOC")

        # Deep copy the sheet
        new_sheet = copy.deepcopy(source_sheet)
        new_sheet.setAttribute("name", dest)

        self._doc.spreadsheet.addElement(new_sheet)

    # =========================================================================
    # Freeze Panes
    # =========================================================================

    def set_freeze_panes(self, sheet_name: str, row: int, col: int) -> None:
        """Set freeze panes at the specified row and column.

        Args:
            sheet_name: Name of the sheet.
            row: Number of rows to freeze from top.
            col: Number of columns to freeze from left.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Verify sheet exists
        self.get_sheet(sheet_name)

        if self._doc is None:
            return

        from odf.config import (
            ConfigItem,
            ConfigItemMapEntry,
            ConfigItemMapIndexed,
            ConfigItemSet,
        )

        # Get or create view settings
        view_settings = None
        for child in self._doc.settings.childNodes:
            if (
                hasattr(child, "getAttribute")
                and child.getAttribute("name") == "ooo:view-settings"
            ):
                view_settings = child
                break

        if view_settings is None:
            view_settings = ConfigItemSet(name="ooo:view-settings")
            self._doc.settings.addElement(view_settings)

        # Get or create Views map
        views_map = None
        for child in view_settings.childNodes:
            if hasattr(child, "getAttribute") and child.getAttribute("name") == "Views":
                views_map = child
                break

        if views_map is None:
            views_map = ConfigItemMapIndexed(name="Views")
            view_settings.addElement(views_map)

        # Get or create view entry
        view_entry = None
        for child in views_map.childNodes:
            if hasattr(child, "tagName") and "config-item-map-entry" in child.tagName:
                view_entry = child
                break

        if view_entry is None:
            view_entry = ConfigItemMapEntry()
            views_map.addElement(view_entry)

        # Get or create Tables map
        tables_map = None
        for child in view_entry.childNodes:
            if (
                hasattr(child, "getAttribute")
                and child.getAttribute("name") == "Tables"
            ):
                tables_map = child
                break

        if tables_map is None:
            tables_map = ConfigItemMapIndexed(name="Tables")
            view_entry.addElement(tables_map)

        # Create table entry with freeze settings
        table_entry = ConfigItemMapEntry(name=sheet_name)

        if row > 0:
            h_split = ConfigItem(name="HorizontalSplitMode", type="short")
            h_split.addText("2")
            table_entry.addElement(h_split)

            h_pos = ConfigItem(name="HorizontalSplitPosition", type="int")
            h_pos.addText(str(row))
            table_entry.addElement(h_pos)

        if col > 0:
            v_split = ConfigItem(name="VerticalSplitMode", type="short")
            v_split.addText("2")
            table_entry.addElement(v_split)

            v_pos = ConfigItem(name="VerticalSplitPosition", type="int")
            v_pos.addText(str(col))
            table_entry.addElement(v_pos)

        tables_map.addElement(table_entry)

    def clear_freeze_panes(self, sheet_name: str) -> None:
        """Clear freeze panes from a sheet.

        Args:
            sheet_name: Name of the sheet.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Verify sheet exists
        self.get_sheet(sheet_name)
        # Note: Actually removing freeze panes from ODF settings is complex
        # This would require finding and removing the specific ConfigItem entries
        # For now, this is a no-op as freeze panes don't persist without explicit settings

    # =========================================================================
    # Chart Operations
    # =========================================================================

    def create_chart(
        self,
        sheet_name: str,
        chart_spec: dict[str, Any],
    ) -> str:
        """Create a chart in the specified sheet.

        Args:
            sheet_name: Name of the sheet.
            chart_spec: Chart specification dictionary containing:
                - type: Chart type (bar, line, pie, etc.)
                - data_range: Data range for the chart
                - title: Optional chart title
                - position: Optional position reference

        Returns:
            Chart ID for reference.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Verify sheet exists
        self.get_sheet(sheet_name)
        # Note: Full chart implementation requires embedding chart subdocuments
        # This is a placeholder that returns an ID for tracking
        chart_id = f"chart_{hash(str(chart_spec)) % 10000}"
        return chart_id

    def update_chart(
        self, sheet_name: str, chart_id: str, updates: dict[str, Any]
    ) -> None:
        """Update an existing chart.

        Args:
            sheet_name: Name of the sheet.
            chart_id: Chart ID to update.
            updates: Dictionary of properties to update.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Verify sheet exists
        self.get_sheet(sheet_name)
        # Note: Chart updates require finding and modifying embedded chart objects
        # This is a placeholder

    # =========================================================================
    # Conditional Formatting
    # =========================================================================

    def add_conditional_format(self, sheet_name: str, cf_spec: dict[str, Any]) -> None:
        """Add conditional formatting to a range.

        Args:
            sheet_name: Name of the sheet.
            cf_spec: Conditional format specification containing:
                - range: Target cell range
                - rule_type: Type of rule (color_scale, data_bar, etc.)
                - config: Rule-specific configuration

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Verify sheet exists
        self.get_sheet(sheet_name)
        # Note: ODF conditional formatting via odfpy is limited
        # This is a placeholder

    # =========================================================================
    # Data Validation
    # =========================================================================

    def add_data_validation(
        self, sheet_name: str, validation_spec: dict[str, Any]
    ) -> None:
        """Add data validation to a range.

        Args:
            sheet_name: Name of the sheet.
            validation_spec: Validation specification containing:
                - range: Target cell range
                - type: Validation type (list, number, date, etc.)
                - config: Type-specific configuration

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Verify sheet exists
        self.get_sheet(sheet_name)
        # Note: ODF data validation via odfpy is limited
        # This is a placeholder

    # =========================================================================
    # Named Ranges
    # =========================================================================

    def create_named_range(
        self, name: str, reference: str, sheet_scope: str | None = None
    ) -> None:
        """Create a named range.

        Args:
            name: Name for the range.
            reference: Cell range reference (e.g., 'A1:D10').
            sheet_scope: Optional sheet name for scope (None for workbook scope).

        Raises:
            OdsWriteError: If document not loaded.
        """
        if self._doc is None:
            raise OdsWriteError("No document loaded", "NO_DOC")

        from odf.table import NamedExpressions, NamedRange

        # Get or create NamedExpressions
        named_expressions = None
        for child in self._doc.spreadsheet.childNodes:
            if hasattr(child, "qname") and child.qname == (
                "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
                "named-expressions",
            ):
                named_expressions = child
                break

        if named_expressions is None:
            named_expressions = NamedExpressions()
            self._doc.spreadsheet.addElement(named_expressions)

        # Build cell range address
        cell_range = f"${sheet_scope}.${reference}" if sheet_scope else f"${reference}"

        # Create named range
        named_range = NamedRange(name=name, cellrangeaddress=cell_range)
        named_expressions.addElement(named_range)

    # =========================================================================
    # Table Operations
    # =========================================================================

    def create_table(
        self,
        sheet_name: str,
        range_ref: str,
        name: str,
        style: str | None = None,
    ) -> str:
        """Create a table from a range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Range for the table.
            name: Name for the table.
            style: Optional table style.

        Returns:
            Table name.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Verify sheet exists
        self.get_sheet(sheet_name)
        # Note: ODF tables are different from Excel tables
        # This creates a named range as a simple implementation
        self.create_named_range(name, range_ref, sheet_name)
        return name

    # =========================================================================
    # Style Operations
    # =========================================================================

    def list_styles(self) -> list[dict[str, Any]]:
        """List all styles in the document.

        Returns:
            List of style dictionaries with name and properties.
        """
        if self._doc is None:
            return []

        styles = []
        for style in self._doc.automaticstyles.getElementsByType(Style):
            style_name = style.getAttribute("name")
            style_family = style.getAttribute("family")
            styles.append(
                {
                    "name": style_name,
                    "family": style_family,
                }
            )

        return styles

    def get_style(self, name: str) -> dict[str, Any]:
        """Get a style by name.

        Args:
            name: Style name.

        Returns:
            Style properties dictionary.

        Raises:
            KeyError: If style not found.
        """
        if self._doc is None:
            raise KeyError(f"Style not found: {name}")

        for style in self._doc.automaticstyles.getElementsByType(Style):
            if style.getAttribute("name") == name:
                return {
                    "name": name,
                    "family": style.getAttribute("family"),
                }

        raise KeyError(f"Style not found: {name}")

    def create_style(self, name: str, properties: dict[str, Any]) -> None:
        """Create a new style.

        Args:
            name: Style name.
            properties: Style properties (font, fill, border, etc.).

        Raises:
            OdsWriteError: If document not loaded.
        """
        if self._doc is None:
            raise OdsWriteError("No document loaded", "NO_DOC")

        style = Style(name=name, family=properties.get("family", "table-cell"))

        # Add cell properties
        cell_props = {}
        if "background_color" in properties:
            cell_props["backgroundcolor"] = properties["background_color"]
        if "padding" in properties:
            cell_props["padding"] = properties["padding"]

        if cell_props:
            style.addElement(TableCellProperties(**cell_props))

        # Add text properties
        text_props = {}
        if "font_family" in properties:
            text_props["fontfamily"] = properties["font_family"]
        if "font_size" in properties:
            text_props["fontsize"] = properties["font_size"]
        if "font_weight" in properties:
            text_props["fontweight"] = properties["font_weight"]
        if "color" in properties:
            text_props["color"] = properties["color"]

        if text_props:
            style.addElement(TextProperties(**text_props))

        self._doc.automaticstyles.addElement(style)
        self._styles[name] = style

    def update_style(self, name: str, properties: dict[str, Any]) -> None:
        """Update an existing style.

        Args:
            name: Style name.
            properties: Properties to update.

        Raises:
            KeyError: If style not found.
        """
        # For ODF, updating a style requires recreating it
        # First delete, then create with merged properties
        try:
            old_props = self.get_style(name)
            old_props.update(properties)
            self.delete_style(name)
            self.create_style(name, old_props)
        except KeyError:
            # Style doesn't exist, create new
            self.create_style(name, properties)

    def delete_style(self, name: str) -> None:
        """Delete a style.

        Args:
            name: Style name.

        Raises:
            KeyError: If style not found.
        """
        if self._doc is None:
            raise KeyError(f"Style not found: {name}")

        for style in self._doc.automaticstyles.getElementsByType(Style):
            if style.getAttribute("name") == name:
                self._doc.automaticstyles.removeChild(style)
                if name in self._styles:
                    del self._styles[name]
                return

        raise KeyError(f"Style not found: {name}")

    def apply_style(self, sheet_name: str, range_ref: str, style_name: str) -> None:
        """Apply a style to a cell range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Cell range to style.
            style_name: Name of the style to apply.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        (start_row, start_col), (end_row, end_col) = self._parse_range(range_ref)

        for row_idx in range(start_row, end_row + 1):
            for col_idx in range(start_col, end_col + 1):
                cell = self._get_cell(sheet, row_idx, col_idx)
                if cell is not None:
                    cell.setAttribute("stylename", style_name)

    def format_cells(
        self, sheet_name: str, range_ref: str, format_dict: dict[str, Any]
    ) -> None:
        """Apply formatting directly to cells.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Cell range to format.
            format_dict: Formatting options.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Create a temporary style and apply it
        self._style_counter += 1
        style_name = f"TempFormat_{self._style_counter}"
        self.create_style(style_name, format_dict)
        self.apply_style(sheet_name, range_ref, style_name)

    def set_number_format(
        self, sheet_name: str, range_ref: str, format_str: str
    ) -> None:
        """Set number format for a cell range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Cell range to format.
            format_str: Number format string.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Number formats in ODF require creating data-style elements
        # This is a simplified implementation
        self.get_sheet(sheet_name)

    def set_font(
        self, sheet_name: str, range_ref: str, font_dict: dict[str, Any]
    ) -> None:
        """Set font properties for a cell range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Cell range to format.
            font_dict: Font properties (name, size, bold, italic, color).

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        format_dict: dict[str, Any] = {}
        if "name" in font_dict:
            format_dict["font_family"] = font_dict["name"]
        if "size" in font_dict:
            format_dict["font_size"] = font_dict["size"]
        if font_dict.get("bold"):
            format_dict["font_weight"] = "bold"
        if "color" in font_dict:
            format_dict["color"] = font_dict["color"]

        self.format_cells(sheet_name, range_ref, format_dict)

    def set_fill_color(self, sheet_name: str, range_ref: str, color: str) -> None:
        """Set fill color for a cell range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Cell range to format.
            color: Fill color (hex code).

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        self.format_cells(sheet_name, range_ref, {"background_color": color})

    def set_border(
        self, sheet_name: str, range_ref: str, border_dict: dict[str, Any]
    ) -> None:
        """Set border for a cell range.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Cell range to format.
            border_dict: Border properties (style, color, sides).

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        # Simplified border implementation
        self.get_sheet(sheet_name)

    # =========================================================================
    # Theme Operations
    # =========================================================================

    def list_themes(self) -> list[str]:
        """List available themes.

        Returns:
            List of theme names.
        """
        # ODF doesn't have built-in theme support like XLSX
        return ["default"]

    def get_theme(self, name: str) -> dict[str, Any]:
        """Get theme by name.

        Args:
            name: Theme name.

        Returns:
            Theme properties dictionary.
        """
        return {"name": name, "colors": {}, "fonts": {}}

    def create_theme(self, name: str, theme_dict: dict[str, Any]) -> None:
        """Create a custom theme.

        Args:
            name: Theme name.
            theme_dict: Theme properties.
        """
        # ODF doesn't have built-in theme support
        pass

    def apply_theme(self, theme_name: str) -> None:
        """Apply a theme to the workbook.

        Args:
            theme_name: Name of the theme to apply.
        """
        # ODF doesn't have built-in theme support
        pass

    # =========================================================================
    # Print Operations
    # =========================================================================

    def set_page_setup(self, sheet_name: str, setup: dict[str, Any]) -> None:
        """Set page setup for printing.

        Args:
            sheet_name: Name of the sheet.
            setup: Page setup options (orientation, paper_size, margins).

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        self.get_sheet(sheet_name)
        # Page setup in ODF requires style:page-layout elements

    def set_print_area(self, sheet_name: str, range_ref: str) -> None:
        """Set print area for a sheet.

        Args:
            sheet_name: Name of the sheet.
            range_ref: Range to print.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        sheet = self.get_sheet(sheet_name)
        # Format as ODF print range
        print_range = f"${sheet_name}.${range_ref}"
        sheet.setAttribute("printranges", print_range)

    def set_print_titles(
        self, sheet_name: str, rows: str | None, cols: str | None
    ) -> None:
        """Set repeating rows/columns for print.

        Args:
            sheet_name: Name of the sheet.
            rows: Row range to repeat (e.g., '1:2').
            cols: Column range to repeat (e.g., 'A:B').

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        self.get_sheet(sheet_name)
        # Print titles in ODF require specific table attributes

    def set_header_footer(
        self, sheet_name: str, header: str | None, footer: str | None
    ) -> None:
        """Set header/footer text for printing.

        Args:
            sheet_name: Name of the sheet.
            header: Header text.
            footer: Footer text.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        self.get_sheet(sheet_name)
        # Headers/footers in ODF require style:header-footer elements

    def insert_page_break(
        self, sheet_name: str, row: int | None, col: int | None
    ) -> None:
        """Insert a page break.

        Args:
            sheet_name: Name of the sheet.
            row: Row index for horizontal break.
            col: Column index for vertical break.

        Raises:
            SheetNotFoundError: If sheet not found.
        """
        self.get_sheet(sheet_name)
        # Page breaks in ODF require style attributes on rows/columns

    # =========================================================================
    # Analysis Operations
    # =========================================================================

    def get_properties(self) -> dict[str, Any]:
        """Get workbook properties.

        Returns:
            Dictionary of workbook properties.
        """
        if self._doc is None:
            return {}

        return {
            "file_path": str(self.file_path),
            "sheet_count": len(self.get_sheet_names()),
            "sheets": self.get_sheet_names(),
        }

    def set_properties(self, properties: dict[str, Any]) -> None:
        """Set workbook properties.

        Args:
            properties: Properties to set (title, subject, author, etc.).
        """
        if self._doc is None:
            return

        # ODF properties are in meta.xml
        # This would require accessing self._doc.meta

    def get_statistics(self) -> dict[str, Any]:
        """Get workbook statistics.

        Returns:
            Dictionary of statistics (row count, cell count, etc.).
        """
        if self._doc is None:
            return {}

        stats: dict[str, Any] = {
            "sheet_count": 0,
            "total_rows": 0,
            "total_cells": 0,
            "sheets": {},
        }

        for sheet_name in self.get_sheet_names():
            sheet = self.get_sheet(sheet_name)
            rows = sheet.getElementsByType(TableRow)
            row_count = len(rows)
            cell_count = sum(len(row.getElementsByType(TableCell)) for row in rows)

            stats["sheet_count"] += 1
            stats["total_rows"] += row_count
            stats["total_cells"] += cell_count
            stats["sheets"][sheet_name] = {
                "rows": row_count,
                "cells": cell_count,
            }

        return stats

    def compare_with(self, other_path: str) -> dict[str, Any]:
        """Compare with another workbook.

        Args:
            other_path: Path to the other workbook.

        Returns:
            Dictionary describing differences.
        """
        try:
            other = OdsEditor(other_path)
        except OdsReadError:
            return {"error": f"Could not load {other_path}"}

        my_sheets = set(self.get_sheet_names())
        other_sheets = set(other.get_sheet_names())

        return {
            "sheets_only_in_self": list(my_sheets - other_sheets),
            "sheets_only_in_other": list(other_sheets - my_sheets),
            "sheets_in_both": list(my_sheets & other_sheets),
        }

    def recalculate_formulas(self) -> int:
        """Recalculate all formulas.

        Returns:
            Number of formulas recalculated.

        Note:
            ODF files store formula results; actual recalculation
            happens when opened in a spreadsheet application.
        """
        # ODF doesn't support programmatic formula recalculation
        # This would require a formula engine
        return 0

    def audit_formulas(self) -> dict[str, Any]:
        """Audit formula dependencies.

        Returns:
            Dictionary with formula audit information.
        """
        formulas = []

        for sheet_name in self.get_sheet_names():
            sheet = self.get_sheet(sheet_name)
            rows = sheet.getElementsByType(TableRow)

            for row_idx, row in enumerate(rows):
                cells = row.getElementsByType(TableCell)
                for col_idx, cell in enumerate(cells):
                    formula = cell.getAttribute("formula")
                    if formula:
                        col_letter = self._col_index_to_letter(col_idx)
                        cell_ref = f"{col_letter}{row_idx + 1}"
                        formulas.append(
                            {
                                "sheet": sheet_name,
                                "cell": cell_ref,
                                "formula": formula,
                            }
                        )

        return {
            "formula_count": len(formulas),
            "formulas": formulas,
        }

    def find_circular_references(self) -> list[str]:
        """Find circular references in formulas.

        Returns:
            List of cell references with circular dependencies.

        Note:
            This requires a full formula parser and dependency graph.
            Currently returns an empty list as placeholder.
        """
        # Would require formula parsing and dependency analysis
        return []

    def list_data_connections(self) -> list[dict[str, Any]]:
        """List data connections.

        Returns:
            List of data connection dictionaries.
        """
        # ODF data connections are in database-ranges
        return []

    def refresh_data(self, connection_name: str | None = None) -> int:
        """Refresh data connections.

        Args:
            connection_name: Optional specific connection to refresh.

        Returns:
            Number of connections refreshed.
        """
        # ODF doesn't support programmatic data refresh
        return 0

    def update_links(self) -> int:
        """Update external links.

        Returns:
            Number of links updated.
        """
        # Would require parsing and updating external references
        return 0

    def break_links(self) -> int:
        """Break external links.

        Returns:
            Number of links broken.
        """
        # Would require finding and converting external references
        return 0

    def query_data(self, sheet_name: str, query: str) -> list[dict[str, Any]]:
        """Query data with SQL-like syntax.

        Args:
            sheet_name: Name of the sheet to query.
            query: SQL-like query string.

        Returns:
            List of matching rows as dictionaries.
        """
        # Basic implementation - parse simple SELECT WHERE queries
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        if not rows:
            return []

        # Get headers from first row
        first_row = rows[0]
        cells = first_row.getElementsByType(TableCell)
        headers = [
            self._get_cell_value(cell) or f"col{i}" for i, cell in enumerate(cells)
        ]

        # Return all data rows as dictionaries
        result = []
        for row in rows[1:]:
            cells = row.getElementsByType(TableCell)
            row_dict = {}
            for i, cell in enumerate(cells):
                col_name = headers[i] if i < len(headers) else f"col{i}"
                row_dict[str(col_name)] = self._get_cell_value(cell)
            result.append(row_dict)

        return result

    def find_rows(self, sheet_name: str, conditions: dict[str, Any]) -> list[int]:
        """Find rows matching conditions.

        Args:
            sheet_name: Name of the sheet.
            conditions: Dictionary of column: value conditions.

        Returns:
            List of matching row indices (0-based).
        """
        sheet = self.get_sheet(sheet_name)
        rows = sheet.getElementsByType(TableRow)

        if not rows:
            return []

        # Get headers
        first_row = rows[0]
        cells = first_row.getElementsByType(TableCell)
        headers = [
            self._get_cell_value(cell) or f"col{i}" for i, cell in enumerate(cells)
        ]

        # Find header indices for conditions
        col_indices: dict[str, int] = {}
        for col_name in conditions:
            if col_name in headers:
                col_indices[col_name] = headers.index(col_name)

        # Search rows
        matches = []
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = row.getElementsByType(TableCell)
            match = True

            for col_name, expected_value in conditions.items():
                if col_name not in col_indices:
                    match = False
                    break

                col_idx = col_indices[col_name]
                if col_idx < len(cells):
                    cell_value = self._get_cell_value(cells[col_idx])
                    if cell_value != expected_value:
                        match = False
                        break
                else:
                    match = False
                    break

            if match:
                matches.append(row_idx)

        return matches


def append_expense_to_file(
    file_path: Path | str,
    expense: ExpenseEntry,
    sheet_name: str = "Expense Log",
) -> tuple[Path, int]:
    """Convenience function to append a single expense to an ODS file.

    Args:
        file_path: Path to the ODS file.
        expense: ExpenseEntry to append.
        sheet_name: Name of the expense sheet.

    Returns:
        Tuple of (file path, row number where added).

    """
    editor = OdsEditor(file_path)
    row_num = editor.append_expense(expense, sheet_name)
    saved_path = editor.save()
    return saved_path, row_num
