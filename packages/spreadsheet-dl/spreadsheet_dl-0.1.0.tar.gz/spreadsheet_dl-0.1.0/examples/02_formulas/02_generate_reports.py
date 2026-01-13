#!/usr/bin/env python3
"""
Example: Generate budget reports.

This script demonstrates how to generate various
report formats from budget data.
"""

from pathlib import Path

from spreadsheet_dl.domains.finance.report_generator import (
    ReportConfig,
    ReportGenerator,
    generate_monthly_report,
)


def example_text_report(ods_path: Path) -> None:
    """Generate plain text report."""
    print("=== Text Report ===")

    generator = ReportGenerator(ods_path)
    report = generator.generate_text_report()

    print(report)
    print()


def example_markdown_report(ods_path: Path) -> None:
    """Generate markdown report."""
    print("=== Markdown Report ===")

    generator = ReportGenerator(ods_path)
    report = generator.generate_markdown_report()

    print(report)
    print()


def example_save_reports(ods_path: Path) -> None:
    """Save reports to files."""
    print("=== Saving Reports ===")

    output_dir = Path("output/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = ReportGenerator(ods_path)

    # Save different formats
    text_path = generator.save_report(output_dir / "budget_report.txt", format="text")
    md_path = generator.save_report(output_dir / "budget_report.md", format="markdown")
    json_path = generator.save_report(output_dir / "budget_report.json", format="json")

    print(f"Text report:     {text_path}")
    print(f"Markdown report: {md_path}")
    print(f"JSON data:       {json_path}")
    print()


def example_custom_config(ods_path: Path) -> None:
    """Generate report with custom configuration."""
    print("=== Custom Config Report ===")

    config = ReportConfig(
        include_category_breakdown=True,
        include_trends=False,
        include_alerts=True,
        include_recommendations=True,
    )

    generator = ReportGenerator(ods_path, config=config)
    report = generator.generate_text_report()

    print(report)
    print()


def example_visualization_data(ods_path: Path) -> None:
    """Get data for charts/visualizations."""
    print("=== Visualization Data ===")

    generator = ReportGenerator(ods_path)
    data = generator.generate_visualization_data()

    # Pie chart data
    print("Pie Chart (Spending by Category):")
    for label, value in zip(
        data["pie_chart"]["labels"],
        data["pie_chart"]["values"],
        strict=True,
    ):
        print(f"  {label}: ${value:,.2f}")
    print()

    # Gauge data
    print(f"Budget Used: {data['gauge']['value']:.1f}%")
    print()


def example_convenience_function(ods_path: Path) -> None:
    """Use convenience function for quick reports."""
    print("=== Convenience Function ===")

    # Return as string
    report = generate_monthly_report(ods_path, format="text")
    print("Generated report string (first 500 chars):")
    if isinstance(report, str):
        print(report[:500])
    else:
        print(f"Unexpected type: {type(report)}")
    print("...")
    print()

    # Save to directory
    output_dir = Path("output/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = generate_monthly_report(ods_path, output_dir=output_dir)
    print(f"Saved to: {path}")


if __name__ == "__main__":
    # Look for a budget file
    budget_path = Path("output/custom_budget_2025_01.ods")

    if not budget_path.exists():
        # Try default path
        from pathlib import Path

        output_dir = Path("output")
        ods_files = list(output_dir.glob("*.ods"))
        if ods_files:
            budget_path = ods_files[0]
        else:
            print("No budget file found. Run create_budget.py first.")
            exit(1)

    print(f"Generating reports for: {budget_path}")
    print()

    example_text_report(budget_path)
    example_save_reports(budget_path)
    example_visualization_data(budget_path)
