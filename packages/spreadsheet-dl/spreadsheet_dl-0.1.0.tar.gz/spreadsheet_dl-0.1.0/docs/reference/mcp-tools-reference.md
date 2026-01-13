# MCP Tools Reference

SpreadsheetDL provides a comprehensive Model Context Protocol (MCP) server with 50+ tools for AI-assisted spreadsheet manipulation. This reference documents all available tools organized by category.

## Quick Navigation

- [Spreadsheet Operations](#spreadsheet-operations)
- [Cell and Range Operations](#cell-and-range-operations)
- [Sheet Management](#sheet-management)
- [Workbook Operations](#workbook-operations)
- [Formula Operations](#formula-operations)
- [Data Operations](#data-operations)
- [Chart Operations](#chart-operations)
- [Conditional Formatting](#conditional-formatting)
- [Data Validation](#data-validation)
- [Named Ranges and Tables](#named-ranges-and-tables)
- [Import Operations](#import-operations)
- [Export Operations](#export-operations)
- [Theme and Styling](#theme-and-styling)
- [Query Operations](#query-operations)

---

## Spreadsheet Operations

### spreadsheet_create

Create a new spreadsheet file.

**Parameters:**

| Parameter   | Type   | Required | Description                  |
| ----------- | ------ | -------- | ---------------------------- |
| `file_path` | string | Yes      | Path for the new spreadsheet |
| `sheets`    | array  | No       | Initial sheet specifications |
| `title`     | string | No       | Document title               |
| `author`    | string | No       | Document author              |

**Example:**

```json
{
  "file_path": "/documents/budget.ods",
  "sheets": [{ "name": "Budget", "columns": ["Item", "Amount"] }],
  "title": "Monthly Budget"
}
```

### spreadsheet_read

Read spreadsheet contents.

**Parameters:**

| Parameter   | Type   | Required | Description                    |
| ----------- | ------ | -------- | ------------------------------ |
| `file_path` | string | Yes      | Path to the spreadsheet        |
| `sheet`     | string | No       | Sheet name (defaults to first) |
| `range`     | string | No       | Cell range (e.g., "A1:D10")    |

**Returns:** JSON with sheet data, cell values, and metadata.

### spreadsheet_info

Get spreadsheet metadata and structure.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

**Returns:** Sheet names, row/column counts, file size, creation date.

---

## Cell and Range Operations

### cell_write

Write value to a specific cell.

**Parameters:**

| Parameter   | Type   | Required | Description                 |
| ----------- | ------ | -------- | --------------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet     |
| `sheet`     | string | Yes      | Target sheet name           |
| `cell`      | string | Yes      | Cell reference (e.g., "A1") |
| `value`     | any    | Yes      | Value to write              |
| `formula`   | string | No       | Formula instead of value    |

### cell_read

Read value from a specific cell.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `sheet`     | string | Yes      | Sheet name              |
| `cell`      | string | Yes      | Cell reference          |

### range_write

Write values to a range of cells.

**Parameters:**

| Parameter   | Type   | Required | Description                      |
| ----------- | ------ | -------- | -------------------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet          |
| `sheet`     | string | Yes      | Target sheet name                |
| `range`     | string | Yes      | Range reference (e.g., "A1:C10") |
| `values`    | array  | Yes      | 2D array of values               |

### range_read

Read values from a range of cells.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `sheet`     | string | Yes      | Sheet name              |
| `range`     | string | Yes      | Range reference         |

### range_format

Apply formatting to a range.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `sheet`     | string | Yes      | Sheet name              |
| `range`     | string | Yes      | Range reference         |
| `format`    | object | Yes      | Format specification    |

**Format options:** `bold`, `italic`, `font_size`, `font_color`, `background`, `border`, `alignment`, `number_format`

---

## Sheet Management

### sheet_create

Create a new sheet in the workbook.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `name`      | string | Yes      | New sheet name          |
| `position`  | number | No       | Position index          |
| `columns`   | array  | No       | Column headers          |

### sheet_rename

Rename an existing sheet.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `old_name`  | string | Yes      | Current sheet name      |
| `new_name`  | string | Yes      | New sheet name          |

### sheet_delete

Delete a sheet from the workbook.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `name`      | string | Yes      | Sheet name to delete    |

### sheet_copy

Copy a sheet within or between workbooks.

**Parameters:**

| Parameter     | Type   | Required | Description                |
| ------------- | ------ | -------- | -------------------------- |
| `file_path`   | string | Yes      | Source spreadsheet path    |
| `sheet`       | string | Yes      | Sheet name to copy         |
| `new_name`    | string | Yes      | Name for the copy          |
| `target_file` | string | No       | Target file (if different) |

### sheet_list

List all sheets in a workbook.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

---

## Workbook Operations

### workbook_properties_get

Get workbook properties and metadata.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

### workbook_properties_set

Set workbook properties.

**Parameters:**

| Parameter    | Type   | Required | Description             |
| ------------ | ------ | -------- | ----------------------- |
| `file_path`  | string | Yes      | Path to the spreadsheet |
| `properties` | object | Yes      | Properties to set       |

**Properties:** `title`, `author`, `subject`, `keywords`, `description`, `created`, `modified`

### workbook_statistics

Get comprehensive workbook statistics.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

**Returns:** Total rows, columns, cells, formulas, charts, named ranges.

### workbooks_compare

Compare two workbooks and report differences.

**Parameters:**

| Parameter    | Type   | Required | Description             |
| ------------ | ------ | -------- | ----------------------- |
| `file_path1` | string | Yes      | First spreadsheet path  |
| `file_path2` | string | Yes      | Second spreadsheet path |

### workbooks_merge

Merge multiple workbooks into one.

**Parameters:**

| Parameter     | Type   | Required | Description               |
| ------------- | ------ | -------- | ------------------------- |
| `output_path` | string | Yes      | Output file path          |
| `sources`     | array  | Yes      | List of source file paths |

---

## Formula Operations

### formulas_recalculate

Force recalculation of all formulas.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

### formulas_audit

Audit formulas for errors and dependencies.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

**Returns:** Formula list, error cells, dependency graph.

### circular_refs_find

Find circular references in formulas.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

---

## Data Operations

### data_connections_list

List all external data connections.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

### data_refresh

Refresh external data connections.

**Parameters:**

| Parameter         | Type   | Required | Description                    |
| ----------------- | ------ | -------- | ------------------------------ |
| `file_path`       | string | Yes      | Path to the spreadsheet        |
| `connection_name` | string | No       | Specific connection to refresh |

### links_update

Update external links in the workbook.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

### links_break

Break external links (convert to values).

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

---

## Chart Operations

### chart_create

Create a new chart.

**Parameters:**

| Parameter    | Type   | Required | Description                         |
| ------------ | ------ | -------- | ----------------------------------- |
| `file_path`  | string | Yes      | Path to the spreadsheet             |
| `sheet`      | string | Yes      | Target sheet                        |
| `chart_type` | string | Yes      | Type: bar, line, pie, area, scatter |
| `data_range` | string | Yes      | Data source range                   |
| `title`      | string | No       | Chart title                         |
| `position`   | string | No       | Anchor cell                         |
| `width`      | number | No       | Chart width in cells                |
| `height`     | number | No       | Chart height in cells               |

**Chart types:** `bar`, `column`, `line`, `pie`, `area`, `scatter`, `radar`, `stock`

### chart_update

Update chart properties.

**Parameters:**

| Parameter    | Type   | Required | Description             |
| ------------ | ------ | -------- | ----------------------- |
| `file_path`  | string | Yes      | Path to the spreadsheet |
| `sheet`      | string | Yes      | Sheet containing chart  |
| `chart_id`   | string | Yes      | Chart identifier        |
| `properties` | object | Yes      | Properties to update    |

---

## Conditional Formatting

### cf_create

Create conditional formatting rule.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `sheet`     | string | Yes      | Target sheet            |
| `range`     | string | Yes      | Range to format         |
| `rule_type` | string | Yes      | Type of rule            |
| `config`    | object | Yes      | Rule configuration      |

**Rule types:**

- `color_scale` - Gradient colors based on values
- `data_bar` - Horizontal bars in cells
- `icon_set` - Icons based on value thresholds
- `cell_value` - Format based on cell value comparison
- `formula` - Format based on custom formula

**Example:**

```json
{
  "file_path": "/docs/data.ods",
  "sheet": "Sales",
  "range": "B2:B100",
  "rule_type": "color_scale",
  "config": {
    "min_color": "#FF0000",
    "mid_color": "#FFFF00",
    "max_color": "#00FF00"
  }
}
```

---

## Data Validation

### validation_create

Create data validation rule.

**Parameters:**

| Parameter         | Type   | Required | Description              |
| ----------------- | ------ | -------- | ------------------------ |
| `file_path`       | string | Yes      | Path to the spreadsheet  |
| `sheet`           | string | Yes      | Target sheet             |
| `range`           | string | Yes      | Range to validate        |
| `validation_type` | string | Yes      | Type of validation       |
| `config`          | object | Yes      | Validation configuration |

**Validation types:**

- `list` - Dropdown list of values
- `number` - Numeric constraints
- `date` - Date constraints
- `text_length` - Text length limits
- `custom` - Custom formula validation

---

## Named Ranges and Tables

### named_range_create

Create a named range.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `name`      | string | Yes      | Range name              |
| `sheet`     | string | Yes      | Sheet containing range  |
| `range`     | string | Yes      | Cell range              |

### table_create

Create a structured table.

**Parameters:**

| Parameter     | Type    | Required | Description             |
| ------------- | ------- | -------- | ----------------------- |
| `file_path`   | string  | Yes      | Path to the spreadsheet |
| `sheet`       | string  | Yes      | Target sheet            |
| `range`       | string  | Yes      | Table range             |
| `name`        | string  | No       | Table name              |
| `has_headers` | boolean | No       | First row as headers    |

---

## Import Operations

### csv_import

Import data from CSV file.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Output spreadsheet path |
| `csv_path`  | string | Yes      | Source CSV file         |
| `sheet`     | string | No       | Target sheet name       |
| `delimiter` | string | No       | Field delimiter         |
| `encoding`  | string | No       | File encoding           |

### tsv_import

Import data from TSV file.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Output spreadsheet path |
| `tsv_path`  | string | Yes      | Source TSV file         |

### json_import

Import data from JSON file.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Output spreadsheet path |
| `json_path` | string | Yes      | Source JSON file        |

### xlsx_import

Import data from XLSX file.

**Parameters:**

| Parameter   | Type   | Required | Description      |
| ----------- | ------ | -------- | ---------------- |
| `file_path` | string | Yes      | Output ODS path  |
| `xlsx_path` | string | Yes      | Source XLSX file |

### format_auto_detect

Auto-detect file format.

**Parameters:**

| Parameter   | Type   | Required | Description     |
| ----------- | ------ | -------- | --------------- |
| `file_path` | string | Yes      | File to analyze |

**Returns:** Detected format, encoding, delimiter (if applicable).

### batch_import

Import multiple files at once.

**Parameters:**

| Parameter   | Type   | Required | Description               |
| ----------- | ------ | -------- | ------------------------- |
| `file_path` | string | Yes      | Output spreadsheet path   |
| `sources`   | array  | Yes      | List of source file paths |

---

## Export Operations

### csv_export

Export spreadsheet to CSV.

**Parameters:**

| Parameter     | Type   | Required | Description             |
| ------------- | ------ | -------- | ----------------------- |
| `file_path`   | string | Yes      | Source spreadsheet path |
| `output_path` | string | Yes      | Output CSV path         |
| `sheet`       | string | No       | Sheet to export         |
| `delimiter`   | string | No       | Field delimiter         |

### tsv_export

Export spreadsheet to TSV.

**Parameters:**

| Parameter     | Type   | Required | Description             |
| ------------- | ------ | -------- | ----------------------- |
| `file_path`   | string | Yes      | Source spreadsheet path |
| `output_path` | string | Yes      | Output TSV path         |

### json_export

Export spreadsheet to JSON.

**Parameters:**

| Parameter     | Type   | Required | Description                       |
| ------------- | ------ | -------- | --------------------------------- |
| `file_path`   | string | Yes      | Source spreadsheet path           |
| `output_path` | string | Yes      | Output JSON path                  |
| `format`      | string | No       | JSON structure (records, columns) |

### xlsx_export

Export ODS to XLSX format.

**Parameters:**

| Parameter     | Type   | Required | Description      |
| ------------- | ------ | -------- | ---------------- |
| `file_path`   | string | Yes      | Source ODS path  |
| `output_path` | string | Yes      | Output XLSX path |

### html_export

Export spreadsheet to HTML.

**Parameters:**

| Parameter        | Type    | Required | Description             |
| ---------------- | ------- | -------- | ----------------------- |
| `file_path`      | string  | Yes      | Source spreadsheet path |
| `output_path`    | string  | Yes      | Output HTML path        |
| `include_styles` | boolean | No       | Include CSS styling     |

### pdf_export

Export spreadsheet to PDF.

**Parameters:**

| Parameter     | Type   | Required | Description             |
| ------------- | ------ | -------- | ----------------------- |
| `file_path`   | string | Yes      | Source spreadsheet path |
| `output_path` | string | Yes      | Output PDF path         |
| `page_size`   | string | No       | Page size (letter, a4)  |
| `orientation` | string | No       | portrait or landscape   |

### batch_export

Export to multiple formats at once.

**Parameters:**

| Parameter    | Type   | Required | Description             |
| ------------ | ------ | -------- | ----------------------- |
| `file_path`  | string | Yes      | Source spreadsheet path |
| `output_dir` | string | Yes      | Output directory        |
| `format`     | string | Yes      | Target format           |

---

## Theme and Styling

### theme_list

List available themes.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |

### theme_get

Get theme details.

**Parameters:**

| Parameter    | Type   | Required | Description             |
| ------------ | ------ | -------- | ----------------------- |
| `file_path`  | string | Yes      | Path to the spreadsheet |
| `theme_name` | string | Yes      | Theme name              |

### theme_create

Create a custom theme.

**Parameters:**

| Parameter    | Type   | Required | Description             |
| ------------ | ------ | -------- | ----------------------- |
| `file_path`  | string | Yes      | Path to the spreadsheet |
| `theme_name` | string | Yes      | New theme name          |
| `properties` | object | Yes      | Theme properties        |

### theme_apply

Apply a theme to the workbook.

**Parameters:**

| Parameter    | Type   | Required | Description             |
| ------------ | ------ | -------- | ----------------------- |
| `file_path`  | string | Yes      | Path to the spreadsheet |
| `theme_name` | string | Yes      | Theme to apply          |

### color_scheme_generate

Generate a color scheme.

**Parameters:**

| Parameter     | Type   | Required | Description      |
| ------------- | ------ | -------- | ---------------- |
| `base_color`  | string | Yes      | Base color (hex) |
| `scheme_type` | string | No       | Type of scheme   |

**Scheme types:** `monochromatic`, `complementary`, `analogous`, `triadic`, `split_complementary`

---

## Query Operations

### query_select

Execute a query on spreadsheet data.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `sheet`     | string | Yes      | Sheet to query          |
| `query`     | string | Yes      | SQL-like query string   |

**Example:**

```json
{
  "file_path": "/data/sales.ods",
  "sheet": "Transactions",
  "query": "SELECT Product, SUM(Amount) WHERE Region = 'North' GROUP BY Product"
}
```

### query_find

Find rows matching criteria.

**Parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `file_path` | string | Yes      | Path to the spreadsheet |
| `sheet`     | string | Yes      | Sheet to search         |
| `criteria`  | object | Yes      | Search criteria         |

**Example:**

```json
{
  "file_path": "/data/inventory.ods",
  "sheet": "Products",
  "criteria": {
    "Category": "Electronics",
    "Stock": { "$lt": 10 }
  }
}
```

---

## Usage with Claude Desktop

To use these tools with Claude Desktop, add SpreadsheetDL to your MCP configuration:

```json
{
  "mcpServers": {
    "spreadsheet-dl": {
      "command": "spreadsheet-dl-mcp",
      "args": ["--allowed-paths", "/home/user/documents"]
    }
  }
}
```

## Security

The MCP server enforces path-based security:

- Only paths in `--allowed-paths` are accessible
- File operations are validated before execution
- Input sanitization prevents injection attacks

## See Also

- [Formula Reference](formula-reference.md)
- [MCP Server API](../api/_mcp/server.md)
- [Claude Desktop Integration](../tutorials/05-use-mcp-tools.md)
