# Visualization and Charting Guide

## Overview

SpreadsheetDL provides comprehensive visualization capabilities for creating charts, dashboards, and interactive reports. This guide covers both embedded ODS charts and standalone web-based visualizations using Chart.js.

**What You'll Learn:**

- Create embedded ODS charts
- Generate interactive HTML dashboards
- Use the ChartBuilder API
- Create sparklines and mini-charts
- Build custom visualizations
- Export charts to various formats

## Visualization Options

### Embedded ODS Charts

Charts created within ODS files, viewable in LibreOffice Calc and Collabora Office.

**Pros:**

- Native spreadsheet integration
- Works offline
- No web browser needed
- Editable in office applications

**Cons:**

- Limited interactivity
- Fixed appearance
- Requires office software

### HTML/Chart.js Visualizations

Interactive web-based charts using Chart.js library.

**Pros:**

- Highly interactive
- Modern, responsive design
- Works in any browser
- Animation and tooltips

**Cons:**

- Requires web browser
- Read-only
- External dependency

## Embedded ODS Charts

### Creating Basic Charts

```python
from spreadsheet_dl import SpreadsheetBuilder, ChartBuilder, ChartType

# Create spreadsheet with data
builder = SpreadsheetBuilder()
builder.sheet("Budget Data") \
    .column("Month") \
    .column("Spent", type="currency") \
    .column("Budget", type="currency") \
    .header_row() \
    .row().cells("January", 2347.89, 5000) \
    .row().cells("February", 2156.43, 5000) \
    .row().cells("March", 2498.12, 5000)

# Create chart
chart = ChartBuilder(chart_type=ChartType.COLUMN) \
    .title("Monthly Spending") \
    .data_range("Budget Data", "A1:C4") \
    .x_axis(title="Month") \
    .y_axis(title="Amount ($)") \
    .legend(position="right")

# Add chart to sheet
builder.add_chart(chart, position="E2", width="400pt", height="300pt")

builder.save("budget_with_chart.ods")
```

### Chart Types

#### Column Chart

```python
from spreadsheet_dl import ChartBuilder, ChartType

chart = ChartBuilder(ChartType.COLUMN) \
    .title("Spending by Category") \
    .data_range("Data", "A1:B10") \
    .x_axis(title="Category") \
    .y_axis(title="Amount") \
    .build()
```

#### Bar Chart (Horizontal)

```python
chart = ChartBuilder(ChartType.BAR) \
    .title("Budget Allocation") \
    .data_range("Data", "A1:B10") \
    .x_axis(title="Amount") \
    .y_axis(title="Category") \
    .build()
```

#### Line Chart

```python
chart = ChartBuilder(ChartType.LINE) \
    .title("Spending Trend") \
    .data_range("Data", "A1:B13") \
    .x_axis(title="Month") \
    .y_axis(title="Total Spent") \
    .add_trendline() \
    .build()
```

#### Pie Chart

```python
chart = ChartBuilder(ChartType.PIE) \
    .title("Spending by Category") \
    .data_range("Data", "A1:B10") \
    .show_percentages(True) \
    .build()
```

#### Area Chart

```python
chart = ChartBuilder(ChartType.AREA) \
    .title("Cumulative Spending") \
    .data_range("Data", "A1:B13") \
    .x_axis(title="Month") \
    .y_axis(title="Cumulative Amount") \
    .stacked(True) \
    .build()
```

#### Scatter Plot

```python
chart = ChartBuilder(ChartType.SCATTER) \
    .title("Budget vs Actual") \
    .data_range("Data", "A1:C20") \
    .x_axis(title="Budgeted") \
    .y_axis(title="Actual") \
    .add_trendline(type="linear") \
    .build()
```

### Chart Customization

#### Styling

```python
from spreadsheet_dl import ChartBuilder, ChartStyle

chart = ChartBuilder(ChartType.COLUMN) \
    .title("Monthly Spending") \
    .data_range("Data", "A1:B13") \
    .style(
        ChartStyle(
            background_color="#FFFFFF",
            plot_area_color="#F5F5F5",
            font_family="Liberation Sans",
            title_font_size=16,
            axis_font_size=12,
        )
    ) \
    .build()
```

#### Colors

```python
# Custom data series colors
chart = ChartBuilder(ChartType.COLUMN) \
    .title("Spending Comparison") \
    .add_series("Budget", "B2:B13", color="#10B981") \
    .add_series("Actual", "C2:C13", color="#EF4444") \
    .x_labels("A2:A13") \
    .build()
```

#### Axis Configuration

