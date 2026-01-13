# Getting Started with SpreadsheetDL

Welcome to SpreadsheetDL, the universal spreadsheet definition language for Python! This guide will help you get up and running quickly.

## What is SpreadsheetDL?

SpreadsheetDL is a declarative toolkit for creating professional spreadsheets programmatically. Unlike traditional spreadsheet libraries that require cell-by-cell manipulation, SpreadsheetDL lets you define **what** you want, not **how** to build it.

### Key Features

- **Declarative API** - Define structure and styling in code, not cell operations
- **Multi-Format Export** - ODS (native), XLSX, PDF from single definition
- **Type-Safe Formulas** - 60+ functions with circular reference detection
- **Theme System** - 5 built-in themes, YAML-based customization
- **Domain Plugins** - Finance, science, engineering specialized formulas
- **MCP Server** - Native integration with Claude and other AI tools

## Installation

### Using pip (Recommended)

```bash
# Install from PyPI
uv pip install spreadsheet-dl

# Install with security enhancements (recommended)
uv pip install spreadsheet-dl[security]

# Install with all extras
uv pip install spreadsheet-dl[all]
```

### Using uv (For Development)

```bash
# Clone the repository
git clone https://github.com/lair-click-bats/spreadsheet-dl.git
cd spreadsheet-dl

# Install with uv (includes all development dependencies)
uv sync --dev
```

### Verify Installation

```bash
# Check version
spreadsheet-dl --version

# Should output: spreadsheet-dl 0.1.0
```

## Your First Budget Spreadsheet

Let's create a simple monthly budget to track your expenses.

### Step 1: Create a Basic Budget (CLI)

The fastest way to get started is using the command-line interface:

```bash
# Create a budget for the current month
spreadsheet-dl generate -o ./budgets/

# This creates: ./budgets/budget_2026_01.ods
```

Open the file in LibreOffice Calc or Excel to see your budget!

### Step 2: Create a Budget with Python

For more control, use the Python API:

```python
from pathlib import Path
from spreadsheet_dl import create_monthly_budget

# Create budget in the budgets directory
output_dir = Path("./budgets")
output_dir.mkdir(exist_ok=True)

budget_path = create_monthly_budget(output_dir)
print(f"Budget created: {budget_path}")
```

Run this script:

```bash
python create_my_budget.py
```

### Step 3: Add Your First Expense

Now let's add an expense to the budget we just created:

```bash
# Add a grocery expense
spreadsheet-dl expense 125.50 "Weekly groceries" -c Groceries

# Add lunch expense (category auto-detected)
spreadsheet-dl expense 15.75 "Lunch at Chipotle"
```

The CLI will find your most recent budget file and append the expense!

### Step 4: View Your Budget Summary

Let's analyze our spending so far:

```bash
# View summary
spreadsheet-dl analyze budgets/budget_2026_01.ods
```

Output:

```
Budget Analysis: budgets/budget_2026_01.ods
----------------------------------------
Total Budget:  $5,000.00
Total Spent:   $141.25
Remaining:     $4,858.75
Used:          2.8%
```

### Step 5: Generate a Report

Create a formatted report to share:

```bash
# Generate markdown report
spreadsheet-dl report budgets/budget_2026_01.ods -f markdown

# Save to file
spreadsheet-dl report budgets/budget_2026_01.ods -f markdown -o report.md
```

## Understanding the Budget Structure

Your budget spreadsheet has several sheets:

1. **Expense Log** - Record all expenses here (date, category, description, amount)
2. **Summary** - Auto-calculated spending by category with budget tracking
3. **Budget** - Set your monthly budget allocations per category
4. **Income** - Track income sources (optional)

All summaries update automatically as you add expenses!

## Basic Operations

### Adding Expenses

**Via CLI:**

```bash
# With specific category
spreadsheet-dl expense 50.00 "Gas station" -c Transportation

# With specific date
spreadsheet-dl expense 200.00 "Electric bill" -d 2026-01-15

# Preview without saving
spreadsheet-dl expense 25.00 "Test expense" --dry-run
```

**Via Python:**

```python
from datetime import date
from decimal import Decimal
from spreadsheet_dl import OdsEditor, ExpenseEntry, ExpenseCategory

# Open existing budget
editor = OdsEditor("budgets/budget_2026_01.ods")

# Create expense
expense = ExpenseEntry(
    date=date(2026, 1, 10),
    category=ExpenseCategory.GROCERIES,
    description="Whole Foods",
    amount=Decimal("87.50")
)

# Add to spreadsheet
row_num = editor.append_expense(expense)
editor.save()

print(f"Added expense at row {row_num}")
```

### Viewing Budget Status

**Via CLI:**

```bash
# Quick summary
spreadsheet-dl analyze budget.ods

# JSON output for scripts
spreadsheet-dl analyze budget.ods --json

# Filter by category
spreadsheet-dl analyze budget.ods --category Groceries

# Filter by date range
spreadsheet-dl analyze budget.ods --start-date 2026-01-01 --end-date 2026-01-15
```

