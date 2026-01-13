"""Tests for recurring expenses functionality."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl import (
    COMMON_RECURRING,
    ExpenseCategory,
    RecurrenceFrequency,
    RecurringExpense,
    RecurringExpenseManager,
    create_common_recurring,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestRecurringExpense:
    """Tests for RecurringExpense dataclass."""

    def test_create_monthly_expense(self) -> None:
        """Test creating a monthly recurring expense."""
        expense = RecurringExpense(
            name="Netflix",
            category=ExpenseCategory.SUBSCRIPTIONS,
            amount=Decimal("15.99"),
            frequency=RecurrenceFrequency.MONTHLY,
            start_date=date(2025, 1, 1),
            day_of_month=15,
        )

        assert expense.name == "Netflix"
        assert expense.frequency == RecurrenceFrequency.MONTHLY
        assert expense.enabled is True

    def test_to_dict(self) -> None:
        """Test serializing to dictionary."""
        expense = RecurringExpense(
            name="Rent",
            category=ExpenseCategory.HOUSING,
            amount=Decimal("1500.00"),
            frequency=RecurrenceFrequency.MONTHLY,
            start_date=date(2025, 1, 1),
            day_of_month=1,
        )

        data = expense.to_dict()
        assert data["name"] == "Rent"
        assert data["amount"] == "1500.00"
        assert data["frequency"] == "monthly"

    def test_from_dict(self) -> None:
        """Test deserializing from dictionary."""
        data = {
            "name": "Electric Bill",
            "category": "Utilities",
            "amount": "150.00",
            "frequency": "monthly",
            "start_date": "2025-01-01",
            "day_of_month": 5,
        }

        expense = RecurringExpense.from_dict(data)
        assert expense.name == "Electric Bill"
        assert expense.category == ExpenseCategory.UTILITIES
        assert expense.amount == Decimal("150.00")


class TestRecurringExpenseManager:
    """Tests for RecurringExpenseManager."""

    def test_add_expense(self) -> None:
        """Test adding a recurring expense."""
        manager = RecurringExpenseManager()
        expense = RecurringExpense(
            name="Test",
            category=ExpenseCategory.SUBSCRIPTIONS,
            amount=Decimal("10.00"),
            frequency=RecurrenceFrequency.MONTHLY,
            start_date=date(2025, 1, 1),
        )

        manager.add(expense)
        assert len(manager.list_all()) == 1

    def test_remove_expense(self) -> None:
        """Test removing a recurring expense."""
        manager = RecurringExpenseManager()
        expense = RecurringExpense(
            name="ToRemove",
            category=ExpenseCategory.SUBSCRIPTIONS,
            amount=Decimal("10.00"),
            frequency=RecurrenceFrequency.MONTHLY,
            start_date=date(2025, 1, 1),
        )

        manager.add(expense)
        assert manager.remove("ToRemove") is True
        assert len(manager.list_all()) == 0

    def test_get_expense(self) -> None:
        """Test getting expense by name."""
        manager = RecurringExpenseManager()
        expense = RecurringExpense(
            name="FindMe",
            category=ExpenseCategory.UTILITIES,
            amount=Decimal("100.00"),
            frequency=RecurrenceFrequency.MONTHLY,
            start_date=date(2025, 1, 1),
        )

        manager.add(expense)
        found = manager.get("FindMe")
        assert found is not None
        assert found.amount == Decimal("100.00")

    def test_generate_for_month_monthly(self) -> None:
        """Test generating monthly expenses for a month."""
        manager = RecurringExpenseManager()
        expense = RecurringExpense(
            name="Rent",
            category=ExpenseCategory.HOUSING,
            amount=Decimal("1500.00"),
            frequency=RecurrenceFrequency.MONTHLY,
            start_date=date(2025, 1, 1),
            day_of_month=1,
        )

        manager.add(expense)
        entries = manager.generate_for_month(1, 2025, update_last_generated=False)

        assert len(entries) == 1
        assert entries[0].amount == Decimal("1500.00")
        assert entries[0].date == date(2025, 1, 1)

    def test_generate_for_month_weekly(self) -> None:
        """Test generating weekly expenses for a month."""
        manager = RecurringExpenseManager()
        expense = RecurringExpense(
            name="Groceries",
            category=ExpenseCategory.GROCERIES,
            amount=Decimal("100.00"),
            frequency=RecurrenceFrequency.WEEKLY,
            start_date=date(2025, 1, 1),
            day_of_week=0,  # Monday
        )

        manager.add(expense)
        entries = manager.generate_for_month(1, 2025, update_last_generated=False)

        # January 2025 has 4-5 Mondays
        assert len(entries) >= 4
        assert all(e.date.weekday() == 0 for e in entries)

    def test_generate_for_month_biweekly(self) -> None:
        """Test generating biweekly expenses."""
        manager = RecurringExpenseManager()
        expense = RecurringExpense(
            name="Paycheck",
            category=ExpenseCategory.MISCELLANEOUS,
            amount=Decimal("2000.00"),
            frequency=RecurrenceFrequency.BIWEEKLY,
            start_date=date(2025, 1, 3),  # First Friday
            day_of_week=4,  # Friday
        )

        manager.add(expense)
        entries = manager.generate_for_month(1, 2025, update_last_generated=False)

        # Should be 3 occurrences in January (Jan 3, 17, 31)
        assert len(entries) == 3
        assert entries[0].date == date(2025, 1, 3)
        assert entries[1].date == date(2025, 1, 17)
        assert entries[2].date == date(2025, 1, 31)

    def test_calculate_monthly_total(self) -> None:
        """Test calculating monthly total."""
        manager = RecurringExpenseManager()

        # Add monthly expense
        manager.add(
            RecurringExpense(
                name="Rent",
                category=ExpenseCategory.HOUSING,
                amount=Decimal("1500.00"),
                frequency=RecurrenceFrequency.MONTHLY,
                start_date=date(2025, 1, 1),
            )
        )

        # Add weekly expense (~4.33 per month)
        manager.add(
            RecurringExpense(
                name="Gas",
                category=ExpenseCategory.TRANSPORTATION,
                amount=Decimal("50.00"),
                frequency=RecurrenceFrequency.WEEKLY,
                start_date=date(2025, 1, 1),
            )
        )

        total = manager.calculate_monthly_total()
        # $1500 + $50 * 4.33 = ~$1716.50
        assert total > Decimal("1700")
        assert total < Decimal("1750")

    def test_save_and_load(self, tmp_path: Path) -> None:
        """Test saving and loading expenses."""
        config_path = tmp_path / "recurring.json"
        manager = RecurringExpenseManager(config_path)

        manager.add(
            RecurringExpense(
                name="Test",
                category=ExpenseCategory.SUBSCRIPTIONS,
                amount=Decimal("9.99"),
                frequency=RecurrenceFrequency.MONTHLY,
                start_date=date(2025, 1, 1),
            )
        )

        manager.save()
        assert config_path.exists()

        # Load in new manager
        manager2 = RecurringExpenseManager(config_path)
        assert len(manager2.list_all()) == 1
        assert manager2.get("Test") is not None

    def test_disabled_expenses(self) -> None:
        """Test that disabled expenses are excluded."""
        manager = RecurringExpenseManager()

        manager.add(
            RecurringExpense(
                name="Active",
                category=ExpenseCategory.SUBSCRIPTIONS,
                amount=Decimal("10.00"),
                frequency=RecurrenceFrequency.MONTHLY,
                start_date=date(2025, 1, 1),
                enabled=True,
            )
        )

        manager.add(
            RecurringExpense(
                name="Disabled",
                category=ExpenseCategory.SUBSCRIPTIONS,
                amount=Decimal("20.00"),
                frequency=RecurrenceFrequency.MONTHLY,
                start_date=date(2025, 1, 1),
                enabled=False,
            )
        )

        enabled = manager.list_enabled()
        assert len(enabled) == 1
        assert enabled[0].name == "Active"


class TestCommonRecurring:
    """Tests for common recurring expense templates."""

    def test_common_templates_exist(self) -> None:
        """Test that common templates are defined."""
        expected = ["rent", "netflix", "electric", "internet", "gym"]
        for template in expected:
            assert template in COMMON_RECURRING

    def test_create_from_template(self) -> None:
        """Test creating expense from template."""
        expense = create_common_recurring("netflix", Decimal("15.99"))

        assert expense.name == "Netflix"
        assert expense.category == ExpenseCategory.SUBSCRIPTIONS
        assert expense.amount == Decimal("15.99")
        assert expense.frequency == RecurrenceFrequency.MONTHLY

    def test_create_with_overrides(self) -> None:
        """Test creating expense with overrides."""
        expense = create_common_recurring(
            "rent",
            Decimal("2000.00"),
            description="Monthly apartment rent",
        )

        assert expense.name == "Rent"
        assert expense.amount == Decimal("2000.00")
        assert expense.description == "Monthly apartment rent"

    def test_invalid_template(self) -> None:
        """Test that invalid template raises error."""
        with pytest.raises(ValueError):
            create_common_recurring("nonexistent", Decimal("100.00"))
