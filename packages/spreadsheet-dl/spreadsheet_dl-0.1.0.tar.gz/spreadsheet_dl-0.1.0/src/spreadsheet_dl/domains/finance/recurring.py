"""Recurring Expenses - Manage recurring/scheduled expenses.

Provides tracking and automatic generation of recurring expenses
like subscriptions, bills, and regular payments.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory, ExpenseEntry


class RecurrenceFrequency(Enum):
    """Frequency of recurring expense."""

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class RecurringExpense:
    """Definition of a recurring expense."""

    name: str
    category: ExpenseCategory
    amount: Decimal
    frequency: RecurrenceFrequency
    start_date: date
    description: str = ""
    day_of_month: int | None = None  # For monthly (1-31)
    day_of_week: int | None = None  # For weekly (0=Monday, 6=Sunday)
    end_date: date | None = None
    enabled: bool = True
    notes: str = ""
    # Tracking
    last_generated: date | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category.value,
            "amount": str(self.amount),
            "frequency": self.frequency.value,
            "start_date": self.start_date.isoformat(),
            "description": self.description,
            "day_of_month": self.day_of_month,
            "day_of_week": self.day_of_week,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "enabled": self.enabled,
            "notes": self.notes,
            "last_generated": self.last_generated.isoformat()
            if self.last_generated
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RecurringExpense:
        """Create from dictionary."""
        category = ExpenseCategory(data["category"])
        frequency = RecurrenceFrequency(data["frequency"])

        return cls(
            name=data["name"],
            category=category,
            amount=Decimal(data["amount"]),
            frequency=frequency,
            start_date=date.fromisoformat(data["start_date"]),
            description=data.get("description", ""),
            day_of_month=data.get("day_of_month"),
            day_of_week=data.get("day_of_week"),
            end_date=date.fromisoformat(data["end_date"])
            if data.get("end_date")
            else None,
            enabled=data.get("enabled", True),
            notes=data.get("notes", ""),
            last_generated=date.fromisoformat(data["last_generated"])
            if data.get("last_generated")
            else None,
        )


class RecurringExpenseManager:
    """Manage recurring expenses.

    Handles storage, scheduling, and generation of recurring expenses
    as ExpenseEntry objects.
    """

    def __init__(self, config_path: Path | str | None = None) -> None:
        """Initialize manager.

        Args:
            config_path: Path to recurring expenses JSON file.
        """
        self.config_path = Path(config_path) if config_path else None
        self._expenses: list[RecurringExpense] = []

        if self.config_path and self.config_path.exists():
            self.load()

    def add(self, expense: RecurringExpense) -> None:
        """Add a recurring expense."""
        self._expenses.append(expense)
        self._save_if_configured()

    def remove(self, name: str) -> bool:
        """Remove a recurring expense by name."""
        original_len = len(self._expenses)
        self._expenses = [e for e in self._expenses if e.name != name]
        removed = len(self._expenses) < original_len
        if removed:
            self._save_if_configured()
        return removed

    def get(self, name: str) -> RecurringExpense | None:
        """Get a recurring expense by name."""
        return next((e for e in self._expenses if e.name == name), None)

    def list_all(self) -> list[RecurringExpense]:
        """List all recurring expenses."""
        return self._expenses.copy()

    def list_enabled(self) -> list[RecurringExpense]:
        """List only enabled recurring expenses."""
        return [e for e in self._expenses if e.enabled]

    def generate_for_period(
        self,
        start_date: date,
        end_date: date,
        update_last_generated: bool = True,
    ) -> list[ExpenseEntry]:
        """Generate ExpenseEntry objects for a date range.

        Args:
            start_date: Start of period.
            end_date: End of period.
            update_last_generated: Update last_generated date.

        Returns:
            List of ExpenseEntry objects for recurring expenses.
        """
        entries = []

        for recurring in self.list_enabled():
            # Check if recurring expense is active in this period
            if recurring.start_date > end_date:
                continue
            if recurring.end_date and recurring.end_date < start_date:
                continue

            # Generate occurrences
            occurrences = self._get_occurrences(recurring, start_date, end_date)

            for occurrence_date in occurrences:
                entry = ExpenseEntry(
                    date=occurrence_date,
                    category=recurring.category,
                    description=recurring.description or recurring.name,
                    amount=recurring.amount,
                    notes=f"Recurring: {recurring.name}"
                    + (f" - {recurring.notes}" if recurring.notes else ""),
                )
                entries.append(entry)

            # Update last generated
            if update_last_generated and occurrences:
                recurring.last_generated = max(occurrences)

        if update_last_generated:
            self._save_if_configured()

        return entries

    def generate_for_month(
        self,
        month: int,
        year: int,
        update_last_generated: bool = True,
    ) -> list[ExpenseEntry]:
        """Generate expenses for a specific month.

        Args:
            month: Month number (1-12).
            year: Year.
            update_last_generated: Update last_generated date.

        Returns:
            List of ExpenseEntry objects.
        """
        import calendar

        start = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end = date(year, month, last_day)

        return self.generate_for_period(start, end, update_last_generated)

    def _get_occurrences(
        self,
        recurring: RecurringExpense,
        start_date: date,
        end_date: date,
    ) -> list[date]:
        """Get all occurrence dates for a recurring expense in a period."""
        occurrences = []
        current = max(recurring.start_date, start_date)

        # Find first occurrence in period
        current = self._find_first_occurrence(recurring, current)

        while current <= end_date:
            if recurring.end_date and current > recurring.end_date:
                break

            if current >= start_date:
                occurrences.append(current)

            # Move to next occurrence
            current = self._next_occurrence(recurring, current)

        return occurrences

    def _find_first_occurrence(
        self,
        recurring: RecurringExpense,
        from_date: date,
    ) -> date:
        """Find first occurrence on or after from_date."""
        freq = recurring.frequency

        if freq == RecurrenceFrequency.DAILY:
            return from_date

        elif freq == RecurrenceFrequency.WEEKLY:
            target_dow = recurring.day_of_week or 0
            days_ahead = (target_dow - from_date.weekday()) % 7
            return from_date + timedelta(days=days_ahead)

        elif freq == RecurrenceFrequency.BIWEEKLY:
            target_dow = recurring.day_of_week or 0
            # Find next occurrence of target day
            days_ahead = (target_dow - from_date.weekday()) % 7
            candidate = from_date + timedelta(days=days_ahead)
            # Check if it aligns with biweekly schedule from start
            weeks_diff = (candidate - recurring.start_date).days // 7
            if weeks_diff % 2 != 0:
                candidate += timedelta(days=7)
            return candidate

        elif freq == RecurrenceFrequency.MONTHLY:
            target_day = recurring.day_of_month or 1
            if from_date.day <= target_day:
                try:
                    return date(from_date.year, from_date.month, target_day)
                except ValueError:
                    # Day doesn't exist in month (e.g., Feb 30)
                    import calendar

                    last_day = calendar.monthrange(from_date.year, from_date.month)[1]
                    return date(
                        from_date.year, from_date.month, min(target_day, last_day)
                    )
            else:
                # Move to next month
                next_month = from_date.month + 1
                next_year = from_date.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                try:
                    return date(next_year, next_month, target_day)
                except ValueError:
                    import calendar

                    last_day = calendar.monthrange(next_year, next_month)[1]
                    return date(next_year, next_month, min(target_day, last_day))

        elif freq == RecurrenceFrequency.QUARTERLY:
            # Every 3 months from start
            start = recurring.start_date
            months_since_start = (from_date.year - start.year) * 12 + (
                from_date.month - start.month
            )
            next_quarter = (months_since_start // 3 + 1) * 3
            target_month = (start.month + next_quarter - 1) % 12 + 1
            target_year = start.year + (start.month + next_quarter - 1) // 12
            try:
                return date(target_year, target_month, start.day)
            except ValueError:
                import calendar

                last_day = calendar.monthrange(target_year, target_month)[1]
                return date(target_year, target_month, min(start.day, last_day))

        elif freq == RecurrenceFrequency.YEARLY:
            try:
                this_year_occurrence = date(
                    from_date.year, recurring.start_date.month, recurring.start_date.day
                )
                if this_year_occurrence >= from_date:
                    return this_year_occurrence
                return date(
                    from_date.year + 1,
                    recurring.start_date.month,
                    recurring.start_date.day,
                )
            except ValueError:
                # Feb 29 handling
                return date(from_date.year + 1, recurring.start_date.month, 28)

        return from_date

    def _next_occurrence(
        self,
        recurring: RecurringExpense,
        current: date,
    ) -> date:
        """Get next occurrence after current date."""
        freq = recurring.frequency

        if freq == RecurrenceFrequency.DAILY:
            return current + timedelta(days=1)

        elif freq == RecurrenceFrequency.WEEKLY:
            return current + timedelta(weeks=1)

        elif freq == RecurrenceFrequency.BIWEEKLY:
            return current + timedelta(weeks=2)

        elif freq == RecurrenceFrequency.MONTHLY:
            next_month = current.month + 1
            next_year = current.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            target_day = recurring.day_of_month or current.day
            try:
                return date(next_year, next_month, target_day)
            except ValueError:
                import calendar

                last_day = calendar.monthrange(next_year, next_month)[1]
                return date(next_year, next_month, min(target_day, last_day))

        elif freq == RecurrenceFrequency.QUARTERLY:
            next_month = current.month + 3
            next_year = current.year
            while next_month > 12:
                next_month -= 12
                next_year += 1
            try:
                return date(next_year, next_month, current.day)
            except ValueError:
                import calendar

                last_day = calendar.monthrange(next_year, next_month)[1]
                return date(next_year, next_month, min(current.day, last_day))

        elif freq == RecurrenceFrequency.YEARLY:
            try:
                return date(current.year + 1, current.month, current.day)
            except ValueError:
                return date(current.year + 1, current.month, 28)

        return current + timedelta(days=1)

    def calculate_monthly_total(self) -> Decimal:
        """Calculate expected total monthly recurring expenses."""
        total = Decimal("0")

        for expense in self.list_enabled():
            if expense.frequency == RecurrenceFrequency.DAILY:
                # ~30 days per month
                total += expense.amount * 30
            elif expense.frequency == RecurrenceFrequency.WEEKLY:
                # ~4.33 weeks per month
                total += expense.amount * Decimal("4.33")
            elif expense.frequency == RecurrenceFrequency.BIWEEKLY:
                # ~2.17 times per month
                total += expense.amount * Decimal("2.17")
            elif expense.frequency == RecurrenceFrequency.MONTHLY:
                total += expense.amount
            elif expense.frequency == RecurrenceFrequency.QUARTERLY:
                total += expense.amount / 3
            elif expense.frequency == RecurrenceFrequency.YEARLY:
                total += expense.amount / 12

        return total.quantize(Decimal("0.01"))

    def load(self, path: Path | str | None = None) -> None:
        """Load recurring expenses from JSON file."""
        path = Path(path) if path else self.config_path
        if path is None or not path.exists():
            return

        with open(path) as f:
            data = json.load(f)

        self._expenses = [
            RecurringExpense.from_dict(item)
            for item in data.get("recurring_expenses", [])
        ]

    def save(self, path: Path | str | None = None) -> Path:
        """Save recurring expenses to JSON file."""
        path = Path(path) if path else self.config_path
        if path is None:
            raise ValueError("No config path specified")

        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "recurring_expenses": [e.to_dict() for e in self._expenses],
            "monthly_estimate": str(self.calculate_monthly_total()),
            "last_updated": date.today().isoformat(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return path

    def _save_if_configured(self) -> None:
        """Save if config path is set."""
        if self.config_path:
            self.save()


# Common recurring expense templates
COMMON_RECURRING: dict[str, dict[str, Any]] = {
    "rent": {
        "name": "Rent",
        "category": ExpenseCategory.HOUSING,
        "frequency": RecurrenceFrequency.MONTHLY,
        "day_of_month": 1,
    },
    "mortgage": {
        "name": "Mortgage",
        "category": ExpenseCategory.HOUSING,
        "frequency": RecurrenceFrequency.MONTHLY,
        "day_of_month": 1,
    },
    "netflix": {
        "name": "Netflix",
        "category": ExpenseCategory.SUBSCRIPTIONS,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "spotify": {
        "name": "Spotify",
        "category": ExpenseCategory.SUBSCRIPTIONS,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "electric": {
        "name": "Electric Bill",
        "category": ExpenseCategory.UTILITIES,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "water": {
        "name": "Water Bill",
        "category": ExpenseCategory.UTILITIES,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "internet": {
        "name": "Internet",
        "category": ExpenseCategory.UTILITIES,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "phone": {
        "name": "Phone",
        "category": ExpenseCategory.UTILITIES,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "car_insurance": {
        "name": "Car Insurance",
        "category": ExpenseCategory.INSURANCE,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "gym": {
        "name": "Gym Membership",
        "category": ExpenseCategory.HEALTHCARE,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
}


def create_common_recurring(
    template: str,
    amount: Decimal,
    start_date: date | None = None,
    **overrides: Any,
) -> RecurringExpense:
    """Create a recurring expense from a common template.

    Args:
        template: Template name (e.g., "netflix", "rent").
        amount: Monthly amount.
        start_date: Start date (defaults to today).
        **overrides: Additional overrides.

    Returns:
        RecurringExpense instance.
    """
    if template not in COMMON_RECURRING:
        raise ValueError(
            f"Unknown template: {template}. Available: {list(COMMON_RECURRING.keys())}"
        )

    config = COMMON_RECURRING[template].copy()
    config["amount"] = amount
    config["start_date"] = start_date or date.today()
    config.update(overrides)

    return RecurringExpense(**config)
