# Example Gallery

**Implements: DOC-PROF-007: Example Gallery**

This gallery showcases practical examples of professional spreadsheet creation
using the spreadsheet-dl library.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Budget Examples](#budget-examples)
3. [Financial Statement Examples](#financial-statement-examples)
4. [Chart Examples](#chart-examples)
5. [Conditional Formatting Examples](#conditional-formatting-examples)
6. [Data Validation Examples](#data-validation-examples)
7. [Template Examples](#template-examples)
8. [Advanced Examples](#advanced-examples)

## Quick Start Examples

### Minimal Spreadsheet

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

# Create a simple spreadsheet
builder = SpreadsheetBuilder()
builder.sheet("Data")
builder.column("Name")
builder.column("Amount", type="currency")
builder.header_row()
builder.row().cell("Item 1").cell(100)
builder.row().cell("Item 2").cell(200)
builder.save("simple.ods")
```

### Spreadsheet with Theme

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="corporate")

builder.workbook_properties(
    title="Sales Report",
    author="Sales Team",
)

builder.sheet("Q1 Sales")
builder.column("Product", width="150pt")
builder.column("Revenue", type="currency")
builder.column("Units", type="number")

builder.header_row(style="header_primary")

builder.row().cell("Widget A").cell(15000).cell(150)
builder.row().cell("Widget B").cell(22500).cell(225)
builder.row().cell("Widget C").cell(18000).cell(180)

builder.total_row(formulas=["Total", "=SUM(B2:B4)", "=SUM(C2:C4)"])

builder.save("sales_report.ods")
```

## Budget Examples

### Simple Monthly Budget

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="corporate")

builder.sheet("Budget")
builder.column("Category", width="150pt")
builder.column("Budget", type="currency")
builder.column("Actual", type="currency")
builder.column("Variance", type="currency")
builder.column("% Used", type="percentage")

builder.freeze(rows=1)
builder.header_row(style="header_primary")

# Add categories
categories = [
    ("Housing", 2000, 1950),
    ("Utilities", 200, 225),
    ("Groceries", 600, 580),
    ("Transport", 300, 320),
    ("Entertainment", 200, 180),
]

for i, (cat, budget, actual) in enumerate(categories, start=2):
    builder.row()
    builder.cell(cat)
    builder.cell(budget, style="currency")
    builder.cell(actual, style="currency")
    builder.cell(f"=B{i}-C{i}", style="currency_variance")
    builder.cell(f"=IF(B{i}=0,0,C{i}/B{i})", style="percentage")

# Total row
last_row = len(categories) + 1
builder.total_row(formulas=[
    "Total",
    f"=SUM(B2:B{last_row})",
    f"=SUM(C2:C{last_row})",
    f"=B{last_row+1}-C{last_row+1}",
    f"=IF(B{last_row+1}=0,0,C{last_row+1}/B{last_row+1})",
])

builder.save("monthly_budget.ods")
```

### Enterprise Budget Template

```python
from spreadsheet_dl.templates import EnterpriseBudgetTemplate, BudgetCategory

template = EnterpriseBudgetTemplate(
    fiscal_year=2024,
    departments=["Engineering", "Sales", "Marketing", "Operations"],
    categories=[
        BudgetCategory("Personnel", ["Salaries", "Benefits", "Training"]),
        BudgetCategory("Operations", ["Rent", "Utilities", "Supplies"]),
        BudgetCategory("Technology", ["Software", "Hardware", "Cloud"]),
    ],
    include_quarterly=True,
    include_variance=True,
)

builder = template.generate()
builder.save("enterprise_budget_2024.ods")
```

## Financial Statement Examples

### Income Statement

```python
from spreadsheet_dl.templates.financial_statements import IncomeStatementTemplate

template = IncomeStatementTemplate(
    company_name="ACME Corporation",
    period="Year Ended December 31, 2024",
    comparative=True,
    revenue_items=[
        "Product Sales",
        "Service Revenue",
        "Licensing Revenue",
    ],
    operating_expenses=[
        "Cost of Goods Sold",
        "Selling & Marketing",
        "General & Administrative",
        "Research & Development",
    ],
)

builder = template.generate()
builder.save("income_statement.ods")
```

### Balance Sheet

```python
from spreadsheet_dl.templates.financial_statements import BalanceSheetTemplate

template = BalanceSheetTemplate(
    company_name="ACME Corporation",
    as_of_date="December 31, 2024",
    comparative=True,
)

builder = template.generate()
builder.save("balance_sheet.ods")
```

### Cash Flow Statement

```python
from spreadsheet_dl.templates.financial_statements import CashFlowStatementTemplate

template = CashFlowStatementTemplate(
    company_name="ACME Corporation",
    period="Year Ended December 31, 2024",
    method="indirect",
    comparative=True,
)

builder = template.generate()
builder.save("cash_flow_statement.ods")
```

## Chart Examples

### Column Chart with Budget vs Actual

```python
from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl.charts import ChartBuilder

builder = SpreadsheetBuilder(theme="corporate")

builder.sheet("Data")
# ... add data ...

# Create chart
chart = (
    ChartBuilder()
    .column_chart()
    .title("Budget vs Actual by Category")
    .series("Budget", "Data.B2:B6", categories="Data.A2:A6")
    .series("Actual", "Data.C2:C6")
    .x_axis(title="Category")
    .y_axis(title="Amount ($)")
    .legend(position="bottom")
    .build()
)

builder.chart(chart)
builder.save("budget_chart.ods")
```

### Pie Chart for Expense Breakdown

```python
from spreadsheet_dl.charts import ChartBuilder

chart = (
    ChartBuilder()
    .pie_chart()
    .title("Expense Distribution")
    .series("Expenses", "Data.B2:B8", categories="Data.A2:A8")
    .data_labels(show_percentage=True)
    .legend(position="right")
    .build()
)
```

### Line Chart with Trendline

```python
from spreadsheet_dl.charts import ChartBuilder, TrendlineType

chart = (
    ChartBuilder()
    .line_chart()
    .title("Monthly Revenue Trend")
    .series("Revenue", "Data.B2:B13", categories="Data.A2:A13")
    .trendline(TrendlineType.LINEAR, forecast_forward=3)
    .x_axis(title="Month")
    .y_axis(title="Revenue ($)")
    .build()
)
```

### Sparklines in Cells

```python
from spreadsheet_dl.charts import SparklineBuilder, SparklineType

sparkline = (
    SparklineBuilder()
    .line()
    .data_range("B2:M2")
    .target_cell("N2")
    .high_point("#70AD47")
    .low_point("#C00000")
    .build()
)
```

## Conditional Formatting Examples

### Budget Variance Highlighting

```python
from spreadsheet_dl.builders.conditional import ConditionalFormatBuilder

# Highlight variances
format = (
    ConditionalFormatBuilder()
    .range("D2:D100")
    .when_value().less_than(0).style("danger")
    .when_value().less_than_formula("B2*0.1").style("warning")
    .when_value().greater_than_or_equal(0).style("success")
    .build()
)
```

### Color Scale for Percentages

```python
from spreadsheet_dl.builders.conditional import ConditionalFormatBuilder

format = (
    ConditionalFormatBuilder()
    .range("E2:E100")
    .color_scale()
        .min_color("#F8696B")   # Red at 0%
        .mid_color("#FFEB84")   # Yellow at 50%
        .max_color("#63BE7B")   # Green at 100%
    .build()
)
```

### Data Bars for Visual Comparison

```python
from spreadsheet_dl.builders.conditional import ConditionalFormatBuilder

format = (
    ConditionalFormatBuilder()
    .range("C2:C50")
    .data_bar()
        .fill("#4472C4")
        .negative("#C00000")
        .gradient()
    .build()
)
```

### Icon Sets for Status

```python
from spreadsheet_dl.builders.conditional import ConditionalFormatBuilder

format = (
    ConditionalFormatBuilder()
    .range("F2:F100")
    .icon_set()
        .three_arrows()
        .hide_value()
    .build()
)
```

## Data Validation Examples

### Category Dropdown

```python
from spreadsheet_dl.schema.data_validation import (
    DataValidation,
    InputMessage,
    ErrorAlert,
)

validation = DataValidation.list(
    items=["Housing", "Food", "Transport", "Utilities", "Entertainment"],
    input_message=InputMessage("Category", "Select expense category"),
    error_alert=ErrorAlert.stop("Invalid", "Please select from list"),
)
```

### Positive Number Validation

```python
from spreadsheet_dl.schema.data_validation import DataValidation

validation = DataValidation.positive_number(
    allow_zero=True,
    input_message=InputMessage("Amount", "Enter positive amount"),
)
```

### Date Range Validation

```python
from datetime import date
from spreadsheet_dl.schema.data_validation import DataValidation

validation = DataValidation.date_between(
    date(2024, 1, 1),
    date(2024, 12, 31),
    input_message=InputMessage("Date", "Enter date in 2024"),
)
```

### Custom Formula Validation

```python
from spreadsheet_dl.schema.data_validation import DataValidation

# Value must not exceed budget
validation = DataValidation.custom(
    formula="=C2<=B2",
    error_alert=ErrorAlert.warning(
        "Over Budget",
        "This value exceeds the budget amount"
    ),
)
```

## Template Examples

### Invoice Template

```python
from spreadsheet_dl.templates import InvoiceTemplate

template = InvoiceTemplate(
    company_name="Your Business LLC",
    company_address="123 Main Street, City, State 12345",
    company_phone="(555) 123-4567",
    company_email="billing@yourbusiness.com",
    invoice_number="INV-2024-001",
    tax_rate=0.08,
)

builder = template.generate()
builder.save("invoice.ods")
```

### Expense Report Template

```python
from spreadsheet_dl.templates import ExpenseReportTemplate

template = ExpenseReportTemplate(
    employee_name="John Smith",
    department="Engineering",
    report_period="November 2024",
)

builder = template.generate()
builder.save("expense_report.ods")
```

### Cash Flow Tracker

```python
from spreadsheet_dl.templates import CashFlowTrackerTemplate

template = CashFlowTrackerTemplate(
    start_date="2024-01-01",
    periods=12,
    period_type="monthly",
    opening_balance=50000.00,
    include_projections=True,
)

builder = template.generate()
builder.save("cash_flow_tracker.ods")
```

## Advanced Examples

### Print-Ready Report

```python
from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl.schema import (
    PageSetup,
    PageSize,
    PageOrientation,
    HeaderFooter,
    HeaderFooterContent,
    RepeatConfig,
)

builder = SpreadsheetBuilder(theme="corporate")

# ... build spreadsheet ...

# Configure print layout
page_setup = PageSetup(
    size=PageSize.A4,
    orientation=PageOrientation.LANDSCAPE,
    header=HeaderFooter(
        center=HeaderFooterContent("Budget Report 2024", bold=True),
        right=HeaderFooterContent.page_number(),
    ),
    footer=HeaderFooter(
        left=HeaderFooterContent.date_time(),
        right=HeaderFooterContent.file_name(),
    ),
    repeat=RepeatConfig.header_row(),
    print_gridlines=True,
)

# Apply to sheet
builder.page_setup(page_setup)
builder.save("printable_report.ods")
```

### Multi-Sheet Workbook

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="corporate")

builder.workbook_properties(
    title="Q1 Financial Package",
    author="Finance Team",
)

# Summary sheet
builder.sheet("Summary")
builder.column("Metric", width="200pt")
builder.column("Value", type="currency")
builder.header_row()
builder.row().cell("Total Revenue").cell("=Revenue.F10")
builder.row().cell("Total Expenses").cell("=Expenses.F100")
builder.row().cell("Net Income").cell("=B2-B3")

# Revenue detail sheet
builder.sheet("Revenue")
# ... build revenue sheet ...

# Expenses detail sheet
builder.sheet("Expenses")
# ... build expenses sheet ...

builder.save("q1_financial_package.ods")
```

### Dashboard with Charts

```python
from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl.charts import ChartBuilder

builder = SpreadsheetBuilder(theme="corporate")

builder.sheet("Dashboard")

# KPI section
builder.row(style="header_primary")
builder.cell("Key Performance Indicators", colspan=4)

# KPI cards
kpis = [
    ("Revenue", "$1.2M", "+12%"),
    ("Expenses", "$800K", "+5%"),
    ("Profit", "$400K", "+25%"),
    ("Margin", "33%", "+3%"),
]

builder.row()
for name, value, change in kpis:
    builder.cell(name, style="kpi_label")

builder.row()
for name, value, change in kpis:
    builder.cell(value, style="kpi_value")

builder.row()
for name, value, change in kpis:
    builder.cell(change, style="kpi_change")

# Add charts
revenue_chart = (
    ChartBuilder()
    .column_chart()
    .title("Monthly Revenue")
    .series("Revenue", "Data.B2:B13")
    .position(cell="A10", width="400pt", height="250pt")
    .build()
)

builder.chart(revenue_chart)
builder.save("dashboard.ods")
```

## See Also

- [Builder API Reference](../api/builder.md)
- [Theme Creation Guide](../guides/theme-creation.md)
- [Best Practices](../guides/best-practices.md)
