"""Tests for builder module - Core classes (CellRef, RangeRef, SheetRef, etc.)."""

from __future__ import annotations

import pytest

from spreadsheet_dl.builder import (
    CellRef,
    NamedRange,
    RangeRef,
    SheetRef,
    WorkbookProperties,
)

pytestmark = [pytest.mark.unit, pytest.mark.builder]


class TestCellRef:
    """Tests for CellRef class."""

    def test_basic_ref(self) -> None:
        """Test basic cell reference."""
        ref = CellRef("A1")
        assert str(ref) == "A1"

    def test_absolute_ref(self) -> None:
        """Test absolute cell reference."""
        ref = CellRef("A1").absolute()
        assert str(ref) == "$A$1"

    def test_abs_col(self) -> None:
        """Test absolute column reference."""
        ref = CellRef("A1").abs_col()
        assert str(ref) == "$A1"

    def test_abs_row(self) -> None:
        """Test absolute row reference."""
        ref = CellRef("A1").abs_row()
        assert str(ref) == "A$1"

    def test_ref_with_multiple_letters(self) -> None:
        """Test cell reference with multi-letter column."""
        ref = CellRef("AA100")
        assert str(ref) == "AA100"

    def test_absolute_ref_multi_letter(self) -> None:
        """Test absolute reference with multi-letter column."""
        ref = CellRef("AB25").absolute()
        assert str(ref) == "$AB$25"

    def test_abs_col_multi_letter(self) -> None:
        """Test absolute column with multi-letter column."""
        ref = CellRef("ZZ999").abs_col()
        assert str(ref) == "$ZZ999"

    def test_abs_row_large_number(self) -> None:
        """Test absolute row with large row number."""
        ref = CellRef("B100000").abs_row()
        assert str(ref) == "B$100000"

    def test_cell_ref_equality(self) -> None:
        """Test CellRef equality based on string representation."""
        ref1 = CellRef("A1")
        ref2 = CellRef("A1")
        assert str(ref1) == str(ref2)

    def test_cell_ref_no_row_number(self) -> None:
        """Test CellRef with only letters (edge case, lines 199-207)."""
        # This tests the edge case where ref has only letters
        ref = CellRef("ABC")
        # The loop will consume all letters, leaving row empty
        result = str(ref)
        # Should output just the column letters since row is empty
        assert "ABC" in result


class TestRangeRef:
    """Tests for RangeRef class."""

    def test_basic_range(self) -> None:
        """Test basic range reference."""
        ref = RangeRef("A1", "A10")
        assert str(ref) == "[.A1:A10]"

    def test_range_with_sheet(self) -> None:
        """Test range with sheet reference."""
        ref = RangeRef("A1", "A10", "Expenses")
        assert str(ref) == "[Expenses.$A1:A10]"

    def test_range_with_space_in_sheet(self) -> None:
        """Test range with space in sheet name."""
        ref = RangeRef("A1", "A10", "Expense Log")
        assert str(ref) == "['Expense Log'.$A1:A10]"

    def test_range_with_quote_in_sheet(self) -> None:
        """Test range with quote in sheet name."""
        ref = RangeRef("A1", "B10", "John's Data")
        assert "'" in str(ref)

    def test_range_large_area(self) -> None:
        """Test range covering large area."""
        ref = RangeRef("A1", "ZZ1000")
        assert str(ref) == "[.A1:ZZ1000]"

    def test_range_single_column(self) -> None:
        """Test range for entire column."""
        ref = RangeRef("A:A", "A:A")
        assert "A:A" in str(ref)


class TestSheetRef:
    """Tests for SheetRef class."""

    def test_col_reference(self) -> None:
        """Test column reference from sheet."""
        sheet = SheetRef("Expenses")
        ref = sheet.col("B")
        assert ref.start == "$B"
        assert ref.sheet == "Expenses"

    def test_range_reference(self) -> None:
        """Test range reference from sheet."""
        sheet = SheetRef("Expenses")
        ref = sheet.range("A1", "B10")
        assert ref.start == "A1"
        assert ref.end == "B10"
        assert ref.sheet == "Expenses"

    def test_cell_reference(self) -> None:
        """Test cell reference from sheet."""
        sheet = SheetRef("Expenses")
        ref = sheet.cell("A2")
        assert ref == "[Expenses.A2]"

    def test_cell_reference_with_space(self) -> None:
        """Test cell reference with space in sheet name."""
        sheet = SheetRef("My Sheet")
        ref = sheet.cell("B5")
        assert "'" in ref

    def test_cell_reference_with_quote(self) -> None:
        """Test cell reference with quote in sheet name."""
        sheet = SheetRef("John's Sheet")
        ref = sheet.cell("C10")
        assert "'" in ref


class TestNamedRange:
    """Tests for NamedRange class."""

    def test_basic_named_range(self) -> None:
        """Test basic named range."""
        nr = NamedRange(
            name="MyRange",
            range=RangeRef("A1", "B10", "Data"),
        )
        assert nr.name == "MyRange"
        assert nr.scope == "workbook"

    def test_named_range_sheet_scope(self) -> None:
        """Test named range with sheet scope."""
        nr = NamedRange(
            name="LocalRange",
            range=RangeRef("A1", "A10"),
            scope="Sheet1",
        )
        assert nr.scope == "Sheet1"


class TestWorkbookProperties:
    """Tests for WorkbookProperties class."""

    def test_default_properties(self) -> None:
        """Test default workbook properties."""
        props = WorkbookProperties()
        assert props.title == ""
        assert props.author == ""
        assert props.subject == ""
        assert props.description == ""
        assert props.keywords == []
        assert props.created is None
        assert props.modified is None
        assert props.custom == {}

    def test_custom_properties(self) -> None:
        """Test custom workbook properties."""
        props = WorkbookProperties(
            title="My Budget",
            author="John Doe",
            subject="Finance",
            description="Personal budget tracker",
            keywords=["budget", "finance", "tracking"],
        )
        assert props.title == "My Budget"
        assert props.author == "John Doe"
        assert len(props.keywords) == 3