```python
from spreadsheet_dl import AxisConfig

chart = ChartBuilder(ChartType.LINE) \
    .title("Spending Trend") \
    .data_range("Data", "A1:B13") \
    .x_axis(
        AxisConfig(
            title="Month",
            show_grid=True,
            label_rotation=45,
        )
    ) \
    .y_axis(
        AxisConfig(
            title="Amount ($)",
            min_value=0,
            max_value=6000,
            major_interval=1000,
            show_grid=True,
            number_format="$#,##0",
        )
    ) \
    .build()
```

#### Legend

```python
from spreadsheet_dl import LegendConfig, LegendPosition

chart = ChartBuilder(ChartType.LINE) \
    .title("Multi-Year Comparison") \
    .data_range("Data", "A1:D13") \
    .legend(
        LegendConfig(
            position=LegendPosition.BOTTOM,
            show=True,
            font_size=10,
        )
    ) \
    .build()
```

### Multiple Series Charts

```python
# Create chart with multiple data series
builder = SpreadsheetBuilder()
builder.sheet("Data") \
    .column("Month") \
    .column("2024", type="currency") \
    .column("2025", type="currency") \
    .column("2026", type="currency") \
    .header_row()

# Add data for each month
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
for i, month in enumerate(months):
    builder.row().cells(
        month,
        2000 + i * 100,  # 2024 data
        2100 + i * 110,  # 2025 data
        2200 + i * 120,  # 2026 data
    )

# Create multi-series line chart
chart = ChartBuilder(ChartType.LINE) \
    .title("Multi-Year Spending Comparison") \
    .add_series("2024", "B2:B7", color="#3B82F6") \
    .add_series("2025", "C2:C7", color="#10B981") \
    .add_series("2026", "D2:D7", color="#F59E0B") \
    .x_labels("A2:A7") \
    .x_axis(title="Month") \
    .y_axis(title="Spending ($)") \
    .legend(position="right") \
    .build()

builder.add_chart(chart, position="F2")
builder.save("multi_year_comparison.ods")
```

### Combo Charts (Dual Axis)

```python
from spreadsheet_dl import ChartBuilder, ChartType

# Column + Line chart
chart = ChartBuilder(ChartType.COMBO) \
    .title("Spending and Savings Rate") \
    .add_series("Spending", "B2:B13", chart_type=ChartType.COLUMN) \
    .add_series("Savings Rate", "C2:C13", chart_type=ChartType.LINE, secondary_axis=True) \
    .x_labels("A2:A13") \
    .y_axis(title="Spending ($)", position="left") \
    .y2_axis(title="Savings Rate (%)", position="right") \
    .build()
```

### Sparklines

Mini charts embedded in cells:

```python
from spreadsheet_dl import SparklineBuilder, SparklineType

builder = SpreadsheetBuilder()
builder.sheet("Dashboard") \
    .column("Category", width="150pt") \
    .column("Trend", width="100pt") \
    .header_row()

# Add sparklines for each category
categories = [
    ("Housing", [1500, 1500, 1500, 1500, 1600]),
    ("Groceries", [500, 450, 520, 480, 510]),
    ("Dining", [200, 250, 180, 220, 240]),
]

for category, values in categories:
    sparkline = SparklineBuilder(SparklineType.LINE) \
        .data(values) \
        .show_markers(True) \
        .color("#3B82F6") \
        .build()

    builder.row() \
        .cell(category) \
        .cell(sparkline)

builder.save("dashboard_with_sparklines.ods")
```

## HTML/Chart.js Visualizations

### Creating Interactive Dashboards

```python
from spreadsheet_dl import create_budget_dashboard, BudgetAnalyzer

# Analyze budget
analyzer = BudgetAnalyzer("budget.ods")

# Create interactive HTML dashboard
create_budget_dashboard(
    analyzer,
    output_path="dashboard.html",
    theme="dark",  # or "light"
    include_charts=[
        "spending_by_category",
        "budget_vs_actual",
        "spending_trend",
        "top_expenses"
    ]
)
```

### Custom Chart.js Visualizations

```python
from spreadsheet_dl import ChartJSBuilder, ChartJSType

# Prepare data
categories = ["Housing", "Groceries", "Dining", "Transport", "Utilities"]
amounts = [1500, 450, 280, 200, 150]

# Create pie chart
chart = ChartJSBuilder(ChartJSType.PIE) \
    .title("Spending Distribution") \
    .labels(categories) \
    .dataset("Amount", amounts, background_colors=[
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Yellow
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
    ]) \
    .build()

# Export to HTML
chart.save_html("spending_pie.html")
```

### Bar Chart Example

```python
chart = ChartJSBuilder(ChartJSType.BAR) \
    .title("Budget vs Actual Spending") \
    .labels(["Jan", "Feb", "Mar", "Apr", "May", "Jun"]) \
    .dataset("Budget", [5000, 5000, 5000, 5000, 5000, 5000], color="#10B981") \
    .dataset("Actual", [4850, 5120, 4920, 5350, 4780, 4990], color="#EF4444") \
    .options({
        "scales": {
            "y": {
                "beginAtZero": True,
                "ticks": {
                    "callback": "function(value) { return '$' + value; }"
                }
            }
        }
    }) \
    .build()

chart.save_html("budget_comparison.html")
```

