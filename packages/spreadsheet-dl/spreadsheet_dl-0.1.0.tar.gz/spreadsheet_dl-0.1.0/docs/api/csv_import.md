# csv_import - CSV Transaction Import

CSV import module for importing bank transactions from CSV exports with automatic categorization and multi-bank format support.

## Overview

The csv_import module provides comprehensive CSV import functionality for bank and credit card transactions:

- Import from 8+ pre-configured bank formats
- Automatic transaction categorization using regex patterns
- Flexible date and amount parsing
- Filter by date range and transaction type
- Auto-detection of CSV format
- Extensible custom categorization rules

## Key Features

- **Multi-Bank Support**: Pre-configured formats for Chase, Bank of America, Wells Fargo, Capital One, Discover, Amex, USAA, and generic CSV
- **Auto-Categorization**: 15+ category rules with pattern matching
- **Flexible Parsing**: Handles various date formats, debit/credit columns, and amount conventions
- **Smart Filtering**: Filter by date range and expense vs. income
- **Progress Tracking**: Progress bar for large imports (>100 rows)
- **Format Detection**: Automatic bank format detection from headers

## Classes

### BankFormat

```python
@dataclass
class BankFormat:
    """Configuration for a bank's CSV format."""
    name: str
    date_column: str
    amount_column: str
    description_column: str
    date_format: str = "%m/%d/%Y"
    debit_column: str | None = None
    credit_column: str | None = None
    memo_column: str | None = None
    skip_rows: int = 0
    expense_is_negative: bool = True
    amount_preprocessor: Callable[[str], str] | None = None
```

Configuration for parsing a specific bank's CSV format.

**Attributes:**

- `name`: Display name of the bank
- `date_column`: CSV column name for transaction date
- `amount_column`: CSV column name for amount
- `description_column`: CSV column name for merchant/description
- `date_format`: strptime format string for parsing dates
- `debit_column`: Optional separate debit column
- `credit_column`: Optional separate credit column
- `memo_column`: Optional notes/memo column
- `skip_rows`: Number of header rows to skip
- `expense_is_negative`: Whether expenses are negative amounts
- `amount_preprocessor`: Optional function to preprocess amount strings

### CategoryRule

```python
@dataclass
class CategoryRule:
    """Rule for automatic transaction categorization."""
    pattern: str  # Regex pattern to match description
    category: ExpenseCategory
    case_sensitive: bool = False
    priority: int = 0
```

Defines a pattern-matching rule for categorizing transactions.

**Attributes:**

- `pattern`: Regex pattern to match against transaction description
- `category`: Category to assign on match
- `case_sensitive`: Whether pattern matching is case-sensitive
- `priority`: Rule priority (higher = checked first)

### TransactionCategorizer

```python
@dataclass
class TransactionCategorizer:
    """Automatic transaction categorizer using pattern matching."""
    rules: list[CategoryRule] = field(default_factory=lambda: DEFAULT_CATEGORY_RULES.copy())
    default_category: ExpenseCategory = ExpenseCategory.MISCELLANEOUS

    def add_rule(
        self,
        pattern: str,
        category: ExpenseCategory,
        priority: int = 0,
        case_sensitive: bool = False,
    ) -> None:
        """Add a custom categorization rule."""

    def categorize(self, description: str) -> ExpenseCategory:
        """Categorize a transaction based on its description."""

    def categorize_with_confidence(
        self,
        description: str,
    ) -> tuple[ExpenseCategory, float]:
        """Categorize with confidence score (0.0-1.0)."""
```

Automatic transaction categorizer using regex pattern matching.

#### Methods

##### `add_rule(pattern, category, priority=0, case_sensitive=False)`

Add a custom categorization rule.

**Parameters:**

- `pattern` (str): Regex pattern to match
- `category` (ExpenseCategory): Category to assign on match
- `priority` (int): Rule priority, higher values checked first
- `case_sensitive` (bool): Whether pattern is case-sensitive

**Example:**

```python
categorizer = TransactionCategorizer()
categorizer.add_rule(
    r"my local store",
    ExpenseCategory.GROCERIES,
    priority=15  # Higher than default rules
)
```

##### `categorize(description)`

Categorize a transaction based on its description.

**Parameters:**

- `description` (str): Transaction description/merchant name

**Returns:**

- `ExpenseCategory`: Matched category or default category

##### `categorize_with_confidence(description)`

Categorize with a confidence score.

**Parameters:**

- `description` (str): Transaction description

**Returns:**

- `tuple[ExpenseCategory, float]`: Category and confidence score (0.0-1.0)

### CSVImporter

```python
class CSVImporter:
    """Import transactions from bank CSV files."""

    def __init__(
        self,
        bank_format: BankFormat | str = "generic",
        categorizer: TransactionCategorizer | None = None,
    ) -> None:
        """Initialize CSV importer."""

    def import_file(
        self,
        csv_path: Path | str,
        filter_expenses_only: bool = True,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ExpenseEntry]:
        """Import transactions from a CSV file."""

    @staticmethod
    def detect_format(csv_path: Path | str) -> str | None:
        """Attempt to detect the bank format from CSV headers."""
```

