# Template Engine API Reference

Complete API reference for the YAML-based template system.

## Overview

The Template Engine provides a powerful YAML-based system for creating reusable spreadsheet templates with:

- **Variable substitution** - Dynamic content with `${variable}` syntax
- **Conditional content** - Show/hide sections based on conditions
- **Reusable components** - Share common sections across templates
- **Built-in functions** - Date formatting, calculations, and transformations
- **Component library** - Pre-built templates for common use cases

**Main Components:**

- `TemplateLoader` - Load templates from YAML files
- `TemplateRenderer` - Render templates with variable values
- `SpreadsheetTemplate` and related schemas - Template structure definitions

---

## Quick Start

```python
from spreadsheet_dl.template_engine import load_template, render_template

# Load template
template = load_template("monthly-budget")

# Render with variables
result = render_template(template, {
    "month": 12,
    "year": 2024,
    "categories": ["Housing", "Utilities", "Food"]
})

# Use result to build spreadsheet
# (RenderedSpreadsheet can be converted to SpreadsheetBuilder)
```

---

## TemplateLoader

### Class: `TemplateLoader`

Loader for YAML-based spreadsheet templates.

```python
from spreadsheet_dl.template_engine import TemplateLoader

# Use default template directory
loader = TemplateLoader()

# Use custom directory
loader = TemplateLoader(template_dir="/path/to/templates")
```

#### Constructor

```python
TemplateLoader(template_dir: Path | str | None = None)
```

**Parameters:**

- `template_dir`: Directory containing template files (uses default if None)

**Default Directory:** `spreadsheet_dl/templates/yaml`

### Methods

#### `load()`

Load template by name from template directory.

```python
load(name: str) -> SpreadsheetTemplate
```

**Parameters:**

- `name`: Template name (without .yaml extension)

**Returns:** `SpreadsheetTemplate` object

**Raises:** `FileNotFoundError` if template not found

**Example:**

```python
template = loader.load("monthly-budget")
```

#### `load_from_file()`

Load template from a specific file.

```python
load_from_file(path: Path | str) -> SpreadsheetTemplate
```

**Parameters:**

- `path`: Path to template YAML file

**Returns:** `SpreadsheetTemplate` object

**Example:**

```python
template = loader.load_from_file("/path/to/custom-template.yaml")
```

#### `load_from_string()`

Load template from YAML string.

```python
load_from_string(yaml_content: str) -> SpreadsheetTemplate
```

**Parameters:**

- `yaml_content`: YAML content as string

**Returns:** `SpreadsheetTemplate` object

**Example:**

```python
yaml_str = """
name: simple-template
version: 1.0.0
variables:
  - name: title
    type: string
    required: true
sheets:
  - name: Sheet1
    ...
"""
template = loader.load_from_string(yaml_str)
```

#### `list_templates()`

List available templates in template directory.

```python
list_templates() -> list[dict[str, str]]
```

**Returns:** List of template info dictionaries

**Example:**

```python
templates = loader.list_templates()
for tmpl in templates:
    print(f"{tmpl['name']}: {tmpl['description']}")
```

---

## TemplateRenderer

### Class: `TemplateRenderer`

Render templates to spreadsheet content.

```python
from spreadsheet_dl.template_engine import TemplateRenderer

# Basic renderer
renderer = TemplateRenderer()

# With custom functions
renderer = TemplateRenderer(custom_functions={
    "my_function": lambda x: x * 2
})
```

#### Constructor

```python
TemplateRenderer(custom_functions: dict[str, Callable] | None = None)
```

**Parameters:**

- `custom_functions`: Additional template functions (merged with built-ins)

### Methods

#### `render()`

Render a template with variable values.

```python
render(
    template: SpreadsheetTemplate,
    variables: dict[str, Any]
) -> RenderedSpreadsheet
```

**Parameters:**

- `template`: Template to render
- `variables`: Variable values

**Returns:** `RenderedSpreadsheet` object

**Raises:** `ValueError` if required variables are missing or invalid

**Example:**

```python
result = renderer.render(template, {
    "month": 12,
    "year": 2024,
    "title": "December Budget"
})
```

