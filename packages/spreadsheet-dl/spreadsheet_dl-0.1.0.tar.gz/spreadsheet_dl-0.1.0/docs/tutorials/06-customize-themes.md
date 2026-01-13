# Tutorial 6: Customize Themes

Learn how to create and customize visual themes for your spreadsheets using SpreadsheetDL's theme system.

## What You'll Learn

- Understand the theme structure
- Modify existing themes
- Create custom themes from scratch
- Apply themes to spreadsheets
- Create dark mode variants

## Prerequisites

- SpreadsheetDL installed with PyYAML (`uv pip install 'spreadsheet-dl[config]'`)
- Text editor
- Completed [Tutorial 1: Create a Budget](01-create-budget.md)

## Theme System Overview

SpreadsheetDL uses YAML-based themes that define:

- Color schemes (headers, cells, borders)
- Typography (fonts, sizes, weights)
- Cell formatting (number formats, alignment)
- Conditional formatting rules

**Built-in themes:**

- `default` - Professional blue/green theme
- `corporate` - Navy blue business theme
- `minimal` - Clean gray theme
- `dark` - Dark mode theme
- `high_contrast` - Accessibility theme

## Step 1: View Existing Themes

List available themes:

```bash
spreadsheet-dl themes
```

View theme YAML files:

```bash
# Find theme directory
python -c "import spreadsheet_dl; import os; print(os.path.dirname(spreadsheet_dl.__file__) + '/themes')"

# Example output: /usr/local/lib/python3.12/site-packages/spreadsheet_dl/themes
```

## Step 2: Examine a Theme File

Let's look at the `default` theme structure:

```yaml
# themes/default.yaml
name: 'Default Finance Theme'
version: '1.0'
description: 'Clean professional theme for budget spreadsheets'

colors:
  # Primary colors
  primary: '#2563EB' # Blue
  secondary: '#10B981' # Green
  accent: '#F59E0B' # Amber

  # Headers
  header_bg: '#2563EB'
  header_text: '#FFFFFF'

  # Status colors
  success: '#10B981' # Green
  warning: '#F59E0B' # Amber
  error: '#EF4444' # Red

  # Backgrounds
  cell_bg: '#FFFFFF'
  alt_row_bg: '#F3F4F6' # Light gray

  # Borders
  border_color: '#D1D5DB' # Gray

typography:
  # Font family
  base_font: 'Liberation Sans'
  mono_font: 'Liberation Mono'

  # Font sizes (in points)
  header_size: 12
  body_size: 10
  small_size: 8

  # Font weights
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
  # Budget status colors
  over_budget:
    bg_color: '#FEE2E2' # Light red
    text_color: '#991B1B' # Dark red

  under_budget:
    bg_color: '#D1FAE5' # Light green
    text_color: '#065F46' # Dark green

  at_budget:
    bg_color: '#FEF3C7' # Light yellow
    text_color: '#92400E' # Dark yellow
```

## Step 3: Create a Custom Theme

Let's create a custom "sunset" theme with warm colors:

```yaml
# ~/.config/spreadsheet-dl/themes/sunset.yaml
name: 'Sunset Theme'
version: '1.0'
description: 'Warm sunset-inspired color scheme'

colors:
  # Primary colors (warm palette)
  primary: '#F97316' # Orange
  secondary: '#EC4899' # Pink
  accent: '#FBBF24' # Yellow

  # Headers
  header_bg: '#F97316'
  header_text: '#FFFFFF'

  # Status colors
  success: '#10B981' # Keep green for success
  warning: '#FBBF24' # Warm yellow
  error: '#DC2626' # Keep red for error

  # Backgrounds
  cell_bg: '#FFFBEB' # Warm white
  alt_row_bg: '#FEF3C7' # Light yellow

  # Borders
  border_color: '#FED7AA' # Warm orange

typography:
  base_font: 'Liberation Sans'
  mono_font: 'Liberation Mono'
  header_size: 12
  body_size: 10
  small_size: 8
  header_weight: 'bold'
  body_weight: 'normal'

formatting:
  currency_format: '$#,##0.00'
  percentage_format: '0.0%'
  date_format: 'YYYY-MM-DD'
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

Save to: `~/.config/spreadsheet-dl/themes/sunset.yaml`

## Step 4: Use Your Custom Theme

```bash
# Create budget with sunset theme
spreadsheet-dl generate -o ~/budgets/ --theme sunset
```

Or in Python:

```python
from spreadsheet_dl import OdsGenerator

