#!/usr/bin/env python3
"""
Example: Generate custom report.

This demonstrates generating reports from an existing budget file
in multiple formats.
"""

from pathlib import Path

from spreadsheet_dl import BudgetAnalyzer, ReportGenerator


def main() -> int:
    """Generate reports from budget file."""

    # For this example, ensure you have a budget file
    budget_file = Path("output/example_budget.ods")

    if not budget_file.exists():
        print(f"Budget file not found: {budget_file}")
        print("Run example_budget.py first to create a sample budget.")
        return 1

    print(f"Generating reports for: {budget_file}")

    # Create report generator
    generator = ReportGenerator(budget_file)

    # 1. Generate text report
    print("\n" + "=" * 70)
    print("TEXT REPORT")
    print("=" * 70)
    text_report = generator.generate_text_report()
    print(text_report)

    # Save text report
    text_file = Path("output/report.txt")
    with open(text_file, "w") as f:
        f.write(text_report)
    print(f"\nSaved text report: {text_file}")

    # 2. Generate markdown report
    md_file = Path("output/report.md")
    generator.save_report(md_file, format="markdown")
    print(f"Saved markdown report: {md_file}")

    # 3. Generate JSON data
    json_file = Path("output/report.json")
    generator.save_report(json_file, format="json")
    print(f"Saved JSON data: {json_file}")

    # 4. Custom analysis with BudgetAnalyzer
    print("\n" + "=" * 70)
    print("CUSTOM ANALYSIS")
    print("=" * 70)

    analyzer = BudgetAnalyzer(budget_file)

    # Category breakdown
    by_category = analyzer.get_category_breakdown()
    print("\nSpending by Category:")
    for category, amount in sorted(
        by_category.items(), key=lambda x: x[1], reverse=True
    ):
        if amount > 0:
            print(f"  {category:20} ${amount:>8,.2f}")

    # Summary statistics
    summary = analyzer.get_summary()
    print("\nBudget Summary:")
    print(f"  Total Budget:  ${summary.total_budget:,.2f}")
    print(f"  Total Spent:   ${summary.total_spent:,.2f}")
    print(f"  Remaining:     ${summary.total_remaining:,.2f}")
    print(f"  Percent Used:  {summary.percent_used:.1f}%")

    # Alerts
    if summary.alerts:
        print("\nAlerts:")
        for alert in summary.alerts:
            print(f"  ! {alert}")

    print("\n" + "=" * 70)
    print("Reports generated successfully!")
    print("\nFiles created:")
    print(f"  - {text_file}")
    print(f"  - {md_file}")
    print(f"  - {json_file}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
