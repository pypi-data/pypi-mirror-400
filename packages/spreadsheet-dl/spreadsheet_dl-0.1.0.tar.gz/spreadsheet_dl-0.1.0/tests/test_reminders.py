"""
Tests for Bill Reminders and Calendar Integration Module.

: Bill Reminders and IR-CAL-001: Calendar Integration.
"""

from __future__ import annotations

import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from spreadsheet_dl import (
    COMMON_BILLS,
    BillReminder,
    BillReminderManager,
    ExpenseCategory,
    ReminderFrequency,
    ReminderStatus,
    create_bill_from_template,
)

pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestBillReminder:
    """Tests for BillReminder."""

    def test_create_bill(self) -> None:
        """Test creating a bill reminder."""
        bill = BillReminder.create(
            name="Electric Bill",
            amount=150,
            due_date=date.today() + timedelta(days=10),
            payee="Power Company",
        )

        assert bill.name == "Electric Bill"
        assert bill.amount == Decimal("150")
        assert bill.payee == "Power Company"
        assert bill.id is not None

    def test_status_pending(self) -> None:
        """Test pending status for future bills."""
        bill = BillReminder.create(
            name="Test",
            amount=100,
            due_date=date.today() + timedelta(days=30),
            remind_days_before=3,
        )

        assert bill.status == ReminderStatus.PENDING
        assert bill.days_until_due == 30

    def test_status_upcoming(self) -> None:
        """Test upcoming status within reminder window."""
        bill = BillReminder.create(
            name="Test",
            amount=100,
            due_date=date.today() + timedelta(days=2),
            remind_days_before=5,
        )

        assert bill.status == ReminderStatus.UPCOMING
        assert bill.is_due_soon

    def test_status_due_today(self) -> None:
        """Test due today status."""
        bill = BillReminder.create(
            name="Test",
            amount=100,
            due_date=date.today(),
        )

        assert bill.status == ReminderStatus.DUE_TODAY

    def test_status_overdue(self) -> None:
        """Test overdue status."""
        bill = BillReminder.create(
            name="Test",
            amount=100,
            due_date=date.today() - timedelta(days=5),
        )

        assert bill.status == ReminderStatus.OVERDUE
        assert bill.days_until_due == -5

    def test_mark_paid_advances_date(self) -> None:
        """Test marking bill as paid advances due date."""
        bill = BillReminder.create(
            name="Test",
            amount=100,
            due_date=date(2025, 1, 15),
            frequency=ReminderFrequency.MONTHLY,
        )

        bill.mark_paid()

        assert bill.last_paid_date == date.today()
        assert bill.last_paid_amount == Decimal("100")
        # Due date should advance to next month
        assert bill.due_date == date(2025, 2, 15)

    def test_mark_paid_custom_amount(self) -> None:
        """Test marking paid with custom amount."""
        bill = BillReminder.create(
            name="Test",
            amount=100,
            due_date=date.today() + timedelta(days=5),
        )

        bill.mark_paid(amount=120)

        assert bill.last_paid_amount == Decimal("120")

    def test_frequency_date_advance(self) -> None:
        """Test date advancement for different frequencies."""
        test_cases = [
            (ReminderFrequency.WEEKLY, 7),
            (ReminderFrequency.BIWEEKLY, 14),
            (ReminderFrequency.MONTHLY, None),  # Varies
            (ReminderFrequency.QUARTERLY, None),
            (ReminderFrequency.ANNUAL, 365),
        ]

        for frequency, expected_days in test_cases:
            bill = BillReminder.create(
                name="Test",
                amount=100,
                due_date=date(2025, 1, 15),
                frequency=frequency,
            )

            old_date = bill.due_date
            bill.mark_paid()

            if expected_days:
                assert bill.due_date == old_date + timedelta(days=expected_days)
            else:
                # Just verify date moved forward
                assert bill.due_date > old_date

    def test_one_time_no_advance(self) -> None:
        """Test one-time bills don't advance date."""
        bill = BillReminder.create(
            name="Test",
            amount=100,
            due_date=date.today(),
            frequency=ReminderFrequency.ONE_TIME,
        )

        old_date = bill.due_date
        bill.mark_paid()

        assert bill.due_date == old_date

    def test_serialization(self) -> None:
        """Test bill serialization/deserialization."""
        bill = BillReminder.create(
            name="Electric",
            amount=150,
            due_date=date(2025, 2, 1),
            payee="Power Co",
            category=ExpenseCategory.UTILITIES,
            frequency=ReminderFrequency.MONTHLY,
            auto_pay=True,
        )

        data = bill.to_dict()
        restored = BillReminder.from_dict(data)

        assert restored.name == bill.name
        assert restored.amount == bill.amount
        assert restored.due_date == bill.due_date
        assert restored.category == bill.category
        assert restored.auto_pay == bill.auto_pay


