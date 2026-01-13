# Tutorial 4: Create Reports

Learn how to generate comprehensive spending reports in multiple formats for analysis and sharing.

## What You'll Learn

- Generate text and markdown reports
- Export to JSON for custom analysis
- Create visualizations and charts
- Schedule recurring reports
- Customize report parameters

## Prerequisites

- Completed [Tutorial 1: Create a Budget](01-create-budget.md)
- Budget file with some expense data
- Basic understanding of command line

## Quick Reference

```bash
# Text report to console
spreadsheet-dl report budget.ods -f text

# Markdown report to file
spreadsheet-dl report budget.ods -f markdown -o report.md

# JSON data export
spreadsheet-dl report budget.ods -f json -o data.json

# Interactive dashboard
spreadsheet-dl dashboard budget.ods

# Visual charts (HTML)
spreadsheet-dl visualize budget.ods -o dashboard.html
```

## Step 1: Generate a Text Report

Create a simple text report for console viewing:

```bash
spreadsheet-dl report ~/budgets/budget_2026_01.ods -f text
```

Output:

```
================================================================================
BUDGET REPORT
January 2026
================================================================================

SUMMARY
------------------------------------------------------------------------
Total Budget:           $5,000.00
Total Spent:            $2,347.89
Remaining:              $2,652.11
Percentage Used:        46.96%

SPENDING BY CATEGORY
------------------------------------------------------------------------
Groceries               $  645.50 /  $600.00   ( 107.6%)  [OVER]
Dining Out              $  328.00 /  $200.00   ( 164.0%)  [OVER]
Transportation          $  245.00 /  $450.00   (  54.4%)
Utilities               $  285.99 /  $250.00   ( 114.4%)  [OVER]
Housing                 $1,650.00 / $1800.00   (  91.7%)
Entertainment           $   98.40 /  $150.00   (  65.6%)
Healthcare              $  125.00 /  $200.00   (  62.5%)
Savings                 $    0.00 /  $800.00   (   0.0%)

TOP EXPENSES
------------------------------------------------------------------------
1. $1,650.00    Housing         Rent payment
2. $  125.00    Healthcare      Doctor copay
3. $  145.50    Groceries       Weekly shopping
4. $   98.00    Dining Out      Restaurant dinner
5. $   89.99    Utilities       Internet bill

ALERTS
------------------------------------------------------------------------
! Groceries over budget by $45.50 (7.6%)
! Dining Out over budget by $128.00 (64.0%)
! Utilities over budget by $35.99 (14.4%)
! No savings contributions this month

RECOMMENDATIONS
------------------------------------------------------------------------
* Reduce dining out to stay within budget
* Transfer $100 from entertainment to savings
* On track for housing and transportation

================================================================================
Report generated: 2026-01-18 14:32:00
================================================================================
```

## Step 2: Generate Markdown Report

Create a markdown report suitable for documentation or GitHub:

```bash
spreadsheet-dl report ~/budgets/budget_2026_01.ods -f markdown -o monthly_report.md
```

Content of `monthly_report.md`:

```markdown
# Budget Report - January 2026

Generated: 2026-01-18

## Summary

| Metric          | Amount    |
| --------------- | --------- |
| Total Budget    | $5,000.00 |
| Total Spent     | $2,347.89 |
| Remaining       | $2,652.11 |
| Percentage Used | 46.96%    |

## Spending by Category

| Category       | Spent     | Budget    | Usage  | Status |
| -------------- | --------- | --------- | ------ | ------ |
| Groceries      | $645.50   | $600.00   | 107.6% | OVER   |
| Dining Out     | $328.00   | $200.00   | 164.0% | OVER   |
| Transportation | $245.00   | $450.00   | 54.4%  | OK     |
| Utilities      | $285.99   | $250.00   | 114.4% | OVER   |
| Housing        | $1,650.00 | $1,800.00 | 91.7%  | OK     |
| Entertainment  | $98.40    | $150.00   | 65.6%  | OK     |
| Healthcare     | $125.00   | $200.00   | 62.5%  | OK     |
| Savings        | $0.00     | $800.00   | 0.0%   | UNDER  |

## Top Expenses

1. **$1,650.00** - Housing: Rent payment
2. **$125.00** - Healthcare: Doctor copay
3. **$145.50** - Groceries: Weekly shopping
4. **$98.00** - Dining Out: Restaurant dinner
5. **$89.99** - Utilities: Internet bill

## Alerts

- Groceries over budget by $45.50 (7.6%)
- Dining Out over budget by $128.00 (64.0%)
- Utilities over budget by $35.99 (14.4%)
- No savings contributions this month

## Recommendations

- Reduce dining out to stay within budget
- Transfer $100 from entertainment to savings
- On track for housing and transportation
```

## Step 3: Export JSON for Analysis

Export to JSON for custom processing or integration:

```bash
spreadsheet-dl report ~/budgets/budget_2026_01.ods -f json -o budget_data.json
```

Output `budget_data.json`:

```json
{
  "month": 1,
  "year": 2026,
  "summary": {
    "total_budget": 5000.00,
    "total_spent": 2347.89,
    "total_remaining": 2652.11,
    "percent_used": 46.96
  },
  "categories": [
    {
      "name": "Groceries",
      "spent": 645.50,
      "budget": 600.00,
      "remaining": -45.50,
      "percent": 107.58,
      "status": "over"
    },
    ...
  ],
  "top_expenses": [
    {
      "date": "2026-01-01",
      "category": "Housing",
      "description": "Rent payment",
      "amount": 1650.00
    },
    ...
  ],
  "transactions": [...]
}
```

## Step 4: Interactive Dashboard

View an interactive analytics dashboard:

```bash
spreadsheet-dl dashboard ~/budgets/budget_2026_01.ods
```

Output:

```
============================================================
BUDGET DASHBOARD
============================================================

Status: [!] CAUTION - Some categories over budget

SUMMARY
----------------------------------------
  Total Budget:     $    5,000.00
  Total Spent:      $    2,347.89
  Remaining:        $    2,652.11
  Budget Used:           46.96%
  Days Remaining:           13
  Daily Budget:     $      204.01

TOP SPENDING
----------------------------------------
  1. Groceries         $    645.50
  2. Dining Out        $    328.00
  3. Utilities         $    285.99
  4. Transportation    $    245.00
  5. Entertainment     $     98.40

ALERTS
----------------------------------------
  ! Groceries over budget
  ! Dining Out significantly over budget
  ! No savings contributions yet

RECOMMENDATIONS
----------------------------------------
  - Reduce dining out by $50/week
  - You can afford $100 towards savings
  - Daily budget remaining: $204/day
  - Transportation under budget - well done!

============================================================
```

**JSON output for scripts:**

```bash
spreadsheet-dl dashboard budget.ods --json > dashboard_data.json
```

## Step 5: Create Visual Charts

Generate interactive HTML charts:

```bash
# Full dashboard with all charts
spreadsheet-dl visualize budget.ods -o dashboard.html

# Specific chart types
spreadsheet-dl visualize budget.ods -o pie.html -t pie
spreadsheet-dl visualize budget.ods -o bar.html -t bar
spreadsheet-dl visualize budget.ods -o trend.html -t trend
```

Open `dashboard.html` in your browser to see:

- Spending pie chart by category
- Budget vs actual bar chart
- Spending trend over time
- Interactive tooltips and legends

**Using Python to customize:**

```python
from spreadsheet_dl import create_budget_dashboard

# Create custom dashboard
create_budget_dashboard(
    budget_file="budget.ods",
    output_path="custom_dashboard.html",
    theme="dark"  # Use dark theme
)
```

## Step 6: Custom Report Generation

Create custom reports with Python:

```python
#!/usr/bin/env python3
"""Generate custom budget report."""

from spreadsheet_dl import BudgetAnalyzer, ReportGenerator
from datetime import date

def generate_custom_report(budget_file):
    """Create detailed analysis report."""

    # Analyze budget
    analyzer = BudgetAnalyzer(budget_file)
    summary = analyzer.get_summary()
    by_category = analyzer.get_category_breakdown()

    # Create custom report
    report = []
    report.append("=" * 70)
    report.append("CUSTOM BUDGET ANALYSIS")
    report.append(f"Generated: {date.today()}")
    report.append("=" * 70)
    report.append("")

    # Overall status
    if summary.percent_used < 50:
        status = "EXCELLENT - Under 50% used"
    elif summary.percent_used < 75:
        status = "GOOD - Under 75% used"
    elif summary.percent_used < 90:
        status = "CAUTION - Approaching budget limit"
    else:
        status = "WARNING - Over 90% budget used"

    report.append(f"Status: {status}")
    report.append(f"Budget Usage: {summary.percent_used:.1f}%")
    report.append("")

    # Category details
    report.append("CATEGORY ANALYSIS")
    report.append("-" * 70)

    for category, spent in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        # Get budget allocation for this category
        budget_alloc = 0  # Would get from analyzer
        if spent > 0:
            report.append(f"  {category:20} ${spent:>8,.2f}")

    report.append("")

    # Savings analysis
    savings_categories = ['Savings', 'Debt Payment', 'Investment']
    total_savings = sum(by_category.get(cat, 0) for cat in savings_categories)
    savings_rate = (total_savings / summary.total_spent * 100) if summary.total_spent > 0 else 0

    report.append("SAVINGS ANALYSIS")
    report.append("-" * 70)
    report.append(f"  Total Saved:     ${total_savings:,.2f}")
    report.append(f"  Savings Rate:    {savings_rate:.1f}%")
    report.append("")

    # Recommendations
    report.append("PERSONALIZED RECOMMENDATIONS")
    report.append("-" * 70)

    if savings_rate < 10:
        report.append("  * Increase savings rate to at least 10%")
    elif savings_rate >= 20:
        report.append("  * Excellent savings rate! Keep it up!")

    if summary.percent_used > 90:
        report.append("  * Reduce discretionary spending this month")
    elif summary.percent_used < 50:
        report.append("  * Extra budget available - consider increasing savings")

    report.append("")
    report.append("=" * 70)

    return "\n".join(report)

# Generate and save
if __name__ == "__main__":
    report_text = generate_custom_report("budget_2026_01.ods")
    print(report_text)

    # Save to file
    with open("custom_report.txt", "w") as f:
        f.write(report_text)
    print("\nSaved to custom_report.txt")
```

