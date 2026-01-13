# Tutorial: Sparklines for Trend Visualization

Learn how to add sparklines (mini charts) to your ODS spreadsheets for at-a-glance trend visualization.

## What are Sparklines?

Sparklines are small, inline charts that fit within a single cell. They provide visual context for data trends without taking up space like full charts. Perfect for dashboards, reports, and summary views.

**Important:** This is a **LibreOffice-specific feature**. Sparklines use the SPARKLINE() function which is only available in LibreOffice Calc. They will not render correctly in Excel or Google Sheets.

## Prerequisites

```bash
# Install SpreadsheetDL
uv pip install spreadsheet-dl

# LibreOffice Calc required for viewing
# Install from: https://www.libreoffice.org/
```

## Basic Line Sparkline

The simplest sparkline shows a trend line:

```python
from spreadsheet_dl.interactive import InteractiveOdsBuilder, SparklineConfig

# Create builder
builder = InteractiveOdsBuilder()

# Add line sparkline
sparkline = SparklineConfig(
    data_range="B2:B10",
    sparkline_type="line",
    color="#2196F3"
)

builder.add_sparkline("C2", sparkline)
```

## Sparkline Types

### 1. Line Sparklines

Best for continuous trends:

```python
# Stock price trend
stock_sparkline = SparklineConfig(
    data_range="B2:B30",  # Daily prices
    sparkline_type="line",
    color="#4CAF50",
    show_markers=True,  # Show data points
    line_width=1.5
)

builder.add_sparkline("D2", stock_sparkline)
```

### 2. Column Sparklines

Best for discrete comparisons:

```python
# Monthly sales
sales_sparkline = SparklineConfig(
    data_range="B2:B13",  # 12 months
    sparkline_type="column",
    color="#FF9800",
    negative_color="#F44336",  # Red for losses
    column_width=0.8
)

builder.add_sparkline("E2", sales_sparkline)
```

### 3. Stacked Sparklines

Best for cumulative values:

```python
# Cumulative revenue
revenue_sparkline = SparklineConfig(
    data_range="B2:B13",
    sparkline_type="stacked",
    color="#9C27B0"
)

builder.add_sparkline("F2", revenue_sparkline)
```

## Advanced Color Customization

Highlight key data points with color:

```python
# Financial dashboard sparkline
financial_sparkline = SparklineConfig(
    data_range="B2:B30",
    sparkline_type="line",
    color="#2196F3",           # Main line color
    high_color="#4CAF50",      # Highest point in green
    low_color="#F44336",       # Lowest point in red
    first_color="#9C27B0",     # First point in purple
    last_color="#FF9800",      # Last point in orange
    negative_color="#F44336",  # Negative values in red
    show_markers=True
)

builder.add_sparkline("G2", financial_sparkline)
```

## Example: Sales Dashboard

Create a complete dashboard with sparklines:

```python
from decimal import Decimal
from spreadsheet_dl.interactive import (
    InteractiveOdsBuilder,
    SparklineConfig,
    DashboardKPI,
    DashboardSection
)

# Create builder
builder = InteractiveOdsBuilder()

# Sample data: Monthly sales (12 months)
sales_data = [120, 135, 128, 145, 152, 148, 160, 155, 170, 165, 180, 195]

# Add sparkline for each product line
products = [
    ("Product A", "B2:B13", "#2196F3"),
    ("Product B", "C2:C13", "#4CAF50"),
    ("Product C", "D2:D13", "#FF9800"),
]

for idx, (product, data_range, color) in enumerate(products):
    sparkline = SparklineConfig(
        data_range=data_range,
        sparkline_type="line",
        color=color,
        high_color="#4CAF50",
        low_color="#F44336",
        show_markers=True,
        line_width=1.5,
        axis=True  # Show zero axis
    )

    # Add sparkline in column E
    builder.add_sparkline(f"E{idx+2}", sparkline)

# Add KPI section
kpi_section = DashboardSection(
    title="Sales Performance",
    kpis=[
        DashboardKPI(
            name="Total Sales",
            value=sum(sales_data),
            unit="$",
            trend="up",
            status="success"
        ),
        DashboardKPI(
            name="Average Monthly",
            value=sum(sales_data) / len(sales_data),
            unit="$",
            trend="up"
        )
    ],
    position=(1, 1)
)

builder.add_dashboard_section(kpi_section)

# Export
builder.export_to_file("sales_dashboard.ods")
```

