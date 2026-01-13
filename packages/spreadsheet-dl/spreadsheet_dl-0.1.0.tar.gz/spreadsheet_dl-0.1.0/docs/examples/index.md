# Examples

Practical examples for using SpreadsheetDL.

## Quick Start Examples

### Create Your First Budget

```python
from spreadsheet_dl import create_monthly_budget

# Create budget for current month
path = create_monthly_budget("./budgets/")
print(f"Created: {path}")
# Output: Created: budgets/budget_2025_01.ods
```

### Add an Expense

```python
from spreadsheet_dl import OdsEditor, ExpenseEntry, ExpenseCategory
from decimal import Decimal
from datetime import date

editor = OdsEditor("budgets/budget_2025_01.ods")
editor.append_expense(ExpenseEntry(
    date=date.today(),
    category=ExpenseCategory.GROCERIES,
    description="Weekly groceries",
    amount=Decimal("125.50"),
))
editor.save()
```

### View Budget Summary

```python
from spreadsheet_dl import BudgetAnalyzer

analyzer = BudgetAnalyzer("budgets/budget_2025_01.ods")
summary = analyzer.get_summary()

print(f"Budget: ${summary.total_budget:,.2f}")
print(f"Spent:  ${summary.total_spent:,.2f}")
print(f"Used:   {summary.percent_used:.1f}%")
```

---

## Complete Workflow Example

```python
"""
Complete monthly budget workflow example.

Creates a budget, adds expenses, analyzes, and generates reports.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from spreadsheet_dl import (
    OdsGenerator,
    OdsEditor,
    BudgetAnalyzer,
    ReportGenerator,
    ExpenseEntry,
    ExpenseCategory,
    BudgetAllocation,
)

# Configuration
OUTPUT_DIR = Path("./budgets")
OUTPUT_DIR.mkdir(exist_ok=True)
MONTH = 1
YEAR = 2025

# Step 1: Create budget with custom allocations
print("Creating budget...")

allocations = [
    BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1500")),
    BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
    BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600")),
    BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("400")),
    BudgetAllocation(ExpenseCategory.HEALTHCARE, Decimal("200")),
    BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
    BudgetAllocation(ExpenseCategory.ENTERTAINMENT, Decimal("150")),
    BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("500")),
]

generator = OdsGenerator(theme="default")
budget_path = generator.create_budget_spreadsheet(
    OUTPUT_DIR / f"budget_{YEAR}_{MONTH:02d}.ods",
    month=MONTH,
    year=YEAR,
    budget_allocations=allocations,
)
print(f"Created: {budget_path}")

# Step 2: Add some expenses
print("\nAdding expenses...")

expenses = [
    ExpenseEntry(
        date=date(2025, 1, 1),
        category=ExpenseCategory.HOUSING,
        description="Rent payment",
        amount=Decimal("1500.00"),
    ),
    ExpenseEntry(
        date=date(2025, 1, 5),
        category=ExpenseCategory.GROCERIES,
        description="Costco shopping",
        amount=Decimal("245.50"),
    ),
    ExpenseEntry(
        date=date(2025, 1, 8),
        category=ExpenseCategory.UTILITIES,
        description="Electric bill",
        amount=Decimal("95.00"),
    ),
    ExpenseEntry(
        date=date(2025, 1, 12),
        category=ExpenseCategory.DINING_OUT,
        description="Birthday dinner",
        amount=Decimal("125.00"),
    ),
    ExpenseEntry(
        date=date(2025, 1, 15),
        category=ExpenseCategory.TRANSPORTATION,
        description="Gas",
        amount=Decimal("45.00"),
    ),
]

editor = OdsEditor(budget_path)
for expense in expenses:
    row = editor.append_expense(expense)
    print(f"  Added: {expense.description} -> row {row}")
editor.save()

# Step 3: Analyze the budget
print("\nAnalyzing budget...")

analyzer = BudgetAnalyzer(budget_path)
summary = analyzer.get_summary()

print(f"\nBudget Summary:")
print(f"  Total Budget:  ${summary.total_budget:,.2f}")
print(f"  Total Spent:   ${summary.total_spent:,.2f}")
print(f"  Remaining:     ${summary.total_remaining:,.2f}")
print(f"  Percent Used:  {summary.percent_used:.1f}%")

if summary.alerts:
    print("\nAlerts:")
    for alert in summary.alerts:
        print(f"  - {alert}")

# Step 4: Generate report
print("\nGenerating report...")

report_gen = ReportGenerator(budget_path)
report_path = OUTPUT_DIR / "january_report.md"
report_gen.save_report(report_path, format="markdown")
print(f"Report saved: {report_path}")

print("\nDone!")
```

---

## CLI Workflow Example

