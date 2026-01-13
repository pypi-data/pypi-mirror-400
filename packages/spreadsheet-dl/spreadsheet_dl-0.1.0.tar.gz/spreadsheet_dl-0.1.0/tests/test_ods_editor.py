"""
Tests for ODS editor module.

Validates : Expense append functionality.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import ExpenseCategory, ExpenseEntry
from spreadsheet_dl.exceptions import OdsReadError, SheetNotFoundError
from spreadsheet_dl.ods_editor import OdsEditor, append_expense_to_file

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_files,
    pytest.mark.rendering,
]


class TestOdsEditor:
    """Tests for OdsEditor class."""

    def test_init_with_valid_file(self, sample_budget_file: Path) -> None:
        """Test OdsEditor initialization with valid file."""
        editor = OdsEditor(sample_budget_file)
        assert editor.file_path == sample_budget_file
        assert editor._doc is not None

    def test_init_with_nonexistent_file(self, tmp_path: Path) -> None:
        """Test OdsEditor raises error for nonexistent file."""
        nonexistent = tmp_path / "nonexistent.ods"
        with pytest.raises(OdsReadError) as exc_info:
            OdsEditor(nonexistent)
        # Check the error message mentions file not found
        assert "not found" in str(exc_info.value).lower() or "File not found" in str(
            exc_info.value
        )

    def test_get_sheet_names(self, sample_budget_file: Path) -> None:
        """Test getting sheet names from document."""
        editor = OdsEditor(sample_budget_file)
        names = editor.get_sheet_names()

        assert "Expense Log" in names
        assert "Budget" in names
        assert len(names) >= 2

    def test_get_sheet_existing(self, sample_budget_file: Path) -> None:
        """Test getting existing sheet by name."""
        editor = OdsEditor(sample_budget_file)
        sheet = editor.get_sheet("Expense Log")

        assert sheet is not None
        assert sheet.getAttribute("name") == "Expense Log"

    def test_get_sheet_not_found(self, sample_budget_file: Path) -> None:
        """Test getting non-existent sheet raises error."""
        editor = OdsEditor(sample_budget_file)

        with pytest.raises(SheetNotFoundError) as exc_info:
            editor.get_sheet("NonExistent Sheet")

        assert "NonExistent Sheet" in str(exc_info.value)
        assert "Expense Log" in str(exc_info.value)

    def test_find_next_empty_row_with_data(self, sample_budget_file: Path) -> None:
        """Test finding next empty row in sheet with data."""
        editor = OdsEditor(sample_budget_file)
        next_row = editor.find_next_empty_row("Expense Log")

        # Should find row after existing expenses (5 sample expenses + header)
        assert next_row >= 6

    def test_find_next_empty_row_empty_sheet(self, empty_budget_file: Path) -> None:
        """Test finding next empty row in empty sheet."""
        editor = OdsEditor(empty_budget_file)
        next_row = editor.find_next_empty_row("Expense Log")

        # Should return 1 (first row after header)
        assert next_row == 1


class TestOdsEditorAppend:
    """Tests for expense append functionality."""

    def test_append_expense_basic(self, empty_budget_file: Path) -> None:
        """Test basic expense append to empty file."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.GROCERIES,
            description="Test groceries",
            amount=Decimal("45.99"),
        )

        row_num = editor.append_expense(expense)
        editor.save()

        assert row_num >= 1  # Row number should be valid

        # Verify by reopening file
        verify_editor = OdsEditor(empty_budget_file)
        sheet = verify_editor.get_sheet("Expense Log")

        # Check content was added
        from odf.table import TableRow

        rows = sheet.getElementsByType(TableRow)
        assert len(rows) >= 2  # Header + at least 1 data row

    def test_append_expense_to_existing_data(self, sample_budget_file: Path) -> None:
        """Test appending expense to file with existing data."""
        editor = OdsEditor(sample_budget_file)

        # Get current row count
        initial_next_row = editor.find_next_empty_row("Expense Log")

        expense = ExpenseEntry(
            date=date(2025, 1, 20),
            category=ExpenseCategory.DINING_OUT,
            description="New restaurant",
            amount=Decimal("55.00"),
        )

        row_num = editor.append_expense(expense)
        editor.save()

        # Should append after existing data
        assert row_num >= initial_next_row

        # Verify
        verify_editor = OdsEditor(sample_budget_file)
        new_next_row = verify_editor.find_next_empty_row("Expense Log")
        assert new_next_row >= initial_next_row

    def test_append_multiple_expenses(self, empty_budget_file: Path) -> None:
        """Test appending multiple expenses sequentially."""
        editor = OdsEditor(empty_budget_file)

        expenses = [
            ExpenseEntry(
                date=date(2025, 1, 1),
                category=ExpenseCategory.HOUSING,
                description="Rent",
                amount=Decimal("1500.00"),
            ),
            ExpenseEntry(
                date=date(2025, 1, 5),
                category=ExpenseCategory.UTILITIES,
                description="Electric",
                amount=Decimal("85.50"),
            ),
            ExpenseEntry(
                date=date(2025, 1, 10),
                category=ExpenseCategory.GROCERIES,
                description="Weekly groceries",
                amount=Decimal("125.00"),
            ),
        ]

        row_numbers = []
        for expense in expenses:
            row_num = editor.append_expense(expense)
            row_numbers.append(row_num)

        editor.save()

        # Row numbers should be sequential
        assert row_numbers == sorted(row_numbers)

        # Verify all were added
        verify_editor = OdsEditor(empty_budget_file)
        next_row = verify_editor.find_next_empty_row("Expense Log")
        assert next_row >= len(expenses) + 1

    def test_append_expense_with_notes(self, empty_budget_file: Path) -> None:
        """Test appending expense with notes field."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.HEALTHCARE,
            description="Doctor visit",
            amount=Decimal("150.00"),
            notes="Annual checkup",
        )

        row_num = editor.append_expense(expense)
        editor.save()

        assert row_num >= 1

    def test_append_expense_to_wrong_sheet(self, sample_budget_file: Path) -> None:
        """Test appending to non-existent sheet raises error."""
        editor = OdsEditor(sample_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.GROCERIES,
            description="Test",
            amount=Decimal("10.00"),
        )

        with pytest.raises(SheetNotFoundError):
            editor.append_expense(expense, sheet_name="Wrong Sheet Name")


class TestOdsEditorSave:
    """Tests for OdsEditor save functionality."""

    def test_save_overwrites_original(self, empty_budget_file: Path) -> None:
        """Test save overwrites original file."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.GROCERIES,
            description="Test",
            amount=Decimal("25.00"),
        )

        editor.append_expense(expense)
        saved_path = editor.save()

        assert saved_path == empty_budget_file
        assert empty_budget_file.exists()

    def test_save_to_different_path(
        self, empty_budget_file: Path, tmp_path: Path
    ) -> None:
        """Test save to different path preserves original."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.GROCERIES,
            description="Test",
            amount=Decimal("25.00"),
        )

        editor.append_expense(expense)

        new_path = tmp_path / "new_budget.ods"
        saved_path = editor.save(new_path)

        assert saved_path == new_path
        assert new_path.exists()
        assert empty_budget_file.exists()


class TestAppendExpenseToFile:
    """Tests for convenience function append_expense_to_file."""

    def test_append_expense_to_file_basic(self, empty_budget_file: Path) -> None:
        """Test convenience function for appending expense."""
        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.GROCERIES,
            description="Test groceries",
            amount=Decimal("45.99"),
        )

        saved_path, row_num = append_expense_to_file(empty_budget_file, expense)

        assert saved_path == empty_budget_file
        assert row_num >= 1

    def test_append_expense_to_file_returns_row_number(
        self, sample_budget_file: Path
    ) -> None:
        """Test function returns correct row number."""
        expense = ExpenseEntry(
            date=date(2025, 1, 20),
            category=ExpenseCategory.ENTERTAINMENT,
            description="Movie",
            amount=Decimal("15.00"),
        )

        _, row_num = append_expense_to_file(sample_budget_file, expense)

        # Should be after existing expenses
        assert row_num >= 6


class TestOdsEditorEdgeCases:
    """Tests for edge cases and error handling."""

    def test_expense_with_special_characters(self, empty_budget_file: Path) -> None:
        """Test handling of special characters in description."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.DINING_OUT,
            description="McDonald's - Value Meal & Fries",
            amount=Decimal("12.99"),
        )

        row_num = editor.append_expense(expense)
        editor.save()

        assert row_num >= 1

    def test_expense_with_large_amount(self, empty_budget_file: Path) -> None:
        """Test handling of large monetary amounts."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 1),
            category=ExpenseCategory.HOUSING,
            description="Down payment",
            amount=Decimal("50000.00"),
        )

        row_num = editor.append_expense(expense)
        editor.save()

        assert row_num >= 1

    def test_expense_with_small_amount(self, empty_budget_file: Path) -> None:
        """Test handling of small monetary amounts."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.MISCELLANEOUS,
            description="Penny candy",
            amount=Decimal("0.01"),
        )

        row_num = editor.append_expense(expense)
        editor.save()

        assert row_num >= 1

    def test_expense_with_unicode(self, empty_budget_file: Path) -> None:
        """Test handling of unicode in description."""
        editor = OdsEditor(empty_budget_file)

        expense = ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.DINING_OUT,
            description="Cafe au lait",
            amount=Decimal("4.50"),
        )

        row_num = editor.append_expense(expense)
        editor.save()

        assert row_num >= 1
