# Conditional Formatting Reference

**Implements:** DOC-PROF-006 (Conditional Formatting Reference)

Complete API reference for SpreadsheetDL's conditional formatting system.

## Overview

Conditional formatting allows automatic styling based on cell values. SpreadsheetDL supports:

- **Cell Value Rules**: Compare values (greater than, less than, equal, etc.)
- **Text Rules**: Match text (contains, begins with, ends with)
- **Color Scales**: Gradient coloring based on value ranges
- **Data Bars**: Visual bar representation of values
- **Icon Sets**: Symbols indicating value categories

## Important Note

Due to odfpy limitations, SpreadsheetDL uses **static evaluation** at render time:

- Conditions are evaluated when the ODS file is created
- Styles are applied permanently based on current values
- Changes in LibreOffice will not trigger re-evaluation

For dynamic conditional formatting, use XLSX format (future support) or add rules manually in LibreOffice after export.

## Core Classes

### ConditionalFormat

Container for conditional formatting rules applied to a range.

```python
from spreadsheet_dl.schema.conditional import ConditionalFormat, ConditionalRule

fmt = ConditionalFormat(
    range="B2:B100",           # Target range
    rules=[rule1, rule2],       # List of rules
    stop_if_true=False,         # Stop processing on first match
)
```

**Parameters:**

| Parameter      | Type                    | Description                                  |
| -------------- | ----------------------- | -------------------------------------------- |
| `range`        | `str`                   | Cell range (e.g., "A1:D50")                  |
| `rules`        | `list[ConditionalRule]` | Rules to apply (processed in order)          |
| `stop_if_true` | `bool`                  | Stop on first matching rule (default: False) |

### ConditionalRule

Individual formatting rule with condition and style.

```python
rule = ConditionalRule(
    type="cell_value",
    operator="greater_than",
    value=0,
    style="positive",
)
```

**Parameters:**

| Parameter  | Type   | Description                            |
| ---------- | ------ | -------------------------------------- |
| `type`     | `str`  | Rule type (see Rule Types)             |
| `operator` | `str`  | Comparison operator (see Operators)    |
| `value`    | `Any`  | Comparison value(s)                    |
| `value2`   | `Any`  | Second value (for between/not_between) |
| `style`    | `str`  | Style name to apply                    |
| `format`   | `dict` | Inline style properties                |

## Rule Types

### Cell Value Rules

Compare cell values against thresholds.

```python
# Greater than
rule = ConditionalRule.cell_value(
    operator=RuleOperator.GREATER_THAN,
    value=1000,
    style="high_value",
)

# Between two values
rule = ConditionalRule.cell_value(
    operator=RuleOperator.BETWEEN,
    value=100,
    value2=500,
    style="medium_value",
)
```

**Operators:**

| Operator                | Description              | Values Required |
| ----------------------- | ------------------------ | --------------- |
| `GREATER_THAN`          | > value                  | 1               |
| `GREATER_THAN_OR_EQUAL` | >= value                 | 1               |
| `LESS_THAN`             | < value                  | 1               |
| `LESS_THAN_OR_EQUAL`    | <= value                 | 1               |
| `EQUAL`                 | == value                 | 1               |
| `NOT_EQUAL`             | != value                 | 1               |
| `BETWEEN`               | value1 <= x <= value2    | 2               |
| `NOT_BETWEEN`           | x < value1 or x > value2 | 2               |

### Text Rules

Match text content in cells.

```python
# Contains text
rule = ConditionalRule.text(
    operator=TextOperator.CONTAINS,
    value="error",
    style="error_text",
)

# Begins with
rule = ConditionalRule.text(
    operator=TextOperator.BEGINS_WITH,
    value="WARN:",
    style="warning_text",
)
```

**Operators:**

| Operator       | Description                |
| -------------- | -------------------------- |
| `CONTAINS`     | Cell contains text         |
| `NOT_CONTAINS` | Cell does not contain text |
| `BEGINS_WITH`  | Cell starts with text      |
| `ENDS_WITH`    | Cell ends with text        |
| `IS_BLANK`     | Cell is empty              |
| `IS_NOT_BLANK` | Cell has content           |

### Color Scales

Apply gradient coloring based on value range.

