#!/usr/bin/env python3
"""
XLSX Export Example

Demonstrates exporting spreadsheets to Excel format (.xlsx).
SpreadsheetDL creates ODS natively but can export to XLSX.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from spreadsheet_dl import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    export_to_xlsx,
)


def main() -> None:
    """Demonstrate XLSX export functionality."""
    print("=" * 70)
    print("XLSX Export Example")
    print("=" * 70)
    print()

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Create a sample budget in ODS format first
    print("Step 1: Creating ODS budget...")
    allocations = [
        BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1800.00")),
        BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600.00")),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("250.00")),
    ]

    expenses = [
        ExpenseEntry(
            date=date(2026, 1, 1),
            category=ExpenseCategory.HOUSING,
            description="Rent",
            amount=Decimal("1800.00"),
        ),
    ]

    generator = OdsGenerator()
    ods_path = generator.create_budget_spreadsheet(
        output_dir / "budget.ods",
        month=1,
        year=2026,
        budget_allocations=allocations,
        expenses=expenses,
    )

    print(f"  Created: {ods_path}")

    # Export to XLSX
    print("\nStep 2: Exporting to XLSX...")
    xlsx_path = output_dir / "budget.xlsx"
    export_to_xlsx(ods_path, xlsx_path)

    print(f"  Exported: {xlsx_path}")

    # Summary
    print("\n" + "=" * 70)
    print("Export Complete!")
    print("=" * 70)
    print(f"\nODS file:  {ods_path}")
    print(f"XLSX file: {xlsx_path}")
    print("\nThe XLSX file can be opened in:")
    print("- Microsoft Excel")
    print("- Google Sheets")
    print("- LibreOffice Calc")
    print("- Any spreadsheet application")


if __name__ == "__main__":
    main()
