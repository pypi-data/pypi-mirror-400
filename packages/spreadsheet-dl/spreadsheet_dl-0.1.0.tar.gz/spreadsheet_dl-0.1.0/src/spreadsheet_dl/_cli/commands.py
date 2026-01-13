"""CLI command handlers for SpreadsheetDL.

Contains all command implementation functions called from the main CLI app.

    - DR-STORE-002: Backup/restore functionality
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import argparse

from spreadsheet_dl._cli.utils import (
    confirm_action,
    confirm_destructive_operation,
    confirm_overwrite,
    validate_amount,
    validate_date,
)
from spreadsheet_dl.exceptions import (
    FileError,
    InvalidCategoryError,
    OdsError,
    OperationCancelledError,
)


def cmd_generate(args: argparse.Namespace) -> int:
    """Handle generate command."""
    from spreadsheet_dl.domains.finance.ods_generator import (
        OdsGenerator,
        create_monthly_budget,
    )

    output = args.output
    skip_confirm = getattr(args, "yes", False) or getattr(args, "force", False)

    # Standard budget generation
    allocations = None

    # Get theme if specified
    theme = getattr(args, "theme", None)
    if theme:
        print(f"Using theme: {theme}")

    if output.is_dir():
        today = date.today()
        month = args.month or today.month
        year = getattr(args, "year", None) or today.year
        filename = f"budget_{year}_{month:02d}.ods"
        output_path = output / filename
    else:
        output_path = output

    # Check for existing file
    if not confirm_overwrite(output_path, skip_confirm=skip_confirm):
        raise OperationCancelledError("File generation")

    if output.is_dir():
        if allocations or theme:
            generator = OdsGenerator(theme=theme)
            today = date.today()
            month = args.month or today.month
            year = getattr(args, "year", None) or today.year
            path = generator.create_budget_spreadsheet(
                output_path,
                month=month,
                year=year,
                budget_allocations=allocations,
            )
        else:
            path = create_monthly_budget(
                output, month=args.month, year=getattr(args, "year", None), theme=theme
            )
    else:
        generator = OdsGenerator(theme=theme)
        path = generator.create_budget_spreadsheet(
            output,
            month=args.month,
            year=getattr(args, "year", None),
            budget_allocations=allocations,
        )

    if getattr(args, "json", False):
        result = {
            "status": "success",
            "action": "generate",
            "file": str(path),
            "month": args.month or date.today().month,
            "year": getattr(args, "year", None) or date.today().year,
            "theme": theme,
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Created: {path}")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Handle analyze command."""
    from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    analyzer = BudgetAnalyzer(args.file)

    # Apply filters if specified
    if args.category:
        filtered = analyzer.filter_by_category(args.category)
        if filtered.empty:
            print(f"No expenses found for category: {args.category}")
            return 0
        print(f"Category: {args.category}")
        print(f"Total: ${filtered['Amount'].sum():,.2f}")
        print(f"Transactions: {len(filtered)}")
        return 0

    if args.start_date or args.end_date:
        start = validate_date(args.start_date) if args.start_date else date(1900, 1, 1)
        end = validate_date(args.end_date) if args.end_date else date(2100, 12, 31)
        filtered = analyzer.filter_by_date_range(start, end)
        if filtered.empty:
            print("No expenses found in date range")
            return 0
        print(f"Date Range: {start} to {end}")
        print(f"Total: ${filtered['Amount'].sum():,.2f}")
        print(f"Transactions: {len(filtered)}")
        return 0

    data = analyzer.to_dict()

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        summary = analyzer.get_summary()
        print(f"Budget Analysis: {args.file}")
        print("-" * 40)
        print(f"Total Budget:  ${summary.total_budget:,.2f}")
        print(f"Total Spent:   ${summary.total_spent:,.2f}")
        print(f"Remaining:     ${summary.total_remaining:,.2f}")
        print(f"Used:          {summary.percent_used:.1f}%")
        print()
        if summary.alerts:
            print("Alerts:")
            for alert in summary.alerts:
                print(f"  - {alert}")

    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Handle report command."""
    from spreadsheet_dl.domains.finance.report_generator import ReportGenerator

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    generator = ReportGenerator(args.file)

    if args.output:
        path = generator.save_report(args.output, format=args.format)
        print(f"Report saved: {path}")
    else:
        if args.format == "text":
            print(generator.generate_text_report())
        elif args.format == "markdown":
            print(generator.generate_markdown_report())
        elif args.format == "json":
            print(json.dumps(generator.generate_visualization_data(), indent=2))

    return 0


def cmd_expense(args: argparse.Namespace) -> int:
    """Handle quick expense entry."""
    from spreadsheet_dl.domains.finance.csv_import import TransactionCategorizer
    from spreadsheet_dl.domains.finance.ods_generator import (
        ExpenseCategory,
        ExpenseEntry,
        OdsGenerator,
    )
    from spreadsheet_dl.ods_editor import OdsEditor

    # Parse amount with validation
    amount = validate_amount(args.amount)

    # Parse date with validation
    expense_date = validate_date(args.date) if args.date else date.today()

    # Determine category
    if args.category:
        try:
            category = ExpenseCategory(args.category)
        except ValueError:
            # Try to find by name (case-insensitive)
            category_lower = args.category.lower().replace(" ", "_")
            for cat in ExpenseCategory:
                if (
                    cat.name.lower() == category_lower
                    or cat.value.lower() == args.category.lower()
                ):
                    category = cat
                    break
            else:
                valid_categories = [cat.value for cat in ExpenseCategory]
                raise InvalidCategoryError(args.category, valid_categories)
    else:
        # Auto-categorize
        categorizer = TransactionCategorizer()
        category = categorizer.categorize(args.description)
        print(f"Auto-categorized as: {category.value}")

    entry = ExpenseEntry(
        date=expense_date,
        category=category,
        description=args.description,
        amount=amount,
    )

    # Find or create ODS file
    if args.file:
        ods_path = args.file
        if not ods_path.exists():
            print(f"Error: File not found: {ods_path}", file=sys.stderr)
            return 1
        file_existed = True
    else:
        # Look for most recent budget file in current directory
        ods_files = list(Path.cwd().glob("budget_*.ods"))
        if ods_files:
            ods_path = max(ods_files, key=lambda p: p.stat().st_mtime)
            print(f"Using: {ods_path}")
            file_existed = True
        else:
            # Create new
            today = date.today()
            ods_path = Path.cwd() / f"budget_{today.year}_{today.month:02d}.ods"
            file_existed = False

    # Handle dry-run mode
    dry_run = getattr(args, "dry_run", False)
    json_output = getattr(args, "json", False)

    if dry_run:
        expense_data = {
            "file": str(ods_path),
            "date": str(entry.date),
            "category": entry.category.value,
            "description": entry.description,
            "amount": float(entry.amount),
            "dry_run": True,
        }
        if json_output:
            print(json.dumps({"status": "dry_run", **expense_data}, indent=2))
        else:
            print("\n[DRY RUN] Would add expense:")
            print(f"  File:        {ods_path}")
            print(f"  Date:        {entry.date}")
            print(f"  Category:    {entry.category.value}")
            print(f"  Description: {entry.description}")
            print(f"  Amount:      ${entry.amount:.2f}")
        return 0

    # Create file if needed
    file_created = False
    if not file_existed:
        generator = OdsGenerator()
        generator.create_budget_spreadsheet(ods_path)
        file_created = True
        if not json_output:
            print(f"Created new budget: {ods_path}")

    # Append expense to file (implementation)
    try:
        editor = OdsEditor(ods_path)
        row_num = editor.append_expense(entry)
        editor.save()

        if json_output:
            result = {
                "status": "success",
                "action": "expense",
                "file": str(ods_path),
                "file_created": file_created,
                "row": row_num,
                "date": str(entry.date),
                "category": entry.category.value,
                "description": entry.description,
                "amount": float(entry.amount),
            }
            print(json.dumps(result, indent=2))
        else:
            print("\nExpense added successfully:")
            print(f"  File:        {ods_path}")
            print(f"  Row:         {row_num}")
            print(f"  Date:        {entry.date}")
            print(f"  Category:    {entry.category.value}")
            print(f"  Description: {entry.description}")
            print(f"  Amount:      ${entry.amount:.2f}")

    except (OdsError, FileError, ValueError, OSError) as e:
        # ODS errors (read/write), file errors, validation errors, I/O errors
        if json_output:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error adding expense: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_import(args: argparse.Namespace) -> int:
    """Handle CSV import."""
    from spreadsheet_dl.domains.finance.bank_formats import BankFormatRegistry
    from spreadsheet_dl.domains.finance.csv_import import import_bank_csv
    from spreadsheet_dl.domains.finance.ods_generator import OdsGenerator

    skip_confirm = getattr(args, "yes", False) or getattr(args, "force", False)

    if not args.csv_file.exists():
        print(f"Error: CSV file not found: {args.csv_file}", file=sys.stderr)
        return 1

    # Detect or use specified bank format
    if args.bank == "auto":
        registry = BankFormatRegistry()
        detected_fmt = registry.detect_format(args.csv_file)
        bank = detected_fmt.id if detected_fmt else "generic"
        print(f"Detected format: {bank}")
    else:
        bank = args.bank

    # Import transactions
    entries = import_bank_csv(args.csv_file, bank)

    if not entries:
        print("No expenses found in CSV file")
        return 0

    print(f"Found {len(entries)} expenses")

    if args.preview:
        print("\nPreview (first 10):")
        for entry in entries[:10]:
            print(
                f"  {entry.date} | {entry.category.value:15} | "
                f"${entry.amount:>8.2f} | {entry.description[:30]}"
            )
        if len(entries) > 10:
            print(f"  ... and {len(entries) - 10} more")
        return 0

    # Create ODS file
    if args.output:
        output_path = args.output
    else:
        today = date.today()
        output_path = Path.cwd() / f"imported_{today.strftime('%Y%m%d')}.ods"

    # Confirm overwrite
    if not confirm_overwrite(output_path, skip_confirm=skip_confirm):
        raise OperationCancelledError("CSV import")

    theme = getattr(args, "theme", None)
    generator = OdsGenerator(theme=theme)
    generator.create_budget_spreadsheet(output_path, expenses=entries)

    print(f"Created: {output_path}")
    print(f"Total imported: ${sum(e.amount for e in entries):,.2f}")

    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Handle export command."""
    from spreadsheet_dl.export import MultiFormatExporter

    skip_confirm = getattr(args, "yes", False) or getattr(args, "force", False)

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Determine output path
    output_path = args.output or args.file.with_suffix(f".{args.format}")

    # Confirm overwrite
    if not confirm_overwrite(output_path, skip_confirm=skip_confirm):
        raise OperationCancelledError("Export")

    exporter = MultiFormatExporter()
    result = exporter.export(args.file, output_path, args.format)

    print(f"Exported: {result}")
    return 0


