"""Tests for backward compatibility.

Ensure that the new declarative DSL does not break existing functionality.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    create_monthly_budget,
)

if TYPE_CHECKING:
    from pathlib import Path

    pass


pytestmark = [pytest.mark.integration]


class TestLegacyOdsGenerator:
    """Tests for legacy OdsGenerator without themes."""

    def test_create_budget_without_theme(self, tmp_path: Path) -> None:
        """Test creating budget spreadsheet without theme (legacy mode)."""
        output = tmp_path / "legacy_budget.ods"
        generator = OdsGenerator()  # No theme

        path = generator.create_budget_spreadsheet(output, month=1, year=2025)

        assert path.exists()
        assert path.stat().st_size > 0

    def test_create_budget_with_expenses(self, tmp_path: Path) -> None:
        """Test creating budget with pre-populated expenses."""
        output = tmp_path / "with_expenses.ods"
        generator = OdsGenerator()

        expenses = [
            ExpenseEntry(
                date=date(2025, 1, 15),
                category=ExpenseCategory.GROCERIES,
                description="Weekly groceries",
                amount=Decimal("125.50"),
            ),
            ExpenseEntry(
                date=date(2025, 1, 16),
                category=ExpenseCategory.TRANSPORTATION,
                description="Gas",
                amount=Decimal("45.00"),
            ),
        ]

        path = generator.create_budget_spreadsheet(output, expenses=expenses)

        assert path.exists()

    def test_create_budget_with_allocations(self, tmp_path: Path) -> None:
        """Test creating budget with custom allocations."""
        output = tmp_path / "with_allocations.ods"
        generator = OdsGenerator()

        allocations = [
            BudgetAllocation(ExpenseCategory.HOUSING, Decimal("2000")),
            BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("800")),
            BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("300")),
        ]

        path = generator.create_budget_spreadsheet(
            output, budget_allocations=allocations
        )

        assert path.exists()

    def test_create_expense_template(self, tmp_path: Path) -> None:
        """Test creating expense template."""
        output = tmp_path / "template.ods"
        generator = OdsGenerator()

        path = generator.create_expense_template(output)

        assert path.exists()


class TestConvenienceFunction:
    """Tests for create_monthly_budget convenience function."""

    def test_create_monthly_budget_no_theme(self, tmp_path: Path) -> None:
        """Test create_monthly_budget without theme."""
        path = create_monthly_budget(tmp_path, month=1, year=2025)

        assert path.exists()
        assert "budget_2025_01" in path.name

    def test_create_monthly_budget_with_theme(self, tmp_path: Path) -> None:
        """Test create_monthly_budget with theme (new feature)."""
        path = create_monthly_budget(tmp_path, month=1, year=2025, theme="default")

        assert path.exists()

    def test_create_monthly_budget_default_date(self, tmp_path: Path) -> None:
        """Test create_monthly_budget uses current date by default."""
        path = create_monthly_budget(tmp_path)

        assert path.exists()
        today = date.today()
        assert f"budget_{today.year}" in path.name


class TestOdsGeneratorWithTheme:
    """Tests for OdsGenerator with theme support (new feature)."""

    def test_theme_string_parameter(self, tmp_path: Path) -> None:
        """Test passing theme as string."""
        output = tmp_path / "theme_string.ods"
        generator = OdsGenerator(theme="default")

        path = generator.create_budget_spreadsheet(output)

        assert path.exists()

    def test_invalid_theme_falls_back(self, tmp_path: Path) -> None:
        """Test invalid theme falls back to legacy styles."""
        output = tmp_path / "invalid_theme.ods"
        # Should not raise, should fall back to legacy
        generator = OdsGenerator(theme="nonexistent_theme")

        path = generator.create_budget_spreadsheet(output)

        assert path.exists()

    def test_none_theme_uses_legacy(self, tmp_path: Path) -> None:
        """Test None theme uses legacy styles."""
        output = tmp_path / "none_theme.ods"
        generator = OdsGenerator(theme=None)

        path = generator.create_budget_spreadsheet(output)

        assert path.exists()


class TestDataClassBackwardCompatibility:
    """Tests for data class backward compatibility."""

    def test_expense_entry_default_notes(self) -> None:
        """Test ExpenseEntry default notes is empty string."""
        entry = ExpenseEntry(
            date=date(2025, 1, 1),
            category=ExpenseCategory.GROCERIES,
            description="Test",
            amount=Decimal("100"),
        )
        assert entry.notes == ""

    def test_expense_entry_with_notes(self) -> None:
        """Test ExpenseEntry with notes."""
        entry = ExpenseEntry(
            date=date(2025, 1, 1),
            category=ExpenseCategory.GROCERIES,
            description="Test",
            amount=Decimal("100"),
            notes="Test note",
        )
        assert entry.notes == "Test note"

    def test_budget_allocation_default_notes(self) -> None:
        """Test BudgetAllocation default notes is empty string."""
        alloc = BudgetAllocation(
            category=ExpenseCategory.GROCERIES,
            monthly_budget=Decimal("500"),
        )
        assert alloc.notes == ""


class TestExpenseCategoryBackwardCompatibility:
    """Tests for ExpenseCategory enum backward compatibility."""

    def test_all_categories_exist(self) -> None:
        """Test all expected categories exist."""
        expected = [
            "HOUSING",
            "UTILITIES",
            "GROCERIES",
            "TRANSPORTATION",
            "HEALTHCARE",
            "INSURANCE",
            "ENTERTAINMENT",
            "DINING_OUT",
            "CLOTHING",
            "PERSONAL",
            "EDUCATION",
            "SAVINGS",
            "DEBT_PAYMENT",
            "GIFTS",
            "SUBSCRIPTIONS",
            "MISCELLANEOUS",
        ]
        for name in expected:
            assert hasattr(ExpenseCategory, name)

    def test_category_values_unchanged(self) -> None:
        """Test category values are unchanged."""
        assert ExpenseCategory.HOUSING.value == "Housing"
        assert ExpenseCategory.GROCERIES.value == "Groceries"
        assert ExpenseCategory.DINING_OUT.value == "Dining Out"


class TestImportBackwardCompatibility:
    """Tests for import statement backward compatibility."""

    def test_import_from_package(self) -> None:
        """Test imports from main package still work."""
        from spreadsheet_dl import (
            BudgetAllocation,
            ExpenseCategory,
            ExpenseEntry,
            OdsGenerator,
            create_monthly_budget,
        )

        assert OdsGenerator is not None
        assert ExpenseCategory is not None
        assert ExpenseEntry is not None
        assert BudgetAllocation is not None
        assert create_monthly_budget is not None

    def test_import_new_components(self) -> None:
        """Test new components can be imported."""
        from spreadsheet_dl import (
            FormulaBuilder,
            OdsRenderer,
            SpreadsheetBuilder,
            create_spreadsheet,
            formula,
            render_sheets,
        )

        assert SpreadsheetBuilder is not None
        assert FormulaBuilder is not None
        assert OdsRenderer is not None
        assert create_spreadsheet is not None
        assert formula is not None
        assert render_sheets is not None

    def test_version_updated(self) -> None:
        """Test version is updated to 0.1.0."""
        from spreadsheet_dl import __version__

        assert __version__ == "0.1.0"
