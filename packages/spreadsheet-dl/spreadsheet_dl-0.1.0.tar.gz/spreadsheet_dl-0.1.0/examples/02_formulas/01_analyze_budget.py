#!/usr/bin/env python3
"""
Example: Analyze a budget ODS file.

This script demonstrates how to analyze budget data
and generate insights using pandas.
"""

import json
from datetime import date
from pathlib import Path

from spreadsheet_dl.domains.finance.budget_analyzer import (
    BudgetAnalyzer,
    analyze_budget,
)


def example_basic_analysis(ods_path: Path) -> None:
    """Basic budget analysis."""
    print("=== Basic Analysis ===")

    analyzer = BudgetAnalyzer(ods_path)
    summary = analyzer.get_summary()

    print(f"Total Budget:  ${summary.total_budget:,.2f}")
    print(f"Total Spent:   ${summary.total_spent:,.2f}")
    print(f"Remaining:     ${summary.total_remaining:,.2f}")
    print(f"Budget Used:   {summary.percent_used:.1f}%")
    print()

    if summary.alerts:
        print("Alerts:")
        for alert in summary.alerts:
            print(f"  - {alert}")
        print()


def example_category_breakdown(ods_path: Path) -> None:
    """Category spending breakdown."""
    print("=== Category Breakdown ===")

    analyzer = BudgetAnalyzer(ods_path)
    breakdown = analyzer.get_category_breakdown()

    for category, amount in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category:<20} ${amount:>10,.2f}")
    print()


def example_pandas_operations(ods_path: Path) -> None:
    """Direct pandas DataFrame operations."""
    print("=== Pandas Operations ===")

    analyzer = BudgetAnalyzer(ods_path)

    # Access raw DataFrames
    expenses_df = analyzer.expenses
    budget_df = analyzer.budget

    print(f"Expense entries: {len(expenses_df)}")
    print(f"Budget categories: {len(budget_df)}")
    print()

    # Custom pandas analysis
    if not expenses_df.empty:
        print("Expenses by category (count):")
        print(expenses_df["Category"].value_counts())
        print()

        print("Expense statistics:")
        print(expenses_df["Amount"].describe())
        print()


def example_date_filtering(ods_path: Path) -> None:
    """Filter expenses by date range."""
    print("=== Date Filtering ===")

    analyzer = BudgetAnalyzer(ods_path)

    # Filter to first week of January
    start = date(2025, 1, 1)
    end = date(2025, 1, 7)
    week1 = analyzer.filter_by_date_range(start, end)

    print(f"Week 1 expenses: {len(week1)} entries")
    if not week1.empty:
        print(f"Week 1 total: ${week1['Amount'].sum():,.2f}")
    print()


def example_json_export(ods_path: Path) -> None:
    """Export analysis as JSON."""
    print("=== JSON Export ===")

    # Using convenience function
    data = analyze_budget(ods_path)

    print(json.dumps(data, indent=2))
    print()


if __name__ == "__main__":
    # Look for a budget file to analyze
    budget_path = Path("output/custom_budget_2025_01.ods")

    if not budget_path.exists():
        # Create one if it doesn't exist
        print("Creating sample budget file first...")
        from spreadsheet_dl.domains.finance.ods_generator import create_monthly_budget

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        budget_path = create_monthly_budget(output_dir, month=1, year=2025)
        print(f"Created: {budget_path}")
        print()

    print(f"Analyzing: {budget_path}")
    print()

    example_basic_analysis(budget_path)
    example_category_breakdown(budget_path)
    example_pandas_operations(budget_path)
    example_date_filtering(budget_path)
    example_json_export(budget_path)
