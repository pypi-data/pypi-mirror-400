"""Integration tests for SpreadsheetDL end-to-end workflows."""

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
    RecurrenceFrequency,
    RecurringExpense,
    RecurringExpenseManager,
    ReportGenerator,
    check_budget_alerts,
    generate_dashboard,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.integration, pytest.mark.requires_files, pytest.mark.finance]


class TestEndToEndWorkflow:
    """Test complete budget workflow from creation to analysis."""

    def test_full_budget_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow: create, analyze, report, alerts."""
        generator = OdsGenerator()

        expenses = [
            ExpenseEntry(
                date=date(2025, 1, 5),
                category=ExpenseCategory.GROCERIES,
                description="Whole Foods",
                amount=Decimal("150.00"),
            ),
            ExpenseEntry(
                date=date(2025, 1, 8),
                category=ExpenseCategory.DINING_OUT,
                description="Restaurant",
                amount=Decimal("85.00"),
            ),
            ExpenseEntry(
                date=date(2025, 1, 10),
                category=ExpenseCategory.TRANSPORTATION,
                description="Gas",
                amount=Decimal("45.00"),
            ),
        ]

        allocations = [
            BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("400")),
            BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
            BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("150")),
            BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1500")),
            BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
        ]

        budget_path = tmp_path / "january_2025.ods"
        generator.create_budget_spreadsheet(
            budget_path,
            month=1,
            year=2025,
            expenses=expenses,
            budget_allocations=allocations,
        )

        assert budget_path.exists()

        # Step 2: Analyze budget
        analyzer = BudgetAnalyzer(budget_path)
        summary = analyzer.get_summary()

        assert summary.total_budget > 0
        assert summary.total_spent == Decimal("280.00")
        assert len(summary.categories) > 0

        # Step 3: Generate report
        report_gen = ReportGenerator(budget_path)
        text_report = report_gen.generate_text_report()
        md_report = report_gen.generate_markdown_report()

        assert "BUDGET REPORT" in text_report
        assert "# Budget Report" in md_report

        # Step 4: Check alerts
        alerts = check_budget_alerts(budget_path)
        # With low spending, should have minimal alerts
        assert isinstance(alerts, list)

        # Step 5: Generate dashboard
        dashboard_data = generate_dashboard(budget_path)

        assert dashboard_data["total_spent"] == 280.0
        assert "charts" in dashboard_data

    def test_high_spending_workflow(self, tmp_path: Path) -> None:
        """Test workflow with high spending that triggers alerts."""
        generator = OdsGenerator()

        # Create expenses that exceed budget
        expenses = [
            ExpenseEntry(
                date=date(2025, 1, 1),
                category=ExpenseCategory.DINING_OUT,
                description="Expensive dinner",
                amount=Decimal("500.00"),
            ),
        ]

        allocations = [
            BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
            BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("400")),
        ]

        budget_path = tmp_path / "over_budget.ods"
        generator.create_budget_spreadsheet(
            budget_path,
            expenses=expenses,
            budget_allocations=allocations,
        )

        # Analyze
        analyzer = BudgetAnalyzer(budget_path)
        summary = analyzer.get_summary()

        # Should have over-budget alert
        assert any("OVER BUDGET" in alert for alert in summary.alerts)

        # Dashboard should show critical status
        dashboard = generate_dashboard(budget_path)
        assert dashboard["budget_status"] in ["warning", "critical"]

        # Alert system should catch this
        alerts = check_budget_alerts(budget_path)
        critical = [a for a in alerts if a.severity.value == "critical"]
        assert len(critical) > 0


class TestRecurringIntegration:
    """Test recurring expenses integration with budget generation."""

    def test_recurring_to_budget(self, tmp_path: Path) -> None:
        """Test generating budget from recurring expenses."""
        # Create recurring expenses
        manager = RecurringExpenseManager()

        manager.add(
            RecurringExpense(
                name="Rent",
                category=ExpenseCategory.HOUSING,
                amount=Decimal("1500.00"),
                frequency=RecurrenceFrequency.MONTHLY,
                start_date=date(2025, 1, 1),
                day_of_month=1,
            )
        )

        manager.add(
            RecurringExpense(
                name="Netflix",
                category=ExpenseCategory.SUBSCRIPTIONS,
                amount=Decimal("15.99"),
                frequency=RecurrenceFrequency.MONTHLY,
                start_date=date(2025, 1, 15),
                day_of_month=15,
            )
        )

        manager.add(
            RecurringExpense(
                name="Groceries",
                category=ExpenseCategory.GROCERIES,
                amount=Decimal("100.00"),
                frequency=RecurrenceFrequency.WEEKLY,
                start_date=date(2025, 1, 1),
                day_of_week=6,  # Sunday
            )
        )

        # Generate entries for January
        entries = manager.generate_for_month(1, 2025, update_last_generated=False)

        # Rent = 1, Netflix = 1, Groceries = 4-5 Sundays
        assert len(entries) >= 6

        # Create budget with recurring entries
        generator = OdsGenerator()
        budget_path = tmp_path / "recurring_budget.ods"

        allocations = [
            BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1500")),
            BudgetAllocation(ExpenseCategory.SUBSCRIPTIONS, Decimal("50")),
            BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("500")),
        ]

        generator.create_budget_spreadsheet(
            budget_path,
            expenses=entries,
            budget_allocations=allocations,
        )

        # Analyze
        analyzer = BudgetAnalyzer(budget_path)
        summary = analyzer.get_summary()

        # Housing should be at 100%
        housing = next(c for c in summary.categories if c.category == "Housing")
        assert housing.percent_used == 100.0


class TestAnalyticsIntegration:
    """Test analytics and dashboard integration."""

    def test_dashboard_with_trends(self, tmp_path: Path) -> None:
        """Test dashboard generates proper trend data."""
        generator = OdsGenerator()

        # Create expenses across multiple days
        expenses = [
            ExpenseEntry(
                date(2025, 1, i),
                ExpenseCategory.GROCERIES,
                "Shopping",
                Decimal("50.00"),
            )
            for i in range(1, 20, 3)
        ]

        budget_path = tmp_path / "trends.ods"
        generator.create_budget_spreadsheet(
            budget_path,
            expenses=expenses,
            budget_allocations=[
                BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("500"))
            ],
        )

        analyzer = BudgetAnalyzer(budget_path)
        dashboard = AnalyticsDashboard(analyzer)
        data = dashboard.generate_dashboard()

        assert data.spending_trend is not None
        assert len(data.spending_trend.periods) > 0

    def test_dashboard_with_alerts(self, tmp_path: Path) -> None:
        """Test dashboard includes alert data."""
        generator = OdsGenerator()

        # Create over-budget scenario
        expenses = [
            ExpenseEntry(
                date(2025, 1, 1),
                ExpenseCategory.DINING_OUT,
                "Restaurant",
                Decimal("300.00"),
            ),
        ]

        budget_path = tmp_path / "alerts.ods"
        generator.create_budget_spreadsheet(
            budget_path,
            expenses=expenses,
            budget_allocations=[
                BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200"))
            ],
        )

        data = generate_dashboard(budget_path)

        assert len(data["alerts"]) > 0
        assert len(data["recommendations"]) > 0


class TestReportIntegration:
    """Test report generation integration."""

    def test_all_report_formats(self, sample_budget_file: Path) -> None:
        """Test generating all report formats."""
        report_gen = ReportGenerator(sample_budget_file)

        # Text report
        text = report_gen.generate_text_report()
        assert "BUDGET REPORT" in text
        assert "Total Budget" in text

        # Markdown report
        md = report_gen.generate_markdown_report()
        assert "# Budget Report" in md
        assert "## Summary" in md

        # Visualization data
        viz = report_gen.generate_visualization_data()
        assert "pie_chart" in viz
        assert "bar_chart" in viz

    def test_report_saves_correctly(
        self,
        sample_budget_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test saving reports to files."""
        report_gen = ReportGenerator(sample_budget_file)

        # Save each format
        text_path = report_gen.save_report(tmp_path / "report.txt", format="text")
        md_path = report_gen.save_report(tmp_path / "report.md", format="markdown")
        json_path = report_gen.save_report(tmp_path / "report.json", format="json")

        assert text_path.exists()
        assert md_path.exists()
        assert json_path.exists()

        # Verify content
        assert "BUDGET REPORT" in text_path.read_text()
        assert "# Budget Report" in md_path.read_text()

        import json

        data = json.loads(json_path.read_text())
        assert "pie_chart" in data