## Example: Stock Portfolio Tracker

Track multiple stocks with sparklines:

```python
# Stock portfolio with 30-day price history
stocks = {
    "AAPL": {"range": "B2:B31", "color": "#2196F3"},
    "GOOGL": {"range": "C2:C31", "color": "#4CAF50"},
    "MSFT": {"range": "D2:D31", "color": "#FF9800"},
    "TSLA": {"range": "E2:E31", "color": "#9C27B0"},
}

builder = InteractiveOdsBuilder()

for idx, (symbol, config) in enumerate(stocks.items()):
    sparkline = SparklineConfig(
        data_range=config["range"],
        sparkline_type="line",
        color=config["color"],
        high_color="#4CAF50",  # Highlight peak
        low_color="#F44336",   # Highlight valley
        show_markers=False,
        line_width=2.0,
        axis=True
    )

    # Add in summary column
    builder.add_sparkline(f"F{idx+2}", sparkline)

builder.export_to_file("portfolio_tracker.ods")
```

## Example: Performance Indicators

Win/loss indicators with column sparklines:

```python
# Monthly performance vs target
performance = [5, -2, 8, 3, -1, 7, 10, -3, 6, 4, 9, 12]

builder = InteractiveOdsBuilder()

# Win/loss sparkline
performance_sparkline = SparklineConfig(
    data_range="B2:B13",
    sparkline_type="column",
    color="#4CAF50",        # Positive = green
    negative_color="#F44336",  # Negative = red
    column_width=1.0,
    axis=True,  # Show zero line
    min_value=-5,
    max_value=15
)

builder.add_sparkline("C2", performance_sparkline)
builder.export_to_file("performance_indicators.ods")
```

## Scaling and Axis Options

Control value ranges for consistent comparison:

```python
# Multiple products with same scale
for idx, product in enumerate(["A", "B", "C"]):
    sparkline = SparklineConfig(
        data_range=f"B{idx+2}:M{idx+2}",  # 12 months
        sparkline_type="line",
        color="#2196F3",
        min_value=0,      # All start at 0
        max_value=1000,   # All end at 1000
        axis=True,        # Show zero line
        show_markers=True
    )

    builder.add_sparkline(f"N{idx+2}", sparkline)
```

## Complete Example: Financial Dashboard

```python
from spreadsheet_dl.interactive import (
    InteractiveOdsBuilder,
    SparklineConfig,
    DashboardKPI,
    DashboardSection,
    ConditionalFormat
)

builder = InteractiveOdsBuilder()

# Revenue sparkline (12 months)
revenue_sparkline = SparklineConfig(
    data_range="B2:M2",
    sparkline_type="line",
    color="#4CAF50",
    high_color="#2E7D32",
    last_color="#1565C0",
    show_markers=True,
    line_width=2.0,
    axis=True
)
builder.add_sparkline("N2", revenue_sparkline)

# Expenses sparkline
expense_sparkline = SparklineConfig(
    data_range="B3:M3",
    sparkline_type="line",
    color="#F44336",
    high_color="#C62828",
    last_color="#1565C0",
    show_markers=True,
    line_width=2.0,
    axis=True
)
builder.add_sparkline("N3", expense_sparkline)

# Profit/Loss column sparkline
profit_sparkline = SparklineConfig(
    data_range="B4:M4",
    sparkline_type="column",
    color="#4CAF50",
    negative_color="#F44336",
    column_width=0.8,
    axis=True
)
builder.add_sparkline("N4", profit_sparkline)

# Add dashboard KPIs
kpi_section = DashboardSection(
    title="Financial Overview",
    kpis=[
        DashboardKPI(name="YTD Revenue", value=156000, unit="$", trend="up"),
        DashboardKPI(name="YTD Expenses", value=89000, unit="$", trend="down"),
        DashboardKPI(name="Net Profit", value=67000, unit="$", status="success"),
    ],
    position=(1, 1)
)
builder.add_dashboard_section(kpi_section)

# Add conditional formatting
builder.add_conditional_format(
    "B4:M4",
    ConditionalFormat.over_budget_warning()
)

builder.export_to_file("financial_dashboard.ods")
```

