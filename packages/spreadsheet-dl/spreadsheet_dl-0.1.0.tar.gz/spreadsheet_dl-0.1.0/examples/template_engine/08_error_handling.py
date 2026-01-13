#!/usr/bin/env python3
"""
Error Handling and Validation Example

Demonstrates error handling and validation including:
- Variable validation
- Type checking
- Missing variable handling
- Invalid template handling
"""


def example_error_handling() -> None:
    """
    Demonstrate error handling and validation.

    Shows:
    - Variable validation
    - Type checking
    - Missing variable handling
    - Invalid template handling
    """
    from spreadsheet_dl.template_engine.loader import TemplateLoader
    from spreadsheet_dl.template_engine.renderer import TemplateRenderer

    print("=" * 70)
    print("Example 8: Error Handling and Validation")
    print("=" * 70)

    yaml_content = """
meta:
  name: Validation Demo
  version: 1.0.0

variables:
  - name: required_field
    type: string
    required: true

  - name: month
    type: integer
    validation: "1 <= value <= 12"

  - name: amount
    type: number
    validation: "value >= 0"

sheets:
  - name: Test
    header:
      cells:
        - value: ${required_field}
"""

    loader = TemplateLoader()
    template = loader.load_from_string(yaml_content)
    renderer = TemplateRenderer()

    # 1. Missing required variable
    print("\n1. Testing missing required variable:")
    try:
        result = renderer.render(template, {"month": 5})
        print("   Template rendered (unexpected)")
    except ValueError as e:
        print(f"   ✓ Caught error: {e}")

    # 2. Invalid variable type
    print("\n2. Testing invalid variable type:")
    try:
        result = renderer.render(
            template, {"required_field": "Test", "month": "not a number"}
        )
        print("   Template rendered (type coercion may occur)")
    except ValueError as e:
        print(f"   ✓ Caught error: {e}")

    # 3. Variable with validation
    print("\n3. Testing variable validation:")
    try:
        result = renderer.render(
            template, {"required_field": "Test", "month": 5, "amount": 100}
        )
        print("   ✓ Valid values accepted")
    except ValueError as e:
        print(f"   ✓ Caught validation error: {e}")

    # 4. Invalid YAML
    print("\n4. Testing invalid YAML:")
    invalid_yaml = """
meta:
  name: Invalid
sheets:
  - name: Test
    header:
      cells:
        - invalid syntax here
"""
    try:
        template = loader.load_from_string(invalid_yaml)
        print("   Template loaded (may have defaults)")
    except Exception as e:
        print(f"   ✓ Caught error: {type(e).__name__}")

    # 5. Successful validation
    print("\n5. Testing successful validation:")
    result = renderer.render(
        template, {"required_field": "Success", "month": 12, "amount": 1000}
    )
    print("   ✓ Template rendered successfully")
    print(f"   Sheet: {result.sheets[0].name}")

    print("\n✓ Error handling demonstrated")
    print()


if __name__ == "__main__":
    example_error_handling()
