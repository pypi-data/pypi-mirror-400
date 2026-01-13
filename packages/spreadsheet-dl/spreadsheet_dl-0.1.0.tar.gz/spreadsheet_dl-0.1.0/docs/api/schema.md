# Theme Schema Specification

## Overview

The SpreadsheetDL theme system uses YAML-based schema files to define visual styling for spreadsheets. This document provides the complete schema specification for creating and validating themes.

**Key Features:**

- YAML-based configuration
- Comprehensive styling options
- Theme inheritance support
- Validation and error checking
- Multiple theme variants (light, dark, high-contrast)
- Cross-platform compatibility

## Schema Structure

### Root Elements

All theme files must include these top-level keys:

```yaml
name: string # Required - Human-readable theme name
version: string # Required - Semantic version (e.g., "1.0.0")
description: string # Required - Theme description
extends: string | null # Optional - Parent theme to inherit from

colors: object # Required - Color definitions
typography: object # Required - Font and text styling
formatting: object # Required - Number and cell formatting
conditional: object # Optional - Conditional formatting rules
```

## Colors Section

### Required Color Keys

```yaml
colors:
  # Primary palette
  primary: color # Primary brand color
  secondary: color # Secondary accent color
  accent: color # Tertiary accent color

  # Headers
  header_bg: color # Header background color
  header_text: color # Header text color

  # Status colors
  success: color # Success/positive indicator
  warning: color # Warning/caution indicator
  error: color # Error/negative indicator

  # Backgrounds
  cell_bg: color # Default cell background
  alt_row_bg: color # Alternating row background

  # Borders
  border_color: color # Default border color
```

### Optional Color Keys

```yaml
colors:
  # Extended text colors
  text_color: color # Default text color (default: #000000)
  dim_text: color # Dimmed/secondary text (default: #666666)
  link_color: color # Hyperlink color (default: primary)

  # Additional backgrounds
  selected_bg: color # Selected cell background
  hover_bg: color # Hover state background
  frozen_bg: color # Frozen pane background

  # Extended borders
  grid_color: color # Grid line color
  major_grid_color: color # Major grid line color
  border_heavy: color # Heavy border color

  # Chart colors
  chart_color_1: color # First chart series color
  chart_color_2: color # Second chart series color
  chart_color_3: color # Third chart series color
  chart_color_4: color # Fourth chart series color
  chart_color_5: color # Fifth chart series color
```

### Color Format

Colors must be specified as hexadecimal RGB values:

```yaml
colors:
  primary: '#3B82F6' # Blue
  secondary: '#10B981' # Green
  error: '#EF4444' # Red
```

**Valid formats:**

- `#RGB` - 3-digit hex (e.g., `#F00` for red)
- `#RRGGBB` - 6-digit hex (e.g., `#FF0000` for red)

**Invalid formats:**

- Named colors (`red`, `blue`)
- RGB functions (`rgb(255, 0, 0)`)
- RGBA with alpha (`#FF0000AA`)

## Typography Section

### Required Typography Keys

```yaml
typography:
  # Font families
  base_font: string # Base font family
  mono_font: string # Monospace font family

  # Font sizes (in points)
  header_size: number # Header font size
  body_size: number # Body text font size
  small_size: number # Small text font size

  # Font weights
  header_weight: string # Header font weight
  body_weight: string # Body font weight
```

### Optional Typography Keys

```yaml
typography:
  # Additional sizes
  title_size: number # Title font size (default: 18)
  subtitle_size: number # Subtitle font size (default: 14)
  caption_size: number # Caption font size (default: 8)

  # Additional weights
  bold_weight: string # Bold text weight (default: "bold")
  light_weight: string # Light text weight (default: "normal")

  # Text decoration
  underline_links: boolean # Underline hyperlinks (default: true)
  strikethrough_invalid: boolean # Strikethrough invalid values (default: false)

  # Line spacing
  line_height: number # Line height multiplier (default: 1.2)
  paragraph_spacing: number # Paragraph spacing (default: 0)
```

