# Recurring Expenses Module

## Overview

The recurring module manages recurring and scheduled expenses like subscriptions, bills, and regular payments. It automatically generates expense entries for configurable frequencies (daily, weekly, monthly, etc.) and integrates with the budget ODS generator.

**Key Features:**

- Multiple recurrence frequencies (daily, weekly, biweekly, monthly, quarterly, yearly)
- Automatic expense entry generation for any time period
- Monthly total calculation with frequency-based averaging
- Day-of-month and day-of-week scheduling
- Start/end date support
- Enable/disable toggle without deletion
- JSON persistence
- Common recurring expense templates
- Last-generated tracking to prevent duplicates

**Use Cases:**

- Track subscriptions (Netflix, Spotify, etc.)
- Manage recurring bills (rent, utilities)
- Auto-generate monthly expenses
- Calculate expected monthly recurring costs
- Schedule regular payments
- Forecast future expenses

## Enums

### RecurrenceFrequency

Frequency options for recurring expenses.

```python
class RecurrenceFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"      # Every 2 weeks
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"     # Every 3 months
    YEARLY = "yearly"
```

## Classes

### RecurringExpense

Definition of a recurring expense with schedule.

**Attributes:**

- `name` (str): Expense name/identifier
- `category` (ExpenseCategory): Budget category
- `amount` (Decimal): Amount per occurrence
- `frequency` (RecurrenceFrequency): How often it recurs
- `start_date` (date): Start date
- `description` (str): Description for expense entries
- `day_of_month` (int | None): Day of month for monthly (1-31)
- `day_of_week` (int | None): Day of week for weekly (0=Monday, 6=Sunday)
- `end_date` (date | None): Optional end date
- `enabled` (bool): Whether actively generating expenses
- `notes` (str): Additional notes
- `last_generated` (date | None): Last generation date (tracking)

**Methods:**

```python
def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for serialization."""
```

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> RecurringExpense:
    """Create from dictionary."""
```

**Example:**

```python
from spreadsheet_dl.domains.finance.recurring import RecurringExpense, RecurrenceFrequency
from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory
from decimal import Decimal
from datetime import date

# Create monthly rent
rent = RecurringExpense(
    name="Rent",
    category=ExpenseCategory.HOUSING,
    amount=Decimal("1500.00"),
    frequency=RecurrenceFrequency.MONTHLY,
    start_date=date(2024, 1, 1),
    day_of_month=1,  # Due on 1st of month
    description="Monthly Rent"
)

# Create weekly coffee subscription
coffee = RecurringExpense(
    name="Coffee Subscription",
    category=ExpenseCategory.GROCERIES,
    amount=Decimal("25.00"),
    frequency=RecurrenceFrequency.WEEKLY,
    start_date=date.today(),
    day_of_week=1,  # Tuesdays
    description="Weekly coffee delivery"
)
```

### RecurringExpenseManager

Manage recurring expenses with generation and persistence.

**Methods:**

```python
def __init__(self, config_path: Path | str | None = None) -> None:
    """
    Initialize manager.

    Args:
        config_path: Path to JSON config file for persistence.
    """
```

```python
def add(self, expense: RecurringExpense) -> None:
    """Add a recurring expense and save."""
```

```python
def remove(self, name: str) -> bool:
    """Remove a recurring expense by name."""
```

```python
def get(self, name: str) -> RecurringExpense | None:
    """Get a recurring expense by name."""
```

```python
def list_all(self) -> list[RecurringExpense]:
    """List all recurring expenses."""
```

```python
def list_enabled(self) -> list[RecurringExpense]:
    """List only enabled recurring expenses."""
```

```python
def generate_for_period(
    self,
    start_date: date,
    end_date: date,
    update_last_generated: bool = True,
) -> list[ExpenseEntry]:
    """
    Generate ExpenseEntry objects for a date range.

    Args:
        start_date: Start of period.
        end_date: End of period.
        update_last_generated: Update last_generated tracking date.

    Returns:
        List of ExpenseEntry objects for all recurring expenses
        in the period.
    """
```

```python
def generate_for_month(
    self,
    month: int,
    year: int,
    update_last_generated: bool = True,
) -> list[ExpenseEntry]:
    """
    Generate expenses for a specific month.

    Args:
        month: Month number (1-12).
        year: Year.
        update_last_generated: Update tracking.

    Returns:
        List of ExpenseEntry objects for the month.
    """
