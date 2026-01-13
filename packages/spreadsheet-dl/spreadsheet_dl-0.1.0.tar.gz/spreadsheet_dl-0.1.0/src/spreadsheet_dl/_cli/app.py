"""Main CLI application setup for SpreadsheetDL.

Contains argument parser setup, command routing, and main entry point.

New in v4.0.0:

New in v0.6.0 (Phase 3: Enhanced Features):

New in v0.5.0:
    - DR-STORE-002: Backup/restore functionality
"""

from __future__ import annotations

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import Any

from spreadsheet_dl._cli import commands
from spreadsheet_dl._version import __version__
from spreadsheet_dl.exceptions import OperationCancelledError, SpreadsheetDLError


def _should_disable_color() -> bool:
    """Check if color output should be disabled.

    Follows the NO_COLOR standard (https://no-color.org/).

    Returns:
        True if colors should be disabled.
    """
    # NO_COLOR standard: if set to any value, disable colors
    if os.environ.get("NO_COLOR") is not None:
        return True
    # Also check common CI environment variables
    if os.environ.get("CI") == "true":
        return True
    # Disable colors if stdout is not a TTY (piped or redirected)
    return not sys.stdout.isatty()


def _setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""

    def handle_sigterm(signum: int, frame: Any) -> None:
        """Handle SIGTERM for graceful shutdown."""
        print("\nReceived termination signal, cleaning up...", file=sys.stderr)
        sys.exit(128 + signum)

    # Register SIGTERM handler (SIGINT is handled by KeyboardInterrupt)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_sigterm)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="spreadsheet-dl",
        description="Family financial tracking with ODS spreadsheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spreadsheet-dl generate -o output/
  spreadsheet-dl generate -o output/ --theme corporate
  spreadsheet-dl analyze budget.ods --json
  spreadsheet-dl report budget.ods -f markdown
  spreadsheet-dl expense 25.50 "Coffee shop" -c "Dining Out"
  spreadsheet-dl import bank_export.csv --preview
  spreadsheet-dl export budget.ods -f xlsx
  spreadsheet-dl backup budget.ods
  spreadsheet-dl dashboard budget.ods
  spreadsheet-dl visualize budget.ods -o dashboard.html
  spreadsheet-dl account add "Primary Checking" --type checking
  spreadsheet-dl account list
  spreadsheet-dl category add "Pet Care" --color "#795548"
  spreadsheet-dl category list
  spreadsheet-dl plugin list
  spreadsheet-dl plugin enable my_plugin
  spreadsheet-dl banks --list
  spreadsheet-dl themes

For more information, visit: https://github.com/lair-click-bats/spreadsheet-dl
""",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit",
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file",
        metavar="FILE",
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        default=_should_disable_color(),
        help="Disable colored output (auto-detected from NO_COLOR env var)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output verbosity (can be repeated: -v, -vv, -vvv)",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-essential output",
    )

    # Global confirmation skip flag
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompts (answer yes to all)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add all subcommand parsers
    _add_generate_parser(subparsers)
    _add_analyze_parser(subparsers)
    _add_report_parser(subparsers)
    _add_expense_parser(subparsers)
    _add_import_parser(subparsers)
    _add_export_parser(subparsers)
    _add_export_dual_parser(subparsers)
    _add_backup_parser(subparsers)
    _add_upload_parser(subparsers)
    _add_dashboard_parser(subparsers)
    _add_visualize_parser(subparsers)
    _add_account_parser(subparsers)
    _add_category_parser(subparsers)
    _add_banks_parser(subparsers)
    _add_currency_parser(subparsers)
    _add_alerts_parser(subparsers)
    _add_templates_parser(subparsers)
    _add_themes_parser(subparsers)
    _add_config_parser(subparsers)
    _add_plugin_parser(subparsers)

    return parser


def _add_generate_parser(
    subparsers: Any,
) -> None:
    """Add generate command parser."""
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate budget spreadsheet",
        description="Create a new budget tracking ODS spreadsheet.",
    )
    gen_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path.cwd(),
        help="Output directory or file path (default: current directory)",
    )
    gen_parser.add_argument(
        "-m",
        "--month",
        type=int,
        choices=range(1, 13),
        metavar="MONTH",
        help="Month number (1-12, default: current month)",
    )
    gen_parser.add_argument(
        "-y",
        "--year",
        type=int,
        help="Year (default: current year)",
    )
    gen_parser.add_argument(
        "--theme",
        type=str,
        help="Visual theme (default, corporate, minimal, dark, high_contrast)",
    )
    gen_parser.add_argument(
        "--empty-rows",
        type=int,
        default=50,
        help="Number of empty rows for data entry (default: 50)",
    )
    gen_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing file without confirmation",
    )
    gen_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )


def _add_analyze_parser(subparsers: Any) -> None:
    """Add analyze command parser."""
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze budget file",
        description="Analyze an existing budget ODS file and show spending summary.",
    )
    analyze_parser.add_argument(
        "file",
        type=Path,
        help="Path to ODS budget file",
    )
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    analyze_parser.add_argument(
        "--category",
        type=str,
        help="Filter by category",
    )
    analyze_parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD)",
    )
    analyze_parser.add_argument(
        "--end-date",
        type=str,
        help="End date (YYYY-MM-DD)",
    )


def _add_report_parser(subparsers: Any) -> None:
    """Add report command parser."""
    report_parser = subparsers.add_parser(
        "report",
        help="Generate report",
        description="Generate a formatted report from a budget file.",
    )
    report_parser.add_argument(
        "file",
        type=Path,
        help="Path to ODS budget file",
    )
    report_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (optional, prints to stdout if not specified)",
    )
    report_parser.add_argument(
        "-f",
        "--format",
        choices=["text", "markdown", "json"],
        default="markdown",
        help="Report format (default: markdown)",
    )


def _add_expense_parser(subparsers: Any) -> None:
    """Add expense command parser."""
    expense_parser = subparsers.add_parser(
        "expense",
        help="Quick expense entry",
        description="Add a quick expense entry to a budget file.",
    )
    expense_parser.add_argument(
        "amount",
        type=str,
        help="Expense amount (e.g., 25.50 or $25.50)",
    )
    expense_parser.add_argument(
        "description",
        type=str,
        help="Expense description",
    )
    expense_parser.add_argument(
        "-c",
        "--category",
        type=str,
        help="Category (auto-detected if not specified)",
    )
    expense_parser.add_argument(
        "-f",
        "--file",
        type=Path,
        help="ODS file to update (uses most recent if not specified)",
    )
    expense_parser.add_argument(
        "-d",
        "--date",
        type=str,
        help="Date (YYYY-MM-DD, defaults to today)",
    )
    expense_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be added without modifying the file",
    )
    expense_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )


def _add_import_parser(subparsers: Any) -> None:
    """Add import command parser."""
    import_parser = subparsers.add_parser(
        "import",
        help="Import bank CSV",
        description="Import transactions from a bank CSV export.",
    )
    import_parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to CSV file",
    )
    import_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output ODS file",
    )
    import_parser.add_argument(
        "-b",
        "--bank",
        type=str,
        default="auto",
        help="Bank format (use 'banks --list' to see available formats)",
    )
    import_parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview import without writing",
    )
    import_parser.add_argument(
        "--theme",
        type=str,
        help="Visual theme for output file",
    )
    import_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output file without confirmation",
    )


def _add_export_parser(subparsers: Any) -> None:
    """Add export command parser."""
    export_parser = subparsers.add_parser(
        "export",
        help="Export to other formats",
        description="Export ODS file to Excel, CSV, PDF, or JSON format.",
    )
    export_parser.add_argument(
        "file",
        type=Path,
        help="Path to ODS budget file",
    )
    export_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: same name with new extension)",
    )
    export_parser.add_argument(
        "-f",
        "--format",
        choices=["xlsx", "csv", "pdf", "json"],
        required=True,
        help="Export format",
    )
    export_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing file without confirmation",
    )


def _add_export_dual_parser(subparsers: Any) -> None:
    """Add export-dual command parser (/002)."""
    export_dual_parser = subparsers.add_parser(
        "export-dual",
        help="Export to ODS + AI-friendly JSON",
        description="Export to both ODS copy and AI-readable JSON for LLM integration.",
    )
    export_dual_parser.add_argument(
        "file",
        type=Path,
        help="Path to ODS budget file",
    )
    export_dual_parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (default: same as source)",
    )


def _add_backup_parser(subparsers: Any) -> None:
    """Add backup command parser (DR-STORE-002)."""
    backup_parser = subparsers.add_parser(
        "backup",
        help="Backup budget files",
        description="Create a backup of a budget file.",
    )
    backup_parser.add_argument(
        "file",
        type=Path,
        help="Path to file to backup",
    )
    backup_parser.add_argument(
        "--list",
        action="store_true",
        help="List available backups for this file",
    )
    backup_parser.add_argument(
        "--restore",
        type=Path,
        metavar="BACKUP_FILE",
        help="Restore from a specific backup file",
    )
    backup_parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove backups older than retention period",
    )
    backup_parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Retention period in days (default: 30)",
    )
    backup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    backup_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation for restore/cleanup",
    )
    backup_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )


def _add_upload_parser(subparsers: Any) -> None:
    """Add upload command parser."""
    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload to Nextcloud",
        description="Upload a budget file to Nextcloud via WebDAV.",
    )
    upload_parser.add_argument(
        "file",
        type=Path,
        help="File to upload",
    )
    upload_parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Remote path on Nextcloud",
    )
    upload_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )


def _add_dashboard_parser(subparsers: Any) -> None:
    """Add dashboard command parser."""
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Analytics dashboard",
        description="Display an analytics dashboard for a budget file.",
    )
    dashboard_parser.add_argument(
        "file",
        type=Path,
        help="Path to ODS budget file",
    )
    dashboard_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )


def _add_visualize_parser(subparsers: Any) -> None:
    """Add visualize command parser."""
    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Generate interactive charts",
        description="Generate interactive HTML charts and dashboards.",
    )
    visualize_parser.add_argument(
        "file",
        type=Path,
        help="Path to ODS budget file",
    )
    visualize_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output HTML file (default: budget_dashboard.html)",
    )
    visualize_parser.add_argument(
        "-t",
        "--type",
        choices=["dashboard", "pie", "bar", "trend"],
        default="dashboard",
        help="Chart type (default: dashboard)",
    )
    visualize_parser.add_argument(
        "--theme",
        choices=["default", "dark"],
        default="default",
        help="Visual theme (default: default)",
    )
    visualize_parser.add_argument(
        "--json",
        action="store_true",
        help="Output chart data as JSON instead of generating HTML",
    )


def _add_account_parser(subparsers: Any) -> None:
    """Add account command parser."""
    account_parser = subparsers.add_parser(
        "account",
        help="Manage financial accounts",
        description="Manage accounts, balances, and transfers.",
    )
    account_subparsers = account_parser.add_subparsers(dest="account_action")

    # Account add
    account_add = account_subparsers.add_parser("add", help="Add a new account")
    account_add.add_argument("name", help="Account name")
    account_add.add_argument(
        "--type",
        choices=["checking", "savings", "credit", "investment", "cash", "retirement"],
        default="checking",
        help="Account type",
    )
    account_add.add_argument("--institution", help="Financial institution")
    account_add.add_argument("--balance", type=float, default=0, help="Initial balance")
    account_add.add_argument("--currency", default="USD", help="Currency code")

    # Account list
    account_list = account_subparsers.add_parser("list", help="List accounts")
    account_list.add_argument("--type", help="Filter by account type")
    account_list.add_argument("--json", action="store_true", help="Output as JSON")

    # Account balance
    account_balance = account_subparsers.add_parser(
        "balance", help="Show account balance"
    )
    account_balance.add_argument("name", nargs="?", help="Account name (or all)")

    # Account transfer
    account_transfer = account_subparsers.add_parser(
        "transfer", help="Transfer between accounts"
    )
    account_transfer.add_argument("from_account", help="Source account name")
    account_transfer.add_argument("to_account", help="Destination account name")
    account_transfer.add_argument("amount", type=float, help="Amount to transfer")

    # Account net-worth
    account_networth = account_subparsers.add_parser(
        "net-worth", help="Calculate net worth"
    )
    account_networth.add_argument("--json", action="store_true", help="Output as JSON")


def _add_category_parser(subparsers: Any) -> None:
    """Add category command parser."""
    category_parser = subparsers.add_parser(
        "category",
        help="Manage expense categories",
        description="Add, edit, delete, and list expense categories.",
    )
    category_subparsers = category_parser.add_subparsers(dest="category_action")

    # Category add
    category_add = category_subparsers.add_parser("add", help="Add a custom category")
    category_add.add_argument("name", help="Category name")
    category_add.add_argument("--color", default="#6B7280", help="Color (hex code)")
    category_add.add_argument("--icon", help="Icon name or emoji")
    category_add.add_argument("--description", help="Category description")
    category_add.add_argument("--parent", help="Parent category name")
    category_add.add_argument(
        "--budget", type=float, default=0, help="Default monthly budget"
    )

    # Category list
    category_list = category_subparsers.add_parser("list", help="List all categories")
    category_list.add_argument(
        "--custom-only", action="store_true", help="Show only custom categories"
    )
    category_list.add_argument(
        "--include-hidden", action="store_true", help="Include hidden categories"
    )
    category_list.add_argument("--json", action="store_true", help="Output as JSON")

    # Category update
    category_update = category_subparsers.add_parser("update", help="Update a category")
    category_update.add_argument("name", help="Category name to update")
    category_update.add_argument("--color", help="New color (hex code)")
    category_update.add_argument("--icon", help="New icon")
    category_update.add_argument("--description", help="New description")
    category_update.add_argument("--rename", help="Rename category to this name")
    category_update.add_argument(
        "--hide", action="store_true", help="Hide category from lists"
    )
    category_update.add_argument(
        "--unhide", action="store_true", help="Unhide category"
    )
    category_update.add_argument("--budget", type=float, help="New default budget")

    # Category delete
    category_delete = category_subparsers.add_parser(
        "delete", help="Delete a custom category"
    )
    category_delete.add_argument("name", help="Category name to delete")
    category_delete.add_argument(
        "--force", action="store_true", help="Force delete even if has sub-categories"
    )

    # Category search
    category_search = category_subparsers.add_parser("search", help="Search categories")
    category_search.add_argument("query", help="Search query")
    category_search.add_argument("--json", action="store_true", help="Output as JSON")

    # Category suggest
    category_suggest = category_subparsers.add_parser(
        "suggest", help="Suggest category for expense description"
    )
    category_suggest.add_argument("description", help="Expense description")


def _add_banks_parser(subparsers: Any) -> None:
    """Add banks command parser."""
    banks_parser = subparsers.add_parser(
        "banks",
        help="List supported bank formats",
        description="List and manage bank CSV format definitions.",
    )
    banks_parser.add_argument(
        "--list",
        action="store_true",
        help="List all supported bank formats",
    )
    banks_parser.add_argument(
        "--search",
        type=str,
        help="Search for banks by name",
    )
    banks_parser.add_argument(
        "--type",
        choices=["checking", "credit", "savings", "investment"],
        help="Filter by account type",
    )
    banks_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    banks_parser.add_argument(
        "--detect",
        type=Path,
        help="Detect format from CSV file",
    )


def _add_currency_parser(subparsers: Any) -> None:
    """Add currency command parser."""
    currency_parser = subparsers.add_parser(
        "currency",
        help="Currency conversion utilities",
        description="Convert between currencies and view exchange rates.",
    )
    currency_parser.add_argument(
        "amount",
        type=float,
        nargs="?",
        help="Amount to convert",
    )
    currency_parser.add_argument(
        "--from",
        dest="from_currency",
        default="USD",
        help="Source currency (default: USD)",
    )
    currency_parser.add_argument(
        "--to",
        dest="to_currency",
        help="Target currency",
    )
    currency_parser.add_argument(
        "--list",
        action="store_true",
        help="List supported currencies",
    )
    currency_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )


def _add_alerts_parser(subparsers: Any) -> None:
    """Add alerts command parser."""
    alerts_parser = subparsers.add_parser(
        "alerts",
        help="Check budget alerts",
        description="Check for budget alerts and warnings.",
    )
    alerts_parser.add_argument(
        "file",
        type=Path,
        help="Path to ODS budget file",
    )
    alerts_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    alerts_parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Show only critical alerts",
    )


def _add_templates_parser(subparsers: Any) -> None:
    """Add templates command parser."""
    templates_parser = subparsers.add_parser(
        "templates",
        help="Show template information (deprecated)",
        description="Templates have been removed. Shows guidance on using examples instead.",
    )
    templates_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )


def _add_themes_parser(subparsers: Any) -> None:
    """Add themes command parser."""
    themes_parser = subparsers.add_parser(
        "themes",
        help="List visual themes",
        description="List available visual themes for spreadsheets.",
    )
    themes_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )


def _add_config_parser(subparsers: Any) -> None:
    """Add config command parser."""
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration",
        description="View or initialize configuration.",
    )
    config_parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new configuration file",
    )
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="Show current configuration",
    )
    config_parser.add_argument(
        "--path",
        type=Path,
        help="Path for configuration file",
    )


def _add_plugin_parser(subparsers: Any) -> None:
    """Add plugin command parser."""
    plugin_parser = subparsers.add_parser(
        "plugin",
        help="Manage plugins",
        description="Manage SpreadsheetDL plugins for extensibility.",
    )
    plugin_subparsers = plugin_parser.add_subparsers(dest="plugin_action")

    # Plugin list
    plugin_list = plugin_subparsers.add_parser("list", help="List all plugins")
    plugin_list.add_argument(
        "--enabled-only", action="store_true", help="Show only enabled plugins"
    )
    plugin_list.add_argument("--json", action="store_true", help="Output as JSON")

    # Plugin enable
    plugin_enable = plugin_subparsers.add_parser("enable", help="Enable a plugin")
    plugin_enable.add_argument("name", help="Plugin name to enable")
    plugin_enable.add_argument(
        "--config", type=str, help="Plugin configuration (JSON string)"
    )

    # Plugin disable
    plugin_disable = plugin_subparsers.add_parser("disable", help="Disable a plugin")
    plugin_disable.add_argument("name", help="Plugin name to disable")

    # Plugin info
    plugin_info = plugin_subparsers.add_parser("info", help="Show plugin information")
    plugin_info.add_argument("name", help="Plugin name")


def route_command(args: argparse.Namespace) -> int:
    """Route parsed arguments to the appropriate command handler.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    command_map = {
        "generate": commands.cmd_generate,
        "analyze": commands.cmd_analyze,
        "report": commands.cmd_report,
        "expense": commands.cmd_expense,
        "import": commands.cmd_import,
        "export": commands.cmd_export,
        "export-dual": commands.cmd_export_dual,
        "backup": commands.cmd_backup,
        "upload": commands.cmd_upload,
        "dashboard": commands.cmd_dashboard,
        "visualize": commands.cmd_visualize,
        "account": commands.cmd_account,
        "category": commands.cmd_category,
        "banks": commands.cmd_banks,
        "currency": commands.cmd_currency,
        "alerts": commands.cmd_alerts,
        "templates": commands.cmd_templates,
        "themes": commands.cmd_themes,
        "config": commands.cmd_config,
        "plugin": commands.cmd_plugin,
    }

    cmd_handler = command_map.get(args.command)
    if cmd_handler:
        return cmd_handler(args)

    return 1


def main() -> int:
    """Main entry point for the CLI application.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Set up signal handlers for graceful shutdown
    _setup_signal_handlers()

    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    try:
        return route_command(args)
    except OperationCancelledError:
        print("Operation cancelled.", file=sys.stderr)
        return 1
    except SpreadsheetDLError as e:
        print(f"Error [{e.error_code}]: {e.message}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 130
    except (ValueError, TypeError, OSError) as e:
        # Catch common runtime errors (invalid input, type mismatches, I/O errors)
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
