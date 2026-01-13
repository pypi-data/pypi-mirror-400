#!/usr/bin/env python3
"""
Variable Substitution Example

Demonstrates variable substitution capabilities including:
- Simple variable substitution
- Nested variable access
- Function calls in templates
- Filter expressions
- Arithmetic expressions
"""


def example_variable_substitution() -> None:
    """
    Demonstrate variable substitution in templates.

    Shows:
    - Simple variable substitution
    - Nested variable access
    - Function calls in templates
    - Filter expressions
    - Arithmetic expressions
    """
    from spreadsheet_dl.template_engine.renderer import ExpressionEvaluator

    print("=" * 70)
    print("Example 2: Variable Substitution")
    print("=" * 70)

    # Create evaluator with variables
    variables = {
        "month": 12,
        "year": 2025,
        "budget": 5000,
        "actual": 4250,
        "categories": ["Housing", "Food", "Transport"],
        "config": {"currency": "$", "locale": "en_US"},
    }

    evaluator = ExpressionEvaluator(variables)

    # 1. Simple variable substitution
    print("\n1. Simple variable substitution:")
    examples = [
        ("Budget for month ${month}", variables),
        ("Year: ${year}", variables),
        ("Total budget: ${budget}", variables),
    ]

    for template, _ in examples:
        result = evaluator.evaluate(template)
        print(f"   '{template}' → '{result}'")

    # 2. Nested variable access
    print("\n2. Nested variable access:")
    nested_examples = [
        "Currency: ${config.currency}",
        "Locale: ${config.locale}",
    ]

    for template in nested_examples:
        result = evaluator.evaluate(template)
        print(f"   '{template}' → '{result}'")

    # 3. Function calls
    print("\n3. Built-in function calls:")
    function_examples = [
        "Month name: ${month_name(month)}",
        "Month abbrev: ${month_abbrev(month)}",
        "Budget formatted: ${format_currency(budget)}",
        "Uppercase: ${upper('budget')}",
    ]

    for template in function_examples:
        result = evaluator.evaluate(template)
        print(f"   '{template}' → '{result}'")

    # 4. Filters
    print("\n4. Filter expressions:")
    filter_examples = [
        ("Title case: ${'budget report'|title}", "'budget report'|title"),
        ("Default value: ${missing|default:N/A}", "missing|default:N/A"),
        ("Currency: ${budget|currency:$}", "budget|currency:$"),
        ("Round: ${4250.753|round:2}", "4250.753|round:2"),
    ]

    for desc, template in filter_examples:
        result = evaluator.evaluate(template)
        print(f"   {desc}")
        print(f"     '{template}' → '{result}'")

    # 5. Arithmetic expressions
    print("\n5. Arithmetic expressions:")
    arithmetic_examples = [
        "Remaining: ${budget - actual}",
        "Percent used: ${actual * 100 / budget}",
    ]

    for template in arithmetic_examples:
        result = evaluator.evaluate(template)
        print(f"   '{template}' → '{result}'")

    print("\n✓ Variable substitution demonstrated")
    print()


if __name__ == "__main__":
    example_variable_substitution()