### Font Families

**Cross-platform safe fonts:**

- `Liberation Sans` - Sans-serif (universal)
- `Liberation Serif` - Serif (universal)
- `Liberation Mono` - Monospace (universal)
- `Arial` - Sans-serif (Windows)
- `Helvetica` - Sans-serif (macOS)
- `Courier New` - Monospace (universal)

**Font stacks (fallbacks):**

```yaml
typography:
  base_font: 'Liberation Sans, Arial, Helvetica, sans-serif'
  mono_font: 'Liberation Mono, Courier New, Consolas, monospace'
```

### Font Weights

Valid font weight values:

- `normal` - Regular weight (400)
- `bold` - Bold weight (700)
- Numeric values: `100`, `200`, `300`, `400`, `500`, `600`, `700`, `800`, `900`

## Formatting Section

### Required Formatting Keys

```yaml
formatting:
  # Number formats
  currency_format: string # Currency display format
  percentage_format: string # Percentage display format
  date_format: string # Date display format

  # Alignment
  header_align: string # Header text alignment
  currency_align: string # Currency alignment
  text_align: string # Default text alignment
```

### Optional Formatting Keys

```yaml
formatting:
  # Extended number formats
  integer_format: string # Integer format (default: "#,##0")
  decimal_format: string # Decimal format (default: "#,##0.00")
  accounting_format: string # Accounting format (default: "_($* #,##0.00_);_($* (#,##0.00);_($* \"-\"??_);_(@_)")

  # Date/time formats
  time_format: string # Time format (default: "HH:MM:SS")
  datetime_format: string # Datetime format (default: "YYYY-MM-DD HH:MM:SS")
  short_date_format: string # Short date (default: "MM/DD/YY")

  # Alignment options
  vertical_align: string # Vertical alignment (default: "middle")
  wrap_text: boolean # Wrap text in cells (default: false)
  shrink_to_fit: boolean # Shrink text to fit (default: false)

  # Decimal places
  default_decimals: number # Default decimal places (default: 2)
  currency_decimals: number # Currency decimal places (default: 2)
```

### Number Format Codes

SpreadsheetDL uses OpenDocument format number codes:

**Currency:**

```yaml
currency_format: "$#,##0.00"              # $1,234.56
currency_format: "$#,##0.00;[RED]-$#,##0.00"  # Red for negative
```

**Percentage:**

```yaml
percentage_format: "0.0%"                 # 12.5%
percentage_format: "0.00%"                # 12.50%
```

**Date:**

```yaml
date_format: "YYYY-MM-DD"                 # 2026-01-15
date_format: "MM/DD/YYYY"                 # 01/15/2026
date_format: "DD MMM YYYY"                # 15 Jan 2026
date_format: "MMMM D, YYYY"               # January 15, 2026
```

**Number:**

```yaml
integer_format: '#,##0' # 1,234
decimal_format: '#,##0.00' # 1,234.56
```

### Alignment Values

Valid alignment values:

- `left` - Left aligned
- `center` - Center aligned
- `right` - Right aligned
- `justify` - Justified

Vertical alignment:

- `top` - Top aligned
- `middle` - Middle aligned
- `bottom` - Bottom aligned

## Conditional Formatting Section

### Structure

```yaml
conditional:
  rule_name:
    bg_color: color # Background color
    text_color: color # Text color
    font_weight: string # Optional font weight
    font_style: string # Optional font style (italic, normal)
    border_color: color # Optional border color
```

### Built-in Rules

