#!/usr/bin/env python3
"""
Built-in Functions Example

Demonstrates built-in template functions including:
- Date/time functions
- String functions
- Math functions
- Formatting functions
"""

from datetime import date


def example_builtin_functions() -> None:
    """
    Demonstrate built-in template functions.

    Shows:
    - Date/time functions
    - String functions
    - Math functions
    - Formatting functions
    """
    from spreadsheet_dl.template_engine.renderer import (
        BUILTIN_FUNCTIONS,
        ExpressionEvaluator,
    )

    print("=" * 70)
    print("Example 6: Built-in Template Functions")
    print("=" * 70)

    print("\n1. Available built-in functions:")
    print(f"   Total functions: {len(BUILTIN_FUNCTIONS)}")
    for func_name in sorted(BUILTIN_FUNCTIONS.keys()):
        print(f"     • {func_name}()")

    # 2. Date functions
    print("\n2. Date/time functions:")
    variables = {"month": 12, "date_obj": date(2025, 12, 25)}
    evaluator = ExpressionEvaluator(variables)

    date_examples = [
        ("Month name: ${month_name(month)}", "month_name(12) → December"),
        ("Month abbrev: ${month_abbrev(month)}", "month_abbrev(12) → Dec"),
    ]

    for template, description in date_examples:
        result = evaluator.evaluate(template)
        print(f"   {description}")
        print(f"     {result}")

    # 3. String functions
    print("\n3. String manipulation functions:")
    variables["text"] = "budget report"
    evaluator = ExpressionEvaluator(variables)

    string_examples = [
        ("${upper(text)}", "BUDGET REPORT"),
        ("${lower(text)}", "budget report"),
        ("${title(text)}", "Budget Report"),
    ]

    for template, _expected in string_examples:
        result = evaluator.evaluate(template)
        print(f"   {template} → {result}")

    # 4. Math functions
    print("\n4. Math functions:")
    variables = {"values": [100, 200, 300, 400, 500], "value": -42.7}
    evaluator = ExpressionEvaluator(variables)

    math_examples = [
        ("Sum: ${sum(values)}", "sum([100,200,300,400,500])"),
        ("Min: ${min(values)}", "min([100,200,300,400,500])"),
        ("Max: ${max(values)}", "max([100,200,300,400,500])"),
        ("Abs: ${abs(value)}", "abs(-42.7)"),
        ("Round: ${round(value)}", "round(-42.7)"),
    ]

    for template, description in math_examples:
        result = evaluator.evaluate(template)
        print(f"   {description}")
        print(f"     {result}")

    # 5. Formatting functions
    print("\n5. Formatting functions:")
    variables = {"amount": 1234.56, "percent": 0.125}
    evaluator = ExpressionEvaluator(variables)

    format_examples = [
        ("${format_currency(amount)}", "$1,234.56"),
        ("${format_currency(amount, '€')}", "€1,234.56"),
        ("${format_percentage(percent)}", "12.5%"),
        ("${format_percentage(percent, 2)}", "12.50%"),
    ]

    for template, _expected in format_examples:
        result = evaluator.evaluate(template)
        print(f"   {template} → {result}")

    print("\n✓ Built-in functions demonstrated")
    print()


if __name__ == "__main__":
    example_builtin_functions()