class TestBillReminderManager:
    """Tests for BillReminderManager."""

    def test_add_and_list_bills(self) -> None:
        """Test adding and listing bills."""
        manager = BillReminderManager()

        manager.add_bill(BillReminder.create("Bill 1", 100, date.today()))
        manager.add_bill(BillReminder.create("Bill 2", 200, date.today()))

        bills = manager.list_bills()
        assert len(bills) == 2

    def test_remove_bill(self) -> None:
        """Test removing a bill."""
        manager = BillReminderManager()
        bill = BillReminder.create("Test", 100, date.today())
        manager.add_bill(bill)

        assert manager.remove_bill(bill.id)
        assert manager.get_bill(bill.id) is None

    def test_get_bill_by_name(self) -> None:
        """Test finding bill by name."""
        manager = BillReminderManager()
        bill = BillReminder.create("Electric Bill", 150, date.today())
        manager.add_bill(bill)

        found = manager.get_bill_by_name("electric bill")
        assert found is not None
        assert found.id == bill.id

    def test_get_upcoming_bills(self) -> None:
        """Test getting upcoming bills."""
        manager = BillReminderManager()

        # Due in 3 days
        manager.add_bill(
            BillReminder.create("Soon", 100, date.today() + timedelta(days=3))
        )
        # Due in 10 days
        manager.add_bill(
            BillReminder.create("Later", 200, date.today() + timedelta(days=10))
        )
        # Due in 30 days
        manager.add_bill(
            BillReminder.create("Far", 300, date.today() + timedelta(days=30))
        )

        upcoming = manager.get_upcoming_bills(days=7)
        assert len(upcoming) == 1
        assert upcoming[0].name == "Soon"

    def test_get_overdue_bills(self) -> None:
        """Test getting overdue bills."""
        manager = BillReminderManager()

        manager.add_bill(
            BillReminder.create("Overdue", 100, date.today() - timedelta(days=5))
        )
        manager.add_bill(
            BillReminder.create("Not Due", 100, date.today() + timedelta(days=5))
        )

        overdue = manager.get_overdue_bills()
        assert len(overdue) == 1
        assert overdue[0].name == "Overdue"

    def test_mark_paid_through_manager(self) -> None:
        """Test marking paid through manager."""
        manager = BillReminderManager()
        bill = BillReminder.create(
            "Test",
            100,
            date.today(),
            frequency=ReminderFrequency.MONTHLY,
        )
        manager.add_bill(bill)

        result = manager.mark_paid(bill.id, 100)
        assert result is not None
        assert result.last_paid_date == date.today()

    def test_monthly_total(self) -> None:
        """Test monthly total calculation."""
        manager = BillReminderManager()

        manager.add_bill(
            BillReminder.create(
                "Monthly",
                100,
                date.today(),
                frequency=ReminderFrequency.MONTHLY,
            )
        )
        manager.add_bill(
            BillReminder.create(
                "Annual",
                1200,
                date.today(),
                frequency=ReminderFrequency.ANNUAL,
            )
        )

        # Monthly: $100 + Annual/12: $100 = $200
        total = manager.get_monthly_total()
        assert total == Decimal("200.00")

    def test_get_alerts(self) -> None:
        """Test alert generation."""
        manager = BillReminderManager()

        manager.add_bill(
            BillReminder.create(
                "Overdue",
                100,
                date.today() - timedelta(days=3),
            )
        )
        manager.add_bill(
            BillReminder.create(
                "Today",
                100,
                date.today(),
            )
        )
        manager.add_bill(
            BillReminder.create(
                "Upcoming",
                100,
                date.today() + timedelta(days=2),
                remind_days_before=5,
            )
        )

        alerts = manager.get_alerts()
        assert len(alerts) == 3

        # Should be sorted by severity
        assert alerts[0]["severity"] == "critical"
        assert alerts[1]["severity"] == "warning"
        assert alerts[2]["severity"] == "info"

    def test_summary(self) -> None:
        """Test summary generation."""
        manager = BillReminderManager()

        manager.add_bill(BillReminder.create("Bill 1", 100, date.today()))
        manager.add_bill(
            BillReminder.create("Bill 2", 200, date.today() + timedelta(days=5))
        )

        summary = manager.get_summary()
        assert summary["total_bills"] == 2
        assert summary["active_bills"] == 2
        assert "monthly_total" in summary

    def test_persistence(self) -> None:
        """Test saving and loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "reminders.json"
            manager = BillReminderManager(data_path=path)

            bill = BillReminder.create("Electric", 150, date(2025, 2, 1))
            manager.add_bill(bill)

            # Reload
            manager2 = BillReminderManager(data_path=path)
            loaded = manager2.get_bill(bill.id)

            assert loaded is not None
            assert loaded.name == bill.name
            assert loaded.amount == bill.amount


class TestCalendarExport:
    """Tests for ICS calendar export."""

    def test_export_to_ics(self) -> None:
        """Test exporting bills to ICS format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BillReminderManager()

            manager.add_bill(
                BillReminder.create(
                    "Electric",
                    150,
                    date(2025, 2, 1),
                    frequency=ReminderFrequency.MONTHLY,
                )
            )

            output_path = Path(tmpdir) / "bills.ics"
            result = manager.export_to_ics(output_path, months_ahead=3)

            assert result.exists()
            content = result.read_text()

            assert "BEGIN:VCALENDAR" in content
            assert "BEGIN:VEVENT" in content
            assert "Electric" in content
            assert "END:VCALENDAR" in content

    def test_ics_includes_reminders(self) -> None:
        """Test ICS includes reminder alarms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BillReminderManager()

            manager.add_bill(
                BillReminder.create(
                    "Test",
                    100,
                    date(2025, 2, 1),
                    remind_days_before=3,
                )
            )

            output_path = Path(tmpdir) / "bills.ics"
            manager.export_to_ics(output_path, include_reminders=True)

            content = output_path.read_text()
            assert "BEGIN:VALARM" in content
            assert "TRIGGER" in content

    def test_ics_recurring_events(self) -> None:
        """Test ICS generates multiple events for recurring bills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BillReminderManager()

            manager.add_bill(
                BillReminder.create(
                    "Monthly Bill",
                    100,
                    date(2025, 1, 1),
                    frequency=ReminderFrequency.MONTHLY,
                )
            )

            output_path = Path(tmpdir) / "bills.ics"
            manager.export_to_ics(output_path, months_ahead=3)

            content = output_path.read_text()
            # Should have at least 3 events
            assert content.count("BEGIN:VEVENT") >= 3


