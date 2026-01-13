"""Tests for budget analyzer."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import (
    BudgetAllocation,
    BudgetAnalyzer,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    analyze_budget,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit, pytest.mark.finance]


@pytest.fixture
def sample_budget_file(tmp_path: Path) -> Path:
    """Create a sample budget file for testing."""
    output_path = tmp_path / "test_budget.ods"
    generator = OdsGenerator()

    expenses = [
        ExpenseEntry(
            date=date(2025, 1, 5),
            category=ExpenseCategory.GROCERIES,
            description="Weekly groceries",
            amount=Decimal("150.00"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 12),
            category=ExpenseCategory.GROCERIES,
            description="Weekly groceries",
            amount=Decimal("125.50"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 8),
            category=ExpenseCategory.UTILITIES,
            description="Electric bill",
            amount=Decimal("95.00"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.DINING_OUT,
            description="Restaurant",
            amount=Decimal("75.00"),
        ),
    ]

    allocations = [
        BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600")),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
        BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
        BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("400")),
    ]

    generator.create_budget_spreadsheet(
        output_path,
        expenses=expenses,
        budget_allocations=allocations,
    )

    return output_path


class TestBudgetAnalyzer:
    """Tests for BudgetAnalyzer class."""

    def test_load_expenses(self, sample_budget_file: Path) -> None:
        """Test loading expenses from ODS file."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        expenses = analyzer.expenses

        assert not expenses.empty
        assert "Date" in expenses.columns
        assert "Category" in expenses.columns
        assert "Amount" in expenses.columns

    def test_load_budget(self, sample_budget_file: Path) -> None:
        """Test loading budget from ODS file."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        budget = analyzer.budget

        assert not budget.empty
        assert "Category" in budget.columns
        assert "Monthly Budget" in budget.columns

    def test_get_summary(self, sample_budget_file: Path) -> None:
        """Test getting budget summary."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        summary = analyzer.get_summary()

        assert summary.total_budget > 0
        assert summary.total_spent > 0
        assert len(summary.categories) > 0

    def test_get_category_breakdown(self, sample_budget_file: Path) -> None:
        """Test category breakdown."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        breakdown = analyzer.get_category_breakdown()

        assert "Groceries" in breakdown
        assert breakdown["Groceries"] == Decimal("275.50")

    def test_get_daily_average(self, sample_budget_file: Path) -> None:
        """Test daily average calculation."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        daily_avg = analyzer.get_daily_average()

        assert daily_avg > 0

    def test_filter_by_category(self, sample_budget_file: Path) -> None:
        """Test filtering by category."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        groceries = analyzer.filter_by_category("Groceries")

        assert len(groceries) == 2
        assert all(groceries["Category"] == "Groceries")

    def test_filter_by_date_range(self, sample_budget_file: Path) -> None:
        """Test filtering by date range."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        filtered = analyzer.filter_by_date_range(
            date(2025, 1, 1),
            date(2025, 1, 10),
        )

        assert len(filtered) >= 1

    def test_to_dict(self, sample_budget_file: Path) -> None:
        """Test exporting analysis to dict."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        data = analyzer.to_dict()

        assert "total_budget" in data
        assert "total_spent" in data
        assert "categories" in data
        assert isinstance(data["total_budget"], float)


class TestAnalyzeBudgetFunction:
    """Tests for analyze_budget convenience function."""

    def test_analyze_budget(self, sample_budget_file: Path) -> None:
        """Test analyze_budget function."""
        result = analyze_budget(sample_budget_file)

        assert isinstance(result, dict)
        assert "total_budget" in result
        assert "total_spent" in result


class TestBudgetSummary:
    """Tests for BudgetSummary attributes."""

    def test_alerts_generated(self, tmp_path: Path) -> None:
        """Test that alerts are generated for over-budget categories."""
        output_path = tmp_path / "over_budget.ods"
        generator = OdsGenerator()

        # Create expense that exceeds budget
        expenses = [
            ExpenseEntry(
                date=date(2025, 1, 1),
                category=ExpenseCategory.DINING_OUT,
                description="Many restaurants",
                amount=Decimal("500.00"),  # Over the 200 budget
            ),
        ]

        allocations = [
            BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
        ]

        generator.create_budget_spreadsheet(
            output_path,
            expenses=expenses,
            budget_allocations=allocations,
        )

        analyzer = BudgetAnalyzer(output_path)
        summary = analyzer.get_summary()

        assert len(summary.alerts) > 0
        assert any("OVER BUDGET" in alert for alert in summary.alerts)

    def test_top_categories(self, sample_budget_file: Path) -> None:
        """Test top categories are sorted correctly."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        summary = analyzer.get_summary()

        # Top category should be Groceries (highest spending)
        assert summary.top_categories[0][0] == "Groceries"
