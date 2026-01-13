# Style System Reference

**Implements:** DOC-PROF-005 (Style System Reference)

Complete reference for SpreadsheetDL's style system including cell styles, number formats, borders, and fonts.

## Overview

The style system provides:

- **Named Styles**: Reusable style definitions
- **Theme Styles**: Built-in styles from themes
- **Number Formats**: Currency, percentage, date, custom
- **Borders**: Cell borders with width, style, color
- **Fonts**: Family, size, weight, color
- **Backgrounds**: Solid colors and gradients
- **Alignment**: Horizontal, vertical, text wrapping

## Style Application

### In Builder API

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(theme="professional")

# Apply style to column
builder.column("Revenue", style="currency_positive")

# Apply style to row
builder.row(style="data_highlight")

# Apply style to cell
builder.cell(value=1500, style="total")
```

### Style Priority (Cascade)

1. **Cell style** (highest priority)
2. **Row style**
3. **Column style**
4. **Theme default** (lowest priority)

## Built-in Styles

### Header Styles

| Style Name         | Description                   |
| ------------------ | ----------------------------- |
| `header`           | Default header style          |
| `header_primary`   | Primary header (theme color)  |
| `header_secondary` | Secondary header (lighter)    |
| `header_dark`      | Dark header (dark background) |

### Data Styles

| Style Name       | Description                   |
| ---------------- | ----------------------------- |
| `data`           | Default data cell             |
| `data_highlight` | Highlighted data row          |
| `row_even`       | Even row (for zebra striping) |
| `row_odd`        | Odd row (for zebra striping)  |

### Total/Summary Styles

| Style Name    | Description                 |
| ------------- | --------------------------- |
| `total`       | Total row style             |
| `subtotal`    | Subtotal row style          |
| `grand_total` | Grand total (bold, borders) |

### Status Styles

| Style Name | Description           |
| ---------- | --------------------- |
| `success`  | Green background/text |
| `warning`  | Yellow/orange styling |
| `danger`   | Red background/text   |
| `info`     | Blue styling          |

### Currency Styles

| Style Name          | Description               |
| ------------------- | ------------------------- |
| `currency`          | Basic currency format     |
| `currency_positive` | Green for positive values |
| `currency_negative` | Red for negative values   |

## Number Formats

### Currency Format

```python
# In style definition
number_format:
  category: currency
  symbol: "$"
  decimal_places: 2
  negative_format: parentheses  # or "minus"
  thousands_separator: true
```

**Negative Formats:**

- `minus`: -$1,234.56
- `parentheses`: ($1,234.56)
- `red`: $1,234.56 (in red)
- `red_parentheses`: ($1,234.56) (in red)

### Percentage Format

```python
number_format:
  category: percentage
  decimal_places: 1
```

Renders as: `12.5%`

### Date Formats

```python
number_format:
  category: date
  pattern: "YYYY-MM-DD"  # ISO format
```

**Common Patterns:**

- `YYYY-MM-DD`: 2024-12-31
- `MM/DD/YYYY`: 12/31/2024
- `DD MMM YYYY`: 31 Dec 2024
- `MMMM D, YYYY`: December 31, 2024

### Custom Number Format

```python
number_format:
  category: custom
  pattern: "#,##0.00"
```

**Pattern Characters:**

- `#`: Digit, optional
- `0`: Digit, always shown
- `.`: Decimal separator
- `,`: Thousands separator
- `%`: Multiply by 100, add %

## Font Properties

### Font Definition

```yaml
font:
  family: 'Liberation Sans'
  size: '12pt'
  weight: bold # normal, bold
  style: italic # normal, italic
  color: '#333333'
  underline: single # none, single, double
  strikethrough: false
```

### Font Families

Recommended families for cross-platform compatibility:

- `Liberation Sans` (sans-serif, default)
- `Liberation Serif` (serif)
- `Liberation Mono` (monospace)
- `DejaVu Sans`
- `DejaVu Serif`
- `DejaVu Sans Mono`

### Font Sizes

Specify with units:

- `12pt` - Points (recommended)
- `16px` - Pixels
- `1em` - Relative to parent

## Border Properties

### Border Definition

```yaml
border:
  top:
    width: '1pt'
    style: solid
    color: '#E0E0E0'
  bottom:
    width: '2pt'
    style: solid
    color: '#000000'
  left:
    width: '1pt'
    style: dashed
    color: '#CCCCCC'
  right:
    width: '1pt'
    style: dotted
    color: '#CCCCCC'
```

