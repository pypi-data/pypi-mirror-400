# 01_basics - Getting Started with SpreadsheetDL

Welcome to the basics! This section teaches fundamental concepts for working with SpreadsheetDL.

## Prerequisites

- Python 3.9 or higher
- SpreadsheetDL installed:

  ```bash
  uv add spreadsheet-dl
  # or
  uv pip install spreadsheet-dl
  ```

## Learning Objectives

By completing these examples, you'll learn how to:

1. **Create spreadsheets** - Generate ODS files programmatically
2. **Define budget structures** - Set up categories and allocations
3. **Add expense entries** - Populate spreadsheets with data
4. **Import from CSV** - Convert existing data to spreadsheets
5. **Use progress indicators** - Show feedback for long operations

## Examples in This Section

### 01_hello_budget.py

**What it does**: Creates your first budget spreadsheet with sample data

**Concepts covered**:

- Basic OdsGenerator usage
- Creating monthly budgets
- Expense categories and entries
- Budget allocations
- File output

**Run it**:

```bash
uv run python examples/01_basics/01_hello_budget.py
```

**Expected output**: `output/budget_2025_01.ods`

---

### 02_create_custom_budget.py

**What it does**: Build a custom budget with your own categories

**Concepts covered**:

- Custom expense categories
- Manual budget allocation setup
- Decimal precision for currency
- Date handling
- File path management

**Run it**:

```bash
uv run python examples/01_basics/02_create_custom_budget.py
```

**Expected output**: `output/custom_budget_2025_01.ods`

---

### 03_import_csv.py

**What it does**: Import expense data from CSV files

**Concepts covered**:

- CSV parsing with pandas
- Data validation
- Category mapping
- Error handling
- Batch data import

**Run it**:

```bash
uv run python examples/01_basics/03_import_csv.py
```

**Expected output**: `output/imported_budget_2025_01.ods`

**Note**: Requires a CSV file. Example CSV format:

```csv
Date,Category,Description,Amount
2025-01-15,Groceries,Weekly shopping,125.50
2025-01-16,Transportation,Gas,45.00
```

---

### 04_progress_indicators.py

**What it does**: Show progress for long-running operations

**Concepts covered**:

- Progress callback functions
- Real-time feedback
- Large dataset handling
- User experience considerations

**Run it**:

```bash
uv run python examples/01_basics/04_progress_indicators.py
```

**Expected output**: `output/large_budget.ods` with progress displayed

## Key Concepts

### OdsGenerator

The main class for creating spreadsheets:

```python
from spreadsheet_dl.ods_generator import OdsGenerator

generator = OdsGenerator()
output_path = generator.create_budget_spreadsheet(
    output_path=Path("output/budget.ods"),
    month=1,
    year=2025,
    expenses=expense_list,
    budget_allocations=allocation_list
)
```

### ExpenseEntry

Represents a single expense:

```python
from spreadsheet_dl.ods_generator import ExpenseEntry, ExpenseCategory
from decimal import Decimal
from datetime import date

expense = ExpenseEntry(
    date=date(2025, 1, 15),
    category=ExpenseCategory.GROCERIES,
    description="Weekly shopping",
    amount=Decimal("125.50")
)
```

### BudgetAllocation

Sets spending limits for categories:

```python
from spreadsheet_dl.ods_generator import BudgetAllocation, ExpenseCategory
from decimal import Decimal

allocation = BudgetAllocation(
    category=ExpenseCategory.GROCERIES,
    monthly_budget=Decimal("600.00")
)
```

## Estimated Time

- **Quick review**: 15 minutes (read code, run examples)
- **Hands-on practice**: 30-45 minutes (modify examples, create own budgets)

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'spreadsheet_dl'`
**Solution**: Install SpreadsheetDL with `uv add spreadsheet-dl` or `uv pip install spreadsheet-dl`

**Issue**: `FileNotFoundError: [Errno 2] No such file or directory: 'output/...'`
**Solution**: The `output/` directory is created automatically. If issues persist, create it manually:

```bash
mkdir -p output
```

**Issue**: Decimal values showing as `Decimal('125.50')` instead of `125.50`
**Solution**: Always use `Decimal("125.50")` (string) not `Decimal(125.50)` (float) for currency

## Next Steps

Once you're comfortable with basics, move on to:

**[02_formulas](../02_formulas/)** - Learn how to analyze budget data and generate reports

## Additional Resources

- [SpreadsheetDL Documentation](https://lair-click-bats.github.io/spreadsheet-dl/)
- [API Reference - OdsGenerator](../../docs/api/_builder/core.md)
- [API Reference - Models](../../docs/api/_builder/models.md)

## Questions?

- Check the [main documentation](https://lair-click-bats.github.io/spreadsheet-dl/)
- Open an issue on GitHub
- Review the API reference docs