## Limitations and Compatibility

### LibreOffice Only

Sparklines use the SPARKLINE() function which is **LibreOffice-specific**:

- Works in: LibreOffice Calc 7.0+
- Does not work in: Microsoft Excel, Google Sheets, Apple Numbers

### Alternatives for Excel

If you need Excel compatibility, consider:

1. Use regular charts instead of sparklines
2. Export to XLSX and add Excel sparklines manually
3. Use conditional formatting data bars (limited features)

### Known Issues

- Formula is embedded in ODS file but renders only in LibreOffice
- Some advanced features may vary by LibreOffice version
- Data range must be on the same sheet as the sparkline

## Best Practices

### 1. Use Consistent Scales

When comparing multiple sparklines:

```python
# All sparklines use same min/max
for idx in range(5):
    sparkline = SparklineConfig(
        data_range=f"B{idx+2}:M{idx+2}",
        sparkline_type="line",
        min_value=0,
        max_value=1000  # Same scale
    )
    builder.add_sparkline(f"N{idx+2}", sparkline)
```

### 2. Choose Appropriate Type

- **Line**: Continuous data, trends, time series
- **Column**: Discrete values, comparisons, periodic data
- **Stacked**: Cumulative values, running totals

### 3. Use Color Purposefully

```python
# Financial data: Green=good, Red=bad
sparkline = SparklineConfig(
    data_range="B2:B30",
    sparkline_type="column",
    color="#4CAF50",          # Positive = green
    negative_color="#F44336",  # Negative = red
)
```

### 4. Keep Data Ranges Reasonable

- **Line sparklines**: 5-100 points ideal
- **Column sparklines**: 5-30 columns ideal
- Too many points = cluttered visualization

### 5. Test in LibreOffice

Always open generated ODS files in LibreOffice Calc to verify sparklines render correctly.

## Troubleshooting

### Sparkline Not Showing

1. Check LibreOffice version (7.0+)
2. Verify data range exists and has values
3. Check formula in cell (should start with `of:=SPARKLINE`)

### Wrong Colors

Colors must be in hex format:

- `"#2196F3"` - correct
- `"blue"` - incorrect
- `"rgb(33, 150, 243)"` - incorrect

### Invalid Cell Reference Error

Cell references must be valid:

- `"A1"` - correct
- `"Z999"` - correct
- `"INVALID"` - incorrect
- `"1A"` - incorrect

## API Reference

### SparklineConfig

```python
@dataclass
class SparklineConfig:
    data_range: str              # Required: "B2:B10"
    sparkline_type: str = "line" # "line", "column", "stacked"
    color: str = "#2196F3"       # Hex color
    negative_color: str | None = "#F44336"
    high_color: str | None = None
    low_color: str | None = None
    first_color: str | None = None
    last_color: str | None = None
    show_markers: bool = False   # Line sparklines only
    line_width: float = 1.0
    column_width: float = 1.0
    axis: bool = False
    min_value: float | None = None
    max_value: float | None = None
```

### Methods

```python
# Add sparkline to builder
builder.add_sparkline(cell: str, config: SparklineConfig)

# Generate formula string
config.to_formula() -> str
```

## Next Steps

- [Conditional Formatting Tutorial](08-conditional-formatting.md)
- [Dashboard Creation Tutorial](04-create-reports.md)
- [API Reference](../api/interactive.md)

## Additional Resources

- [LibreOffice Calc SPARKLINE Documentation](https://help.libreoffice.org/)
- [SparklineConfig API Docs](../api/interactive.md)
- [InteractiveOdsBuilder API Docs](../api/interactive.md)