# Use custom theme
generator = OdsGenerator(theme="sunset")
generator.create_budget_spreadsheet("sunset_budget.ods")
```

## Step 5: Create a Dark Mode Theme

Let's create a professional dark theme:

```yaml
# ~/.config/spreadsheet-dl/themes/dark_pro.yaml
name: 'Dark Professional'
version: '1.0'
description: 'Professional dark mode theme for reduced eye strain'

colors:
  # Dark palette
  primary: '#3B82F6' # Bright blue
  secondary: '#10B981' # Bright green
  accent: '#F59E0B' # Amber

  # Headers
  header_bg: '#1F2937' # Dark gray
  header_text: '#F3F4F6' # Light gray

  # Status colors (brighter for dark mode)
  success: '#34D399' # Bright green
  warning: '#FBBF24' # Bright yellow
  error: '#F87171' # Bright red

  # Backgrounds
  cell_bg: '#111827' # Very dark gray
  alt_row_bg: '#1F2937' # Dark gray

  # Borders
  border_color: '#374151' # Medium gray

  # Text
  text_color: '#E5E7EB' # Light gray
  dim_text: '#9CA3AF' # Medium gray

typography:
  base_font: 'Liberation Sans'
  mono_font: 'Liberation Mono'
  header_size: 12
  body_size: 10
  small_size: 8
  header_weight: 'bold'
  body_weight: 'normal'

formatting:
  currency_format: '$#,##0.00'
  percentage_format: '0.0%'
  date_format: 'YYYY-MM-DD'
  header_align: 'center'
  currency_align: 'right'
  text_align: 'left'

conditional:
  over_budget:
    bg_color: '#7F1D1D' # Dark red
    text_color: '#FCA5A5' # Light red
  under_budget:
    bg_color: '#064E3B' # Dark green
    text_color: '#6EE7B7' # Light green
  at_budget:
    bg_color: '#78350F' # Dark yellow
    text_color: '#FDE68A' # Light yellow
```

## Step 6: Modify an Existing Theme

Copy a built-in theme and modify it:

```bash
# Copy default theme to config directory
mkdir -p ~/.config/spreadsheet-dl/themes
cp $(python -c "import spreadsheet_dl; import os; print(os.path.dirname(spreadsheet_dl.__file__) + '/themes/default.yaml')") \
   ~/.config/spreadsheet-dl/themes/my_theme.yaml

# Edit the file
nano ~/.config/spreadsheet-dl/themes/my_theme.yaml
```

Example modifications:

```yaml
# Change just the header colors
colors:
  header_bg: '#7C3AED' # Purple instead of blue
  header_text: '#FFFFFF'
  # ... rest stays the same
```

## Step 7: Theme Inheritance (Advanced)

Create a theme that extends another:

```yaml
# ~/.config/spreadsheet-dl/themes/corporate_dark.yaml
name: 'Corporate Dark'
version: '1.0'
description: 'Dark variant of corporate theme'
extends: 'corporate' # Inherit from corporate theme

# Override specific colors
colors:
  cell_bg: '#1E293B' # Dark blue-gray
  alt_row_bg: '#334155' # Medium blue-gray
  text_color: '#E2E8F0' # Light gray
  header_bg: '#0F172A' # Very dark blue
```

## Step 8: Apply Themes Programmatically

Use themes in your Python scripts:

```python
from pathlib import Path
from spreadsheet_dl import create_spreadsheet, OdsGenerator

