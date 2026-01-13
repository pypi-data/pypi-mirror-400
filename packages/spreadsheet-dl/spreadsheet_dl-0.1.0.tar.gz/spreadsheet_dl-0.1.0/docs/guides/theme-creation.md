# Theme Creation Guide

A comprehensive guide to creating custom themes for SpreadsheetDL spreadsheets.

**Implements:** DOC-PROF-002 (Theme Creation Guide)

## Overview

Themes provide a consistent visual identity across all your spreadsheets. A theme defines:

- **Color Palettes**: Primary, secondary, accent, and semantic colors
- **Typography**: Font families, sizes, and pairings
- **Cell Styles**: Pre-defined styles for headers, data, totals, etc.
- **Number Formats**: Currency, percentage, date formats

## Theme Structure

Themes are defined in YAML files with the following structure:

```yaml
name: corporate
version: '1.0'
description: 'Professional corporate theme'

# Optional: inherit from another theme
extends: default

colors:
  palette:
    primary: '#1A3A5C'
    secondary: '#4472C4'
    accent: '#ED7D31'
    success: '#70AD47'
    warning: '#FFC000'
    danger: '#C00000'

  semantic:
    header_bg: '{colors.primary}'
    header_fg: '#FFFFFF'
    alternate_row: '#F5F9FC'
    border: '#DEE2E6'

fonts:
  primary:
    family: 'Liberation Sans'
    fallback: ['Arial', 'Helvetica', 'sans-serif']

  heading:
    family: 'Liberation Sans'
    weight: bold

  monospace:
    family: 'Liberation Mono'
    fallback: ['Consolas', 'monospace']

typography:
  base_size: '11pt'
  scale: 'minor_third' # 1.2 ratio

  headings:
    h1: { size: '18pt', weight: bold, color: '{colors.primary}' }
    h2: { size: '14pt', weight: bold }
    h3: { size: '12pt', weight: bold }

styles:
  header:
    font: { family: '{fonts.heading.family}', weight: bold, color: '#FFFFFF' }
    fill: { color: '{colors.primary}' }
    alignment: { horizontal: center, vertical: middle }
    border: { bottom: { style: medium, color: '{colors.primary}' } }

  data:
    font: { family: '{fonts.primary.family}', size: '11pt' }
    alignment: { vertical: middle }

  currency:
    extends: data
    number_format: '$#,##0.00'
    alignment: { horizontal: right }

  total:
    extends: data
    font: { weight: bold }
    fill: { color: '#E8F4FD' }
    border: { top: { style: thin, color: '{colors.border}' } }

formats:
  currency: '$#,##0.00'
  percentage: '0.00%'
  date: 'YYYY-MM-DD'
  date_time: 'YYYY-MM-DD HH:MM'
```

## Color Palette Design

### Primary Colors

Your primary color should represent your brand and be used for:

- Headers and titles
- Primary action buttons
- Key visual elements

```yaml
colors:
  palette:
    primary: '#1A3A5C' # Dark blue - main brand color
    primary_light: '#2D5A87' # Lighter variant
    primary_dark: '#0D1F30' # Darker variant
```

### Secondary and Accent Colors

Secondary colors complement the primary:

```yaml
colors:
  palette:
    secondary: '#4472C4' # Used for charts, links
    accent: '#ED7D31' # Highlights, call-to-action
```

### Semantic Colors

Use semantic colors for meaning:

```yaml
colors:
  semantic:
    success: '#70AD47' # Positive values, growth
    warning: '#FFC000' # Caution, attention needed
    danger: '#C00000' # Negative values, errors
    info: '#5B9BD5' # Informational content
```

### Contrast and Accessibility

Ensure sufficient contrast for readability:

```python
from spreadsheet_dl.schema.styles import Color

# Check contrast ratio
primary = Color("#1A3A5C")
white = Color("#FFFFFF")

ratio = primary.contrast_ratio(white)
print(f"Contrast ratio: {ratio:.2f}")  # Should be >= 4.5 for AA

# WCAG compliance check
if primary.is_wcag_aa(white):
    print("Passes WCAG AA")
if primary.is_wcag_aaa(white):
    print("Passes WCAG AAA")
```

## Font Configuration

### Font Pairing

Choose fonts that work well together:

```yaml
fonts:
  # Primary: Clean sans-serif for data
  primary:
    family: 'Liberation Sans'
    fallback: ['Arial', 'Helvetica', 'sans-serif']

  # Heading: Same family, bolder weight for hierarchy
  heading:
    family: 'Liberation Sans'
    weight: bold

  # Code: Monospace for formulas, IDs
  monospace:
    family: 'Liberation Mono'
    fallback: ['Consolas', 'Courier New', 'monospace']
```

### Pre-built Font Pairings

Use the built-in font pairings:

```python
from spreadsheet_dl.schema.typography import get_font_pairing

# Professional (Liberation Sans + Serif)
professional = get_font_pairing("professional")

# Modern (Open Sans + Roboto Mono)
modern = get_font_pairing("modern")

# Traditional (Times-like)
traditional = get_font_pairing("traditional")

# Minimal (System fonts)
minimal = get_font_pairing("minimal")
```

