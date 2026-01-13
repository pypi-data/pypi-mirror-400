# Tutorial 5: Use MCP Tools

Learn how to use SpreadsheetDL's Model Context Protocol (MCP) server for AI-powered spreadsheet operations with Claude and other AI assistants.

## What You'll Learn

- Set up the MCP server
- Connect from Claude Desktop
- Use natural language for spreadsheet operations
- Automate complex workflows
- Analyze budgets with AI assistance

## Prerequisites

- SpreadsheetDL installed
- Claude Desktop app (for Claude integration)
- Basic understanding of spreadsheets
- Completed [Tutorial 1: Create a Budget](01-create-budget.md)

## What is MCP?

Model Context Protocol (MCP) is Anthropic's standard for AI-tool integration. SpreadsheetDL's MCP server exposes universal spreadsheet operations as tools that AI assistants like Claude can use.

**Benefits:**

- Natural language spreadsheet manipulation
- Cell operations via conversational interface
- Style and formatting through AI assistance
- Structure modifications (rows, columns, sheets)
- Advanced features (charts, validation, formulas)

**Architecture Note**: Domain-specific features (budget analysis, account management, reporting) are available via Python APIs, not MCP tools. This keeps MCP focused on universal spreadsheet operations.

## Step 1: Start the MCP Server

Launch the SpreadsheetDL MCP server:

```bash
# Start server on default port (3000)
spreadsheet-dl mcp-server

# Or specify custom port
spreadsheet-dl mcp-server --port 3001

# With specific capabilities
spreadsheet-dl mcp-server --enable-write --enable-ai-analysis
```

Output:

```
SpreadsheetDL MCP Server v0.1.0
===============================
Server running on: http://localhost:3000
Tools available: 96
Categories: 8 (cell, style, structure, workbook, theme, print, import/export, advanced)

Press Ctrl+C to stop
```

## Step 2: Configure Claude Desktop

Add SpreadsheetDL to Claude Desktop's MCP configuration:

1. Open Claude Desktop settings
2. Navigate to "Developer" → "Edit Config"
3. Add SpreadsheetDL configuration:

```json
{
  "mcpServers": {
    "spreadsheet-dl": {
      "command": "spreadsheet-dl",
      "args": ["mcp-server"],
      "env": {
        "SPREADSHEET_DIR": "/home/user/budgets"
      }
    }
  }
}
```

