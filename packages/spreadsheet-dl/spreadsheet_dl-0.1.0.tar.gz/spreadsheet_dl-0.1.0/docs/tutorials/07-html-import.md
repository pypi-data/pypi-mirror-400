# Tutorial 07: Import Spreadsheets from HTML Tables

Learn how to import spreadsheet data from HTML tables into SpreadsheetDL. This feature is useful for extracting data from web pages, reports, or HTML exports from other systems.

## Prerequisites

Install the HTML import dependencies:

```bash
uv pip install spreadsheet-dl[html]
```

This adds `beautifulsoup4` and `lxml` for HTML parsing.

## Basic HTML Import

### Simple Table Import

Let's start with a basic HTML table:

```python
from pathlib import Path
from spreadsheet_dl.adapters import HtmlAdapter

# HTML file with a simple table
html_content = """
<!DOCTYPE html>
<html>
<body>
    <h2>Employee Data</h2>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Department</th>
                <th>Salary</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Alice Smith</td>
                <td>Engineering</td>
                <td>95000</td>
            </tr>
            <tr>
                <td>Bob Johnson</td>
                <td>Sales</td>
                <td>75000</td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""

# Save to file
html_file = Path("employees.html")
html_file.write_text(html_content)

# Import the table
adapter = HtmlAdapter()
sheets = adapter.import_file(html_file)

# Access the data
sheet = sheets[0]
print(f"Sheet name: {sheet.name}")  # "Employee Data" (from <h2>)
print(f"Columns: {[col.name for col in sheet.columns]}")
print(f"Row count: {len(sheet.rows)}")

# Export to ODS
from spreadsheet_dl.adapters import OdsAdapter
OdsAdapter().export(sheets, Path("employees.ods"))
```

**Key Points:**

- Sheet name is extracted from preceding `<h2>` heading or `<caption>` element
- Headers are detected from `<thead>` or `<th>` cells
- Data types are auto-detected (integers, floats, dates)

## Import Options

### HTMLImportOptions Configuration

Customize import behavior with `HTMLImportOptions`:

```python
from spreadsheet_dl.adapters import HTMLImportOptions

options = HTMLImportOptions(
    table_selector="table.data",  # CSS selector for specific tables
    header_row=True,               # Treat first row as header
    skip_empty_rows=True,          # Skip rows with all empty cells
    trim_whitespace=True,          # Trim leading/trailing whitespace
    detect_types=True,             # Auto-detect int/float/date types
)

sheets = adapter.import_file(html_file, options)
```

### CSS Selector Filtering

Import only specific tables using CSS selectors:

```python
# HTML with multiple tables
html_content = """
<table class="data">
    <tr><th>Important</th></tr>
    <tr><td>Data</td></tr>
</table>
<table class="metadata">
    <tr><th>Metadata</th></tr>
    <tr><td>Info</td></tr>
</table>
"""

html_file.write_text(html_content)

# Import only tables with class="data"
options = HTMLImportOptions(table_selector="table.data")
sheets = adapter.import_file(html_file, options)

assert len(sheets) == 1  # Only "data" table imported
```

## Multiple Tables

Import all tables from a single HTML file:

```python
html_content = """
<html>
<body>
    <h2>Q1 Sales</h2>
    <table>
        <tr><th>Product</th><th>Revenue</th></tr>
        <tr><td>Widget A</td><td>50000</td></tr>
    </table>

    <h2>Q2 Sales</h2>
    <table>
        <tr><th>Product</th><th>Revenue</th></tr>
        <tr><td>Widget B</td><td>75000</td></tr>
    </table>
</body>
</html>
"""

html_file.write_text(html_content)
sheets = adapter.import_file(html_file)

assert len(sheets) == 2
assert sheets[0].name == "Q1 Sales"
assert sheets[1].name == "Q2 Sales"
```

## Handling Merged Cells

### Colspan Support

```python
html_content = """
<table>
    <tr>
        <th colspan="2">Merged Header</th>
        <th>Column C</th>
    </tr>
    <tr>
        <td>A1</td>
        <td>B1</td>
        <td>C1</td>
    </tr>
</table>
"""

html_file.write_text(html_content)
sheets = adapter.import_file(html_file)

# Colspan creates multiple columns
assert len(sheets[0].columns) == 3
assert sheets[0].columns[0].name == "Merged Header"
assert sheets[0].columns[1].name == ""  # Empty from colspan
```

### Rowspan Support