class TestBillTemplates:
    """Tests for bill templates."""

    def test_common_bills_defined(self) -> None:
        """Test that common bills are defined."""
        expected_bills = ["rent", "electric", "internet", "netflix", "gym"]
        for bill_type in expected_bills:
            assert bill_type in COMMON_BILLS

    def test_create_from_template(self) -> None:
        """Test creating bill from template."""
        bill = create_bill_from_template(
            "electric",
            amount=150,
            due_date=date(2025, 2, 15),
        )

        assert bill.name == "Electric Bill"
        assert bill.amount == Decimal("150")
        assert bill.category == ExpenseCategory.UTILITIES
        assert bill.frequency == ReminderFrequency.MONTHLY

    def test_template_with_overrides(self) -> None:
        """Test template with custom overrides."""
        bill = create_bill_from_template(
            "rent",
            amount=2000,
            due_date=date(2025, 2, 1),
            payee="Landlord LLC",
            auto_pay=True,
        )

        assert bill.amount == Decimal("2000")
        assert bill.payee == "Landlord LLC"
        assert bill.auto_pay is True

    def test_invalid_template(self) -> None:
        """Test error on invalid template."""
        with pytest.raises(ValueError, match="Unknown template"):
            create_bill_from_template("not_a_template", 100, date.today())
