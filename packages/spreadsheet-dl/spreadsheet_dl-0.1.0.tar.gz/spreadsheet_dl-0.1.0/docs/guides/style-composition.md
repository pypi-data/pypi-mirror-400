# Style Composition Guide

**Implements: DOC-PROF-004: Style Composition Guide**

This guide explains how to compose and inherit styles using the spreadsheet-dl's
style system for professional, consistent spreadsheet formatting.

## Overview

The style composition system provides:

- **Single inheritance**: Styles can extend a parent style
- **Trait composition**: Mix in reusable style traits
- **Color references**: Use theme colors with transformations
- **Cascading properties**: Properties flow from parent to child

## Style Hierarchy

```
Base Style (from theme)
    |
    +-- Extended Style (user-defined)
            |
            +-- Final Style (with traits mixed in)
```

## Defining Styles in YAML

### Basic Style Definition

```yaml
styles:
  my_header:
    font_family: 'Liberation Sans'
    font_size: '12pt'
    font_weight: bold
    font_color: '#FFFFFF'
    background_color: '#1A3A5C'
    text_align: center
    vertical_align: middle
    border_bottom:
      width: '2pt'
      style: solid
      color: '#0F2540'
```

### Style Inheritance with `extends`

```yaml
styles:
  # Base header style
  header_base:
    font_family: 'Liberation Sans'
    font_weight: bold
    text_align: center
    vertical_align: middle

  # Primary header extends base
  header_primary:
    extends: header_base
    font_size: '12pt'
    font_color: '#FFFFFF'
    background_color: '{colors.primary}'

  # Secondary header with different color
  header_secondary:
    extends: header_base
    font_size: '11pt'
    font_color: '{colors.primary}'
    background_color: '{colors.primary|lighten:0.8}'
```

### Traits (Reusable Mixins)

```yaml
traits:
  # Currency formatting trait
  currency_format:
    text_align: right
    number_format:
      category: currency
      symbol: '$'
      decimal_places: 2
      negative_format: parentheses

  # Percentage formatting trait
  percentage_format:
    text_align: right
    number_format:
      category: percentage
      decimal_places: 1

  # Bold text trait
  bold_text:
    font_weight: bold

  # Bordered cell trait
  bordered:
    border_top: '1pt solid #E0E0E0'
    border_bottom: '1pt solid #E0E0E0'
    border_left: '1pt solid #E0E0E0'
    border_right: '1pt solid #E0E0E0'

styles:
  # Compose style from traits
  currency_cell:
    includes:
      - currency_format
      - bordered

  # Extend and include traits
  total_currency:
    extends: currency_cell
    includes:
      - bold_text
    background_color: '#F5F5F5'
    border_top: '2pt solid #4472C4'
```

## Color References

Reference theme colors with transformations:

```yaml
styles:
  example_style:
    # Direct reference
    font_color: '{colors.primary}'

    # Lighten by 20%
    background_color: '{colors.primary|lighten:0.2}'

    # Darken by 30%
    border_color: '{colors.primary|darken:0.3}'

    # Desaturate by 50%
    highlight_color: '{colors.primary|desaturate:0.5}'
```

### Available Transformations

| Transformation | Example                            | Description         |
| -------------- | ---------------------------------- | ------------------- |
| `lighten`      | `{colors.primary\|lighten:0.2}`    | Increase lightness  |
| `darken`       | `{colors.primary\|darken:0.3}`     | Decrease lightness  |
| `saturate`     | `{colors.primary\|saturate:0.2}`   | Increase saturation |
| `desaturate`   | `{colors.primary\|desaturate:0.5}` | Decrease saturation |

## Using StyleBuilder (Programmatic)

```python
from spreadsheet_dl.builders.style import StyleBuilder

# Create a header style
header = (
    StyleBuilder("custom_header")
    .font(family="Arial", size="14pt", weight="bold", color="#FFFFFF")
    .background("#4472C4")
    .align(horizontal="center", vertical="middle")
    .border_bottom("2pt", "solid", "#2F4A82")
    .padding("4pt")
    .build()
)

# Inherit from existing style
child_header = (
    StyleBuilder("child_header")
    .extends(header)
    .font_size("12pt")  # Override just the size
    .build()
)

# Currency formatting
currency = (
    StyleBuilder("amount")
    .align_right()
    .currency(symbol="$", negatives="parentheses")
    .build()
)

# Percentage with conditional coloring
variance = (
    StyleBuilder("variance_pct")
    .align_right()
    .percentage(decimal_places=1)
    .build()
)
```

## Best Practices

