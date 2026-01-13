# ODS Generator API Reference

Generate ODS spreadsheets for budget tracking with formatting and formulas.

## Overview

The ODS Generator module creates formatted ODS (OpenDocument Spreadsheet) files for family budget tracking. It generates expense tracking sheets, budget allocation sheets, and summary sheets with formulas and conditional formatting.

Features:

- Expense tracking with dates, categories, and amounts
- Budget allocation and variance tracking
- Summary sheets with SUM formulas
- Conditional formatting for over-budget alerts
- Theme-based styling support
- Mobile-compatible formatting (Collabora Office)
- Compatible with LibreOffice, Apache OpenOffice, and Excel

## Enumerations

### ExpenseCategory

Standard expense categories for budget tracking.

```python
from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory

ExpenseCategory.HOUSING            # Rent, mortgage
ExpenseCategory.UTILITIES          # Electric, water, gas
ExpenseCategory.GROCERIES          # Food shopping
ExpenseCategory.TRANSPORTATION     # Gas, public transit
ExpenseCategory.HEALTHCARE         # Doctor, pharmacy
ExpenseCategory.INSURANCE          # Health, auto, home
ExpenseCategory.ENTERTAINMENT      # Movies, hobbies
ExpenseCategory.DINING_OUT         # Restaurants, cafes
ExpenseCategory.CLOTHING           # Clothes, shoes
ExpenseCategory.PERSONAL           # Hair, hygiene
ExpenseCategory.EDUCATION          # Classes, books
ExpenseCategory.SAVINGS            # Savings contributions
ExpenseCategory.DEBT_PAYMENT       # Credit card, loans
ExpenseCategory.GIFTS              # Gifts for others
ExpenseCategory.SUBSCRIPTIONS      # Services, memberships
ExpenseCategory.MISCELLANEOUS      # Other expenses

# Get category value for display
print(ExpenseCategory.GROCERIES.value)  # -> "Groceries"
```

---

## Data Classes

### ExpenseEntry

Single expense entry.

```python
from spreadsheet_dl.domains.finance.ods_generator import ExpenseEntry, ExpenseCategory
from datetime import date
from decimal import Decimal

expense = ExpenseEntry(
    date=date(2024, 1, 15),
    category=ExpenseCategory.GROCERIES,
    description="Whole Foods Market",
    amount=Decimal("125.50"),
    notes="Weekly grocery shopping"
)
```

**Attributes:**

- `date: date` - Date of expense
- `category: ExpenseCategory` - Category enum
- `description: str` - Description of expense
- `amount: Decimal` - Amount spent
- `notes: str` - Additional notes (optional)

---

### BudgetAllocation

Budget allocation for a category.

```python
from spreadsheet_dl.domains.finance.ods_generator import BudgetAllocation, ExpenseCategory
from decimal import Decimal

allocation = BudgetAllocation(
    category=ExpenseCategory.GROCERIES,
    monthly_budget=Decimal("500.00"),
    notes="Food budget for family of 4"
)
```

**Attributes:**

- `category: ExpenseCategory` - Category enum
- `monthly_budget: Decimal` - Allocated budget
- `notes: str` - Additional notes (optional)

---

## ODS Generator Class

### OdsGenerator

Generate ODS spreadsheets for budget tracking.

```python
from spreadsheet_dl.domains.finance.ods_generator import OdsGenerator
from pathlib import Path

# Create with default styling
generator = OdsGenerator()

# Create with theme
generator = OdsGenerator(theme="corporate")

# Create with custom theme directory
generator = OdsGenerator(
    theme="minimal",
    theme_dir="/path/to/themes"
)
```

**Constructor Parameters:**

- `theme: str | Theme | None` - Theme name or Theme object. Options: "default", "corporate", "minimal", "dark", "high_contrast"
- `theme_dir: Path | str | None` - Directory containing theme YAML files

---

### Methods

#### `create_budget_spreadsheet(output_path, *, month=None, year=None, budget_allocations=None, expenses=None) -> Path`

Create a complete budget spreadsheet.

