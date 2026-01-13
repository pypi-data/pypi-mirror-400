# SpreadsheetDL Cookbook

**Implements: DOC-PROF-010: Cookbook | PHASE-12: Documentation Expansion**

A collection of 25+ practical recipes for common spreadsheet tasks using SpreadsheetDL v0.1.0. Each recipe includes complete, working code examples.

## Table of Contents

1. [Basic Recipes](#basic-recipes)
2. [Financial Recipes](#financial-recipes)
3. [Data Import/Export](#data-importexport)
4. [Chart Recipes](#chart-recipes)
5. [Styling Recipes](#styling-recipes)
6. [Formula Recipes](#formula-recipes)
7. [MCP Server Recipes](#mcp-server-recipes)
8. [CLI Automation](#cli-automation)
9. [Anti-Patterns](#anti-patterns)

## Basic Recipes

### Recipe 1: Create a Simple Budget

**Use Case**: Create a monthly budget spreadsheet with categories and totals.

```python
from spreadsheet_dl import SpreadsheetBuilder

def create_monthly_budget(output_path: str = "budget.ods"):
    """Create a simple monthly budget spreadsheet."""
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Budget")
    builder.column("Category", width="150pt")
    builder.column("Budgeted", width="100pt", type="currency")
    builder.column("Actual", width="100pt", type="currency")
    builder.column("Difference", width="100pt", type="currency")

    builder.header_row()

    # Budget data
    categories = [
        ("Housing", 2000, 1950),
        ("Food", 500, 520),
        ("Transportation", 300, 280),
        ("Entertainment", 200, 150),
        ("Utilities", 150, 145),
        ("Insurance", 250, 250),
        ("Savings", 800, 800),
    ]

    row_num = 2
    for category, budgeted, actual in categories:
        builder.row()
        builder.cell(category)
        builder.cell(budgeted)
        builder.cell(actual)
        builder.cell(f"=C{row_num}-B{row_num}")  # Difference
        row_num += 1

    # Total row
    builder.row()
    builder.cell("Total", style="total")
    builder.cell(f"=SUM(B2:B{row_num-1})", style="total")
    builder.cell(f"=SUM(C2:C{row_num-1})", style="total")
    builder.cell(f"=SUM(D2:D{row_num-1})", style="total")

    builder.save(output_path)
    return output_path

# Usage
create_monthly_budget()
```

**Output**: Professional budget spreadsheet with automatic calculations.

### Recipe 2: Import CSV to Spreadsheet

**Use Case**: Convert CSV data to a formatted ODS spreadsheet.

```python
from spreadsheet_dl import SpreadsheetBuilder
import pandas as pd

def csv_to_ods(csv_path: str, output_path: str, theme: str = "default"):
    """Convert CSV to formatted ODS."""
    # Read CSV
    df = pd.read_csv(csv_path)

    # Create spreadsheet
    builder = SpreadsheetBuilder(theme=theme)
    builder.sheet("Data")

    # Add columns
    for col in df.columns:
        # Detect column type
        if df[col].dtype == 'float64':
            col_type = "number"
        elif df[col].dtype == 'int64':
            col_type = "integer"
        elif "date" in col.lower():
            col_type = "date"
        elif "amount" in col.lower() or "price" in col.lower():
            col_type = "currency"
        else:
            col_type = "string"

        builder.column(col, type=col_type, width="120pt")

    builder.header_row()

    # Add data
    for _, row in df.iterrows():
        builder.row()
        for value in row:
            builder.cell(value)

    # Add summary info
    builder.row()  # Blank row
    builder.row()
    builder.cell("Total Rows:", style="total")
    builder.cell(len(df), style="total")

    builder.save(output_path)
    return output_path

# Usage
csv_to_ods("transactions.csv", "transactions.ods", theme="corporate")
```

**Best Practice**: Always detect column types for proper formatting.

### Recipe 3: Multi-Sheet Workbook

**Use Case**: Create a workbook with multiple related sheets.

```python
from spreadsheet_dl import SpreadsheetBuilder

def create_annual_report(year: int, output_path: str = "annual_report.ods"):
    """Create annual report with quarterly sheets."""
    builder = SpreadsheetBuilder(theme="corporate")

    quarters = ["Q1", "Q2", "Q3", "Q4"]
    quarterly_data = {
        "Q1": {"revenue": 250000, "expenses": 180000},
        "Q2": {"revenue": 280000, "expenses": 195000},
        "Q3": {"revenue": 310000, "expenses": 210000},
        "Q4": {"revenue": 340000, "expenses": 225000},
    }

    # Create a sheet for each quarter
    for quarter in quarters:
        builder.sheet(quarter)
        builder.column("Metric", width="150pt")
        builder.column("Amount", width="120pt", type="currency")

        builder.header_row()

        data = quarterly_data[quarter]
        builder.row()
        builder.cell("Revenue")
        builder.cell(data["revenue"])

        builder.row()
        builder.cell("Expenses")
        builder.cell(data["expenses"])

        builder.row()
        builder.cell("Profit", style="total")
        builder.cell("=B2-B3", style="total")

    # Summary sheet
    builder.sheet("Annual Summary")
    builder.column("Quarter", width="100pt")
    builder.column("Revenue", width="120pt", type="currency")
    builder.column("Expenses", width="120pt", type="currency")
    builder.column("Profit", width="120pt", type="currency")

    builder.header_row()

    for i, quarter in enumerate(quarters, start=2):
        builder.row()
        builder.cell(quarter)
        builder.cell(f"={quarter}.B2")  # Cross-sheet reference
        builder.cell(f"={quarter}.B3")
        builder.cell(f"={quarter}.B4")

    # Annual totals
    builder.row()
    builder.cell("Annual Total", style="total")
    builder.cell(f"=SUM(B2:B5)", style="total")
    builder.cell(f"=SUM(C2:C5)", style="total")
    builder.cell(f"=SUM(D2:D5)", style="total")

    builder.save(output_path)
    return output_path

# Usage
create_annual_report(2025)
```

**Tip**: Use cross-sheet references to link data between sheets.

## Financial Recipes

### Recipe 4: Loan Amortization Schedule

**Use Case**: Calculate monthly loan payments and amortization.

```python
from spreadsheet_dl import SpreadsheetBuilder
from spreadsheet_dl.builder import formula

def create_loan_schedule(
    principal: float,
    annual_rate: float,
    years: int,
    output_path: str = "loan_schedule.ods"
):
    """Create loan amortization schedule."""
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Loan Schedule")

    # Loan parameters
    builder.row()
    builder.cell("Principal Amount:")
    builder.cell(principal, style="currency")

    builder.row()
    builder.cell("Annual Interest Rate:")
    builder.cell(annual_rate / 100, style="percent")

    builder.row()
    builder.cell("Loan Term (years):")
    builder.cell(years)

    builder.row()
    builder.cell("Monthly Payment:")
    # PMT formula: =PMT(rate/12, years*12, -principal)
    builder.cell(
        f"=PMT({annual_rate/100}/12, {years}*12, -{principal})",
        style="currency"
    )

    # Amortization table
    builder.row()  # Blank
    builder.row()

    builder.column("Month", width="80pt", type="integer")
    builder.column("Payment", width="100pt", type="currency")
    builder.column("Principal", width="100pt", type="currency")
    builder.column("Interest", width="100pt", type="currency")
    builder.column("Balance", width="100pt", type="currency")

    builder.header_row()

    # Calculate monthly payment
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    monthly_payment = (principal * monthly_rate * (1 + monthly_rate)**num_payments) / \
                      ((1 + monthly_rate)**num_payments - 1)

    balance = principal

    for month in range(1, num_payments + 1):
        interest = balance * monthly_rate
        principal_payment = monthly_payment - interest
        balance -= principal_payment

        builder.row()
        builder.cell(month)
        builder.cell(monthly_payment)
        builder.cell(principal_payment)
        builder.cell(interest)
        builder.cell(max(0, balance))  # Avoid negative due to rounding

    builder.save(output_path)
    return output_path

# Usage
create_loan_schedule(
    principal=300000,
    annual_rate=4.5,
    years=30
)
```

**Financial Functions**: Use PMT, IPMT, PPMT for loan calculations.

### Recipe 5: Investment Portfolio Tracker

**Use Case**: Track investment portfolio with returns.

```python
from spreadsheet_dl import SpreadsheetBuilder, ChartBuilder

def create_portfolio_tracker(
    holdings: list[dict],
    output_path: str = "portfolio.ods"
):
    """Create investment portfolio tracker.

    Args:
        holdings: List of dicts with keys: symbol, shares, purchase_price, current_price
    """
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Holdings")
    builder.column("Symbol", width="80pt")
    builder.column("Shares", width="80pt", type="number")
    builder.column("Purchase Price", width="120pt", type="currency")
    builder.column("Current Price", width="120pt", type="currency")
    builder.column("Cost Basis", width="120pt", type="currency")
    builder.column("Current Value", width="120pt", type="currency")
    builder.column("Gain/Loss", width="120pt", type="currency")
    builder.column("Return %", width="100pt", type="percent")

    builder.header_row()

    row_num = 2
    for holding in holdings:
        builder.row()
        builder.cell(holding["symbol"])
        builder.cell(holding["shares"])
        builder.cell(holding["purchase_price"])
        builder.cell(holding["current_price"])
        builder.cell(f"=B{row_num}*C{row_num}")  # Cost basis
        builder.cell(f"=B{row_num}*D{row_num}")  # Current value
        builder.cell(f"=F{row_num}-E{row_num}")  # Gain/Loss
        builder.cell(f"=G{row_num}/E{row_num}")  # Return %
        row_num += 1

    # Portfolio summary
    builder.row()
    builder.cell("Total", style="total")
    builder.cell("", style="total")
    builder.cell("", style="total")
    builder.cell("", style="total")
    builder.cell(f"=SUM(E2:E{row_num-1})", style="total")
    builder.cell(f"=SUM(F2:F{row_num-1})", style="total")
    builder.cell(f"=SUM(G2:G{row_num-1})", style="total")
    builder.cell(f"=G{row_num}/E{row_num}", style="total")

    # Add chart
    chart = ChartBuilder() \
        .pie_chart() \
        .title("Portfolio Allocation") \
        .series("Current Value", f"F2:F{row_num-1}", categories=f"A2:A{row_num-1}") \
        .position(cell="J2", width="400pt", height="300pt") \
        .build()

    builder.chart(chart)

    builder.save(output_path)
    return output_path

# Usage
holdings = [
    {"symbol": "AAPL", "shares": 50, "purchase_price": 150, "current_price": 180},
    {"symbol": "GOOGL", "shares": 20, "purchase_price": 2800, "current_price": 2950},
    {"symbol": "MSFT", "shares": 75, "purchase_price": 300, "current_price": 380},
]
create_portfolio_tracker(holdings)
```

**Features**: Automatic calculations, pie chart for allocation.

### Recipe 6: Expense Categorization

**Use Case**: Categorize and analyze expenses.

```python
from spreadsheet_dl import SpreadsheetBuilder
from datetime import datetime, timedelta

def create_expense_report(
    expenses: list[dict],
    output_path: str = "expenses.ods"
):
    """Create expense report with category analysis.

    Args:
        expenses: List of dicts with keys: date, description, amount, category
    """
    builder = SpreadsheetBuilder(theme="corporate")

    # Transactions sheet
    builder.sheet("Transactions")
    builder.column("Date", width="100pt", type="date")
    builder.column("Description", width="200pt")
    builder.column("Amount", width="100pt", type="currency")
    builder.column("Category", width="120pt")

    builder.header_row()

    for expense in expenses:
        builder.row()
        builder.cell(expense["date"])
        builder.cell(expense["description"])
        builder.cell(expense["amount"])
        builder.cell(expense["category"])

    # Category summary sheet
    builder.sheet("Category Summary")
    builder.column("Category", width="150pt")
    builder.column("Total", width="120pt", type="currency")
    builder.column("Count", width="80pt", type="integer")
    builder.column("Average", width="120pt", type="currency")

    builder.header_row()

    # Get unique categories
    categories = sorted(set(e["category"] for e in expenses))

    row_num = 2
    for category in categories:
        builder.row()
        builder.cell(category)
        builder.cell(f'=SUMIF(Transactions.D:D,"{category}",Transactions.C:C)')
        builder.cell(f'=COUNTIF(Transactions.D:D,"{category}")')
        builder.cell(f"=B{row_num}/C{row_num}")
        row_num += 1

    # Total row
    builder.row()
    builder.cell("Total", style="total")
    builder.cell(f"=SUM(B2:B{row_num-1})", style="total")
    builder.cell(f"=SUM(C2:C{row_num-1})", style="total")
    builder.cell(f"=B{row_num}/C{row_num}", style="total")

    # Add chart
    chart = ChartBuilder() \
        .column_chart() \
        .title("Expenses by Category") \
        .series("Amount", f"B2:B{row_num-1}", categories=f"A2:A{row_num-1}") \
        .position(cell="F2") \
        .build()

    builder.chart(chart)

    builder.save(output_path)
    return output_path

# Usage
expenses = [
    {"date": "2025-01-15", "description": "Grocery Store", "amount": 125.50, "category": "Food"},
    {"date": "2025-01-16", "description": "Gas Station", "amount": 45.00, "category": "Transportation"},
    {"date": "2025-01-17", "description": "Restaurant", "amount": 60.00, "category": "Dining Out"},
    # ... more expenses
]
create_expense_report(expenses)
```

**Key Formula**: `SUMIF()` for category-based summation.

## Data Import/Export

### Recipe 7: Pandas DataFrame to ODS

**Use Case**: Export pandas DataFrame with proper formatting.

```python
from spreadsheet_dl import SpreadsheetBuilder
import pandas as pd
import numpy as np

def dataframe_to_ods(
    df: pd.DataFrame,
    output_path: str,
    sheet_name: str = "Data",
    theme: str = "corporate",
    include_summary: bool = True,
):
    """Export pandas DataFrame to ODS with formatting.

    Args:
        df: DataFrame to export
        output_path: Output file path
        sheet_name: Name of the sheet
        theme: Theme to use
        include_summary: Whether to include summary statistics
    """
    builder = SpreadsheetBuilder(theme=theme)
    builder.sheet(sheet_name)

    # Detect column types and add columns
    for col in df.columns:
        dtype = df[col].dtype

        if dtype == np.float64:
            col_type = "number"
        elif dtype == np.int64:
            col_type = "integer"
        elif dtype == 'datetime64[ns]':
            col_type = "date"
        elif "amount" in col.lower() or "price" in col.lower() or "cost" in col.lower():
            col_type = "currency"
        else:
            col_type = "string"

        builder.column(col, type=col_type, width="120pt")

    builder.header_row()

    # Add data
    for _, row in df.iterrows():
        builder.row()
        for value in row:
            # Handle NaN values
            if pd.isna(value):
                builder.cell("")
            else:
                builder.cell(value)

    # Add summary statistics if requested
    if include_summary:
        builder.row()  # Blank row
        builder.row()

        builder.cell("Summary Statistics", style="header_primary")

        # For numeric columns, add statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            col_idx = df.columns.get_loc(col)
            col_letter = chr(65 + col_idx)  # A, B, C, ...

            builder.row()
            builder.cell(f"{col} - Mean:")
            builder.cell(f"=AVERAGE({col_letter}2:{col_letter}{len(df)+1})")

            builder.row()
            builder.cell(f"{col} - Sum:")
            builder.cell(f"=SUM({col_letter}2:{col_letter}{len(df)+1})")

    builder.save(output_path)
    return output_path

# Usage
df = pd.DataFrame({
    "Date": pd.date_range("2025-01-01", periods=100),
    "Product": np.random.choice(["A", "B", "C"], 100),
    "Amount": np.random.uniform(10, 1000, 100),
    "Quantity": np.random.randint(1, 50, 100),
})

dataframe_to_ods(df, "sales_data.ods", include_summary=True)
```

**Best Practice**: Detect column types from DataFrame dtypes.

### Recipe 8: Export to Multiple Formats

**Use Case**: Export same data to ODS, XLSX, and PDF.

```python
from spreadsheet_dl import SpreadsheetBuilder
from spreadsheet_dl.adapters import XlsxAdapter, PdfAdapter, CsvAdapter

def export_multi_format(
    data: list[dict],
    base_name: str = "report",
):
    """Export data to multiple formats.

    Args:
        data: List of dicts representing rows
        base_name: Base filename (without extension)

    Returns:
        Dict of format -> output path
    """
    # Build spreadsheet
    builder = SpreadsheetBuilder(theme="corporate")
    builder.sheet("Data")

    # Add columns from first row
    if data:
        for key in data[0].keys():
            builder.column(key, width="120pt")

        builder.header_row()

        # Add data
        for row_data in data:
            builder.row()
            for value in row_data.values():
                builder.cell(value)

    # Get spec
    spec = builder.build()

    # Export to all formats
    outputs = {}

    # ODS (native)
    ods_path = f"{base_name}.ods"
    builder.save(ods_path)
    outputs["ods"] = ods_path

    # XLSX
    xlsx_path = f"{base_name}.xlsx"
    XlsxAdapter().export(spec, xlsx_path)
    outputs["xlsx"] = xlsx_path

    # PDF
    pdf_path = f"{base_name}.pdf"
    PdfAdapter(page_size="A4", orientation="landscape").export(spec, pdf_path)
    outputs["pdf"] = pdf_path

    # CSV
    csv_path = f"{base_name}.csv"
    CsvAdapter().export(spec, csv_path)
    outputs["csv"] = csv_path

    return outputs

# Usage
data = [
    {"Name": "Alice", "Age": 30, "Salary": 75000},
    {"Name": "Bob", "Age": 25, "Salary": 65000},
    {"Name": "Charlie", "Age": 35, "Salary": 85000},
]

outputs = export_multi_format(data, "employee_data")
print(f"Exported: {outputs}")
```

**Result**: Same data in 4 different formats.

### Recipe 9: Import and Modify Existing ODS

**Use Case**: Load existing spreadsheet, modify it, and save.

```python
from spreadsheet_dl import import_ods

def add_ytd_column(input_path: str, output_path: str):
    """Add Year-to-Date column to existing budget."""
    # Import existing spreadsheet
    builder = import_ods(input_path)

    # Select the sheet to modify
    builder.select_sheet("Budget")

    # Add new column
    builder.column("YTD Total", width="120pt", type="currency")

    # Add YTD formula to each row
    # Assuming original columns are: Category, Jan, Feb, Mar, ...
    num_months = 12  # Assuming 12 monthly columns
    start_row = 2  # Data starts at row 2

    # Navigate to YTD column and add formulas
    for row_num in range(start_row, start_row + 20):  # Adjust range as needed
        builder.select_cell(f"N{row_num}")  # Column N for YTD
        builder.cell(f"=SUM(B{row_num}:M{row_num})")  # Sum Jan-Dec

    # Save modified spreadsheet
    builder.save(output_path)
    return output_path

# Usage
add_ytd_column("budget_2025.ods", "budget_2025_ytd.ods")
```

**Tip**: Use `import_ods()` for round-trip editing.

## Chart Recipes

### Recipe 10: Create Revenue Trend Chart

**Use Case**: Visualize revenue over time.

```python
from spreadsheet_dl import SpreadsheetBuilder, ChartBuilder

def create_revenue_trend(
    monthly_data: list[dict],
    output_path: str = "revenue_trend.ods"
):
    """Create revenue trend chart.

    Args:
        monthly_data: List of dicts with keys: month, revenue, expenses
    """
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Revenue Data")
    builder.column("Month", width="100pt")
    builder.column("Revenue", width="120pt", type="currency")
    builder.column("Expenses", width="120pt", type="currency")
    builder.column("Profit", width="120pt", type="currency")

    builder.header_row()

    row_num = 2
    for data in monthly_data:
        builder.row()
        builder.cell(data["month"])
        builder.cell(data["revenue"])
        builder.cell(data["expenses"])
        builder.cell(f"=B{row_num}-C{row_num}")  # Profit
        row_num += 1

    # Create line chart with trendline
    chart = ChartBuilder() \
        .line_chart() \
        .title("Revenue and Expenses Trend") \
        .series("Revenue", f"B2:B{row_num-1}", categories=f"A2:A{row_num-1}") \
        .series("Expenses", f"C2:C{row_num-1}") \
        .series("Profit", f"D2:D{row_num-1}") \
        .trendline(series_index=0, type="linear", forecast=3) \
        .legend(position="bottom") \
        .position(cell="F2", width="500pt", height="350pt") \
        .build()

    builder.chart(chart)

    builder.save(output_path)
    return output_path

# Usage
monthly_data = [
    {"month": "Jan", "revenue": 50000, "expenses": 35000},
    {"month": "Feb", "revenue": 55000, "expenses": 36000},
    {"month": "Mar", "revenue": 58000, "expenses": 37000},
    {"month": "Apr", "revenue": 62000, "expenses": 38000},
    {"month": "May", "revenue": 65000, "expenses": 39000},
    {"month": "Jun", "revenue": 70000, "expenses": 40000},
]

create_revenue_trend(monthly_data)
```

**Features**: Multiple series, trendline with forecast.

### Recipe 11: Sparklines for Quick Visualization

**Use Case**: Add inline sparklines to show trends.

```python
from spreadsheet_dl import SpreadsheetBuilder
from spreadsheet_dl.charts import ChartBuilder

def create_sales_dashboard(
    sales_reps: list[dict],
    output_path: str = "sales_dashboard.ods"
):
    """Create sales dashboard with sparklines.

    Args:
        sales_reps: List of dicts with keys: name, q1, q2, q3, q4
    """
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Sales Dashboard")
    builder.column("Sales Rep", width="120pt")
    builder.column("Q1", width="80pt", type="currency")
    builder.column("Q2", width="80pt", type="currency")
    builder.column("Q3", width="80pt", type="currency")
    builder.column("Q4", width="80pt", type="currency")
    builder.column("Total", width="100pt", type="currency")
    builder.column("Trend", width="100pt")

    builder.header_row()

    row_num = 2
    for rep in sales_reps:
        builder.row()
        builder.cell(rep["name"])
        builder.cell(rep["q1"])
        builder.cell(rep["q2"])
        builder.cell(rep["q3"])
        builder.cell(rep["q4"])
        builder.cell(f"=SUM(B{row_num}:E{row_num})")  # Total

        # Add sparkline for trend
        sparkline = ChartBuilder() \
            .sparkline(
                data_range=f"B{row_num}:E{row_num}",
                sparkline_type="line"
            ) \
            .position(cell=f"G{row_num}", width="80pt", height="20pt") \
            .build()

        builder.chart(sparkline)
        row_num += 1

    builder.save(output_path)
    return output_path

# Usage
sales_reps = [
    {"name": "Alice", "q1": 50000, "q2": 55000, "q3": 60000, "q4": 65000},
    {"name": "Bob", "q1": 45000, "q2": 47000, "q3": 48000, "q4": 50000},
    {"name": "Charlie", "q1": 60000, "q2": 58000, "q3": 62000, "q4": 64000},
]

create_sales_dashboard(sales_reps)
```

**Sparklines**: Inline charts for at-a-glance trends.

### Recipe 12: Combination Chart (Dual Axis)

**Use Case**: Show revenue (bars) and profit margin % (line) on same chart.

```python
from spreadsheet_dl import SpreadsheetBuilder, ChartBuilder

def create_combo_chart(
    data: list[dict],
    output_path: str = "performance_chart.ods"
):
    """Create combination chart with dual axis.

    Args:
        data: List of dicts with keys: month, revenue, margin_pct
    """
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Performance")
    builder.column("Month", width="100pt")
    builder.column("Revenue", width="120pt", type="currency")
    builder.column("Margin %", width="100pt", type="percent")

    builder.header_row()

    for item in data:
        builder.row()
        builder.cell(item["month"])
        builder.cell(item["revenue"])
        builder.cell(item["margin_pct"] / 100)  # Convert to decimal

    # Create combination chart
    chart = ChartBuilder() \
        .combo_chart() \
        .title("Revenue and Profit Margin") \
        .series("Revenue", "B2:B13", categories="A2:A13", chart_type="column") \
        .series("Margin %", "C2:C13", chart_type="line", secondary_axis=True) \
        .position(cell="E2", width="500pt", height="350pt") \
        .legend(position="bottom") \
        .build()

    builder.chart(chart)

    builder.save(output_path)
    return output_path

# Usage
data = [
    {"month": "Jan", "revenue": 100000, "margin_pct": 15},
    {"month": "Feb", "revenue": 110000, "margin_pct": 16},
    {"month": "Mar", "revenue": 105000, "margin_pct": 14},
    # ... more months
]

create_combo_chart(data)
```

**Combo Chart**: Different chart types on same axes.

## Styling Recipes

### Recipe 13: Conditional Formatting for Alerts

**Use Case**: Highlight over-budget items in red.

```python
from spreadsheet_dl import SpreadsheetBuilder
from spreadsheet_dl.schema import ConditionalFormat, ColorScaleRule

def create_budget_with_alerts(
    budget_items: list[dict],
    output_path: str = "budget_alerts.ods"
):
    """Create budget with conditional formatting alerts.

    Args:
        budget_items: List of dicts with keys: category, budget, actual
    """
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Budget")
    builder.column("Category", width="150pt")
    builder.column("Budget", width="100pt", type="currency")
    builder.column("Actual", width="100pt", type="currency")
    builder.column("Status", width="80pt")

    builder.header_row()

    row_num = 2
    for item in budget_items:
        builder.row()
        builder.cell(item["category"])
        builder.cell(item["budget"])
        builder.cell(item["actual"])

        # Status formula: Over/Under
        builder.cell(f'=IF(C{row_num}>B{row_num},"Over","Under")')
        row_num += 1

    # Apply conditional formatting to Status column
    builder.conditional_format(
        range=f"D2:D{row_num-1}",
        rule=ConditionalFormat(
            condition='cell_value == "Over"',
            style={"background_color": "#FFCCCC", "font_color": "#CC0000"}
        )
    )

    builder.conditional_format(
        range=f"D2:D{row_num-1}",
        rule=ConditionalFormat(
            condition='cell_value == "Under"',
            style={"background_color": "#CCFFCC", "font_color": "#00CC00"}
        )
    )

    # Color scale for Actual amounts
    builder.conditional_format(
        range=f"C2:C{row_num-1}",
        rule=ColorScaleRule(
            min_color="#63BE7B",  # Green for low
            mid_color="#FFEB84",  # Yellow for mid
            max_color="#F8696B",  # Red for high
        )
    )

    builder.save(output_path)
    return output_path

# Usage
budget_items = [
    {"category": "Marketing", "budget": 5000, "actual": 5200},
    {"category": "Sales", "budget": 10000, "actual": 9500},
    {"category": "Operations", "budget": 15000, "actual": 14800},
]

create_budget_with_alerts(budget_items)
```

**Visual Alerts**: Red for over-budget, green for under-budget.

### Recipe 14: Alternating Row Colors

**Use Case**: Improve readability with alternating row styles.

```python
from spreadsheet_dl import SpreadsheetBuilder

def create_readable_table(
    data: list[list],
    headers: list[str],
    output_path: str = "readable_table.ods"
):
    """Create table with alternating row colors."""
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Data")

    # Add columns
    for header in headers:
        builder.column(header, width="120pt")

    builder.header_row()

    # Add data with alternating styles
    for i, row_data in enumerate(data):
        style = "row_even" if i % 2 == 0 else "row_odd"
        builder.row(style=style)

        for value in row_data:
            builder.cell(value)

    builder.save(output_path)
    return output_path

# Usage
headers = ["Name", "Department", "Salary"]
data = [
    ["Alice", "Engineering", 95000],
    ["Bob", "Marketing", 75000],
    ["Charlie", "Sales", 80000],
    ["Diana", "Operations", 70000],
]

create_readable_table(data, headers)
```

**Readability**: Alternating colors improve table scanning.

### Recipe 15: Custom Theme

**Use Case**: Create spreadsheet with company branding.

```python
from spreadsheet_dl import SpreadsheetBuilder
from spreadsheet_dl.schema import Theme, ThemeColors, ThemeStyles

def create_branded_report(
    data: list[dict],
    output_path: str = "branded_report.ods"
):
    """Create report with custom company theme."""
    # Define custom theme
    custom_theme = Theme(
        name="company_brand",
        colors=ThemeColors(
            primary="#1E40AF",  # Company blue
            secondary="#F59E0B",  # Company gold
            accent="#10B981",  # Success green
            background="#FFFFFF",
            text="#1F2937",
        ),
        styles=ThemeStyles(
            header={
                "background_color": "{colors.primary}",
                "font_color": "#FFFFFF",
                "font_weight": "bold",
                "font_size": "12pt",
            },
            total={
                "font_weight": "bold",
                "border_top": "2pt solid {colors.secondary}",
            }
        )
    )

    builder = SpreadsheetBuilder(theme=custom_theme)

    builder.sheet("Report")

    # Add company logo (if image support available)
    # builder.image("company_logo.png", position="A1")

    builder.column("Product", width="150pt")
    builder.column("Sales", width="120pt", type="currency")

    builder.header_row()

    for item in data:
        builder.row()
        builder.cell(item["product"])
        builder.cell(item["sales"])

    builder.save(output_path)
    return output_path

# Usage
data = [
    {"product": "Widget A", "sales": 10000},
    {"product": "Widget B", "sales": 15000},
]

create_branded_report(data)
```

**Branding**: Custom colors match company identity.

## Formula Recipes

### Recipe 16: Dynamic Ranges with OFFSET

**Use Case**: Create formulas that automatically expand with data.

```python
from spreadsheet_dl import SpreadsheetBuilder

def create_dynamic_summary(
    output_path: str = "dynamic_summary.ods"
):
    """Create summary with dynamic ranges."""
    builder = SpreadsheetBuilder(theme="corporate")

    builder.sheet("Data")
    builder.column("Month", width="100pt")
    builder.column("Sales", width="120pt", type="currency")

    builder.header_row()

    # Sample data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    sales = [10000, 12000, 11500, 13000, 14500, 15000]

    for month, sale in zip(months, sales):
        builder.row()
        builder.cell(month)
        builder.cell(sale)

    # Summary section
    builder.row()  # Blank
    builder.row()

    builder.cell("Total Sales (Dynamic):")
    # Use OFFSET to create dynamic range from B2 to last row
    # =SUM(OFFSET(B2,0,0,COUNTA(B:B)-1,1))
    builder.cell("=SUM(OFFSET(B2,0,0,COUNTA(B:B)-1,1))")

    builder.row()
    builder.cell("Average Sales (Dynamic):")
    builder.cell("=AVERAGE(OFFSET(B2,0,0,COUNTA(B:B)-1,1))")

    builder.save(output_path)
    return output_path

# Usage
create_dynamic_summary()
```

**Dynamic**: Formulas automatically adjust when rows are added.

### Recipe 17: Data Validation Dropdowns

**Use Case**: Create dropdowns for category selection.

```python
from spreadsheet_dl import SpreadsheetBuilder
from spreadsheet_dl.schema import ValidationRule, ValidationRuleType

def create_expense_entry_form(
    output_path: str = "expense_form.ods"
):
    """Create expense entry form with validation."""
    builder = SpreadsheetBuilder(theme="corporate")

    # Categories reference sheet
    builder.sheet("Categories")
    builder.column("Category")
    builder.header_row()

    categories = ["Food", "Transportation", "Entertainment", "Utilities", "Other"]
    for category in categories:
        builder.row()
        builder.cell(category)

    # Entry form sheet
    builder.sheet("Expense Entry")
    builder.column("Date", width="100pt", type="date")
    builder.column("Description", width="200pt")
    builder.column("Amount", width="120pt", type="currency")
    builder.column("Category", width="120pt")

    builder.header_row()

    # Add 50 blank rows for entry
    for i in range(50):
        builder.row()
        builder.cell("")  # Date
        builder.cell("")  # Description
        builder.cell("")  # Amount

        # Category with dropdown validation
        # Note: ValidationRule implementation may vary
        builder.cell("", validation=ValidationRule(
            rule_type=ValidationRuleType.LIST,
            formula="Categories.A2:A6",
            show_dropdown=True,
        ))

    builder.save(output_path)
    return output_path

# Usage
create_expense_entry_form()
```

**Data Validation**: Ensures consistent category entry.

### Recipe 18: Lookup Tables with VLOOKUP

**Use Case**: Look up prices from a product catalog.

```python
from spreadsheet_dl import SpreadsheetBuilder

def create_invoice_with_lookup(
    products: list[dict],
    line_items: list[dict],
    output_path: str = "invoice.ods"
):
    """Create invoice with VLOOKUP for prices.

    Args:
        products: List of dicts with keys: code, name, price
        line_items: List of dicts with keys: product_code, quantity
    """
    builder = SpreadsheetBuilder(theme="corporate")

    # Product catalog sheet
    builder.sheet("Product Catalog")
    builder.column("Code", width="80pt")
    builder.column("Name", width="150pt")
    builder.column("Price", width="100pt", type="currency")

    builder.header_row()

    for product in products:
        builder.row()
        builder.cell(product["code"])
        builder.cell(product["name"])
        builder.cell(product["price"])

    # Invoice sheet
    builder.sheet("Invoice")
    builder.column("Product Code", width="100pt")
    builder.column("Product Name", width="150pt")
    builder.column("Unit Price", width="100pt", type="currency")
    builder.column("Quantity", width="80pt", type="integer")
    builder.column("Total", width="120pt", type="currency")

    builder.header_row()

    row_num = 2
    for item in line_items:
        builder.row()
        builder.cell(item["product_code"])

        # VLOOKUP product name
        builder.cell(f'=VLOOKUP(A{row_num},\'Product Catalog\'.A:C,2,FALSE)')

        # VLOOKUP price
        builder.cell(f'=VLOOKUP(A{row_num},\'Product Catalog\'.A:C,3,FALSE)')

        builder.cell(item["quantity"])

        # Calculate total
        builder.cell(f"=C{row_num}*D{row_num}")

        row_num += 1

    # Invoice total
    builder.row()
    builder.cell("", style="total")
    builder.cell("", style="total")
    builder.cell("", style="total")
    builder.cell("Total:", style="total")
    builder.cell(f"=SUM(E2:E{row_num-1})", style="total")

    builder.save(output_path)
    return output_path

# Usage
products = [
    {"code": "WID-001", "name": "Widget A", "price": 25.00},
    {"code": "WID-002", "name": "Widget B", "price": 35.00},
    {"code": "GAD-001", "name": "Gadget X", "price": 50.00},
]

line_items = [
    {"product_code": "WID-001", "quantity": 5},
    {"product_code": "GAD-001", "quantity": 2},
    {"product_code": "WID-002", "quantity": 3},
]

create_invoice_with_lookup(products, line_items)
```

**VLOOKUP**: Automatic price lookup from catalog.

## MCP Server Recipes

### Recipe 19: Natural Language Spreadsheet Creation

**Use Case**: Use Claude to create spreadsheets via MCP server.

```python
from spreadsheet_dl.mcp_server import MCPServer, MCPConfig
from pathlib import Path

def setup_mcp_server():
    """Set up MCP server for Claude integration."""
    config = MCPConfig(
        allowed_paths=[Path("~/Documents/Spreadsheets")],
        rate_limit_per_minute=120,
        enable_file_creation=True,
        enable_file_modification=True,
    )

    server = MCPServer(config)

    # Start server (runs in stdio mode for Claude Desktop)
    server.run()

# In Claude Desktop config (claude_desktop_config.json):
# {
#   "mcpServers": {
#     "spreadsheet-dl": {
#       "type": "stdio",
#       "command": "uv",
#       "args": ["run", "python", "-m", "spreadsheet_dl.mcp_server"],
#       "env": {
#         "SPREADSHEET_DL_ALLOWED_PATHS": "~/Documents/Spreadsheets"
#       }
#     }
#   }
# }

# Usage in Claude:
# User: "Create a budget spreadsheet with categories Housing, Food, and Transport"
# Claude uses MCP tools to:
# - create_spreadsheet(name="Budget")
# - add_sheet(name="Budget")
# - add_columns(["Category", "Amount"])
# - add_rows([...])
# - save_spreadsheet(path="Budget.ods")
```

**AI Integration**: Create spreadsheets through natural language.

### Recipe 20: Custom MCP Tool

**Use Case**: Register custom spreadsheet operation as MCP tool.

```python
from spreadsheet_dl.mcp_server import mcp_tool, MCPToolCategory

@mcp_tool(
    name="calculate_tax",
    description="Calculate sales tax for invoice",
    category=MCPToolCategory.FINANCIAL,
)
def calculate_tax(
    subtotal: float,
    tax_rate: float = 0.08,
) -> dict:
    """Calculate sales tax and total.

    Args:
        subtotal: Subtotal amount
        tax_rate: Tax rate (default 8%)

    Returns:
        Dict with tax amount and total
    """
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    return {
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total": total,
        "formula": f"=subtotal * {tax_rate}"
    }

# Now available as MCP tool in Claude Desktop
```

**Custom Tools**: Extend MCP server with domain-specific operations.

## CLI Automation

### Recipe 21: Automated Monthly Reports

**Use Case**: Generate monthly report automatically via cron.

```bash
#!/bin/bash
# monthly_report.sh

MONTH=$(date +%B)
YEAR=$(date +%Y)
OUTPUT_DIR="$HOME/Documents/Reports"

# Generate budget report
uv run spreadsheet-dl generate \
    --template monthly_budget \
    --output "$OUTPUT_DIR/${MONTH}_${YEAR}_budget.ods" \
    --theme corporate \
    --variable month="$MONTH" \
    --variable year="$YEAR"

# Import transactions from bank CSV
uv run spreadsheet-dl import \
    --file "$HOME/Downloads/transactions_${MONTH}.csv" \
    --bank chase \
    --output "$OUTPUT_DIR/${MONTH}_${YEAR}_budget.ods"

# Generate summary
uv run spreadsheet-dl analyze \
    "$OUTPUT_DIR/${MONTH}_${YEAR}_budget.ods" \
    --format markdown \
    > "$OUTPUT_DIR/${MONTH}_${YEAR}_summary.md"

# Upload to Nextcloud
uv run spreadsheet-dl upload \
    "$OUTPUT_DIR/${MONTH}_${YEAR}_budget.ods" \
    --nextcloud-url "https://cloud.example.com" \
    --remote-path "/Budgets/${YEAR}/${MONTH}.ods"

echo "Monthly report generated for $MONTH $YEAR"
```

**Automation**: Schedule with `cron` for automatic execution.

### Recipe 22: Batch Processing

**Use Case**: Process multiple CSV files into spreadsheets.

```bash
#!/bin/bash
# batch_process.sh

INPUT_DIR="./data"
OUTPUT_DIR="./reports"

mkdir -p "$OUTPUT_DIR"

# Process all CSV files in input directory
for csv_file in "$INPUT_DIR"/*.csv; do
    filename=$(basename "$csv_file" .csv)

    echo "Processing $filename..."

    uv run python -c "
from spreadsheet_dl import SpreadsheetBuilder
import pandas as pd

df = pd.read_csv('$csv_file')
builder = SpreadsheetBuilder(theme='corporate')
builder.sheet('Data')

for col in df.columns:
    builder.column(col, width='120pt')

builder.header_row()

for _, row in df.iterrows():
    builder.row()
    for value in row:
        builder.cell(value)

builder.save('$OUTPUT_DIR/$filename.ods')
print(f'Created $filename.ods')
"
done

echo "Batch processing complete. Processed $(ls -1 "$OUTPUT_DIR" | wc -l) files."
```

**Batch**: Process multiple files in one command.

## Anti-Patterns

### Anti-Pattern 1: Not Using Themes ❌

**Bad**:

```python
# Don't do this: Inline styles everywhere
for i in range(100):
    builder.cell(
        "Header",
        style={
            "font_weight": "bold",
            "background_color": "#4472C4",
            "font_color": "#FFFFFF",
        }
    )
```

**Good**:

```python
# Do this: Use theme styles
builder = SpreadsheetBuilder(theme="corporate")
for i in range(100):
    builder.cell("Header", style="header_primary")
```

### Anti-Pattern 2: Not Using Streaming for Large Files ❌

**Bad**:

```python
# Don't do this: Builder API for 100K rows
builder = SpreadsheetBuilder()
for i in range(100_000):  # 💥 High memory usage
    builder.row()
    builder.cell(f"Row {i}")
```

**Good**:

```python
# Do this: Streaming API for large files
with StreamingWriter("large.ods") as writer:
    writer.write_header(["Data"])
    for i in range(100_000):  # ✅ Low memory
        writer.write_row([f"Row {i}"])
```

### Anti-Pattern 3: Full Column References ❌

**Bad**:

```python
# Don't do this: References entire column
builder.cell("=SUM(A:A)")  # 65K+ cells referenced
```

**Good**:

```python
# Do this: Specific range
builder.cell(f"=SUM(A2:A{num_rows+1})")  # Only data cells
```

### Anti-Pattern 4: Not Handling Errors ❌

**Bad**:

```python
# Don't do this: No error handling
builder.save("output.ods")  # Might fail
```

**Good**:

```python
# Do this: Handle errors
from spreadsheet_dl.exceptions import SpreadsheetDLError

try:
    builder.save("output.ods")
except SpreadsheetDLError as e:
    print(f"Error: {e.message}")
    print(f"Suggestion: {e.suggestion}")
```

### Anti-Pattern 5: Ignoring Type Hints ❌

**Bad**:

```python
# Don't do this: No type hints
def create_report(data):  # What is data?
    builder = SpreadsheetBuilder()
    # ...
```

**Good**:

```python
# Do this: Use type hints
def create_report(data: list[dict]) -> str:
    """Create report and return output path."""
    builder = SpreadsheetBuilder()
    # ...
    return output_path
```

## See Also

- [API Reference](../api/index.md)
- [Best Practices Guide](best-practices.md)
- [Integration Guide](./integration.md)
- [Performance Guide](./performance.md)
- [Examples Gallery](../examples/gallery.md)
