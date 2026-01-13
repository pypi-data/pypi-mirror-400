# Template Creation Guide

A comprehensive guide to creating reusable spreadsheet templates in SpreadsheetDL.

**Implements:** DOC-PROF-003 (Template Creation Guide)

## Overview

Templates provide reusable spreadsheet structures that can be instantiated with different data while maintaining consistent formatting, formulas, and layout. A template defines:

- **Structure**: Sheet layout, column definitions, row groups
- **Styles**: Pre-configured cell styles and conditional formatting
- **Formulas**: Calculation logic with parameterized cell references
- **Metadata**: Template name, version, description, and variables

## Template Structure

Templates are defined in YAML files with the following structure:

```yaml
name: monthly-budget
version: '1.0'
description: 'Monthly budget tracking template'
author: 'Finance Team'

# Template variables for customization
variables:
  month: 'January'
  year: 2026
  currency_symbol: '$'

# Sheet definitions
sheets:
  - name: 'Budget'
    columns:
      - name: 'Category'
        width: 200
      - name: 'Budgeted'
        width: 120
      - name: 'Actual'
        width: 120
      - name: 'Variance'
        width: 120

    rows:
      - cells:
          - value: '{variables.month} {variables.year} Budget'
            style: title
            merge: 4

      - cells:
          - value: 'Category'
            style: header
          - value: 'Budgeted'
            style: header
          - value: 'Actual'
            style: header
          - value: 'Variance'
            style: header

      - cells:
          - value: 'Income'
            style: category
          - value: 5000
            style: currency
          - value: 4800
            style: currency
          - formula: '=C3-B3'
            style: currency_variance

# Styles specific to this template
styles:
  title:
    extends: header_primary
    font_size: '16pt'

  category:
    extends: data
    font_weight: bold

  currency_variance:
    extends: currency
    conditional:
      - condition: 'value < 0'
        style: danger
```

## Creating Templates in YAML

### Basic Template Definition

```yaml
name: expense-report
version: '1.0.0'
description: 'Employee expense report template'
created: '2026-01-06'

# Global template settings
settings:
  theme: corporate
  default_font: 'Liberation Sans'
  page_size: letter
  orientation: portrait

# Template parameters
variables:
  employee_name: 'Employee Name'
  department: 'Department'
  report_period: 'Month/Year'

sheets:
  - name: 'Expenses'
    # Sheet configuration...
```

### Variables and Parameters

Templates can define variables that are substituted when the template is instantiated:

```yaml
variables:
  # Simple scalar values
  title: 'Q1 Report'
  year: 2026

  # Formatted values
  currency_symbol: '$'
  date_format: 'YYYY-MM-DD'

  # Lists for dynamic content
  categories:
    - 'Rent'
    - 'Utilities'
    - 'Supplies'
    - 'Marketing'

  # Nested structures
  company:
    name: 'Acme Corp'
    address: '123 Main St'
    phone: '555-1234'

# Use variables in cells
rows:
  - cells:
      - value: '{variables.title}'
      - value: '{variables.company.name}'
      - value: '{variables.currency_symbol}1,000'
```

### Column Definitions

Define column widths, styles, and data types:

```yaml
sheets:
  - name: 'Data'
    columns:
      - name: 'ID'
        width: 80
        data_type: integer
        style: data_center
        locked: true

      - name: 'Description'
        width: 300
        data_type: text
        style: data
        wrap_text: true

      - name: 'Amount'
        width: 120
        data_type: currency
        style: currency
        format: '$#,##0.00'

      - name: 'Date'
        width: 120
        data_type: date
        style: date
        format: 'YYYY-MM-DD'

      - name: 'Status'
        width: 100
        data_type: dropdown
        style: data_center
        validation:
          type: list
          values: ['Pending', 'Approved', 'Rejected']
```

### Row Groups and Sections

Organize rows into logical groups:

```yaml
sheets:
  - name: 'Report'
    row_groups:
      - name: header
        rows:
          - cells:
              - value: 'Company Name'
                style: title
                merge: 4
          - cells:
              - value: 'Report Date:'
                style: label
              - value: '{variables.date}'
                style: data

      - name: data
        repeat: true # Can be repeated with new data
        rows:
          - cells:
              - value: '{item.category}'
                style: category
              - value: '{item.amount}'
                style: currency

      - name: totals
        rows:
          - cells:
              - value: 'Grand Total:'
                style: total_label
                merge: 3
              - formula: '=SUM(B5:B100)'
                style: total_currency
```

### Formula Templates

Define formulas that adapt to the data:

```yaml
rows:
  - cells:
      # Simple formula
      - formula: '=B2+C2'
        style: currency

      # Formula with named ranges
      - formula: '=SUM(Income)'
        style: total

      # Conditional formula
      - formula: '=IF(D2>0,"Over","Under")'
        style: data_center

      # Array formula
      - formula: '=SUMPRODUCT(B2:B10, C2:C10)'
        style: currency
        array: true

      # Dynamic references using variables
      - formula: '=SUM(B{variables.start_row}:B{variables.end_row})'
        style: total
```

### Conditional Formatting

Apply conditional formatting rules:

```yaml
styles:
  budget_cell:
    extends: currency
    conditional_format:
      - condition: 'value < 0'
        style:
          font_color: '{colors.danger}'
          font_weight: bold

      - condition: 'value > 1000'
        style:
          background_color: '{colors.success|lighten:0.8}'

      - condition: 'AND(value >= 0, value <= 100)'
        style:
          background_color: '{colors.warning|lighten:0.7}'
```

## Creating Templates Programmatically

### Using TemplateBuilder

```python
from spreadsheet_dl.builders import TemplateBuilder, SheetBuilder

# Create a template
template = (
    TemplateBuilder("invoice-template")
    .version("1.0.0")
    .description("Professional invoice template")
    .variable("invoice_number", "INV-001")
    .variable("invoice_date", "2026-01-06")
    .variable("due_date", "2026-02-05")
    .variable("customer_name", "Customer Name")
    .build()
)

# Define a sheet structure
sheet = (
    SheetBuilder("Invoice")
    .column("Description", width=300)
    .column("Quantity", width=80, data_type="integer")
    .column("Unit Price", width=120, data_type="currency")
    .column("Total", width=120, data_type="currency")

    # Header section
    .row()
        .cell("INVOICE", style="title", merge=4)
    .row()
        .cell("Invoice #:")
        .cell("{variables.invoice_number}")
    .row()
        .cell("Date:")
        .cell("{variables.invoice_date}")

    # Column headers
    .row()
        .cell("Description", style="header")
        .cell("Qty", style="header")
        .cell("Price", style="header")
        .cell("Total", style="header")

    # Data rows (to be filled dynamically)
    .row_group("line_items", repeat=True)
        .cell("{item.description}", style="data")
        .cell("{item.quantity}", style="data_center")
        .cell("{item.price}", style="currency")
        .formula("=B{row}*C{row}", style="currency")

    # Total row
    .row()
        .cell("TOTAL:", style="total_label", merge=3)
        .formula("=SUM(D6:D20)", style="total_currency")

    .build()
)

template.add_sheet(sheet)
```

### Dynamic Row Generation

Generate rows based on data:

```python
from spreadsheet_dl.builders import TemplateBuilder

template = TemplateBuilder("dynamic-report").build()

# Add dynamic data rows
categories = ['Rent', 'Utilities', 'Supplies', 'Marketing']

for i, category in enumerate(categories, start=3):
    template.add_row([
        category,
        f"=Budget!B{i}",
        f"=Actual!B{i}",
        f"=C{i}-B{i}",
    ], styles=['category', 'currency', 'currency', 'currency_variance'])
```

## Template Instantiation

### From YAML File

```python
from spreadsheet_dl.template import TemplateLoader
from pathlib import Path

# Load template
loader = TemplateLoader(Path("./templates"))
template = loader.load("monthly-budget")

# Instantiate with custom variables
spreadsheet = template.instantiate({
    'month': 'March',
    'year': 2026,
    'currency_symbol': '$',
    'categories': [
        {'name': 'Housing', 'budgeted': 1500, 'actual': 1450},
        {'name': 'Food', 'budgeted': 600, 'actual': 625},
        {'name': 'Transport', 'budgeted': 300, 'actual': 275},
    ]
})

# Export to file
spreadsheet.export("budget-march.ods")
```