```

```python
def calculate_monthly_total(self) -> Decimal:
    """
    Calculate expected monthly total for all enabled recurring expenses.

    Converts all frequencies to monthly equivalents:
    - Daily: amount * 30
    - Weekly: amount * 4.33
    - Biweekly: amount * 2.17
    - Monthly: amount
    - Quarterly: amount / 3
    - Yearly: amount / 12

    Returns:
        Expected monthly total.
    """
```

```python
def load(self, path: Path | str | None = None) -> None:
    """Load recurring expenses from JSON."""
```

```python
def save(self, path: Path | str | None = None) -> Path:
    """Save recurring expenses to JSON."""
```

**Example:**

```python
from spreadsheet_dl.domains.finance.recurring import RecurringExpenseManager, create_common_recurring
from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory
from decimal import Decimal
from datetime import date

# Create manager with persistence
manager = RecurringExpenseManager("recurring.json")

# Add recurring expenses using templates
netflix = create_common_recurring("netflix", amount=15.99, start_date=date.today())
rent = create_common_recurring("rent", amount=1500, start_date=date(2024, 1, 1))

manager.add(netflix)
manager.add(rent)

# Generate expenses for current month
entries = manager.generate_for_month(month=6, year=2024)
print(f"Generated {len(entries)} expense entries")

for entry in entries:
    print(f"{entry.date}: {entry.description} - ${entry.amount}")

# Calculate monthly total
monthly_total = manager.calculate_monthly_total()
print(f"\nExpected monthly total: ${monthly_total:,.2f}")

# List all recurring
for recurring in manager.list_enabled():
    print(f"{recurring.name}: ${recurring.amount} {recurring.frequency.value}")
```

## Functions

### create_common_recurring(template, amount, start_date=None, \*\*overrides) -> RecurringExpense

Create a recurring expense from a predefined template.

**Parameters:**

- `template` (str): Template name (see COMMON_RECURRING dict)
- `amount` (Decimal): Amount per occurrence
- `start_date` (date | None): Start date (defaults to today)
- `**overrides`: Override template values

**Available Templates:**

- `rent`, `mortgage`, `netflix`, `spotify`, `electric`, `water`, `internet`, `phone`
- `car_insurance`, `gym`

**Returns:**

- RecurringExpense instance

**Example:**

```python
from spreadsheet_dl.domains.finance.recurring import create_common_recurring
from datetime import date

# Create Netflix subscription
netflix = create_common_recurring("netflix", amount=15.99)

# Create rent with custom day
rent = create_common_recurring(
    "rent",
    amount=1500,
    start_date=date(2024, 1, 1),
    day_of_month=5  # Override to 5th instead of 1st
)

# Create custom recurring not in template
from spreadsheet_dl.domains.finance.recurring import RecurringExpense, RecurrenceFrequency
from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory

custom = RecurringExpense(
    name="Dog Walker",
    category=ExpenseCategory.PETS,
    amount=40,
    frequency=RecurrenceFrequency.WEEKLY,
    start_date=date.today(),
    day_of_week=3  # Thursdays
)
```

## Constants

### COMMON_RECURRING

Dictionary of common recurring expense templates.

```python
COMMON_RECURRING = {
    "rent": {
        "name": "Rent",
        "category": ExpenseCategory.HOUSING,
        "frequency": RecurrenceFrequency.MONTHLY,
        "day_of_month": 1,
    },
    "mortgage": {...},
    "netflix": {
        "name": "Netflix",
        "category": ExpenseCategory.SUBSCRIPTIONS,
        "frequency": RecurrenceFrequency.MONTHLY,
    },
    "spotify": {...},
    "electric": {...},
    "water": {...},
    "internet": {...},
    "phone": {...},
    "car_insurance": {...},
    "gym": {...},
}
```

## Usage Examples

### Basic Recurring Expense Management

```python
from spreadsheet_dl.domains.finance.recurring import RecurringExpenseManager, create_common_recurring
from datetime import date

# Initialize manager
manager = RecurringExpenseManager("recurring.json")

# Add common expenses
manager.add(create_common_recurring("netflix", 15.99))
manager.add(create_common_recurring("spotify", 10.99))
manager.add(create_common_recurring("rent", 1500))
manager.add(create_common_recurring("electric", 120))