def cmd_export_dual(args: argparse.Namespace) -> int:
    """Handle dual export command."""
    from spreadsheet_dl.ai_export import AIExporter

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    output_dir = args.output_dir or args.file.parent

    exporter = AIExporter()
    ods_path, json_path = exporter.export_dual(args.file, output_dir)

    print("Exported:")
    print(f"  ODS:  {ods_path}")
    print(f"  JSON: {json_path}")
    print("\nThe JSON file is formatted for AI/LLM consumption with semantic metadata.")

    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    """Handle backup command.

    DR-STORE-002: Backup/restore functionality
    """
    from spreadsheet_dl.backup import BackupManager, BackupReason

    skip_confirm = getattr(args, "yes", False) or getattr(args, "force", False)
    dry_run = getattr(args, "dry_run", False)
    json_output = getattr(args, "json", False)

    manager = BackupManager(retention_days=args.days)

    # List backups
    if args.list:
        backups = manager.list_backups(args.file)
        if json_output:
            backup_list = [
                {
                    "path": str(backup.backup_path),
                    "created": backup.created.isoformat(),
                    "reason": backup.metadata.reason,
                    "size_bytes": (
                        backup.backup_path.stat().st_size
                        if backup.backup_path.exists()
                        else 0
                    ),
                    "content_hash": backup.metadata.content_hash,
                }
                for backup in backups
            ]
            print(
                json.dumps(
                    {
                        "status": "success",
                        "action": "list",
                        "file": str(args.file),
                        "count": len(backup_list),
                        "backups": backup_list,
                    },
                    indent=2,
                )
            )
            return 0

        if not backups:
            print(f"No backups found for: {args.file}")
            return 0

        print(f"Backups for: {args.file}")
        print("-" * 60)
        for backup in backups:
            size_kb = (
                backup.backup_path.stat().st_size / 1024
                if backup.backup_path.exists()
                else 0
            )
            print(
                f"  {backup.created.strftime('%Y-%m-%d %H:%M')}  "
                f"{size_kb:>8.1f} KB  {backup.metadata.reason}"
            )
            print(f"    Path: {backup.backup_path}")
        return 0

    # Cleanup old backups
    if args.cleanup:
        if not confirm_destructive_operation(
            "backup cleanup",
            f"This will remove backups older than {args.days} days.",
            skip_confirm=skip_confirm,
        ):
            raise OperationCancelledError("Backup cleanup")

        deleted = manager.cleanup_old_backups(args.days, dry_run=dry_run)

        if json_output:
            print(
                json.dumps(
                    {
                        "status": "success" if not dry_run else "dry_run",
                        "action": "cleanup",
                        "retention_days": args.days,
                        "deleted_count": len(deleted),
                        "deleted": [str(p) for p in deleted],
                    },
                    indent=2,
                )
            )
        elif dry_run:
            print(f"[DRY RUN] Would delete {len(deleted)} backup(s)")
        else:
            print(f"Deleted {len(deleted)} old backup(s)")
        return 0

    # Restore from backup
    if args.restore:
        if not args.restore.exists():
            if json_output:
                print(
                    json.dumps(
                        {
                            "status": "error",
                            "error": f"Backup file not found: {args.restore}",
                        },
                        indent=2,
                    )
                )
            else:
                print(f"Error: Backup file not found: {args.restore}", file=sys.stderr)
            return 1

        target = args.file
        if target.exists() and not confirm_overwrite(target, skip_confirm=skip_confirm):
            raise OperationCancelledError("Backup restore")

        if dry_run:
            if json_output:
                print(
                    json.dumps(
                        {
                            "status": "dry_run",
                            "action": "restore",
                            "source": str(args.restore),
                            "target": str(target),
                        },
                        indent=2,
                    )
                )
            else:
                print(f"[DRY RUN] Would restore {args.restore} to {target}")
            return 0

        restored = manager.restore_backup(args.restore, target, overwrite=True)
        if json_output:
            print(
                json.dumps(
                    {
                        "status": "success",
                        "action": "restore",
                        "source": str(args.restore),
                        "target": str(restored),
                    },
                    indent=2,
                )
            )
        else:
            print(f"Restored: {restored}")
        return 0

    # Create backup (default action)
    if not args.file.exists():
        if json_output:
            print(
                json.dumps(
                    {"status": "error", "error": f"File not found: {args.file}"},
                    indent=2,
                )
            )
        else:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    backup_info = manager.create_backup(args.file, BackupReason.MANUAL)
    if json_output:
        print(
            json.dumps(
                {
                    "status": "success",
                    "action": "create",
                    "source": str(args.file),
                    "backup_path": str(backup_info.backup_path),
                    "content_hash": backup_info.metadata.content_hash,
                    "created": backup_info.created.isoformat(),
                },
                indent=2,
            )
        )
    else:
        print(f"Backup created: {backup_info.backup_path}")
        print(f"  Original: {args.file}")
        print(f"  Hash: {backup_info.metadata.content_hash[:16]}...")

    return 0


def cmd_upload(args: argparse.Namespace) -> int:
    """Handle Nextcloud upload."""
    from spreadsheet_dl.webdav_upload import NextcloudConfig, upload_budget

    json_output = getattr(args, "json", False)

    if not args.file.exists():
        if json_output:
            print(
                json.dumps(
                    {"status": "error", "error": f"File not found: {args.file}"},
                    indent=2,
                )
            )
        else:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    try:
        config = NextcloudConfig.from_env()
    except ValueError as e:
        if json_output:
            print(
                json.dumps(
                    {"status": "error", "error": f"Configuration error: {e}"},
                    indent=2,
                )
            )
        else:
            print(f"Configuration error: {e}", file=sys.stderr)
            print("\nSet these environment variables:")
            print("  NEXTCLOUD_URL=https://your-nextcloud.com")
            print("  NEXTCLOUD_USER=username")
            print("  NEXTCLOUD_PASSWORD=app-password")
            print("\nOr create a configuration file:")
            print("  spreadsheet-dl config --init")
        return 1

    if not json_output:
        print(f"Uploading to {config.server_url}...")

    url = upload_budget(args.file, config)

    if json_output:
        print(
            json.dumps(
                {
                    "status": "success",
                    "action": "upload",
                    "file": str(args.file),
                    "server": config.server_url,
                    "url": url,
                },
                indent=2,
            )
        )
    else:
        print(f"Uploaded: {url}")

    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    """Handle dashboard command."""
    from spreadsheet_dl.domains.finance.analytics import generate_dashboard

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    data = generate_dashboard(args.file)

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    # Pretty print dashboard
    print("=" * 60)
    print("BUDGET DASHBOARD")
    print("=" * 60)
    print()

    # Status
    status_icons = {
        "healthy": "[OK]",
        "caution": "[!]",
        "warning": "[!!]",
        "critical": "[!!!]",
    }
    print(
        f"Status: {status_icons.get(data['budget_status'], '[?]')} {data['status_message']}"
    )
    print()

    # Summary
    print("SUMMARY")
    print("-" * 40)
    print(f"  Total Budget:     ${data['total_budget']:>12,.2f}")
    print(f"  Total Spent:      ${data['total_spent']:>12,.2f}")
    print(f"  Remaining:        ${data['total_remaining']:>12,.2f}")
    print(f"  Budget Used:      {data['percent_used']:>12.1f}%")
    print(f"  Days Remaining:   {data['days_remaining']:>12}")
    print(f"  Daily Budget:     ${data['daily_budget_remaining']:>12,.2f}")
    print()

    # Top spending
    print("TOP SPENDING")
    print("-" * 40)
    for i, (cat, amount) in enumerate(data["top_spending"][:5], 1):
        print(f"  {i}. {cat:<20} ${amount:>10,.2f}")
    print()

    # Alerts
    if data["alerts"]:
        print("ALERTS")
        print("-" * 40)
        for alert in data["alerts"]:
            print(f"  ! {alert}")
        print()

    # Recommendations
    if data["recommendations"]:
        print("RECOMMENDATIONS")
        print("-" * 40)
        for rec in data["recommendations"]:
            print(f"  - {rec}")
        print()

    print("=" * 60)

    return 0