### With SpreadsheetBuilder

```python
from spreadsheet_dl.builder import SpreadsheetBuilder

builder = SpreadsheetBuilder(template="invoice-template")

# Override variables
builder.set_variable("invoice_number", "INV-2026-001")
builder.set_variable("customer_name", "Acme Corporation")

# Add line items
builder.add_data("line_items", [
    {"description": "Consulting Services", "quantity": 10, "price": 150},
    {"description": "Software License", "quantity": 1, "price": 500},
])

# Build and export
spreadsheet = builder.build()
spreadsheet.export("invoice-2026-001.xlsx")
```

## Template Library Organization

### Directory Structure

```
templates/
├── financial/
│   ├── invoice.yaml
│   ├── budget.yaml
│   ├── expense-report.yaml
│   └── balance-sheet.yaml
├── reports/
│   ├── monthly-summary.yaml
│   ├── quarterly-report.yaml
│   └── annual-review.yaml
├── tracking/
│   ├── time-tracker.yaml
│   ├── inventory.yaml
│   └── project-tasks.yaml
└── themes/
    ├── corporate.yaml
    └── minimal.yaml
```

### Template Metadata

Include comprehensive metadata:

```yaml
name: professional-invoice
version: '2.1.0'
description: 'Professional invoice template with payment terms and tax calculation'
author: 'Finance Team'
created: '2024-03-15'
updated: '2026-01-06'
category: financial
tags:
  - invoice
  - billing
  - accounting

# Version history
changelog:
  - version: '2.1.0'
    date: '2026-01-06'
    changes:
      - Added automatic tax calculation
      - Improved payment terms section

  - version: '2.0.0'
    date: '2025-06-01'
    changes:
      - Major redesign with new corporate theme
      - Added multi-currency support

# Dependencies
requires:
  spreadsheet_dl: '>=0.1.0'
  theme: corporate
```

## Best Practices

### 1. Use Semantic Naming

Name templates and variables clearly:

```yaml
# Good
name: employee-expense-reimbursement
variables:
  employee_name: ''
  submission_date: ''
  total_amount: 0

# Avoid
name: template1
variables:
  var1: ''
  x: ''
```

### 2. Provide Default Values

Always provide sensible defaults:

```yaml
variables:
  # Good - with defaults
  currency_symbol: '$'
  date_format: 'YYYY-MM-DD'
  page_size: 'letter'

  # Bad - empty without guidance
  value1: null
  value2: null
```

### 3. Document Variables

Add descriptions for all variables:

```yaml
variables:
  invoice_number:
    type: string
    description: 'Unique invoice identifier (e.g., INV-2026-001)'
    default: 'INV-XXXX'
    required: true

  payment_terms:
    type: integer
    description: 'Payment due days from invoice date'
    default: 30
    min: 0
    max: 90
```

### 4. Create Reusable Components

Extract common sections:

```yaml
# shared-components.yaml
components:
  company_header:
    rows:
      - cells:
          - value: '{variables.company_name}'
            style: title
            merge: 4
      - cells:
          - value: '{variables.company_address}'
            style: data
            merge: 4

# Use in templates
sheets:
  - name: 'Report'
    sections:
      - include: 'company_header'
      - include: 'data_table'
```

### 5. Validate Input Data

Define validation rules:

```yaml
variables:
  email:
    type: string
    pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

  quantity:
    type: integer
    min: 1
    max: 9999

  status:
    type: string
    enum: ['Draft', 'Submitted', 'Approved', 'Rejected']
```

## Complete Template Example

```yaml
# templates/financial/invoice.yaml
name: professional-invoice
version: '2.1.0'
description: 'Professional invoice template with tax calculation'
author: 'Finance Team'
created: '2024-03-15'

# Settings
settings:
  theme: corporate
  page_size: letter
  orientation: portrait

# Variables
variables:
  # Invoice details
  invoice_number:
    type: string
    description: 'Unique invoice number'
    default: 'INV-XXXX'

  invoice_date:
    type: date
    description: 'Invoice issue date'
    default: 'today'

  due_date:
    type: date
    description: 'Payment due date'
    default: '+30 days'

  # Company information
  company_name:
    type: string
    default: 'Your Company Name'

  company_address:
    type: string
    default: '123 Business St, City, State ZIP'

  # Customer information
  customer_name:
    type: string
    description: 'Bill to customer name'
    required: true

  customer_address:
    type: string

  # Financial settings
  tax_rate:
    type: number
    description: 'Tax rate as decimal (e.g., 0.08 for 8%)'
    default: 0.08
    min: 0
    max: 0.5

  currency_symbol:
    type: string
    default: '$'

# Sheets
sheets:
  - name: 'Invoice'
    columns:
      - { name: 'Description', width: 300 }
      - { name: 'Quantity', width: 80 }
      - { name: 'Unit Price', width: 120 }
      - { name: 'Total', width: 120 }

    sections:
      # Header
      - name: header
        rows:
          - cells:
              - value: 'INVOICE'
                style: title
                merge: 4

          - cells:
              - value: '{variables.company_name}'
                style: company_name
                merge: 4

          - cells:
              - value: '{variables.company_address}'
                style: company_info
                merge: 4

          - cells: [] # Blank row

          - cells:
              - value: 'Bill To:'
                style: label
              - value: '{variables.customer_name}'
                style: data
                merge: 3

          - cells:
              - value: ''
              - value: '{variables.customer_address}'
                style: data
                merge: 3

          - cells: [] # Blank row

          - cells:
              - value: 'Invoice #:'
                style: label
              - value: '{variables.invoice_number}'
                style: data
              - value: 'Date:'
                style: label
              - value: '{variables.invoice_date}'
                style: date

          - cells:
              - value: ''
              - value: ''
              - value: 'Due Date:'
                style: label
              - value: '{variables.due_date}'
                style: date

          - cells: [] # Blank row

      # Column Headers
      - name: column_headers
        rows:
          - cells:
              - value: 'Description'
                style: header
              - value: 'Qty'
                style: header
              - value: 'Unit Price'
                style: header
              - value: 'Total'
                style: header

      # Line Items (repeatable)
      - name: line_items
        repeat: true
        max_rows: 20
        rows:
          - cells:
              - value: '{item.description}'
                style: data
              - value: '{item.quantity}'
                style: data_center
              - value: '{item.unit_price}'
                style: currency
              - formula: '=B{row}*C{row}'
                style: currency

      # Summary
      - name: summary
        rows:
          - cells:
              - value: 'Subtotal:'
                style: subtotal_label
                merge: 3
              - formula: '=SUM(D12:D31)'
                style: subtotal

          - cells:
              - value: 'Tax ({variables.tax_rate|percent}):'
                style: subtotal_label
                merge: 3
              - formula: '=D32*{variables.tax_rate}'
                style: subtotal

          - cells:
              - value: 'TOTAL DUE:'
                style: total_label
                merge: 3
              - formula: '=D32+D33'
                style: total

          - cells: [] # Blank row

          - cells:
              - value: 'Payment Terms: Net {variables.payment_terms} days'
                style: note
                merge: 4

# Template-specific styles
styles:
  title:
    extends: header_primary
    font_size: '18pt'
    text_align: center

  company_name:
    extends: data
    font_size: '14pt'
    font_weight: bold

  company_info:
    extends: data
    font_size: '10pt'

  label:
    extends: data
    font_weight: bold

  subtotal_label:
    extends: total_label
    font_size: '11pt'

  subtotal:
    extends: currency
    border_top: '1pt solid {colors.border}'

  note:
    extends: data
    font_size: '9pt'
    font_italic: true
```

## See Also

- [Theme Creation Guide](./theme-creation.md) - Creating custom themes
- [Style Composition Guide](./style-composition.md) - Composing styles
- [Builder API Reference](../api/builder.md) - Programmatic building
- [Best Practices](./best-practices.md) - General best practices