```python
from spreadsheet_dl.domains.finance.ods_generator import (
    OdsGenerator,
    ExpenseCategory,
    BudgetAllocation,
    ExpenseEntry,
)
from pathlib import Path
from datetime import date
from decimal import Decimal

generator = OdsGenerator(theme="corporate")

# Define budget allocations
allocations = [
    BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("500")),
    BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
    BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("150")),
]

# Define expenses
expenses = [
    ExpenseEntry(
        date=date(2024, 1, 5),
        category=ExpenseCategory.GROCERIES,
        description="Trader Joe's",
        amount=Decimal("125.50")
    ),
    ExpenseEntry(
        date=date(2024, 1, 10),
        category=ExpenseCategory.UTILITIES,
        description="Electric bill",
        amount=Decimal("95.00")
    ),
]

# Generate spreadsheet
output = generator.create_budget_spreadsheet(
    output_path="budget_jan_2024.ods",
    month=1,
    year=2024,
    budget_allocations=allocations,
    expenses=expenses
)

print(f"Generated: {output}")
```

**Parameters:**

- `output_path: Path | str` - Path to save ODS file
- `month: int | None` - Month number (1-12), for display
- `year: int | None` - Year, for display
- `budget_allocations: Sequence[BudgetAllocation] | None` - Budget allocations (optional)
- `expenses: Sequence[ExpenseEntry] | None` - Expenses (optional)

**Returns:** Path to created ODS file

**Raises:** OSError if output directory doesn't exist

---

### Generated Spreadsheet Structure

The created spreadsheet contains:

#### Budget Sheet

| Header         | Description                                 |
| -------------- | ------------------------------------------- |
| Category       | Expense category name                       |
| Monthly Budget | Allocated budget                            |
| Expenses       | SUM of expenses in category                 |
| Remaining      | Formula: Monthly Budget - Expenses          |
| % Used         | Formula: (Expenses / Monthly Budget) \* 100 |

Conditional formatting:

- Green: Under budget
- Orange: 80-100% of budget
- Red: Over budget

#### Expenses Sheet

| Header      | Description             |
| ----------- | ----------------------- |
| Date        | Expense date            |
| Category    | Expense category        |
| Description | Transaction description |
| Amount      | Amount spent            |
| Notes       | Additional notes        |

#### Summary Sheet

- Total Budget: Sum of all allocations
- Total Spent: Sum of all expenses
- Total Remaining: Total Budget - Total Spent
- % of Budget Used: (Total Spent / Total Budget) \* 100

---

## Convenience Functions

### create_monthly_budget(output_path, \*, month=None, year=None, theme=None) -> Path

Create a blank monthly budget spreadsheet.

```python
from spreadsheet_dl.domains.finance.ods_generator import create_monthly_budget
from pathlib import Path

# Create with defaults
output = create_monthly_budget("budget.ods")

# Specify month and year
output = create_monthly_budget(
    "budget_march_2024.ods",
    month=3,
    year=2024,
    theme="corporate"
)

print(f"Created: {output}")
```

**Parameters:**

- `output_path: Path | str` - Path to save ODS file
- `month: int | None` - Month number (1-12)
- `year: int | None` - Year
- `theme: str | None` - Theme name

**Returns:** Path to created ODS file

---

## Complete Example

```python
from spreadsheet_dl.domains.finance.ods_generator import (
    OdsGenerator,
    create_monthly_budget,
    ExpenseCategory,
    BudgetAllocation,
    ExpenseEntry,
)
from pathlib import Path
from datetime import date
from decimal import Decimal

# Method 1: Create blank budget
blank_budget = create_monthly_budget(
    "blank_budget.ods",
    month=1,
    year=2024,
    theme="corporate"
)
print(f"Blank budget: {blank_budget}")

# Method 2: Create with data
generator = OdsGenerator(theme="minimal")

# Define budget for the month
budget = [
    BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1500")),
    BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
    BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600")),
    BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("300")),
    BudgetAllocation(ExpenseCategory.ENTERTAINMENT, Decimal("200")),
]

# Log expenses
expenses = [
    ExpenseEntry(
        date=date(2024, 1, 1),
        category=ExpenseCategory.HOUSING,
        description="January rent",
        amount=Decimal("1500")
    ),
    ExpenseEntry(
        date=date(2024, 1, 3),
        category=ExpenseCategory.GROCERIES,
        description="Whole Foods",
        amount=Decimal("125.50")
    ),
    ExpenseEntry(
        date=date(2024, 1, 5),
        category=ExpenseCategory.GROCERIES,
        description="Trader Joe's",
        amount=Decimal("89.25")
    ),
    ExpenseEntry(
        date=date(2024, 1, 7),
        category=ExpenseCategory.TRANSPORTATION,
        description="Gas",
        amount=Decimal("50.00")
    ),
    ExpenseEntry(
        date=date(2024, 1, 10),
        category=ExpenseCategory.UTILITIES,
        description="Electric bill",
        amount=Decimal("125.50")
    ),
    ExpenseEntry(
        date=date(2024, 1, 14),
        category=ExpenseCategory.ENTERTAINMENT,
        description="Movie tickets",
        amount=Decimal("30.00")
    ),
]

# Generate budget
output = generator.create_budget_spreadsheet(
    "january_budget.ods",
    month=1,
    year=2024,
    budget_allocations=budget,
    expenses=expenses
)

print(f"Generated budget: {output}")

# Verify file was created
if Path(output).exists():
    size_kb = Path(output).stat().st_size / 1024
    print(f"File size: {size_kb:.1f} KB")
```

