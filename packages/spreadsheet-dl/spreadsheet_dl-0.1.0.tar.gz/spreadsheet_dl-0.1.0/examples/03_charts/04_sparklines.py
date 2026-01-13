#!/usr/bin/env python3
"""
Sparklines Demo: LibreOffice Mini-Charts

Demonstrates sparkline functionality for ODS documents.
Sparklines are mini charts that fit in a single cell.

Requirements:
    - LibreOffice Calc 7.0+ to view sparklines
    - Sparklines are LibreOffice-specific (not compatible with Excel/Sheets)

Implements: FUTURE-003 (Sparkline application to ODS documents)
"""

from pathlib import Path

from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import P

from spreadsheet_dl.interactive import InteractiveOdsBuilder, SparklineConfig


def create_sample_data_table(doc: OpenDocumentSpreadsheet) -> Table:
    """Create a sample data table with numeric values."""
    table = Table(name="Sales Data")

    # Add columns
    for _ in range(15):
        col = TableColumn()
        table.addElement(col)

    # Header row
    header_row = TableRow()
    headers = [
        "Product",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
        "Trend",
    ]
    for header in headers:
        cell = TableCell()
        p = P()
        p.addText(header)
        cell.addElement(p)
        header_row.addElement(cell)
    table.addElement(header_row)

    # Data rows with sample sales figures
    products = [
        ("Product A", [120, 135, 128, 145, 152, 148, 160, 155, 170, 165, 180, 195]),
        ("Product B", [200, 195, 210, 205, 220, 215, 230, 225, 240, 235, 250, 245]),
        ("Product C", [80, 90, 85, 95, 100, 92, 105, 110, 108, 115, 120, 125]),
    ]

    for product_name, monthly_sales in products:
        row = TableRow()

        # Product name
        cell = TableCell()
        p = P()
        p.addText(product_name)
        cell.addElement(p)
        row.addElement(cell)

        # Monthly sales values
        for value in monthly_sales:
            cell = TableCell(valuetype="float", value=str(value))
            p = P()
            p.addText(str(value))
            cell.addElement(p)
            row.addElement(cell)

        # Placeholder for sparkline (will be filled by InteractiveOdsBuilder)
        cell = TableCell()
        row.addElement(cell)

        table.addElement(row)

    return table


def create_sales_dashboard() -> None:
    """Create sales dashboard with sparklines."""
    print("Creating sales dashboard with sparklines...")

    # Create ODS document
    doc = OpenDocumentSpreadsheet()

    # Add sample data table
    table = create_sample_data_table(doc)
    doc.spreadsheet.addElement(table)

    # Create interactive builder
    builder = InteractiveOdsBuilder()

    # Add line sparklines for each product
    print("  Adding line sparklines...")
    for row_idx in range(1, 4):  # Rows 2-4 (1-indexed)
        sparkline = SparklineConfig(
            data_range=f"B{row_idx + 1}:M{row_idx + 1}",  # Jan-Dec data
            sparkline_type="line",
            color="#2196F3",
            high_color="#4CAF50",  # Green for peak
            low_color="#F44336",  # Red for valley
            show_markers=True,
            line_width=1.5,
        )
        builder.add_sparkline(f"N{row_idx + 1}", sparkline)

    # Apply sparklines to document
    builder.apply_to_document(doc)

    # Save document
    output_file = Path("sales_dashboard_sparklines.ods")
    doc.save(output_file)
    print(f"✓ Created: {output_file}")
    print("  Open in LibreOffice Calc to view sparklines")


