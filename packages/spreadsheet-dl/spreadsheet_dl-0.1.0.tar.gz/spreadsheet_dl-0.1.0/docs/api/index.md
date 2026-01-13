# API Reference

Complete API documentation for SpreadsheetDL v0.1.

## Module Overview

### Core Modules

| Module                                | Description                   |
| ------------------------------------- | ----------------------------- |
| [ods_generator](ods_generator.md)     | Create ODS spreadsheets       |
| [ods_editor](ods_editor.md)           | Modify existing ODS files     |
| [builder](builder.md)                 | Fluent builder API            |
| [charts](charts.md)                   | Chart builder and types       |
| [template_engine](template_engine.md) | Template system               |
| [mcp_server](mcp_server.md)           | MCP server for AI integration |

### v0.1 Modules

| Module                            | Description                        |
| --------------------------------- | ---------------------------------- |
| [streaming](streaming.md)         | Stream-based I/O for large files   |
| [serialization](serialization.md) | Round-trip JSON/YAML serialization |
| [adapters](adapters.md)           | Multi-format export/import         |
| [performance](performance.md)     | Caching, lazy loading, benchmarks  |

### Budget & Finance

| Module                                | Description                |
| ------------------------------------- | -------------------------- |
| [budget_analyzer](budget_analyzer.md) | Analyze budget data        |
| [accounts](accounts.md)               | Account management         |
| [categories](categories.md)           | Custom category management |
| [csv_import](csv_import.md)           | Import bank CSV files      |
| [recurring](recurring.md)             | Recurring expenses         |
| [alerts](alerts.md)                   | Budget alert system        |

### Reporting & Visualization

| Module                                  | Description                     |
| --------------------------------------- | ------------------------------- |
| [report_generator](report_generator.md) | Generate reports                |
| [visualization](visualization.md)       | Interactive charts & dashboards |
| [analytics](analytics.md)               | Dashboard analytics             |

### Security & Configuration

| Module                      | Description              |
| --------------------------- | ------------------------ |
| [security](security.md)     | Encryption & credentials |
| [config](config.md)         | Configuration management |
| [exceptions](exceptions.md) | Exception classes        |

### Integration

| Module                            | Description      |
| --------------------------------- | ---------------- |
| [webdav_upload](webdav_upload.md) | Nextcloud WebDAV |
| [templates](templates.md)         | Budget templates |

## Quick Reference

### Creating Budgets

```python
from spreadsheet_dl import OdsGenerator, create_monthly_budget

# Simple creation
path = create_monthly_budget("./budgets")

# With options
generator = OdsGenerator(theme="corporate")
generator.create_budget_spreadsheet(
    "budget.ods",
    month=1,
    year=2025,
)
```

### Adding Expenses

```python
from spreadsheet_dl import OdsEditor, ExpenseEntry, ExpenseCategory
from decimal import Decimal
from datetime import date

# Edit existing file
editor = OdsEditor("budget.ods")
editor.append_expense(ExpenseEntry(
    date=date.today(),
    category=ExpenseCategory.GROCERIES,
    description="Weekly shopping",
    amount=Decimal("125.50"),
))
editor.save()
```

### Using the Builder API

```python
from spreadsheet_dl import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="professional")
builder.sheet("Budget") \
    .column("Category", width="150pt") \
    .column("Budget", type="currency") \
    .column("Actual", type="currency") \
    .header_row() \
    .row().cells("Housing", 1500, 1450) \
    .row().cells("Groceries", 500, 480) \
    .total_row(formulas=["Total", "=SUM(B2:B3)", "=SUM(C2:C3)"])

builder.save("budget_report.ods")
```

### Streaming Large Files

```python
from spreadsheet_dl import stream_read, stream_write

# Read large file row by row
with stream_read("large_file.ods") as reader:
    for row in reader.rows("Data"):
        process_row(row)

# Write large file in chunks
with stream_write("output.ods") as writer:
    writer.start_sheet("Data", columns=["A", "B", "C"])
    for chunk in data_generator():
        writer.write_rows(chunk)
```

### Multi-Format Export

```python
from spreadsheet_dl import export_to, import_from

# Export to various formats
export_to(sheets, "data.csv")
export_to(sheets, "data.json")
export_to(sheets, "data.html")

# Import from various formats
sheets = import_from("data.csv")
```

### Performance Optimization

```python
from spreadsheet_dl import cached, LRUCache, batch_process

# Cache expensive computations
@cached(maxsize=100, ttl=3600)
def analyze_budget(budget_id: str) -> dict:
    return expensive_analysis(budget_id)

# Process items in batches
result = batch_process(
    items=large_list,
    processor=process_item,
    batch_size=100
)
print(f"Processed {result.success_count} items")
```

### Account Management

```python
from spreadsheet_dl import AccountManager, AccountType
from decimal import Decimal

manager = AccountManager("accounts.json")

# Add accounts
checking = manager.add_account(
    name="Primary Checking",
    account_type=AccountType.CHECKING,
    balance=Decimal("5000")
)

# Transfer funds
manager.transfer(checking.id, savings.id, Decimal("500"))

# Calculate net worth
net_worth = manager.calculate_net_worth()
print(f"Net worth: ${net_worth.net_worth:,.2f}")
```

### File Encryption

```python
from spreadsheet_dl import FileEncryptor

encryptor = FileEncryptor()
encryptor.encrypt_file("budget.ods", "budget.ods.enc", "password")
encryptor.decrypt_file("budget.ods.enc", "budget.ods", "password")
```

### Interactive Visualization

```python
from spreadsheet_dl import create_budget_dashboard, BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")
create_budget_dashboard(analyzer, "dashboard.html", theme="dark")
```

## Core Classes

### OdsGenerator

Creates new ODS spreadsheets.

```python
class OdsGenerator:
    def __init__(
        self,
        theme: str | Theme | None = None,
        theme_dir: Path | str | None = None,
    ) -> None: ...

    def create_budget_spreadsheet(
        self,
        output_path: Path | str,
        *,
        month: int | None = None,
        year: int | None = None,
        budget_allocations: Sequence[BudgetAllocation] | None = None,
        expenses: Sequence[ExpenseEntry] | None = None,
    ) -> Path: ...
```

### OdsEditor

Modifies existing ODS files.

```python
class OdsEditor:
    def __init__(self, file_path: Path | str) -> None: ...

    def append_expense(
        self,
        expense: ExpenseEntry,
        sheet_name: str = "Expense Log",
    ) -> int: ...

    def save(self, output_path: Path | str | None = None) -> Path: ...
```

### SpreadsheetBuilder

Fluent builder for creating spreadsheets.

```python
class SpreadsheetBuilder:
    def __init__(self, theme: str | None = "default") -> None: ...

    def sheet(self, name: str) -> Self: ...
    def column(self, name: str, **kwargs) -> Self: ...
    def row(self, **kwargs) -> Self: ...
    def cell(self, value: Any = None, **kwargs) -> Self: ...
    def save(self, path: Path | str) -> Path: ...
```

### BudgetAnalyzer

Analyzes budget data.

```python
class BudgetAnalyzer:
    def __init__(self, file_path: Path | str) -> None: ...

    def get_summary(self) -> BudgetSummary: ...
    def filter_by_category(self, category: str) -> pd.DataFrame: ...
    def filter_by_date_range(self, start: date, end: date) -> pd.DataFrame: ...
```

## Data Classes

### ExpenseEntry

```python
@dataclass
class ExpenseEntry:
    date: date
    category: ExpenseCategory
    description: str
    amount: Decimal
    notes: str = ""
```

### BudgetAllocation

```python
@dataclass
class BudgetAllocation:
    category: ExpenseCategory
    monthly_budget: Decimal
    notes: str = ""
```

### ExpenseCategory

```python
class ExpenseCategory(Enum):
    HOUSING = "Housing"
    UTILITIES = "Utilities"
    GROCERIES = "Groceries"
    TRANSPORTATION = "Transportation"
    HEALTHCARE = "Healthcare"
    INSURANCE = "Insurance"
    ENTERTAINMENT = "Entertainment"
    DINING_OUT = "Dining Out"
    CLOTHING = "Clothing"
    PERSONAL = "Personal Care"
    EDUCATION = "Education"
    SAVINGS = "Savings"
    DEBT_PAYMENT = "Debt Payment"
    GIFTS = "Gifts"
    SUBSCRIPTIONS = "Subscriptions"
    MISCELLANEOUS = "Miscellaneous"
```

## Exceptions

All exceptions inherit from `SpreadsheetDLError`:

```python
class SpreadsheetDLError(Exception):
    message: str
    error_code: str

class OdsError(SpreadsheetDLError): ...
class OdsReadError(OdsError): ...
class OdsWriteError(OdsError): ...
class SheetNotFoundError(OdsError): ...

class ValidationError(SpreadsheetDLError): ...
class InvalidAmountError(ValidationError): ...
class InvalidDateError(ValidationError): ...
class InvalidCategoryError(ValidationError): ...

class EncryptionError(SpreadsheetDLError): ...
class DecryptionError(SpreadsheetDLError): ...
class IntegrityError(SpreadsheetDLError): ...
```

## Type Hints

The library is fully typed. Common type aliases:

```python
from pathlib import Path
from decimal import Decimal
from datetime import date
from typing import Sequence

# Path can be string or Path object
def func(path: Path | str) -> Path: ...

# Sequences accept lists, tuples, etc.
def func(items: Sequence[ExpenseEntry]) -> None: ...
```

## Version History

- **v0.1.0**: Universal Spreadsheet Definition Language with MCP server integration, 10+ domain plugins, streaming I/O, multi-format adapters, comprehensive performance optimization
- **Pre-4.0**: Professional templates, charts, conditional formatting, goals tracking, account management, multi-currency support, backup/restore, builder API, themes, security features

For detailed version history and migration guides, see [CHANGELOG.md](../CHANGELOG.md) and [Migration Guide](../guides/migration-guide.md)