---

## Styling and Themes

### Available Themes

- **default** - Simple, clean design with basic formatting
- **corporate** - Professional appearance with blues and grays
- **minimal** - Minimalist with subtle colors
- **dark** - Dark theme with light text (for dark mode)
- **high_contrast** - High contrast for accessibility

### Using Themes

```python
# Default theme (hardcoded styles)
generator = OdsGenerator()

# Named theme
generator = OdsGenerator(theme="corporate")

# Theme from custom directory
generator = OdsGenerator(
    theme="custom",
    theme_dir="/home/user/my_themes"
)
```

### Theme Files

Themes are defined in YAML files in the theme directory:

```yaml
# corporate.yaml
name: Corporate Theme
colors:
  primary: '#003366'
  header: '#0066CC'
  success: '#00CC00'
  warning: '#FFCC00'
  error: '#FF0000'

styles:
  header:
    font_weight: bold
    background_color: '#003366'
    font_color: '#FFFFFF'
  data:
    background_color: '#F0F0F0'
```

---

## Conditional Formatting

The generated spreadsheets include conditional formatting for budget status:

- **Green Background**: Under budget (0-80%)
- **Yellow Background**: Warning zone (80-100%)
- **Red Background**: Over budget (>100%)

This helps users quickly identify:

- Categories within budget
- Categories approaching limit
- Categories that exceeded budget

---

## Calculation Formulas

Formulas automatically generated:

### Remaining Budget

```
Monthly Budget - SUM(Expenses)
```

### Percentage Used

```
(SUM(Expenses) / Monthly Budget) * 100
```

### Total Remaining

```
SUM(Monthly Budget) - SUM(Expenses)
```

### Budget Summary

```
Total Budget: SUM(all allocations)
Total Spent: SUM(all expenses)
Remaining: Total Budget - Total Spent
Percent Used: (Total Spent / Total Budget) * 100
```

---

## Mobile Compatibility

ODS files created by OdsGenerator are compatible with:

- **Collabora Online** (via Nextcloud)
- **LibreOffice Mobile** (Android)
- **OnlyOffice**
- **Microsoft Excel** (after conversion)

Mobile editing works best with:

- Simple, flat structure
- Moderate number of rows/columns
- Clear formatting without complex styles

---

## File Format Details

- **Format**: ODS (OpenDocument Spreadsheet)
- **Version**: 1.3 compatible
- **Encoding**: UTF-8
- **Size**: Typically 15-50 KB (depending on data)
- **Compatibility**: LibreOffice 3.0+, OpenOffice 2.0+

---

## Performance Considerations

Generation time for various data sizes:

- 100 expenses: < 100 ms
- 1000 expenses: < 500 ms
- 10000 expenses: < 3 seconds

Memory usage: ~5-10 MB for typical budgets

---

## Error Handling

```python
from spreadsheet_dl.domains.finance.ods_generator import OdsGenerator
import logging

logging.basicConfig(level=logging.INFO)

try:
    generator = OdsGenerator(theme="nonexistent")
except Exception as e:
    print(f"Theme loading failed: {e}")

try:
    output = generator.create_budget_spreadsheet(
        "/read-only/budget.ods",  # Can't write here
        month=1,
        year=2024
    )
except OSError as e:
    print(f"Failed to create file: {e}")
```

---

## Backwards Compatibility

The module is also accessible via:

```python
# Old import path (shim for backwards compatibility)
from spreadsheet_dl.ods_generator import OdsGenerator

# New import path (recommended)
from spreadsheet_dl.domains.finance.ods_generator import OdsGenerator
```

Both imports work identically.