### Line Chart with Trend

```python
import numpy as np

# Generate trend data
months = list(range(1, 13))
spending = [2000 + 100 * m + np.random.randint(-200, 200) for m in months]

# Calculate trend line
z = np.polyfit(months, spending, 1)
p = np.poly1d(z)
trend = [p(m) for m in months]

# Create chart
chart = ChartJSBuilder(ChartJSType.LINE) \
    .title("Spending Trend with Projection") \
    .labels([f"Month {m}" for m in months]) \
    .dataset("Actual", spending, color="#3B82F6", fill=False) \
    .dataset("Trend", trend, color="#EF4444", border_dash=[5, 5], fill=False) \
    .options({
        "plugins": {
            "legend": {
                "display": True,
                "position": "bottom"
            }
        }
    }) \
    .build()

chart.save_html("spending_trend.html")
```

### Donut Chart

```python
chart = ChartJSBuilder(ChartJSType.DOUGHNUT) \
    .title("Budget Allocation") \
    .labels(["Fixed", "Variable", "Savings", "Discretionary"]) \
    .dataset("Allocation", [3000, 1500, 800, 700], background_colors=[
        "#EF4444",  # Red for fixed
        "#F59E0B",  # Yellow for variable
        "#10B981",  # Green for savings
        "#3B82F6",  # Blue for discretionary
    ]) \
    .options({
        "cutout": "50%",  # Donut hole size
        "plugins": {
            "legend": {
                "position": "right"
            }
        }
    }) \
    .build()

chart.save_html("budget_donut.html")
```

### Multi-Dataset Visualization

```python
# Complex dashboard with multiple charts
from spreadsheet_dl import DashboardBuilder

dashboard = DashboardBuilder(title="Monthly Financial Dashboard")

# Spending by category (pie)
dashboard.add_chart(
    ChartJSBuilder(ChartJSType.PIE)
        .title("Spending by Category")
        .labels(categories)
        .dataset("Amount", amounts)
        .build(),
    position="top-left"
)

# Budget vs actual (bar)
dashboard.add_chart(
    ChartJSBuilder(ChartJSType.BAR)
        .title("Budget vs Actual")
        .labels(months)
        .dataset("Budget", budget_values)
        .dataset("Actual", actual_values)
        .build(),
    position="top-right"
)

# Spending trend (line)
dashboard.add_chart(
    ChartJSBuilder(ChartJSType.LINE)
        .title("Spending Trend")
        .labels(months)
        .dataset("Spending", spending_values)
        .build(),
    position="bottom"
)

dashboard.save("complete_dashboard.html")
```

## Advanced Visualizations

### Heatmap for Spending Patterns

```python
from spreadsheet_dl import HeatmapBuilder

# Create spending heatmap (category vs month)
heatmap = HeatmapBuilder() \
    .title("Spending Patterns by Category and Month") \
    .x_labels(["Jan", "Feb", "Mar", "Apr", "May", "Jun"]) \
    .y_labels(["Housing", "Food", "Transport", "Entertainment"]) \
    .data([
        [1500, 1500, 1500, 1600, 1500, 1500],  # Housing
        [600, 550, 620, 580, 590, 610],        # Food
        [250, 280, 230, 260, 270, 240],        # Transport
        [150, 200, 180, 220, 160, 190],        # Entertainment
    ]) \
    .color_scale("RdYlGn_r")  # Red for high, green for low \
    .build()

heatmap.save_html("spending_heatmap.html")
```

### Sankey Diagram (Flow)

```python
from spreadsheet_dl import SankeyBuilder

# Money flow: Income -> Categories -> Subcategories
sankey = SankeyBuilder() \
    .title("Money Flow") \
    .add_flow("Income", "Housing", 1500) \
    .add_flow("Income", "Food", 600) \
    .add_flow("Income", "Savings", 800) \
    .add_flow("Food", "Groceries", 400) \
    .add_flow("Food", "Dining Out", 200) \
    .build()

sankey.save_html("money_flow.html")
```

### Gauge Chart for Budget Status

```python
from spreadsheet_dl import GaugeBuilder

# Budget usage gauge
gauge = GaugeBuilder() \
    .title("Budget Usage") \
    .value(78.5)  # Percentage \
    .min_value(0) \
    .max_value(100) \
    .thresholds([
        (0, 70, "#10B981"),    # Green
        (70, 90, "#F59E0B"),   # Yellow
        (90, 100, "#EF4444"),  # Red
    ]) \
    .build()

gauge.save_html("budget_gauge.html")
```

## Budget-Specific Visualizations

