# Tutorial 2: Track Expenses

Learn how to effectively track daily expenses using SpreadsheetDL's CLI and Python API.

## What You'll Learn

- Add expenses via command line
- Categorize transactions accurately
- View spending by category
- Track against your budget
- Edit and correct expense entries

## Prerequisites

- Completed [Tutorial 1: Create a Budget](01-create-budget.md)
- A budget file created (`budget_2026_01.ods`)
- Basic command-line familiarity

## Quick Reference

```bash
# Add expense (simplest form)
spreadsheet-dl expense 25.50 "Lunch at cafe"

# Add with specific category
spreadsheet-dl expense 150.00 "Whole Foods" -c Groceries

# Add with custom date
spreadsheet-dl expense 89.99 "Electric bill" -d 2026-01-15

# Preview without saving
spreadsheet-dl expense 50.00 "Test" --dry-run

# Add to specific file
spreadsheet-dl expense 35.00 "Gas" -f ~/budgets/budget_2026_01.ods
```

## Step 1: Add Your First Expense

Let's add a grocery shopping trip:

```bash
# Navigate to your budgets directory
cd ~/budgets

# Add the expense
spreadsheet-dl expense 125.50 "Weekly groceries at Safeway" -c Groceries
```

Output:

```
Using: budget_2026_01.ods

Expense added successfully:
  File:        budget_2026_01.ods
  Row:         3
  Date:        2026-01-03
  Category:    Groceries
  Description: Weekly groceries at Safeway
  Amount:      $125.50
```

**What happened:**

1. CLI found your most recent budget file
2. Added the expense to the "Expense Log" sheet
3. Formulas automatically updated the summary

## Step 2: Use Auto-Categorization

SpreadsheetDL can automatically categorize based on description:

```bash
# These will auto-categorize correctly
spreadsheet-dl expense 15.75 "Chipotle"         # -> Dining Out
spreadsheet-dl expense 45.00 "Shell gas"        # -> Transportation
spreadsheet-dl expense 12.99 "Netflix"          # -> Entertainment
spreadsheet-dl expense 85.00 "Electric bill"    # -> Utilities
```

The categorizer uses keywords to determine categories:

- "grocery", "safeway", "kroger" → Groceries
- "restaurant", "cafe", "lunch" → Dining Out
- "gas", "fuel", "uber" → Transportation
- "netflix", "spotify", "movie" → Entertainment

**Override auto-categorization:**

```bash
# Force specific category
spreadsheet-dl expense 50.00 "Amazon Prime" -c Shopping
```

## Step 3: Track Daily Spending

Let's track a full day's expenses:

```bash
# Morning coffee
spreadsheet-dl expense 4.50 "Starbucks coffee"

# Lunch
spreadsheet-dl expense 12.95 "Subway sandwich"

# Afternoon
spreadsheet-dl expense 65.00 "Target - household items" -c Shopping

# Evening
spreadsheet-dl expense 48.50 "Dinner at Olive Garden" -c "Dining Out"

# Fuel
spreadsheet-dl expense 52.00 "Gas at Chevron" -c Transportation
```

## Step 4: Add Back-Dated Expenses

Forgot to log yesterday's expenses? No problem:

```bash
# Add expense for specific date
spreadsheet-dl expense 125.00 "Doctor copay" -d 2026-01-02 -c Healthcare

# Add expense from last week
spreadsheet-dl expense 89.99 "Shoes" -d 2025-12-28 -c Clothing
```

**Using Python for batch entry:**

```python
from datetime import date, timedelta
from decimal import Decimal
from spreadsheet_dl import OdsEditor, ExpenseEntry, ExpenseCategory

# Open budget
editor = OdsEditor("budget_2026_01.ods")

# Define a week's worth of expenses
expenses = [
    ExpenseEntry(
        date=date(2026, 1, 1),
        category=ExpenseCategory.GROCERIES,
        description="Walmart - groceries",
        amount=Decimal("145.50")
    ),
    ExpenseEntry(
        date=date(2026, 1, 2),
        category=ExpenseCategory.DINING_OUT,
        description="Pizza delivery",
        amount=Decimal("32.00")
    ),
    ExpenseEntry(
        date=date(2026, 1, 3),
        category=ExpenseCategory.ENTERTAINMENT,
        description="Movie tickets",
        amount=Decimal("28.00")
    ),
    ExpenseEntry(
        date=date(2026, 1, 4),
        category=ExpenseCategory.TRANSPORTATION,
        description="Gas - Shell",
        amount=Decimal("48.00")
    ),
    ExpenseEntry(
        date=date(2026, 1, 5),
        category=ExpenseCategory.UTILITIES,
        description="Internet bill",
        amount=Decimal("79.99")
    ),
]

# Add all expenses
for expense in expenses:
    row_num = editor.append_expense(expense)
    print(f"Added: {expense.description} (${expense.amount}) at row {row_num}")

# Save changes
editor.save()
print(f"\nAdded {len(expenses)} expenses successfully!")
```