**Via Python:**

```python
from spreadsheet_dl import BudgetAnalyzer

# Analyze budget
analyzer = BudgetAnalyzer("budgets/budget_2026_01.ods")
summary = analyzer.get_summary()

print(f"Total spent: ${summary.total_spent}")
print(f"Budget used: {summary.percent_used:.1f}%")
print(f"Remaining: ${summary.total_remaining}")

# Get category breakdown
by_category = analyzer.get_category_breakdown()
for category, amount in by_category.items():
    print(f"{category}: ${amount:,.2f}")
```

### Generating Reports

**Via CLI:**

```bash
# Text report (console output)
spreadsheet-dl report budget.ods -f text

# Markdown report
spreadsheet-dl report budget.ods -f markdown -o monthly_report.md

# JSON data for custom processing
spreadsheet-dl report budget.ods -f json -o data.json
```

**Via Python:**

```python
from spreadsheet_dl import ReportGenerator

# Generate report
generator = ReportGenerator("budgets/budget_2026_01.ods")

# Print to console
print(generator.generate_text_report())

# Save as markdown
generator.save_report("report.md", format="markdown")

# Get raw data
data = generator.generate_visualization_data()
print(f"Categories: {len(data['categories'])}")
```

## Using Themes

SpreadsheetDL includes 5 built-in themes for different use cases:

```bash
# List available themes
spreadsheet-dl themes

# Create budget with specific theme
spreadsheet-dl generate -o ./budgets/ --theme corporate
spreadsheet-dl generate -o ./budgets/ --theme minimal
spreadsheet-dl generate -o ./budgets/ --theme dark
```

**Theme Options:**

- `default` - Clean professional (blue headers, green/red indicators)
- `corporate` - Business-focused (navy blue, brown accents)
- `minimal` - Distraction-free (gray, subtle borders)
- `dark` - Dark mode (dark backgrounds, light text)
- `high_contrast` - Accessibility (bold colors, large fonts)

In Python:

```python
from spreadsheet_dl import OdsGenerator

# Create with theme
generator = OdsGenerator(theme="corporate")
generator.create_budget_spreadsheet("corporate_budget.ods")
```

## Next Steps

Now that you have the basics, explore these topics:

### Tutorials

1. **[Create a Monthly Budget](tutorials/01-create-budget.md)** - Detailed budget setup
2. **[Track Expenses](tutorials/02-track-expenses.md)** - Daily expense tracking workflow
3. **[Import Bank Data](tutorials/03-import-bank-data.md)** - Automate from CSV exports
4. **[Create Reports](tutorials/04-create-reports.md)** - Generate and customize reports
5. **[Use MCP Tools](tutorials/05-use-mcp-tools.md)** - AI-powered spreadsheet operations
6. **[Customize Themes](tutorials/06-customize-themes.md)** - Create your own themes

### Advanced Topics

- **[API Reference](api/index.md)** - Complete Python API documentation
- **[CLI Reference](cli.md)** - All command-line options
- **[Best Practices](guides/best-practices.md)** - Tips and recommendations
- **[MCP Integration](MCP_INTEGRATION.md)** - Claude Desktop setup

### Getting Help

- **Documentation**: [docs/index.md](index.md)
- **Examples**: See `examples/` directory in the repository
- **Issues**: Report bugs on GitHub
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Common Questions

**Q: Can I use Excel to view/edit my budgets?**

A: Yes! ODS files open in Excel, LibreOffice Calc, and Google Sheets. You can also export to XLSX:

```bash
spreadsheet-dl export budget.ods -f xlsx -o budget.xlsx
```

**Q: How do I backup my budgets?**

A: Use the built-in backup command:

```bash
# Create backup
spreadsheet-dl backup budget.ods

# List backups
spreadsheet-dl backup budget.ods --list

# Restore from backup
spreadsheet-dl backup budget.ods --restore backup_file.ods.gz
```

**Q: Can I track multiple accounts?**

A: Yes! Use the account management features:

```bash
spreadsheet-dl account add "Checking" --type checking --balance 1000
spreadsheet-dl account add "Savings" --type savings --balance 5000
spreadsheet-dl account list
```

**Q: How do I import from my bank?**

A: Export transactions as CSV from your bank, then:

```bash
# Auto-detect bank format
spreadsheet-dl import bank_export.csv

# Or specify bank
spreadsheet-dl import transactions.csv --bank chase
```

**Q: Can I create custom categories?**

A: Yes! The category system is fully extensible:

```bash
spreadsheet-dl category add "Pet Care" --color "#795548"
spreadsheet-dl category list
```

## What's Next?

Ready to dive deeper? Start with the tutorials:

- **Beginner**: [Create a Monthly Budget](tutorials/01-create-budget.md)
- **Intermediate**: [Import Bank Data](tutorials/03-import-bank-data.md)
- **Advanced**: [Use MCP Tools](tutorials/05-use-mcp-tools.md)

Happy budgeting!
