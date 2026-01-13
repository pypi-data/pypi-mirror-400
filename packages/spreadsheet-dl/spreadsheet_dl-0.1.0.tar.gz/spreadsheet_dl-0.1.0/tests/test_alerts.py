"""Tests for budget alerts system."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import (
    Alert,
    AlertConfig,
    AlertMonitor,
    AlertSeverity,
    AlertType,
    BudgetAllocation,
    BudgetAnalyzer,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    check_budget_alerts,
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
            amount=Decimal("550.00"),  # Near budget
        ),
        ExpenseEntry(
            date=date(2025, 1, 12),
            category=ExpenseCategory.DINING_OUT,
            description="Restaurants",
            amount=Decimal("250.00"),  # Over budget
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
        BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
        BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("500")),
    ]

    generator.create_budget_spreadsheet(
        output_path,
        expenses=expenses,
        budget_allocations=allocations,
    )

    return output_path


@pytest.fixture
def over_budget_file(tmp_path: Path) -> Path:
    """Create a budget file that's over budget."""
    output_path = tmp_path / "over_budget.ods"
    generator = OdsGenerator()

    # Expenses that exceed budget
    expenses = [
        ExpenseEntry(
            date=date(2025, 1, 1),
            category=ExpenseCategory.DINING_OUT,
            description="Excessive dining",
            amount=Decimal("500.00"),
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

    return output_path


class TestAlertConfig:
    """Tests for AlertConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = AlertConfig()

        assert config.budget_warning_threshold == 80.0
        assert config.budget_critical_threshold == 95.0
        assert config.large_transaction_threshold == 200.0

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = AlertConfig(
            budget_warning_threshold=70.0,
            large_transaction_threshold=100.0,
            watched_categories=["Dining Out"],
        )

        assert config.budget_warning_threshold == 70.0
        assert "Dining Out" in config.watched_categories


class TestAlertMonitor:
    """Tests for AlertMonitor."""

    def test_check_all(self, sample_budget_file: Path) -> None:
        """Test running all alert checks."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        monitor = AlertMonitor(analyzer)
        alerts = monitor.check_all()

        assert isinstance(alerts, list)

    def test_over_budget_alert(self, over_budget_file: Path) -> None:
        """Test over-budget category alert."""
        analyzer = BudgetAnalyzer(over_budget_file)
        monitor = AlertMonitor(analyzer)
        alerts = monitor.check_all()

        over_budget_alerts = [a for a in alerts if a.type == AlertType.CATEGORY_OVER]
        assert len(over_budget_alerts) > 0
        assert any(a.severity == AlertSeverity.CRITICAL for a in over_budget_alerts)

    def test_large_transaction_alert(self, tmp_path: Path) -> None:
        """Test large transaction alert."""
        output_path = tmp_path / "large_trans.ods"
        generator = OdsGenerator()

        expenses = [
            ExpenseEntry(
                date=date(2025, 1, 1),
                category=ExpenseCategory.MISCELLANEOUS,
                description="Large purchase",
                amount=Decimal("500.00"),
            ),
        ]

        allocations = [
            BudgetAllocation(ExpenseCategory.MISCELLANEOUS, Decimal("1000")),
        ]

        generator.create_budget_spreadsheet(
            output_path,
            expenses=expenses,
            budget_allocations=allocations,
        )

        analyzer = BudgetAnalyzer(output_path)
        config = AlertConfig(large_transaction_threshold=200.0)
        monitor = AlertMonitor(analyzer, config)
        alerts = monitor.check_all()

        large_alerts = [a for a in alerts if a.type == AlertType.LARGE_TRANSACTION]
        assert len(large_alerts) >= 1

    def test_get_critical_alerts(self, over_budget_file: Path) -> None:
        """Test filtering critical alerts."""
        analyzer = BudgetAnalyzer(over_budget_file)
        monitor = AlertMonitor(analyzer)
        monitor.check_all()
        critical = monitor.get_critical_alerts()

        assert all(a.severity == AlertSeverity.CRITICAL for a in critical)

    def test_format_text(self, sample_budget_file: Path) -> None:
        """Test text formatting of alerts."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        monitor = AlertMonitor(analyzer)
        monitor.check_all()
        text = monitor.format_text()

        assert isinstance(text, str)

    def test_to_json(self, sample_budget_file: Path) -> None:
        """Test JSON export of alerts."""
        analyzer = BudgetAnalyzer(sample_budget_file)
        monitor = AlertMonitor(analyzer)
        monitor.check_all()
        json_str = monitor.to_json()

        import json

        data = json.loads(json_str)
        assert isinstance(data, list)


class TestAlert:
    """Tests for Alert dataclass."""

    def test_alert_creation(self) -> None:
        """Test creating an alert."""
        alert = Alert(
            type=AlertType.BUDGET_THRESHOLD,
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="This is a test",
        )

        assert alert.type == AlertType.BUDGET_THRESHOLD
        assert alert.severity == AlertSeverity.WARNING
        assert alert.dismissed is False

    def test_alert_to_dict(self) -> None:
        """Test converting alert to dictionary."""
        alert = Alert(
            type=AlertType.CATEGORY_OVER,
            severity=AlertSeverity.CRITICAL,
            title="Over Budget",
            message="Category exceeded",
            category="Dining Out",
            amount=Decimal("500.00"),
        )

        data = alert.to_dict()
        assert data["type"] == "category_over"
        assert data["severity"] == "critical"
        assert data["category"] == "Dining Out"


class TestCheckBudgetAlerts:
    """Tests for check_budget_alerts convenience function."""

    def test_check_budget_alerts(self, sample_budget_file: Path) -> None:
        """Test convenience function."""
        alerts = check_budget_alerts(sample_budget_file)

        assert isinstance(alerts, list)
        assert all(isinstance(a, Alert) for a in alerts)
