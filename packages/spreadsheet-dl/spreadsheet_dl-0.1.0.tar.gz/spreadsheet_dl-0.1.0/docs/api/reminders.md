# Reminders Module

## Overview

The reminders module provides bill due date tracking, reminder generation, and ICS calendar export. It manages recurring bills with automatic status detection, alert generation, and integration with calendar applications.

**Key Features:**

- Bill due date tracking with status (upcoming, due today, overdue)
- Multiple reminder frequencies (one-time, weekly, monthly, annual, etc.)
- Configurable reminder days before due date
- Auto-pay tracking
- Payment history and next-due-date calculation
- ICS calendar export with alarms
- Bill templates for common expenses
- Monthly cost calculation
- Alert generation for due/overdue bills

**Use Cases:**

- Track all recurring bills in one place
- Get reminders before bills are due
- Export to calendar (Google Calendar, Apple Calendar, Outlook)
- Monitor overdue payments
- Calculate monthly bill totals
- Manage auto-pay vs manual bills

## Enums

### ReminderStatus

```python
class ReminderStatus(Enum):
    PENDING = "pending"          # Not yet in reminder window
    UPCOMING = "upcoming"        # Within reminder window
    DUE_TODAY = "due_today"      # Due today
    OVERDUE = "overdue"          # Past due
    PAID = "paid"                # Paid (after marking)
    SKIPPED = "skipped"          # Inactive
```

### ReminderFrequency

```python
class ReminderFrequency(Enum):
    ONE_TIME = "one_time"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
```

## Classes

### BillReminder

A bill with due date tracking and reminders.

**Attributes:**

- `id` (str): Unique identifier
- `name` (str): Bill name
- `payee` (str): Who to pay
- `amount` (Decimal): Expected amount
- `due_date` (date): Next due date
- `category` (ExpenseCategory): Category
- `frequency` (ReminderFrequency): How often it recurs
- `remind_days_before` (int): Days before to remind (default: 3)
- `auto_pay` (bool): Whether on auto-pay
- `account` (str): Account/card used
- `notes` (str): Additional notes
- `last_paid_date` (date | None): Last payment date
- `last_paid_amount` (Decimal | None): Last payment amount
- `is_active` (bool): Whether actively tracking

**Properties:**

- `days_until_due` (int): Days until due date
- `status` (ReminderStatus): Current status (auto-calculated)
- `is_due_soon` (bool): Within reminder window
- `next_due_date` (date): Calculated next due date

**Methods:**

```python
@classmethod
def create(
    cls,
    name: str,
    amount: Decimal | float | str,
    due_date: date,
    payee: str = "",
    **kwargs: Any,
) -> BillReminder:
    """Create new bill reminder with auto-generated ID."""
```

```python
def mark_paid(
    self,
    amount: Decimal | float | str | None = None,
    paid_date: date | None = None,
    advance_due_date: bool = True,
) -> None:
    """
    Mark bill as paid and optionally advance to next due date.

    Args:
        amount: Amount paid (defaults to expected amount).
        paid_date: Payment date (defaults to today).
        advance_due_date: Advance to next occurrence.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.reminders import BillReminder, ReminderFrequency
from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory
from datetime import date, timedelta

# Create monthly rent bill
rent = BillReminder.create(
    name="Rent",
    amount=1500,
    due_date=date.today() + timedelta(days=5),
    payee="Landlord LLC",
    frequency=ReminderFrequency.MONTHLY,
    category=ExpenseCategory.HOUSING,
    remind_days_before=5
)

# Check status
print(f"Status: {rent.status.value}")
print(f"Days until due: {rent.days_until_due}")
print(f"Is due soon: {rent.is_due_soon}")

# Mark as paid
rent.mark_paid(amount=1500)
print(f"Next due date: {rent.due_date}")
```

### BillReminderManager

Manage bill reminders with CRUD, alerts, and calendar export.

**Methods:**

```python
def add_bill(self, bill: BillReminder) -> None:
    """Add a bill reminder and save."""
```

```python
def remove_bill(self, bill_id: str) -> bool:
    """Remove a bill by ID."""
```

```python
def list_bills(
    self,
    active_only: bool = True,
    status: ReminderStatus | None = None,
) -> list[BillReminder]:
    """List bills with optional filtering."""
```

```python
def get_upcoming_bills(self, days: int = 7) -> list[BillReminder]:
    """Get bills due within specified days."""
```

```python
def get_overdue_bills(self) -> list[BillReminder]:
    """Get all overdue bills."""
```

```python
def get_bills_due_today(self) -> list[BillReminder]:
    """Get bills due today."""
```

```python
def mark_paid(
    self,
    bill_id: str,
    amount: Decimal | float | str | None = None,
    paid_date: date | None = None,
) -> BillReminder | None:
    """Mark a bill as paid."""
```

```python
def get_monthly_total(self) -> Decimal:
    """Get expected monthly bill total (frequency-averaged)."""
```

```python
def get_summary(self) -> dict[str, Any]:
    """
    Get summary of bill reminders.

    Returns:
        Dict with counts, totals, and status breakdown.
    """
```

```python
def get_alerts(self) -> list[dict[str, Any]]:
    """
    Get actionable alerts for bills needing attention.

    Returns:
        List of alert dicts with type, severity, and message.
    """
```