1. Restart Claude Desktop
2. Verify connection (you'll see "spreadsheet-dl" in available tools)

## Step 3: Manipulate Spreadsheets with Natural Language

Once connected, ask Claude to work with spreadsheet data:

**Example 1: Reading Cell Values**

> Get the values from cells A1 through E1 in my family_budget.ods file.

Claude will use the MCP cell_batch_get tool to retrieve the values.

**Example 2: Styling Cells**

> Make the first row of my budget spreadsheet bold with a blue background.

Claude will use style formatting tools to apply the requested styling.

**Example 3: Structural Changes**

> Insert 3 blank rows above row 10 in Sheet1.

Claude will use the row_insert tool with the appropriate parameters.

## Step 4: Work with Spreadsheet Data

Ask Claude to help with data operations:

**Example: Finding Data**

> Find all cells in Sheet1 that contain the word "Total".

Claude will use the cell_find tool to locate matching cells.

**Example: Creating Charts**

> Create a bar chart from the data in cells A1:D10 in my budget file.

Claude will use the chart_create tool with the appropriate data range.

**Example: Data Validation**

> Add data validation to column C so it only accepts numbers between 0 and 10000.

Claude will use the validation_create tool to set up the constraint.

## Step 5: Export and Import Data

**Example: Export to Different Formats**

> Export my budget spreadsheet to Excel format as budget_2026.xlsx.

Claude will use the export tools to convert the file.

**Example: Import CSV Data**

> Import the data from transactions.csv into a new sheet called "Transactions".

Claude will use the import_csv tool to load the data.

**Note**: For domain-specific reporting (budget analysis, spending summaries), use the Python API directly:

```python
from spreadsheet_dl.report_generator import ReportGenerator

generator = ReportGenerator("budget_2026_01.ods")
report = generator.generate_monthly_report(format="markdown")
print(report)
```

## Step 6: Apply Themes and Styling

**Example: Apply a Theme**

> Apply the corporate theme to my budget spreadsheet.

Claude will use the theme_apply tool to change the overall appearance.

**Example: Custom Styling**

> Create a custom style called "warning" with yellow background and red text, then apply it to cells that are over budget.

Claude will use style_create and style_apply to set up and use the custom style.

## Available MCP Tools

The SpreadsheetDL MCP server provides 96 universal spreadsheet tools across 8 categories:

| Category             | Tools | Example Use                             |
| -------------------- | ----- | --------------------------------------- |
| Cell Operations      | 11    | "Get cell A1", "Set B5 to 100"          |
| Style Operations     | 11    | "Make row 1 bold", "Apply header style" |
| Structure Operations | 11    | "Insert 3 rows", "Hide column D"        |
| Advanced Operations  | 8     | "Create chart", "Add validation"        |
| Workbook Operations  | 16    | "Get workbook properties"               |
| Theme Management     | 12    | "Apply corporate theme"                 |
| Print Layout         | 10    | "Export to PDF"                         |
| Import/Export        | 17    | "Import CSV", "Export to Excel"         |

**Domain-Specific APIs (use Python directly):**

- `BudgetAnalyzer` - Budget analysis and spending insights
- `AccountManager` - Multi-account tracking
- `GoalManager` - Financial goal planning
- `ReportGenerator` - Comprehensive financial reports

## Example Workflows

### Workflow 1: Formatting a Budget Spreadsheet

Prompt to Claude:

> I have a budget spreadsheet at budget_2026_02.ods. Please:
>
> 1. Make the first row bold with a dark blue background
> 2. Apply number formatting to column C (currency with 2 decimals)
> 3. Add borders around the data range A1:E20
> 4. Freeze the first row so it stays visible when scrolling
> 5. Apply the minimal theme to the entire sheet

Claude will use MCP tools (style_apply, format_number, format_border, freeze_set, theme_apply) to complete these tasks.

### Workflow 2: Import and Organize Data

> I've downloaded my bank transactions as chase_jan.csv. Please:
>
> 1. Import the CSV into a new sheet called "Transactions"
> 2. Apply the header style to the first row
> 3. Add data validation to the Amount column (numbers only)
> 4. Create a chart showing spending by category

For analysis and categorization, use the Python API:

```python
from spreadsheet_dl.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("budget_with_transactions.ods")
analysis = analyzer.analyze()
print(f"Total spending: ${analysis.total_spent:,.2f}")
print(f"By category: {analysis.by_category}")
```

### Workflow 3: Export and Share

> It's month-end. For my January 2026 budget, please:
>
> 1. Export the main sheet to Excel format for sharing
> 2. Create a PDF of the summary page for printing
> 3. Export the raw data to CSV for backup

For comprehensive reporting and analysis, use the Python API:

```python
from spreadsheet_dl.report_generator import ReportGenerator

generator = ReportGenerator("budget_2026_01.ods")

# Generate markdown report
md_report = generator.generate_monthly_report(format="markdown")
print(md_report)

# Generate HTML dashboard
html_dashboard = generator.generate_dashboard(format="html")
with open("budget_dashboard.html", "w") as f:
    f.write(html_dashboard)
```

## Python API for MCP

You can also use the MCP server from Python:

```python
from spreadsheet_dl import MCPServer, MCPConfig

# Create MCP server
config = MCPConfig(
    port=3000,
    host="localhost",
    enable_write=True,
    enable_ai_analysis=True
)

server = MCPServer(config)

# Start server
server.start()

# Server runs until stopped
# Access via Claude Desktop or other MCP clients
```

## Advanced: Custom MCP Tools

Create custom MCP tools for specialized workflows:

```python
from spreadsheet_dl import MCPServer, MCPTool

# Define custom tool
class CustomBudgetTool(MCPTool):
    name = "create_zero_based_budget"
    description = "Create a zero-based budget where every dollar is allocated"

    def execute(self, income: float, **kwargs):
        """Create budget with all income allocated."""
        # Implementation here
        pass

# Add to server
server = MCPServer()
server.register_tool(CustomBudgetTool())
server.start()
```

## Security Considerations

1. **Local Only** - MCP server runs locally by default
2. **Authentication** - Configure auth tokens for remote access
3. **File Permissions** - Server respects OS file permissions
4. **Audit Logging** - All operations logged

**Enable authentication:**

```bash
# Start with auth token
export MCP_AUTH_TOKEN="your-secret-token"
spreadsheet-dl mcp-server --require-auth
```

## Troubleshooting

**Claude Desktop can't connect?**

- Verify server is running: `curl http://localhost:3000/health`
- Check config path in Claude Desktop settings
- Restart Claude Desktop after config changes

**Tools not appearing?**

- Ensure server started successfully
- Check Claude Desktop Developer Console for errors
- Verify MCP protocol version compatibility

**Permission errors?**

- Check `SPREADSHEET_DIR` environment variable
- Ensure write permissions to output directory
- Run server with appropriate user permissions

## Best Practices

1. **Start Simple** - Begin with basic operations, progress to complex
2. **Be Specific** - Provide clear instructions to AI assistant
3. **Verify Results** - Check generated spreadsheets
4. **Iterate** - Refine prompts based on results
5. **Use Templates** - Reference existing templates in prompts

## Example Prompts

**Cell Operations:**

- "Get the value from cell B5"
- "Set cells A1 through A10 to the values from this list: [...]"
- "Find all cells containing 'TOTAL'"
- "Copy the range A1:D10 to E1:H10"

**Formatting:**

- "Make the header row bold and centered"
- "Apply currency formatting to column C"
- "Add borders around the data table"
- "Create a style called 'highlight' with yellow background"

**Structure:**

- "Insert 5 rows above row 10"
- "Hide columns F through J"
- "Create a new sheet called 'Summary'"
- "Freeze the first 2 rows"

**Data Visualization:**

- "Create a bar chart from A1:B10"
- "Add a pie chart showing category percentages"
- "Generate sparklines for the trend data"

**Import/Export:**

- "Import transactions.csv into a new sheet"
- "Export this sheet to Excel format"
- "Convert the workbook to PDF"

## Next Steps

- **[Tutorial 6: Customize Themes](06-customize-themes.md)** - Create custom themes
- **[Best Practices](../guides/best-practices.md)** - Advanced tips
- **[MCP Integration Guide](../MCP_INTEGRATION.md)** - Detailed setup

## Additional Resources

- [MCP Server API](../api/mcp_server.md)
- [Claude Desktop Setup](https://claude.ai/desktop)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