## Step 5: View Spending Summary

Check your spending by category:

```bash
# View full summary
spreadsheet-dl analyze budget_2026_01.ods
```

Output:

```
Budget Analysis: budget_2026_01.ods
----------------------------------------
Total Budget:  $5,000.00
Total Spent:   $823.43
Remaining:     $4,176.57
Used:          16.5%

Category Breakdown:
  Groceries:       $270.50 / $600.00  (45.1%)
  Dining Out:      $109.20 / $200.00  (54.6%)
  Transportation:  $100.00 / $450.00  (22.2%)
  Entertainment:   $40.99  / $150.00  (27.3%)
  Utilities:       $165.99 / $250.00  (66.4%)
```

**Filter by category:**

```bash
# View only grocery spending
spreadsheet-dl analyze budget_2026_01.ods --category Groceries

# Output:
# Category: Groceries
# Total: $270.50
# Transactions: 3
```

**Filter by date range:**

```bash
# View spending for first week
spreadsheet-dl analyze budget_2026_01.ods \
  --start-date 2026-01-01 \
  --end-date 2026-01-07
```

## Step 6: Use Python for Custom Queries

```python
from spreadsheet_dl import BudgetAnalyzer

# Load budget
analyzer = BudgetAnalyzer("budget_2026_01.ods")

# Get category breakdown
by_category = analyzer.get_category_breakdown()

print("Spending by Category:")
for category, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
    print(f"  {category:20} ${amount:>8.2f}")

# Find highest expense
expenses_df = analyzer.expenses
if not expenses_df.empty:
    max_expense = expenses_df.loc[expenses_df['Amount'].idxmax()]
    print(f"\nHighest expense: ${max_expense['Amount']:.2f}")
    print(f"  Category: {max_expense['Category']}")
    print(f"  Description: {max_expense['Description']}")

# Get summary statistics
summary = analyzer.get_summary()
print(f"\nBudget Summary:")
print(f"  Total Budget: ${summary.total_budget:,.2f}")
print(f"  Total Spent: ${summary.total_spent:,.2f}")
print(f"  Percent Used: {summary.percent_used:.1f}%")
print(f"  Daily Average: ${summary.total_spent / 7:.2f}")  # First week
```

## Step 7: Preview Before Saving

Always preview large or unusual expenses:

```bash
# Preview the expense
spreadsheet-dl expense 1299.00 "New laptop" --dry-run

# Output shows what would be added without actually saving:
# [DRY RUN] Would add expense:
#   File:        budget_2026_01.ods
#   Date:        2026-01-03
#   Category:    Electronics
#   Description: New laptop
#   Amount:      $1299.00

# If correct, run without --dry-run
spreadsheet-dl expense 1299.00 "New laptop" -c Electronics
```

## Step 8: Track Against Budget Goals

Monitor your progress toward budget targets:

```bash
# Check budget alerts
spreadsheet-dl alerts budget_2026_01.ods
```

Example output:

```
Budget Alerts for budget_2026_01.ods
====================================

WARNING ALERTS:
  [!] Dining Out at 78.5% of budget
      You've spent $157.00 of $200.00 allocated.
      Consider reducing spending in this category.

  [!] Groceries trending over budget
      Based on current pace, you'll spend $850 (41.7% over budget).

RECOMMENDATIONS:
  - Reduce dining out by ~$20/week for remainder of month
  - You're under budget on Entertainment - $89 remaining
  - Great job on Transportation - only 22% used
```

**Get JSON output for scripting:**

```bash
spreadsheet-dl alerts budget_2026_01.ods --json > alerts.json
```

## Step 9: Advanced Python Tracking