```python
def export_to_ics(
    self,
    output_path: Path | str,
    months_ahead: int = 12,
    include_reminders: bool = True,
) -> Path:
    """
    Export bills to ICS calendar format.

    Args:
        output_path: Path for ICS file.
        months_ahead: Months to generate events (default: 12).
        include_reminders: Add reminder alarms (default: True).

    Returns:
        Path to created ICS file.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.reminders import BillReminderManager, create_bill_from_template
from datetime import date

# Initialize manager
manager = BillReminderManager("bills.json")

# Add bills using templates
rent = create_bill_from_template("rent", 1500, date(2024, 7, 1))
electric = create_bill_from_template("electric", 120, date(2024, 7, 15))
netflix = create_bill_from_template("netflix", 15.99, date(2024, 7, 10))

manager.add_bill(rent)
manager.add_bill(electric)
manager.add_bill(netflix)

# Get upcoming bills
upcoming = manager.get_upcoming_bills(days=7)
print(f"{len(upcoming)} bills due in next 7 days")

# Get alerts
alerts = manager.get_alerts()
for alert in alerts:
    print(f"[{alert['severity'].upper()}] {alert['message']}")

# Export to calendar
calendar_file = manager.export_to_ics("bills.ics", months_ahead=12)
print(f"Calendar exported to {calendar_file}")

# Get summary
summary = manager.get_summary()
print(f"Total bills: {summary['total_bills']}")
print(f"Monthly total: ${summary['monthly_total']}")
print(f"Overdue: {summary['overdue']}")
```

## Functions

### create_bill_from_template(template, amount, due_date, \*\*overrides) -> BillReminder

Create a bill reminder from a common template.

**Available Templates:**

- `rent`, `mortgage`, `electric`, `gas`, `water`, `internet`, `phone`
- `car_insurance`, `health_insurance`, `car_payment`
- `credit_card`, `student_loan`
- `netflix`, `spotify`, `gym`
- `property_tax`, `home_insurance`

**Example:**

```python
from spreadsheet_dl.domains.finance.reminders import create_bill_from_template
from datetime import date

# Create electric bill
electric = create_bill_from_template(
    "electric",
    amount=120,
    due_date=date(2024, 7, 15),
    account="Checking ***1234"  # Override
)
```

### get_calendar_feed_url(manager, base_url="") -> str

Generate URL for calendar feed (webcal:// protocol).

**Parameters:**

- `manager` (BillReminderManager): Manager instance
- `base_url` (str): Base URL (optional)

**Returns:**

- webcal:// URL for calendar subscription

## Usage Examples

### Daily Bill Check

```python
from spreadsheet_dl.domains.finance.reminders import BillReminderManager

manager = BillReminderManager("bills.json")

# Check for urgent bills
overdue = manager.get_overdue_bills()
if overdue:
    print(f"OVERDUE BILLS: {len(overdue)}")
    for bill in overdue:
        days_late = abs(bill.days_until_due)
        print(f"  - {bill.name}: ${bill.amount} ({days_late} days late)")

# Today's bills
today = manager.get_bills_due_today()
if today:
    print(f"\nDUE TODAY: {len(today)}")
    for bill in today:
        auto = "(AUTO-PAY)" if bill.auto_pay else ""
        print(f"  - {bill.name}: ${bill.amount} {auto}")

# Upcoming
upcoming = manager.get_upcoming_bills(days=3)
if upcoming:
    print(f"\nUPCOMING (next 3 days): {len(upcoming)}")
    for bill in upcoming:
        print(f"  - {bill.name}: ${bill.amount} in {bill.days_until_due} days")
```

### Pay Bills Workflow

```python
from spreadsheet_dl.domains.finance.reminders import BillReminderManager
from datetime import date

manager = BillReminderManager("bills.json")

# Get bills to pay
to_pay = manager.get_bills_due_today() + manager.get_upcoming_bills(days=2)

for bill in to_pay:
    if bill.auto_pay:
        print(f"Skipping {bill.name} (auto-pay)")
        continue

    print(f"Pay {bill.name} to {bill.payee}: ${bill.amount}")
    # ... payment logic ...

    # Mark as paid
    manager.mark_paid(bill.id, amount=bill.amount, paid_date=date.today())
    print(f"  ✓ Paid. Next due: {bill.due_date}")
```

### Calendar Integration

```python
from spreadsheet_dl.domains.finance.reminders import BillReminderManager

manager = BillReminderManager("bills.json")

# Export to ICS file
ics_file = manager.export_to_ics(
    "my_bills.ics",
    months_ahead=12,
    include_reminders=True
)

print(f"Calendar file created: {ics_file}")
print("Import this file into:")
print("  - Google Calendar")
print("  - Apple Calendar")
print("  - Outlook")
print("  - Any calendar app supporting ICS")
```

### Monthly Planning

```python
from spreadsheet_dl.domains.finance.reminders import BillReminderManager

manager = BillReminderManager("bills.json")

summary = manager.get_summary()

print("MONTHLY BILL SUMMARY")
print("=" * 50)
print(f"Total Bills: {summary['total_bills']}")
print(f"Active: {summary['active_bills']}")
print(f"Auto-Pay: {summary['auto_pay_count']}")
print(f"\nExpected Monthly Total: ${summary['monthly_total']:,.2f}")

# Breakdown by status
print("\nBy Status:")
for status, count in summary['bills_by_status'].items():
    if count > 0:
        print(f"  {status}: {count}")
```

## See Also

- [recurring](recurring.md) - Recurring expense management
- [notifications](../notifications.md) - Notification delivery
- [goals](goals.md) - Goal tracking and debt payoff