# Generate for current month
today = date.today()
entries = manager.generate_for_month(today.month, today.year)

print(f"Recurring expenses for {today.month}/{today.year}:")
for entry in entries:
    print(f"  {entry.date}: {entry.description} - ${entry.amount}")
```

### Custom Recurrence Schedules

```python
from spreadsheet_dl.domains.finance.recurring import RecurringExpense, RecurrenceFrequency, RecurringExpenseManager
from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory
from decimal import Decimal
from datetime import date

manager = RecurringExpenseManager()

# Biweekly paycheck deduction
insurance = RecurringExpense(
    name="Health Insurance",
    category=ExpenseCategory.INSURANCE,
    amount=Decimal("150.00"),
    frequency=RecurrenceFrequency.BIWEEKLY,
    start_date=date(2024, 1, 5),  # First Friday of year
    day_of_week=4,  # Fridays
    description="Health insurance deduction"
)
manager.add(insurance)

# Quarterly estimated taxes
taxes = RecurringExpense(
    name="Estimated Taxes",
    category=ExpenseCategory.MISCELLANEOUS,
    amount=Decimal("1200.00"),
    frequency=RecurrenceFrequency.QUARTERLY,
    start_date=date(2024, 1, 15),
    description="Quarterly tax payment"
)
manager.add(taxes)

# Generate for full year
start = date(2024, 1, 1)
end = date(2024, 12, 31)
all_entries = manager.generate_for_period(start, end)
print(f"Total recurring expenses for year: {len(all_entries)} entries")
```

### Integration with Budget ODS

```python
from spreadsheet_dl.domains.finance.recurring import RecurringExpenseManager
from spreadsheet_dl.domains.finance.ods_generator import BudgetODSGenerator
from datetime import date

# Setup recurring expenses
recurring_manager = RecurringExpenseManager("recurring.json")

# Generate recurring entries for current month
today = date.today()
recurring_entries = recurring_manager.generate_for_month(today.month, today.year)

# Create budget with recurring expenses
budget_gen = BudgetODSGenerator()

# Add recurring entries
for entry in recurring_entries:
    budget_gen.add_expense(entry)

# Add manual entries
budget_gen.add_expense_simple(date.today(), "Groceries", "Weekly shopping", 85.50)

# Generate budget file
budget_gen.save("budget_with_recurring.ods")
```

### Monthly Budget Calculation

```python
from spreadsheet_dl.domains.finance.recurring import RecurringExpenseManager, create_common_recurring

manager = RecurringExpenseManager()

# Add various frequencies
manager.add(create_common_recurring("rent", 1500))           # Monthly
manager.add(create_common_recurring("netflix", 15.99))       # Monthly
manager.add(create_common_recurring("car_insurance", 180))   # Monthly

# Calculate expected monthly total
monthly_total = manager.calculate_monthly_total()
print(f"Expected monthly recurring expenses: ${monthly_total:,.2f}")

# Break down by category
from collections import defaultdict
by_category = defaultdict(Decimal)

for recurring in manager.list_enabled():
    # Convert to monthly amount
    if recurring.frequency.value == "monthly":
        monthly_amt = recurring.amount
    elif recurring.frequency.value == "weekly":
        monthly_amt = recurring.amount * Decimal("4.33")
    elif recurring.frequency.value == "yearly":
        monthly_amt = recurring.amount / 12
    # ... etc

    by_category[recurring.category.value] += monthly_amt

print("\nBy Category:")
for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat}: ${amt:,.2f}")
```

### Disable/Enable Expenses

```python
from spreadsheet_dl.domains.finance.recurring import RecurringExpenseManager

manager = RecurringExpenseManager("recurring.json")

# Temporarily disable an expense
gym = manager.get("Gym Membership")
if gym:
    gym.enabled = False
    manager.save()  # Persist change

# Later, re-enable
gym.enabled = True
manager.save()

# Only enabled expenses are included in generation
enabled_count = len(manager.list_enabled())
total_count = len(manager.list_all())
print(f"{enabled_count} of {total_count} recurring expenses enabled")
```

## See Also

- [ods_generator](ods_generator.md) - Budget ODS file generation
- [reminders](reminders.md) - Bill reminders and notifications
- [budget_analyzer](budget_analyzer.md) - Budget analysis