Create a custom expense tracking script:

```python
#!/usr/bin/env python3
"""Interactive expense tracker."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from spreadsheet_dl import (
    OdsEditor,
    ExpenseEntry,
    ExpenseCategory,
    TransactionCategorizer,
)

def add_expense_interactive():
    """Interactive expense entry."""

    # Get budget file
    budget_files = list(Path.cwd().glob("budget_*.ods"))
    if not budget_files:
        print("No budget file found in current directory!")
        return

    budget_file = max(budget_files, key=lambda p: p.stat().st_mtime)
    print(f"Using budget: {budget_file.name}\n")

    # Get expense details
    try:
        amount_str = input("Amount: $")
        amount = Decimal(amount_str)

        description = input("Description: ")

        # Suggest category
        categorizer = TransactionCategorizer()
        suggested = categorizer.categorize(description)
        print(f"Suggested category: {suggested.value}")

        use_suggestion = input("Use this category? [Y/n]: ").strip().lower()
        if use_suggestion in ('n', 'no'):
            print("\nAvailable categories:")
            for i, cat in enumerate(ExpenseCategory, 1):
                print(f"  {i}. {cat.value}")
            cat_choice = int(input("Choose category (number): "))
            category = list(ExpenseCategory)[cat_choice - 1]
        else:
            category = suggested

        # Create expense
        expense = ExpenseEntry(
            date=date.today(),
            category=category,
            description=description,
            amount=amount
        )

        # Confirm
        print(f"\nAdding expense:")
        print(f"  {expense.date} | {expense.category.value}")
        print(f"  {expense.description}")
        print(f"  ${expense.amount:.2f}")

        confirm = input("\nConfirm? [Y/n]: ").strip().lower()
        if confirm in ('n', 'no'):
            print("Cancelled.")
            return

        # Add to budget
        editor = OdsEditor(budget_file)
        row_num = editor.append_expense(expense)
        editor.save()

        print(f"\nExpense added at row {row_num}!")

    except (ValueError, KeyboardInterrupt) as e:
        print(f"\nError: {e}")
        return

if __name__ == "__main__":
    print("=== Expense Tracker ===\n")
    add_expense_interactive()
```

Save as `track_expense.py` and run:

```bash
python track_expense.py
```

## Best Practices

1. **Log Daily** - Add expenses at the end of each day while fresh
2. **Be Specific** - "Safeway - week groceries" better than "food"
3. **Round to Cents** - Always include cents for accuracy
4. **Use Consistent Categories** - Stick to standard categories when possible
5. **Review Weekly** - Check spending patterns every week

## Common Patterns

### Morning Routine

```bash
# Add yesterday's expenses in the morning
spreadsheet-dl expense 45.00 "Dinner at restaurant" -d 2026-01-02
spreadsheet-dl expense 8.50 "Coffee shop" -d 2026-01-02
```

### End of Week Batch

```bash
# Review receipts, add in batch with Python script
python batch_add_expenses.py receipts.csv
```

### Monthly Bills

```bash
# Add recurring monthly bills on payment date
spreadsheet-dl expense 1650.00 "Rent" -d 2026-01-01 -c Housing
spreadsheet-dl expense 79.99 "Internet" -d 2026-01-05 -c Utilities
spreadsheet-dl expense 150.00 "Car insurance" -d 2026-01-10 -c Transportation
```

## Troubleshooting

**"No budget file found" error?**

- Make sure you're in the directory with your budget file
- Or specify file explicitly: `-f ~/budgets/budget_2026_01.ods`

**Wrong category assigned?**

- Always specify category for ambiguous descriptions: `-c CategoryName`
- Update auto-categorization rules in Python

**Expense not showing in summary?**

- Verify the expense was added: `spreadsheet-dl analyze budget.ods`
- Check formulas in LibreOffice Calc
- Ensure file was saved after adding expense

## Next Steps

- **[Tutorial 3: Import Bank Data](03-import-bank-data.md)** - Automate expense entry
- **[Tutorial 4: Create Reports](04-create-reports.md)** - Generate spending reports
- **[Best Practices](../guides/best-practices.md)** - Advanced tracking strategies

## Additional Resources

- [Available Expense Categories](../api/ods_generator.md#expensecategory)
- [Custom Categories](../api/categories.md)
- [CLI Reference](../cli.md)