```yaml
conditional:
  # Budget status rules
  over_budget:
    bg_color: '#FEE2E2' # Light red
    text_color: '#991B1B' # Dark red
    font_weight: 'bold'

  under_budget:
    bg_color: '#D1FAE5' # Light green
    text_color: '#065F46' # Dark green

  at_budget:
    bg_color: '#FEF3C7' # Light yellow
    text_color: '#92400E' # Dark yellow

  # Alert levels
  critical_alert:
    bg_color: '#FEE2E2'
    text_color: '#991B1B'
    font_weight: 'bold'

  warning_alert:
    bg_color: '#FEF3C7'
    text_color: '#92400E'

  info_alert:
    bg_color: '#DBEAFE'
    text_color: '#1E40AF'
```

### Custom Rules

You can define custom conditional formatting rules:

```yaml
conditional:
  high_priority:
    bg_color: '#FECACA'
    text_color: '#7F1D1D'
    font_weight: 'bold'
    border_color: '#DC2626'

  low_priority:
    bg_color: '#E5E7EB'
    text_color: '#6B7280'
    font_style: 'italic'
```

## Theme Inheritance

### Extending Base Themes

Themes can inherit from other themes using the `extends` key:

```yaml
name: 'Dark Professional'
version: '1.0.0'
description: 'Dark mode variant of professional theme'
extends: 'professional' # Inherit from professional theme

# Override specific colors
colors:
  cell_bg: '#1F2937' # Dark background
  text_color: '#F3F4F6' # Light text
  header_bg: '#111827' # Darker header


# Typography and formatting inherited automatically
```

**Inheritance rules:**

1. Child theme inherits all keys from parent
2. Child theme can override any inherited key
3. Deeply nested keys are merged
4. Arrays are replaced (not merged)
5. Circular inheritance is not allowed

### Multiple Inheritance Levels

```yaml
# base.yaml
name: "Base Theme"
colors:
  primary: "#3B82F6"
  secondary: "#10B981"

# professional.yaml
name: "Professional"
extends: "base"
colors:
  primary: "#1E40AF"  # Override

# dark_professional.yaml
name: "Dark Professional"
extends: "professional"
colors:
  cell_bg: "#1F2937"  # Override
  # Inherits professional's primary, base's secondary
```

## Complete Example

### Light Theme

```yaml
name: 'Professional Light'
version: '1.0.0'
description: 'Clean professional light theme for business use'

colors:
  # Primary palette
  primary: '#2563EB' # Blue
  secondary: '#10B981' # Green
  accent: '#F59E0B' # Amber

  # Headers
  header_bg: '#2563EB'
  header_text: '#FFFFFF'

  # Status colors
  success: '#10B981'
  warning: '#F59E0B'
  error: '#EF4444'

  # Backgrounds
  cell_bg: '#FFFFFF'
  alt_row_bg: '#F9FAFB'

  # Borders
  border_color: '#E5E7EB'

  # Text
  text_color: '#111827'
  dim_text: '#6B7280'

typography:
  # Fonts
  base_font: 'Liberation Sans, Arial, Helvetica, sans-serif'
  mono_font: 'Liberation Mono, Courier New, monospace'

  # Sizes
  header_size: 12
  body_size: 10
  small_size: 8

  # Weights
  header_weight: 'bold'
  body_weight: 'normal'

formatting:
  # Number formats
  currency_format: '$#,##0.00'
  percentage_format: '0.0%'
  date_format: 'YYYY-MM-DD'

  # Alignment
  header_align: 'center'
  currency_align: 'right'
  text_align: 'left'

conditional:
  over_budget:
    bg_color: '#FEE2E2'
    text_color: '#991B1B'

  under_budget:
    bg_color: '#D1FAE5'
    text_color: '#065F46'

  at_budget:
    bg_color: '#FEF3C7'
    text_color: '#92400E'
```

### Dark Theme

