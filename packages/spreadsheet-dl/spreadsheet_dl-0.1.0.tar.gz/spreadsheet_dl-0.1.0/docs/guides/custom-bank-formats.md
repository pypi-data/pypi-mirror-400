# Custom Bank Format Creation Guide

## Overview

SpreadsheetDL supports 50+ built-in bank CSV formats, but you may need to add support for your specific financial institution. This guide shows you how to create custom format definitions for importing bank transactions.

**What You'll Learn:**

- Understand CSV format structure
- Create format specifications
- Define column mappings
- Add categorization rules
- Test and validate formats
- Register custom formats

## Prerequisites

- Python 3.10 or later
- SpreadsheetDL installed
- Sample CSV export from your bank
- Basic understanding of CSV format

## Bank CSV Format Structure

### Common Format Patterns

Most bank CSVs follow one of these patterns:

**Pattern 1: Standard Format**

```csv
Date,Description,Amount,Balance
2026-01-15,SAFEWAY #1234,45.67,1234.56
2026-01-16,PAYMENT - THANK YOU,-500.00,1734.56
```

**Pattern 2: Separate Debit/Credit Columns**

```csv
Date,Description,Debit,Credit,Balance
2026-01-15,SAFEWAY #1234,45.67,,1234.56
2026-01-16,PAYMENT,,500.00,1734.56
```

**Pattern 3: Detailed Format**

```csv
Transaction Date,Post Date,Description,Category,Type,Amount,Memo
01/15/2026,01/15/2026,SAFEWAY #1234,Shopping,Debit,45.67,
```

## Step 1: Analyze Your Bank's CSV

### Export Sample Data

1. Log into your bank's website
2. Download transactions (CSV format)
3. Open in text editor (not Excel)
4. Note the structure

### Identify Key Elements

Record these details:

- **Date column name(s)**: Which column contains transaction dates?
- **Date format**: MM/DD/YYYY, YYYY-MM-DD, DD/MM/YYYY?
- **Description column**: Where is merchant/description?
- **Amount representation**: Single column or separate debit/credit?
- **Amount sign convention**: Negative for debits or positive?
- **Header row**: Does first row contain column names?
- **Delimiter**: Comma, tab, semicolon?
- **Quote character**: Are fields quoted?

### Example Analysis

```csv
Transaction Date,Description,Debit,Credit,Running Balance
01/15/2026,"SAFEWAY #1234",45.67,,2954.33
01/16/2026,"RENT PAYMENT - ACH",,1500.00,4454.33
01/17/2026,"ATM WITHDRAWAL - 123 MAIN ST",40.00,,4414.33
```

**Analysis:**

- Date column: "Transaction Date"
- Date format: MM/DD/YYYY
- Description: "Description" (with quotes)
- Amount: Separate Debit/Credit columns
- Debits are positive in Debit column
- Credits are positive in Credit column
- Has header row
- Delimiter: comma
- Quote character: double quote

## Step 2: Create Format Specification

### Format Class Structure