```python
# Two-color scale (red to green)
rule = ConditionalRule.color_scale(
    min_color="#FF0000",    # Red for minimum
    max_color="#00FF00",    # Green for maximum
    min_type="min",         # Use actual minimum
    max_type="max",         # Use actual maximum
)

# Three-color scale (red-yellow-green)
rule = ConditionalRule.color_scale(
    min_color="#FF0000",
    mid_color="#FFFF00",
    max_color="#00FF00",
    min_type="min",
    mid_type="percentile",
    mid_value=50,
    max_type="max",
)
```

**Value Types:**

| Type         | Description                 |
| ------------ | --------------------------- |
| `min`        | Actual minimum in range     |
| `max`        | Actual maximum in range     |
| `number`     | Specific numeric value      |
| `percent`    | Percentage of range (0-100) |
| `percentile` | Percentile value (0-100)    |

### Data Bars

Visual bars representing cell values.

```python
rule = ConditionalRule.data_bar(
    color="#4472C4",        # Bar color
    min_type="min",
    max_type="max",
    show_value=True,        # Show value alongside bar
    gradient_fill=True,     # Gradient vs solid fill
)
```

**Parameters:**

| Parameter           | Type   | Description                         |
| ------------------- | ------ | ----------------------------------- |
| `color`             | `str`  | Bar color (hex)                     |
| `min_type`          | `str`  | Minimum value type                  |
| `max_type`          | `str`  | Maximum value type                  |
| `min_value`         | `Any`  | Minimum value (if type is "number") |
| `max_value`         | `Any`  | Maximum value (if type is "number") |
| `show_value`        | `bool` | Display value text (default: True)  |
| `gradient_fill`     | `bool` | Gradient fill (default: True)       |
| `negative_color`    | `str`  | Color for negative values           |
| `negative_bar_same` | `bool` | Same direction for negatives        |

### Icon Sets

Display icons based on value thresholds.

```python
rule = ConditionalRule.icon_set(
    icon_style="3_arrows",
    reverse_order=False,
    show_value=True,
    thresholds=[
        {"type": "percent", "value": 33},
        {"type": "percent", "value": 67},
    ],
)
```

**Icon Styles:**

| Style              | Icons                  | Thresholds |
| ------------------ | ---------------------- | ---------- |
| `3_arrows`         | Up/Right/Down arrows   | 2          |
| `3_arrows_gray`    | Gray arrows            | 2          |
| `3_flags`          | Green/Yellow/Red flags | 2          |
| `3_traffic_lights` | Traffic light colors   | 2          |
| `3_symbols`        | Check/Alert/X          | 2          |
| `4_arrows`         | 4 directional arrows   | 3          |
| `4_ratings`        | Rating bars            | 3          |
| `5_arrows`         | 5 directional arrows   | 4          |
| `5_ratings`        | Rating bars            | 4          |

## Rule Factory Methods

### Cell Value Factory

```python
from spreadsheet_dl.schema.conditional import ConditionalRule, RuleOperator

# Highlight negatives
negative_rule = ConditionalRule.cell_value(
    operator=RuleOperator.LESS_THAN,
    value=0,
    style="danger",
)

# Highlight positives
positive_rule = ConditionalRule.cell_value(
    operator=RuleOperator.GREATER_THAN,
    value=0,
    style="success",
)

# Highlight specific value
zero_rule = ConditionalRule.cell_value(
    operator=RuleOperator.EQUAL,
    value=0,
    style="neutral",
)

# Between range
range_rule = ConditionalRule.cell_value(
    operator=RuleOperator.BETWEEN,
    value=-100,
    value2=100,
    style="normal",
)
```

### Text Factory

```python
from spreadsheet_dl.schema.conditional import ConditionalRule, TextOperator

# Error messages
error_rule = ConditionalRule.text(
    operator=TextOperator.CONTAINS,
    value="ERROR",
    style="error_cell",
)

# Warning prefix
warning_rule = ConditionalRule.text(
    operator=TextOperator.BEGINS_WITH,
    value="WARN:",
    style="warning_cell",
)

# Empty cells
blank_rule = ConditionalRule.text(
    operator=TextOperator.IS_BLANK,
    style="empty_cell",
)
```

## Complete Examples

