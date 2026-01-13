# Migration Guide

**Implements: DOC-PROF-006: Migration Guide | v0.1 Documentation**

This guide helps you migrate from other spreadsheet tools (openpyxl, pandas, Excel VBA) to the universal SpreadsheetDL v0.1.

Future versions of this guide will include migration instructions when upgrading between major versions of SpreadsheetDL.

## Table of Contents

1. [Future Version Migration](#future-version-migration)
2. [Migrating from Basic API to Builder API](#migrating-from-basic-api-to-builder-api)
3. [Migrating from openpyxl](#migrating-from-openpyxl)
4. [Migrating from pandas](#migrating-from-pandas)
5. [Migrating from Excel VBA](#migrating-from-excel-vba)
6. [Migrating Themes](#migrating-themes)

## Future Version Migration

SpreadsheetDL v0.1.0 is the first public release. Migration guides will be provided for future versions as they are released.

### Breaking Changes Policy

SpreadsheetDL follows [Semantic Versioning](https://semver.org/):

- **Major versions** (v1.0, v2.0, etc.) may include breaking changes
- **Minor versions** (v0.2, v0.3, etc.) add features without breaking existing code
- **Patch versions** (v0.1.1, v0.1.2, etc.) fix bugs without breaking existing code

When a new major version is released, this guide will provide detailed migration instructions.

## Migrating from Basic API to Builder API

### Before: Procedural Style

```python
from spreadsheet_dl.ods_generator import ODSGenerator

gen = ODSGenerator()
sheet = gen.create_sheet("Expenses")

# Add headers manually
gen.add_row(["Date", "Description", "Amount"])

# Add data rows
for expense in expenses:
    gen.add_row([
        expense.date,
        expense.description,
        expense.amount,
    ])

# Add total
gen.add_row(["", "Total", "=SUM(C2:C100)"])

gen.save("expenses.ods")
```

### After: Builder Pattern

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="corporate")

builder.sheet("Expenses")

# Define columns
builder.column("Date", width="80pt", type="date")
builder.column("Description", width="200pt")
builder.column("Amount", width="100pt", type="currency")

# Add header
builder.header_row(style="header_primary")

# Add data
for expense in expenses:
    builder.row()
    builder.cell(expense.date)
    builder.cell(expense.description)
    builder.cell(expense.amount)

# Add total with style
builder.total_row(
    style="total",
    formulas=["", "Total", "=SUM(C2:C{})".format(len(expenses) + 1)],
)

builder.save("expenses.ods")
```

### Key Differences

| Aspect      | Basic API       | Builder API             |
| ----------- | --------------- | ----------------------- |
| Styling     | Inline dicts    | Named styles from theme |
| Structure   | Imperative      | Declarative             |
| Reusability | Copy-paste      | Templates               |
| Maintenance | Edit everywhere | Edit theme once         |

## Migrating from openpyxl

If you're currently using openpyxl for Excel files, here's how to migrate.

### openpyxl Original

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
ws = wb.active
ws.title = "Budget"

# Headers
headers = ["Category", "Budget", "Actual"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="4472C4")
    cell.alignment = Alignment(horizontal="center")

# Data
data = [("Housing", 2000, 1800), ("Food", 500, 450)]
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        ws.cell(row=row_idx, column=col_idx, value=value)

# Total row
ws.cell(row=4, column=1, value="Total")
ws.cell(row=4, column=2, value="=SUM(B2:B3)")
ws.cell(row=4, column=3, value="=SUM(C2:C3)")

wb.save("budget.xlsx")
```

### spreadsheet-dl Equivalent

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="corporate")

builder.sheet("Budget")
builder.column("Category", width="100pt")
builder.column("Budget", type="currency")
builder.column("Actual", type="currency")

builder.header_row(style="header_primary")

data = [("Housing", 2000, 1800), ("Food", 500, 450)]
for category, budget, actual in data:
    builder.row()
    builder.cell(category)
    builder.cell(budget, style="currency")
    builder.cell(actual, style="currency")

builder.total_row(
    formulas=["Total", "=SUM(B2:B3)", "=SUM(C2:C3)"],
    style="total",
)

builder.save("budget.ods")
```

### Style Mapping

| openpyxl                         | spreadsheet-dl                      |
| -------------------------------- | ----------------------------------- |
| `Font(bold=True)`                | `font_weight: bold` in style        |
| `PatternFill("solid", ...)`      | `background_color: "#..."`          |
| `Alignment(horizontal="center")` | `text_align: center`                |
| `Border(...)`                    | `border_top`, `border_bottom`, etc. |
| `NumberFormat(...)`              | `number_format: { category: ... }`  |

## Migrating from pandas

pandas DataFrames can be easily converted.

### pandas to_excel

```python
import pandas as pd

df = pd.DataFrame({
    "Category": ["Housing", "Food", "Transport"],
    "Budget": [2000, 500, 300],
    "Actual": [1800, 450, 350],
})

df.to_excel("budget.xlsx", index=False)
```

### spreadsheet-dl with DataFrame

```python
import pandas as pd
from spreadsheet_dl.builder import SpreadsheetBuilder

df = pd.DataFrame({
    "Category": ["Housing", "Food", "Transport"],
    "Budget": [2000, 500, 300],
    "Actual": [1800, 450, 350],
})

builder = SpreadsheetBuilder(theme="corporate")
builder.sheet("Budget")

# Define columns with types
for col in df.columns:
    col_type = "currency" if col in ["Budget", "Actual"] else "string"
    builder.column(col, type=col_type)

builder.header_row()

# Add data from DataFrame
for _, row in df.iterrows():
    builder.row()
    for value in row:
        builder.cell(value)

# Add total row
builder.total_row(formulas=[
    "Total",
    f"=SUM(B2:B{len(df)+1})",
    f"=SUM(C2:C{len(df)+1})",
])

builder.save("budget.ods")
```

### Helper Function

```python
def dataframe_to_spreadsheet(
    df: pd.DataFrame,
    filename: str,
    theme: str = "default",
    currency_columns: list[str] = None,
) -> None:
    """Convert DataFrame to ODS with professional formatting."""
    currency_columns = currency_columns or []

    builder = SpreadsheetBuilder(theme=theme)
    builder.sheet("Data")

    # Columns
    for col in df.columns:
        col_type = "currency" if col in currency_columns else "string"
        builder.column(col, type=col_type)

    builder.header_row()

    # Data
    for _, row in df.iterrows():
        builder.row()
        for col, value in row.items():
            style = "currency" if col in currency_columns else None
            builder.cell(value, style=style)

    builder.save(filename)
```

## Migrating from Excel VBA

### VBA Macro

```vba
Sub CreateBudget()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets.Add
    ws.Name = "Budget"

    ' Headers
    ws.Range("A1:C1").Value = Array("Category", "Budget", "Actual")
    ws.Range("A1:C1").Font.Bold = True
    ws.Range("A1:C1").Interior.Color = RGB(68, 114, 196)
    ws.Range("A1:C1").Font.Color = vbWhite

    ' Data
    ws.Range("A2").Value = "Housing"
    ws.Range("B2").Value = 2000
    ws.Range("C2").Value = 1800

    ' Total
    ws.Range("A3").Value = "Total"
    ws.Range("B3").Formula = "=SUM(B2:B2)"
    ws.Range("C3").Formula = "=SUM(C2:C2)"
End Sub
```

### Python Equivalent

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

def create_budget():
    builder = SpreadsheetBuilder(theme="corporate")
    builder.sheet("Budget")

    # Columns (headers defined here)
    builder.column("Category")
    builder.column("Budget", type="currency")
    builder.column("Actual", type="currency")

    # Header row with styling from theme
    builder.header_row(style="header_primary")

    # Data
    builder.row()
    builder.cell("Housing")
    builder.cell(2000)
    builder.cell(1800)

    # Total
    builder.total_row(
        formulas=["Total", "=SUM(B2:B2)", "=SUM(C2:C2)"],
    )

    builder.save("budget.ods")
```

### VBA Concept Mapping

| VBA Concept            | Python Equivalent                 |
| ---------------------- | --------------------------------- |
| `Worksheet`            | `builder.sheet()`                 |
| `Range.Value`          | `builder.cell(value)`             |
| `Range.Formula`        | `builder.cell(formula="...")`     |
| `Range.Font.Bold`      | Style: `font_weight: bold`        |
| `Range.Interior.Color` | Style: `background_color: "#..."` |
| `Range.NumberFormat`   | Style: `number_format: {...}`     |
| `Cells(row, col)`      | `builder.cell()` in row context   |

## Migrating Themes

### From CSS/HTML Styles

```css
/* CSS */
.header {
  background-color: #4472c4;
  color: white;
  font-weight: bold;
  text-align: center;
  border-bottom: 2px solid #2f4a82;
}
```

```yaml
# spreadsheet-dl theme
styles:
  header:
    background_color: '#4472C4'
    font_color: '#FFFFFF'
    font_weight: bold
    text_align: center
    border_bottom:
      width: '2pt'
      style: solid
      color: '#2F4A82'
```

### From Excel Styles

```python
# Excel style object
{
    "font": {"bold": True, "size": 12, "color": "FFFFFF"},
    "fill": {"patternType": "solid", "fgColor": "4472C4"},
    "alignment": {"horizontal": "center"},
}
```

```yaml
# spreadsheet-dl style
header_primary:
  font_weight: bold
  font_size: '12pt'
  font_color: '#FFFFFF'
  background_color: '#4472C4'
  text_align: center
```

## Migration Checklist

### Before Migration

- [ ] Document current spreadsheet structure
- [ ] List all styles/formatting used
- [ ] Identify formulas and calculations
- [ ] Note data validation rules
- [ ] Review conditional formatting

### During Migration

- [ ] Create theme with all styles
- [ ] Convert to builder pattern
- [ ] Test formula compatibility
- [ ] Verify data validation
- [ ] Check print layout

### After Migration

- [ ] Validate output against original
- [ ] Test with real data
- [ ] Review accessibility
- [ ] Update documentation

## Getting Help

If you encounter issues during migration:

1. Check the [API Reference](../api/builder.md)
2. Review [Best Practices](best-practices.md)
3. See [Examples](../examples/index.md)
4. Open an issue on GitHub

## See Also

- [Builder API Reference](../api/builder.md)
- [Theme Creation Guide](./theme-creation.md)
- [Style Composition Guide](./style-composition.md)