def cmd_visualize(args: argparse.Namespace) -> int:
    """Handle visualize command."""
    from spreadsheet_dl.visualization import (
        ChartConfig,
        ChartDataPoint,
        ChartGenerator,
        ChartType,
        create_budget_dashboard,
    )

    json_output = getattr(args, "json", False)

    if not args.file.exists():
        if json_output:
            print(
                json.dumps(
                    {"status": "error", "error": f"File not found: {args.file}"},
                    indent=2,
                )
            )
        else:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # For JSON output, return chart data instead of generating HTML
    if json_output:
        from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

        analyzer = BudgetAnalyzer(args.file)
        by_category = analyzer.get_category_breakdown()
        summary = analyzer.get_summary()

        chart_data = {
            "status": "success",
            "action": "visualize",
            "file": str(args.file),
            "chart_type": args.type,
            "theme": args.theme,
            "data": {
                "categories": [
                    {"name": cat, "amount": float(amt)}
                    for cat, amt in by_category.items()
                    if amt > 0
                ],
                "summary": {
                    "total_budget": float(summary.total_budget),
                    "total_spent": float(summary.total_spent),
                    "total_remaining": float(summary.total_remaining),
                    "percent_used": float(summary.percent_used),
                },
            },
        }
        print(json.dumps(chart_data, indent=2))
        return 0

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = args.file.with_suffix(".html")
        output_path = output_path.with_stem(f"{output_path.stem}_dashboard")

    # Generate visualization
    if args.type == "dashboard":
        html = create_budget_dashboard(
            output_path=output_path,
            theme=args.theme,
        )
        print(f"Dashboard created: {output_path}")
    else:
        # For specific chart types, we'd need budget data
        from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

        analyzer = BudgetAnalyzer(args.file)
        by_category = analyzer.get_category_breakdown()

        generator = ChartGenerator(theme=args.theme)
        data = [
            ChartDataPoint(label=cat, value=float(amt), category=cat)
            for cat, amt in by_category.items()
            if amt > 0
        ]

        if args.type == "pie":
            config = ChartConfig(
                title="Spending by Category", chart_type=ChartType.PIE, cutout=60
            )
            html = generator.create_pie_chart(data, config)
        elif args.type == "bar":
            config = ChartConfig(title="Spending by Category", chart_type=ChartType.BAR)
            html = generator.create_bar_chart(data, config)
        else:
            config = ChartConfig(title="Spending Trend", chart_type=ChartType.LINE)
            # Would need time series data for trend
            html = generator.create_bar_chart(data, config)

        with open(output_path, "w") as f:
            f.write(html)
        print(f"Chart created: {output_path}")

    print("\nOpen the HTML file in a browser to view interactive charts.")
    return 0


def cmd_account(args: argparse.Namespace) -> int:
    """Handle account command."""
    from decimal import Decimal

    from spreadsheet_dl.domains.finance.accounts import AccountManager, AccountType

    # Get data file path
    config_dir = Path.home() / ".config" / "spreadsheet-dl"
    config_dir.mkdir(parents=True, exist_ok=True)
    data_file = config_dir / "accounts.json"

    manager = AccountManager(data_file=data_file)

    if args.account_action == "add":
        # Map string to AccountType
        type_map = {
            "checking": AccountType.CHECKING,
            "savings": AccountType.SAVINGS,
            "credit": AccountType.CREDIT,
            "investment": AccountType.INVESTMENT,
            "cash": AccountType.CASH,
            "retirement": AccountType.RETIREMENT,
        }
        account_type = type_map.get(args.type, AccountType.CHECKING)

        account = manager.add_account(
            name=args.name,
            account_type=account_type,
            institution=args.institution or "",
            balance=Decimal(str(args.balance)),
            currency=args.currency,
        )
        print(f"Account created: {account.name}")
        print(f"  ID: {account.id}")
        print(f"  Type: {account.account_type.value}")
        print(f"  Balance: ${account.balance:,.2f}")
        return 0

    elif args.account_action == "list":
        accounts = manager.list_accounts()

        if not accounts:
            print("No accounts found. Add one with: spreadsheet-dl account add <name>")
            return 0

        if getattr(args, "json", False):
            print(json.dumps([a.to_dict() for a in accounts], indent=2))
            return 0

        print("Accounts")
        print("=" * 60)
        for acc in accounts:
            status = "(active)" if acc.is_active else "(inactive)"
            print(f"  {acc.name} {status}")
            print(f"    Type: {acc.account_type.value}")
            print(f"    Balance: ${acc.balance:,.2f} {acc.currency}")
            if acc.institution:
                print(f"    Institution: {acc.institution}")
            print()
        return 0

    elif args.account_action == "balance":
        if args.name:
            found_account = manager.get_account_by_name(args.name)
            if found_account is None:
                print(f"Account not found: {args.name}", file=sys.stderr)
                return 1
            print(f"{found_account.name}: ${found_account.balance:,.2f}")
        else:
            accounts = manager.list_accounts()
            total = sum(a.balance for a in accounts)
            for acc in accounts:
                print(f"  {acc.name}: ${acc.balance:,.2f}")
            print("-" * 40)
            print(f"  Total: ${total:,.2f}")
        return 0

    elif args.account_action == "transfer":
        from_acc = manager.get_account_by_name(args.from_account)
        to_acc = manager.get_account_by_name(args.to_account)

        if not from_acc:
            print(f"Source account not found: {args.from_account}", file=sys.stderr)
            return 1
        if not to_acc:
            print(f"Destination account not found: {args.to_account}", file=sys.stderr)
            return 1

        transfer = manager.transfer(
            from_acc.id,
            to_acc.id,
            Decimal(str(args.amount)),
        )

        if transfer:
            print("Transfer complete:")
            print(f"  From: {from_acc.name} -> ${from_acc.balance:,.2f}")
            print(f"  To: {to_acc.name} -> ${to_acc.balance:,.2f}")
        else:
            print("Transfer failed", file=sys.stderr)
            return 1
        return 0

    elif args.account_action == "net-worth":
        net_worth = manager.calculate_net_worth()

        if getattr(args, "json", False):
            print(json.dumps(net_worth.to_dict(), indent=2))
            return 0

        print("Net Worth Summary")
        print("=" * 40)
        print(f"  Total Assets:      ${net_worth.total_assets:>12,.2f}")
        print(f"  Total Liabilities: ${net_worth.total_liabilities:>12,.2f}")
        print("-" * 40)
        print(f"  Net Worth:         ${net_worth.net_worth:>12,.2f}")

        if net_worth.assets_by_type:
            print("\nAssets by Type:")
            for atype, amount in net_worth.assets_by_type.items():
                print(f"  {atype.value}: ${amount:,.2f}")

        if net_worth.liabilities_by_type:
            print("\nLiabilities by Type:")
            for ltype, amount in net_worth.liabilities_by_type.items():
                print(f"  {ltype.value}: ${amount:,.2f}")

        return 0

    else:
        print("Usage: spreadsheet-dl account <add|list|balance|transfer|net-worth>")
        print("\nManage financial accounts, balances, and transfers.")
        print("\nExamples:")
        print(
            "  spreadsheet-dl account add 'Primary Checking' --type checking --balance 1000"
        )
        print("  spreadsheet-dl account list")
        print("  spreadsheet-dl account balance")
        print("  spreadsheet-dl account transfer 'Checking' 'Savings' 500")
        print("  spreadsheet-dl account net-worth")
        return 0


def cmd_category(args: argparse.Namespace) -> int:
    """Handle category command."""
    from spreadsheet_dl.domains.finance.categories import Category, CategoryManager

    manager = CategoryManager()

    if args.category_action == "add":
        try:
            cat = Category(
                name=args.name,
                color=args.color,
                icon=args.icon or "",
                description=args.description or "",
                parent=args.parent,
                budget_default=args.budget,
            )
            manager.add_category(cat)
            manager.save()

            print(f"Category created: {cat.name}")
            print(f"  Color: {cat.color}")
            if cat.parent:
                print(f"  Parent: {cat.parent}")
            if cat.budget_default:
                print(f"  Default budget: ${cat.budget_default:,.2f}")
            return 0
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.category_action == "list":
        categories = manager.list_categories(
            include_hidden=getattr(args, "include_hidden", False),
            custom_only=getattr(args, "custom_only", False),
        )

        if getattr(args, "json", False):
            print(json.dumps([c.to_dict() for c in categories], indent=2))
            return 0

        print("Expense Categories")
        print("=" * 60)

        custom = [c for c in categories if c.is_custom]
        standard = [c for c in categories if not c.is_custom]

        if standard:
            print("\nStandard Categories:")
            print("-" * 40)
            for cat in standard:
                hidden = " (hidden)" if cat.is_hidden else ""
                print(f"  {cat.name}{hidden}")
                print(f"    Color: {cat.color}")

        if custom:
            print("\nCustom Categories:")
            print("-" * 40)
            for cat in custom:
                hidden = " (hidden)" if cat.is_hidden else ""
                print(f"  {cat.name}{hidden}")
                print(f"    Color: {cat.color}")
                if cat.description:
                    print(f"    Description: {cat.description}")
                if cat.parent:
                    print(f"    Parent: {cat.parent}")

        print()
        print(f"Total: {len(categories)} categories")
        return 0

    elif args.category_action == "update":
        try:
            is_hidden = None
            if getattr(args, "hide", False):
                is_hidden = True
            elif getattr(args, "unhide", False):
                is_hidden = False

            cat = manager.update_category(
                args.name,
                color=args.color,
                icon=args.icon,
                description=args.description,
                new_name=args.rename,
                is_hidden=is_hidden,
                budget_default=args.budget,
            )
            manager.save()

            print(f"Category updated: {cat.name}")
            return 0
        except (KeyError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.category_action == "delete":
        try:
            skip_confirm = getattr(args, "force", False)
            if not skip_confirm and not confirm_action(
                f"Delete category '{args.name}'?", default=False
            ):
                raise OperationCancelledError("Category deletion")

            result = manager.delete_category(
                args.name, force=getattr(args, "force", False)
            )
            if result:
                manager.save()
                print(f"Category deleted: {args.name}")
            else:
                print(f"Category not found: {args.name}")
                return 1
            return 0
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.category_action == "search":
        results = manager.search_categories(args.query)

        if getattr(args, "json", False):
            print(json.dumps([c.to_dict() for c in results], indent=2))
            return 0

        if not results:
            print(f"No categories found matching: {args.query}")
            return 0

        print(f"Categories matching '{args.query}':")
        for cat in results:
            custom_label = " (custom)" if cat.is_custom else ""
            print(f"  {cat.name}{custom_label}")
        return 0

    elif args.category_action == "suggest":
        suggested_cat: Category | None = manager.suggest_category(args.description)
        if suggested_cat is not None:
            print(f"Suggested category: {suggested_cat.name}")
            print(f"  Color: {suggested_cat.color}")
        else:
            print("No suggestion available")
        return 0

    else:
        print("Usage: spreadsheet-dl category <add|list|update|delete|search|suggest>")
        print("\nManage expense categories.")
        print("\nExamples:")
        print("  spreadsheet-dl category add 'Pet Care' --color '#795548'")
        print("  spreadsheet-dl category list")
        print("  spreadsheet-dl category list --custom-only")
        print("  spreadsheet-dl category update 'Pet Care' --color '#8B4513'")
        print("  spreadsheet-dl category delete 'Pet Care'")
        print("  spreadsheet-dl category search pet")
        print("  spreadsheet-dl category suggest 'vet bill for dog'")
        return 0


def cmd_banks(args: argparse.Namespace) -> int:
    """Handle banks command."""
    from spreadsheet_dl.domains.finance.bank_formats import (
        BankFormatRegistry,
        count_formats,
    )

    registry = BankFormatRegistry()

    # Detect format from file
    if args.detect:
        if not args.detect.exists():
            print(f"Error: File not found: {args.detect}", file=sys.stderr)
            return 1

        detected = registry.detect_format(args.detect)
        if detected:
            print(f"Detected format: {detected.name}")
            print(f"  ID: {detected.id}")
            print(f"  Institution: {detected.institution}")
            print(f"  Type: {detected.format_type}")
        else:
            print("Could not auto-detect format. Try specifying with --bank option.")
        return 0

    # List or search formats
    formats = registry.list_formats(
        institution=args.search,
        format_type=args.type,
    )

    if args.json:
        print(json.dumps([f.to_dict() for f in formats], indent=2))
        return 0

    print(f"Supported Bank Formats ({count_formats()} total)")
    print("=" * 60)

    if args.search:
        print(f"Filtered by: {args.search}")
    if args.type:
        print(f"Type: {args.type}")
    print()

    # Group by institution
    by_institution: dict[str, list[Any]] = {}
    for fmt in formats:
        inst = fmt.institution or "Other"
        by_institution.setdefault(inst, []).append(fmt)

    for institution in sorted(by_institution.keys()):
        print(f"{institution}")
        for fmt in by_institution[institution]:
            print(f"  - {fmt.id}: {fmt.name} ({fmt.format_type})")
        print()

    print("Use with: spreadsheet-dl import data.csv --bank <format_id>")
    return 0


def cmd_currency(args: argparse.Namespace) -> int:
    """Handle currency command."""
    from spreadsheet_dl.domains.finance.currency import (
        CurrencyConverter,
        get_currency,
        list_currencies,
    )

    # List currencies
    if args.list:
        currencies = list_currencies()

        if args.json:
            print(
                json.dumps(
                    [
                        {"code": c.code, "name": c.name, "symbol": c.symbol}
                        for c in currencies
                    ],
                    indent=2,
                )
            )
            return 0

        print("Supported Currencies")
        print("=" * 60)
        for curr in currencies:
            print(f"  {curr.code}  {curr.symbol:>4}  {curr.name}")
        return 0

    # Convert currency
    if args.amount and args.to_currency:
        from decimal import Decimal

        converter = CurrencyConverter()
        result = converter.convert(
            Decimal(str(args.amount)),
            args.from_currency,
            args.to_currency,
        )

        from_curr = get_currency(args.from_currency)
        to_curr = get_currency(args.to_currency)

        if args.json:
            print(
                json.dumps(
                    {
                        "from": {"amount": args.amount, "currency": args.from_currency},
                        "to": {"amount": float(result), "currency": args.to_currency},
                    },
                    indent=2,
                )
            )
        else:
            from_formatted = from_curr.format(Decimal(str(args.amount)))
            to_formatted = to_curr.format(result)
            print(f"{from_formatted} = {to_formatted}")

        return 0

    # Show help
    print("Currency Conversion")
    print("=" * 40)
    print("\nUsage:")
    print("  spreadsheet-dl currency --list")
    print("  spreadsheet-dl currency 100 --from USD --to EUR")
    print()
    print("Examples:")
    print("  spreadsheet-dl currency 1000 --to EUR")
    print("  spreadsheet-dl currency 50 --from GBP --to USD")

    return 0


def cmd_alerts(args: argparse.Namespace) -> int:
    """Handle alerts command."""
    from spreadsheet_dl.domains.finance.alerts import AlertMonitor, AlertSeverity
    from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    analyzer = BudgetAnalyzer(args.file)
    monitor = AlertMonitor(analyzer)
    alerts = monitor.check_all()

    if args.critical_only:
        alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]

    if args.json:
        print(monitor.to_json())
        return 0

    if not alerts:
        print("No alerts at this time.")
        return 0

    print(monitor.format_text())

    return 0


def cmd_templates(args: argparse.Namespace) -> int:
    """Handle templates command.

    Note: Templates have been removed in favor of examples.
    Users should refer to the examples directory for sample spreadsheets.
    """
    if args.json:
        print(
            json.dumps(
                {
                    "message": "Templates are no longer available. See examples directory."
                },
                indent=2,
            )
        )
        return 0

    print("Templates")
    print("=" * 60)
    print()
    print("Templates have been removed from SpreadsheetDL.")
    print()
    print("Instead, users are encouraged to:")
    print("  1. Review the examples/ directory for sample spreadsheets")
    print("  2. Use the domain-specific formulas and functions directly")
    print("  3. Create custom spreadsheets using the builder API")
    print()
    print("For budget generation, use: spreadsheet-dl generate")

    return 0


def cmd_themes(args: argparse.Namespace) -> int:
    """Handle themes command."""
    # Built-in themes with descriptions
    themes_info = [
        {
            "name": "default",
            "display_name": "Default Finance Theme",
            "description": "Clean professional theme for budget spreadsheets",
            "colors": "Blue headers, green/red status indicators",
        },
        {
            "name": "corporate",
            "display_name": "Corporate Theme",
            "description": "Professional corporate styling for business use",
            "colors": "Navy blue headers, brown accents",
        },
        {
            "name": "minimal",
            "display_name": "Minimal Theme",
            "description": "Clean minimal design for focused work",
            "colors": "Gray headers, subtle borders, muted colors",
        },
        {
            "name": "dark",
            "display_name": "Dark Theme",
            "description": "Dark mode theme for reduced eye strain",
            "colors": "Dark backgrounds, light text, blue accents",
        },
        {
            "name": "high_contrast",
            "display_name": "High Contrast Theme",
            "description": "High contrast theme for accessibility",
            "colors": "Bold colors, large fonts, strong borders",
        },
    ]

    if args.json:
        print(json.dumps(themes_info, indent=2))
        return 0

    print("Available Visual Themes")
    print("=" * 60)
    print()

    for t in themes_info:
        print(f"  {t['name']}")
        print(f"    {t['display_name']}")
        print(f"    {t['description']}")
        print(f"    Style: {t['colors']}")
        print()

    print("Use: spreadsheet-dl generate --theme <theme_name>")
    print()
    print("Note: Themes require PyYAML. Install with:")
    print("  pip install 'spreadsheet-dl[config]'")

    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """Handle config command."""
    from spreadsheet_dl.config import get_config, init_config_file

    if args.init:
        path = init_config_file(args.path)
        print(f"Configuration file created: {path}")
        print("\nEdit this file to customize settings.")
        print("Note: For security, set NEXTCLOUD_PASSWORD as an environment variable.")
        return 0

    if args.show:
        config = get_config()
        print(json.dumps(config.to_dict(), indent=2))
        return 0

    # Default: show help
    print("Configuration Management")
    print("=" * 60)
    print()
    print("Commands:")
    print("  spreadsheet-dl config --init     Create a new config file")
    print("  spreadsheet-dl config --show     Show current configuration")
    print()
    print("Configuration sources (in priority order):")
    print("  1. Command-line arguments")
    print("  2. Environment variables")
    print("  3. Configuration file")
    print()
    print("Config file locations (first found is used):")
    print("  - ~/.config/spreadsheet-dl/config.yaml")
    print("  - ~/.spreadsheet-dl.yaml")
    print("  - ./.spreadsheet-dl.yaml")
    print()
    print("Environment variables:")
    print("  NEXTCLOUD_URL       - Nextcloud server URL")
    print("  NEXTCLOUD_USER      - Nextcloud username")
    print("  NEXTCLOUD_PASSWORD  - Nextcloud password/app token")
    print("  NO_COLOR            - Disable colored output")

    return 0