```bash
#!/bin/bash
# Monthly budget workflow using CLI

# Create directory
mkdir -p ~/finances/2025

# Generate January budget
uv run spreadsheet-dl generate \
    -o ~/finances/2025/ \
    -m 1 -y 2025 \
    --theme default

# Add expenses
uv run spreadsheet-dl expense 1500 "Rent" -c Housing -d 2025-01-01
uv run spreadsheet-dl expense 245.50 "Costco" -c Groceries -d 2025-01-05
uv run spreadsheet-dl expense 95 "Electric" -c Utilities -d 2025-01-08
uv run spreadsheet-dl expense 125 "Dinner out" -c "Dining Out" -d 2025-01-12
uv run spreadsheet-dl expense 45 "Gas" -c Transportation -d 2025-01-15

# View dashboard
uv run spreadsheet-dl dashboard ~/finances/2025/budget_2025_01.ods

# Check alerts
uv run spreadsheet-dl alerts ~/finances/2025/budget_2025_01.ods

# Generate report
uv run spreadsheet-dl report \
    ~/finances/2025/budget_2025_01.ods \
    -f markdown \
    -o ~/finances/2025/january_report.md

echo "Done!"
```

---

## Import Bank Data Example

```python
"""
Import bank CSV and create budget.
"""

from pathlib import Path
from spreadsheet_dl import import_bank_csv, OdsGenerator

# Import from Chase CSV
csv_path = Path("~/Downloads/Chase_Activity.csv").expanduser()
expenses = import_bank_csv(csv_path, bank="chase")

print(f"Imported {len(expenses)} transactions")
print(f"Total: ${sum(e.amount for e in expenses):,.2f}")

# Preview categories
from collections import Counter
categories = Counter(e.category.value for e in expenses)
print("\nBy category:")
for cat, count in categories.most_common():
    print(f"  {cat}: {count}")

# Create budget with imported expenses
generator = OdsGenerator(theme="minimal")
generator.create_budget_spreadsheet(
    "imported_budget.ods",
    expenses=expenses,
)
```

---

## Recurring Expenses Example

```python
"""
Manage recurring expenses.
"""

from decimal import Decimal
from datetime import date
from spreadsheet_dl import (
    RecurringExpenseManager,
    RecurringExpense,
    RecurrenceFrequency,
    ExpenseCategory,
)

# Create manager
manager = RecurringExpenseManager("recurring.json")

# Add common subscriptions
manager.add(RecurringExpense(
    name="Netflix",
    category=ExpenseCategory.SUBSCRIPTIONS,
    amount=Decimal("15.99"),
    frequency=RecurrenceFrequency.MONTHLY,
    day_of_month=15,
))

manager.add(RecurringExpense(
    name="Spotify",
    category=ExpenseCategory.SUBSCRIPTIONS,
    amount=Decimal("9.99"),
    frequency=RecurrenceFrequency.MONTHLY,
    day_of_month=1,
))

manager.add(RecurringExpense(
    name="Rent",
    category=ExpenseCategory.HOUSING,
    amount=Decimal("1500.00"),
    frequency=RecurrenceFrequency.MONTHLY,
    day_of_month=1,
))

# Calculate totals
monthly = manager.calculate_monthly_total()
print(f"Monthly recurring: ${monthly:,.2f}")
print(f"Annual estimate:   ${monthly * 12:,.2f}")

# Generate entries for January
entries = manager.generate_for_month(1, 2025)
print(f"\nGenerated {len(entries)} entries for January")

# Add to budget
from spreadsheet_dl import OdsEditor

editor = OdsEditor("budget_2025_01.ods")
for entry in entries:
    editor.append_expense(entry)
editor.save()
```

---

## Custom Theme Example

```python
"""
Create budget with custom theme colors.
"""

from spreadsheet_dl import OdsGenerator

# Use built-in theme
generator = OdsGenerator(theme="corporate")
generator.create_budget_spreadsheet("corporate_budget.ods")

# Or use high contrast for accessibility
generator = OdsGenerator(theme="high_contrast")
generator.create_budget_spreadsheet("accessible_budget.ods")
```

---

## Analytics Dashboard Example

```python
"""
Generate analytics dashboard data.
"""

from spreadsheet_dl import generate_dashboard, BudgetAnalyzer

# Get dashboard data
data = generate_dashboard("budget_2025_01.ods")

print(f"Status: {data['budget_status']}")
print(f"Message: {data['status_message']}")
print()
print(f"Total Budget:     ${data['total_budget']:,.2f}")
print(f"Total Spent:      ${data['total_spent']:,.2f}")
print(f"Days Remaining:   {data['days_remaining']}")
print(f"Daily Budget:     ${data['daily_budget_remaining']:,.2f}")

print("\nTop Spending:")
for cat, amount in data['top_spending'][:5]:
    print(f"  {cat}: ${amount:,.2f}")

if data['alerts']:
    print("\nAlerts:")
    for alert in data['alerts']:
        print(f"  ! {alert}")

if data['recommendations']:
    print("\nRecommendations:")
    for rec in data['recommendations']:
        print(f"  - {rec}")
```

---

## Alert Configuration Example

```python
"""
Configure custom budget alerts.
"""

from spreadsheet_dl import check_budget_alerts, AlertConfig

config = AlertConfig(
    budget_warning_threshold=75.0,  # Warn at 75% used
    budget_critical_threshold=90.0, # Critical at 90%
    large_transaction_threshold=200.0,  # Flag $200+ transactions
    watched_categories=["Dining Out", "Entertainment"],
)

alerts = check_budget_alerts("budget_2025_01.ods", config)

for alert in alerts:
    print(f"[{alert.severity.value}] {alert.title}")
    print(f"  {alert.message}")
    if alert.recommendation:
        print(f"  Recommendation: {alert.recommendation}")
    print()
```
