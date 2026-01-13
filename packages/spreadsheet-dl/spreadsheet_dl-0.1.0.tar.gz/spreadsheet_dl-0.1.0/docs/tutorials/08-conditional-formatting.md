# Conditional Formatting Tutorial

This tutorial demonstrates how to use conditional formatting in SpreadsheetDL to create visually enhanced spreadsheets with automatic styling based on cell values.

## Overview

SpreadsheetDL provides comprehensive conditional formatting support through the `ConditionalFormat` and `ConditionalRule` classes. Conditional formatting allows you to:

- Highlight cells based on their values (greater than, less than, equal, etc.)
- Apply text-based formatting (contains, begins with, ends with)
- Create color scales for gradient-style visualizations
- Add data bars for visual comparison
- Use icon sets to show trends or ratings

## Important Limitations

**Note:** odfpy does not support ODF `calc:conditional-formats` elements, so SpreadsheetDL uses **static evaluation** at render time:

- Conditions are evaluated when the ODS file is created
- Styles are applied permanently based on current values
- Changes to cell values in LibreOffice won't trigger re-evaluation
- Works perfectly for static data or reports generated from known data

For dynamic conditional formatting, either:

- Use XLSX format (future support)
- Manually add conditional formatting rules in LibreOffice after export

## Basic Cell Value Comparisons

### Less Than Rule

Highlight negative values in red:

```python
from spreadsheet_dl.schema.conditional import (
    ConditionalFormat,
    ConditionalRule,
    RuleOperator,
)

# Highlight cells less than 0
negative_rule = ConditionalRule.cell_value(
    operator=RuleOperator.LESS_THAN,
    value=0,
    style="danger",  # Built-in red style
)

fmt = ConditionalFormat(
    range="D2:D100",
    rules=[negative_rule],
)
```

### Greater Than Rule

Highlight high values in green:

```python
positive_rule = ConditionalRule.cell_value(
    operator=RuleOperator.GREATER_THAN,
    value=100,
    style="success",  # Built-in green style
)

fmt = ConditionalFormat(
    range="E2:E100",
    rules=[positive_rule],
)
```

### Between Rule

Highlight values in a specific range:

```python
normal_range = ConditionalRule.between(
    min_value=50,
    max_value=150,
    style="normal",
)

fmt = ConditionalFormat(
    range="F2:F100",
    rules=[normal_range],
)
```

## Multiple Rules with Priority

Apply multiple rules to the same range, evaluated in priority order:

```python
budget_format = ConditionalFormat(
    range="D2:D100",
    rules=[
        # Priority 1: Over budget (negative) = Red
        ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=0,
            style="danger",
            priority=1,
        ),
        # Priority 2: Low remaining (<100) = Yellow
        ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=100,
            style="warning",
            priority=2,
        ),
        # Priority 3: Healthy (>=100) = Green
        ConditionalRule.cell_value(
            operator=RuleOperator.GREATER_THAN_OR_EQUAL,
            value=100,
            style="success",
            priority=3,
        ),
    ],
)
```

## Text-Based Conditions

### Contains Text

Highlight cells containing specific text:

```python
error_rule = ConditionalRule.contains_text(
    text="Error",
    style="danger",
)

fmt = ConditionalFormat(
    range="A1:A100",
    rules=[error_rule],
)
```

### Begins With

```python
from spreadsheet_dl.schema.conditional import ConditionalRuleType

warning_rule = ConditionalRule(
    type=ConditionalRuleType.TEXT,
    operator=RuleOperator.BEGINS_WITH,
    text="WARN",
    style="warning",
)
```

### Ends With

```python
pdf_rule = ConditionalRule(
    type=ConditionalRuleType.TEXT,
    operator=RuleOperator.ENDS_WITH,
    text=".pdf",
    style="info",
)
```

## Color Scales

Create gradient-style color scales for heat maps and visualizations:

### Three-Color Scale (Red-Yellow-Green)

```python
from spreadsheet_dl.schema.conditional import ColorScale

heat_map = ConditionalFormat(
    range="E2:E100",
    rules=[
        ConditionalRule(
            type=ConditionalRuleType.COLOR_SCALE,
            color_scale=ColorScale.red_yellow_green(),
        ),
    ],
)
```

