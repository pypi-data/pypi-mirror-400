#!/usr/bin/env python3
"""
Data Science Plugin Example

Demonstrates how domain plugins extend SpreadsheetDL for data science workflows.
This example shows the finance domain in action (already imported by default).
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from spreadsheet_dl import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    analyze_budget,
)


def main() -> None:
    """Demonstrate domain plugin usage with finance domain."""
    print("=" * 70)
    print("Domain Plugin Example - Finance Domain")
    print("=" * 70)
    print()
    print("This example demonstrates how domain plugins extend SpreadsheetDL")
    print("with specialized functions for specific fields.")
    print()

    # Create sample budget using finance domain
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    allocations = [
        BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1800.00")),
        BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600.00")),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("250.00")),
        BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("400.00")),
    ]

    expenses = [
        ExpenseEntry(
            date=date(2026, 1, 1),
            category=ExpenseCategory.HOUSING,
            description="Rent",
            amount=Decimal("1800.00"),
        ),
        ExpenseEntry(
            date=date(2026, 1, 5),
            category=ExpenseCategory.GROCERIES,
            description="Groceries",
            amount=Decimal("145.50"),
        ),
    ]

    generator = OdsGenerator(theme="default")
    budget_path = generator.create_budget_spreadsheet(
        output_dir / "domain_example.ods",
        month=1,
        year=2026,
        budget_allocations=allocations,
        expenses=expenses,
    )

    print(f"Created budget: {budget_path}")

    # Analyze using domain-specific function
    analysis = analyze_budget(budget_path)

    print("\nBudget Analysis (using finance domain plugin):")
    print(f"  Total Budget: ${analysis['total_budget']:,.2f}")
    print(f"  Total Spent: ${analysis['total_spent']:,.2f}")
    print(f"  Remaining: ${analysis['total_remaining']:,.2f}")
    print(f"  Percent Used: {analysis['percent_used']:.1f}%")

    print("\n" + "=" * 70)
    print("Domain plugins provide:")
    print("- Specialized data types (BudgetAllocation, ExpenseEntry)")
    print("- Domain-specific functions (analyze_budget, create_monthly_budget)")
    print("- Format-aware generators (OdsGenerator for finance)")
    print("- Pre-built templates and workflows")
    print("=" * 70)


if __name__ == "__main__":
    main()
