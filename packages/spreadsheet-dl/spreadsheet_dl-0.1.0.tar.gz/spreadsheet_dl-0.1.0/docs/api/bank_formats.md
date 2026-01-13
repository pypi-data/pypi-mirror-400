# Bank Formats API Reference

## Overview

The `bank_formats` module provides extended support for 50+ bank and credit card CSV formats, enabling seamless import of transaction data from various financial institutions.

**Key Features:**

- 50+ pre-configured bank format definitions
- YAML-based format configuration
- Auto-detection of CSV formats
- Custom format builder for unsupported banks
- Format validation and testing
- Extensible registry system

**Module Location:** `spreadsheet_dl.domains.finance.bank_formats`

---

## Core Classes

### BankFormatDefinition

Complete bank CSV format definition.

```python
@dataclass
class BankFormatDefinition:
    id: str
    name: str
    institution: str = ""
    format_type: str = "checking"
    date_column: str = "Date"
    date_format: str = "%m/%d/%Y"
    amount_column: str = "Amount"
    description_column: str = "Description"
    debit_column: str | None = None
    credit_column: str | None = None
    memo_column: str | None = None
    category_column: str | None = None
    reference_column: str | None = None
    balance_column: str | None = None
    skip_rows: int = 0
    encoding: str = "utf-8-sig"
    delimiter: str = ","
    expense_is_negative: bool = True
    header_patterns: list[str] = field(default_factory=list)
    notes: str = ""
```

#### Methods

##### `to_dict() -> dict[str, Any]`

Convert format definition to dictionary for serialization.

```python
format_def = BankFormatDefinition(
    id="my_bank",
    name="My Bank - Checking"
)
data = format_def.to_dict()
```

##### `from_dict(data: dict[str, Any]) -> BankFormatDefinition`

Create format definition from dictionary.

```python
data = {...}
format_def = BankFormatDefinition.from_dict(data)
```

##### `to_yaml() -> str`

Convert format definition to YAML string.

```python
yaml_str = format_def.to_yaml()
print(yaml_str)
# Output:
# id: my_bank
# name: My Bank - Checking
# ...
```

---

### BankFormatRegistry

Registry for managing bank format definitions.

```python
class BankFormatRegistry:
    def __init__(
        self,
        custom_dir: Path | str | None = None,
    ) -> None
```

#### Methods

##### `get_format(format_id: str) -> BankFormatDefinition | None`

Get a format by ID (checks custom formats first, then built-in).

```python
registry = BankFormatRegistry()
chase = registry.get_format("chase_checking")
```

##### `list_formats(institution: str | None = None, format_type: str | None = None, include_custom: bool = True) -> list[BankFormatDefinition]`

List available formats with optional filters.

```python
# All formats
all_formats = registry.list_formats()

# Chase formats only
chase_formats = registry.list_formats(institution="Chase")

# All credit card formats
credit_formats = registry.list_formats(format_type="credit")
```

##### `list_institutions() -> list[str]`

Get list of unique institutions.

```python
institutions = registry.list_institutions()
print(institutions)
# ['Chase', 'Bank of America', 'Wells Fargo', ...]
```

##### `add_custom_format(fmt: BankFormatDefinition) -> None`

Add a custom format (persisted to disk).

```python
custom = BankFormatDefinition(
    id="my_credit_union",
    name="My Credit Union",
    ...
)
registry.add_custom_format(custom)
```

##### `remove_custom_format(format_id: str) -> bool`

Remove a custom format.

```python
removed = registry.remove_custom_format("my_credit_union")
```

##### `detect_format(csv_path: Path | str, *, sample_rows: int = 5) -> BankFormatDefinition | None`

Auto-detect CSV format based on headers.

```python
detected = registry.detect_format("transactions.csv")
if detected:
    print(f"Detected: {detected.name}")
```

##### `validate_format(fmt: BankFormatDefinition, csv_path: Path | str) -> list[str]`

Validate a format against a CSV file.

```python
errors = registry.validate_format(chase_format, "chase_transactions.csv")
if errors:
    print("Validation errors:", errors)
```

---

### FormatBuilder

Interactive builder for creating custom bank formats.

```python
class FormatBuilder:
    def __init__(self) -> None
```

#### Builder Methods

All builder methods return `self` for chaining.

##### `set_institution(name: str) -> FormatBuilder`

##### `set_name(name: str) -> FormatBuilder`

##### `set_format_type(format_type: str) -> FormatBuilder`

Set basic properties.

```python
builder = FormatBuilder()
builder.set_institution("My Bank")
builder.set_name("My Bank - Checking")
builder.set_format_type("checking")
```