```python
html_content = """
<table>
    <tr>
        <th>Category</th>
        <th>Item</th>
    </tr>
    <tr>
        <td rowspan="2">Fruits</td>
        <td>Apple</td>
    </tr>
    <tr>
        <td>Orange</td>
    </tr>
</table>
"""

html_file.write_text(html_content)
sheets = adapter.import_file(html_file)

# Rowspan cells appear as None in spanned rows
assert sheets[0].rows[0].cells[0].value == "Fruits"
assert sheets[0].rows[1].cells[0].value is None  # Spanned cell
assert sheets[0].rows[1].cells[1].value == "Orange"
```

## Type Detection

SpreadsheetDL automatically detects common data types:

```python
html_content = """
<table>
    <tr>
        <th>Integer</th>
        <th>Float</th>
        <th>Date</th>
        <th>Text</th>
    </tr>
    <tr>
        <td>42</td>
        <td>3.14</td>
        <td>2025-01-15</td>
        <td>Hello</td>
    </tr>
</table>
"""

html_file.write_text(html_content)
sheets = adapter.import_file(html_file)

row = sheets[0].rows[0]
assert isinstance(row.cells[0].value, int)      # 42
assert isinstance(row.cells[1].value, float)    # 3.14
assert isinstance(row.cells[2].value, date)     # date(2025, 1, 15)
assert isinstance(row.cells[3].value, str)      # "Hello"
```

### Supported Date Formats

- ISO format: `2025-01-15`
- US format: `01/15/2025`
- US with dashes: `01-15-2025`
- ISO with slashes: `2025/01/15`

### Disable Type Detection

Keep all values as strings:

```python
options = HTMLImportOptions(detect_types=False)
sheets = adapter.import_file(html_file, options)

# All values are strings
assert isinstance(row.cells[0].value, str)  # "42"
assert isinstance(row.cells[1].value, str)  # "3.14"
```

## Header Detection

### Auto-Detection

Headers are automatically detected from:

1. Rows in `<thead>` section
2. Rows using `<th>` cells instead of `<td>`

```python
# Both work the same
html_with_thead = """
<table>
    <thead>
        <tr><th>Name</th></tr>
    </thead>
    <tbody>
        <tr><td>Alice</td></tr>
    </tbody>
</table>
"""

html_with_th = """
<table>
    <tr><th>Name</th></tr>
    <tr><td>Alice</td></tr>
</table>
"""
```

### Force Header/No Header

```python
# Force first row as header (even if using <td>)
options = HTMLImportOptions(header_row=True)
sheets = adapter.import_file(html_file, options)

# No header row (generate column names)
options = HTMLImportOptions(header_row=False)
sheets = adapter.import_file(html_file, options)
# Columns: "Column_1", "Column_2", etc.
```

## Real-World Example: Import Web Data

Extract financial data from an HTML report:

```python
from pathlib import Path
from spreadsheet_dl.adapters import HtmlAdapter, HTMLImportOptions
from spreadsheet_dl.builder import SpreadsheetBuilder

# HTML financial report
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Q4 2024 Financial Report</title>
</head>
<body>
    <h1>Financial Summary</h1>

    <h2>Revenue by Product</h2>
    <table class="financial-data">
        <thead>
            <tr>
                <th>Product</th>
                <th>Units Sold</th>
                <th>Revenue</th>
                <th>Profit Margin</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Widget Pro</td>
                <td>15000</td>
                <td>375000.00</td>
                <td>0.35</td>
            </tr>
            <tr>
                <td>Widget Lite</td>
                <td>25000</td>
                <td>250000.00</td>
                <td>0.42</td>
            </tr>
        </tbody>
    </table>

    <h2>Quarterly Expenses</h2>
    <table class="financial-data">
        <thead>
            <tr>
                <th>Category</th>
                <th>Q1</th>
                <th>Q2</th>
                <th>Q3</th>
                <th>Q4</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Marketing</td>
                <td>45000</td>
                <td>52000</td>
                <td>48000</td>
                <td>61000</td>
            </tr>
            <tr>
                <td>Operations</td>
                <td>125000</td>
                <td>130000</td>
                <td>128000</td>
                <td>135000</td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""

# Save report
report_file = Path("q4_report.html")
report_file.write_text(html_content)

# Import financial tables
adapter = HtmlAdapter()
options = HTMLImportOptions(
    table_selector="table.financial-data",  # Only financial tables
    skip_empty_rows=True,
    detect_types=True,  # Auto-detect numbers
)

sheets = adapter.import_file(report_file, options)

# Process data
print(f"Imported {len(sheets)} tables:")
for sheet in sheets:
    print(f"  - {sheet.name}: {len(sheet.rows)} rows")

# Export to ODS for further analysis
from spreadsheet_dl.adapters import OdsAdapter
OdsAdapter().export(sheets, Path("q4_analysis.ods"))

# Or use SpreadsheetBuilder for additional formatting
builder = SpreadsheetBuilder()
for sheet in sheets:
    builder.add_sheet(sheet)

builder.theme("professional")
builder.build("q4_formatted.ods")
```

