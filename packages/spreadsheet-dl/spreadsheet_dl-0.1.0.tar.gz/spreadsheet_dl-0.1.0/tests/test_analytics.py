"""Tests for analytics dashboard functionality."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import (
    AnalyticsDashboard,
    BudgetAllocation,
    BudgetAnalyzer,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    generate_dashboard,
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
        BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("500")),
    ]

    generator.create_budget_spreadsheet(
        output_path,
        expenses=expenses,
        budget_allocations=allocations,
    )

    return output_path


class TestAnalyticsDashboard:
    """Tests for AnalyticsDashboard class."""

    def test_generate_dashboard(self, sample_budget_file: Path) -> None:
        """Test generating dashboard data."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        dashboard = AnalyticsDashboard(analyzer)
        data = dashboard.generate_dashboard()

        assert data.total_budget > 0
        assert data.total_spent > 0
        assert data.percent_used > 0
        assert len(data.categories) > 0

    def test_dashboard_status(self, sample_budget_file: Path) -> None:
        """Test budget status determination."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        dashboard = AnalyticsDashboard(analyzer)
        data = dashboard.generate_dashboard()

        assert data.budget_status in ["healthy", "caution", "warning", "critical"]
        assert data.status_message != ""

    def test_dashboard_charts(self, sample_budget_file: Path) -> None:
        """Test chart data generation."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        dashboard = AnalyticsDashboard(analyzer)
        data = dashboard.generate_dashboard()

        assert "category_pie" in data.charts
        assert "budget_vs_actual" in data.charts
        assert "budget_gauge" in data.charts
        assert "daily_spending" in data.charts

    def test_dashboard_top_spending(self, sample_budget_file: Path) -> None:
        """Test top spending categories."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        dashboard = AnalyticsDashboard(analyzer)
        data = dashboard.generate_dashboard()

        assert len(data.top_spending) > 0
        # Should be sorted by amount descending
        if len(data.top_spending) > 1:
            amounts = [t[1] for t in data.top_spending]
            assert amounts == sorted(amounts, reverse=True)

    def test_category_insights(self, sample_budget_file: Path) -> None:
        """Test category insights generation."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        dashboard = AnalyticsDashboard(analyzer)
        data = dashboard.generate_dashboard()

        for cat in data.categories:
            assert cat.category != ""
            assert cat.budget >= 0
            assert cat.current_spending >= 0
            assert cat.percent_used >= 0
            assert cat.trend in ["increasing", "decreasing", "stable"]

    def test_to_dict(self, sample_budget_file: Path) -> None:
        """Test exporting dashboard to dictionary."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        dashboard = AnalyticsDashboard(analyzer)
        data = dashboard.to_dict()

        assert isinstance(data, dict)
        assert "total_budget" in data
        assert "total_spent" in data
        assert "categories" in data
        assert "charts" in data


class TestGenerateDashboard:
    """Tests for generate_dashboard convenience function."""

    def test_generate_dashboard(self, sample_budget_file: Path) -> None:
        """Test convenience function."""
        data = generate_dashboard(sample_budget_file)

        assert isinstance(data, dict)
        assert "total_budget" in data
        assert "budget_status" in data
        assert "recommendations" in data
