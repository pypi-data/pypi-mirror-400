# User Guide

A comprehensive guide to using SpreadsheetDL for family budget management.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Budgets](#creating-budgets)
3. [Adding Expenses](#adding-expenses)
4. [Analyzing Budgets](#analyzing-budgets)
5. [Generating Reports](#generating-reports)
6. [Visual Themes](#visual-themes)
7. [Importing Bank Data](#importing-bank-data)
8. [Recurring Expenses](#recurring-expenses)
9. [Nextcloud Integration](#nextcloud-integration)
10. [Best Practices](#best-practices)

---

## Getting Started

### First Budget

Create your first budget with a single command:

```bash
uv run spreadsheet-dl generate -o ./budgets/
```

This creates a file like `budgets/budget_2025_01.ods` with:

- Expense Log sheet for tracking spending
- Budget sheet with default allocations
- Summary sheet with formulas

### Opening Your Budget

Open the ODS file with:

- LibreOffice Calc (desktop)
- Collabora Office (browser via Nextcloud)
- Nextcloud mobile apps (iOS/Android)

---

## Creating Budgets

### Basic Creation

```bash
# Current month budget in current directory
uv run spreadsheet-dl generate

# Specific output directory
uv run spreadsheet-dl generate -o ~/finances/

# Specific month and year
uv run spreadsheet-dl generate -m 6 -y 2025 -o ~/finances/
```

### With Themes

Apply visual styling:

```bash
# Corporate theme
uv run spreadsheet-dl generate --theme corporate

# High contrast (accessibility)
uv run spreadsheet-dl generate --theme high_contrast
```

See [Visual Themes](#visual-themes) for all options.

---

## Adding Expenses

### Quick Expense Entry

Add expenses directly from the command line:

```bash
# Basic expense with auto-categorization
uv run spreadsheet-dl expense 25.50 "Walmart groceries"
# Output: Auto-categorized as: Groceries

# Specify category
uv run spreadsheet-dl expense 45.00 "Gas station" -c Transportation

# Specify date
uv run spreadsheet-dl expense 150.00 "Electric bill" -c Utilities -d 2025-01-15

# Specify file
uv run spreadsheet-dl expense 12.99 "Netflix" -c Subscriptions -f budget_2025_01.ods
```

### Dry Run Mode

Preview what will be added without modifying files:

```bash
uv run spreadsheet-dl expense 100.00 "Test" --dry-run
# Output: [DRY RUN] Would add expense: ...
```

### Auto-Categorization

If you don't specify a category, SpreadsheetDL automatically categorizes based on the description:

| Description Contains            | Category       |
| ------------------------------- | -------------- |
| walmart, kroger, safeway        | Groceries      |
| gas, shell, chevron             | Transportation |
| netflix, spotify, hulu          | Subscriptions  |
| restaurant, chipotle, starbucks | Dining Out     |
| electric, water, internet       | Utilities      |
| ...                             | ...            |

### Valid Categories

- Housing
- Utilities
- Groceries
- Transportation
- Healthcare
- Insurance
- Entertainment
- Dining Out
- Clothing
- Personal Care
- Education
- Savings
- Debt Payment
- Gifts
- Subscriptions
- Miscellaneous

---

## Analyzing Budgets

### Basic Analysis

```bash
# Summary view
uv run spreadsheet-dl analyze budget_2025_01.ods

# Output:
# Budget Analysis: budget_2025_01.ods
# ----------------------------------------
# Total Budget:  $4,825.00
# Total Spent:   $1,245.50
# Remaining:     $3,579.50
# Used:          25.8%
```

### JSON Output

```bash
uv run spreadsheet-dl analyze budget_2025_01.ods --json
```

### Filter by Category

```bash
uv run spreadsheet-dl analyze budget_2025_01.ods --category Groceries
# Output:
# Category: Groceries
# Total: $275.50
# Transactions: 4
```

### Filter by Date Range

```bash
uv run spreadsheet-dl analyze budget_2025_01.ods \
  --start-date 2025-01-01 --end-date 2025-01-15
```

---

## Generating Reports

### Text Report

```bash
uv run spreadsheet-dl report budget_2025_01.ods -f text
```

### Markdown Report

```bash
uv run spreadsheet-dl report budget_2025_01.ods -f markdown
```

### Save to File

```bash
uv run spreadsheet-dl report budget_2025_01.ods -f markdown -o report.md
```

### JSON Data for Visualizations

```bash
uv run spreadsheet-dl report budget_2025_01.ods -f json
```

---

## Visual Themes

### Available Themes

| Theme           | Description        | Colors                         |
| --------------- | ------------------ | ------------------------------ |
| `default`       | Clean professional | Blue headers, green/red status |
| `corporate`     | Business styling   | Navy blue, brown accents       |
| `minimal`       | Distraction-free   | Gray headers, subtle borders   |
| `dark`          | Dark mode          | Dark backgrounds, light text   |
| `high_contrast` | Accessibility      | Bold colors, large fonts       |

### List All Themes

```bash
uv run spreadsheet-dl themes
uv run spreadsheet-dl themes --json
```

### Custom Themes

Create custom themes by adding YAML files to `src/spreadsheet_dl/themes/`.

---

## Importing Bank Data

### Supported Banks

- Chase
- Bank of America
- Capital One
- Wells Fargo
- Citi
- USAA
- Generic CSV

### Auto-Detection

```bash
# Auto-detect bank format
uv run spreadsheet-dl import transactions.csv
```

### Specify Bank

```bash
uv run spreadsheet-dl import transactions.csv --bank chase
```

### Preview Before Import

```bash
uv run spreadsheet-dl import transactions.csv --preview
# Output:
# Preview (first 10):
#   2025-01-15 | Groceries       | $  125.50 | WALMART
#   2025-01-14 | Dining Out      | $   45.00 | CHIPOTLE
#   ...
```

### Import with Theme

```bash
uv run spreadsheet-dl import transactions.csv --theme corporate -o imported.ods
```

---

## Recurring Expenses

### Python API

```python
from spreadsheet_dl import RecurringExpenseManager, RecurringExpense
from spreadsheet_dl import ExpenseCategory, RecurrenceFrequency
from decimal import Decimal

# Create manager
manager = RecurringExpenseManager("recurring.json")

# Add recurring expense
manager.add(RecurringExpense(
    name="Netflix",
    category=ExpenseCategory.SUBSCRIPTIONS,
    amount=Decimal("15.99"),
    frequency=RecurrenceFrequency.MONTHLY,
))

# Generate for a month
entries = manager.generate_for_month(1, 2025)

# Get monthly total
print(f"Monthly recurring: ${manager.calculate_monthly_total()}")
```

---

## Nextcloud Integration

### Setup

1. Create an app password in Nextcloud
2. Set environment variables:

```bash
export NEXTCLOUD_URL=https://your-nextcloud.com
export NEXTCLOUD_USER=username
export NEXTCLOUD_PASSWORD=app-password
```

### Upload Budget

```bash
uv run spreadsheet-dl upload budget_2025_01.ods
# Output: Uploaded: https://your-nextcloud.com/remote.php/dav/files/...
```

### Editing with Collabora

1. Navigate to the file in Nextcloud
2. Click to open in Collabora Office
3. Edit directly in browser
4. Changes sync automatically

### Mobile Editing

1. Install Nextcloud app
2. Open ODS file
3. Collabora editor loads automatically

---

## Best Practices

### File Organization

```
~/finances/
├── 2024/
│   ├── budget_2024_01.ods
│   ├── budget_2024_02.ods
│   └── ...
├── 2025/
│   ├── budget_2025_01.ods
│   └── ...
├── imports/
│   └── bank_exports/
└── reports/
```

### Regular Workflow

1. **Daily**: Add expenses as they occur
2. **Weekly**: Review category totals
3. **Monthly**: Generate report, start new budget
4. **Yearly**: Archive old files

### Security

- Never commit financial data to git
- Use `.gitignore` for ODS files
- Use Nextcloud app passwords
- Enable two-factor authentication

### Backup

1. Enable Nextcloud versioning
2. Regular local backups
3. Consider encrypted storage

---

## Troubleshooting

### Common Issues

**File won't open**

- Ensure LibreOffice or Collabora is installed
- Check file permissions

**Formulas not calculating**

- Enable automatic calculation in spreadsheet app
- Check formula references

**Expense not appearing**

- Verify correct file was updated
- Check sheet name (default: "Expense Log")

### Getting Help

- Check the [API Reference](api/index.md)
- Review [Examples](examples/index.md)
- Open an issue on GitHub
