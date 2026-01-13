"""Bill Reminders and Calendar Integration Module.

Provides bill due date tracking, reminder generation, and ICS calendar export.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory


class ReminderStatus(Enum):
    """Status of a bill reminder."""

    PENDING = "pending"
    UPCOMING = "upcoming"  # Within reminder window
    DUE_TODAY = "due_today"
    OVERDUE = "overdue"
    PAID = "paid"
    SKIPPED = "skipped"


class ReminderFrequency(Enum):
    """How often the bill recurs."""

    ONE_TIME = "one_time"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


@dataclass
class BillReminder:
    """A bill with due date tracking and reminders.

    Attributes:
        id: Unique identifier.
        name: Bill name.
        payee: Who to pay.
        amount: Expected amount (can be estimate).
        due_date: Next due date.
        category: Expense category.
        frequency: How often bill recurs.
        remind_days_before: Days before due date to remind.
        auto_pay: Whether bill is on auto-pay.
        account: Account/card used for payment.
        notes: Additional notes.
        last_paid_date: When bill was last paid.
        last_paid_amount: Amount of last payment.
    """

    id: str
    name: str
    payee: str
    amount: Decimal
    due_date: date
    category: ExpenseCategory = ExpenseCategory.MISCELLANEOUS
    frequency: ReminderFrequency = ReminderFrequency.MONTHLY
    remind_days_before: int = 3
    auto_pay: bool = False
    account: str = ""
    notes: str = ""
    last_paid_date: date | None = None
    last_paid_amount: Decimal | None = None
    is_active: bool = True

    @classmethod
    def create(
        cls,
        name: str,
        amount: Decimal | float | str,
        due_date: date,
        payee: str = "",
        **kwargs: Any,
    ) -> BillReminder:
        """Create a new bill reminder."""
        return cls(
            id=str(uuid.uuid4())[:8],
            name=name,
            payee=payee or name,
            amount=Decimal(str(amount)),
            due_date=due_date,
            **kwargs,
        )

    @property
    def days_until_due(self) -> int:
        """Days until the bill is due."""
        return (self.due_date - date.today()).days

    @property
    def status(self) -> ReminderStatus:
        """Calculate current status."""
        if not self.is_active:
            return ReminderStatus.SKIPPED

        days = self.days_until_due

        if days < 0:
            return ReminderStatus.OVERDUE
        elif days == 0:
            return ReminderStatus.DUE_TODAY
        elif days <= self.remind_days_before:
            return ReminderStatus.UPCOMING
        else:
            return ReminderStatus.PENDING

    @property
    def is_due_soon(self) -> bool:
        """Check if bill is due within reminder window."""
        return self.days_until_due <= self.remind_days_before

    @property
    def next_due_date(self) -> date:
        """Calculate next due date after current one."""
        if self.frequency == ReminderFrequency.ONE_TIME:
            return self.due_date

        current = self.due_date
        today = date.today()

        # Advance to next occurrence if current is in the past
        while current < today:
            current = self._advance_date(current)

        return current

    def _advance_date(self, from_date: date) -> date:
        """Advance date by frequency."""
        if self.frequency == ReminderFrequency.WEEKLY:
            return from_date + timedelta(weeks=1)
        elif self.frequency == ReminderFrequency.BIWEEKLY:
            return from_date + timedelta(weeks=2)
        elif self.frequency == ReminderFrequency.MONTHLY:
            month = from_date.month + 1
            year = from_date.year
            if month > 12:
                month = 1
                year += 1
            # Handle months with fewer days
            day = min(from_date.day, self._days_in_month(year, month))
            return date(year, month, day)
        elif self.frequency == ReminderFrequency.QUARTERLY:
            month = from_date.month + 3
            year = from_date.year
            while month > 12:
                month -= 12
                year += 1
            day = min(from_date.day, self._days_in_month(year, month))
            return date(year, month, day)
        elif self.frequency == ReminderFrequency.SEMI_ANNUAL:
            month = from_date.month + 6
            year = from_date.year
            while month > 12:
                month -= 12
                year += 1
            day = min(from_date.day, self._days_in_month(year, month))
            return date(year, month, day)
        elif self.frequency == ReminderFrequency.ANNUAL:
            try:
                return date(from_date.year + 1, from_date.month, from_date.day)
            except ValueError:
                # Feb 29 handling
                return date(from_date.year + 1, from_date.month, 28)
        return from_date

    @staticmethod
    def _days_in_month(year: int, month: int) -> int:
        """Get days in a month."""
        import calendar

        return calendar.monthrange(year, month)[1]

    def mark_paid(
        self,
        amount: Decimal | float | str | None = None,
        paid_date: date | None = None,
        advance_due_date: bool = True,
    ) -> None:
        """Mark the bill as paid.

        Args:
            amount: Amount paid (defaults to expected amount).
            paid_date: Date of payment (defaults to today).
            advance_due_date: Advance to next due date.
        """
        self.last_paid_date = paid_date or date.today()
        self.last_paid_amount = Decimal(str(amount)) if amount else self.amount

        if advance_due_date and self.frequency != ReminderFrequency.ONE_TIME:
            self.due_date = self._advance_date(self.due_date)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "payee": self.payee,
            "amount": str(self.amount),
            "due_date": self.due_date.isoformat(),
            "category": self.category.value,
            "frequency": self.frequency.value,
            "remind_days_before": self.remind_days_before,
            "auto_pay": self.auto_pay,
            "account": self.account,
            "notes": self.notes,
            "last_paid_date": self.last_paid_date.isoformat()
            if self.last_paid_date
            else None,
            "last_paid_amount": str(self.last_paid_amount)
            if self.last_paid_amount
            else None,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BillReminder:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            payee=data.get("payee", data["name"]),
            amount=Decimal(data["amount"]),
            due_date=date.fromisoformat(data["due_date"]),
            category=ExpenseCategory(data.get("category", "miscellaneous")),
            frequency=ReminderFrequency(data.get("frequency", "monthly")),
            remind_days_before=data.get("remind_days_before", 3),
            auto_pay=data.get("auto_pay", False),
            account=data.get("account", ""),
            notes=data.get("notes", ""),
            last_paid_date=date.fromisoformat(data["last_paid_date"])
            if data.get("last_paid_date")
            else None,
            last_paid_amount=Decimal(data["last_paid_amount"])
            if data.get("last_paid_amount")
            else None,
            is_active=data.get("is_active", True),
        )


class BillReminderManager:
    """Manage bill reminders.

    Provides CRUD operations, reminder checking, and calendar export.
    """

    def __init__(self, data_path: Path | str | None = None) -> None:
        """Initialize reminder manager.

        Args:
            data_path: Path to reminders JSON file.
        """
        self.data_path = Path(data_path) if data_path else None
        self._bills: list[BillReminder] = []

        if self.data_path and self.data_path.exists():
            self.load()

    def add_bill(self, bill: BillReminder) -> None:
        """Add a bill reminder."""
        self._bills.append(bill)
        self._save_if_configured()

    def remove_bill(self, bill_id: str) -> bool:
        """Remove a bill by ID."""
        original_len = len(self._bills)
        self._bills = [b for b in self._bills if b.id != bill_id]
        removed = len(self._bills) < original_len
        if removed:
            self._save_if_configured()
        return removed

    def get_bill(self, bill_id: str) -> BillReminder | None:
        """Get a bill by ID."""
        return next((b for b in self._bills if b.id == bill_id), None)

    def get_bill_by_name(self, name: str) -> BillReminder | None:
        """Get a bill by name."""
        return next((b for b in self._bills if b.name.lower() == name.lower()), None)

    def list_bills(
        self,
        active_only: bool = True,
        status: ReminderStatus | None = None,
    ) -> list[BillReminder]:
        """List bills with optional filtering.

        Args:
            active_only: Only show active bills.
            status: Filter by status.
        """
        bills = self._bills.copy()

        if active_only:
            bills = [b for b in bills if b.is_active]

        if status:
            bills = [b for b in bills if b.status == status]

        return sorted(bills, key=lambda b: b.due_date)

    def get_upcoming_bills(self, days: int = 7) -> list[BillReminder]:
        """Get bills due within specified days."""
        cutoff = date.today() + timedelta(days=days)
        return [b for b in self._bills if b.is_active and b.due_date <= cutoff]

    def get_overdue_bills(self) -> list[BillReminder]:
        """Get all overdue bills."""
        return [b for b in self._bills if b.status == ReminderStatus.OVERDUE]

    def get_bills_due_today(self) -> list[BillReminder]:
        """Get bills due today."""
        return [b for b in self._bills if b.status == ReminderStatus.DUE_TODAY]

    def mark_paid(
        self,
        bill_id: str,
        amount: Decimal | float | str | None = None,
        paid_date: date | None = None,
    ) -> BillReminder | None:
        """Mark a bill as paid."""
        bill = self.get_bill(bill_id)
        if bill:
            bill.mark_paid(amount, paid_date)
            self._save_if_configured()
        return bill

    def get_monthly_total(self) -> Decimal:
        """Get expected monthly bill total."""
        total = Decimal("0")
        for bill in self._bills:
            if not bill.is_active:
                continue

            if bill.frequency == ReminderFrequency.WEEKLY:
                total += bill.amount * Decimal("4.33")
            elif bill.frequency == ReminderFrequency.BIWEEKLY:
                total += bill.amount * Decimal("2.17")
            elif bill.frequency == ReminderFrequency.MONTHLY:
                total += bill.amount
            elif bill.frequency == ReminderFrequency.QUARTERLY:
                total += bill.amount / 3
            elif bill.frequency == ReminderFrequency.SEMI_ANNUAL:
                total += bill.amount / 6
            elif bill.frequency == ReminderFrequency.ANNUAL:
                total += bill.amount / 12
            elif bill.frequency == ReminderFrequency.ONE_TIME:
                # Don't count one-time bills in monthly
                pass

        return total.quantize(Decimal("0.01"))

    def get_summary(self) -> dict[str, Any]:
        """Get summary of bill reminders."""
        active_bills = [b for b in self._bills if b.is_active]

        return {
            "total_bills": len(self._bills),
            "active_bills": len(active_bills),
            "overdue": len(self.get_overdue_bills()),
            "due_today": len(self.get_bills_due_today()),
            "upcoming_7_days": len(self.get_upcoming_bills(7)),
            "upcoming_30_days": len(self.get_upcoming_bills(30)),
            "auto_pay_count": len([b for b in active_bills if b.auto_pay]),
            "monthly_total": self.get_monthly_total(),
            "bills_by_status": {
                status.value: len([b for b in active_bills if b.status == status])
                for status in ReminderStatus
            },
        }

    def get_alerts(self) -> list[dict[str, Any]]:
        """Get actionable alerts for bills needing attention."""
        alerts = []

        for bill in self._bills:
            if not bill.is_active:
                continue

            if bill.status == ReminderStatus.OVERDUE:
                alerts.append(
                    {
                        "type": "overdue",
                        "severity": "critical",
                        "bill_id": bill.id,
                        "bill_name": bill.name,
                        "amount": bill.amount,
                        "due_date": bill.due_date,
                        "days_overdue": abs(bill.days_until_due),
                        "message": f"OVERDUE: {bill.name} was due {abs(bill.days_until_due)} days ago",
                    }
                )
            elif bill.status == ReminderStatus.DUE_TODAY:
                alerts.append(
                    {
                        "type": "due_today",
                        "severity": "warning",
                        "bill_id": bill.id,
                        "bill_name": bill.name,
                        "amount": bill.amount,
                        "due_date": bill.due_date,
                        "auto_pay": bill.auto_pay,
                        "message": f"DUE TODAY: {bill.name} - ${bill.amount}"
                        + (" (auto-pay)" if bill.auto_pay else ""),
                    }
                )
            elif bill.status == ReminderStatus.UPCOMING:
                alerts.append(
                    {
                        "type": "upcoming",
                        "severity": "info",
                        "bill_id": bill.id,
                        "bill_name": bill.name,
                        "amount": bill.amount,
                        "due_date": bill.due_date,
                        "days_until_due": bill.days_until_due,
                        "message": f"UPCOMING: {bill.name} due in {bill.days_until_due} days - ${bill.amount}",
                    }
                )

        # Sort by severity and due date
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        return sorted(
            alerts,
            key=lambda a: (severity_order[a["severity"]], a["due_date"]),
        )

    # Calendar Export (ICS)

    def export_to_ics(
        self,
        output_path: Path | str,
        months_ahead: int = 12,
        include_reminders: bool = True,
    ) -> Path:
        """Export bills to ICS calendar format.

        Args:
            output_path: Path for ICS file.
            months_ahead: How many months ahead to generate events.
            include_reminders: Add reminder alarms to events.

        Returns:
            Path to created ICS file.
        """
        output_path = Path(output_path)
        events = self._generate_calendar_events(months_ahead, include_reminders)

        ics_content = self._build_ics(events)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(ics_content)

        return output_path

    def _generate_calendar_events(
        self,
        months_ahead: int,
        include_reminders: bool,
    ) -> list[dict[str, Any]]:
        """Generate calendar events for bills."""
        events = []
        end_date = date.today() + timedelta(days=months_ahead * 30)

        for bill in self._bills:
            if not bill.is_active:
                continue

            current_date = bill.due_date
            while current_date <= end_date:
                event = {
                    "uid": f"{bill.id}-{current_date.isoformat()}",
                    "summary": f"Bill Due: {bill.name}",
                    "description": self._build_event_description(bill),
                    "date": current_date,
                    "categories": [bill.category.value.upper(), "BILLS"],
                    "remind_minutes": bill.remind_days_before * 24 * 60
                    if include_reminders
                    else None,
                }
                events.append(event)

                # Move to next occurrence
                if bill.frequency == ReminderFrequency.ONE_TIME:
                    break
                current_date = bill._advance_date(current_date)

        return sorted(events, key=lambda e: e["date"])

    def _build_event_description(self, bill: BillReminder) -> str:
        """Build event description for ICS."""
        lines = [
            f"Payee: {bill.payee}",
            f"Amount: ${bill.amount}",
            f"Category: {bill.category.value}",
            f"Frequency: {bill.frequency.value}",
        ]

        if bill.account:
            lines.append(f"Payment Account: {bill.account}")

        if bill.auto_pay:
            lines.append("Status: AUTO-PAY ENABLED")
        else:
            lines.append("Status: Manual payment required")

        if bill.notes:
            lines.append(f"Notes: {bill.notes}")

        return "\\n".join(lines)

    def _build_ics(self, events: list[dict[str, Any]]) -> str:
        """Build ICS file content."""
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//SpreadsheetDL//Bill Reminders//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:Bill Reminders",
            "X-WR-TIMEZONE:UTC",
        ]

        now = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

        for event in events:
            event_date = event["date"].strftime("%Y%m%d")

            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:{event['uid']}@spreadsheet-dl",
                    f"DTSTAMP:{now}",
                    f"DTSTART;VALUE=DATE:{event_date}",
                    f"DTEND;VALUE=DATE:{event_date}",
                    f"SUMMARY:{self._escape_ics(event['summary'])}",
                    f"DESCRIPTION:{event['description']}",
                    f"CATEGORIES:{','.join(event['categories'])}",
                    "TRANSP:TRANSPARENT",
                ]
            )

            # Add reminder alarm
            if event.get("remind_minutes"):
                lines.extend(
                    [
                        "BEGIN:VALARM",
                        "TRIGGER:-PT" + str(event["remind_minutes"]) + "M",
                        "ACTION:DISPLAY",
                        f"DESCRIPTION:Reminder: {event['summary']}",
                        "END:VALARM",
                    ]
                )

            lines.append("END:VEVENT")

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)

    @staticmethod
    def _escape_ics(text: str) -> str:
        """Escape special characters for ICS format."""
        return (
            text.replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )

    # Persistence

    def load(self, path: Path | str | None = None) -> None:
        """Load reminders from JSON file."""
        path = Path(path) if path else self.data_path
        if path is None or not path.exists():
            return

        with open(path) as f:
            data = json.load(f)

        self._bills = [
            BillReminder.from_dict(b) for b in data.get("bill_reminders", [])
        ]

    def save(self, path: Path | str | None = None) -> Path:
        """Save reminders to JSON file."""
        path = Path(path) if path else self.data_path
        if path is None:
            raise ValueError("No data path specified")

        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "bill_reminders": [b.to_dict() for b in self._bills],
            "summary": self.get_summary(),
            "last_updated": date.today().isoformat(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return path

    def _save_if_configured(self) -> None:
        """Save if data path is set."""
        if self.data_path:
            self.save()


# Common bill templates


COMMON_BILLS: dict[str, dict[str, Any]] = {
    "rent": {
        "name": "Rent",
        "category": ExpenseCategory.HOUSING,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 5,
    },
    "mortgage": {
        "name": "Mortgage",
        "category": ExpenseCategory.HOUSING,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 5,
    },
    "electric": {
        "name": "Electric Bill",
        "category": ExpenseCategory.UTILITIES,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 3,
    },
    "gas": {
        "name": "Gas Bill",
        "category": ExpenseCategory.UTILITIES,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 3,
    },
    "water": {
        "name": "Water Bill",
        "category": ExpenseCategory.UTILITIES,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 3,
    },
    "internet": {
        "name": "Internet",
        "category": ExpenseCategory.UTILITIES,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 3,
    },
    "phone": {
        "name": "Phone",
        "category": ExpenseCategory.UTILITIES,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 3,
    },
    "car_insurance": {
        "name": "Car Insurance",
        "category": ExpenseCategory.INSURANCE,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 5,
    },
    "health_insurance": {
        "name": "Health Insurance",
        "category": ExpenseCategory.INSURANCE,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 5,
    },
    "car_payment": {
        "name": "Car Payment",
        "category": ExpenseCategory.TRANSPORTATION,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 5,
    },
    "credit_card": {
        "name": "Credit Card",
        "category": ExpenseCategory.DEBT_PAYMENT,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 5,
    },
    "student_loan": {
        "name": "Student Loan",
        "category": ExpenseCategory.DEBT_PAYMENT,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 5,
    },
    "netflix": {
        "name": "Netflix",
        "category": ExpenseCategory.SUBSCRIPTIONS,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 1,
        "auto_pay": True,
    },
    "spotify": {
        "name": "Spotify",
        "category": ExpenseCategory.SUBSCRIPTIONS,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 1,
        "auto_pay": True,
    },
    "gym": {
        "name": "Gym Membership",
        "category": ExpenseCategory.HEALTHCARE,
        "frequency": ReminderFrequency.MONTHLY,
        "remind_days_before": 3,
    },
    "property_tax": {
        "name": "Property Tax",
        "category": ExpenseCategory.HOUSING,
        "frequency": ReminderFrequency.SEMI_ANNUAL,
        "remind_days_before": 14,
    },
    "home_insurance": {
        "name": "Home Insurance",
        "category": ExpenseCategory.INSURANCE,
        "frequency": ReminderFrequency.ANNUAL,
        "remind_days_before": 14,
    },
}


def create_bill_from_template(
    template: str,
    amount: Decimal | float | str,
    due_date: date,
    **overrides: Any,
) -> BillReminder:
    """Create a bill reminder from a common template.

    Args:
        template: Template name (e.g., "rent", "electric").
        amount: Bill amount.
        due_date: First due date.
        **overrides: Additional overrides.

    Returns:
        BillReminder instance.
    """
    if template not in COMMON_BILLS:
        raise ValueError(
            f"Unknown template: {template}. Available: {list(COMMON_BILLS.keys())}"
        )

    config = COMMON_BILLS[template].copy()
    config.update(overrides)

    return BillReminder.create(
        name=config.pop("name"),
        amount=amount,
        due_date=due_date,
        **config,
    )


def get_calendar_feed_url(
    manager: BillReminderManager,
    base_url: str = "",
) -> str:
    """Generate a URL for calendar feed (for webcal:// protocol).

    Args:
        manager: BillReminderManager instance.
        base_url: Base URL for the feed.

    Returns:
        webcal:// URL for subscription.
    """
    # This would typically be hosted on a server
    # For local use, return file:// path
    if manager.data_path:
        ics_path = manager.data_path.parent / "bills.ics"
        return f"file://{ics_path}"
    return f"{base_url}/bills.ics"