---

## ExpressionEvaluator

### Class: `ExpressionEvaluator`

Evaluate expressions in template strings.

Supports:

- Simple variables: `${var_name}`
- Nested access: `${parent.child}`
- Function calls: `${month_name(month)}`
- Filters: `${value|default:0}`
- Arithmetic: `${a + b}`

```python
from spreadsheet_dl.template_engine import ExpressionEvaluator

evaluator = ExpressionEvaluator(
    variables={"month": 12, "year": 2024},
    functions={"custom_fn": lambda x: x * 2}
)
```

### Methods

#### `evaluate()`

Evaluate a template string.

```python
evaluate(text: str | Any) -> Any
```

**Parameters:**

- `text`: Template string with `${...}` expressions

**Returns:** Evaluated result

**Examples:**

```python
# Simple variable
result = evaluator.evaluate("${month}")  # 12

# Function call
result = evaluator.evaluate("${month_name(month)}")  # "December"

# Arithmetic
evaluator = ExpressionEvaluator({"a": 10, "b": 5})
result = evaluator.evaluate("${a + b}")  # 15

# Filter
evaluator = ExpressionEvaluator({"value": None})
result = evaluator.evaluate("${value|default:0}")  # 0

# Complex expression in text
result = evaluator.evaluate("Budget for ${month_name(month)} ${year}")
# "Budget for December 2024"
```

### Supported Filters

| Filter                | Description          | Example                 |
| --------------------- | -------------------- | ----------------------- |
| `default:value`       | Use default if None  | `${amount\|default:0}`  |
| `upper`               | Uppercase string     | `${name\|upper}`        |
| `lower`               | Lowercase string     | `${name\|lower}`        |
| `title`               | Title case           | `${name\|title}`        |
| `round:n`             | Round to n decimals  | `${value\|round:2}`     |
| `currency:symbol`     | Format as currency   | `${amount\|currency:$}` |
| `percentage:decimals` | Format as percentage | `${rate\|percentage:1}` |

---

## Built-in Functions

Available in templates via `${function_name(args)}` syntax.

### Date/Time Functions

#### `month_name(month: int) -> str`

Get full month name from number (1-12).

```yaml
value: '${month_name(month)}' # "January", "February", etc.
```

#### `month_abbrev(month: int) -> str`

Get abbreviated month name.

```yaml
value: '${month_abbrev(month)}' # "Jan", "Feb", etc.
```

#### `format_date(date: date, pattern: str = "%Y-%m-%d") -> str`

Format a date with given pattern.

```yaml
value: "${format_date(current_date, '%B %d, %Y')}"
# "December 15, 2024"
```

### Formatting Functions

#### `format_currency(value: float, symbol: str = "$", decimals: int = 2) -> str`

Format number as currency.

```yaml
value: "${format_currency(1234.5)}"  # "$1,234.50"
value: "${format_currency(1234.5, '€', 2)}"  # "€1,234.50"
```

#### `format_percentage(value: float, decimals: int = 1) -> str`

Format number as percentage.

```yaml
value: "${format_percentage(0.15)}"  # "15.0%"
value: "${format_percentage(0.1567, 2)}"  # "15.67%"
```

### String Functions

- `upper(s)` - Uppercase
- `lower(s)` - Lowercase
- `title(s)` - Title case

### Math Functions

- `abs(x)` - Absolute value
- `round(x, n)` - Round to n decimals
- `min(*values)` - Minimum value
- `max(*values)` - Maximum value
- `sum(values)` - Sum of values
- `len(sequence)` - Length of sequence

### Built-in Variables

Always available in templates:

| Variable             | Description          | Example Value         |
| -------------------- | -------------------- | --------------------- |
| `current_date`       | Today's date         | `2024-12-15`          |
| `current_datetime`   | Current datetime     | `2024-12-15 10:30:00` |
| `current_year`       | Current year         | `2024`                |
| `current_month`      | Current month (1-12) | `12`                  |
| `current_month_name` | Current month name   | `"December"`          |
| `current_day`        | Current day of month | `15`                  |

---

## Template Schema

### SpreadsheetTemplate