### Border Styles

- `solid`: Continuous line
- `dashed`: Dashed line
- `dotted`: Dotted line
- `double`: Double line
- `none`: No border

### Shorthand Border

```yaml
# All borders same
border: '1pt solid #E0E0E0'

# Individual borders
border_top: '2pt solid #000'
border_bottom: '1pt solid #CCC'
```

## Background Properties

### Solid Color

```yaml
background_color: '#F5F5F5'
```

### Color References

Reference theme colors with transformations:

```yaml
background_color: "{colors.primary}"              # Theme primary
background_color: "{colors.primary|lighten:0.2}"  # 20% lighter
background_color: "{colors.primary|darken:0.1}"   # 10% darker
background_color: "{colors.primary|alpha:0.5}"    # 50% transparent
```

## Alignment Properties

### Text Alignment

```yaml
text_align: left # left, center, right, justify
vertical_align: middle # top, middle, bottom
```

### Text Wrapping

```yaml
text_wrap: true # Wrap long text
shrink_to_fit: false # Shrink font to fit
```

### Text Rotation

```yaml
text_rotation: 45 # Degrees (0-360)
```

## Style Inheritance

### Using `extends`

```yaml
styles:
  base_header:
    font_weight: bold
    text_align: center
    vertical_align: middle

  header_primary:
    extends: base_header
    font_size: '12pt'
    background_color: '{colors.primary}'
    font_color: '#FFFFFF'

  header_secondary:
    extends: base_header
    font_size: '11pt'
    background_color: '{colors.primary|lighten:0.6}'
    font_color: '{colors.primary}'
```

### Using Traits

Traits are reusable style fragments:

```yaml
traits:
  currency_format:
    text_align: right
    number_format:
      category: currency
      symbol: '$'
      decimal_places: 2

  bold_text:
    font_weight: bold

styles:
  total_amount:
    traits:
      - currency_format
      - bold_text
    background_color: '#F0F0F0'
```

## Complete Style Example

```yaml
# Custom theme with full style definitions
name: 'corporate'
version: '1.0.0'

colors:
  primary: '#1A3A5C'
  secondary: '#6B8BA4'
  accent: '#E67E22'
  success: '#27AE60'
  warning: '#F39C12'
  danger: '#E74C3C'

traits:
  currency:
    text_align: right
    number_format:
      category: currency
      symbol: '$'
      decimal_places: 2
      negative_format: parentheses

  percentage:
    text_align: right
    number_format:
      category: percentage
      decimal_places: 1

styles:
  header_primary:
    font_family: 'Liberation Sans'
    font_size: '12pt'
    font_weight: bold
    font_color: '#FFFFFF'
    background_color: '{colors.primary}'
    text_align: center
    vertical_align: middle
    border_bottom:
      width: '2pt'
      style: solid
      color: '{colors.primary|darken:0.2}'

  data:
    font_family: 'Liberation Sans'
    font_size: '10pt'
    font_color: '#333333'
    vertical_align: middle
    border_bottom: '1pt solid #E0E0E0'

  currency_positive:
    extends: data
    traits:
      - currency
    font_color: '{colors.success}'

  currency_negative:
    extends: data
    traits:
      - currency
    font_color: '{colors.danger}'

  total:
    extends: data
    font_weight: bold
    background_color: '#F5F5F5'
    border_top:
      width: '2pt'
      style: solid
      color: '{colors.primary}'
```

## Programmatic Style Creation

### Using Python

```python
from spreadsheet_dl.schema import CellStyle, NumberFormat, Border, Font

# Create style programmatically
style = CellStyle(
    name="custom_currency",
    font=Font(
        family="Liberation Sans",
        size="11pt",
        weight="bold",
        color="#27AE60",
    ),
    number_format=NumberFormat(
        category="currency",
        symbol="$",
        decimal_places=2,
    ),
    text_align="right",
    background_color="#F0FFF0",
    border_bottom=Border(
        width="1pt",
        style="solid",
        color="#27AE60",
    ),
)

# Register with builder
builder.register_style(style)
builder.cell(value=1500.00, style="custom_currency")
```

## See Also

- [Style Composition Guide](../guides/style-composition.md) - Advanced composition
- [Theme Creation Guide](../guides/theme-creation.md) - Creating themes
- [Conditional Formatting](./conditional.md) - Dynamic styling
- [Builder API](./builder.md) - Using styles in builder
