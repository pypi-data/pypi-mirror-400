#!/usr/bin/env python3
"""
Example: Create a monthly budget spreadsheet.

This script demonstrates how to create a budget ODS file
with custom categories and pre-populated expenses.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from spreadsheet_dl.domains.finance.ods_generator import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    create_monthly_budget,
)


def example_simple() -> None:
    """Create a simple monthly budget with defaults."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Using convenience function
    path = create_monthly_budget(output_dir)
    print(f"Created budget at: {path}")


def example_custom() -> None:
    """Create a budget with custom allocations and expenses."""
    generator = OdsGenerator()

    # Custom budget allocations
    allocations = [
        BudgetAllocation(
            ExpenseCategory.HOUSING,
            Decimal("1800"),
            notes="Rent + renters insurance",
        ),
        BudgetAllocation(
            ExpenseCategory.GROCERIES,
            Decimal("700"),
            notes="Family of 4",
        ),
        BudgetAllocation(
            ExpenseCategory.UTILITIES,
            Decimal("250"),
            notes="Electric, gas, water, internet",
        ),
        BudgetAllocation(
            ExpenseCategory.TRANSPORTATION,
            Decimal("500"),
            notes="Car payment + gas + insurance",
        ),
        BudgetAllocation(
            ExpenseCategory.HEALTHCARE,
            Decimal("200"),
        ),
        BudgetAllocation(
            ExpenseCategory.SAVINGS,
            Decimal("600"),
            notes="Emergency fund + retirement",
        ),
        BudgetAllocation(
            ExpenseCategory.ENTERTAINMENT,
            Decimal("150"),
        ),
        BudgetAllocation(
            ExpenseCategory.DINING_OUT,
            Decimal("200"),
        ),
    ]

    # Pre-populate some expenses
    expenses = [
        ExpenseEntry(
            date=date(2025, 1, 1),
            category=ExpenseCategory.HOUSING,
            description="January rent",
            amount=Decimal("1650"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 5),
            category=ExpenseCategory.GROCERIES,
            description="Weekly grocery run",
            amount=Decimal("185.50"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 8),
            category=ExpenseCategory.UTILITIES,
            description="Electric bill",
            amount=Decimal("95.00"),
        ),
    ]

    output_path = Path("output/custom_budget_2025_01.ods")
    output_path.parent.mkdir(exist_ok=True)

    path = generator.create_budget_spreadsheet(
        output_path,
        month=1,
        year=2025,
        budget_allocations=allocations,
        expenses=expenses,
    )
    print(f"Created custom budget at: {path}")


def example_template() -> None:
    """Create a blank expense tracking template."""
    generator = OdsGenerator()

    output_path = Path("output/expense_template.ods")
    output_path.parent.mkdir(exist_ok=True)

    path = generator.create_expense_template(output_path)
    print(f"Created template at: {path}")


if __name__ == "__main__":
    print("Example 1: Simple budget with defaults")
    example_simple()
    print()

    print("Example 2: Custom budget with allocations")
    example_custom()
    print()

    print("Example 3: Expense template")
    example_template()