Top-level template definition.

```python
@dataclass
class SpreadsheetTemplate:
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    theme: str = "default"
    variables: list[TemplateVariable] = []
    components: dict[str, ComponentDefinition] = {}
    sheets: list[SheetTemplate] = []
    properties: dict[str, Any] = {}
    validations: dict[str, Any] = {}
    conditional_formats: dict[str, Any] = {}
    styles: dict[str, Any] = {}
```

**YAML Example:**

```yaml
name: monthly-budget
version: 1.0.0
description: Monthly budget tracking template
author: Finance Team
theme: corporate

variables:
  - name: month
    type: number
    required: true
    description: Month number (1-12)

  - name: year
    type: number
    required: true

  - name: categories
    type: list
    required: true
    description: List of budget categories

sheets:
  - name: '${month_name(month)} ${year}'
    columns: [...]
    rows: [...]
```

### TemplateVariable

Variable definition.

```python
@dataclass
class TemplateVariable:
    name: str
    type: VariableType = VariableType.STRING
    description: str = ""
    required: bool = False
    default: Any = None
    validation: str | None = None
    choices: list[str] = []
```

**Variable Types:**

- `STRING` - Text values
- `NUMBER` - Numeric values
- `CURRENCY` - Currency amounts
- `DATE` - Date values
- `BOOLEAN` - True/false
- `LIST` - List of values
- `FORMULA` - Formula expressions

**YAML Example:**

```yaml
variables:
  - name: month
    type: number
    required: true
    description: Month number (1-12)

  - name: budget_total
    type: currency
    default: 5000.00

  - name: include_charts
    type: boolean
    default: true

  - name: category
    type: string
    choices: ['Housing', 'Food', 'Transport']
```

### SheetTemplate

Sheet definition.

```python
@dataclass
class SheetTemplate:
    name: str
    name_template: str | None = None  # e.g., "${month_name} ${year}"
    columns: list[ColumnTemplate] = []
    header_row: RowTemplate | None = None
    data_rows: RowTemplate | None = None
    total_row: RowTemplate | None = None
    custom_rows: list[RowTemplate] = []
    components: list[str] = []  # Component references
    freeze_rows: int = 0
    freeze_cols: int = 0
    print_area: str | None = None
    protection: dict[str, Any] = {}
    conditionals: list[ConditionalBlock] = []
    validations: list[str] = []
    conditional_formats: list[str] = []
```

**YAML Example:**

```yaml
sheets:
  - name: Budget
    name_template: '${month_name(month)} Budget'
    freeze_rows: 1

    columns:
      - name: Category
        width: 4cm
        type: string

      - name: Budgeted
        width: 3cm
        type: currency

      - name: Actual
        width: 3cm
        type: currency

    header:
      style: header
      cells:
        - value: Category
        - value: Budgeted
        - value: Actual

    data_rows:
      repeat: 15
      style: data
      alternate_style: data_alt

    total:
      style: total
      cells:
        - value: Total
        - formula: '=SUM(B2:B16)'
        - formula: '=SUM(C2:C16)'
```

### ColumnTemplate

Column definition.

```python
@dataclass
class ColumnTemplate:
    name: str
    width: str = "2.5cm"
    type: str = "string"
    style: str | None = None
    validation: str | None = None
    conditional_format: str | None = None
    hidden: bool = False
    frozen: bool = False
```

**YAML Example:**

```yaml
columns:
  - name: Date
    width: 2.5cm
    type: date

  - name: Category
    width: 4cm
    validation: category_list

  - name: Amount
    width: 3cm
    type: currency
    style: currency
```

### RowTemplate

Row definition.

```python
@dataclass
class RowTemplate:
    cells: list[CellTemplate] = []
    style: str | None = None
    height: str | None = None
    repeat: int = 1
    alternate_style: str | None = None
    conditional: ConditionalBlock | None = None
```

**YAML Example:**

```yaml
# Header row
header:
  style: header
  cells:
    - value: Month
    - value: Budget
    - value: Actual

# Data rows with repeat
data_rows:
  repeat: 20
  style: data
  alternate_style: data_alt
  cells:
    - type: date
    - type: currency
    - type: currency

# Total row
total:
  style: total
  cells:
    - value: Total
    - formula: '=SUM(B2:B21)'
    - formula: '=SUM(C2:C21)'
```

