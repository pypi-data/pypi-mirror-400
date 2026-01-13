#!/usr/bin/env python3
"""
Example: Use MCP server from Python.

This demonstrates starting and using the MCP server
programmatically for AI-powered spreadsheet operations.
"""

from pathlib import Path

from spreadsheet_dl import MCPConfig, MCPServer


def main() -> None:
    """Start MCP server and demonstrate basic usage."""

    print("SpreadsheetDL MCP Server Example")
    print("=" * 50)

    # Configure MCP server
    config = MCPConfig(
        name="spreadsheet-dl",
        version="1.0.0",
        allowed_paths=[Path("output").absolute()],
        rate_limit_per_minute=60,
        enable_audit_log=True,
    )

    print("\nConfiguration:")
    print(f"  Name: {config.name}")
    print(f"  Version: {config.version}")
    print(f"  Allowed paths: {config.allowed_paths}")
    print(f"  Rate limit: {config.rate_limit_per_minute}/min")
    print(f"  Audit log: {config.enable_audit_log}")

    # Create server
    server = MCPServer(config)

    print("\nAvailable tools:")
    for tool_name, tool in server._tools.items():
        print(f"  - {tool_name}: {tool.description}")

    print("\n" + "=" * 50)
    print("MCP Server Setup Complete!")
    print("=" * 50)

    print("\nTo use with Claude Desktop:")
    print("1. Add this to Claude Desktop's config:")
    print("""
    {
      "mcpServers": {
        "spreadsheet-dl": {
          "command": "spreadsheet-dl",
          "args": ["mcp-server"],
          "env": {
            "SPREADSHEET_DIR": "/path/to/budgets"
          }
        }
      }
    }
    """)

    print("\n2. Restart Claude Desktop")

    print("\n3. Try these prompts:")
    print('   - "Create a monthly budget for January 2026"')
    print('   - "Add these expenses to my budget: groceries $125, gas $45"')
    print('   - "Analyze my spending and show me where I can save"')
    print('   - "Generate a report for this month"')

    print("\nTo start server manually:")
    print("  spreadsheet-dl mcp-server")

    print("\nServer is configured but not started (run manually)")
    print("See docs/tutorials/05-use-mcp-tools.md for detailed guide")


if __name__ == "__main__":
    main()
