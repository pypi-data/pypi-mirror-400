# Report Generator Module

## Overview

The report_generator module creates formatted budget reports in multiple formats (text, markdown, JSON) from analyzed budget data. It generates human-readable summaries, recommendations, and visualization-ready data structures.

**Key Features:**

- Plain text report generation
- Markdown formatted reports
- JSON export for web applications
- Category breakdowns and comparisons
- Automatic recommendations based on spending patterns
- Top spending analysis
- Alert integration
- Configurable report sections
- Visualization data preparation

**Use Cases:**

- Generate monthly budget reports
- Create markdown reports for documentation
- Export data for web dashboards
- Email/print budget summaries
- Generate recommendations
- Track budget health over time

## Classes

### ReportConfig

Configuration for report generation.

**Attributes:**

- `include_category_breakdown` (bool): Include category details (default: True)
- `include_trends` (bool): Include trend analysis (default: True)
- `include_alerts` (bool): Include alert messages (default: True)
- `include_recommendations` (bool): Include recommendations (default: True)
- `trend_months` (int): Months of trend data (default: 6)

**Example:**

```python
from spreadsheet_dl.domains.finance.report_generator import ReportConfig

config = ReportConfig(
    include_category_breakdown=True,
    include_trends=False,  # Skip trends for faster generation
    include_alerts=True,
    include_recommendations=True
)
```

### ReportGenerator

Generate formatted reports from budget analysis.

**Methods:**

```python
def __init__(
    self,
    ods_path: Path | str,
    config: ReportConfig | None = None,
) -> None:
    """
    Initialize report generator.

    Args:
        ods_path: Path to ODS budget file.
        config: Report configuration (uses defaults if None).
    """
```

```python
def generate_text_report(self) -> str:
    """
    Generate plain text budget report.

    Returns:
        Formatted text report with:
        - Header with date
        - Overall summary (budget, spent, remaining, %)
        - Alerts (if any)
        - Category breakdown table
        - Top spending categories
        - Daily average
        - Recommendations
    """
```

```python
def generate_markdown_report(self) -> str:
    """
    Generate Markdown formatted budget report.

    Returns:
        Markdown report with:
        - H1 header with date
        - Summary table
        - Alerts list
        - Category breakdown table (bold for over-budget)
        - Top spending list
        - Recommendations
    """
```

```python
def generate_visualization_data(self) -> dict[str, Any]:
    """
    Generate data suitable for chart visualization.

    Returns:
        Dictionary with chart-ready data:
        - pie_chart: Spending by category
        - bar_chart: Budget vs actual by category
        - gauge: Budget usage percentage
        - summary: High-level metrics
    """
```

```python
def save_report(
    self,
    output_path: Path | str,
    format: str = "markdown",
) -> Path:
    """
    Save report to file.

    Args:
        output_path: Path to save file.
        format: Report format ('text', 'markdown', 'json').

    Returns:
        Path to saved file.
    """
```

**Example:**

```python
from spreadsheet_dl.domains.finance.report_generator import ReportGenerator, ReportConfig

# Create generator
generator = ReportGenerator("budget.ods")

# Generate text report
text_report = generator.generate_text_report()
print(text_report)

# Generate markdown report
md_report = generator.generate_markdown_report()
with open("report.md", "w") as f:
    f.write(md_report)

# Get visualization data
viz_data = generator.generate_visualization_data()
print(f"Budget used: {viz_data['gauge']['value']}%")

# Save reports
generator.save_report("report.txt", format="text")
generator.save_report("report.md", format="markdown")
generator.save_report("report.json", format="json")
```

## Functions

### generate_monthly_report(ods_path, output_dir=None, format="markdown") -> str | Path

Convenience function to generate a monthly report.

**Parameters:**

- `ods_path` (Path | str): Path to ODS budget file
- `output_dir` (Path | str | None): Directory to save (if None, returns string)
- `format` (str): Report format ('text', 'markdown', 'json')

**Returns:**

- Report content (str) if output_dir is None, or Path to saved file

**Example:**

```python
from spreadsheet_dl.domains.finance.report_generator import generate_monthly_report

# Get report as string
report_text = generate_monthly_report("budget.ods", format="markdown")
print(report_text)

# Save to directory
report_path = generate_monthly_report(
    "budget.ods",
    output_dir="reports",
    format="markdown"
)
print(f"Report saved to: {report_path}")
# Creates: reports/budget_report_2024_06.md
```

## Usage Examples

### Basic Report Generation

```python
from spreadsheet_dl.domains.finance.report_generator import generate_monthly_report

# Quick text report
report = generate_monthly_report("budget.ods", format="text")
print(report)
```

### Customized Reports

```python
from spreadsheet_dl.domains.finance.report_generator import ReportGenerator, ReportConfig

# Custom configuration
config = ReportConfig(
    include_category_breakdown=True,
    include_trends=False,  # Skip for speed
    include_alerts=True,
    include_recommendations=True
)

# Generate report
generator = ReportGenerator("budget.ods", config)

# Text version for email
text_report = generator.generate_text_report()
send_email(to="family@example.com", body=text_report)

# Markdown for documentation
md_report = generator.generate_markdown_report()
save_to_wiki(md_report)

# JSON for web app
viz_data = generator.generate_visualization_data()
api_response = {"budget_data": viz_data}
```

### Text Report Format

The generated text report follows this structure:

```
============================================================
BUDGET REPORT - June 2024
============================================================

OVERALL SUMMARY
----------------------------------------
Total Budget:         $5,000.00
Total Spent:          $4,250.00
Remaining:              $750.00
Budget Used:             85.0%

ALERTS
----------------------------------------
  ! WARNING: Dining Out at 95% of budget

CATEGORY BREAKDOWN
----------------------------------------
Category             Budget     Actual    Remain     %
------------------------------------------------------------
Housing              $1,500     $1,500        $0   100%*
Groceries              $600       $550       $50    92%
Dining Out             $400       $380       $20    95%*
Transportation         $300       $280       $20    93%
...

TOP SPENDING CATEGORIES
----------------------------------------
  1. Housing                     $1,500.00
  2. Groceries                     $550.00
  3. Dining Out                    $380.00
  ...

SPENDING METRICS
----------------------------------------
Daily Average:              $141.67

RECOMMENDATIONS
----------------------------------------
  - Dining Out at 95% of budget. Consider pausing.
  - Savings goal not met - contribute $150.00 to reach target

============================================================
Generated: 2024-06-15 14:30
```

### Markdown Report Format

```markdown
# Budget Report - June 2024

_Generated: 2024-06-15 14:30_

## Summary

| Metric       | Amount    |
| ------------ | --------- |
| Total Budget | $5,000.00 |
| Total Spent  | $4,250.00 |
| Remaining    | $750.00   |
| Budget Used  | 85.0%     |

## Alerts

- WARNING: Dining Out at 95% of budget

## Category Breakdown

| Category       | Budget | Actual | Remaining | % Used |
| -------------- | ------ | ------ | --------- | ------ |
| **Housing**    | $1,500 | $1,500 | $0        | 100%   |
| Groceries      | $600   | $550   | $50       | 92%    |
| **Dining Out** | $400   | $380   | $20       | 95%    |

...

## Top Spending

1. **Housing**: $1,500.00
2. **Groceries**: $550.00
3. **Dining Out**: $380.00
   ...

## Recommendations

- Dining Out at 95% of budget. Consider pausing.
- Savings goal not met - contribute $150.00 to reach target
```

### Visualization Data Structure

```python
from spreadsheet_dl.domains.finance.report_generator import ReportGenerator

generator = ReportGenerator("budget.ods")
viz_data = generator.generate_visualization_data()

# Structure:
{
    "pie_chart": {
        "title": "Spending by Category",
        "labels": ["Housing", "Groceries", "Dining Out", ...],
        "values": [1500.0, 550.0, 380.0, ...]
    },
    "bar_chart": {
        "title": "Budget vs Actual by Category",
        "categories": ["Housing", "Groceries", ...],
        "budget": [1500.0, 600.0, ...],
        "actual": [1500.0, 550.0, ...]
    },
    "gauge": {
        "title": "Budget Used",
        "value": 85.0,
        "max": 100
    },
    "summary": {
        "total_budget": 5000.0,
        "total_spent": 4250.0,
        "total_remaining": 750.0,
        "percent_used": 85.0
    }
}
```

### Integration with Charts

```python
from spreadsheet_dl.domains.finance.report_generator import ReportGenerator
import matplotlib.pyplot as plt

generator = ReportGenerator("budget.ods")
data = generator.generate_visualization_data()

# Pie chart
pie = data['pie_chart']
plt.figure(figsize=(8, 8))
plt.pie(pie['values'], labels=pie['labels'], autopct='%1.1f%%')
plt.title(pie['title'])
plt.savefig("spending_pie.png")

# Bar chart
bar = data['bar_chart']
import numpy as np
x = np.arange(len(bar['categories']))
width = 0.35
plt.figure(figsize=(12, 6))
plt.bar(x - width/2, bar['budget'], width, label='Budget')
plt.bar(x + width/2, bar['actual'], width, label='Actual')
plt.xlabel('Category')
plt.ylabel('Amount ($)')
plt.title(bar['title'])
plt.xticks(x, bar['categories'], rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig("budget_vs_actual.png")
```

### Automated Monthly Reports

```python
from spreadsheet_dl.domains.finance.report_generator import generate_monthly_report
from datetime import date
import os

def create_monthly_reports(budget_file, output_base="reports"):
    """Generate all report formats for archival."""

    today = date.today()
    month_dir = os.path.join(output_base, f"{today.year}-{today.month:02d}")
    os.makedirs(month_dir, exist_ok=True)

    # Generate all formats
    formats = ["text", "markdown", "json"]
    paths = {}

    for fmt in formats:
        path = generate_monthly_report(
            budget_file,
            output_dir=month_dir,
            format=fmt
        )
        paths[fmt] = path
        print(f"Generated {fmt}: {path}")

    return paths

# Usage
reports = create_monthly_reports("budget.ods")
```

### Email Report

```python
from spreadsheet_dl.domains.finance.report_generator import ReportGenerator
import smtplib
from email.mime.text import MIMEText

generator = ReportGenerator("budget.ods")
report = generator.generate_text_report()

# Send email
msg = MIMEText(report)
msg['Subject'] = 'Monthly Budget Report'
msg['From'] = 'budget@example.com'
msg['To'] = 'family@example.com'

with smtplib.SMTP('localhost') as server:
    server.send_message(msg)
```

## See Also

- [budget_analyzer](budget_analyzer.md) - Core budget analysis
- [analytics](analytics.md) - Advanced analytics and dashboards
- [alerts](alerts.md) - Alert system integration
