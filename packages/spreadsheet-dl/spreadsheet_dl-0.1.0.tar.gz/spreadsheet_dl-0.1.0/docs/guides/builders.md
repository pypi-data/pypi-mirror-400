# Builder Pattern Guide

**Implements:** DOC-PROF-003 (Builder Pattern Guide)

This guide explains the fluent builder pattern used throughout SpreadsheetDL for constructing spreadsheets, formulas, and charts.

## Overview

SpreadsheetDL uses the **Builder Pattern** to provide a fluent, chainable API for spreadsheet construction. This pattern offers several advantages:

- **Readability**: Code reads like natural language
- **Discoverability**: IDE autocomplete guides you through options
- **Safety**: Type hints catch errors at development time
- **Flexibility**: Optional configuration without dozens of parameters

## Core Builders

SpreadsheetDL provides three main builders:

| Builder              | Purpose                      | Import                                                       |
| -------------------- | ---------------------------- | ------------------------------------------------------------ |
| `SpreadsheetBuilder` | Create multi-sheet workbooks | `from spreadsheet_dl.builder import SpreadsheetBuilder`      |
| `FormulaBuilder`     | Construct type-safe formulas | `from spreadsheet_dl.builder import FormulaBuilder, formula` |
| `ChartBuilder`       | Create charts and sparklines | `from spreadsheet_dl.charts import ChartBuilder`             |

## SpreadsheetBuilder Basics

### Creating a Builder

```python
from spreadsheet_dl.builder import SpreadsheetBuilder, create_spreadsheet

# Method 1: Direct instantiation
builder = SpreadsheetBuilder(theme="corporate")

# Method 2: Convenience function
builder = create_spreadsheet(theme="default")
```

### Fluent Chaining

All builder methods return `self`, enabling method chaining:

```python
builder = SpreadsheetBuilder(theme="professional") \
    .workbook_properties(title="Sales Report", author="Sales Team") \
    .sheet("Q4 Sales") \
    .column("Region", width="120pt") \
    .column("Revenue", width="100pt", type="currency") \
    .column("Growth", width="80pt", type="percentage") \
    .freeze(rows=1) \
    .header_row(style="header") \
    .row().cells("North", 150000, 0.12) \
    .row().cells("South", 125000, 0.08) \
    .row().cells("East", 180000, 0.15) \
    .row().cells("West", 145000, 0.10) \
    .total_row(formulas=["Total", "=SUM(B2:B5)", "=AVERAGE(C2:C5)"])
```

### Builder Lifecycle

1. **Configure** workbook properties (optional)
2. **Create** sheets with columns
3. **Add** rows and cells
4. **Apply** formatting and charts
5. **Build** or **Save**

```python
# Build returns sheet specifications (for inspection/testing)
sheets = builder.build()

# Save writes the ODS file
output_path = builder.save("report.ods")
```

## Sheet Operations

### Creating Sheets

```python
builder.sheet("Summary")  # Create new sheet
builder.sheet("Details")  # Create another sheet
```

### Column Definition

Define columns before adding rows:

```python
builder.sheet("Budget") \
    .column("Category", width="150pt", style="text") \
    .column("Budget", width="100pt", type="currency") \
    .column("Actual", width="100pt", type="currency") \
    .column("Variance", width="100pt", type="currency")
```

**Column Parameters:**

- `name`: Column header text
- `width`: Width with units (pt, cm, px)
- `type`: Value type (string, currency, date, percentage)
- `style`: Default cell style
- `hidden`: Hide column (default: False)

### Freezing Panes

Freeze rows/columns for scrolling:

```python
builder.sheet("Data") \
    .freeze(rows=1)           # Freeze header row
    .freeze(cols=1)           # Freeze first column
    .freeze(rows=2, cols=1)   # Freeze both
```

## Row Operations

### Header Row

Automatically generates from column names:

```python
builder.header_row(style="header_primary")
```

### Data Rows

Add individual rows:

```python
builder.row(style="data") \
    .cell("Category A") \
    .cell(1500.00) \
    .cell(1450.00) \
    .cell(formula="=B2-C2")
```

Or add multiple cells at once:

```python
builder.row().cells("Category A", 1500.00, 1450.00, "=B2-C2")
```

### Bulk Data Rows

Create empty rows for data entry:

```python
# Simple: 20 empty rows
builder.data_rows(20)

# With zebra striping
builder.data_rows(20, alternate_styles=["row_even", "row_odd"])
```

### Total Row

Add a summary row with formulas:

```python
builder.total_row(
    style="total",
    formulas=[
        "Total",
        "=SUM(B2:B21)",
        "=SUM(C2:C21)",
        "=B22-C22"
    ]
)
```

## Cell Operations

### Basic Cells

```python
builder.row() \
    .cell("Text value") \
    .cell(1234.56) \
    .cell(0.15, value_type="percentage") \
    .cell(formula="=SUM(A1:A10)")
```

### Cell Formatting

```python
builder.cell(
    value=1500.00,
    style="currency_positive",
    colspan=2,        # Span multiple columns
    rowspan=1,        # Span multiple rows
    value_type="currency"
)
```

### Formula Cells

```python
# Direct formula string
builder.cell(formula="=SUM(B2:B10)")

# Using FormulaBuilder
from spreadsheet_dl.builder import formula

f = formula()
builder.cell(formula=f.sum(f.range("B2", "B10")))
```

## FormulaBuilder

### Creating Formulas

```python
from spreadsheet_dl.builder import FormulaBuilder, formula

# Convenience function
f = formula()

# Or direct instantiation
f = FormulaBuilder()
```