## Advanced: Web Scraping Integration

Combine with `requests` to import live web data:

```python
import requests
from pathlib import Path
from spreadsheet_dl.adapters import HtmlAdapter, HTMLImportOptions

# Fetch HTML from web (example - respect robots.txt and terms of service!)
# url = "https://example.com/data-table"
# response = requests.get(url)
# html_content = response.text

# For this example, use local file
html_content = """
<h2>Live Stock Prices</h2>
<table>
    <tr>
        <th>Symbol</th>
        <th>Price</th>
        <th>Change</th>
    </tr>
    <tr>
        <td>AAPL</td>
        <td>175.43</td>
        <td>+2.15</td>
    </tr>
    <tr>
        <td>GOOGL</td>
        <td>142.87</td>
        <td>-1.32</td>
    </tr>
</table>
"""

# Save and import
temp_file = Path("stocks.html")
temp_file.write_text(html_content)

adapter = HtmlAdapter()
sheets = adapter.import_file(temp_file)

# Export to ODS
from spreadsheet_dl.adapters import OdsAdapter
OdsAdapter().export(sheets, Path("stocks.ods"))

print(f"Imported {len(sheets[0].rows)} stock prices")
```

## Limitations

### Known Limitations

1. **Nested Tables**: Nested tables are found separately, not as single merged structure
2. **Complex Formatting**: CSS styles are not imported (only structure and data)
3. **Formulas**: HTML tables don't contain formulas, only values
4. **Images**: Images in cells are not imported
5. **Comments**: HTML comments are ignored

### Unsupported HTML

```python
# Will skip or handle gracefully
html_content = """
<table>
    <tr>
        <td>
            <!-- Nested table - will be found separately -->
            <table>
                <tr><td>Inner</td></tr>
            </table>
        </td>
    </tr>
</table>
"""
```

## Error Handling

### No Tables Found

```python
from spreadsheet_dl.adapters import HtmlAdapter

html_file = Path("no_tables.html")
html_file.write_text("<html><body><p>No tables here</p></body></html>")

adapter = HtmlAdapter()
try:
    sheets = adapter.import_file(html_file)
except ValueError as e:
    print(f"Error: {e}")  # "No HTML tables found"
```

### Missing Dependencies

```python
# If beautifulsoup4/lxml not installed
try:
    sheets = adapter.import_file(html_file)
except ImportError as e:
    print(f"Install dependencies: uv pip install spreadsheet-dl[html]")
```

## Best Practices

### 1. Use CSS Selectors

```python
# Import only data tables, skip navigation/layout tables
options = HTMLImportOptions(
    table_selector="table.data, table[data-type='financial']"
)
```

### 2. Handle Empty Rows

```python
# Skip empty rows for cleaner data
options = HTMLImportOptions(skip_empty_rows=True)
```

### 3. Validate Imported Data

```python
sheets = adapter.import_file(html_file)

# Validate structure
for sheet in sheets:
    if len(sheet.rows) == 0:
        print(f"Warning: {sheet.name} is empty")

    # Check expected columns
    expected_cols = ["Name", "Amount", "Date"]
    actual_cols = [col.name for col in sheet.columns]
    if actual_cols != expected_cols:
        print(f"Column mismatch: expected {expected_cols}, got {actual_cols}")
```

### 4. Type Detection Trade-offs

```python
# Enable for numeric/date data
options = HTMLImportOptions(detect_types=True)

# Disable for text data with number-like strings (e.g., "001", "42A")
options = HTMLImportOptions(detect_types=False)
```

## Summary

**HTML import features:**

- Parse HTML tables to SheetSpec
- Handle `<thead>`, `<tbody>`, `<tfoot>`
- Handle `<th>` vs `<td>` cells
- Handle colspan/rowspan
- CSS selector filtering
- Auto-detect types (int, float, date)
- Multiple tables per file
- Round-trip export/import

**Next Steps:**

- See [Tutorial 03: Import Bank Data](03-import-bank-data.md) for CSV import
- See [Tutorial 05: Use MCP Tools](05-use-mcp-tools.md) for automated workflows
- Check [API Reference](../api/adapters.md) for complete `HtmlAdapter` documentation

**Resources:**

- BeautifulSoup4 documentation: https://www.crummy.com/software/BeautifulSoup/
- CSS selectors reference: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors
