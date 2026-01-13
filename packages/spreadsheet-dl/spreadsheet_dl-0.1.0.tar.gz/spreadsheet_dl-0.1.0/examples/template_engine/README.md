# Template Engine Examples

Advanced examples demonstrating the SpreadsheetDL template engine for creating reusable, parameterized spreadsheet templates.

## Overview

The template engine enables creating spreadsheet templates with variable substitution, conditional rendering, and component composition - similar to Jinja2 but optimized for spreadsheets.

## Examples in This Directory

1. **01_basic_loading.py** - Load and render YAML templates
2. **02_variable_substitution.py** - Use variables in templates
3. **03_conditional_rendering.py** - Conditional logic in templates
4. **04_component_composition.py** - Reusable components
5. **05_complete_template.py** - Full template workflow
6. **06_builtin_functions.py** - Built-in template functions
7. **07_custom_template.py** - Create custom templates
8. **08_error_handling.py** - Template validation and errors
9. **run_all.py** - Run all template examples

## Quick Start

Run all examples:

```bash
python run_all.py
```

Run individual examples:

```bash
python 01_basic_loading.py
python 02_variable_substitution.py
```

## Key Features

- **YAML-based templates** - Define templates in YAML format
- **Variable substitution** - `{{ variable }}` syntax
- **Conditional rendering** - Show/hide based on conditions
- **Component reuse** - Define once, use many times
- **Built-in functions** - Date formatting, calculations, etc.
- **Type safety** - Validated schemas

## When to Use Templates

Templates are ideal when you need to:

- Generate similar spreadsheets with different data
- Maintain consistency across multiple reports
- Separate structure from content
- Enable non-programmers to create spreadsheets

## Template Structure

```yaml
name: 'Budget Template'
sheets:
  - name: 'Summary'
    rows:
      - cells:
          - value: '{{ title }}'
            style: header
      - cells:
          - value: 'Total: {{ total }}'
```

## See Also

- Template engine documentation: `../../docs/api/template_engine.md`
- Schema documentation: `../../docs/api/template_engine.md#schema`
- Main examples: `../README.md`
