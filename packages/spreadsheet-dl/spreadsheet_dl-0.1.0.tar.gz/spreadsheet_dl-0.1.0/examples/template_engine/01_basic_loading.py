#!/usr/bin/env python3
"""
Basic Template Loading Example

Demonstrates how to load templates from various sources including:
- Loading by name from template directory
- Loading from file paths
- Loading from YAML strings
- Listing available templates
"""


def example_basic_template_loading() -> None:
    """
    Demonstrate basic template loading from YAML.

    Shows:
    - Loading templates by name
    - Loading from file path
    - Loading from YAML string
    - Listing available templates
    """
    from spreadsheet_dl.template_engine.loader import TemplateLoader

    print("=" * 70)
    print("Example 1: Basic Template Loading")
    print("=" * 70)

    # 1. Create template loader
    print("\n1. Creating template loader:")
    loader = TemplateLoader()
    print(f"   Template directory: {loader._template_dir}")

    # 2. List available templates
    print("\n2. Listing available templates:")
    templates = loader.list_templates()
    if templates:
        print(f"   Found {len(templates)} templates:")
        for tmpl in templates[:5]:  # Show first 5
            print(f"     • {tmpl['name']} v{tmpl['version']}")
            print(f"       {tmpl['description']}")
    else:
        print("   No templates found (this is a demonstration)")

    # 3. Load template from YAML string
    print("\n3. Loading template from YAML string:")
    yaml_content = """
meta:
  name: Simple Budget
  version: 1.0.0
  description: A simple budget template

variables:
  - name: month
    type: integer
    description: Month number (1-12)
    required: true
  - name: year
    type: integer
    description: Year
    required: true

sheets:
  - name: Budget
    columns:
      - name: Category
        width: 4cm
      - name: Budget
        width: 3cm
        type: currency
      - name: Actual
        width: 3cm
        type: currency

    header:
      cells:
        - value: Category
          style: header
        - value: Budget
          style: header
        - value: Actual
          style: header
"""

    template = loader.load_from_string(yaml_content)
    print(f"   Template loaded: {template.name}")
    print(f"   Version: {template.version}")
    print(f"   Variables: {len(template.variables)}")
    print(f"   Sheets: {len(template.sheets)}")

    print("\n✓ Template loading demonstrated")
    print()


if __name__ == "__main__":
    example_basic_template_loading()