### CellTemplate

Cell definition.

```python
@dataclass
class CellTemplate:
    value: Any = None
    formula: str | None = None
    style: str | None = None
    type: str | None = None
    colspan: int = 1
    rowspan: int = 1
    validation: str | None = None
    conditional_format: str | None = None
```

**YAML Example:**

```yaml
cells:
  # Static value
  - value: 'Total'

  # Variable reference
  - value: '${month_name(month)}'

  # Formula
  - formula: '=SUM(B2:B${last_row})'
    type: currency
    style: total

  # Merged cell
  - value: 'Budget Report'
    colspan: 3
    style: title
```

### ComponentDefinition

Reusable component.

```python
@dataclass
class ComponentDefinition:
    name: str
    description: str = ""
    variables: list[TemplateVariable] = []
    columns: list[ColumnTemplate] = []
    rows: list[RowTemplate] = []
    styles: dict[str, str] = {}
```

**YAML Example:**

```yaml
components:
  budget_header:
    description: Standard budget header with title and date
    variables:
      - name: title
        type: string
        required: true
      - name: date
        type: date

    rows:
      - style: title
        cells:
          - value: '${title}'
            colspan: 4

      - style: subtitle
        cells:
          - value: 'Generated: ${format_date(date)}'
            colspan: 4

# Use component in sheet
sheets:
  - name: Budget
    components:
      - budget_header:title=Monthly Budget,date=${current_date}
```

### ConditionalBlock

Conditional content.

```python
@dataclass
class ConditionalBlock:
    condition: str
    content: list[Any] = []
    else_content: list[Any] = []
    style: str | None = None
```

**YAML Example:**

```yaml
# Conditional row
- if: "${include_summary}"
  then:
    - cells:
        - value: "Summary"
        - formula: "=SUM(B:B)"
  else: []

# Conditional in sheet
conditionals:
  - if: "${has_charts}"
    style: with_charts
```

---

## Rendered Output Classes

### RenderedSpreadsheet

Fully rendered spreadsheet.

```python
@dataclass
class RenderedSpreadsheet:
    name: str
    version: str = "1.0.0"
    description: str = ""
    sheets: list[RenderedSheet] = []
    styles: dict[str, Any] = {}
    properties: dict[str, Any] = {}
```

### RenderedSheet

Rendered sheet.

```python
@dataclass
class RenderedSheet:
    name: str
    columns: list[dict[str, Any]] = []
    rows: list[RenderedRow] = []
    freeze_rows: int = 0
    freeze_cols: int = 0
    protection: dict[str, Any] = {}
```

### RenderedRow

Rendered row.

```python
@dataclass
class RenderedRow:
    cells: list[RenderedCell] = []
    style: str | None = None
    height: str | None = None
```

### RenderedCell

Rendered cell.

```python
@dataclass
class RenderedCell:
    value: Any = None
    formula: str | None = None
    style: str | None = None
    type: str | None = None
    colspan: int = 1
    rowspan: int = 1
```

---

## Convenience Functions

### `load_template()`

Load template by name.

```python
def load_template(
    name: str,
    template_dir: Path | str | None = None
) -> SpreadsheetTemplate
```

**Example:**

```python
from spreadsheet_dl.template_engine import load_template

template = load_template("monthly-budget")
```

### `load_template_from_yaml()`

Load template from YAML string.

```python
def load_template_from_yaml(yaml_content: str) -> SpreadsheetTemplate
```

**Example:**

```python
from spreadsheet_dl.template_engine import load_template_from_yaml

yaml_str = """
name: simple
sheets:
  - name: Sheet1
"""
template = load_template_from_yaml(yaml_str)
```

### `render_template()`

Render template with variables.

```python
def render_template(
    template: SpreadsheetTemplate,
    variables: dict[str, Any],
    custom_functions: dict[str, Callable] | None = None
) -> RenderedSpreadsheet
```

**Example:**