## Typography Hierarchy

### Type Scale

Choose a ratio for consistent sizing:

| Scale            | Ratio | Description           |
| ---------------- | ----- | --------------------- |
| `minor_second`   | 1.067 | Subtle variation      |
| `major_second`   | 1.125 | Conservative          |
| `minor_third`    | 1.200 | **Recommended**       |
| `major_third`    | 1.250 | More dramatic         |
| `perfect_fourth` | 1.333 | Strong hierarchy      |
| `golden_ratio`   | 1.618 | Classical proportions |

```yaml
typography:
  base_size: '11pt'
  scale: 'minor_third'

  # Generated sizes (base * ratio^n):
  # xs:   7.6pt  (base * 1.2^-2)
  # sm:   9.2pt  (base * 1.2^-1)
  # base: 11pt   (base * 1.2^0)
  # lg:   13.2pt (base * 1.2^1)
  # xl:   15.8pt (base * 1.2^2)
  # 2xl:  19pt   (base * 1.2^3)
  # 3xl:  22.8pt (base * 1.2^4)
```

### Heading Styles

Define heading levels for document structure:

```yaml
typography:
  headings:
    h1:
      size: '18pt'
      weight: bold
      color: '{colors.primary}'
      spacing_after: '12pt'

    h2:
      size: '14pt'
      weight: bold
      color: '{colors.primary}'
      spacing_after: '8pt'

    h3:
      size: '12pt'
      weight: bold
      spacing_after: '6pt'
```

## Style Definitions

### Basic Style Structure

```yaml
styles:
  style_name:
    font:
      family: 'Font Name'
      size: '11pt'
      weight: normal | bold
      italic: false
      color: '#000000'

    fill:
      color: '#FFFFFF'

    alignment:
      horizontal: left | center | right
      vertical: top | middle | bottom
      wrap_text: false

    border:
      top: { style: thin, color: '#000000' }
      bottom: { style: thin, color: '#000000' }
      left: { style: thin, color: '#000000' }
      right: { style: thin, color: '#000000' }

    number_format: 'General'
```

### Style Inheritance

Extend existing styles to reduce duplication:

```yaml
styles:
  # Base data style
  data:
    font: { family: '{fonts.primary.family}', size: '11pt' }
    alignment: { vertical: middle }

  # Currency extends data
  currency:
    extends: data
    number_format: '$#,##0.00'
    alignment: { horizontal: right }

  # Negative currency - different color
  currency_negative:
    extends: currency
    font: { color: '{colors.danger}' }
```

### Common Style Patterns

#### Header Styles

```yaml
styles:
  header_primary:
    font:
      family: '{fonts.heading.family}'
      size: '12pt'
      weight: bold
      color: '#FFFFFF'
    fill:
      color: '{colors.primary}'
    alignment:
      horizontal: center
      vertical: middle
    border:
      bottom: { style: medium, color: '{colors.primary_dark}' }

  header_secondary:
    extends: header_primary
    fill:
      color: '{colors.secondary}'
```

#### Alternating Rows

```yaml
styles:
  row_even:
    fill:
      color: '#FFFFFF'

  row_odd:
    fill:
      color: '{colors.alternate_row}'
```

#### Total Rows

```yaml
styles:
  total:
    font:
      weight: bold
    fill:
      color: '#E8F4FD'
    border:
      top: { style: double, color: '{colors.primary}' }
```

#### Conditional Styles

```yaml
styles:
  positive_value:
    font:
      color: '{colors.success}'

  negative_value:
    font:
      color: '{colors.danger}'

  warning_value:
    fill:
      color: '{colors.warning}'
    font:
      color: '#000000'
```

## Number Formats

### Common Formats

```yaml
formats:
  # Currency
  currency: '$#,##0.00'
  currency_no_cents: '$#,##0'
  currency_negative_red: '$#,##0.00;[Red]-$#,##0.00'

  # Percentage
  percentage: '0%'
  percentage_decimal: '0.00%'

  # Numbers
  number: '#,##0'
  number_decimal: '#,##0.00'

  # Dates
  date_short: 'MM/DD/YYYY'
  date_long: 'MMMM D, YYYY'
  date_iso: 'YYYY-MM-DD'

  # Time
  time_12h: 'h:mm AM/PM'
  time_24h: 'HH:mm'
  datetime: 'YYYY-MM-DD HH:mm'
```

### Custom Format Codes

| Code    | Meaning             | Example              |
| ------- | ------------------- | -------------------- |
| `0`     | Required digit      | `00.00` -> `01.50`   |
| `#`     | Optional digit      | `#.##` -> `1.5`      |
| `,`     | Thousands separator | `#,##0` -> `1,234`   |
| `%`     | Percentage          | `0%` -> `75%`        |
| `$`     | Currency symbol     | `$#,##0` -> `$1,234` |
| `;`     | Section separator   | `pos;neg;zero`       |
| `[Red]` | Color               | `[Red]-#,##0`        |