## Step 7: Automated Monthly Reports

Create a script to generate reports automatically:

```python
#!/usr/bin/env python3
"""
Automated monthly report generator.

Run this at month-end to generate all reports.
"""

import sys
from pathlib import Path
from datetime import date
from spreadsheet_dl import ReportGenerator, create_budget_dashboard

def generate_month_end_reports():
    """Generate all monthly reports."""

    # Configuration
    budget_dir = Path.home() / "budgets"
    reports_dir = budget_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Find current month's budget
    today = date.today()
    budget_file = budget_dir / f"budget_{today.year}_{today.month:02d}.ods"

    if not budget_file.exists():
        print(f"Budget file not found: {budget_file}")
        return 1

    print(f"Generating reports for: {budget_file.name}\n")

    # Create report generator
    generator = ReportGenerator(budget_file)

    # Generate text report
    text_path = reports_dir / f"report_{today.year}_{today.month:02d}.txt"
    print(f"1. Text report: {text_path.name}")
    with open(text_path, "w") as f:
        f.write(generator.generate_text_report())

    # Generate markdown report
    md_path = reports_dir / f"report_{today.year}_{today.month:02d}.md"
    print(f"2. Markdown report: {md_path.name}")
    generator.save_report(md_path, format="markdown")

    # Generate JSON data
    json_path = reports_dir / f"data_{today.year}_{today.month:02d}.json"
    print(f"3. JSON data: {json_path.name}")
    generator.save_report(json_path, format="json")

    # Generate HTML dashboard
    html_path = reports_dir / f"dashboard_{today.year}_{today.month:02d}.html"
    print(f"4. HTML dashboard: {html_path.name}")
    create_budget_dashboard(
        budget_file=budget_file,
        output_path=html_path
    )

    print(f"\nAll reports generated in: {reports_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(generate_month_end_reports())
```

Save as `generate_reports.py` and run monthly:

```bash
# Run at month-end
python generate_reports.py
```

## Step 8: Email Reports

Combine with email for automatic delivery:

```python
#!/usr/bin/env python3
"""Email monthly budget report."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from spreadsheet_dl import ReportGenerator

def email_report(budget_file, recipient):
    """Email budget report."""

    # Generate report
    generator = ReportGenerator(budget_file)
    report_text = generator.generate_text_report()

    # Create email
    msg = MIMEMultipart()
    msg['Subject'] = f"Monthly Budget Report - {budget_file.stem}"
    msg['From'] = "your-email@example.com"
    msg['To'] = recipient

    # Add report as body
    body = MIMEText(report_text, 'plain')
    msg.attach(body)

    # Send email (configure your SMTP settings)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("your-email@example.com", "your-app-password")
        server.send_message(msg)

    print(f"Report emailed to {recipient}")

# Usage
email_report("budget_2026_01.ods", "recipient@example.com")
```

## Best Practices

1. **Regular Generation** - Create reports weekly or monthly
2. **Multiple Formats** - Save as markdown (shareable) and JSON (analysis)
3. **Archive Reports** - Keep historical reports for comparison
4. **Customize Thresholds** - Adjust alert levels for your needs
5. **Automate** - Use cron/Task Scheduler for automatic generation

## Report Types Comparison

| Format    | Best For               | Pros                            | Cons               |
| --------- | ---------------------- | ------------------------------- | ------------------ |
| Text      | Quick console viewing  | Fast, simple                    | No formatting      |
| Markdown  | Documentation, sharing | Human-readable, version control | Static             |
| JSON      | Automation, analysis   | Structured, parseable           | Not human-friendly |
| Dashboard | Interactive review     | Real-time, visual               | Terminal only      |
| HTML      | Visualization          | Beautiful charts                | Requires browser   |

## Troubleshooting

**Reports show incorrect totals?**

- Verify budget file has correct data
- Check formulas in LibreOffice Calc
- Ensure all expenses have categories

**Charts not displaying?**

- Check HTML file opens in browser
- Verify chart.js is loading (internet required)
- Try different browser

**JSON export fails?**

- Check file permissions
- Ensure output directory exists
- Verify budget file is valid ODS

## Next Steps

- **[Tutorial 5: Use MCP Tools](05-use-mcp-tools.md)** - AI-powered analysis
- **[Tutorial 6: Customize Themes](06-customize-themes.md)** - Custom styling
- **[Best Practices](../guides/best-practices.md)** - Advanced reporting strategies

## Additional Resources

- [Report API Reference](../api/report_generator.md)
- [Visualization Guide](../guides/visualization.md)
- [CLI Reference](../cli.md)