```python
from spreadsheet_dl.template_engine import render_template

result = render_template(template, {
    "month": 12,
    "year": 2024
})
```

---

## Complete Examples

### Example 1: Simple Budget Template

**Template YAML (budget-simple.yaml):**

```yaml
name: budget-simple
version: 1.0.0
description: Simple monthly budget
theme: corporate

variables:
  - name: month
    type: number
    required: true

  - name: year
    type: number
    required: true

  - name: budget_amount
    type: currency
    default: 5000.00

sheets:
  - name: '${month_name(month)} ${year} Budget'
    freeze_rows: 1

    columns:
      - name: Category
        width: 4cm
      - name: Budgeted
        width: 3cm
        type: currency
      - name: Actual
        width: 3cm
        type: currency
      - name: Difference
        width: 3cm
        type: currency

    header:
      style: header
      cells:
        - value: Category
        - value: Budgeted
        - value: Actual
        - value: Difference

    data_rows:
      repeat: 15
      style: data
      alternate_style: data_alt

    total:
      style: total
      cells:
        - value: Total
        - formula: '=SUM(B2:B16)'
        - formula: '=SUM(C2:C16)'
        - formula: '=B17-C17'
```

**Usage:**

```python
from spreadsheet_dl.template_engine import load_template, render_template

# Load template
template = load_template("budget-simple")

# Render with variables
result = render_template(template, {
    "month": 12,
    "year": 2024,
    "budget_amount": 5000.00
})

# Convert to spreadsheet
# (Integration with SpreadsheetBuilder)
```

### Example 2: Template with Components

**Template YAML:**

```yaml
name: report-with-header
version: 1.0.0

variables:
  - name: title
    type: string
    required: true
  - name: period
    type: string
    required: true

components:
  report_header:
    description: Standard report header
    variables:
      - name: title
        type: string
      - name: period
        type: string

    rows:
      - style: title
        cells:
          - value: '${title}'
            colspan: 4

      - style: subtitle
        cells:
          - value: 'Period: ${period}'
            colspan: 4

      - cells: [] # Blank row

sheets:
  - name: Report
    components:
      - 'report_header:title=${title},period=${period}'

    columns:
      - name: Item
        width: 6cm
      - name: Value
        width: 3cm
        type: currency

    data_rows:
      repeat: 10
```

**Usage:**

```python
result = render_template(template, {
    "title": "Monthly Sales Report",
    "period": "December 2024"
})
```

### Example 3: Conditional Content

**Template YAML:**

```yaml
name: conditional-budget
version: 1.0.0

variables:
  - name: include_summary
    type: boolean
    default: true

  - name: include_charts
    type: boolean
    default: false

sheets:
  - name: Budget
    columns:
      - name: Category
        width: 4cm
      - name: Amount
        width: 3cm
        type: currency

    header:
      cells:
        - value: Category
        - value: Amount

    data_rows:
      repeat: 10

    # Conditional total row
    custom_rows:
      - if: '${include_summary}'
        then:
          - style: total
            cells:
              - value: Total
              - formula: '=SUM(B2:B11)'
        else: []

    # Conditional components
    conditionals:
      - if: '${include_charts}'
        content:
          - chart_component
```

### Example 4: Advanced Variable Substitution

**Template YAML:**

```yaml
name: advanced-vars
version: 1.0.0

variables:
  - name: month
    type: number
  - name: rate
    type: number
  - name: amount
    type: currency

sheets:
  - name: Calculations
    rows:
      - cells:
          # Function call
          - value: 'Month: ${month_name(month)}'

          # Arithmetic
          - value: '${amount * rate}'
            type: currency

          # Filter with default
          - value: '${optional_field|default:N/A}'

          # Nested function
          - value: '${upper(month_name(month))}'

          # Format function
          - value: '${format_currency(amount)}'
```

### Example 5: Component Library Usage

**Template YAML:**