##### `set_date_column(column: str, date_format: str = "%Y-%m-%d") -> FormatBuilder`

Set date column and format.

```python
builder.set_date_column("Transaction Date", "%m/%d/%Y")
```

##### `set_amount_column(column: str) -> FormatBuilder`

##### `set_debit_credit_columns(debit: str, credit: str) -> FormatBuilder`

Set amount or separate debit/credit columns.

```python
# Single amount column
builder.set_amount_column("Amount")

# Or separate columns
builder.set_debit_credit_columns("Debit", "Credit")
```

##### `set_description_column(column: str) -> FormatBuilder`

##### `set_memo_column(column: str) -> FormatBuilder`

##### `set_category_column(column: str) -> FormatBuilder`

##### `set_reference_column(column: str) -> FormatBuilder`

##### `set_balance_column(column: str) -> FormatBuilder`

Set optional columns.

##### `set_skip_rows(count: int) -> FormatBuilder`

##### `set_encoding(encoding: str) -> FormatBuilder`

##### `set_delimiter(delimiter: str) -> FormatBuilder`

##### `set_expense_is_negative(value: bool) -> FormatBuilder`

##### `add_header_pattern(pattern: str) -> FormatBuilder`

##### `set_notes(notes: str) -> FormatBuilder`

Set file settings and metadata.

##### `from_csv_headers(csv_path: Path | str) -> FormatBuilder`

Infer format settings from a sample CSV file.

```python
builder.from_csv_headers("sample_export.csv")
```

##### `build(format_id: str) -> BankFormatDefinition`

Build the final format definition.

```python
format_def = builder.build("my_bank_checking")
```

---

## Built-in Formats

### Supported Institutions (50+)

**Major US Banks:**

- Chase (checking, credit)
- Bank of America (checking, credit)
- Wells Fargo (checking, credit)
- Citibank (checking, credit)
- Capital One (checking, credit)
- USAA (checking, credit)
- PNC, TD Bank, US Bank, Regions, Fifth Third, Huntington

**Online Banks:**

- Ally, Discover, Simple, Chime, SoFi, Marcus, Wealthfront, Betterment, Varo, Current

**Credit Cards:**

- American Express, Discover, Barclays, Synchrony, Apple Card

**Credit Unions:**

- Navy Federal, PenFed, Alliant, BECU, DCU

**Investment Accounts:**

- Fidelity, Vanguard, Schwab, E\*TRADE, Robinhood

**Payment Services:**

- PayPal, Venmo, Zelle, Cash App

**International:**

- HSBC, Barclays UK, RBC, TD Canada

**Generic/Aggregators:**

- Mint, YNAB, Quicken, Generic CSV

---

## Convenience Functions

### `get_format(format_id: str) -> BankFormatDefinition | None`

Get a bank format by ID.

```python
from spreadsheet_dl.domains.finance.bank_formats import get_format

chase = get_format("chase_checking")
```

### `list_formats(institution: str | None = None, format_type: str | None = None) -> list[BankFormatDefinition]`

List available bank formats.

```python
from spreadsheet_dl.domains.finance.bank_formats import list_formats

all_formats = list_formats()
credit_formats = list_formats(format_type="credit")
```

### `detect_format(csv_path: Path | str) -> BankFormatDefinition | None`

Auto-detect CSV format.

```python
from spreadsheet_dl.domains.finance.bank_formats import detect_format

detected = detect_format("my_transactions.csv")
```

### `count_formats() -> int`

Get total number of supported formats.

```python
from spreadsheet_dl.domains.finance.bank_formats import count_formats

print(f"{count_formats()} formats supported")  # 50+ formats supported
```

---

## Usage Examples

### Example 1: List All Formats

```python
from spreadsheet_dl.domains.finance.bank_formats import BankFormatRegistry

registry = BankFormatRegistry()
for fmt in registry.list_formats():
    print(f"{fmt.id}: {fmt.name} ({fmt.institution})")
```

### Example 2: Auto-Detect Format

```python
from spreadsheet_dl.domains.finance.bank_formats import detect_format

detected = detect_format("transactions.csv")
if detected:
    print(f"Detected: {detected.name}")
    print(f"Institution: {detected.institution}")
    print(f"Columns: Date={detected.date_column}, Amount={detected.amount_column}")
else:
    print("Could not detect format")
```

### Example 3: Create Custom Format

```python
from spreadsheet_dl.domains.finance.bank_formats import FormatBuilder

builder = FormatBuilder()
format_def = (
    builder
    .set_institution("My Credit Union")
    .set_name("My CU - Checking")
    .set_date_column("Date", "%Y-%m-%d")
    .set_amount_column("Amount")
    .set_description_column("Details")
    .set_memo_column("Notes")
    .add_header_pattern("date")
    .add_header_pattern("amount")
    .add_header_pattern("details")
    .build("my_cu_checking")
)

registry = BankFormatRegistry()
registry.add_custom_format(format_def)
```

