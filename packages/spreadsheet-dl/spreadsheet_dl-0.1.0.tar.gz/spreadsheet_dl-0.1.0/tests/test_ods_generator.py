"""Tests for ODS spreadsheet generation."""

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


pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_files,
    pytest.mark.rendering,
]


class TestOdsGenerator:
    """Tests for OdsGenerator class."""

    def test_create_budget_spreadsheet_default(self, tmp_path: Path) -> None:
        """Test creating a budget spreadsheet with defaults."""
        output_path = tmp_path / "test_budget.ods"
        generator = OdsGenerator()

        result = generator.create_budget_spreadsheet(output_path)

        assert result == output_path
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_create_budget_spreadsheet_with_month(self, tmp_path: Path) -> None:
        """Test creating a budget spreadsheet for specific month."""
        output_path = tmp_path / "budget_jan.ods"
        generator = OdsGenerator()

        result = generator.create_budget_spreadsheet(output_path, month=1, year=2025)

        assert result == output_path
        assert output_path.exists()

    def test_create_budget_spreadsheet_with_expenses(self, tmp_path: Path) -> None:
        """Test creating spreadsheet with pre-populated expenses."""
        output_path = tmp_path / "budget_expenses.ods"
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
                notes="Highway trip",
            ),
        ]

        result = generator.create_budget_spreadsheet(output_path, expenses=expenses)

        assert result == output_path
        assert output_path.exists()

    def test_create_budget_spreadsheet_with_allocations(self, tmp_path: Path) -> None:
        """Test creating spreadsheet with custom budget allocations."""
        output_path = tmp_path / "budget_custom.ods"
        generator = OdsGenerator()

        allocations = [
            BudgetAllocation(ExpenseCategory.HOUSING, Decimal("2000")),
            BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("800")),
        ]

        result = generator.create_budget_spreadsheet(
            output_path, budget_allocations=allocations
        )

        assert result == output_path
        assert output_path.exists()

    def test_create_expense_template(self, tmp_path: Path) -> None:
        """Test creating an expense template."""
        output_path = tmp_path / "template.ods"
        generator = OdsGenerator()

        result = generator.create_expense_template(output_path)

        assert result == output_path
        assert output_path.exists()

    def test_create_expense_template_limited_categories(self, tmp_path: Path) -> None:
        """Test template with limited categories."""
        output_path = tmp_path / "template_limited.ods"
        generator = OdsGenerator()

        categories = [ExpenseCategory.GROCERIES, ExpenseCategory.UTILITIES]
        result = generator.create_expense_template(output_path, categories=categories)

        assert result == output_path
        assert output_path.exists()


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_monthly_budget(self, tmp_path: Path) -> None:
        """Test create_monthly_budget function."""
        result = create_monthly_budget(tmp_path)

        assert result.exists()
        assert result.parent == tmp_path
        assert result.suffix == ".ods"

    def test_create_monthly_budget_specific_month(self, tmp_path: Path) -> None:
        """Test create_monthly_budget for specific month."""
        result = create_monthly_budget(tmp_path, month=6, year=2025)

        assert result.exists()
        assert "2025_06" in result.name


class TestExpenseCategory:
    """Tests for ExpenseCategory enum."""

    def test_all_categories_have_values(self) -> None:
        """Test all categories have string values."""
        for category in ExpenseCategory:
            assert isinstance(category.value, str)
            assert len(category.value) > 0

    def test_category_count(self) -> None:
        """Test expected number of categories."""
        assert len(ExpenseCategory) >= 10  # At least 10 categories


class TestDataClasses:
    """Tests for data classes."""

    def test_expense_entry_creation(self) -> None:
        """Test creating ExpenseEntry."""
        entry = ExpenseEntry(
            date=date(2025, 1, 1),
            category=ExpenseCategory.GROCERIES,
            description="Test",
            amount=Decimal("100"),
        )

        assert entry.date == date(2025, 1, 1)
        assert entry.category == ExpenseCategory.GROCERIES
        assert entry.amount == Decimal("100")
        assert entry.notes == ""  # Default

    def test_budget_allocation_creation(self) -> None:
        """Test creating BudgetAllocation."""
        alloc = BudgetAllocation(
            category=ExpenseCategory.HOUSING,
            monthly_budget=Decimal("1500"),
            notes="Rent + utilities",
        )

        assert alloc.category == ExpenseCategory.HOUSING
        assert alloc.monthly_budget == Decimal("1500")
        assert alloc.notes == "Rent + utilities"