### Budget Variance Highlighting

```python
from spreadsheet_dl.schema.conditional import (
    ConditionalFormat,
    ConditionalRule,
    RuleOperator,
)
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="professional")

# Define conditional format for variance column
variance_format = ConditionalFormat(
    range="D2:D100",
    rules=[
        # Negative variance (over budget) - red
        ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=0,
            style="danger",
        ),
        # Small positive variance - yellow
        ConditionalRule.cell_value(
            operator=RuleOperator.BETWEEN,
            value=0,
            value2=100,
            style="warning",
        ),
        # Large positive variance (under budget) - green
        ConditionalRule.cell_value(
            operator=RuleOperator.GREATER_THAN,
            value=100,
            style="success",
        ),
    ],
)

builder.sheet("Budget") \
    .column("Category", width="150pt") \
    .column("Budget", width="100pt", type="currency") \
    .column("Actual", width="100pt", type="currency") \
    .column("Variance", width="100pt", type="currency") \
    .conditional_format(variance_format) \
    .header_row() \
    .row().cells("Marketing", 10000, 9500, 500) \
    .row().cells("Salaries", 50000, 52000, -2000) \
    .row().cells("IT", 8000, 7950, 50)
```

### Sales Performance with Color Scale

```python
# Color scale: Red (low) to Green (high)
performance_format = ConditionalFormat(
    range="B2:B50",
    rules=[
        ConditionalRule.color_scale(
            min_color="#F8696B",    # Red
            mid_color="#FFEB84",    # Yellow
            max_color="#63BE7B",    # Green
            min_type="min",
            mid_type="percentile",
            mid_value=50,
            max_type="max",
        ),
    ],
)
```

### Progress Bars

```python
# Data bars for completion percentage
progress_format = ConditionalFormat(
    range="C2:C20",
    rules=[
        ConditionalRule.data_bar(
            color="#4472C4",
            min_type="number",
            min_value=0,
            max_type="number",
            max_value=100,
            show_value=True,
        ),
    ],
)
```

### Status Icons

```python
# Traffic light icons for status
status_format = ConditionalFormat(
    range="E2:E50",
    rules=[
        ConditionalRule.icon_set(
            icon_style="3_traffic_lights",
            thresholds=[
                {"type": "number", "value": 50},   # Red < 50
                {"type": "number", "value": 80},   # Yellow < 80
                                                    # Green >= 80
            ],
        ),
    ],
)
```

## Inline Styles

Apply styles inline without pre-defined style names:

```python
rule = ConditionalRule.cell_value(
    operator=RuleOperator.LESS_THAN,
    value=0,
    format={
        "font_color": "#FF0000",
        "font_weight": "bold",
        "background_color": "#FFEEEE",
    },
)
```

## Applying to Builder

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder()

builder.sheet("Data") \
    .column("Value") \
    .conditional_format(variance_format) \
    .conditional_format(status_format) \
    .header_row() \
    # ... add data
```

## Best Practices

### 1. Order Rules by Priority

Rules are evaluated in order; place most specific first:

```python
rules=[
    # Most specific first
    ConditionalRule.cell_value(RuleOperator.EQUAL, 0, style="zero"),
    ConditionalRule.cell_value(RuleOperator.LESS_THAN, 0, style="negative"),
    ConditionalRule.cell_value(RuleOperator.GREATER_THAN, 0, style="positive"),
]
```

### 2. Use Consistent Color Schemes

Follow established conventions:

- **Red**: Negative, danger, errors
- **Yellow/Orange**: Warnings, caution
- **Green**: Positive, success, on-track
- **Blue**: Neutral, informational

### 3. Limit Number of Rules

Too many rules can be confusing:

- Use 3-5 rules maximum per range
- Consider color scales for continuous data
- Use icon sets for quick visual scanning

### 4. Test Edge Cases

Verify behavior for:

- Zero values
- Empty cells
- Extreme values
- Text in numeric columns

## See Also

- [Conditional Formatting Tutorial](../tutorials/08-conditional-formatting.md) - Step-by-step guide
- [Style System](./styles.md) - Style definitions
- [Builder API](./builder.md) - Using with SpreadsheetBuilder
- [Theme System](../guides/theme-creation.md) - Defining styles in themes