```python
from spreadsheet_dl.csv_import import BankFormatSpec, ColumnMapping
from datetime import datetime
from decimal import Decimal

class MyBankFormat(BankFormatSpec):
    """Format specification for My Bank CSV exports."""

    @property
    def format_id(self) -> str:
        """Unique identifier for this format."""
        return "mybank_checking"

    @property
    def format_name(self) -> str:
        """Human-readable format name."""
        return "My Bank - Checking Account"

    @property
    def column_mapping(self) -> ColumnMapping:
        """Define how CSV columns map to transaction fields."""
        return ColumnMapping(
            date_column="Transaction Date",
            description_column="Description",
            debit_column="Debit",
            credit_column="Credit",
            # Optional columns
            balance_column="Running Balance",
            category_column=None,  # No category in export
            memo_column=None,
        )

    @property
    def date_format(self) -> str:
        """Date format string for parsing."""
        return "%m/%d/%Y"  # MM/DD/YYYY

    @property
    def has_header(self) -> bool:
        """Whether CSV has header row."""
        return True

    @property
    def delimiter(self) -> str:
        """CSV delimiter character."""
        return ","

    @property
    def quotechar(self) -> str:
        """Quote character for fields."""
        return '"'

    def detect(self, csv_sample: str) -> bool:
        """
        Detect if CSV matches this format.

        Args:
            csv_sample: First few lines of CSV file.

        Returns:
            True if this format applies.
        """
        # Check for key column names
        required_columns = [
            "Transaction Date",
            "Description",
            "Debit",
            "Credit"
        ]
        return all(col in csv_sample for col in required_columns)

    def parse_amount(self, row: dict) -> Decimal:
        """
        Parse transaction amount from row.

        Args:
            row: CSV row as dictionary.

        Returns:
            Transaction amount (positive for expenses).
        """
        debit = row.get("Debit", "").strip()
        credit = row.get("Credit", "").strip()

        # Debits are expenses (positive)
        if debit:
            return Decimal(debit)

        # Credits are income (negative for expense tracking)
        if credit:
            return -Decimal(credit)

        return Decimal("0.00")

    def parse_date(self, date_str: str) -> datetime:
        """
        Parse date string.

        Args:
            date_str: Date string from CSV.

        Returns:
            Parsed datetime object.
        """
        return datetime.strptime(date_str.strip(), self.date_format)

    def clean_description(self, description: str) -> str:
        """
        Clean and normalize description.

        Args:
            description: Raw description from CSV.

        Returns:
            Cleaned description.
        """
        # Remove extra whitespace
        cleaned = " ".join(description.split())

        # Remove bank-specific codes
        # Example: "POS DEB - SAFEWAY #1234" -> "SAFEWAY #1234"
        if cleaned.startswith("POS DEB - "):
            cleaned = cleaned[10:]
        elif cleaned.startswith("ATM WITHDRAWAL - "):
            cleaned = "ATM " + cleaned[17:]

        return cleaned.upper()
```

## Step 3: Single vs Split Amount Columns

### Single Amount Column (With Sign)

If your bank uses one amount column with positive/negative values:

```python
@property
def column_mapping(self) -> ColumnMapping:
    return ColumnMapping(
        date_column="Date",
        description_column="Description",
        amount_column="Amount",  # Single column
        debit_column=None,
        credit_column=None,
    )

def parse_amount(self, row: dict) -> Decimal:
    """Single column - negative means expense."""
    amount_str = row.get("Amount", "0").strip()

    # Remove currency symbols
    amount_str = amount_str.replace("$", "").replace(",", "")

    amount = Decimal(amount_str)

    # Negative in CSV = expense (make positive)
    # Positive in CSV = income (make negative for expense tracking)
    return abs(amount) if amount < 0 else -amount
```

### Split Debit/Credit Columns

If your bank has separate debit and credit columns:

```python
@property
def column_mapping(self) -> ColumnMapping:
    return ColumnMapping(
        date_column="Date",
        description_column="Description",
        amount_column=None,  # No single column
        debit_column="Debits",
        credit_column="Credits",
    )

def parse_amount(self, row: dict) -> Decimal:
    """Split columns - debits are expenses."""
    debit = row.get("Debits", "").strip()
    credit = row.get("Credits", "").strip()

    if debit:
        # Debit is expense (positive)
        return Decimal(debit.replace("$", "").replace(",", ""))

    if credit:
        # Credit is income (negative for expense tracking)
        return -Decimal(credit.replace("$", "").replace(",", ""))

    return Decimal("0.00")
```

## Step 4: Date Format Handling

### Common Date Formats

```python
# US Format: 01/15/2026
date_format = "%m/%d/%Y"

# ISO Format: 2026-01-15
date_format = "%Y-%m-%d"

# European: 15/01/2026
date_format = "%d/%m/%Y"

# Long format: January 15, 2026
date_format = "%B %d, %Y"

# With time: 01/15/2026 14:32:15
date_format = "%m/%d/%Y %H:%M:%S"
```

### Flexible Date Parsing

If your bank uses multiple date formats:

```python
def parse_date(self, date_str: str) -> datetime:
    """Try multiple date formats."""
    date_str = date_str.strip()

    formats = [
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m-%d-%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: {date_str}")
```

## Step 5: Description Cleaning

### Remove Bank Codes

Banks often add prefixes or codes to descriptions:

```python
def clean_description(self, description: str) -> str:
    """Remove bank-specific formatting."""
    cleaned = description.strip()

    # Remove common prefixes
    prefixes_to_remove = [
        "POS DEB - ",
        "POS PURCHASE - ",
        "CHECK CARD PURCHASE - ",
        "RECURRING DEBIT - ",
        "ATM WITHDRAWAL - ",
        "ONLINE PAYMENT - ",
        "ACH DEBIT - ",
    ]

    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break

    # Remove transaction IDs
    # Example: "SAFEWAY #1234 TXN#12345678" -> "SAFEWAY #1234"
    if " TXN#" in cleaned:
        cleaned = cleaned.split(" TXN#")[0]

    # Normalize whitespace
    cleaned = " ".join(cleaned.split())

    return cleaned.upper()
```

### Extract Merchant Name

```python
def extract_merchant(self, description: str) -> str:
    """Extract core merchant name."""
    cleaned = self.clean_description(description)

    # Remove location codes
    # "SAFEWAY #1234" -> "SAFEWAY"
    if "#" in cleaned:
        cleaned = cleaned.split("#")[0].strip()

    # Remove trailing location info
    # "MCDONALDS MAIN ST" -> "MCDONALDS"
    words = cleaned.split()
    if len(words) > 2:
        # Keep first 2 words
        cleaned = " ".join(words[:2])

    return cleaned
```

## Step 6: Add Categorization Rules

### Pattern-Based Categorization

```python
def suggest_category(self, description: str) -> ExpenseCategory | None:
    """
    Suggest category based on description.

    Returns:
        Suggested category or None if unknown.
    """
    from spreadsheet_dl import ExpenseCategory

    description_upper = description.upper()

    # Groceries
    if any(store in description_upper for store in [
        "SAFEWAY", "KROGER", "WHOLE FOODS", "TRADER JOE",
        "WALMART GROCERY", "TARGET", "COSTCO"
    ]):
        return ExpenseCategory.GROCERIES

    # Dining
    if any(keyword in description_upper for keyword in [
        "RESTAURANT", "CAFE", "COFFEE", "PIZZA", "BURGER",
        "MCDONALD", "CHIPOTLE", "STARBUCKS", "SUBWAY"
    ]):
        return ExpenseCategory.DINING_OUT

    # Gas/Transportation
    if any(keyword in description_upper for keyword in [
        "SHELL", "CHEVRON", "EXXON", "BP ", "MOBIL",
        "GAS STATION", "FUEL"
    ]):
        return ExpenseCategory.TRANSPORTATION

    # Utilities
    if any(keyword in description_upper for keyword in [
        "ELECTRIC", "GAS COMPANY", "WATER", "PG&E",
        "INTERNET", "COMCAST", "AT&T", "VERIZON"
    ]):
        return ExpenseCategory.UTILITIES

    # Entertainment
    if any(keyword in description_upper for keyword in [
        "NETFLIX", "SPOTIFY", "HULU", "DISNEY",
        "MOVIE", "THEATER", "AMC ", "CINEMA"
    ]):
        return ExpenseCategory.ENTERTAINMENT

    # Healthcare
    if any(keyword in description_upper for keyword in [
        "PHARMACY", "CVS", "WALGREENS", "DOCTOR",
        "HOSPITAL", "CLINIC", "MEDICAL"
    ]):
        return ExpenseCategory.HEALTHCARE

    # Default to None (unknown)
    return None
```

## Step 7: Register Custom Format

### Register Globally

```python
from spreadsheet_dl import register_bank_format

# Register your custom format
register_bank_format(MyBankFormat())

# Now it's available for import
from spreadsheet_dl import import_bank_csv

transactions = import_bank_csv("mybank.csv")
# Auto-detects and uses MyBankFormat
```

### Register for Specific Use

```python
from spreadsheet_dl import CSVImporter

# Create importer with custom format
importer = CSVImporter()
importer.register_format(MyBankFormat())

# Import with your format
result = importer.import_file("mybank.csv", format_id="mybank_checking")
```

## Step 8: Test Your Format

### Create Test File