Main CSV importer class.

#### Methods

##### `__init__(bank_format="generic", categorizer=None)`

Initialize the CSV importer.

**Parameters:**

- `bank_format` (BankFormat | str): Bank format config or preset name
- `categorizer` (TransactionCategorizer | None): Custom categorizer (uses default if None)

**Raises:**

- `ValueError`: If bank format name is unknown

##### `import_file(csv_path, filter_expenses_only=True, start_date=None, end_date=None)`

Import transactions from a CSV file.

**Parameters:**

- `csv_path` (Path | str): Path to CSV file
- `filter_expenses_only` (bool): Only import expenses, skip income
- `start_date` (date | None): Filter transactions from this date
- `end_date` (date | None): Filter transactions until this date

**Returns:**

- `list[ExpenseEntry]`: List of imported expense entries

**Raises:**

- `FileNotFoundError`: If CSV file doesn't exist

**Example:**

```python
from spreadsheet_dl.csv_import import CSVImporter

# Import Chase transactions
importer = CSVImporter("chase")
expenses = importer.import_file(
    "chase_export.csv",
    filter_expenses_only=True,
    start_date=date(2024, 1, 1)
)

print(f"Imported {len(expenses)} expenses")
```

##### `detect_format(csv_path)` (static)

Attempt to auto-detect the bank format from CSV headers.

**Parameters:**

- `csv_path` (Path | str): Path to CSV file

**Returns:**

- `str | None`: Detected bank format name or None

**Example:**

```python
format_name = CSVImporter.detect_format("unknown_bank.csv")
print(f"Detected format: {format_name}")

importer = CSVImporter(format_name)
expenses = importer.import_file("unknown_bank.csv")
```

## Constants

### BANK_FORMATS

```python
BANK_FORMATS: dict[str, BankFormat]
```

Pre-configured bank formats dictionary. Available formats:

- `"chase"`: Chase Bank checking accounts
- `"chase_credit"`: Chase credit cards
- `"bank_of_america"`: Bank of America
- `"wells_fargo"`: Wells Fargo
- `"capital_one"`: Capital One (debit/credit columns)
- `"discover"`: Discover credit cards
- `"amex"`: American Express
- `"usaa"`: USAA
- `"generic"`: Generic CSV with standard columns

### DEFAULT_CATEGORY_RULES

```python
DEFAULT_CATEGORY_RULES: list[CategoryRule]
```

Default categorization rules covering common merchants and categories:

**Groceries**: Whole Foods, Trader Joe's, Safeway, Kroger, Publix, Wegmans, Aldi, Costco, Walmart, Target, Instacart

**Dining Out**: McDonald's, Burger King, Wendy's, Chick-fil-A, Chipotle, Starbucks, Dunkin', Panera, Subway, Pizza places, DoorDash, Uber Eats, Grubhub

**Transportation**: Shell, Exxon, Chevron, BP, Speedway, Uber, Lyft, Parking, Tolls, Transit, Amtrak

**Utilities**: Electric, Water, Gas, Power, Energy, Internet providers (Comcast, Verizon, AT&T, Spectrum)

**Healthcare**: Pharmacy (CVS, Walgreens, Rite Aid), Doctors, Hospitals, Medical, Dental, Vision, Clinics

**Entertainment**: Netflix, Hulu, Disney+, HBO, Spotify, Apple Music, YouTube, Movies, Concerts, Ticketmaster, Gyms

**Subscriptions**: Streaming services, Monthly memberships

**Housing**: Rent, Mortgage, HOA, Property tax, Home insurance

**Insurance**: Geico, Progressive, State Farm, Allstate, Liberty Mutual

**Clothing**: Retail stores, Apparel shops

**Personal Care**: Haircut, Salon, Barber, Spa, Beauty products

**Education**: Tuition, School, University, Courses, Textbooks, Online learning

**Gifts**: Gift shops, Flowers, Edible Arrangements

## Convenience Functions

### import_bank_csv

```python
def import_bank_csv(
    csv_path: Path | str,
    bank: str = "auto",
    filter_expenses: bool = True,
) -> list[ExpenseEntry]:
    """Convenience function to import bank CSV."""
```

Quick import with auto-detection.

**Parameters:**

- `csv_path` (Path | str): Path to CSV file
- `bank` (str): Bank name or "auto" for auto-detection
- `filter_expenses` (bool): Only import expenses

**Returns:**

- `list[ExpenseEntry]`: List of imported expenses

**Example:**

```python
from spreadsheet_dl.csv_import import import_bank_csv

# Auto-detect format and import
expenses = import_bank_csv("transactions.csv", bank="auto")
```

## Usage Examples

### Basic Import

```python
from spreadsheet_dl.csv_import import CSVImporter

# Import from Chase
importer = CSVImporter("chase")
expenses = importer.import_file("chase_export.csv")

for expense in expenses:
    print(f"{expense.date}: {expense.description} - ${expense.amount}")
```

### Auto-Detection

```python
from spreadsheet_dl.csv_import import import_bank_csv

# Let the importer detect the bank format
expenses = import_bank_csv("unknown_bank.csv", bank="auto")
```

### Date Range Filtering

```python
from datetime import date

importer = CSVImporter("chase_credit")
expenses = importer.import_file(
    "transactions.csv",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 3, 31)
)
print(f"Q1 2024: {len(expenses)} expenses")
```

### Custom Categorization Rules

```python
from spreadsheet_dl.csv_import import CSVImporter, TransactionCategorizer, CategoryRule
from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory

# Create custom categorizer
categorizer = TransactionCategorizer()

# Add custom rules
categorizer.add_rule(
    r"my local cafe",
    ExpenseCategory.DINING_OUT,
    priority=15  # Higher priority than defaults
)

categorizer.add_rule(
    r"company gym",
    ExpenseCategory.ENTERTAINMENT,
    priority=15
)

# Use custom categorizer
importer = CSVImporter("chase", categorizer=categorizer)
expenses = importer.import_file("transactions.csv")
```

### Categorization with Confidence

```python
categorizer = TransactionCategorizer()

description = "STARBUCKS #12345"
category, confidence = categorizer.categorize_with_confidence(description)

print(f"Category: {category.name}")
print(f"Confidence: {confidence:.0%}")
# Output: Category: DINING_OUT, Confidence: 70%
```

### Custom Bank Format

```python
from spreadsheet_dl.csv_import import CSVImporter, BankFormat

# Define custom bank format
my_bank = BankFormat(
    name="My Credit Union",
    date_column="Trans Date",
    date_format="%Y-%m-%d",
    amount_column="Amount",
    description_column="Merchant",
    memo_column="Notes",
    expense_is_negative=True
)

# Use custom format
importer = CSVImporter(my_bank)
expenses = importer.import_file("my_bank.csv")
```

### Include Income Transactions

```python
# Import all transactions (expenses and income)
importer = CSVImporter("chase")
all_transactions = importer.import_file(
    "transactions.csv",
    filter_expenses_only=False
)

expenses = [t for t in all_transactions if t.amount > 0]
income = [t for t in all_transactions if t.amount < 0]

print(f"Expenses: {len(expenses)}, Income: {len(income)}")
```

## Supported Bank Formats

### Chase

- **Format**: `"chase"` or `"chase_credit"`
- **Date Format**: MM/DD/YYYY
- **Columns**: Posting Date, Description, Amount
- **Convention**: Negative amounts = expenses

### Bank of America

- **Format**: `"bank_of_america"`
- **Date Format**: MM/DD/YYYY
- **Columns**: Date, Description, Amount
- **Convention**: Negative amounts = expenses

### Wells Fargo

- **Format**: `"wells_fargo"`
- **Date Format**: MM/DD/YYYY
- **Columns**: Date, Amount, Description
- **Convention**: Negative amounts = expenses

### Capital One

- **Format**: `"capital_one"`
- **Date Format**: YYYY-MM-DD
- **Columns**: Transaction Date, Debit, Credit, Description
- **Convention**: Separate debit/credit columns

### Discover

- **Format**: `"discover"`
- **Date Format**: MM/DD/YYYY
- **Columns**: Trans. Date, Description, Amount
- **Convention**: Negative amounts = expenses

### American Express

- **Format**: `"amex"`
- **Date Format**: MM/DD/YYYY
- **Columns**: Date, Description, Amount
- **Convention**: Positive amounts = expenses

### USAA

- **Format**: `"usaa"`
- **Date Format**: YYYY-MM-DD
- **Columns**: Date, Description, Amount
- **Convention**: Negative amounts = expenses

### Generic

- **Format**: `"generic"`
- **Date Format**: YYYY-MM-DD
- **Columns**: Date, Amount, Description
- **Convention**: Negative amounts = expenses

## Performance

- **Small files (<100 rows)**: Instant import
- **Medium files (100-1000 rows)**: Progress bar shown, ~1-3 seconds
- **Large files (>1000 rows)**: Progress bar shown, ~3-15 seconds

Progress tracking is automatically enabled for files with more than 100 rows.

## Related Modules

- [bank_formats](bank_formats.md) - Extended bank format support (50+ banks)
- [plaid_integration](plaid_integration.md) - Direct bank API integration
- [ods_generator](ods_generator.md) - Generate ODS from expense entries
- [export](export.md) - Export to multiple formats

## Notes

- All imported amounts are stored as positive values in `ExpenseEntry`
- The `expense_is_negative` convention is handled during import
- UTF-8-SIG encoding is used to handle BOM in CSV files
- Duplicate transactions are not automatically detected
- For advanced bank format management, see [bank_formats](bank_formats.md) module