### Two-Color Scale

```python
from spreadsheet_dl.schema.styles import Color

custom_scale = ConditionalFormat(
    range="F2:F100",
    rules=[
        ConditionalRule(
            type=ConditionalRuleType.COLOR_SCALE,
            color_scale=ColorScale.two_color(
                min_color=Color("#FFFFFF"),  # White
                max_color=Color("#5A8AC6"),  # Blue
            ),
        ),
    ],
)
```

### Custom Three-Color Scale

```python
custom_three = ColorScale.three_color(
    min_color=Color("#F8696B"),  # Red
    mid_color=Color("#FFEB84"),  # Yellow
    max_color=Color("#63BE7B"),  # Green
    mid_value=50,  # Midpoint at 50th percentile
)
```

## Data Bars

Add horizontal bars to cells for visual comparison:

```python
from spreadsheet_dl.schema.conditional import DataBar

expense_bars = ConditionalFormat(
    range="C2:C100",
    rules=[
        ConditionalRule(
            type=ConditionalRuleType.DATA_BAR,
            data_bar=DataBar.default(),  # Blue bars
        ),
    ],
)
```

### Custom Data Bar

```python
variance_bars = ConditionalFormat(
    range="D2:D100",
    rules=[
        ConditionalRule(
            type=ConditionalRuleType.DATA_BAR,
            data_bar=DataBar.budget_variance(),  # Green/red for +/-
        ),
    ],
)
```

### Data Bar with Custom Colors

```python
custom_bar = DataBar(
    fill_color=Color("#4472C4"),
    negative_color=Color("#C00000"),
    show_value=True,
    gradient_fill=True,
    axis_position="midpoint",
)
```

## Icon Sets

Display icons to show trends, ratings, or status:

### Three Arrows

```python
from spreadsheet_dl.schema.conditional import IconSet

trend_icons = ConditionalFormat(
    range="F2:F100",
    rules=[
        ConditionalRule(
            type=ConditionalRuleType.ICON_SET,
            icon_set=IconSet.three_arrows(),
        ),
    ],
)
```

### Traffic Lights

```python
status_icons = ConditionalFormat(
    range="G2:G100",
    rules=[
        ConditionalRule(
            type=ConditionalRuleType.ICON_SET,
            icon_set=IconSet.three_traffic_lights(),
        ),
    ],
)
```

### Five Star Ratings

```python
rating_icons = ConditionalFormat(
    range="H2:H100",
    rules=[
        ConditionalRule(
            type=ConditionalRuleType.ICON_SET,
            icon_set=IconSet.five_ratings(),
        ),
    ],
)
```

## Financial Presets

Pre-configured conditional formats for common financial scenarios:

### Budget Variance

```python
from spreadsheet_dl.schema.conditional import FinancialFormats

budget_fmt = FinancialFormats.budget_variance(
    range_ref="D2:D100",
    danger_style="danger",    # Over budget
    warning_style="warning",   # Near limit
    success_style="success",   # Healthy
)
```

### Percentage Used Scale

```python
pct_fmt = FinancialFormats.percent_used_scale("E2:E100")
# Green at 0%, yellow at 50%, red at 100%
```

### Expense Data Bars

```python
expense_fmt = FinancialFormats.expense_data_bar("C2:C100")
# Blue gradient bars
```

### Positive/Negative Values

```python
variance_fmt = FinancialFormats.positive_negative(
    range_ref="F2:F100",
    positive_style="success",
    negative_style="danger",
)
```

## Complete Example: Budget Tracker