```python
import tempfile
from pathlib import Path

def test_mybank_format():
    """Test custom format with sample data."""

    # Create test CSV
    test_csv = """Transaction Date,Description,Debit,Credit,Running Balance
01/15/2026,"SAFEWAY #1234",45.67,,2954.33
01/16/2026,"RENT PAYMENT - ACH",,1500.00,4454.33
01/17/2026,"SHELL GAS STATION",52.00,,4402.33
"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(test_csv)
        temp_path = Path(f.name)

    try:
        # Test import
        from spreadsheet_dl import CSVImporter

        importer = CSVImporter()
        importer.register_format(MyBankFormat())

        result = importer.import_file(temp_path)

        # Verify results
        assert result.success, f"Import failed: {result.errors}"
        assert len(result.data) == 3, f"Expected 3 transactions, got {len(result.data)}"

        # Check first transaction
        first = result.data[0]
        assert first.description == "SAFEWAY #1234"
        assert first.amount == 45.67
        assert first.category == ExpenseCategory.GROCERIES

        print("✓ All tests passed!")

    finally:
        temp_path.unlink()

if __name__ == "__main__":
    test_mybank_format()
```

### Validate Detection

```python
def test_format_detection():
    """Test format auto-detection."""

    sample = """Transaction Date,Description,Debit,Credit,Running Balance
01/15/2026,"SAFEWAY",45.67,,2954.33
"""

    format_spec = MyBankFormat()

    # Should detect correctly
    assert format_spec.detect(sample), "Format detection failed"

    # Should not detect wrong format
    wrong_sample = "Date,Amount,Description\n01/15/2026,45.67,SAFEWAY\n"
    assert not format_spec.detect(wrong_sample), "False positive detection"

    print("✓ Detection tests passed!")
```

## Step 9: Handle Edge Cases

### Missing/Empty Fields

```python
def parse_amount(self, row: dict) -> Decimal:
    """Handle missing or empty amount fields."""
    debit = row.get("Debit", "").strip()
    credit = row.get("Credit", "").strip()

    # Handle empty strings
    if not debit and not credit:
        return Decimal("0.00")

    # Handle placeholder values
    if debit in ("", "-", "N/A", "None"):
        debit = None
    if credit in ("", "-", "N/A", "None"):
        credit = None

    if debit:
        return Decimal(debit.replace("$", "").replace(",", ""))
    if credit:
        return -Decimal(credit.replace("$", "").replace(",", ""))

    return Decimal("0.00")
```

### Multiple Date Columns

```python
@property
def column_mapping(self) -> ColumnMapping:
    """Use transaction date, not post date."""
    return ColumnMapping(
        date_column="Transaction Date",  # Prefer transaction date
        # Alternative: "Post Date" if transaction date unavailable
        description_column="Description",
        debit_column="Debit",
        credit_column="Credit",
    )

def parse_date(self, date_str: str) -> datetime:
    """Parse date, handling both columns."""
    # Try transaction date first
    try:
        return datetime.strptime(date_str.strip(), self.date_format)
    except ValueError:
        pass

    # Fallback to alternative format
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Could not parse date: {date_str}")
```

### Currency Symbols

```python
def parse_amount(self, row: dict) -> Decimal:
    """Handle various currency formats."""
    amount_str = row.get("Amount", "0").strip()

    # Remove currency symbols
    amount_str = amount_str.replace("$", "")
    amount_str = amount_str.replace("€", "")
    amount_str = amount_str.replace("£", "")
    amount_str = amount_str.replace("¥", "")

    # Remove thousands separators
    amount_str = amount_str.replace(",", "")

    # Handle parentheses for negative
    if amount_str.startswith("(") and amount_str.endswith(")"):
        amount_str = "-" + amount_str[1:-1]

    return Decimal(amount_str)
```

## Complete Example

Here's a complete, production-ready format specification:

```python
"""
Custom bank format for Example Bank.

Usage:
    from my_formats import ExampleBankFormat
    from spreadsheet_dl import register_bank_format

    register_bank_format(ExampleBankFormat())
"""

from spreadsheet_dl.csv_import import BankFormatSpec, ColumnMapping
from spreadsheet_dl import ExpenseCategory
from datetime import datetime
from decimal import Decimal


class ExampleBankFormat(BankFormatSpec):
    """Example Bank CSV format specification."""

    @property
    def format_id(self) -> str:
        return "example_bank_checking"

    @property
    def format_name(self) -> str:
        return "Example Bank - Checking Account"

    @property
    def column_mapping(self) -> ColumnMapping:
        return ColumnMapping(
            date_column="Transaction Date",
            description_column="Description",
            debit_column="Debits",
            credit_column="Credits",
            balance_column="Balance",
        )

    @property
    def date_format(self) -> str:
        return "%m/%d/%Y"

    @property
    def has_header(self) -> bool:
        return True

    @property
    def delimiter(self) -> str:
        return ","

    @property
    def quotechar(self) -> str:
        return '"'

    def detect(self, csv_sample: str) -> bool:
        """Detect Example Bank format."""
        required = ["Transaction Date", "Description", "Debits", "Credits"]
        return all(col in csv_sample for col in required)

    def parse_amount(self, row: dict) -> Decimal:
        """Parse amount from debit/credit columns."""
        debit = row.get("Debits", "").strip()
        credit = row.get("Credits", "").strip()

        # Clean currency formatting
        def clean(s: str) -> Decimal:
            if not s or s in ("-", "N/A"):
                return Decimal("0.00")
            s = s.replace("$", "").replace(",", "")
            return Decimal(s)

        debit_amount = clean(debit)
        credit_amount = clean(credit)

        # Debits are expenses (positive)
        if debit_amount > 0:
            return debit_amount

        # Credits are income (negative)
        if credit_amount > 0:
            return -credit_amount

        return Decimal("0.00")

    def parse_date(self, date_str: str) -> datetime:
        """Parse date string."""
        return datetime.strptime(date_str.strip(), self.date_format)

    def clean_description(self, description: str) -> str:
        """Clean transaction description."""
        cleaned = description.strip().upper()

        # Remove bank prefixes
        prefixes = ["POS DEB - ", "ONLINE - ", "CHECK CARD - "]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break

        # Remove transaction IDs
        if " #TXN" in cleaned:
            cleaned = cleaned.split(" #TXN")[0]

        return " ".join(cleaned.split())

    def suggest_category(self, description: str) -> ExpenseCategory | None:
        """Suggest expense category from description."""
        desc_upper = description.upper()

        # Groceries
        groceries = ["SAFEWAY", "KROGER", "TRADER JOE", "WHOLE FOODS"]
        if any(store in desc_upper for store in groceries):
            return ExpenseCategory.GROCERIES

        # Dining
        dining = ["RESTAURANT", "CAFE", "PIZZA", "BURGER", "STARBUCKS"]
        if any(word in desc_upper for word in dining):
            return ExpenseCategory.DINING_OUT

        # Transportation
        gas = ["SHELL", "CHEVRON", "BP", "EXXON", "MOBIL"]
        if any(station in desc_upper for station in gas):
            return ExpenseCategory.TRANSPORTATION

        # Utilities
        utilities = ["ELECTRIC", "GAS CO", "WATER", "INTERNET", "PG&E"]
        if any(util in desc_upper for util in utilities):
            return ExpenseCategory.UTILITIES

        return None


# Auto-register on import
register_bank_format(ExampleBankFormat())
```

## Best Practices

1. **Test with Real Data**: Use actual exports from your bank
2. **Handle Edge Cases**: Empty fields, missing data, special characters
3. **Document Format**: Add comments explaining bank-specific quirks
4. **Version Control**: Track format changes over time
5. **Share Formats**: Contribute to SpreadsheetDL repository
6. **Regular Testing**: Banks change export formats periodically

## Troubleshooting

**Import failing?**

- Check CSV encoding (UTF-8 vs others)
- Verify column names match exactly (case-sensitive)
- Test detection logic with actual CSV header
- Add debug logging to parse methods

**Wrong amounts?**

- Verify debit/credit sign conventions
- Check for hidden currency symbols
- Test with positive and negative values
- Ensure decimal precision is correct

**Date parsing errors?**

- Confirm exact date format
- Check for leading/trailing whitespace
- Test with multiple date examples
- Consider timezone if timestamps included

**Categories not working?**

- Update categorization rules with actual merchant names
- Use broader pattern matching
- Test with representative transactions
- Consider machine learning for better categorization

## See Also

- [CSV Import API](../api/csv_import.md) - CSV import module reference
- [Bank Formats](../api/bank_formats.md) - Built-in format list
- [Tutorial: Import Bank Data](../tutorials/03-import-bank-data.md) - Import tutorial
- [Expense Categories](../api/categories.md) - Category system
