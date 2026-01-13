# Best Practices Guide

**Implements: DOC-PROF-005: Best Practices Documentation**

This guide covers best practices for creating professional, maintainable
spreadsheets using spreadsheet-dl.

## Table of Contents

1. [Architecture Patterns](#architecture-patterns)
2. [Theme Design](#theme-design)
3. [Style Organization](#style-organization)
4. [Formula Best Practices](#formula-best-practices)
5. [Data Validation](#data-validation)
6. [Conditional Formatting](#conditional-formatting)
7. [Print Layout](#print-layout)
8. [Performance Optimization](#performance-optimization)
9. [Accessibility](#accessibility)
10. [Maintenance](#maintenance)

## Architecture Patterns

### Separation of Concerns

Keep data, presentation, and logic separate:

```
my_project/
    themes/
        corporate.yaml      # Presentation layer
        minimal.yaml
    templates/
        budget.py          # Structure/logic layer
        cash_flow.py
    data/
        budget_data.csv    # Data layer
```

### Use the Builder Pattern

```python
# Good: Fluent builder pattern
builder = (
    SpreadsheetBuilder(theme="corporate")
    .workbook_properties(title="Q1 Budget")
    .sheet("Budget")
    .column("Category", width="150pt")
    .column("Amount", type="currency")
    .header_row(style="header_primary")
    .data_rows(10)
    .total_row(formulas=["Total", "=SUM(B2:B11)"])
)

# Avoid: Direct manipulation
# (prone to errors, hard to maintain)
```

### Template-Based Architecture

Create reusable templates for common documents:

```python
# templates/monthly_report.py
class MonthlyReportTemplate:
    """Reusable monthly report template."""

    def __init__(self, month: str, year: int):
        self.month = month
        self.year = year

    def generate(self) -> SpreadsheetBuilder:
        builder = SpreadsheetBuilder(theme="corporate")
        self._add_header_section(builder)
        self._add_summary_section(builder)
        self._add_detail_section(builder)
        return builder
```

## Theme Design

### Color Palette Guidelines

```yaml
colors:
  # Primary brand colors
  primary: '#1A3A5C' # Main brand color
  secondary: '#4472C4' # Secondary brand color

  # Semantic colors (consistent meaning)
  success: '#70AD47' # Green for positive
  warning: '#FFC000' # Yellow for attention
  danger: '#C00000' # Red for negative/errors

  # Neutral colors
  text: '#333333' # Main text
  text_light: '#666666' # Secondary text
  background: '#FFFFFF' # Main background
  border: '#E0E0E0' # Borders and dividers
```

### Color Contrast for Accessibility

Always ensure sufficient contrast:

```python
from spreadsheet_dl.schema import Color

bg_color = Color("#4472C4")
text_color = Color("#FFFFFF")

# Check WCAG AA compliance (4.5:1 for normal text)
ratio = bg_color.contrast_ratio(text_color)
assert ratio >= 4.5, f"Contrast ratio {ratio} fails WCAG AA"

# Or use the built-in check
assert bg_color.is_wcag_aa(text_color), "Fails WCAG AA"
```

### Limit Color Palette

Use 5-7 main colors maximum:

```yaml
# Good: Limited, purposeful palette
colors:
  primary: "#1A3A5C"
  accent: "#4472C4"
  success: "#70AD47"
  warning: "#FFC000"
  danger: "#C00000"

# Avoid: Too many colors (confusing)
colors:
  blue1: "#0000FF"
  blue2: "#0066FF"
  blue3: "#0099FF"
  # ... endless variations
```

## Style Organization

### Use Semantic Names

```yaml
# Good: Semantic names
styles:
  section_header:     # What it IS
  category_label:     # What it IS
  currency_positive:  # What it MEANS
  input_cell:         # What it DOES

# Avoid: Visual descriptions
styles:
  blue_bold:          # What it LOOKS like
  large_text:         # What it LOOKS like
  red_background:     # What it LOOKS like
```

### Create a Style Hierarchy

```yaml
# Base styles
base_styles:
  default:
    font_family: 'Liberation Sans'
    font_size: '10pt'

# Semantic styles extending base
styles:
  header_primary:
    extends: default
    font_weight: bold
    font_size: '12pt'

  header_secondary:
    extends: header_primary
    font_size: '11pt'

  data:
    extends: default

  data_currency:
    extends: data
    includes: [currency_format]
```

### Use Traits for Composition

```yaml
traits:
  # Format traits
  currency_format:
    text_align: right
    number_format:
      category: currency
      decimal_places: 2

  # State traits
  editable:
    locked: false
    background_color: '#FFFFC0'

  # Emphasis traits
  bold:
    font_weight: bold

styles:
  # Compose multiple traits
  input_currency:
    includes:
      - currency_format
      - editable
```

## Formula Best Practices

### Use Named Ranges

```python
# Define named ranges for clarity
builder.named_range("budget", "B2", "B100")
builder.named_range("actual", "C2", "C100")

# Use in formulas
builder.cell("=SUM(budget)")           # Clear intent
# vs
builder.cell("=SUM(B2:B100)")          # Magic range
```

### Use Structured References

```python
from spreadsheet_dl.builder import formula

# Build formulas with clear structure
variance = (
    formula()
    .ref("Budget", col="B")
    .minus()
    .ref("Actual", col="C")
    .build()
)
```

### Avoid Deep Nesting

```python
# Good: Break down complex formulas
builder.cell("=IF(Budget>0, Actual/Budget, 0)", name="Usage")
builder.cell("=IF(Usage>1, 'Over Budget', 'Within Budget')")

# Avoid: Complex nested formula
builder.cell(
    '=IF(Budget>0, IF(Actual/Budget>1, "Over", "Within"), "N/A")'
)
```

## Data Validation

### Always Validate User Input

```python
from spreadsheet_dl.schema.data_validation import (
    DataValidation,
    InputMessage,
    ErrorAlert,
)

# Category dropdown
category_validation = DataValidation.list(
    items=["Housing", "Utilities", "Food", "Transport"],
    input_message=InputMessage("Category", "Select expense category"),
    error_alert=ErrorAlert.stop("Invalid", "Select from list"),
)

# Positive amount
amount_validation = DataValidation.positive_number(
    allow_zero=True,
    input_message=InputMessage("Amount", "Enter positive amount"),
)
```

### Provide Helpful Messages

```python
# Good: Helpful input message
DataValidation.decimal_between(
    0, 100,
    input_message=InputMessage(
        "Percentage",
        "Enter a percentage between 0 and 100"
    ),
    error_alert=ErrorAlert.stop(
        "Invalid Percentage",
        "Please enter a number between 0 and 100"
    ),
)

# Avoid: No guidance
DataValidation.decimal_between(0, 100)  # User doesn't know constraints
```

## Conditional Formatting

### Use Conditional Formatting Sparingly

```python
# Good: Meaningful highlighting
builder.conditional_format("C2:C100")
    .when_value().less_than(0).style("danger")      # Over budget
    .when_value().less_than(100).style("warning")   # Low remaining
    .build()

# Avoid: Rainbow chaos
# Don't create rules for every possible condition
```

### Prioritize Rules Correctly

Rules are evaluated in priority order (lowest number first):

```python
# High priority rules first
ConditionalFormatBuilder()
    .range("B2:B100")
    .when_formula("=ISBLANK(B2)", "neutral", priority=1)  # First
    .when_value().less_than(0).style("danger", priority=2)  # Then
    .when_value().greater_than(1000).style("highlight", priority=3)
    .build()
```

### Use Color Scales for Gradients

```python
# Good: Heat map for trends
ConditionalFormatBuilder()
    .range("D2:D50")
    .color_scale()
        .min_color("#F8696B")   # Red for low
        .mid_color("#FFEB84")   # Yellow for middle
        .max_color("#63BE7B")   # Green for high
    .build()
```

## Print Layout

### Always Set Print Area

```python
from spreadsheet_dl.schema.print_layout import PageSetup, PrintArea

setup = PageSetup(
    print_area=PrintArea("A1:F50"),  # Define what prints
    repeat=RepeatConfig.header_row(),  # Repeat headers
)
```

### Use Appropriate Page Size

```python
# Landscape for wide tables
PageSetup(
    size=PageSize.A4,
    orientation=PageOrientation.LANDSCAPE,
    scale_mode=PrintScale.FIT_TO_WIDTH,
)

# Portrait for narrative reports
PageSetup(
    size=PageSize.A4,
    orientation=PageOrientation.PORTRAIT,
)
```

### Include Headers and Footers

```python
from spreadsheet_dl.schema.print_layout import (
    HeaderFooter,
    HeaderFooterContent,
)

PageSetup(
    header=HeaderFooter(
        center=HeaderFooterContent("Budget Report", bold=True),
        right=HeaderFooterContent.page_number(),
    ),
    footer=HeaderFooter(
        left=HeaderFooterContent.date_time(),
        right=HeaderFooterContent.file_name(),
    ),
)
```

## Performance Optimization

### Limit Formula Scope

```python
# Good: Specific ranges
builder.cell("=SUM(B2:B100)")

# Avoid: Full column references (slow)
builder.cell("=SUM(B:B)")
```

### Use Efficient Functions

```python
# Good: SUMIF for conditional sums
builder.cell('=SUMIF(A:A,"Housing",B:B)')

# Avoid: Array formulas when possible
builder.cell('=SUM(IF(A2:A100="Housing",B2:B100))')
```

### Minimize Conditional Formatting

```python
# Good: Apply to data range only
builder.conditional_format("B2:B100")  # Just the data

# Avoid: Whole column
builder.conditional_format("B:B")  # Unnecessarily large
```

## Accessibility

### Color Contrast

```python
# Check contrast ratios
bg = Color("#4472C4")
text = Color("#FFFFFF")

# WCAG AA requires 4.5:1 for normal text
if bg.contrast_ratio(text) < 4.5:
    raise ValueError("Insufficient contrast")
```

### Don't Rely on Color Alone

```python
# Good: Color + text indicator
builder.conditional_format("D2:D100")
    .when_value().less_than(0)
    .style("danger")  # Red

# Also add text indicators
builder.cell(
    '=IF(C2<0, "Over Budget", "On Track")',
    conditional_format="status_colors",
)
```

### Use Clear Labels

```python
# Good: Descriptive headers
builder.column("Budget Amount (USD)", type="currency")
builder.column("Actual Spend (USD)", type="currency")
builder.column("Remaining (USD)", type="currency")

# Avoid: Abbreviated/cryptic
builder.column("Bgt")
builder.column("Act")
builder.column("Rem")
```

## Maintenance

### Version Your Themes

```yaml
meta:
  name: 'corporate-theme'
  version: '2.1.0'
  description: 'Corporate financial theme'
  changelog:
    - version: '2.1.0'
      changes: ['Added danger-light color']
    - version: '2.0.0'
      changes: ['Redesigned color palette']
```

### Document Custom Styles

```yaml
styles:
  budget_variance:
    description: |
      Style for budget variance columns.
      Shows negative values in red parentheses.
    extends: currency
    # ...
```

### Keep Templates Updated

```python
class BudgetTemplate:
    """
    Monthly budget template.

    Version: 2.0.0
    Last Updated: 2024-12-28

    Changelog:
    - 2.0.0: Added department breakdown
    - 1.1.0: Added quarterly summaries
    - 1.0.0: Initial version
    """
```

### Use Source Control

```bash
# Track theme and template changes
git add themes/ templates/
git commit -m "feat(themes): add quarterly report theme"
```

## Summary Checklist

### Before Creating a Spreadsheet

- [ ] Define purpose and audience
- [ ] Choose appropriate theme
- [ ] Plan sheet structure
- [ ] Identify data validation needs

### Style Design

- [ ] Use semantic style names
- [ ] Create style hierarchy
- [ ] Ensure color contrast
- [ ] Limit color palette

### Data Quality

- [ ] Validate all user inputs
- [ ] Provide helpful messages
- [ ] Use named ranges
- [ ] Keep formulas simple

### Print Ready

- [ ] Set print area
- [ ] Configure headers/footers
- [ ] Test print preview
- [ ] Repeat headers on pages

### Accessibility

- [ ] Sufficient color contrast
- [ ] Clear labels
- [ ] Don't rely on color alone

## See Also

- [Style Composition Guide](style-composition.md)
- [Theme Creation Guide](theme-creation.md)
- [Builder API Reference](../api/builder.md)
