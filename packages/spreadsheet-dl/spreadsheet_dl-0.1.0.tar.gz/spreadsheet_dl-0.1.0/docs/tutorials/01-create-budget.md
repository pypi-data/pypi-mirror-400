# Tutorial 1: Create a Monthly Budget

Learn how to create a comprehensive monthly budget from scratch using SpreadsheetDL.

## What You'll Learn

- Set up budget categories and allocations
- Define income sources
- Create a functional budget spreadsheet
- Customize budget amounts for your needs
- Use the theme system

## Prerequisites

- SpreadsheetDL installed (`uv pip install spreadsheet-dl`)
- Basic understanding of budgeting concepts
- Text editor or Python IDE

## Step 1: Create a Basic Budget

Let's start with the simplest approach - using the CLI:

```bash
# Create a directory for your budgets
mkdir -p ~/budgets

# Generate budget for current month
spreadsheet-dl generate -o ~/budgets/
```

This creates `budget_2026_01.ods` with:

- Pre-configured expense categories
- Empty expense log sheet
- Summary sheet with formulas
- Default budget allocations

**Open the file** in LibreOffice Calc or Excel to see what was created!

## Step 2: Customize Budget Allocations

Let's create a budget tailored to your specific needs using Python:

```python
#!/usr/bin/env python3
"""Create a customized monthly budget."""

from pathlib import Path
from decimal import Decimal
from spreadsheet_dl import OdsGenerator, BudgetAllocation, ExpenseCategory

# Define your monthly budget allocations
my_budget = [
    # Housing (rent/mortgage, insurance, utilities)
    BudgetAllocation(
        ExpenseCategory.HOUSING,
        Decimal("1800.00"),
        notes="Rent + renters insurance"
    ),
    BudgetAllocation(
        ExpenseCategory.UTILITIES,
        Decimal("250.00"),
        notes="Electric, gas, water, internet"
    ),

    # Food
    BudgetAllocation(
        ExpenseCategory.GROCERIES,
        Decimal("600.00"),
        notes="$150/week for 4 people"
    ),
    BudgetAllocation(
        ExpenseCategory.DINING_OUT,
        Decimal("200.00"),
        notes="Restaurants, takeout"
    ),

    # Transportation
    BudgetAllocation(
        ExpenseCategory.TRANSPORTATION,
        Decimal("450.00"),
        notes="Car payment $300 + gas $150"
    ),

    # Healthcare
    BudgetAllocation(
        ExpenseCategory.HEALTHCARE,
        Decimal("200.00"),
        notes="Insurance premiums, copays"
    ),

    # Personal & Lifestyle
    BudgetAllocation(
        ExpenseCategory.ENTERTAINMENT,
        Decimal("150.00"),
        notes="Movies, hobbies, subscriptions"
    ),
    BudgetAllocation(
        ExpenseCategory.CLOTHING,
        Decimal("100.00")
    ),
    BudgetAllocation(
        ExpenseCategory.PERSONAL,
        Decimal("75.00")
    ),

    # Financial
    BudgetAllocation(
        ExpenseCategory.SAVINGS,
        Decimal("800.00"),
        notes="Emergency fund + retirement"
    ),
    BudgetAllocation(
        ExpenseCategory.DEBT_PAYMENT,
        Decimal("300.00"),
        notes="Student loan minimum payment"
    ),

    # Miscellaneous
    BudgetAllocation(
        ExpenseCategory.MISCELLANEOUS,
        Decimal("75.00")
    ),
]

# Calculate total
total = sum(alloc.amount for alloc in my_budget)
print(f"Total monthly budget: ${total:,.2f}")

# Create the budget spreadsheet
output_dir = Path.home() / "budgets"
output_dir.mkdir(exist_ok=True)

generator = OdsGenerator()
budget_path = generator.create_budget_spreadsheet(
    output_dir / "my_budget_2026_01.ods",
    month=1,
    year=2026,
    budget_allocations=my_budget
)

print(f"Budget created: {budget_path}")
```

Save this as `create_my_budget.py` and run:

```bash
python create_my_budget.py
```

## Step 3: Add Income Tracking

Let's enhance the budget to track income sources:

```python
from datetime import date
from decimal import Decimal
from pathlib import Path
from spreadsheet_dl import create_spreadsheet, formula

# Create a budget with income tracking
builder = create_spreadsheet(theme="default")

# Income sheet
f = formula()
builder.sheet("Income") \
    .column("Date", width="2.5cm", type="date") \
    .column("Source", width="3cm") \
    .column("Amount", width="2.5cm", type="currency") \
    .column("Notes", width="4cm") \
    .header_row(style="header_primary") \
    .row() \
        .cell(date(2026, 1, 5)) \
        .cell("Salary") \
        .cell(Decimal("3500.00")) \
        .cell("Bi-weekly paycheck") \
    .row() \
        .cell(date(2026, 1, 15)) \
        .cell("Freelance") \
        .cell(Decimal("800.00")) \
        .cell("Web design project") \
    .row() \
        .cell(date(2026, 1, 19)) \
        .cell("Salary") \
        .cell(Decimal("3500.00")) \
        .cell("Bi-weekly paycheck")

# Add total row
builder.sheet("Income") \
    .row().cell("").cell("TOTAL").cell(
        formula=f.sum(f.range("C2", "C10"))
    ).cell("")

# Save
builder.save(Path.home() / "budgets" / "budget_with_income.ods")
print("Budget with income tracking created!")
```

