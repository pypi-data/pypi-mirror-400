#!/usr/bin/env python3
"""
Conditional Rendering Example

Demonstrates conditional content rendering including:
- If/else conditionals
- Comparison operators
- Boolean logic
- Conditional formatting
"""


def example_conditional_rendering() -> None:
    """
    Demonstrate conditional content rendering.

    Shows:
    - If/else conditionals
    - Comparison operators
    - Boolean logic
    - Conditional formatting
    """
    from spreadsheet_dl.template_engine.renderer import (
        ConditionalEvaluator,
        ExpressionEvaluator,
    )
    from spreadsheet_dl.template_engine.schema import ConditionalBlock

    print("=" * 70)
    print("Example 3: Conditional Rendering")
    print("=" * 70)

    # 1. Simple conditionals
    print("\n1. Simple conditional evaluation:")
    variables = {"budget": 5000, "actual": 5500, "month": 12}
    expr_eval = ExpressionEvaluator(variables)
    cond_eval = ConditionalEvaluator(expr_eval)

    conditions = [
        ("actual > budget", "Over budget"),
        ("actual < budget", "Under budget"),
        ("month == 12", "December"),
        ("budget > 0", "Budget exists"),
    ]

    for condition, description in conditions:
        result = cond_eval.evaluate(condition)
        print(f"   '{condition}' → {result} ({description})")

    # 2. Conditional blocks
    print("\n2. Conditional blocks with if/else:")

    # Over budget scenario
    over_budget_block = ConditionalBlock(
        condition="actual > budget",
        content=["⚠️ Over budget!", "Review spending"],
        else_content=["✓ On track", "Good job"],
    )

    selected_content = cond_eval.select_content(over_budget_block)
    print(
        f"   Condition: actual ({variables['actual']}) > budget ({variables['budget']})"
    )
    print(f"   Result: {selected_content}")

    # Under budget scenario
    variables_under = {"budget": 5000, "actual": 4500}
    expr_eval_under = ExpressionEvaluator(variables_under)
    cond_eval_under = ConditionalEvaluator(expr_eval_under)

    selected_content = cond_eval_under.select_content(over_budget_block)
    print(
        f"\n   Condition: actual ({variables_under['actual']}) > budget ({variables_under['budget']})"
    )
    print(f"   Result: {selected_content}")

    # 3. Complex conditionals
    print("\n3. Complex conditional expressions:")
    complex_conditions = [
        "actual > budget and month == 12",
        "actual > 0 and budget > 0",
    ]

    for condition in complex_conditions:
        result = cond_eval.evaluate(condition)
        print(f"   '{condition}' → {result}")

    print("\n✓ Conditional rendering demonstrated")
    print()


if __name__ == "__main__":
    example_conditional_rendering()
