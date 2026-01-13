#!/usr/bin/env python3
"""
Component Composition Example

Demonstrates reusable component composition including:
- Defining components
- Component variables
- Component reuse
- Inline variable assignment
"""


def example_component_composition() -> None:
    """
    Demonstrate reusable component composition.

    Shows:
    - Defining components
    - Component variables
    - Component reuse
    - Inline variable assignment
    """
    from spreadsheet_dl.template_engine.loader import TemplateLoader

    print("=" * 70)
    print("Example 4: Component Composition")
    print("=" * 70)

    # Create template with components
    yaml_content = """
meta:
  name: Component Demo
  version: 1.0.0

variables:
  - name: title
    type: string
    required: true

components:
  header:
    description: Standard header component
    variables:
      - name: title
        type: string
        required: true
      - name: subtitle
        type: string
        default: ""
    rows:
      - cells:
          - value: ${title}
            style: header
            colspan: 3
      - cells:
          - value: ${subtitle}
            style: subheader
            colspan: 3

  footer:
    description: Standard footer component
    variables:
      - name: generated_date
        type: string
        default: Today
    rows:
      - cells:
          - value: "Generated: ${generated_date}"
            style: footer
            colspan: 3

sheets:
  - name: Report
    components:
      - "header:title=Monthly Budget,subtitle=December 2025"
      - "footer:generated_date=2025-12-01"

    header:
      cells:
        - value: Category
        - value: Budget
        - value: Actual
"""

    print("\n1. Loading template with components:")
    loader = TemplateLoader()
    template = loader.load_from_string(yaml_content)

    print(f"   Template: {template.name}")
    print(f"   Components defined: {len(template.components)}")
    for comp_name, comp in template.components.items():
        print(f"     • {comp_name}: {comp.description}")
        print(f"       Variables: {len(comp.variables)}")
        print(f"       Rows: {len(comp.rows)}")

    # 2. Render template with components
    print("\n2. Rendering template with components:")
    from spreadsheet_dl.template_engine.renderer import TemplateRenderer

    renderer = TemplateRenderer()
    try:
        result = renderer.render(template, {"title": "My Report"})
        print("   ✓ Template rendered successfully")
        print(f"   Sheets: {len(result.sheets)}")
        for sheet in result.sheets:
            print(f"     • {sheet.name}: {len(sheet.rows)} rows")
    except ValueError as e:
        print(f"   Error: {e}")

    # 3. Component inheritance and reuse
    print("\n3. Component reuse benefits:")
    print("   • Define once, use multiple times")
    print("   • Consistent styling across sheets")
    print("   • Easy maintenance and updates")
    print("   • Variable substitution per usage")

    print("\n✓ Component composition demonstrated")
    print()


if __name__ == "__main__":
    example_component_composition()
