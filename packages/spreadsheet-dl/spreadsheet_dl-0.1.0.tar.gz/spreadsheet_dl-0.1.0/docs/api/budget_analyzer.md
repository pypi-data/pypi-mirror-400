# Budget Analyzer Module

## Overview

The budget_analyzer module is the core budget analysis engine for SpreadsheetDL. It provides comprehensive analysis of ODS budget files using pandas for data manipulation. The module extracts expense and budget data, calculates spending metrics, analyzes trends, and generates detailed summaries.

**Key Features:**

- Direct ODS file reading using odfpy
- Pandas-based data analysis for expenses
- Budget vs actual comparison
- Category-level spending breakdown
- Monthly trend analysis
- Alert generation for overspending
- Daily average calculations
- Date range filtering
- JSON export capabilities

**Use Cases:**

- Analyze personal or family budgets
- Track spending by category
- Monitor budget adherence
- Generate spending trends over time
- Export analysis data for reporting
- Filter expenses by category or date range

## Data Classes

### CategorySpending

Spending summary for a single budget category.

**Attributes:**

- `category` (str): Category name
- `budget` (Decimal): Budgeted amount
- `actual` (Decimal): Actual amount spent
- `remaining` (Decimal): Remaining budget (budget - actual)
- `percent_used` (float): Percentage of budget used

### BudgetSummary

Overall budget summary with all categories and alerts.

**Attributes:**

- `total_budget` (Decimal): Total budgeted amount across all categories
- `total_spent` (Decimal): Total amount spent
- `total_remaining` (Decimal): Total remaining budget
- `percent_used` (float): Overall percentage of budget used
- `categories` (list[CategorySpending]): List of category summaries
- `top_categories` (list[tuple[str, Decimal]]): Top 5 spending categories
- `alerts` (list[str]): List of alert messages for overspending

### SpendingTrend

Spending trend data for a specific time period.

**Attributes:**

- `period` (str): Period identifier (e.g., "2024-06")
- `total` (Decimal): Total spending for the period
- `by_category` (dict[str, Decimal]): Spending breakdown by category

## Classes

### BudgetAnalyzer

Main class for analyzing ODS budget files.

**Methods:**

```python
def __init__(self, ods_path: Path | str) -> None:
    """
    Initialize analyzer with an ODS budget file.

    Args:
        ods_path: Path to the ODS budget file containing
                  "Budget" and "Expense Log" sheets.
    """
```

```python
@property
def expenses(self) -> pd.DataFrame:
    """
    Load and return the expense log dataframe.

    Returns:
        DataFrame with columns: Date, Category, Description, Amount, Notes.
        Cached after first load.
    """
```

```python
@property
def budget(self) -> pd.DataFrame:
    """
    Load and return the budget dataframe.

    Returns:
        DataFrame with columns: Category, Monthly Budget, Notes.
        Cached after first load.
    """
```

```python
def get_summary(self) -> BudgetSummary:
    """
    Get comprehensive budget summary.

    Returns:
        BudgetSummary with:
        - Total budget, spent, and remaining amounts
        - Percentage used
        - Category-level breakdown
        - Top spending categories
        - Alerts for categories over 90% or 100%
    """
```

```python
def get_monthly_trend(self, months: int = 6) -> list[SpendingTrend]:
    """
    Get spending trends over recent months.

    Args:
        months: Number of months to analyze (default: 6).

    Returns:
        List of SpendingTrend objects, one per month, sorted by date.
    """
```

```python
def get_category_breakdown(self) -> dict[str, Decimal]:
    """
    Get spending breakdown by category.

    Returns:
        Dictionary mapping category names to total spent amounts.
    """
```

```python
def get_daily_average(self) -> Decimal:
    """
    Calculate average daily spending.

    Returns:
        Average amount spent per day across the expense period.
    """
```

```python
def filter_by_category(self, category: str) -> pd.DataFrame:
    """
    Get expenses for a specific category.

    Args:
        category: Category name to filter.

    Returns:
        DataFrame of expenses in that category.
    """
```

```python
def filter_by_date_range(
    self,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """
    Get expenses within a date range.

    Args:
        start_date: Start of range (inclusive).
        end_date: End of range (inclusive).

    Returns:
        DataFrame of expenses in the date range.
    """
```

```python
def to_dict(self) -> dict[str, Any]:
    """
    Export complete analysis as dictionary.

    Returns:
        Dictionary with all analysis data including:
        - File path
        - Budget totals
        - Category breakdown
        - Top categories
        - Alerts
        - Daily average
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer
from datetime import date

# Load and analyze budget
analyzer = BudgetAnalyzer("family_budget.ods")

# Get summary
summary = analyzer.get_summary()
print(f"Total Budget: ${summary.total_budget}")
print(f"Total Spent: ${summary.total_spent} ({summary.percent_used:.1f}%)")
print(f"Remaining: ${summary.total_remaining}")

# Check alerts
if summary.alerts:
    print("\nAlerts:")
    for alert in summary.alerts:
        print(f"  ⚠ {alert}")

# Category breakdown
for cat in summary.categories:
    print(f"{cat.category}: ${cat.actual} / ${cat.budget} ({cat.percent_used:.0f}%)")

# Filter by category
groceries = analyzer.filter_by_category("Groceries")
print(f"Groceries transactions: {len(groceries)}")

# Daily average
daily_avg = analyzer.get_daily_average()
print(f"Daily average spending: ${daily_avg:.2f}")
```

## Functions

### analyze_budget(ods_path) -> dict[str, Any]

Convenience function to analyze a budget file and return results as a dictionary.

**Parameters:**

- `ods_path` (Path | str): Path to ODS budget file

**Returns:**

- Dictionary with complete analysis results

**Example:**

```python
from spreadsheet_dl.domains.finance.budget_analyzer import analyze_budget

# Quick analysis
results = analyze_budget("budget.ods")

print(f"Budget: ${results['total_budget']}")
print(f"Spent: ${results['total_spent']}")
print(f"Alerts: {len(results['alerts'])}")

# Export to JSON
import json
with open("analysis.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Usage Examples

### Basic Budget Analysis

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

# Analyze budget file
analyzer = BudgetAnalyzer("my_budget.ods")

# Get high-level summary
summary = analyzer.get_summary()

print(f"Budget Overview:")
print(f"  Total Budget: ${summary.total_budget:,.2f}")
print(f"  Total Spent:  ${summary.total_spent:,.2f}")
print(f"  Remaining:    ${summary.total_remaining:,.2f}")
print(f"  Used:         {summary.percent_used:.1f}%")

# Top spending
print("\nTop Spending Categories:")
for i, (category, amount) in enumerate(summary.top_categories, 1):
    print(f"  {i}. {category}: ${amount:,.2f}")
```

### Category Analysis

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")
summary = analyzer.get_summary()

print("CATEGORY ANALYSIS")
print("=" * 70)
print(f"{'Category':<20} {'Budget':>10} {'Actual':>10} {'Remaining':>12} {'%':>6}")
print("-" * 70)

for cat in summary.categories:
    status = "✓" if cat.percent_used < 90 else "⚠"
    print(f"{cat.category:<20} ${cat.budget:>9,.0f} ${cat.actual:>9,.0f} "
          f"${cat.remaining:>11,.0f} {cat.percent_used:>5.0f}% {status}")
```

### Trend Analysis

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")

# Get 6-month trend
trends = analyzer.get_monthly_trend(months=6)

print("SPENDING TRENDS (Last 6 Months)")
print("=" * 60)

for trend in trends:
    print(f"\n{trend.period}")
    print(f"  Total: ${trend.total:,.2f}")
    print(f"  Top categories:")

    # Sort categories by amount
    sorted_cats = sorted(trend.by_category.items(),
                         key=lambda x: x[1], reverse=True)

    for cat, amount in sorted_cats[:5]:
        print(f"    - {cat}: ${amount:,.2f}")
```

### Filtering Expenses

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer
from datetime import date, timedelta

analyzer = BudgetAnalyzer("budget.ods")

# Filter by category
dining = analyzer.filter_by_category("Dining Out")
print(f"Dining Out transactions: {len(dining)}")
print(f"Total: ${dining['Amount'].sum():,.2f}")

# Filter by date range
end_date = date.today()
start_date = end_date - timedelta(days=7)
last_week = analyzer.filter_by_date_range(start_date, end_date)

print(f"\nLast 7 days:")
print(f"  Transactions: {len(last_week)}")
print(f"  Total spent: ${last_week['Amount'].sum():,.2f}")

# Detailed transaction view
for _, tx in last_week.iterrows():
    print(f"  {tx['Date'].date()}: {tx['Description']} - ${tx['Amount']:.2f}")
```

### Alert Monitoring

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")
summary = analyzer.get_summary()

# Check for budget issues
if summary.percent_used > 100:
    print("🚨 CRITICAL: Budget exceeded!")
elif summary.percent_used > 90:
    print("⚠️  WARNING: Budget nearly exhausted")
else:
    print("✅ Budget on track")

# Category-specific alerts
if summary.alerts:
    print("\nCategory Alerts:")
    for alert in summary.alerts:
        print(f"  • {alert}")

# Find problem categories
problem_cats = [c for c in summary.categories if c.percent_used >= 100]
if problem_cats:
    print("\nOver-Budget Categories:")
    for cat in problem_cats:
        overage = abs(cat.remaining)
        print(f"  • {cat.category}: Over by ${overage:,.2f}")
```

### Export Analysis

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer
import json

analyzer = BudgetAnalyzer("budget.ods")

# Export complete analysis
analysis = analyzer.to_dict()

# Save to JSON
with open("budget_analysis.json", "w") as f:
    json.dump(analysis, f, indent=2)

# Export category breakdown
breakdown = analyzer.get_category_breakdown()
print("\nCategory Breakdown:")
for category, amount in sorted(breakdown.items(),
                                key=lambda x: x[1], reverse=True):
    print(f"  {category}: ${amount:,.2f}")
```

### Daily Spending Analysis

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget.ods")

# Calculate daily metrics
daily_avg = analyzer.get_daily_average()
summary = analyzer.get_summary()

# Days remaining in month
from datetime import date
import calendar

today = date.today()
days_in_month = calendar.monthrange(today.year, today.month)[1]
days_remaining = days_in_month - today.day + 1

# Calculate daily budget for remaining days
if days_remaining > 0:
    daily_budget = float(summary.total_remaining) / days_remaining
    print(f"Daily Metrics:")
    print(f"  Average daily spending: ${daily_avg:.2f}")
    print(f"  Days remaining: {days_remaining}")
    print(f"  Daily budget remaining: ${daily_budget:.2f}")

    if daily_avg > daily_budget:
        print(f"  ⚠ Current rate exceeds available budget!")
    else:
        print(f"  ✓ Spending within limits")
```

### Integration with Pandas

```python
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer
import pandas as pd

analyzer = BudgetAnalyzer("budget.ods")

# Access raw expense data
expenses_df = analyzer.expenses

# Pandas analysis
print("Expense Statistics:")
print(expenses_df['Amount'].describe())

# Group by category
by_category = expenses_df.groupby('Category')['Amount'].agg(['count', 'sum', 'mean'])
print("\nBy Category:")
print(by_category)

# Find largest transactions
top_expenses = expenses_df.nlargest(10, 'Amount')[['Date', 'Description', 'Category', 'Amount']]
print("\nTop 10 Expenses:")
print(top_expenses)
```

## Implementation Notes

### ODS File Format

The module expects ODS files with two sheets:

**Budget Sheet:**

- Columns: Category, Monthly Budget, Notes
- Contains budget allocations for each category
- TOTAL row is automatically skipped

**Expense Log Sheet:**

- Columns: Date, Category, Description, Amount, Notes
- Contains all expense transactions
- Dates should be in date format
- Amounts can be numbers or currency-formatted strings

### Data Type Handling

The analyzer uses **odfpy** for reliable ODS reading, avoiding pandas ODF engine issues:

- Currency values are properly parsed (removes $ and , symbols)
- Dates are converted to pandas datetime
- Empty/invalid rows are filtered out
- All monetary amounts use `Decimal` for precision

## See Also

- [analytics](analytics.md) - Advanced analytics and dashboards
- [alerts](alerts.md) - Alert monitoring system
- [report_generator](report_generator.md) - Report generation