### Category Spending Breakdown

```python
from spreadsheet_dl import BudgetAnalyzer, create_category_breakdown

analyzer = BudgetAnalyzer("budget.ods")
breakdown = analyzer.get_category_breakdown()

# Create pie chart
create_category_breakdown(
    breakdown,
    output_path="category_breakdown.html",
    chart_type="pie"
)
```

### Budget vs Actual Comparison

```python
from spreadsheet_dl import create_budget_comparison

analyzer = BudgetAnalyzer("budget.ods")

create_budget_comparison(
    analyzer,
    output_path="comparison.html",
    chart_type="bar",  # or "column"
    show_variance=True
)
```

### Spending Trend Over Time

```python
from spreadsheet_dl import create_spending_trend

analyzer = BudgetAnalyzer("budget.ods")

create_spending_trend(
    analyzer,
    output_path="trend.html",
    group_by="month",  # or "week", "day"
    show_forecast=True,
    forecast_periods=3
)
```

### Top Expenses

```python
from spreadsheet_dl import create_top_expenses_chart

analyzer = BudgetAnalyzer("budget.ods")

create_top_expenses_chart(
    analyzer,
    output_path="top_expenses.html",
    limit=10,
    chart_type="horizontal_bar"
)
```

## Export Options

### Export Charts as Images

```python
from spreadsheet_dl import ChartExporter

exporter = ChartExporter()

# Export embedded ODS chart to PNG
exporter.export_ods_chart(
    ods_file="budget.ods",
    chart_name="Spending Chart",
    output_path="chart.png",
    format="png",
    width=800,
    height=600,
    dpi=150
)

# Export Chart.js to image (requires headless browser)
exporter.export_chartjs(
    html_file="dashboard.html",
    output_path="dashboard.png",
    format="png"
)
```

### Export to PDF

```python
# Export dashboard to PDF
from spreadsheet_dl import export_dashboard_pdf

export_dashboard_pdf(
    html_file="dashboard.html",
    output_path="dashboard.pdf",
    page_size="A4",
    orientation="landscape"
)
```

## Dashboard Templates

### Monthly Budget Dashboard

```python
from spreadsheet_dl import MonthlyBudgetDashboard

dashboard = MonthlyBudgetDashboard(
    budget_file="budget.ods",
    month=1,
    year=2026
)

dashboard.add_kpi_cards()  # Total spent, remaining, percentage
dashboard.add_category_pie()
dashboard.add_budget_comparison_bar()
dashboard.add_daily_spending_line()
dashboard.add_top_expenses_list()

dashboard.save("monthly_dashboard.html")
```

### Year-to-Date Dashboard

```python
from spreadsheet_dl import YTDBudgetDashboard

dashboard = YTDBudgetDashboard(
    budget_files=["jan.ods", "feb.ods", "mar.ods"],
    year=2026
)

dashboard.add_ytd_summary()
dashboard.add_monthly_comparison()
dashboard.add_category_trends()
dashboard.add_savings_progress()

dashboard.save("ytd_dashboard.html")
```

## Best Practices

1. **Choose the Right Chart Type**
   - Pie/Donut: Part-to-whole relationships
   - Bar/Column: Comparisons across categories
   - Line: Trends over time
   - Scatter: Correlations
   - Area: Cumulative values

2. **Color Coding**
   - Use consistent colors across charts
   - Red for over-budget, green for under-budget
   - Limit to 5-7 colors per chart
   - Consider colorblind-friendly palettes

3. **Simplicity**
   - Don't overcrowd charts
   - Focus on key insights
   - Remove unnecessary gridlines
   - Use clear, concise titles

4. **Accessibility**
   - Provide text alternatives
   - Use patterns in addition to colors
   - Ensure sufficient contrast
   - Include data tables

5. **Performance**
   - Limit data points in web charts
   - Use sampling for large datasets
   - Optimize image sizes
   - Lazy load charts

## Troubleshooting

**Charts not appearing in ODS?**

- Verify data range is correct
- Check LibreOffice Calc version
- Ensure chart library is enabled
- Try recreating with simpler settings

**Chart.js visualizations not loading?**

- Check internet connection (CDN)
- Verify HTML file opens in browser
- Look for JavaScript errors in console
- Test with simpler chart first

**Export to image failing?**

- Install required dependencies (Pillow, selenium)
- Check Chrome/Firefox drivers installed
- Verify file permissions
- Try different export format

## See Also

- [Chart API Reference](../api/charts.md) - Chart builder API
- [Visualization API](../api/visualization.md) - Visualization module
- [Dashboard Analytics](../api/analytics.md) - Analytics dashboard
- [Report Generator](../api/report_generator.md) - Report generation
- [Tutorial: Create Reports](../tutorials/04-create-reports.md) - Reporting tutorial