### 1. Use a Style Hierarchy

```
base_text
    +-- body_text
    +-- header_text
            +-- header_primary
            +-- header_secondary

base_number
    +-- currency
            +-- currency_positive
            +-- currency_negative
    +-- percentage
```

### 2. Create Semantic Styles

Instead of:

```yaml
blue_bold_12pt:
  font_color: '#0000FF'
  font_weight: bold
  font_size: '12pt'
```

Use:

```yaml
section_header:
  font_color: '{colors.primary}'
  font_weight: bold
  font_size: '12pt'
```

### 3. Use Traits for Cross-Cutting Concerns

```yaml
traits:
  # Input cells - unlocked for editing
  editable:
    locked: false
    background_color: '#FFFFC0'

  # Protected cells
  protected:
    locked: true
    hidden: false

  # High-emphasis text
  emphasis:
    font_weight: bold
    font_color: '{colors.primary}'

styles:
  input_amount:
    includes:
      - editable
      - currency_format

  readonly_amount:
    includes:
      - protected
      - currency_format
```

### 4. Keep Styles DRY

Don't repeat - extract common properties:

```yaml
# Bad: Repetition
header_a:
  font_family: 'Liberation Sans'
  font_size: '12pt'
  font_weight: bold
  background_color: '#4472C4'
  font_color: '#FFFFFF'

header_b:
  font_family: 'Liberation Sans'
  font_size: '12pt'
  font_weight: bold
  background_color: '#ED7D31'
  font_color: '#FFFFFF'

# Good: Base style with extensions
header_base:
  font_family: 'Liberation Sans'
  font_size: '12pt'
  font_weight: bold
  font_color: '#FFFFFF'

header_primary:
  extends: header_base
  background_color: '{colors.primary}'

header_secondary:
  extends: header_base
  background_color: '{colors.secondary}'
```

## Complete Example Theme

```yaml
meta:
  name: 'financial-report'
  version: '1.0.0'
  description: 'Professional financial report theme'

colors:
  primary: '#1A3A5C'
  secondary: '#4472C4'
  accent: '#ED7D31'
  success: '#70AD47'
  warning: '#FFC000'
  danger: '#C00000'
  text: '#333333'
  background: '#FFFFFF'
  border: '#E0E0E0'

traits:
  currency_format:
    text_align: right
    number_format:
      category: currency
      symbol: '$'
      decimal_places: 2
      negative_format: parentheses

  percentage_format:
    text_align: right
    number_format:
      category: percentage
      decimal_places: 1

  input_cell:
    locked: false
    background_color: '#FFFFC0'

  bordered:
    border_top: '1pt solid {colors.border}'
    border_bottom: '1pt solid {colors.border}'
    border_left: '1pt solid {colors.border}'
    border_right: '1pt solid {colors.border}'

base_styles:
  default:
    font_family: 'Liberation Sans'
    font_size: '10pt'
    font_color: '{colors.text}'
    vertical_align: middle
    padding: '2pt'

styles:
  header_primary:
    extends: default
    font_size: '12pt'
    font_weight: bold
    font_color: '#FFFFFF'
    background_color: '{colors.primary}'
    text_align: center
    border_bottom: '2pt solid {colors.primary|darken:0.3}'

  header_secondary:
    extends: default
    font_size: '11pt'
    font_weight: bold
    font_color: '{colors.primary}'
    background_color: '{colors.primary|lighten:0.85}'
    text_align: center

  category:
    extends: default
    font_weight: bold
    background_color: '{colors.primary|lighten:0.9}'

  data:
    extends: default
    includes:
      - bordered

  currency:
    extends: data
    includes:
      - currency_format

  currency_input:
    extends: currency
    includes:
      - input_cell

  percentage:
    extends: data
    includes:
      - percentage_format

  total:
    extends: default
    font_weight: bold
    background_color: '{colors.primary|lighten:0.8}'
    border_top: '2pt solid {colors.primary}'

  success:
    font_color: '{colors.success}'

  warning:
    font_color: '{colors.warning}'
    background_color: '{colors.warning|lighten:0.7}'

  danger:
    font_color: '{colors.danger}'
    background_color: '{colors.danger|lighten:0.8}'
```

## Resolution Order

When resolving a style's final properties:

1. Start with defaults
2. Apply parent style (if `extends`)
3. Apply traits (in order listed in `includes`)
4. Apply style's own properties
5. Resolve color references

Later values override earlier values.

## See Also

- [Theme Creation Guide](./theme-creation.md)
- [Builder API Reference](../api/builder.md)