### Cell References

```python
# Simple reference
ref = f.cell("A1")          # -> [.A1]

# Absolute reference
ref = f.cell("A1").absolute()  # -> $A$1

# Range reference
rng = f.range("A1", "A100")    # -> [.A1:A100]

# Cross-sheet reference
sheet = f.sheet("Budget")
rng = sheet.range("B2", "B50")  # -> ['Budget'.B2:B50]
```

### Common Functions

```python
# Mathematical
f.sum(f.range("A1", "A10"))       # SUM
f.average(f.range("A1", "A10"))   # AVERAGE
f.round("A1", 2)                   # ROUND

# Logical
f.if_expr("[.A1]>0", "Yes", "No")  # IF
f.iferror("A1/B1", 0)              # IFERROR

# Lookup
f.vlookup("A1", f.range("D:F"), 2) # VLOOKUP
f.index_match(                      # INDEX/MATCH
    f.range("C:C"),
    f.match("A2", f.range("B:B"))
)

# Financial
f.pmt("B1/12", "B2*12", "B3")      # PMT (loan payment)
f.npv("B1", f.range("C2", "C10"))  # NPV
```

### Building Formula Strings

```python
# Get the formula string
formula_str = f.sum(f.range("B2", "B10"))
# -> "of:=SUM([.B2:B10])"

# Use in builder
builder.cell(formula=formula_str)
```

## ChartBuilder

### Creating Charts

```python
from spreadsheet_dl.charts import ChartBuilder

chart = ChartBuilder() \
    .column_chart() \
    .title("Sales by Region") \
    .categories("Sheet1.A2:A5") \
    .series("2023", "Sheet1.B2:B5", color="#4472C4") \
    .series("2024", "Sheet1.C2:C5", color="#ED7D31") \
    .legend(position="bottom") \
    .position("E2") \
    .size(400, 300) \
    .build()

builder.sheet("Report").chart(chart)
```

### Chart Types

```python
chart.column_chart()    # Vertical bars
chart.bar_chart()       # Horizontal bars
chart.line_chart()      # Line graph
chart.area_chart()      # Filled area
chart.pie_chart()       # Pie/donut
chart.scatter_chart()   # X-Y scatter
```

## Best Practices

### 1. Use Method Chaining

```python
# Good: Fluent chain
builder.sheet("Data") \
    .column("Name") \
    .column("Value") \
    .header_row() \
    .row().cells("Item 1", 100)

# Avoid: Breaking chain unnecessarily
builder.sheet("Data")
builder.column("Name")
builder.column("Value")
```

### 2. Define Columns First

```python
# Good: Columns before rows
builder.sheet("Budget") \
    .column("Category") \
    .column("Amount") \
    .header_row() \
    .row().cells("Food", 500)

# Bad: Adding cells without columns
builder.sheet("Budget") \
    .row().cells("Food", 500)  # No column definitions
```

### 3. Use Named Ranges

```python
builder.named_range("BudgetData", "B2", "B50", sheet="Budget")

f = formula()
total = f.sum(f.sheet("Budget").range("BudgetData"))
```

### 4. Separate Complex Formulas

```python
from spreadsheet_dl.builder import formula

f = formula()

# Define complex formulas separately
variance_formula = f.if_expr(
    f.cell("B2") + ">" + f.cell("C2"),
    f.cell("B2") + "-" + f.cell("C2"),
    "0"
)

# Use in builder
builder.cell(formula=variance_formula)
```

## Complete Example

```python
from spreadsheet_dl.builder import SpreadsheetBuilder, formula
from spreadsheet_dl.charts import ChartBuilder

# Create builder with theme
builder = SpreadsheetBuilder(theme="professional")

# Set workbook metadata
builder.workbook_properties(
    title="Q4 2024 Budget Report",
    author="Finance Department",
    keywords=["budget", "q4", "2024"],
)

# Create Budget sheet
f = formula()

builder.sheet("Budget") \
    .column("Category", width="150pt") \
    .column("Budget", width="100pt", type="currency") \
    .column("Actual", width="100pt", type="currency") \
    .column("Variance", width="100pt", type="currency") \
    .column("Status", width="80pt") \
    .freeze(rows=1) \
    .header_row(style="header") \
    .row().cells("Salaries", 50000, 48500) \
    .row().cells("Marketing", 15000, 17200) \
    .row().cells("Operations", 25000, 24100) \
    .row().cells("IT", 10000, 9800) \
    .total_row(formulas=[
        "Total",
        "=SUM(B2:B5)",
        "=SUM(C2:C5)",
        "=SUM(D2:D5)",
        None
    ])

# Add variance formulas
for row in range(2, 6):
    builder.sheet("Budget")
    # Variance = Budget - Actual
    # Status = IF(Variance >= 0, "OK", "Over")

# Add chart
chart = ChartBuilder() \
    .column_chart() \
    .title("Budget vs Actual") \
    .categories("Budget.A2:A5") \
    .series("Budget", "Budget.B2:B5", color="#4472C4") \
    .series("Actual", "Budget.C2:C5", color="#ED7D31") \
    .legend(position="bottom") \
    .position("G2") \
    .size(450, 300) \
    .build()

builder.chart(chart)

# Save
builder.save("q4_budget_report.ods")
```

## See Also

- [Builder API Reference](../api/builder.md) - Complete API documentation
- [Formula Reference](../api/builder.md) - All formula functions
- [Chart Reference](../api/charts.md) - Chart builder API
- [Theme System](./theme-creation.md) - Custom themes
- [Style Composition](./style-composition.md) - Style inheritance
