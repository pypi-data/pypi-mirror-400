# Analytics Module

## Overview

The analytics module provides advanced budget analytics, trend analysis, and dashboard data generation. It transforms budget data into actionable insights with spending trends, forecasting, category-level analytics, and visualization-ready chart data.

**Key Features:**

- Trend analysis with direction detection (increasing/decreasing/stable)
- Spending forecasts based on historical patterns
- Category-level insights with recommendations
- Budget health status determination
- Day-of-week spending patterns
- Chart-ready data structures for visualization
- Comprehensive dashboard data generation

**Use Cases:**

- Generate executive dashboard data
- Analyze spending trends over time
- Forecast future spending
- Identify spending patterns by day of week
- Generate actionable recommendations
- Create visualization data for charts and graphs

## Data Classes

### TrendData

Trend analysis data for a metric over time.

**Attributes:**

- `periods` (list[str]): Period labels (e.g., "Week 1", "Week 2")
- `values` (list[float]): Values for each period
- `trend_direction` (str): "increasing", "decreasing", or "stable"
- `change_percent` (float): Percentage change from first to last period
- `forecast_next` (float | None): Forecast for next period (optional)

**Example:**

```python
trend = TrendData(
    periods=["Week 1", "Week 2", "Week 3", "Week 4"],
    values=[450.0, 520.0, 480.0, 550.0],
    trend_direction="increasing",
    change_percent=22.2,
    forecast_next=577.5
)
```

### CategoryInsight

Detailed insights for a spending category.

**Attributes:**

- `category` (str): Category name
- `current_spending` (Decimal): Current amount spent
- `budget` (Decimal): Budgeted amount
- `percent_used` (float): Percentage of budget used
- `trend` (str): Spending trend ("increasing", "decreasing", "stable")
- `average_transaction` (Decimal): Average transaction amount
- `transaction_count` (int): Number of transactions
- `largest_transaction` (Decimal): Largest single transaction
- `recommendation` (str | None): AI-generated recommendation (optional)

**Example:**

```python
from decimal import Decimal

insight = CategoryInsight(
    category="Dining Out",
    current_spending=Decimal("450.00"),
    budget=Decimal("500.00"),
    percent_used=90.0,
    trend="increasing",
    average_transaction=Decimal("37.50"),
    transaction_count=12,
    largest_transaction=Decimal("85.00"),
    recommendation="Near budget limit. Consider pausing non-essential Dining Out purchases."
)
```

### DashboardData

Complete dashboard data structure with all analytics.

**Attributes:**

_Summary Metrics:_

- `total_budget` (float): Total budget amount
- `total_spent` (float): Total amount spent
- `total_remaining` (float): Remaining budget
- `percent_used` (float): Percentage of budget used
- `days_remaining` (int): Days left in month
- `daily_budget_remaining` (float): Average daily budget remaining

_Status:_

- `budget_status` (str): "healthy", "caution", "warning", or "critical"
- `status_message` (str): Human-readable status description

_Statistics:_

- `transaction_count` (int): Total number of transactions
- `average_transaction` (float): Average transaction amount
- `largest_expense` (float): Largest single expense
- `spending_by_day` (dict[str, float]): Spending by day of week

_Category Data:_

- `categories` (list[CategoryInsight]): Category-level insights
- `top_spending` (list[tuple[str, float]]): Top spending categories

_Trends:_

- `spending_trend` (TrendData): Overall spending trend
- `category_trends` (dict[str, TrendData]): Trends per category

_Guidance:_

- `alerts` (list[str]): Alert messages
- `recommendations` (list[str]): Actionable recommendations

_Visualization:_

- `charts` (dict[str, Any]): Chart-ready data structures

## Classes

### AnalyticsDashboard

Generate comprehensive analytics dashboard data from budget files.

**Methods:**

```python
def __init__(
    self,
    analyzer: BudgetAnalyzer,
    month: int | None = None,
    year: int | None = None,
) -> None:
    """
    Initialize dashboard generator.

    Args:
        analyzer: BudgetAnalyzer with loaded budget data.
        month: Target month (defaults to current month).
        year: Target year (defaults to current year).
    """
```

```python
@property
def summary(self) -> BudgetSummary:
    """
    Get budget summary (cached).

    Returns:
        BudgetSummary from the analyzer.
    """
```

```python
def generate_dashboard(self) -> DashboardData:
    """
    Generate complete dashboard data with all analytics.

    Returns:
        DashboardData object containing:
        - Summary metrics
        - Budget health status
        - Transaction statistics
        - Category insights with recommendations
        - Spending trends and forecasts
        - Chart-ready visualization data
    """
```

```python
def to_dict(self) -> dict[str, Any]:
    """
    Export dashboard as dictionary.

    Returns:
        Dictionary with all dashboard data, suitable for JSON export.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer
from spreadsheet_dl.domains.finance.analytics import AnalyticsDashboard

# Load budget data
analyzer = BudgetAnalyzer("budget.ods")

# Generate dashboard for current month
dashboard = AnalyticsDashboard(analyzer)
data = dashboard.generate_dashboard()

# Access summary metrics
print(f"Budget Status: {data.budget_status}")
print(f"Total Spent: ${data.total_spent:,.2f}")
print(f"Days Remaining: {data.days_remaining}")
print(f"Daily Budget: ${data.daily_budget_remaining:.2f}")

# View recommendations
for rec in data.recommendations:
    print(f"- {rec}")

# Access category insights
for insight in data.categories:
    print(f"{insight.category}: {insight.percent_used:.1f}% used")
    if insight.recommendation:
        print(f"  → {insight.recommendation}")

# Get chart data
print(f"Spending trend: {data.spending_trend.trend_direction}")
print(f"Forecast next period: ${data.spending_trend.forecast_next:.2f}")
```

## Functions

### generate_dashboard(ods_path, month=None, year=None) -> dict[str, Any]

Convenience function to generate dashboard data from an ODS file.

**Parameters:**

- `ods_path` (Path | str): Path to ODS budget file
- `month` (int | None): Target month (optional, defaults to current)
- `year` (int | None): Target year (optional, defaults to current)

**Returns:**

- Dictionary with complete dashboard data

**Example:**

```python
from spreadsheet_dl.domains.finance.analytics import generate_dashboard
import json

# Generate dashboard for current month
dashboard_data = generate_dashboard("budget.ods")

# Export to JSON for web app
with open("dashboard.json", "w") as f:
    json.dump(dashboard_data, f, indent=2)

# Access specific data
print(f"Budget Status: {dashboard_data['budget_status']}")
print(f"Status: {dashboard_data['status_message']}")

# Get spending by day
for day, amount in dashboard_data['spending_by_day'].items():
    print(f"{day}: ${amount:.2f}")
```

## Usage Examples

### Basic Dashboard Generation

```python
from spreadsheet_dl.domains.finance.analytics import generate_dashboard

# Quick dashboard generation
data = generate_dashboard("my_budget.ods")

print(f"Budget Health: {data['budget_status']}")
print(f"Message: {data['status_message']}")
print(f"Spent: ${data['total_spent']:,.2f} of ${data['total_budget']:,.2f}")
print(f"Remaining: ${data['total_remaining']:,.2f}")

# Show recommendations
print("\nRecommendations:")
for rec in data['recommendations']:
    print(f"  • {rec}")
```

### Detailed Category Analysis

```python
from spreadsheet_dl.domains.finance.analytics import AnalyticsDashboard
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")
dashboard = AnalyticsDashboard(analyzer)
data = dashboard.generate_dashboard()

# Analyze each category
print("CATEGORY ANALYSIS")
print("=" * 70)
for cat in data.categories:
    status = "✓" if cat.percent_used < 80 else "⚠" if cat.percent_used < 100 else "✗"
    print(f"{status} {cat.category:20} ${cat.current_spending:>8.2f} / ${cat.budget:>8.2f} ({cat.percent_used:>5.1f}%)")
    print(f"   Trend: {cat.trend:12} | Transactions: {cat.transaction_count:3} | Avg: ${cat.average_transaction:.2f}")

    if cat.recommendation:
        print(f"   💡 {cat.recommendation}")
    print()
```

### Trend Analysis

```python
from spreadsheet_dl.domains.finance.analytics import AnalyticsDashboard
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")
dashboard = AnalyticsDashboard(analyzer)
data = dashboard.generate_dashboard()

# Overall spending trend
trend = data.spending_trend
print(f"Spending Trend: {trend.trend_direction}")
print(f"Change: {trend.change_percent:+.1f}%")
if trend.forecast_next:
    print(f"Forecast Next Period: ${trend.forecast_next:.2f}")

# Category-specific trends
print("\nCategory Trends:")
for category, trend_data in data.category_trends.items():
    direction_icon = "📈" if trend_data.trend_direction == "increasing" else \
                     "📉" if trend_data.trend_direction == "decreasing" else "➡️"
    print(f"{direction_icon} {category}: {trend_data.trend_direction} ({trend_data.change_percent:+.1f}%)")
```

### Spending Pattern Analysis

```python
from spreadsheet_dl.domains.finance.analytics import AnalyticsDashboard
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")
dashboard = AnalyticsDashboard(analyzer)
data = dashboard.generate_dashboard()

# Analyze spending by day of week
print("SPENDING BY DAY OF WEEK")
print("-" * 40)
for day, amount in data.spending_by_day.items():
    bar = "█" * int(amount / 20)  # Visual bar chart
    print(f"{day:12} ${amount:>7.2f} {bar}")

# Find highest spending day
max_day = max(data.spending_by_day.items(), key=lambda x: x[1])
print(f"\nHighest spending day: {max_day[0]} (${max_day[1]:.2f})")
```

### Chart Data Export

```python
from spreadsheet_dl.domains.finance.analytics import AnalyticsDashboard
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer
import json

analyzer = BudgetAnalyzer("budget.ods")
dashboard = AnalyticsDashboard(analyzer)
data = dashboard.generate_dashboard()

# Export chart data for visualization library
charts = data.charts

# Pie chart data
print("Pie Chart - Spending by Category:")
print(json.dumps(charts['category_pie'], indent=2))

# Bar chart data
print("\nBar Chart - Budget vs Actual:")
print(json.dumps(charts['budget_vs_actual'], indent=2))

# Gauge chart data
print("\nGauge Chart - Budget Usage:")
print(json.dumps(charts['budget_gauge'], indent=2))

# Line chart data
print("\nLine Chart - Cumulative Spending:")
print(json.dumps(charts['cumulative_spending'], indent=2))
```

### Web Dashboard Integration

```python
from spreadsheet_dl.domains.finance.analytics import generate_dashboard
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/dashboard')
def get_dashboard():
    """API endpoint for dashboard data."""
    data = generate_dashboard("budget.ods")
    return jsonify(data)

@app.route('/api/dashboard/charts')
def get_charts():
    """API endpoint for chart data only."""
    data = generate_dashboard("budget.ods")
    return jsonify(data['charts'])

@app.route('/api/dashboard/recommendations')
def get_recommendations():
    """API endpoint for recommendations."""
    data = generate_dashboard("budget.ods")
    return jsonify(data['recommendations'])
```

### Custom Period Analysis

```python
from spreadsheet_dl.domains.finance.analytics import AnalyticsDashboard
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")

# Analyze specific month
dashboard = AnalyticsDashboard(analyzer, month=6, year=2024)
data = dashboard.generate_dashboard()

print(f"Analysis for: June 2024")
print(f"Status: {data.budget_status}")
print(f"Spent: ${data.total_spent:,.2f}")
```

## See Also

- [budget_analyzer](budget_analyzer.md) - Core budget analysis engine
- [alerts](alerts.md) - Alert monitoring system
- [report_generator](report_generator.md) - Report generation