# Method 1: Using builder API
builder = create_spreadsheet(theme="sunset")
builder.sheet("Budget") \
    .column("Category").column("Amount") \
    .header_row() \
    .row().cell("Housing").cell(1800) \
    .row().cell("Food").cell(600)
builder.save("themed_budget.ods")

# Method 2: Using OdsGenerator
generator = OdsGenerator(theme="dark_pro")
generator.create_budget_spreadsheet("dark_budget.ods")

# Method 3: Load custom theme
from spreadsheet_dl.schema.loader import ThemeLoader

loader = ThemeLoader()
custom_theme = loader.load_theme(Path("~/.config/spreadsheet-dl/themes/sunset.yaml").expanduser())

# Use with builder
builder = create_spreadsheet(theme=custom_theme)
```

## Color Palette Guidelines

**Professional Themes:**

- Use muted, business-appropriate colors
- Headers: Blues, navy, gray
- Success: Greens
- Warnings: Yellows, oranges
- Errors: Reds

**Dark Themes:**

- Use brighter accent colors
- Reduce contrast to avoid eye strain
- Text should be off-white, not pure white
- Backgrounds should be dark gray, not black

**High Contrast Themes:**

- Maximum contrast for accessibility
- Bold, saturated colors
- Clear color differences
- Large, readable fonts

## Theme Testing

Create a test spreadsheet with all theme elements:

```python
#!/usr/bin/env python3
"""Test theme appearance."""

from decimal import Decimal
from spreadsheet_dl import create_spreadsheet, formula

def test_theme(theme_name):
    """Create test spreadsheet with theme."""

    builder = create_spreadsheet(theme=theme_name)

    # Test all cell types
    f = formula()
    builder.sheet("Theme Test") \
        .column("Text", width="3cm") \
        .column("Currency", width="2.5cm", type="currency") \
        .column("Percentage", width="2.5cm") \
        .column("Date", width="2.5cm", type="date") \
        .header_row(style="header_primary") \
        .row() \
            .cell("Under Budget") \
            .cell(Decimal("450.00")) \
            .cell(formula=f.divide("B2", "500")) \
            .cell("2026-01-15") \
        .row() \
            .cell("At Budget") \
            .cell(Decimal("500.00")) \
            .cell(formula=f.divide("B3", "500")) \
            .cell("2026-01-20") \
        .row() \
            .cell("Over Budget") \
            .cell(Decimal("650.00")) \
            .cell(formula=f.divide("B4", "500")) \
            .cell("2026-01-25")

    output_file = f"theme_test_{theme_name}.ods"
    builder.save(output_file)
    print(f"Test file created: {output_file}")

# Test all themes
for theme in ["default", "corporate", "minimal", "dark", "sunset"]:
    test_theme(theme)
```

## Troubleshooting

**Theme not found?**

- Check theme file exists in `~/.config/spreadsheet-dl/themes/`
- Verify YAML syntax is valid
- Ensure theme name matches filename (without .yaml)

**Colors not applying?**

- Check color format (must be hex: #RRGGBB)
- Verify all required color keys are present
- Test in LibreOffice Calc (better ODS support)

**Fonts not working?**

- Use standard fonts available on all platforms
- Liberation Sans/Serif/Mono (cross-platform)
- Arial, Times New Roman (Windows)
- Helvetica, Times (macOS)

## Best Practices

1. **Start from Existing** - Modify built-in theme rather than from scratch
2. **Test Thoroughly** - Check all cell types and conditions
3. **Accessibility** - Ensure sufficient color contrast
4. **Consistency** - Use consistent color palette
5. **Documentation** - Add description to theme YAML

## Next Steps

- **[Best Practices](../guides/best-practices.md)** - Advanced usage tips
- **[API Reference](../api/index.md)** - Complete API documentation
- **[Theme Schema](../api/schema.md)** - Full theme specification

## Additional Resources

- [Color Palette Tools](https://coolors.co)
- [Accessibility Checker](https://www.a11yproject.com)
- [YAML Syntax Guide](https://yaml.org)