def cmd_plugin(args: argparse.Namespace) -> int:
    """Handle plugin command."""
    from spreadsheet_dl.plugins import get_plugin_manager

    manager = get_plugin_manager()

    if args.plugin_action == "list":
        plugins = manager.list_plugins(
            enabled_only=getattr(args, "enabled_only", False)
        )

        if getattr(args, "json", False):
            print(json.dumps(plugins, indent=2))
            return 0

        if not plugins:
            print("No plugins found.")
            print("\nTo add plugins:")
            print("  1. Create a plugin implementing PluginInterface")
            print("  2. Place it in ~/.spreadsheet-dl/plugins/ or ./plugins/")
            print("  3. Run: spreadsheet-dl plugin list")
            return 0

        print("SpreadsheetDL Plugins")
        print("=" * 60)
        print()

        enabled_plugins = [p for p in plugins if p["enabled"]]
        disabled_plugins = [p for p in plugins if not p["enabled"]]

        if enabled_plugins:
            print("Enabled Plugins:")
            print("-" * 40)
            for p in enabled_plugins:
                print(f"  ✓ {p['name']} v{p['version']}")
                if p["description"]:
                    print(f"    {p['description']}")
                if p["author"]:
                    print(f"    Author: {p['author']}")
                print()

        if disabled_plugins:
            print("Disabled Plugins:")
            print("-" * 40)
            for p in disabled_plugins:
                print(f"    {p['name']} v{p['version']}")
                if p["description"]:
                    print(f"    {p['description']}")
                if p["author"]:
                    print(f"    Author: {p['author']}")
                print()

        print(f"Total: {len(plugins)} plugin(s)")
        return 0

    elif args.plugin_action == "enable":
        try:
            # Parse config if provided
            config = None
            if hasattr(args, "config") and args.config:
                config = json.loads(args.config)

            manager.enable(args.name, config)
            print(f"Enabled plugin: {args.name}")
            return 0
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON config: {e}", file=sys.stderr)
            return 1

    elif args.plugin_action == "disable":
        manager.disable(args.name)
        print(f"Disabled plugin: {args.name}")
        return 0

    elif args.plugin_action == "info":
        plugin = manager.get_plugin(args.name)
        if plugin:
            enabled_plugin_names: list[str] = [
                p["name"] for p in manager.list_plugins(enabled_only=True)
            ]
            is_enabled = plugin.name in enabled_plugin_names

            print(f"Plugin: {plugin.name}")
            print("=" * 40)
            print(f"  Version:     {plugin.version}")
            print(f"  Author:      {plugin.author or 'N/A'}")
            print(f"  Description: {plugin.description or 'N/A'}")
            print(f"  Status:      {'Enabled' if is_enabled else 'Disabled'}")
        else:
            print(f"Plugin not found: {args.name}", file=sys.stderr)
            return 1
        return 0

    else:
        print("Usage: spreadsheet-dl plugin <list|enable|disable|info>")
        print("\nManage plugins for extending SpreadsheetDL.")
        print("\nExamples:")
        print("  spreadsheet-dl plugin list")
        print("  spreadsheet-dl plugin list --enabled-only")
        print("  spreadsheet-dl plugin enable my_plugin")
        print('  spreadsheet-dl plugin enable my_plugin --config \'{"key":"value"}\'')
        print("  spreadsheet-dl plugin disable my_plugin")
        print("  spreadsheet-dl plugin info my_plugin")
        return 0