## Step 4: Apply Themes

Make your budget look professional with themes:

```bash
# Corporate theme (navy blue, professional)
spreadsheet-dl generate -o ~/budgets/ --theme corporate

# Minimal theme (clean, distraction-free)
spreadsheet-dl generate -o ~/budgets/ --theme minimal

# Dark theme (dark mode for night work)
spreadsheet-dl generate -o ~/budgets/ --theme dark
```

**In Python:**

```python
from spreadsheet_dl import OdsGenerator

# Create with corporate theme
generator = OdsGenerator(theme="corporate")
generator.create_budget_spreadsheet(
    "corporate_budget.ods",
    month=1,
    year=2026
)
```

## Step 5: Verify Your Budget

Once created, verify the budget is working correctly:

```bash
# Analyze the budget
spreadsheet-dl analyze ~/budgets/my_budget_2026_01.ods

# Should show:
# Total Budget:  $5,000.00
# Total Spent:   $0.00
# Remaining:     $5,000.00
# Used:          0.0%
```

## Complete Example

Here's a complete script that creates a family budget:

```python
#!/usr/bin/env python3
"""Create a comprehensive family budget."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from spreadsheet_dl import (
    OdsGenerator,
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
)

def create_family_budget():
    """Create a budget for a family of four."""

    # Budget allocations based on $6,000/month income
    allocations = [
        # Fixed expenses (50% = $3,000)
        BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1650"),
                        notes="Rent"),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("300")),
        BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("700"),
                        notes="$175/week"),
        BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("350"),
                        notes="Car payment + gas"),

        # Flexible expenses (30% = $1,800)
        BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("300")),
        BudgetAllocation(ExpenseCategory.ENTERTAINMENT, Decimal("200")),
        BudgetAllocation(ExpenseCategory.CLOTHING, Decimal("150")),
        BudgetAllocation(ExpenseCategory.PERSONAL, Decimal("100")),
        BudgetAllocation(ExpenseCategory.EDUCATION, Decimal("1050"),
                        notes="Childcare + tuition"),

        # Savings & debt (20% = $1,200)
        BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("900"),
                        notes="Emergency fund + retirement"),
        BudgetAllocation(ExpenseCategory.DEBT_PAYMENT, Decimal("300")),
    ]

    # Pre-populate with month-start expenses
    expenses = [
        ExpenseEntry(
            date=date(2026, 1, 1),
            category=ExpenseCategory.HOUSING,
            description="January rent",
            amount=Decimal("1650.00")
        ),
        ExpenseEntry(
            date=date(2026, 1, 1),
            category=ExpenseCategory.EDUCATION,
            description="Childcare - January",
            amount=Decimal("800.00")
        ),
    ]

    # Create budget
    output_dir = Path.home() / "budgets"
    output_dir.mkdir(exist_ok=True)

    generator = OdsGenerator(theme="default")
    budget_path = generator.create_budget_spreadsheet(
        output_dir / "family_budget_2026_01.ods",
        month=1,
        year=2026,
        budget_allocations=allocations,
        expenses=expenses
    )

    # Print summary
    total_budget = sum(a.amount for a in allocations)
    total_spent = sum(e.amount for e in expenses)

    print(f"Family Budget Created!")
    print(f"Path: {budget_path}")
    print(f"\nSummary:")
    print(f"  Total Budget: ${total_budget:,.2f}")
    print(f"  Pre-populated expenses: ${total_spent:,.2f}")
    print(f"  Remaining: ${total_budget - total_spent:,.2f}")
    print(f"\nNext: Add daily expenses with:")
    print(f"  spreadsheet-dl expense <amount> <description>")

if __name__ == "__main__":
    create_family_budget()
```

## Expected Output

Your budget spreadsheet should have:

1. **Expense Log Sheet**
   - Columns: Date, Category, Description, Amount, Notes
   - 50+ empty rows for data entry
   - Clean formatting with alternating row colors

2. **Summary Sheet**
   - Category breakdown
   - Budget vs. Actual comparison
   - Remaining amounts
   - Progress bars (conditional formatting)

3. **Budget Sheet**
   - Category list
   - Allocated amounts
   - Notes column

4. **Formulas**
   - Auto-sum expenses by category
   - Calculate remaining budget
   - Percentage used indicators

## Tips for Success

1. **Start Simple** - Begin with major categories, add detail later
2. **Be Realistic** - Look at 3 months of past spending for accurate allocations
3. **Include Buffer** - Add 5-10% miscellaneous for unexpected expenses
4. **Monthly Review** - Adjust allocations based on actual spending
5. **Use Notes** - Document why you set specific amounts

## Troubleshooting

**Budget totals don't match income?**

- Ensure all allocations sum to your monthly income
- Check the calculations in the Summary sheet

**Categories missing?**

- Check available categories: `spreadsheet-dl category list`
- Add custom categories: `spreadsheet-dl category add "Pet Care"`

**Formulas not calculating?**

- Open in LibreOffice Calc (better ODS support than Excel)
- Enable automatic calculation in your spreadsheet app

## Next Steps

- **[Tutorial 2: Track Expenses](02-track-expenses.md)** - Daily expense tracking
- **[Tutorial 3: Import Bank Data](03-import-bank-data.md)** - Automate from bank CSV
- **[Best Practices](../guides/best-practices.md)** - Budget management tips

## Additional Resources

- [Theme System](../index.md)
- [Python API Reference](../api/index.md)