```python
from spreadsheet_dl.schema.conditional import (
    ConditionalFormat,
    ConditionalRule,
    RuleOperator,
    FinancialFormats,
)
from spreadsheet_dl.builder import SheetBuilder

# Create budget sheet
budget = SheetBuilder("Budget 2025")

# Add headers
budget.add_row(["Category", "Budget", "Spent", "Remaining", "% Used"])

# Add data rows
budget.add_row(["Salaries", 50000, 45000, 5000, 0.9])
budget.add_row(["Marketing", 10000, 8500, 1500, 0.85])
budget.add_row(["Equipment", 15000, 12000, 3000, 0.8])
budget.add_row(["Travel", 8000, 9500, -1500, 1.19])  # Over budget

# Apply conditional formatting

# 1. Highlight remaining budget
remaining_fmt = FinancialFormats.budget_variance(
    range_ref="D2:D5",
    danger_style="danger",
    warning_style="warning",
    success_style="success",
)

# 2. Color scale for % used
pct_fmt = FinancialFormats.percent_used_scale("E2:E5")

# 3. Data bars for spent amounts
spent_fmt = FinancialFormats.expense_data_bar("C2:C5")

# Apply formatting (when supported by renderer)
# budget.add_conditional_format(remaining_fmt)
# budget.add_conditional_format(pct_fmt)
# budget.add_conditional_format(spent_fmt)
```

## Custom Cell Styles

Create custom styles for conditional formatting:

```python
from spreadsheet_dl.schema.styles import CellStyle, Color, Font, FontWeight

# Define custom style
critical_style = CellStyle(
    name="critical",
    background_color=Color("#FF0000"),
    font=Font(
        color=Color("#FFFFFF"),
        weight=FontWeight.BOLD,
    ),
)

# Use in rule
critical_rule = ConditionalRule.cell_value(
    operator=RuleOperator.LESS_THAN,
    value=-1000,
    style=critical_style,
)
```

## Builder Pattern

Use the fluent builder API for cleaner syntax:

```python
from spreadsheet_dl.builders.conditional import ConditionalFormatBuilder

budget_fmt = (
    ConditionalFormatBuilder()
    .range("D2:D100")
    .when_value().less_than(0).style("danger")
    .when_value().less_than(100).style("warning")
    .when_value().greater_than_or_equal(100).style("success")
    .build()
)
```

## Best Practices

1. **Priority Matters**: Lower priority numbers are evaluated first. Use `stop_if_true=True` to prevent subsequent rules from applying.

2. **Use Built-in Styles**: "danger", "warning", "success" styles are automatically created with appropriate colors.

3. **Test with Static Data**: Since evaluation is static, test with representative data to ensure formatting works as expected.

4. **Color Scale Tips**:
   - Use green-yellow-red for "good to bad" metrics
   - Use red-yellow-green for "bad to good" metrics (inverted)
   - Two-color scales work well for simple gradients

5. **Data Bar Tips**:
   - Show values for context (default)
   - Hide values for pure visual comparison
   - Use negative colors for variance bars

6. **Icon Set Tips**:
   - Three arrows: Good for trends
   - Traffic lights: Good for status
   - Five stars: Good for ratings

## Troubleshooting

### Formatting Not Applied

- Ensure cell values are present at render time
- Check that the range syntax is correct ("A1:B10")
- Verify style names are valid or built-in

### Wrong Cells Highlighted

- Check operator (LESS_THAN vs LESS_THAN_OR_EQUAL)
- Verify comparison values
- Test with print statements to debug rule evaluation

### Color Scales Look Wrong

- Ensure min/mid/max values match your data range
- Try different value types (MIN, MAX, PERCENTILE, NUMBER)
- Check color definitions are valid hex codes

## Current Limitations

1. **Static Evaluation**: Conditions evaluated at export time only
2. **No Formula Support**: Formula-based rules not supported in static mode
3. **Limited ODF Support**: odfpy doesn't support native ODF conditional formats
4. **No Top/Bottom Rules**: Top N, bottom N rules defined but not evaluated statically

## Additional Resources

- [Conditional Formatting Reference](../api/conditional.md)
- [Builder Pattern Guide](../guides/builders.md)
- [Style System Reference](../api/styles.md)
- [Finance Domain API](../api/domain-plugins.md)

## Example Gallery

See [Example Gallery](../examples/gallery.md) for complete working examples of:

- Budget variance tracking
- Sales performance dashboards
- Project status reports
- Expense analysis sheets
