# Tutorial 3: Import Bank Data

Learn how to automatically import transactions from bank CSV exports and eliminate manual data entry.

## What You'll Learn

- Export transactions from your bank
- Use SpreadsheetDL's CSV import
- Map columns to categories
- Auto-categorize transactions
- Review and adjust imports

## Prerequisites

- Bank account with online access
- Completed [Tutorial 1: Create a Budget](01-create-budget.md)
- CSV export from your bank (we'll show you how)

## Supported Banks

SpreadsheetDL supports 50+ bank formats including:

**Major Banks:**

- Chase (checking, credit cards)
- Bank of America
- Wells Fargo
- Citibank
- Capital One

**Credit Unions:**

- Navy Federal
- BECU
- Alliant

**Credit Cards:**

- American Express
- Discover
- Chase Sapphire

**View full list:**

```bash
spreadsheet-dl banks --list
```

## Step 1: Export From Your Bank

### Chase Example

1. Log into chase.com
2. Navigate to your checking account
3. Click "Download transactions"
4. Select:
   - **Format**: CSV
   - **Date Range**: Last 30 days
   - **Account**: Your checking account
5. Click "Download"
6. Save as `chase_transactions.csv`

### Bank of America Example

1. Log into bankofamerica.com
2. Go to account activity
3. Click "Download" (top right)
4. Select:
   - **Format**: CSV (Microsoft Excel)
   - **Date Range**: Custom (last month)
5. Click "Download"
6. Save as `bofa_transactions.csv`

### Generic CSV Export

If your bank isn't listed, export with these columns:

- Date (YYYY-MM-DD or MM/DD/YYYY)
- Description
- Amount (positive for credits, negative for debits)
- Category (optional)

## Step 2: Preview the Import

Before importing, preview what will be added:

```bash
# Preview import (doesn't create file)
spreadsheet-dl import chase_transactions.csv --preview
```

Output:

```
Detected format: chase_checking

Found 47 expenses

Preview (first 10):
  2026-01-02 | Groceries      | $ 125.50 | SAFEWAY #1234
  2026-01-02 | Dining Out     | $  45.00 | CHIPOTLE MEXICAN
  2026-01-03 | Transportation | $  52.00 | CHEVRON GAS STATION
  2026-01-03 | Shopping       | $  89.99 | AMAZON.COM
  2026-01-04 | Groceries      | $  87.50 | WHOLE FOODS MARKET
  2026-01-05 | Entertainment  | $  12.99 | NETFLIX.COM
  2026-01-05 | Utilities      | $  79.99 | PG&E ENERGY BILL
  2026-01-06 | Dining Out     | $  32.00 | PIZZA HUT
  2026-01-07 | Healthcare     | $ 125.00 | DR SMITH COPAY
  2026-01-08 | Personal Care  | $  45.50 | CVS PHARMACY
  ... and 37 more
```

**What happened:**

1. Auto-detected Chase format
2. Parsed CSV columns
3. Auto-categorized based on merchant names
4. Showed preview without creating file

## Step 3: Import to New Budget

Create a new budget with imported transactions:

```bash
# Import and create budget
spreadsheet-dl import chase_transactions.csv -o ~/budgets/imported_jan.ods
```

Output:

```
Detected format: chase_checking
Found 47 expenses
Created: /home/user/budgets/imported_jan.ods
Total imported: $1,847.48
```

Open the file - all transactions are now in the Expense Log!

## Step 4: Import to Existing Budget

Add transactions to your current budget:

```bash
# Import into existing file
spreadsheet-dl import chase_transactions.csv
```

The transactions will be appended to your most recent budget file.

## Step 5: Specify Bank Format

If auto-detection fails, specify the bank:

```bash
# List available formats
spreadsheet-dl banks --list

# Use specific format
spreadsheet-dl import transactions.csv --bank chase_credit
spreadsheet-dl import transactions.csv --bank bofa_checking
spreadsheet-dl import transactions.csv --bank amex
```

**Detect format from file:**

```bash
# Let SpreadsheetDL analyze the CSV
spreadsheet-dl banks --detect transactions.csv
```

## Step 6: Review and Adjust Categories

After import, review auto-categorization:

```bash
# View categorization summary
spreadsheet-dl analyze ~/budgets/imported_jan.ods
```

**Common adjustments needed:**

```python
from spreadsheet_dl import OdsEditor, ExpenseCategory

# Open the imported budget
editor = OdsEditor("imported_jan.ods")

# Fix miscategorized transactions
# (You'll need to identify row numbers from the file)

# Example: Change row 15 from Shopping to Entertainment
editor.update_expense_category(15, ExpenseCategory.ENTERTAINMENT)

# Example: Change row 23 from Miscellaneous to Healthcare
editor.update_expense_category(23, ExpenseCategory.HEALTHCARE)

# Save changes
editor.save()
```

## Step 7: Custom Import with Python

For advanced control, use the Python API:

```python
#!/usr/bin/env python3
"""Custom CSV import with filtering and adjustments."""

from pathlib import Path
from decimal import Decimal
from datetime import date
from spreadsheet_dl import (
    import_bank_csv,
    OdsGenerator,
    ExpenseCategory,
)

# Import transactions
csv_path = Path("~/Downloads/chase_transactions.csv").expanduser()
transactions = import_bank_csv(csv_path, bank="auto")

print(f"Imported {len(transactions)} transactions")

# Filter out transfers and credits (keep debits only)
debits = [t for t in transactions if t.amount > 0]
print(f"Filtered to {len(debits)} debit transactions")

# Remove very small transactions (< $1)
significant = [t for t in debits if t.amount >= Decimal("1.00")]
print(f"Filtered to {len(significant)} significant transactions")

# Manually adjust specific categories
for transaction in significant:
    # Example: Recategorize all Amazon as Shopping
    if "AMAZON" in transaction.description.upper():
        transaction.category = ExpenseCategory.SHOPPING

    # Example: ATM withdrawals -> Cash
    if "ATM" in transaction.description.upper():
        transaction.category = ExpenseCategory.CASH

# Create budget with filtered transactions
output_path = Path("~/budgets/filtered_import.ods").expanduser()
generator = OdsGenerator()
generator.create_budget_spreadsheet(
    output_path,
    expenses=significant,
    month=date.today().month,
    year=date.today().year
)

print(f"\nCreated budget: {output_path}")
print(f"Total amount: ${sum(t.amount for t in significant):,.2f}")
```

## Step 8: Handle Multiple Accounts

Import from multiple bank accounts:

```python
#!/usr/bin/env python3
"""Import from multiple bank accounts."""

from pathlib import Path
from spreadsheet_dl import import_bank_csv, OdsGenerator

# Import from checking account
checking_path = Path("~/Downloads/chase_checking.csv").expanduser()
checking_transactions = import_bank_csv(checking_path, bank="chase_checking")

# Import from credit card
credit_path = Path("~/Downloads/chase_credit.csv").expanduser()
credit_transactions = import_bank_csv(credit_path, bank="chase_credit")

# Combine all transactions
all_transactions = checking_transactions + credit_transactions

print(f"Checking: {len(checking_transactions)} transactions")
print(f"Credit:   {len(credit_transactions)} transactions")
print(f"Total:    {len(all_transactions)} transactions")

# Sort by date
all_transactions.sort(key=lambda t: t.date)

# Create consolidated budget
generator = OdsGenerator()
budget_path = generator.create_budget_spreadsheet(
    "consolidated_budget.ods",
    expenses=all_transactions
)

print(f"\nConsolidated budget created: {budget_path}")
```

## Step 9: Apply Theme to Import

Import with a specific theme:

```bash
# Import with corporate theme
spreadsheet-dl import transactions.csv --theme corporate -o import.ods

# Import with dark theme
spreadsheet-dl import transactions.csv --theme dark -o import.ods
```

## Step 10: Automate Monthly Imports

Create a script to automate monthly imports:

```python
#!/usr/bin/env python3
"""
Monthly import automation script.

Run this at the end of each month to import transactions.
"""

import sys
from pathlib import Path
from datetime import date
from spreadsheet_dl import import_bank_csv, OdsGenerator

def monthly_import():
    """Import transactions and create monthly budget."""

    # Configuration
    DOWNLOAD_DIR = Path.home() / "Downloads"
    BUDGET_DIR = Path.home() / "budgets"
    BANK_FORMAT = "chase_checking"

    # Find most recent CSV in downloads
    csv_files = list(DOWNLOAD_DIR.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in Downloads folder!")
        return 1

    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"Processing: {latest_csv.name}")

    # Import transactions
    try:
        transactions = import_bank_csv(latest_csv, bank=BANK_FORMAT)
        print(f"Imported {len(transactions)} transactions")
    except Exception as e:
        print(f"Import failed: {e}")
        return 1

    if not transactions:
        print("No transactions found!")
        return 1

    # Create budget for current month
    today = date.today()
    output_file = BUDGET_DIR / f"budget_{today.year}_{today.month:02d}.ods"

    if output_file.exists():
        confirm = input(f"{output_file.name} exists. Overwrite? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return 0

    # Generate budget
    generator = OdsGenerator(theme="default")
    budget_path = generator.create_budget_spreadsheet(
        output_file,
        month=today.month,
        year=today.year,
        expenses=transactions
    )

    # Summary
    total = sum(t.amount for t in transactions)
    print(f"\nSuccess!")
    print(f"  Budget: {budget_path}")
    print(f"  Transactions: {len(transactions)}")
    print(f"  Total: ${total:,.2f}")

    # Cleanup (optional)
    cleanup = input("\nMove CSV to archive? [y/N]: ")
    if cleanup.lower() == 'y':
        archive_dir = BUDGET_DIR / "archives"
        archive_dir.mkdir(exist_ok=True)
        latest_csv.rename(archive_dir / latest_csv.name)
        print(f"Archived: {latest_csv.name}")

    return 0

if __name__ == "__main__":
    sys.exit(monthly_import())
```

Save as `monthly_import.py` and run at month-end:

```bash
python monthly_import.py
```

## Categorization Rules

SpreadsheetDL uses these patterns for auto-categorization:

| Pattern                                  | Category       |
| ---------------------------------------- | -------------- |
| safeway, kroger, trader joe, whole foods | Groceries      |
| restaurant, cafe, chipotle, mcdonald     | Dining Out     |
| shell, chevron, bp, mobil, exxon         | Transportation |
| amazon, target, walmart, best buy        | Shopping       |
| netflix, spotify, hulu, disney           | Entertainment  |
| electric, gas, water, internet, pg&e     | Utilities      |
| cvs, walgreens, pharmacy, doctor         | Healthcare     |

**Customize categorization:**

```python
from spreadsheet_dl import TransactionCategorizer, ExpenseCategory

categorizer = TransactionCategorizer()

# Add custom rule
categorizer.add_pattern("my gym name", ExpenseCategory.HEALTHCARE)
categorizer.add_pattern("my barber", ExpenseCategory.PERSONAL_CARE)

# Use for categorization
category = categorizer.categorize("MY GYM NAME MEMBERSHIP")
# Returns: ExpenseCategory.HEALTHCARE
```

## Troubleshooting

**"Could not auto-detect format" error?**

- Your bank may not be in the built-in list
- Specify format manually: `--bank generic`
- Or create custom format (see Advanced section)

**Wrong categories assigned?**

- Review with `--preview` first
- Adjust manually after import
- Add custom categorization rules

**Duplicate transactions?**

- Check date ranges when exporting from bank
- SpreadsheetDL doesn't auto-deduplicate
- Filter manually or in Python

**CSV encoding errors?**

- Some banks use non-UTF-8 encoding
- Open CSV in Excel, save as "CSV UTF-8"
- Or specify encoding in Python import

## Best Practices

1. **Export Monthly** - Download transactions at the end of each month
2. **Always Preview** - Use `--preview` before importing
3. **Keep Archives** - Save original CSV files
4. **Review Categories** - Check auto-categorization accuracy
5. **Consistent Format** - Use same export format each month

## Next Steps

- **[Tutorial 4: Create Reports](04-create-reports.md)** - Generate spending reports
- **[Tutorial 5: Use MCP Tools](05-use-mcp-tools.md)** - AI-powered analysis
- **[Best Practices](../guides/best-practices.md)** - Advanced import strategies

## Additional Resources

- [Supported Bank Formats](../api/bank_formats.md)
- [Custom Format Creation](../guides/custom-bank-formats.md)
- [CLI Import Reference](../cli.md)