```yaml
name: 'Professional Dark'
version: '1.0.0'
description: 'Professional dark theme for reduced eye strain'
extends: 'professional_light' # Inherit structure

colors:
  # Primary palette (brighter for dark mode)
  primary: '#60A5FA'
  secondary: '#34D399'
  accent: '#FBBF24'

  # Headers
  header_bg: '#1F2937'
  header_text: '#F3F4F6'

  # Status colors (brighter)
  success: '#34D399'
  warning: '#FBBF24'
  error: '#F87171'

  # Backgrounds
  cell_bg: '#111827'
  alt_row_bg: '#1F2937'

  # Borders
  border_color: '#374151'

  # Text
  text_color: '#F9FAFB'
  dim_text: '#9CA3AF'

conditional:
  over_budget:
    bg_color: '#7F1D1D'
    text_color: '#FCA5A5'

  under_budget:
    bg_color: '#064E3B'
    text_color: '#6EE7B7'

  at_budget:
    bg_color: '#78350F'
    text_color: '#FDE68A'
```

## Validation Rules

### Schema Validation

Themes are validated against these rules:

1. **Required keys present**
   - `name`, `version`, `description`
   - `colors`, `typography`, `formatting`

2. **Color format validation**
   - All colors must be valid hex codes
   - Format: `#RGB` or `#RRGGBB`

3. **Typography validation**
   - Font sizes must be positive numbers
   - Font weights must be valid values
   - Font families must be strings

4. **Formatting validation**
   - Format codes must be valid ODF format strings
   - Alignment values must be valid options

5. **Version validation**
   - Version must follow semantic versioning
   - Format: `MAJOR.MINOR.PATCH`

### Validation Example

```python
from spreadsheet_dl.schema import ThemeValidator, ValidationError

validator = ThemeValidator()

try:
    # Validate theme file
    validator.validate_file("my_theme.yaml")
    print("Theme is valid!")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

## Theme Loading

### Load Theme

```python
from spreadsheet_dl.schema import ThemeLoader

loader = ThemeLoader()

# Load theme from file
theme = loader.load_theme("themes/professional.yaml")

# Load theme from string
yaml_content = """
name: "Custom Theme"
version: "1.0.0"
...
"""
theme = loader.load_theme_from_string(yaml_content)

# Get theme by name (searches standard directories)
theme = loader.get_theme("professional")
```

### Theme Directories

Themes are searched in this order:

1. `~/.config/spreadsheet-dl/themes/` - User themes
2. `./themes/` - Project themes
3. Package themes - Built-in themes

## Best Practices

1. **Start from Base Theme**
   - Use `extends` to inherit from built-in themes
   - Only override what you need to change

2. **Color Contrast**
   - Ensure sufficient contrast (WCAG AA: 4.5:1 for text)
   - Test with colorblind simulation tools
   - Provide high-contrast variant

3. **Font Selection**
   - Use cross-platform fonts
   - Provide fallback font stacks
   - Test on multiple platforms

4. **Number Formats**
   - Follow locale conventions
   - Provide clear format codes
   - Document custom formats

5. **Documentation**
   - Add clear description
   - Document custom conditional rules
   - Provide usage examples

6. **Versioning**
   - Use semantic versioning
   - Document breaking changes
   - Maintain changelog

## Troubleshooting

**Theme not loading?**

- Check YAML syntax (use YAML validator)
- Verify all required keys present
- Check file permissions
- Ensure theme is in search path

**Colors not applying?**

- Verify hex color format (#RRGGBB)
- Check color keys match schema
- Test with built-in theme first
- Look for inheritance issues

**Fonts not working?**

- Use cross-platform fonts
- Check font name spelling
- Provide fallback fonts
- Test in target application

**Validation errors?**

- Read error messages carefully
- Check for typos in keys
- Verify value types (string vs number)
- Use schema documentation

## See Also

- [Theme Creation Guide](../guides/theme-creation.md) - Creating custom themes
- [Tutorial: Customize Themes](../tutorials/06-customize-themes.md) - Theme customization
- [Styles API](styles.md) - Programmatic styling
- [Template Engine](template_engine.md) - Template system
- [Builder API](builder.md) - Spreadsheet builder