def create_financial_dashboard() -> None:
    """Create financial dashboard with multiple sparkline types."""
    print("\nCreating financial dashboard...")

    doc = OpenDocumentSpreadsheet()
    table = Table(name="Financial Dashboard")

    # Add columns
    for _ in range(10):
        col = TableColumn()
        table.addElement(col)

    # Headers
    header_row = TableRow()
    for header in ["Metric", "Q1", "Q2", "Q3", "Q4", "Trend"]:
        cell = TableCell()
        p = P()
        p.addText(header)
        cell.addElement(p)
        header_row.addElement(cell)
    table.addElement(header_row)

    # Financial data
    metrics = [
        ("Revenue", [1200000, 1350000, 1280000, 1450000]),
        ("Expenses", [850000, 920000, 880000, 950000]),
        ("Profit", [350000, 430000, 400000, 500000]),
    ]

    for metric_name, quarterly_values in metrics:
        row = TableRow()

        # Metric name
        cell = TableCell()
        p = P()
        p.addText(metric_name)
        cell.addElement(p)
        row.addElement(cell)

        # Quarterly values
        for value in quarterly_values:
            cell = TableCell(valuetype="float", value=str(value))
            p = P()
            p.addText(f"${value:,}")
            cell.addElement(p)
            row.addElement(cell)

        # Placeholder for sparkline
        cell = TableCell()
        row.addElement(cell)

        table.addElement(row)

    doc.spreadsheet.addElement(table)

    # Create builder and add sparklines
    builder = InteractiveOdsBuilder()

    print("  Adding revenue sparkline (line)...")
    builder.add_sparkline(
        "F2",
        SparklineConfig(
            data_range="B2:E2",
            sparkline_type="line",
            color="#4CAF50",
            show_markers=True,
            line_width=2.0,
        ),
    )

    print("  Adding expense sparkline (line)...")
    builder.add_sparkline(
        "F3",
        SparklineConfig(
            data_range="B3:E3",
            sparkline_type="line",
            color="#F44336",
            show_markers=True,
            line_width=2.0,
        ),
    )

    print("  Adding profit sparkline (column)...")
    builder.add_sparkline(
        "F4",
        SparklineConfig(
            data_range="B4:E4",
            sparkline_type="column",
            color="#4CAF50",
            column_width=0.8,
        ),
    )

    # Apply to document
    builder.apply_to_document(doc)

    # Save
    output_file = Path("financial_dashboard_sparklines.ods")
    doc.save(output_file)
    print(f"✓ Created: {output_file}")


def create_stock_portfolio() -> None:
    """Create stock portfolio with price trends."""
    print("\nCreating stock portfolio tracker...")

    doc = OpenDocumentSpreadsheet()
    table = Table(name="Portfolio")

    # Add columns
    for _ in range(12):
        col = TableColumn()
        table.addElement(col)

    # Header
    header_row = TableRow()
    headers = [
        "Symbol",
        "W1",
        "W2",
        "W3",
        "W4",
        "W5",
        "W6",
        "W7",
        "W8",
        "W9",
        "W10",
        "Trend",
    ]
    for header in headers:
        cell = TableCell()
        p = P()
        p.addText(header)
        cell.addElement(p)
        header_row.addElement(cell)
    table.addElement(header_row)

    # Stock data (10 weeks of prices)
    stocks = [
        ("AAPL", [145, 148, 152, 149, 155, 158, 156, 162, 165, 168]),
        ("GOOGL", [2800, 2850, 2820, 2900, 2950, 2920, 3000, 3050, 3020, 3100]),
        ("MSFT", [290, 295, 292, 298, 305, 302, 310, 315, 312, 320]),
    ]

    for symbol, weekly_prices in stocks:
        row = TableRow()

        # Symbol
        cell = TableCell()
        p = P()
        p.addText(symbol)
        cell.addElement(p)
        row.addElement(cell)

        # Weekly prices
        for price in weekly_prices:
            cell = TableCell(valuetype="float", value=str(price))
            p = P()
            p.addText(f"${price}")
            cell.addElement(p)
            row.addElement(cell)

        # Sparkline placeholder
        cell = TableCell()
        row.addElement(cell)

        table.addElement(row)

    doc.spreadsheet.addElement(table)

    # Add sparklines
    builder = InteractiveOdsBuilder()

    print("  Adding stock price sparklines...")
    for idx, (_symbol, _) in enumerate(stocks):
        builder.add_sparkline(
            f"L{idx + 2}",
            SparklineConfig(
                data_range=f"B{idx + 2}:K{idx + 2}",
                sparkline_type="line",
                color="#2196F3",
                high_color="#4CAF50",
                low_color="#F44336",
                last_color="#FF9800",
                show_markers=True,
                line_width=1.5,
            ),
        )

    builder.apply_to_document(doc)

    # Save
    output_file = Path("stock_portfolio_sparklines.ods")
    doc.save(output_file)
    print(f"✓ Created: {output_file}")


def main() -> None:
    """Run all sparkline demos."""
    print("=" * 60)
    print("Sparklines Demo - LibreOffice Mini-Charts")
    print("=" * 60)
    print()
    print("NOTE: Sparklines require LibreOffice Calc 7.0+ to view.")
    print("They will NOT render in Excel or Google Sheets.")
    print()

    create_sales_dashboard()
    create_financial_dashboard()
    create_stock_portfolio()

    print()
    print("=" * 60)
    print("✓ All examples created successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Open any .ods file in LibreOffice Calc")
    print("2. Sparklines will render in the 'Trend' column")
    print("3. Click on sparkline cells to see the formula")
    print()


if __name__ == "__main__":
    main()
