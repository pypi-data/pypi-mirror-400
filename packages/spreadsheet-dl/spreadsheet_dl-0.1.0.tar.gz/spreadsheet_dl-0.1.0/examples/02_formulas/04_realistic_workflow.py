#!/usr/bin/env python3
"""
Realistic Family Budget Workflow Example

Demonstrates creating a complete monthly budget with:
- Realistic expense entries
- Custom budget allocations
- Multiple spending categories
- Real-world scenarios
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from spreadsheet_dl.domains.finance.ods_generator import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
)


def create_december_2025_budget() -> Path:
    """Create a realistic December 2025 family budget."""

    # December 2025 expenses (family of 4)
    expenses = [
        # Week 1
        ExpenseEntry(
            date(2025, 12, 1),
            ExpenseCategory.GROCERIES,
            "Whole Foods - weekly shop",
            Decimal("182.45"),
        ),
        ExpenseEntry(
            date(2025, 12, 2),
            ExpenseCategory.UTILITIES,
            "Electric bill",
            Decimal("135.22"),
        ),
        ExpenseEntry(
            date(2025, 12, 3),
            ExpenseCategory.TRANSPORTATION,
            "Gas station",
            Decimal("52.00"),
        ),
        # Week 2
        ExpenseEntry(
            date(2025, 12, 5),
            ExpenseCategory.GROCERIES,
            "Trader Joe's",
            Decimal("95.30"),
        ),
        ExpenseEntry(
            date(2025, 12, 7),
            ExpenseCategory.DINING_OUT,
            "Family dinner - Italian restaurant",
            Decimal("89.50"),
        ),
        ExpenseEntry(
            date(2025, 12, 8),
            ExpenseCategory.HEALTHCARE,
            "Pharmacy - prescriptions",
            Decimal("45.00"),
        ),
        ExpenseEntry(
            date(2025, 12, 9),
            ExpenseCategory.ENTERTAINMENT,
            "Movie tickets + snacks",
            Decimal("68.00"),
        ),
        # Week 3
        ExpenseEntry(
            date(2025, 12, 10),
            ExpenseCategory.GROCERIES,
            "Costco bulk purchase",
            Decimal("245.60"),
        ),
        ExpenseEntry(
            date(2025, 12, 11),
            ExpenseCategory.CLOTHING,
            "Kids winter jackets",
            Decimal("135.00"),
        ),
        ExpenseEntry(
            date(2025, 12, 12),
            ExpenseCategory.TRANSPORTATION,
            "Gas + car wash",
            Decimal("58.25"),
        ),
        ExpenseEntry(
            date(2025, 12, 14),
            ExpenseCategory.SUBSCRIPTIONS,
            "Netflix + Spotify family",
            Decimal("32.98"),
        ),
        # Week 4
        ExpenseEntry(
            date(2025, 12, 16),
            ExpenseCategory.GROCERIES,
            "Fresh market",
            Decimal("72.80"),
        ),
        ExpenseEntry(
            date(2025, 12, 17),
            ExpenseCategory.GIFTS,
            "Birthday present",
            Decimal("65.00"),
        ),
        ExpenseEntry(
            date(2025, 12, 19),
            ExpenseCategory.DINING_OUT,
            "Pizza night",
            Decimal("45.75"),
        ),
        ExpenseEntry(
            date(2025, 12, 20),
            ExpenseCategory.PERSONAL,
            "Haircuts (2)",
            Decimal("80.00"),
        ),
        ExpenseEntry(
            date(2025, 12, 22),
            ExpenseCategory.GROCERIES,
            "Holiday dinner ingredients",
            Decimal("156.30"),
        ),
        ExpenseEntry(
            date(2025, 12, 24),
            ExpenseCategory.ENTERTAINMENT,
            "Holiday event tickets",
            Decimal("95.00"),
        ),
        ExpenseEntry(
            date(2025, 12, 26),
            ExpenseCategory.GIFTS,
            "Christmas presents",
            Decimal("425.00"),
        ),
        ExpenseEntry(
            date(2025, 12, 28),
            ExpenseCategory.HEALTHCARE,
            "Doctor visit copay",
            Decimal("35.00"),
        ),
        ExpenseEntry(
            date(2025, 12, 30),
            ExpenseCategory.TRANSPORTATION,
            "End of month gas fill-up",
            Decimal("54.00"),
        ),
    ]

    # Monthly budget allocations (family of 4)
    allocations = [
        BudgetAllocation(ExpenseCategory.HOUSING, Decimal("2200.00")),  # Rent/mortgage
        BudgetAllocation(
            ExpenseCategory.UTILITIES, Decimal("250.00")
        ),  # Electric, water, gas
        BudgetAllocation(
            ExpenseCategory.GROCERIES, Decimal("800.00")
        ),  # Weekly shopping
        BudgetAllocation(
            ExpenseCategory.TRANSPORTATION, Decimal("300.00")
        ),  # Gas, maintenance
        BudgetAllocation(
            ExpenseCategory.HEALTHCARE, Decimal("200.00")
        ),  # Insurance, copays
        BudgetAllocation(
            ExpenseCategory.INSURANCE, Decimal("450.00")
        ),  # Car, life insurance
        BudgetAllocation(
            ExpenseCategory.ENTERTAINMENT, Decimal("200.00")
        ),  # Activities, movies
        BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("250.00")),  # Restaurants
        BudgetAllocation(
            ExpenseCategory.CLOTHING, Decimal("150.00")
        ),  # Seasonal purchases
        BudgetAllocation(ExpenseCategory.PERSONAL, Decimal("100.00")),  # Haircuts, etc.
        BudgetAllocation(
            ExpenseCategory.EDUCATION, Decimal("75.00")
        ),  # Books, supplies
        BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("750.00")),  # Emergency fund
        BudgetAllocation(
            ExpenseCategory.DEBT_PAYMENT, Decimal("400.00")
        ),  # Credit cards, loans
        BudgetAllocation(
            ExpenseCategory.GIFTS, Decimal("150.00")
        ),  # Birthdays, holidays
        BudgetAllocation(
            ExpenseCategory.SUBSCRIPTIONS, Decimal("125.00")
        ),  # Streaming, apps
        BudgetAllocation(
            ExpenseCategory.MISCELLANEOUS, Decimal("100.00")
        ),  # Unexpected
    ]

    # Generate the budget
    generator = OdsGenerator()
    output_path = generator.create_budget_spreadsheet(
        output_path=Path("output/december_2025_family_budget.ods"),
        month=12,
        year=2025,
        expenses=expenses,
        budget_allocations=allocations,
    )

    # Calculate summary
    total_expenses = sum(e.amount for e in expenses)
    total_budget = sum(a.monthly_budget for a in allocations)
    remaining = total_budget - total_expenses

    print("=" * 70)
    print("December 2025 Family Budget - Generated Successfully!")
    print("=" * 70)
    print(f"\n📄 File: {output_path}")
    print("\n📊 Summary:")
    print(f"  Total Budget:   ${total_budget:,.2f}")
    print(f"  Total Expenses: ${total_expenses:,.2f}")
    print(
        f"  Remaining:      ${remaining:,.2f} ({remaining / total_budget * 100:.1f}%)"
    )
    print("\n📝 Details:")
    print(f"  Expense Entries: {len(expenses)}")
    print(f"  Budget Categories: {len(allocations)}")
    print("\n🎯 Top Spending Categories:")

    # Calculate spending by category
    category_spending: dict[str, Decimal] = {}
    for expense in expenses:
        cat = expense.category.value
        category_spending[cat] = (
            category_spending.get(cat, Decimal("0")) + expense.amount
        )

    top_5 = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
    for cat, amount in top_5:
        print(f"  {cat:<20} ${amount:>8,.2f}")

    print("\n✅ Ready to upload to Nextcloud!")
    print("✅ Compatible with Collabora Office on desktop and mobile")
    print("✅ Formulas will calculate automatically when opened")
    print("=" * 70)

    return output_path


if __name__ == "__main__":
    create_december_2025_budget()