### Example 4: Quick Format from CSV

```python
from spreadsheet_dl.domains.finance.bank_formats import FormatBuilder

builder = FormatBuilder()
builder.from_csv_headers("sample_export.csv")
format_def = builder.build("inferred_format")

print(format_def.to_yaml())
```

### Example 5: Validate Format

```python
from spreadsheet_dl.domains.finance.bank_formats import BankFormatRegistry

registry = BankFormatRegistry()
chase_format = registry.get_format("chase_checking")

errors = registry.validate_format(chase_format, "my_transactions.csv")
if not errors:
    print("Format is valid!")
else:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Example 6: Export Format to YAML

```python
from spreadsheet_dl.domains.finance.bank_formats import get_format

chase = get_format("chase_checking")
yaml_content = chase.to_yaml()

# Save to file
with open("chase_format.yaml", "w") as f:
    f.write(yaml_content)
```

### Example 7: Search by Institution

```python
from spreadsheet_dl.domains.finance.bank_formats import BankFormatRegistry

registry = BankFormatRegistry()

# Find all Chase formats
chase_formats = registry.list_formats(institution="Chase")
for fmt in chase_formats:
    print(f"{fmt.id}: {fmt.name}")

# Find all credit card formats
credit_cards = registry.list_formats(format_type="credit")
print(f"Found {len(credit_cards)} credit card formats")
```

### Example 8: Handle Debit/Credit Columns

```python
from spreadsheet_dl.domains.finance.bank_formats import FormatBuilder

# For banks that separate debits and credits
builder = FormatBuilder()
format_def = (
    builder
    .set_institution("Citibank")
    .set_debit_credit_columns("Debit", "Credit")
    .set_date_column("Date", "%m/%d/%Y")
    .set_description_column("Description")
    .set_expense_is_negative(False)  # Amounts are positive
    .build("citi_custom")
)
```

### Example 9: Manage Custom Formats

```python
from spreadsheet_dl.domains.finance.bank_formats import BankFormatRegistry
from pathlib import Path

# Use custom directory
registry = BankFormatRegistry(custom_dir=Path.home() / ".my_formats")

# Add custom format
registry.add_custom_format(my_format)

# List custom only
custom_formats = [f for f in registry.list_formats() if f.id.startswith("my_")]

# Remove custom format
registry.remove_custom_format("my_old_format")
```

### Example 10: Comprehensive Format Builder

```python
from spreadsheet_dl.domains.finance.bank_formats import FormatBuilder

builder = FormatBuilder()
full_format = (
    builder
    .set_institution("Example Bank")
    .set_name("Example Bank - Premium Checking")
    .set_format_type("checking")
    .set_date_column("Transaction Date", "%Y-%m-%d")
    .set_amount_column("Amount")
    .set_description_column("Merchant")
    .set_memo_column("Notes")
    .set_category_column("Type")
    .set_reference_column("Ref #")
    .set_balance_column("Running Balance")
    .set_skip_rows(1)  # Skip header row
    .set_encoding("utf-8")
    .set_delimiter(",")
    .set_expense_is_negative(True)
    .add_header_pattern("transaction date")
    .add_header_pattern("amount")
    .add_header_pattern("merchant")
    .set_notes("Custom format for Example Bank premium accounts")
    .build("example_premium")
)

print(f"Created format: {full_format.name}")
print(f"Date format: {full_format.date_format}")
print(f"Columns mapped: {len([c for c in [full_format.date_column, full_format.amount_column, full_format.description_column] if c])}")
```

---

## Format Types

- `"checking"` - Checking accounts
- `"savings"` - Savings accounts
- `"credit"` - Credit cards
- `"investment"` - Investment accounts

---

## Date Format Patterns

Common date formats used:

- `"%m/%d/%Y"` - 12/31/2024
- `"%Y-%m-%d"` - 2024-12-31
- `"%d/%m/%Y"` - 31/12/2024 (European)
- `"%m/%d/%y"` - 12/31/24
- `"%Y-%m-%dT%H:%M:%S"` - ISO 8601 with time

---

## Notes

- **Custom formats are persisted** to `~/.config/spreadsheet-dl/bank-formats/` as JSON files
- **Built-in formats cover 50+ institutions** including major US banks, credit unions, online banks, and international institutions
- **Auto-detection uses header patterns** to score and match formats
- **Format validation checks** column presence and date format compatibility
- **YAML export** allows sharing formats between users/systems
