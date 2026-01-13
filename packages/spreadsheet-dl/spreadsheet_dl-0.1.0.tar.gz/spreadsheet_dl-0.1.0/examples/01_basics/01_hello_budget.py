#!/usr/bin/env python3
"""
Example: Create a sample budget programmatically.

This demonstrates the basic workflow for creating a monthly budget
with budget allocations and some pre-populated expenses.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from spreadsheet_dl import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
)


def main() -> None:
    """Create a sample monthly budget."""

    # Define budget allocations for the month
    allocations = [
        BudgetAllocation(
            ExpenseCategory.HOUSING,
            Decimal("1800.00"),
            notes="Rent + renters insurance",
        ),
        BudgetAllocation(
            ExpenseCategory.GROCERIES,
            Decimal("600.00"),
            notes="Weekly grocery shopping",
        ),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("250.00")),
        BudgetAllocation(
            ExpenseCategory.TRANSPORTATION,
            Decimal("400.00"),
            notes="Car payment + gas",
        ),
        BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200.00")),
        BudgetAllocation(ExpenseCategory.ENTERTAINMENT, Decimal("150.00")),
        BudgetAllocation(ExpenseCategory.HEALTHCARE, Decimal("200.00")),
        BudgetAllocation(
            ExpenseCategory.SAVINGS,
            Decimal("800.00"),
            notes="Emergency fund + retirement",
        ),
        BudgetAllocation(ExpenseCategory.MISCELLANEOUS, Decimal("100.00")),
    ]

    # Add some sample expenses
    expenses = [
        ExpenseEntry(
            date=date(2026, 1, 1),
            category=ExpenseCategory.HOUSING,
            description="January rent",
            amount=Decimal("1800.00"),
        ),
        ExpenseEntry(
            date=date(2026, 1, 5),
            category=ExpenseCategory.GROCERIES,
            description="Weekly groceries - Safeway",
            amount=Decimal("145.50"),
        ),
        ExpenseEntry(
            date=date(2026, 1, 8),
            category=ExpenseCategory.UTILITIES,
            description="Electric bill",
            amount=Decimal("89.99"),
        ),
        ExpenseEntry(
            date=date(2026, 1, 10),
            category=ExpenseCategory.TRANSPORTATION,
            description="Gas - Shell",
            amount=Decimal("52.00"),
        ),
        ExpenseEntry(
            date=date(2026, 1, 12),
            category=ExpenseCategory.DINING_OUT,
            description="Dinner at Italian restaurant",
            amount=Decimal("78.50"),
        ),
    ]

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Generate the budget
    generator = OdsGenerator(theme="default")
    budget_path = generator.create_budget_spreadsheet(
        output_dir / "example_budget.ods",
        month=1,
        year=2026,
        budget_allocations=allocations,
        expenses=expenses,
    )

    # Print summary
    total_budget = sum(a.monthly_budget for a in allocations)
    total_spent = sum(e.amount for e in expenses)

    print("Budget created successfully!")
    print(f"File: {budget_path}")
    print("\nSummary:")
    print(f"  Total Budget: ${total_budget:,.2f}")
    print(f"  Pre-populated Expenses: ${total_spent:,.2f}")
    print(f"  Remaining: ${total_budget - total_spent:,.2f}")
    print(f"\nOpen {budget_path} in LibreOffice Calc or Excel to view!")


if __name__ == "__main__":
    main()
