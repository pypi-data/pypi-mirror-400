#!/usr/bin/env python3
# mypy: ignore-errors
"""
MCP Server Usage Examples - v0.1 Feature Showcase

Demonstrates comprehensive usage of the SpreadsheetDL MCP server including:
- Server startup and configuration
- Cell operations (get, set, batch operations)
- Style management
- Budget analysis via MCP tools
- Error handling and best practices

The MCP (Model Context Protocol) server enables natural language interaction
with spreadsheets via Claude Desktop and other MCP-compatible clients.
"""

import json
import logging
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Basic Server Setup
# ============================================================================


def example_basic_server_setup() -> None:
    """
    Demonstrate basic MCP server initialization.

    Shows:
    - Creating server with default configuration
    - Configuring allowed paths for security
    - Setting rate limits
    - Enabling audit logging
    """
    from spreadsheet_dl.mcp_server import MCPConfig, MCPServer

    print("=" * 70)
    print("Example 1: Basic MCP Server Setup")
    print("=" * 70)

    # Create configuration with custom settings
    config = MCPConfig(
        name="spreadsheet-dl",
        version="0.1.0",
        # Allow access to specific directories only
        allowed_paths=[
            Path.cwd(),  # Current directory
            Path.home() / "Documents" / "Budgets",  # User's budget directory
        ],
        rate_limit_per_minute=60,  # Limit to 60 requests per minute
        enable_audit_log=True,  # Enable audit logging
        audit_log_path=Path("output/mcp_audit.log"),  # Audit log file
    )

    # Create server instance
    server = MCPServer(config)

    print(f"\n✓ Server configured: {config.name} v{config.version}")
    print(f"  Allowed paths: {len(config.allowed_paths)}")
    for path in config.allowed_paths:
        print(f"    - {path}")
    print(f"  Rate limit: {config.rate_limit_per_minute} requests/minute")
    print(f"  Audit logging: {config.enable_audit_log}")

    # List available tools
    tools = server._tools
    print(f"\n  Available tools: {len(tools)}")

    # Group tools by category
    categories = {
        "budget": [
            t
            for t in tools
            if any(kw in t for kw in ["budget", "expense", "spending", "alert"])
        ],
        "cell": [t for t in tools if t.startswith("cell_")],
        "style": [t for t in tools if any(kw in t for kw in ["style", "format"])],
        "structure": [
            t
            for t in tools
            if any(kw in t for kw in ["row_", "column_", "sheet_", "freeze"])
        ],
        "advanced": [
            t
            for t in tools
            if any(
                kw in t
                for kw in [
                    "chart",
                    "validation",
                    "cf_",
                    "named_range",
                    "table",
                    "query",
                ]
            )
        ],
    }

    for category, tool_list in categories.items():
        if tool_list:
            print(f"\n    {category.capitalize()} operations ({len(tool_list)}):")
            for tool in sorted(tool_list)[:5]:  # Show first 5
                print(f"      - {tool}")
            if len(tool_list) > 5:
                print(f"      ... and {len(tool_list) - 5} more")

    print("\n✓ Server ready to accept MCP connections")
    print()


# ============================================================================
# Example 2: Cell Operations via MCP
# ============================================================================


def example_cell_operations() -> None:
    """
    Demonstrate cell operations through MCP tools.

    Shows:
    - Getting cell values
    - Setting cell values
    - Batch operations for efficiency
    - Cell find and replace
    - Error handling
    """
    from spreadsheet_dl.mcp_server import MCPServer

    print("=" * 70)
    print("Example 2: Cell Operations via MCP")
    print("=" * 70)

    # Create server
    server = MCPServer()

    # Simulate tool calls (normally these come from MCP client)

    # 1. Get cell value
    print("\n1. Getting cell value:")
    try:
        result = server._handle_cell_get(
            file_path="output/budget_2025_01.ods",
            sheet="Expenses",
            cell="B5",
        )
        print(f"   Cell B5 value: {result.content[0]['text']}")
    except Exception as e:
        print(f"   Note: {e} (cell operations are stubs for demonstration)")

    # 2. Set cell value
    print("\n2. Setting cell value:")
    result = server._handle_cell_set(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
        cell="B5",
        value="1200.50",
    )
    print(f"   {result.content[0]['text']}")

    # 3. Batch get multiple cells
    print("\n3. Batch getting multiple cells:")
    result = server._handle_cell_batch_get(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
        cells="A1,B1,C1,D1",
    )
    print(f"   {result.content[0]['text']}")

    # 4. Batch set multiple cells
    print("\n4. Batch setting multiple cells:")
    values = {
        "A1": "Date",
        "B1": "Category",
        "C1": "Description",
        "D1": "Amount",
    }
    result = server._handle_cell_batch_set(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
        values=json.dumps(values),
    )
    print(f"   {result.content[0]['text']}")

    # 5. Find cells containing text
    print("\n5. Finding cells containing 'Groceries':")
    result = server._handle_cell_find(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
        search_text="Groceries",
        match_case=False,
    )
    print(f"   {result.content[0]['text']}")

    # 6. Find and replace
    print("\n6. Replacing 'Groceries' with 'Food Shopping':")
    result = server._handle_cell_replace(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
        search_text="Groceries",
        replace_text="Food Shopping",
        match_case=False,
    )
    print(f"   {result.content[0]['text']}")

    print("\n✓ Cell operations demonstrated")
    print()


# ============================================================================
# Example 3: Budget Analysis via MCP
# ============================================================================


def example_budget_analysis() -> None:
    """
    Demonstrate budget analysis through MCP tools.

    Shows:
    - Creating a budget file first
    - Analyzing budget with different analysis types
    - Querying budget with natural language
    - Getting spending trends
    - Comparing time periods
    - Generating reports
    """
    from spreadsheet_dl.mcp_server import MCPServer
    from spreadsheet_dl.ods_generator import (
        BudgetAllocation,
        ExpenseCategory,
        ExpenseEntry,
        OdsGenerator,
    )

    print("=" * 70)
    print("Example 3: Budget Analysis via MCP")
    print("=" * 70)

    # First, create a sample budget file
    print("\n1. Creating sample budget file...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    generator = OdsGenerator()

    # Create budget with allocations and expenses
    allocations = [
        BudgetAllocation(ExpenseCategory.HOUSING, Decimal("2000")),
        BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600")),
        BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("250")),
        BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("400")),
        BudgetAllocation(ExpenseCategory.ENTERTAINMENT, Decimal("200")),
        BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("150")),
        BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("500")),
    ]

    expenses = [
        ExpenseEntry(
            date=date(2025, 1, 1),
            category=ExpenseCategory.HOUSING,
            description="January rent",
            amount=Decimal("2000"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 5),
            category=ExpenseCategory.GROCERIES,
            description="Weekly groceries",
            amount=Decimal("145.50"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 8),
            category=ExpenseCategory.UTILITIES,
            description="Electric bill",
            amount=Decimal("95.00"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 10),
            category=ExpenseCategory.TRANSPORTATION,
            description="Gas",
            amount=Decimal("45.00"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 12),
            category=ExpenseCategory.GROCERIES,
            description="Weekly groceries",
            amount=Decimal("158.25"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 14),
            category=ExpenseCategory.DINING_OUT,
            description="Restaurant",
            amount=Decimal("65.00"),
        ),
        ExpenseEntry(
            date=date(2025, 1, 15),
            category=ExpenseCategory.ENTERTAINMENT,
            description="Movie tickets",
            amount=Decimal("32.00"),
        ),
    ]

    budget_path = generator.create_budget_spreadsheet(
        output_path=output_dir / "mcp_example_budget.ods",
        month=1,
        year=2025,
        budget_allocations=allocations,
        expenses=expenses,
    )

    print(f"   ✓ Created budget: {budget_path}")

    # Create MCP server
    server = MCPServer()

    # 2. Analyze budget - Summary
    print("\n2. Analyzing budget (summary):")
    result = server._handle_analyze_budget(
        file_path=str(budget_path),
        analysis_type="summary",
    )

    if not result.is_error:
        data = json.loads(result.content[0]["text"])
        print(f"   Total Budget:   ${data['total_budget']:,.2f}")
        print(f"   Total Spent:    ${data['total_spent']:,.2f}")
        print(f"   Remaining:      ${data['remaining']:,.2f}")
        print(f"   Percent Used:   {data['percent_used']:.1f}%")
        print(f"   Status:         {data['status']}")
    else:
        print(f"   Error: {result.content[0]['text']}")

    # 3. Detailed analysis with category breakdown
    print("\n3. Analyzing budget (detailed with categories):")
    result = server._handle_analyze_budget(
        file_path=str(budget_path),
        analysis_type="detailed",
    )

    if not result.is_error:
        data = json.loads(result.content[0]["text"])
        print(f"   Transaction Count: {data['transaction_count']}")
        print("\n   Spending by Category:")
        for category, amount in sorted(
            data["by_category"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            print(f"     {category:<20} ${amount:>10,.2f}")
    else:
        print(f"   Error: {result.content[0]['text']}")

    # 4. Natural language query
    print("\n4. Querying budget with natural language:")
    questions = [
        "How much have I spent on groceries?",
        "How much budget do I have left?",
        "Am I over budget?",
    ]

    for question in questions:
        result = server._handle_query_budget(
            question=question,
            file_path=str(budget_path),
        )

        if not result.is_error:
            data = json.loads(result.content[0]["text"])
            print(f"\n   Q: {question}")
            print(f"   A: {data['answer']}")
        else:
            print(f"   Error: {result.content[0]['text']}")

    # 5. Get spending trends
    print("\n5. Getting spending trends:")
    result = server._handle_spending_trends(
        file_path=str(budget_path),
        period="month",
        category="Groceries",
    )

    if not result.is_error:
        data = json.loads(result.content[0]["text"])
        print(f"   Period: {data['period']}")
        print(f"   Category: {data.get('category', 'All')}")
        stats = data.get("statistics", {})
        print(f"   Average Daily: ${stats.get('average_daily', 0):.2f}")
        print(f"   Highest Day: {stats.get('highest_day', 'N/A')}")
        print(f"   Highest Amount: ${stats.get('highest_amount', 0):.2f}")
    else:
        print(f"   Error: {result.content[0]['text']}")

    # 6. Get budget alerts
    print("\n6. Checking for budget alerts:")
    result = server._handle_get_alerts(
        file_path=str(budget_path),
        severity="info",
    )

    if not result.is_error:
        data = json.loads(result.content[0]["text"])
        print(f"   Total Alerts: {data['total_alerts']}")
        for alert in data["alerts"]:
            severity_symbol = {
                "info": "i",
                "warning": "!",
                "critical": "!!",
            }.get(alert["severity"], "•")
            print(f"   {severity_symbol} {alert['message']}")
    else:
        print(f"   Error: {result.content[0]['text']}")

    # 7. Generate markdown report
    print("\n7. Generating markdown report:")
    result = server._handle_generate_report(
        file_path=str(budget_path),
        format="markdown",
        include_recommendations=True,
    )

    if not result.is_error:
        report = result.content[0]["text"]
        # Print first few lines
        lines = report.split("\n")[:15]
        for line in lines:
            print(f"   {line}")
        if len(report.split("\n")) > 15:
            print(f"   ... ({len(report.split('\n')) - 15} more lines)")
    else:
        print(f"   Error: {result.content[0]['text']}")

    print("\n✓ Budget analysis completed")
    print()


# ============================================================================
# Example 4: Style Management via MCP
# ============================================================================


def example_style_management() -> None:
    """
    Demonstrate style management through MCP tools.

    Shows:
    - Listing available styles
    - Creating custom styles
    - Applying styles to cells
    - Formatting cells with font, fill, border
    - Number formatting
    """
    from spreadsheet_dl.mcp_server import MCPServer

    print("=" * 70)
    print("Example 4: Style Management via MCP")
    print("=" * 70)

    server = MCPServer()

    # 1. List available styles
    print("\n1. Listing available styles:")
    result = server._handle_style_list(
        file_path="output/budget_2025_01.ods",
    )
    print(f"   {result.content[0]['text']}")

    # 2. Create a custom style
    print("\n2. Creating custom style 'HighlightRed':")
    result = server._handle_style_create(
        file_path="output/budget_2025_01.ods",
    )
    print(f"   {result.content[0]['text']}")

    # 3. Apply style to cells
    print("\n3. Applying style to range A1:D1:")
    result = server._handle_style_apply(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
    )
    print(f"   {result.content[0]['text']}")

    # 4. Format cells with font
    print("\n4. Formatting cells with bold font:")
    result = server._handle_format_font(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
    )
    print(f"   {result.content[0]['text']}")

    # 5. Format cells with fill color
    print("\n5. Formatting cells with fill color:")
    result = server._handle_format_fill(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
    )
    print(f"   {result.content[0]['text']}")

    # 6. Format numbers as currency
    print("\n6. Formatting numbers as currency:")
    result = server._handle_format_number(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
    )
    print(f"   {result.content[0]['text']}")

    # 7. Apply borders
    print("\n7. Applying borders to cells:")
    result = server._handle_format_border(
        file_path="output/budget_2025_01.ods",
        sheet="Expenses",
    )
    print(f"   {result.content[0]['text']}")

    print("\n✓ Style management demonstrated")
    print()


# ============================================================================
# Example 5: Error Handling and Best Practices
# ============================================================================


def example_error_handling() -> None:
    """
    Demonstrate error handling and best practices.

    Shows:
    - Handling file not found errors
    - Path security validation
    - Rate limiting
    - Proper error messages
    - Logging and audit trails
    """
    from spreadsheet_dl.mcp_server import MCPConfig, MCPServer

    print("=" * 70)
    print("Example 5: Error Handling and Best Practices")
    print("=" * 70)

    # 1. Path security validation
    print("\n1. Testing path security validation:")
    config = MCPConfig(
        allowed_paths=[Path("/tmp/allowed")],
    )
    server = MCPServer(config)

    try:
        # This should fail - path not in allowed list
        result = server._handle_analyze_budget(
            file_path="/path/to/budget.ods",
            analysis_type="summary",
        )
        print(f"   Result: {result.content[0]['text']}")
    except Exception as e:
        print(f"   ✓ Security check working: {type(e).__name__}")

    # 2. File not found handling
    print("\n2. Testing file not found handling:")
    config = MCPConfig(
        allowed_paths=[Path.cwd()],
    )
    server = MCPServer(config)

    result = server._handle_analyze_budget(
        file_path="nonexistent_file.ods",
        analysis_type="summary",
    )

    if result.is_error:
        print(f"   ✓ Handled gracefully: {result.content[0]['text']}")

    # 3. Invalid parameters
    print("\n3. Testing invalid parameter handling:")
    result = server._handle_analyze_budget(
        file_path="output/mcp_example_budget.ods",
        analysis_type="invalid_type",  # Invalid analysis type
    )

    # Should still work, fallback to default
    print("   Handled with fallback behavior")

    # 4. Audit logging
    print("\n4. Testing audit logging:")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    audit_path = output_dir / "mcp_audit_example.log"

    config = MCPConfig(
        allowed_paths=[Path.cwd()],
        enable_audit_log=True,
        audit_log_path=audit_path,
    )
    server = MCPServer(config)

    # Make a few requests
    server._handle_list_categories()

    if audit_path.exists():
        with open(audit_path) as f:
            logs = f.readlines()
        print(f"   ✓ Audit log created with {len(logs)} entries")
        if logs:
            print(f"   Example entry: {logs[0].strip()}")
    else:
        print("   Note: Audit logging configured")

    # 5. Rate limiting check
    print("\n5. Testing rate limiting:")
    print(f"   Rate limit: {server.config.rate_limit_per_minute} requests/min")
    print(f"   Current count: {server._request_count}")

    # Simulate rate limit check
    can_proceed = server._check_rate_limit()
    print(f"   ✓ Can proceed: {can_proceed}")

    print("\n✓ Error handling demonstrated")
    print()


# ============================================================================
# Example 6: Advanced MCP Configuration
# ============================================================================


def example_advanced_configuration() -> None:
    """
    Demonstrate advanced MCP server configuration.

    Shows:
    - Custom MCP configuration
    - Multiple allowed path patterns
    - Tool registry management
    - Custom tool categories
    """
    from spreadsheet_dl.mcp_server import MCPConfig, MCPServer

    print("=" * 70)
    print("Example 6: Advanced MCP Configuration")
    print("=" * 70)

    # Create advanced configuration
    config = MCPConfig(
        name="spreadsheet-dl-pro",
        version="0.1.0",
        allowed_paths=[
            Path.cwd() / "output",
            Path.home() / "Documents" / "Spreadsheets",
            Path("/shared/budgets"),
        ],
        rate_limit_per_minute=120,  # Higher limit for power users
        enable_audit_log=True,
        audit_log_path=Path("output/mcp_advanced_audit.log"),
    )

    server = MCPServer(config)

    print(f"\n✓ Advanced server configured: {config.name}")
    print("\n  Security Configuration:")
    print(f"    Allowed paths: {len(config.allowed_paths)}")
    for path in config.allowed_paths:
        print(f"      • {path}")

    print("\n  Performance Configuration:")
    print(f"    Rate limit: {config.rate_limit_per_minute} requests/min")

    print("\n  Audit Configuration:")
    print(f"    Logging enabled: {config.enable_audit_log}")
    print(f"    Log file: {config.audit_log_path}")

    # Explore tool registry
    print("\n  Tool Registry:")
    registry = server._registry
    categories = registry.get_categories()
    print(f"    Categories: {', '.join(categories)}")

    for category in categories:
        tools = registry.get_tools_by_category(category)
        print(f"    {category}: {len(tools)} tools")

    print(f"\n  Total tools registered: {registry.get_tool_count()}")

    print("\n✓ Advanced configuration demonstrated")
    print()


# ============================================================================
# Main Example Runner
# ============================================================================


def main() -> None:
    """Run all MCP server examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  MCP Server Usage Examples - SpreadsheetDL v0.1".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        # Run all examples
        example_basic_server_setup()
        example_cell_operations()
        example_budget_analysis()
        example_style_management()
        example_error_handling()
        example_advanced_configuration()

        print("=" * 70)
        print("All MCP Server Examples Completed Successfully!")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("  • MCP server enables natural language spreadsheet interaction")
        print("  • Security through path restrictions and rate limiting")
        print("  • Comprehensive tool set for cell, style, and budget operations")
        print("  • Built-in error handling and audit logging")
        print("  • Easy integration with Claude Desktop and MCP clients")
        print()
        print("To use with Claude Desktop:")
        print("  1. Configure MCP server in Claude Desktop settings")
        print(
            "  2. Add server command: spreadsheet-dl-mcp --allowed-paths /path/to/budgets"
        )
        print("  3. Claude can now interact with your spreadsheets naturally")
        print()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Error running examples")
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
