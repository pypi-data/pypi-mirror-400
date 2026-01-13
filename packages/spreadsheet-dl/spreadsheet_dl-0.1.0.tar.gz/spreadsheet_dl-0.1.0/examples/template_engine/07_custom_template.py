#!/usr/bin/env python3
"""
Custom Template Creation Example

Demonstrates creating custom templates programmatically including:
- Building template objects in code
- Custom variables and validation
- Dynamic sheet generation
- Template export to YAML
"""


def example_custom_template() -> None:
    """
    Demonstrate creating custom templates programmatically.

    Shows:
    - Building template objects in code
    - Custom variables and validation
    - Dynamic sheet generation
    - Template export to YAML
    """
    from spreadsheet_dl.template_engine.schema import (
        CellTemplate,
        ColumnTemplate,
        RowTemplate,
        SheetTemplate,
        SpreadsheetTemplate,
        TemplateVariable,
        VariableType,
    )

    print("=" * 70)
    print("Example 7: Custom Template Creation")
    print("=" * 70)

    # 1. Create template programmatically
    print("\n1. Creating template programmatically:")

    # Define variables
    variables = [
        TemplateVariable(
            name="report_title",
            type=VariableType.STRING,
            description="Report title",
            required=True,
        ),
        TemplateVariable(
            name="num_rows",
            type=VariableType.NUMBER,
            description="Number of data rows",
            default=10,
        ),
    ]

    # Define columns
    columns = [
        ColumnTemplate(name="ID", width="2cm", type="integer"),
        ColumnTemplate(name="Description", width="6cm", type="string"),
        ColumnTemplate(name="Amount", width="3cm", type="currency"),
    ]

    # Define header row
    header_row = RowTemplate(
        cells=[
            CellTemplate(value="ID", style="header"),
            CellTemplate(value="Description", style="header"),
            CellTemplate(value="Amount", style="header"),
        ],
    )

    # Define data rows
    data_rows = RowTemplate(
        cells=[
            CellTemplate(value="", type="integer"),
            CellTemplate(value="", type="string"),
            CellTemplate(value="", type="currency"),
        ],
        repeat=10,
    )

    # Define total row
    total_row = RowTemplate(
        cells=[
            CellTemplate(value="TOTAL", style="total", colspan=2),
            CellTemplate(formula="=SUM(C2:C11)", style="total"),
        ],
    )

    # Create sheet
    sheet = SheetTemplate(
        name="${report_title}",
        columns=columns,
        header_row=header_row,
        data_rows=data_rows,
        total_row=total_row,
        freeze_rows=1,
    )

    # Create template
    template = SpreadsheetTemplate(
        name="Custom Report Template",
        version="1.0.0",
        description="Programmatically created template",
        variables=variables,
        sheets=[sheet],
        styles={
            "header": {
                "font_weight": "bold",
                "background_color": "#4472C4",
                "font_color": "#FFFFFF",
            },
            "total": {"font_weight": "bold", "border_top": "2pt solid #000000"},
        },
    )

    print(f"   Template created: {template.name}")
    print(f"   Variables: {len(template.variables)}")
    print(f"   Sheets: {len(template.sheets)}")
    print(f"   Columns: {len(template.sheets[0].columns)}")

    # 2. Validate template
    print("\n2. Validating template:")
    test_vars = {"report_title": "My Custom Report"}
    errors = template.validate_variables(test_vars)

    if errors:
        print(f"   ✗ Validation errors: {errors}")
    else:
        print("   ✓ Template validation passed")

    # 3. Render template
    print("\n3. Rendering custom template:")
    from spreadsheet_dl.template_engine.renderer import TemplateRenderer

    renderer = TemplateRenderer()
    result = renderer.render(template, test_vars)

    print("   ✓ Template rendered")
    print(f"   Sheet name: {result.sheets[0].name}")
    print(f"   Rows generated: {len(result.sheets[0].rows)}")

    print("\n✓ Custom template creation demonstrated")
    print()


if __name__ == "__main__":
    example_custom_template()
