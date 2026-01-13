#!/usr/bin/env python3
"""
Complete Template Example

Demonstrates a complete budget template including:
- Full template structure
- Variable validation
- Sheet rendering
- Formulas in templates
- Styling
"""


def example_complete_template() -> None:
    """
    Demonstrate a complete budget template.

    Shows:
    - Full template structure
    - Variable validation
    - Sheet rendering
    - Formulas in templates
    - Styling
    """
    from spreadsheet_dl.template_engine.loader import TemplateLoader
    from spreadsheet_dl.template_engine.renderer import TemplateRenderer

    print("=" * 70)
    print("Example 5: Complete Budget Template")
    print("=" * 70)

    # Create comprehensive budget template
    yaml_content = """
meta:
  name: Monthly Budget Template
  version: 2.0.0
  description: Complete monthly budget with categories and analysis
  author: SpreadsheetDL
  theme: professional

variables:
  - name: month
    type: integer
    description: Month number (1-12)
    required: true
    validation: "1 <= value <= 12"

  - name: year
    type: integer
    description: Year
    required: true

  - name: categories
    type: list
    description: Budget categories
    default: ["Housing", "Food", "Transportation", "Entertainment"]

  - name: currency_symbol
    type: string
    description: Currency symbol
    default: "$"

styles:
  header:
    font_weight: bold
    background_color: "#4472C4"
    font_color: "#FFFFFF"

  total:
    font_weight: bold
    border_top: "2pt solid #000000"

  currency:
    format_code: "$#,##0.00"

sheets:
  - name: ${month_name(month)} ${year} Budget
    freeze_rows: 1
    freeze_cols: 1

    columns:
      - name: Category
        width: 5cm
      - name: Budgeted
        width: 3cm
        type: currency
      - name: Actual
        width: 3cm
        type: currency
      - name: Variance
        width: 3cm
        type: currency
      - name: "Percent of Budget"
        width: 3cm
        type: percentage

    header:
      style: header
      cells:
        - value: Category
        - value: Budgeted
        - value: Actual
        - value: Variance
        - value: Percent of Budget

    data_rows:
      repeat: 1
      cells:
        - value: ""
          type: string
        - value: ""
          type: currency
        - value: ""
          type: currency
        - formula: "=C2-B2"
          type: currency
        - formula: "=C2/B2"
          type: percentage

    total_row:
      style: total
      cells:
        - value: "TOTAL"
        - formula: "=SUM(B2:B10)"
          style: currency
        - formula: "=SUM(C2:C10)"
          style: currency
        - formula: "=SUM(D2:D10)"
          style: currency
        - formula: "=C11/B11"
          type: percentage
"""

    print("\n1. Loading complete budget template:")
    loader = TemplateLoader()
    template = loader.load_from_string(yaml_content)

    print(f"   Template: {template.name}")
    print(f"   Version: {template.version}")
    print(f"   Description: {template.description}")
    print(f"   Variables: {len(template.variables)}")
    print(f"   Sheets: {len(template.sheets)}")
    print(f"   Styles defined: {len(template.styles)}")

    # 2. Show template variables
    print("\n2. Template variables:")
    for var in template.variables:
        required_str = "required" if var.required else "optional"
        default_str = f", default={var.default}" if var.default else ""
        print(f"   • {var.name} ({var.type.value}, {required_str}{default_str})")
        print(f"     {var.description}")

    # 3. Validate and render template
    print("\n3. Rendering template with variables:")
    renderer = TemplateRenderer()

    variables = {
        "month": 12,
        "year": 2025,
        "categories": [
            "Housing",
            "Groceries",
            "Utilities",
            "Transportation",
            "Entertainment",
        ],
        "currency_symbol": "$",
    }

    try:
        result = renderer.render(template, variables)
        print("   ✓ Template rendered successfully")
        print("\n   Generated spreadsheet:")
        print(f"     Name: {result.name}")
        print(f"     Sheets: {len(result.sheets)}")

        for sheet in result.sheets:
            print(f"\n     Sheet: {sheet.name}")
            print(f"       Columns: {len(sheet.columns)}")
            for col in sheet.columns:
                print(f"         • {col['name']} ({col['width']})")
            print(f"       Rows: {len(sheet.rows)}")
            print(f"       Frozen: {sheet.freeze_rows} rows, {sheet.freeze_cols} cols")

    except ValueError as e:
        print(f"   ✗ Validation error: {e}")

    # 4. Test with missing required variable
    print("\n4. Testing variable validation:")
    try:
        result = renderer.render(template, {"year": 2025})  # Missing month
        print("   Template rendered (unexpected)")
    except ValueError as e:
        print(f"   ✓ Validation caught missing variable: {e}")

    print("\n✓ Complete template demonstrated")
    print()


if __name__ == "__main__":
    example_complete_template()
