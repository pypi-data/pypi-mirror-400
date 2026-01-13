"""Tests for report generator."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from spreadsheet_dl import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    ReportConfig,
    ReportGenerator,
    generate_monthly_report,
)

pytestmark = [pytest.mark.integration, pytest.mark.requires_files]


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
    ]

    allocations = [
        BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600")),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
        BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("500")),
    ]

    generator.create_budget_spreadsheet(
        output_path,
        expenses=expenses,
        budget_allocations=allocations,
    )

    return output_path


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_generate_text_report(self, sample_budget_file: Path) -> None:
        """Test generating text report."""
        generator = ReportGenerator(sample_budget_file)
        report = generator.generate_text_report()

        assert "BUDGET REPORT" in report
        assert "Total Budget" in report
        assert "Total Spent" in report
        assert "$" in report

    def test_generate_markdown_report(self, sample_budget_file: Path) -> None:
        """Test generating markdown report."""
        generator = ReportGenerator(sample_budget_file)
        report = generator.generate_markdown_report()

        assert "# Budget Report" in report
        assert "## Summary" in report
        assert "|" in report  # Tables

    def test_generate_visualization_data(self, sample_budget_file: Path) -> None:
        """Test generating visualization data."""
        generator = ReportGenerator(sample_budget_file)
        data = generator.generate_visualization_data()

        assert "pie_chart" in data
        assert "bar_chart" in data
        assert "gauge" in data
        assert "summary" in data

        assert "labels" in data["pie_chart"]
        assert "values" in data["pie_chart"]

    def test_save_report_text(self, sample_budget_file: Path, tmp_path: Path) -> None:
        """Test saving text report."""
        generator = ReportGenerator(sample_budget_file)
        output_path = tmp_path / "report.txt"

        result = generator.save_report(output_path, format="text")

        assert result == output_path
        assert output_path.exists()
        content = output_path.read_text()
        assert "BUDGET REPORT" in content

    def test_save_report_markdown(
        self, sample_budget_file: Path, tmp_path: Path
    ) -> None:
        """Test saving markdown report."""
        generator = ReportGenerator(sample_budget_file)
        output_path = tmp_path / "report.md"

        result = generator.save_report(output_path, format="markdown")

        assert result == output_path
        assert output_path.exists()
        content = output_path.read_text()
        assert "# Budget Report" in content

    def test_save_report_json(self, sample_budget_file: Path, tmp_path: Path) -> None:
        """Test saving JSON report."""
        generator = ReportGenerator(sample_budget_file)
        output_path = tmp_path / "report.json"

        result = generator.save_report(output_path, format="json")

        assert result == output_path
        assert output_path.exists()

        import json

        data = json.loads(output_path.read_text())
        assert "pie_chart" in data

    def test_custom_config(self, sample_budget_file: Path) -> None:
        """Test report with custom config."""
        config = ReportConfig(
            include_category_breakdown=False,
            include_trends=False,
            include_alerts=True,
            include_recommendations=False,
        )
        generator = ReportGenerator(sample_budget_file, config=config)
        report = generator.generate_text_report()

        assert "OVERALL SUMMARY" in report
        # Category breakdown should be excluded
        assert "CATEGORY BREAKDOWN" not in report


class TestReportRecommendations:
    """Tests for report recommendations."""

    def test_savings_recommendation(self, sample_budget_file: Path) -> None:
        """Test savings recommendation appears when under target."""
        generator = ReportGenerator(sample_budget_file)
        report = generator.generate_text_report()

        # Savings has 500 budget but 0 actual in sample
        assert "Savings goal" in report or "RECOMMENDATIONS" in report

    def test_over_budget_recommendation(self, tmp_path: Path) -> None:
        """Test over-budget recommendations."""
        output_path = tmp_path / "over_budget.ods"
        ods_gen = OdsGenerator()

        expenses = [
            ExpenseEntry(
                date=date(2025, 1, 1),
                category=ExpenseCategory.DINING_OUT,
                description="Restaurants",
                amount=Decimal("500.00"),
            ),
        ]

        allocations = [
            BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
        ]

        ods_gen.create_budget_spreadsheet(
            output_path,
            expenses=expenses,
            budget_allocations=allocations,
        )

        generator = ReportGenerator(output_path)
        report = generator.generate_text_report()

        assert "Reduce" in report or "over budget" in report.lower()


class TestGenerateMonthlyReportFunction:
    """Tests for generate_monthly_report function."""

    def test_returns_string(self, sample_budget_file: Path) -> None:
        """Test returning string when no output dir."""
        result = generate_monthly_report(sample_budget_file)

        assert isinstance(result, str)
        assert "# Budget Report" in result

    def test_saves_to_file(self, sample_budget_file: Path, tmp_path: Path) -> None:
        """Test saving to file."""
        result = generate_monthly_report(
            sample_budget_file,
            output_dir=tmp_path,
        )

        assert isinstance(result, Path)
        assert result.exists()

    def test_different_formats(self, sample_budget_file: Path) -> None:
        """Test different output formats."""
        text = generate_monthly_report(sample_budget_file, format="text")
        md = generate_monthly_report(sample_budget_file, format="markdown")
        json_str = generate_monthly_report(sample_budget_file, format="json")

        assert isinstance(text, str) and "BUDGET REPORT" in text
        assert isinstance(md, str) and "# Budget Report" in md
        assert isinstance(json_str, str) and "pie_chart" in json_str
