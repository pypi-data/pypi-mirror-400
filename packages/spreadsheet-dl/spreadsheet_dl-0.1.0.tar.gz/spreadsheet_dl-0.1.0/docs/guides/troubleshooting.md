# Troubleshooting Guide

**Implements: DOC-PROF-008: Troubleshooting Guide**

This guide helps you diagnose and resolve common issues when using the
spreadsheet-dl library.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Theme Issues](#theme-issues)
3. [Style Issues](#style-issues)
4. [Formula Issues](#formula-issues)
5. [Chart Issues](#chart-issues)
6. [Print Issues](#print-issues)
7. [File Issues](#file-issues)
8. [Performance Issues](#performance-issues)
9. [Common Error Messages](#common-error-messages)
10. [Getting Help](#getting-help)

## Installation Issues

### Import Errors

**Problem:** `ImportError: No module named 'spreadsheet_dl'`

**Solution:**

```bash
# Ensure package is installed
uv pip install spreadsheet-dl

# Or install from source
uv pip install -e .

# Verify installation
python -c "import spreadsheet_dl; print(spreadsheet_dl.__version__)"
```

### Missing Dependencies

**Problem:** `ImportError: No module named 'yaml'`

**Solution:**

```bash
# Install all dependencies
uv pip install spreadsheet-dl[all]

# Or install specific dependency
uv pip install pyyaml
```

### Version Conflicts

**Problem:** Incompatible package versions

**Solution:**

```bash
# Check versions
pip list | grep finance

# Create clean virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

uv pip install spreadsheet-dl
```

## Theme Issues

### Theme Not Found

**Problem:** `ThemeNotFoundError: Theme 'corporate' not found`

**Causes:**

1. Theme file doesn't exist
2. Theme directory not specified
3. Invalid theme name

**Solutions:**

```python
# Check available themes
from spreadsheet_dl.schema import ThemeLoader

loader = ThemeLoader()
print(loader.list_themes())

# Specify theme directory
builder = SpreadsheetBuilder(
    theme="corporate",
    theme_dir="/path/to/themes"
)

# Use default theme
builder = SpreadsheetBuilder(theme="default")
```

### Theme Validation Errors

**Problem:** `SchemaValidationError: Invalid theme configuration`

**Common Causes:**

- Invalid color format
- Missing required fields
- Incorrect YAML syntax

**Debug Steps:**

```python
from spreadsheet_dl.schema import validate_theme
import yaml

with open("theme.yaml") as f:
    theme_data = yaml.safe_load(f)

# Validate theme
errors = validate_theme(theme_data)
for error in errors:
    print(f"Error: {error}")
```

**Fix Common Errors:**

```yaml
# Wrong: Missing hash in color
colors:
  primary: 4472C4

# Correct: Include hash
colors:
  primary: "#4472C4"

# Wrong: Invalid size format
font_size: 12

# Correct: Include unit
font_size: "12pt"
```

### Color Resolution Failures

**Problem:** Color reference not resolving

**Solution:**

```yaml
# Ensure color exists in palette
colors:
  primary: '#4472C4'
  secondary: '#ED7D31'

styles:
  header:
    # Reference must match exactly
    background_color: '{colors.primary}' # Correct
    # Not: "{color.primary}" or "{primary}"
```

## Style Issues

### Style Not Applied

**Problem:** Cells don't have expected formatting

**Causes:**

1. Style name doesn't match theme
2. Cell style overridden
3. Style inheritance issue

**Debug:**

```python
# Check available styles
theme = builder._get_theme()
print(list(theme.styles.keys()))

# Verify style exists
if "header_primary" in theme.styles:
    print(theme.styles["header_primary"])
else:
    print("Style not found!")

# Check style application
builder.cell("Value", style="header_primary")  # Explicit style
```

### Style Inheritance Not Working

**Problem:** Extended style missing parent properties

**Check:**

```yaml
styles:
  base:
    font_family: 'Arial'
    font_size: '11pt'

  derived:
    extends: base # Must match exactly
    font_weight: bold

# Verify extends is present and correct
```

### Font Not Rendering

**Problem:** Wrong font displayed

**Causes:**

1. Font not installed on system
2. Font name misspelled
3. Missing fallback fonts

**Solution:**

```yaml
styles:
  text:
    font_family: 'Liberation Sans'
    # Add fallbacks
    fallback:
      - 'Arial'
      - 'Helvetica'
      - 'sans-serif'
```

## Formula Issues

### Formula Not Calculating

**Problem:** Formula shows as text, not result

**Causes:**

1. Missing `=` prefix
2. Using `value` instead of `formula` parameter

**Fix:**

```python
# Wrong
builder.cell("SUM(A1:A10)")
builder.cell(value="=SUM(A1:A10)")

# Correct
builder.cell(formula="=SUM(A1:A10)")
# or
builder.cell("=SUM(A1:A10)")  # Auto-detected
```

### Formula Errors in Spreadsheet

**Problem:** `#REF!`, `#NAME?`, `#VALUE!` errors

**Diagnose:**

```python
# #REF! - Invalid cell reference
# Check range is valid
builder.cell("=SUM(B2:B100)")  # Row 100 exists?

# #NAME? - Unknown function or name
# Check function spelling
builder.cell("=SUMM(A:A)")  # Wrong: SUMM
builder.cell("=SUM(A:A)")   # Correct: SUM

# #VALUE! - Wrong argument type
# Check data types
builder.cell("=SUM(A1:A10)")  # A1:A10 must be numbers
```

### Cross-Sheet References

**Problem:** References to other sheets not working

**Fix:**

```python
# Use sheet name with dot notation
builder.cell("=Summary.B10")  # Correct
builder.cell("='Sheet Name'.B10")  # With spaces

# For ranges
builder.cell("=SUM(Data.B2:B100)")
```

## Chart Issues

### Chart Not Displaying

**Problem:** Chart missing or blank

**Causes:**

1. Invalid data range
2. Missing series data
3. Incompatible chart type

**Debug:**

```python
chart = (
    ChartBuilder()
    .column_chart()
    .title("Test")
    # Verify range is correct
    .series("Data", "Sheet1.B2:B10", categories="Sheet1.A2:A10")
    .build()
)

# Check chart spec
print(chart.to_dict())
```

### Wrong Data in Chart

**Problem:** Chart shows unexpected values

**Check:**

```python
# Verify ranges match data
# Check if ranges include headers (they shouldn't)
.series("Revenue", "Data.B2:B13")  # Start at row 2
# Not: "Data.B1:B13" (includes header)

# Verify sheet name
.series("Revenue", "Data.B2:B13")  # Sheet name is "Data"
```

### Chart Positioning Issues

**Problem:** Chart in wrong position or size

**Fix:**

```python
chart = (
    ChartBuilder()
    .column_chart()
    # Specify position explicitly
    .position(
        cell="E2",           # Anchor cell
        width="400pt",       # Chart width
        height="300pt",      # Chart height
        offset_x="0",        # X offset
        offset_y="0",        # Y offset
    )
    .build()
)
```

## Print Issues

### Wrong Paper Size

**Problem:** Printout on wrong paper size

**Fix:**

```python
from spreadsheet_dl.schema import PageSetup, PageSize

setup = PageSetup(
    size=PageSize.A4,  # or LETTER, LEGAL, etc.
    orientation=PageOrientation.LANDSCAPE,
)
```

### Cut-off Content

**Problem:** Content cut off when printing

**Solutions:**

```python
# Option 1: Fit to width
setup = PageSetup(
    scale_mode=PrintScale.FIT_TO_WIDTH,
    fit_to_pages_wide=1,
)

# Option 2: Adjust margins
setup = PageSetup(
    margins=PageMargins.narrow(),
)

# Option 3: Use landscape
setup = PageSetup(
    orientation=PageOrientation.LANDSCAPE,
)
```

### Headers Not Repeating

**Problem:** Header row only on first page

**Fix:**

```python
from spreadsheet_dl.schema import RepeatConfig

setup = PageSetup(
    repeat=RepeatConfig.header_row(1),  # Repeat row 1
)
```

## File Issues

### File Won't Open

**Problem:** LibreOffice won't open generated file

**Causes:**

1. Corrupted file
2. Invalid ODF structure
3. Unsupported features

**Debug:**

```bash
# Validate ODF file (Linux)
unzip -t output.ods

# Check file size
ls -la output.ods  # Should not be 0 bytes
```

### File Too Large

**Problem:** Generated file unexpectedly large

**Solutions:**

```python
# Remove unused styles
builder = SpreadsheetBuilder(
    theme="minimal",  # Smaller theme
)

# Limit data ranges
# Instead of full column references
builder.cell("=SUM(A:A)")  # Large file

# Use specific ranges
builder.cell("=SUM(A2:A1000)")  # Smaller file
```

### Encoding Issues

**Problem:** Special characters not displaying

**Fix:**

```python
# Ensure UTF-8 encoding
builder.cell("Caf\u00e9")  # Unicode escape
builder.cell("Cafe")       # Or use ASCII

# For file paths
from pathlib import Path
path = Path("output.ods")
builder.save(path)
```

## Performance Issues

### Slow Generation

**Problem:** Spreadsheet takes too long to generate

**Solutions:**

```python
# 1. Batch row operations
data = [["A", 1], ["B", 2], ["C", 3]]
for row in data:
    builder.row()
    for cell in row:
        builder.cell(cell)

# 2. Use specific ranges (not full columns)
# Slow:
builder.cell("=SUM(A:A)")
# Fast:
builder.cell("=SUM(A2:A1000)")

# 3. Limit conditional formatting scope
# Slow:
.range("A:A")
# Fast:
.range("A2:A1000")

# 4. Reduce chart data points
# Consider aggregating data for charts
```

### Memory Issues

**Problem:** `MemoryError` or high memory usage

**Solutions:**

```python
# Process in chunks for large data
chunk_size = 1000
for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    for row in chunk:
        builder.row()
        for cell in row:
            builder.cell(cell)

# Clear references when done
del builder
```

## Common Error Messages

### `ValueError: No sheet selected`

**Cause:** Trying to add content without selecting a sheet

**Fix:**

```python
builder = SpreadsheetBuilder()
builder.sheet("Data")  # Must call sheet() first
builder.column("Name")
```

### `KeyError: 'style_name'`

**Cause:** Style not found in theme

**Fix:**

```python
# Check style exists
theme = builder._get_theme()
if "my_style" in theme.styles:
    builder.cell("value", style="my_style")
else:
    print("Style not found, available:", list(theme.styles.keys()))
```

### `TypeError: expected str, got NoneType`

**Cause:** Passing None where string expected

**Fix:**

```python
# Check for None before passing
title = get_title() or "Default Title"
builder.cell(title)
```

### `SchemaValidationError: Invalid color`

**Cause:** Invalid color format

**Fix:**

```python
from spreadsheet_dl.schema import Color

# Valid formats
Color("#4472C4")      # 6-digit hex
Color("#FFF")         # 3-digit hex
Color.from_rgb(68, 114, 196)  # RGB

# Invalid
Color("4472C4")       # Missing #
Color("#GGGGGG")      # Invalid hex
```

## Getting Help

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code
builder = SpreadsheetBuilder(theme="corporate")
```

### Validate Theme

```python
from spreadsheet_dl.schema import validate_theme
import yaml

with open("theme.yaml") as f:
    theme = yaml.safe_load(f)

errors = validate_theme(theme)
if errors:
    for error in errors:
        print(f"Validation error: {error}")
else:
    print("Theme is valid")
```

### Check Generated Structure

```python
# Inspect builder state
print(f"Sheets: {[s.name for s in builder._sheets]}")
print(f"Current sheet: {builder._current_sheet.name}")
print(f"Columns: {[c.name for c in builder._current_sheet.columns]}")
print(f"Rows: {len(builder._current_sheet.rows)}")
```

### Report Issues

When reporting issues, include:

1. **Version information:**

   ```python
   import spreadsheet_dl
   print(spreadsheet_dl.__version__)
   ```

2. **Minimal reproducible example**

3. **Error message and traceback**

4. **Expected vs actual behavior**

5. **Environment:**
   - Python version
   - Operating system
   - LibreOffice version (if applicable)

## See Also

- [Best Practices](best-practices.md)
- [API Reference](../api/builder.md)
- [Examples Gallery](../examples/gallery.md)
