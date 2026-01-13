#!/usr/bin/env python3
"""
Example: Import and process bank CSV.

This demonstrates importing bank transactions from a CSV file
and creating a budget spreadsheet.
"""

from pathlib import Path

from spreadsheet_dl import OdsGenerator, import_bank_csv


def main() -> None:
    """Import bank CSV and create budget."""

    # For this example, we'll create a sample CSV first
    sample_csv = Path("output/sample_transactions.csv")
    sample_csv.parent.mkdir(exist_ok=True)

    # Create sample CSV (normally you'd export this from your bank)
    csv_content = """Date,Description,Amount
2026-01-05,"SAFEWAY #1234",-125.50
2026-01-06,"SHELL GAS STATION",-45.00
2026-01-07,"CHIPOTLE MEXICAN",-15.75
2026-01-08,"AMAZON.COM",-89.99
2026-01-10,"NETFLIX.COM",-15.99
2026-01-12,"WHOLE FOODS MARKET",-87.50
2026-01-15,"PG&E ENERGY BILL",-125.00
2026-01-18,"CVS PHARMACY",-32.50
"""

    sample_csv.write_text(csv_content)
    print(f"Created sample CSV: {sample_csv}")

    # Import transactions
    print("\nImporting transactions...")
    transactions = import_bank_csv(sample_csv, bank="auto")

    print(f"Imported {len(transactions)} transactions:")
    for t in transactions:
        print(
            f"  {t.date} | {t.category.value:15} | ${t.amount:>7.2f} | {t.description}"
        )

    # Create budget with imported transactions
    print("\nCreating budget...")
    output_file = Path("output/imported_budget.ods")

    generator = OdsGenerator(theme="default")
    budget_path = generator.create_budget_spreadsheet(
        output_file,
        expenses=transactions,
        month=1,
        year=2026,
    )

    # Summary
    total = sum(t.amount for t in transactions)
    print(f"\nBudget created: {budget_path}")
    print(f"Total imported: ${total:,.2f}")
    print("\nNext steps:")
    print("  1. Open the budget in LibreOffice Calc")
    print("  2. Review auto-categorization")
    print("  3. Adjust categories if needed")
    print("  4. Set budget allocations")


if __name__ == "__main__":
    main()
