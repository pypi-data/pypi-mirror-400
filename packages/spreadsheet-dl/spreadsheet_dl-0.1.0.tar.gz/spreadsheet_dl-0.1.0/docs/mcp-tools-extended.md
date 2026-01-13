# Extended MCP Tools Documentation

**Universal Spreadsheet MCP Tools**

This document details the MCP tools available in SpreadsheetDL for universal spreadsheet manipulation. The MCP server provides 8 categories of tools focused on spreadsheet operations.

## Overview

SpreadsheetDL provides comprehensive MCP tools for spreadsheet manipulation. All tools are exposed via the Model Context Protocol (MCP), enabling natural language interaction through Claude and other MCP-compatible clients.

## Architecture Change Notice

**Domain-Specific APIs Available via Python**: Budget analysis, account management, goal tracking, and reporting functionality are available through Python APIs (BudgetAnalyzer, AccountManager, GoalManager, ReportGenerator) but are not exposed as MCP tools. This architectural decision keeps MCP tools focused on universal spreadsheet operations while domain-specific workflows use the Python APIs directly.

## Tool Categories

### 1. Workbook Operations (16 tools)

Complete workbook-level operations for properties, protection, and analysis.

#### Properties & Metadata

- **workbook_properties_get** - Get workbook properties and metadata
- **workbook_properties_set** - Set workbook properties
- **workbook_metadata_get** - Get detailed workbook metadata
- **workbook_metadata_set** - Update workbook metadata

#### Protection

- **workbook_protection_enable** - Enable workbook-level protection
- **workbook_protection_disable** - Disable workbook protection

#### Formula Management

- **formulas_recalculate** - Recalculate all formulas in the workbook
- **formulas_audit** - Audit formulas for errors and warnings
- **circular_refs_find** - Detect circular references

#### External Links

- **links_update** - Update external links
- **links_break** - Break external links and convert to values

#### Data Connections

- **data_connections_list** - List all data connections
- **data_refresh** - Refresh data from external sources

#### Workbook Analysis

- **workbooks_compare** - Compare two workbooks for differences
- **workbooks_merge** - Merge multiple workbooks
- **workbook_statistics** - Get comprehensive workbook statistics

### 2. Theme Management (12 tools)

Professional theming and style management.

#### Theme Operations

- **theme_list** - List all available themes
- **theme_get** - Get details of a specific theme
- **theme_create** - Create a new custom theme
- **theme_update** - Update an existing theme
- **theme_delete** - Delete a custom theme
- **theme_apply** - Apply a theme to the workbook

#### Theme Import/Export

- **theme_export** - Export theme definition to file
- **theme_import** - Import theme from file
- **theme_preview** - Preview theme appearance

#### Advanced Theming

- **color_scheme_generate** - Generate harmonious color schemes
- **font_set_apply** - Apply coordinated font sets
- **style_guide_create** - Create comprehensive style guide

### 3. Print Layout (10 tools)

Complete print and PDF export functionality.

#### Page Setup

- **page_setup** - Configure page layout, orientation, margins
- **print_area_set** - Define print area for sheets
- **pages_fit_to** - Fit content to specific number of pages

#### Page Breaks

- **page_breaks_insert** - Insert manual page breaks
- **page_breaks_remove** - Remove page breaks

#### Headers & Footers

- **header_footer_set** - Set header and footer content
- **print_titles_set** - Set rows/columns to repeat on each page

#### Print Options

- **print_options_set** - Configure gridlines, quality, etc.
- **print_preview** - Generate print preview
- **pdf_export** - Export sheet to PDF format

### 4. Import/Export Operations (17 tools)

Comprehensive data import/export across multiple formats.

#### Import Tools

- **csv_import** - Import data from CSV files
- **tsv_import** - Import data from TSV files
- **json_import** - Import data from JSON files
- **xlsx_import** - Import data from XLSX files
- **xml_import** - Import data from XML files
- **html_import** - Import data from HTML tables

#### Export Tools

- **csv_export** - Export sheet to CSV format
- **tsv_export** - Export sheet to TSV format
- **json_export** - Export sheet to JSON format
- **xlsx_export** - Export to XLSX format
- **xml_export** - Export to XML format
- **html_export** - Export to HTML table
- **pdf_export** - Export to PDF (also in Print Layout)

#### Batch Operations

- **batch_import** - Import from multiple files
- **batch_export** - Export to multiple formats

#### Advanced Import

- **data_mapping_create** - Create data mapping schemas
- **column_mapping_apply** - Apply column mappings
- **format_auto_detect** - Auto-detect file formats

## Implementation Status

### Universal Spreadsheet Tools

Core spreadsheet manipulation tools are fully implemented:

- **Cell Operations** (11 tools): cell_get, cell_set, cell_batch_get, etc.
- **Style Operations** (11 tools): style_list, format_cells, format_number, etc.
- **Structure Operations** (11 tools): row_insert, column_hide, freeze_set, etc.
- **Advanced Operations** (8 tools): chart_create, validation_create, etc.