## Loading Custom Themes

### From File

```python
from spreadsheet_dl.schema.loader import ThemeLoader
from pathlib import Path

# Load from directory
loader = ThemeLoader(Path("./themes"))
theme = loader.load("corporate")
```

### Programmatically

```python
from spreadsheet_dl.schema.styles import Theme, ColorPalette, Color

theme = Theme(
    name="custom",
    colors=ColorPalette(
        primary=Color("#1A3A5C"),
        secondary=Color("#4472C4"),
    ),
    # ... other settings
)
```

### Using with SpreadsheetBuilder

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

# By name (looks in default themes directory)
builder = SpreadsheetBuilder(theme="corporate")

# By Theme object
builder = SpreadsheetBuilder(theme=my_theme)

# With custom theme directory
builder = SpreadsheetBuilder(
    theme="corporate",
    theme_dir="./custom_themes"
)
```

## Best Practices

### 1. Start with Inheritance

Always extend a base theme:

```yaml
extends: default
```

This ensures you have fallback values for any missing properties.

### 2. Use Variables

Reference colors and fonts by name:

```yaml
# Good
fill:
  color: "{colors.primary}"

# Avoid
fill:
  color: "#1A3A5C"
```

### 3. Test Accessibility

Verify color contrast:

```python
# Minimum contrast ratios:
# - Normal text: 4.5:1 (WCAG AA)
# - Large text: 3:1 (WCAG AA)
# - Enhanced: 7:1 (WCAG AAA)
```

### 4. Consider Print

Dark backgrounds use more ink. For print-heavy uses:

```yaml
styles:
  header_print:
    fill:
      color: '#FFFFFF'
    font:
      color: '{colors.primary}'
    border:
      bottom: { style: medium, color: '{colors.primary}' }
```

### 5. Document Your Theme

Include metadata:

```yaml
name: corporate_2024
version: '1.0.0'
description: |
  Corporate theme following 2024 brand guidelines.
  Primary color updated per marketing directive Q3-2024.
author: Design Team
created: '2024-01-15'
```

## Complete Theme Example

```yaml
# corporate_theme.yaml
name: corporate
version: '1.0'
description: 'Professional corporate theme for financial reports'
extends: default

colors:
  palette:
    primary: '#1A3A5C'
    primary_light: '#2D5A87'
    secondary: '#4472C4'
    accent: '#ED7D31'
    success: '#70AD47'
    warning: '#FFC000'
    danger: '#C00000'

  semantic:
    header_bg: '{colors.primary}'
    header_fg: '#FFFFFF'
    subheader_bg: '{colors.secondary}'
    alternate_row: '#F5F9FC'
    border_light: '#DEE2E6'
    border_dark: '{colors.primary}'

fonts:
  primary:
    family: 'Liberation Sans'
    fallback: ['Arial', 'sans-serif']
  heading:
    family: 'Liberation Sans'
    weight: bold
  monospace:
    family: 'Liberation Mono'
    fallback: ['Consolas', 'monospace']

typography:
  base_size: '11pt'
  scale: 'minor_third'

styles:
  # Headers
  header:
    font:
      family: '{fonts.heading.family}'
      size: '12pt'
      weight: bold
      color: '{colors.header_fg}'
    fill:
      color: '{colors.header_bg}'
    alignment:
      horizontal: center
      vertical: middle
    border:
      bottom: { style: medium, color: '{colors.primary_light}' }

  subheader:
    extends: header
    font:
      size: '11pt'
    fill:
      color: '{colors.subheader_bg}'

  # Data cells
  data:
    font:
      family: '{fonts.primary.family}'
      size: '11pt'
      color: '#333333'
    alignment:
      vertical: middle

  data_center:
    extends: data
    alignment:
      horizontal: center

  currency:
    extends: data
    number_format: '$#,##0.00'
    alignment:
      horizontal: right

  currency_negative:
    extends: currency
    font:
      color: '{colors.danger}'

  percentage:
    extends: data
    number_format: '0.0%'
    alignment:
      horizontal: right

  date:
    extends: data
    number_format: 'YYYY-MM-DD'
    alignment:
      horizontal: center

  # Row styles
  row_even:
    fill:
      color: '#FFFFFF'

  row_odd:
    fill:
      color: '{colors.alternate_row}'

  # Summary rows
  subtotal:
    extends: data
    font:
      weight: bold
    fill:
      color: '#E8F4FD'

  total:
    extends: subtotal
    fill:
      color: '#D0E8F8'
    border:
      top: { style: double, color: '{colors.primary}' }

  grand_total:
    extends: total
    font:
      size: '12pt'
    fill:
      color: '{colors.primary_light}'

  # Special cells
  label:
    extends: data
    font:
      weight: bold

  note:
    extends: data
    font:
      size: '9pt'
      italic: true
      color: '#666666'

formats:
  currency: '$#,##0.00'
  currency_k: '$#,##0,K'
  percentage: '0.0%'
  number: '#,##0'
  date: 'YYYY-MM-DD'
  date_long: 'MMMM D, YYYY'
```