```yaml
name: using-components
version: 1.0.0

variables:
  - name: title
    type: string
  - name: month
    type: number

components:
  header:
    variables:
      - name: title
        type: string
    rows:
      - style: header
        cells:
          - value: "${title}"
            colspan: 3

  footer:
    rows:
      - style: footer
        cells:
          - value: "Generated: ${format_date(current_date)}"
            colspan: 3

sheets:
  - name: Report
    components:
      - "header:title=${title}"

    columns:
      - name: Item
      - name: Value
      - name: Status

    data_rows:
      repeat: 5

    components:
      - footer
```

---

## Best Practices

### 1. Use Descriptive Variable Names

```yaml
# Good
variables:
  - name: monthly_budget_amount
  - name: reporting_period_start

# Avoid
variables:
  - name: amt
  - name: d1
```

### 2. Provide Defaults for Optional Variables

```yaml
variables:
  - name: include_charts
    type: boolean
    default: true # Good: sensible default

  - name: currency_symbol
    type: string
    default: '$'
```

### 3. Document Templates

```yaml
name: monthly-budget
description: |
  Monthly budget tracking template with:
  - Category-based expense tracking
  - Budget vs. actual comparison
  - Optional charts and summaries
author: Finance Team
version: 1.2.0
```

### 4. Use Components for Reusability

```yaml
# Define once
components:
  standard_header:
    rows: [...]

# Use many times
sheets:
  - name: Sheet1
    components: [standard_header]

  - name: Sheet2
    components: [standard_header]
```

### 5. Validate Input with Choices

```yaml
variables:
  - name: report_type
    type: string
    choices: ['summary', 'detailed', 'comparison']
    description: Type of report to generate
```

### 6. Use Conditional Content Wisely

```yaml
# Good: Optional features
- if: '${include_summary}'
  then: [summary_rows]

# Good: Different layouts
- if: "${layout == 'detailed'}"
  then: [detailed_columns]
  else: [simple_columns]
# Avoid: Complex nested conditions
# (better to use separate templates)
```

### 7. Leverage Built-in Variables

```yaml
cells:
  # Use current date
  - value: 'Report Date: ${format_date(current_date)}'

  # Use current year for copyright
  - value: '© ${current_year} Company Name'
```

### 8. Test Templates with Edge Cases

```python
# Test with minimum values
result = render_template(template, {"month": 1, "year": 2000})

# Test with maximum values
result = render_template(template, {"month": 12, "year": 9999})

# Test with empty lists
result = render_template(template, {"categories": []})
```

---

## Error Handling

### Variable Validation Errors

```python
try:
    result = render_template(template, {"month": 12})
except ValueError as e:
    print(f"Variable error: {e}")
    # "Required variable 'year' not provided"
```

### Template Loading Errors

```python
from spreadsheet_dl.template_engine import TemplateLoader

try:
    template = loader.load("nonexistent")
except FileNotFoundError as e:
    print(f"Template not found: {e}")
```

### Expression Evaluation Errors

```python
# Invalid expressions return None or empty string
evaluator = ExpressionEvaluator({"x": 10})

# Unknown function
result = evaluator.evaluate("${unknown_fn(x)}")  # Returns "${unknown_fn(x)}"

# Missing variable (with filter)
result = evaluator.evaluate("${missing|default:0}")  # Returns 0

# Missing variable (without filter)
result = evaluator.evaluate("${missing}")  # Returns None or ""
```

---

## Integration with SpreadsheetBuilder

```python
from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl.template_engine import load_template, render_template

# Load and render template
template = load_template("monthly-budget")
rendered = render_template(template, {
    "month": 12,
    "year": 2024,
    "categories": ["Housing", "Food", "Transport"]
})

# Convert to spreadsheet
builder = SpreadsheetBuilder(theme=rendered.properties.get("theme", "default"))

for sheet in rendered.sheets:
    builder.sheet(sheet.name)

    # Add columns
    for col in sheet.columns:
        builder.column(
            col["name"],
            width=col.get("width", "2.5cm"),
            type=col.get("type", "string")
        )

    # Add rows
    for row in sheet.rows:
        builder.row(style=row.style, height=row.height)
        for cell in row.cells:
            builder.cell(
                value=cell.value,
                formula=cell.formula,
                style=cell.style,
                type=cell.type
            )

# Save
builder.save("budget.ods")
```