### Extended Tools (Documented Stubs)

Extended tools have well-documented stub implementations:

- **Workbook Operations** (16 tools)
- **Theme Management** (12 tools)
- **Print Layout** (10 tools)
- **Import/Export** (17 tools)

These stubs:

- Accept correct parameters with full validation
- Return appropriate JSON schema responses
- Include clear "Stub: [feature] not yet implemented" messages

- Ready for full implementation

## Usage Examples

### Python API - Universal Spreadsheet Operations

```python
from spreadsheet_dl.mcp_server import MCPServer, MCPConfig
from pathlib import Path

# Create server
config = MCPConfig(
    allowed_paths=[Path("~/Documents")],
    rate_limit_per_minute=60,
)
server = MCPServer(config)

# Get workbook properties
result = server._handle_workbook_properties_get("/path/to/file.ods")
print(result.content)

# Get cell value
result = server._handle_cell_get("/path/to/file.ods", "Sheet1", "A1")
print(result.content)

# Apply style to range
result = server._handle_style_apply("/path/to/file.ods", "Sheet1", "A1:E1", "header")
print(result.content)
```

### Python API - Domain-Specific Operations

For budget analysis, account management, and reporting, use the Python APIs directly:

```python
from spreadsheet_dl.budget_analyzer import BudgetAnalyzer
from spreadsheet_dl.report_generator import ReportGenerator

# Analyze budget
analyzer = BudgetAnalyzer("/path/to/budget.ods")
analysis = analyzer.analyze()
print(f"Total spent: ${analysis.total_spent:,.2f}")

# Generate report
generator = ReportGenerator("/path/to/budget.ods")
report = generator.generate_monthly_report(format="markdown")
print(report)
```

### MCP Protocol (via Claude Desktop)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "workbook_properties_get",
    "arguments": {
      "file_path": "/home/user/budget.ods"
    }
  }
}
```

### Natural Language (via Claude)

With MCP integration for universal spreadsheet operations:

- "Show me the properties of my budget workbook"
- "Get the value of cell A1 in Sheet1"
- "Apply the header style to the first row"
- "Export this sheet to PDF"
- "What themes are available?"
- "Insert 3 rows above row 10"
- "Create a chart from data in A1:D10"

## Tool Categories Summary

| Category             | Tool Count | Implementation Status |
| -------------------- | ---------- | --------------------- |
| Cell Operations      | 11         | Fully Implemented     |
| Style Operations     | 11         | Fully Implemented     |
| Structure Operations | 11         | Fully Implemented     |
| Advanced Operations  | 8          | Fully Implemented     |
| Workbook Operations  | 16         | Documented Stubs      |
| Theme Management     | 12         | Documented Stubs      |
| Print Layout         | 10         | Documented Stubs      |
| Import/Export        | 17         | Documented Stubs      |
| **Total**            | **96**     | **41 + 55**           |

**Note**: Domain-specific functionality (budget analysis, account management, goal tracking, reporting) is available via Python APIs, not MCP tools.

## Architecture

### Tool Registry

All tools are managed through `MCPToolRegistry`:

```python
registry = MCPToolRegistry()

# Tools are categorized
categories = registry.get_categories()
# ['cell_operations', 'workbook_operations', ...]

# Get tools by category
workbook_tools = registry.get_tools_by_category("workbook_operations")
# Returns list of 16 workbook operation tools
```

### Handler Pattern

Each tool has a corresponding handler method:

```python
def _handle_workbook_properties_get(self, file_path: str) -> MCPToolResult:
    """
    Get workbook properties and metadata.

    Stub implementation.

    Args:
        file_path: Path to spreadsheet file

    Returns:
        Workbook properties
    """
    try:
        path = self._validate_path(file_path)
        return MCPToolResult.json({
            "success": True,
            "file": str(path),
            "properties": {...},
            "message": "Stub: Full implementation pending"
        })
    except Exception as e:
        return MCPToolResult.error(str(e))
```

## Security

All tools enforce security measures:

- **Path Validation**: Only allowed paths accessible
- **Rate Limiting**: 60 requests/minute default
- **Audit Logging**: All tool invocations logged
- **Error Handling**: Safe error responses without data leaks

## Testing

Comprehensive test coverage:

- **test_mcp_server.py** (226 tests): Original tool tests
- **test_mcp_tools_extended.py** (36 tests): New tool category tests

All 18 tools verified for:

- Proper registration
- Handler existence
- Parameter validation
- Return value schemas
- Error handling

## References

- **IR-MCP-002**: Native MCP Server requirement
- **MCP Specification**: https://modelcontextprotocol.io/

## Version History

- **v0.1.0** (2026-01-04): First public release with 96 universal spreadsheet MCP tools across 8 categories
