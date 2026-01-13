"""Additional CLI command tests for coverage improvement.

Tests specific command paths in _cli/commands.py.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from spreadsheet_dl._cli import commands
from spreadsheet_dl.exceptions import OperationCancelledError

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestCmdReport:
    """Tests for cmd_report command."""

    def test_report_file_not_found(self, tmp_path: Path) -> None:
        """Test report with non-existent file."""
        args = MagicMock()
        args.file = tmp_path / "nonexistent.ods"
        args.format = "text"

        result = commands.cmd_report(args)

        assert result == 1

    def test_report_text_format(self, tmp_path: Path) -> None:
        """Test report with text format."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.format = "text"
        args.output = None

        with patch(
            "spreadsheet_dl.domains.finance.report_generator.ReportGenerator"
        ) as mock_gen:
            mock_instance = MagicMock()
            mock_gen.return_value = mock_instance
            mock_instance.generate_text_report.return_value = "Report text"

            result = commands.cmd_report(args)

        assert result == 0


class TestCmdExpense:
    """Tests for cmd_expense command."""

    def test_expense_file_not_found(self, tmp_path: Path) -> None:
        """Test expense with non-existent file."""
        args = MagicMock()
        args.file = tmp_path / "nonexistent.ods"
        args.amount = "50"
        args.category = "Groceries"  # Use valid category
        args.description = "Lunch"
        args.date = None

        result = commands.cmd_expense(args)

        assert result == 1

    def test_expense_invalid_amount(self, tmp_path: Path) -> None:
        """Test expense with invalid amount."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.amount = "invalid"
        args.category = "Groceries"
        args.description = "Lunch"
        args.date = None

        # validate_amount will raise ValueError for invalid amounts
        with (
            patch(
                "spreadsheet_dl._cli.commands.validate_amount",
                side_effect=ValueError("Invalid amount"),
            ),
            pytest.raises(ValueError),
        ):
            commands.cmd_expense(args)


class TestCmdImport:
    """Tests for cmd_import command."""

    def test_import_file_not_found(self, tmp_path: Path) -> None:
        """Test import with non-existent file."""
        args = MagicMock()
        args.csv_file = tmp_path / "nonexistent.csv"
        args.output = tmp_path / "output.ods"
        args.bank = "chase"

        result = commands.cmd_import(args)

        assert result == 1

    def test_import_cancelled(self, tmp_path: Path) -> None:
        """Test import when user cancels."""
        from datetime import date

        from spreadsheet_dl.domains.finance.ods_generator import (
            ExpenseCategory,
            ExpenseEntry,
        )

        input_file = tmp_path / "input.csv"
        input_file.write_text("Date,Description,Amount\n2024-01-01,Test,50.00")

        # Create output file that already exists to trigger overwrite check
        output_file = tmp_path / "output.ods"
        output_file.write_bytes(b"existing")

        args = MagicMock()
        args.csv_file = input_file
        args.output = output_file
        args.bank = "chase"
        args.yes = False
        args.preview = False

        # Create a real ExpenseEntry for proper formatting
        mock_entry = ExpenseEntry(
            date=date(2024, 1, 1),
            category=ExpenseCategory.GROCERIES,
            description="Test",
            amount=Decimal("50.00"),
        )

        with (
            patch(
                "spreadsheet_dl.domains.finance.csv_import.import_bank_csv",
                return_value=[mock_entry],
            ),
            patch("spreadsheet_dl._cli.utils.confirm_action", return_value=False),
            pytest.raises(OperationCancelledError),
        ):
            commands.cmd_import(args)


class TestCmdExportDual:
    """Tests for cmd_export_dual command."""

    def test_export_dual_file_not_found(self, tmp_path: Path) -> None:
        """Test dual export with non-existent file."""
        args = MagicMock()
        args.file = tmp_path / "nonexistent.ods"
        args.output = tmp_path

        result = commands.cmd_export_dual(args)

        assert result == 1


class TestCmdBackup:
    """Tests for cmd_backup command."""

    def test_backup_no_files(self, tmp_path: Path) -> None:
        """Test backup list with no backups."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.list = True
        args.cleanup = False
        args.restore = None
        args.days = 30

        with patch("spreadsheet_dl.backup.BackupManager") as mock_mgr:
            mock_instance = MagicMock()
            mock_mgr.return_value = mock_instance
            mock_instance.list_backups.return_value = []

            result = commands.cmd_backup(args)

        assert result == 0


class TestCmdDashboard:
    """Tests for cmd_dashboard command."""

    def test_dashboard_file_not_found(self, tmp_path: Path) -> None:
        """Test dashboard with non-existent file."""
        args = MagicMock()
        args.file = tmp_path / "nonexistent.ods"

        result = commands.cmd_dashboard(args)

        assert result == 1


class TestCmdVisualize:
    """Tests for cmd_visualize command."""

    def test_visualize_file_not_found(self, tmp_path: Path) -> None:
        """Test visualize with non-existent file."""
        args = MagicMock()
        args.file = tmp_path / "nonexistent.ods"
        args.type = "spending"

        result = commands.cmd_visualize(args)

        assert result == 1


class TestCmdAccount:
    """Tests for cmd_account command."""

    def test_account_list(self, tmp_path: Path) -> None:
        """Test account list subcommand."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.account_cmd = "list"

        with patch("spreadsheet_dl.ods_editor.OdsEditor") as mock_editor:
            mock_instance = MagicMock()
            mock_editor.return_value = mock_instance
            mock_instance.list_accounts.return_value = ["Account1", "Account2"]

            result = commands.cmd_account(args)

        assert result == 0


class TestCmdCategory:
    """Tests for cmd_category command."""

    def test_category_list(self, tmp_path: Path) -> None:
        """Test category list subcommand."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.category_cmd = "list"

        with patch("spreadsheet_dl.ods_editor.OdsEditor") as mock_editor:
            mock_instance = MagicMock()
            mock_editor.return_value = mock_instance
            mock_instance.list_categories.return_value = ["Food", "Transport"]

            result = commands.cmd_category(args)

        assert result == 0


class TestCmdBanks:
    """Tests for cmd_banks command."""

    def test_banks_list(self) -> None:
        """Test banks list subcommand."""
        args = MagicMock()
        args.detect = None
        args.search = None
        args.type = None
        args.json = False

        with patch(
            "spreadsheet_dl.domains.finance.bank_formats.BankFormatRegistry"
        ) as mock_reg:
            mock_instance = MagicMock()
            mock_reg.return_value = mock_instance
            mock_instance.list_formats.return_value = []

            result = commands.cmd_banks(args)

        assert result == 0


class TestCmdCurrency:
    """Tests for cmd_currency command."""

    def test_currency_list(self) -> None:
        """Test currency list subcommand."""
        args = MagicMock()
        args.list = True
        args.json = False
        args.amount = None
        args.to_currency = None

        with patch(
            "spreadsheet_dl.domains.finance.currency.list_currencies", return_value=[]
        ):
            result = commands.cmd_currency(args)

        assert result == 0


class TestCmdTemplates:
    """Tests for cmd_templates command (deprecated)."""

    def test_templates_shows_deprecation(self) -> None:
        """Test templates command shows deprecation message."""
        args = MagicMock()
        args.json = False

        result = commands.cmd_templates(args)

        assert result == 0

    def test_templates_json(self) -> None:
        """Test templates command JSON output."""
        args = MagicMock()
        args.json = True

        result = commands.cmd_templates(args)

        assert result == 0


class TestCmdThemes:
    """Tests for cmd_themes command."""

    def test_themes_list(self) -> None:
        """Test themes list subcommand."""
        args = MagicMock()
        args.json = False

        result = commands.cmd_themes(args)

        assert result == 0


class TestCmdPlugin:
    """Tests for cmd_plugin command."""

    def test_plugin_list(self) -> None:
        """Test plugin list subcommand."""
        args = MagicMock()
        args.plugin_action = "list"
        args.enabled_only = False
        args.json = False

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_pm_func:
            mock_pm = MagicMock()
            mock_pm_func.return_value = mock_pm
            mock_pm.list_plugins.return_value = []

            result = commands.cmd_plugin(args)

        assert result == 0


# Additional comprehensive tests for better coverage


class TestCmdAnalyzeAdditional:
    """Additional tests for cmd_analyze command."""

    def test_analyze_with_category_filter(self, tmp_path: Path) -> None:
        """Test analyze with category filter."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.category = "Groceries"
        args.start_date = None
        args.end_date = None
        args.json = False

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer:
            mock_instance = MagicMock()
            mock_analyzer.return_value = mock_instance
            mock_instance.filter_by_category.return_value = MagicMock(
                empty=False, __getitem__=lambda self, key: MagicMock(sum=lambda: 100.0)
            )

            result = commands.cmd_analyze(args)

        assert result == 0

    def test_analyze_json_output(self, tmp_path: Path) -> None:
        """Test analyze with JSON output."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.category = None
        args.start_date = None
        args.end_date = None
        args.json = True

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer:
            mock_instance = MagicMock()
            mock_analyzer.return_value = mock_instance
            mock_instance.to_dict.return_value = {"test": "data"}

            result = commands.cmd_analyze(args)

        assert result == 0


class TestCmdAccountAdditional:
    """Additional tests for cmd_account command."""

    def test_account_add(self, tmp_path: Path) -> None:
        """Test account add subcommand."""
        args = MagicMock()
        args.account_action = "add"
        args.name = "Test Checking"
        args.type = "checking"
        args.institution = "Test Bank"
        args.balance = 1000.0
        args.currency = "USD"

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr:
            mock_instance = MagicMock()
            mock_mgr.return_value = mock_instance
            mock_account = MagicMock()
            mock_account.name = "Test Checking"
            mock_account.id = "test-123"
            mock_account.account_type.value = "checking"
            mock_account.balance = 1000.0
            mock_instance.add_account.return_value = mock_account

            result = commands.cmd_account(args)

        assert result == 0

    def test_account_net_worth(self, tmp_path: Path) -> None:
        """Test account net-worth subcommand."""
        args = MagicMock()
        args.account_action = "net-worth"
        args.json = False

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr:
            mock_instance = MagicMock()
            mock_mgr.return_value = mock_instance
            mock_net_worth = MagicMock()
            mock_net_worth.total_assets = 10000.0
            mock_net_worth.total_liabilities = 2000.0
            mock_net_worth.net_worth = 8000.0
            mock_net_worth.assets_by_type = {}
            mock_net_worth.liabilities_by_type = {}
            mock_instance.calculate_net_worth.return_value = mock_net_worth

            result = commands.cmd_account(args)

        assert result == 0


class TestCmdCategoryAdditional:
    """Additional tests for cmd_category command."""

    def test_category_add(self, tmp_path: Path) -> None:
        """Test category add subcommand."""
        args = MagicMock()
        args.category_action = "add"
        args.name = "Pet Care"
        args.color = "#795548"
        args.icon = ""
        args.description = ""
        args.parent = None
        args.budget = None

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr:
            mock_instance = MagicMock()
            mock_mgr.return_value = mock_instance

            result = commands.cmd_category(args)

        assert result == 0

    def test_category_search(self, tmp_path: Path) -> None:
        """Test category search subcommand."""
        args = MagicMock()
        args.category_action = "search"
        args.query = "food"
        args.json = False

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr:
            mock_instance = MagicMock()
            mock_mgr.return_value = mock_instance
            mock_instance.search_categories.return_value = []

            result = commands.cmd_category(args)

        assert result == 0


class TestCmdConfigAdditional:
    """Additional tests for cmd_config command."""

    def test_config_init(self, tmp_path: Path) -> None:
        """Test config init subcommand."""
        args = MagicMock()
        args.init = True
        args.show = False
        args.path = tmp_path / "config.yaml"

        with patch("spreadsheet_dl.config.init_config_file") as mock_init:
            mock_init.return_value = tmp_path / "config.yaml"

            result = commands.cmd_config(args)

        assert result == 0

    def test_config_show(self, tmp_path: Path) -> None:
        """Test config show subcommand."""
        args = MagicMock()
        args.init = False
        args.show = True

        with patch("spreadsheet_dl.config.get_config") as mock_get:
            mock_config = MagicMock()
            mock_config.to_dict.return_value = {"test": "config"}
            mock_get.return_value = mock_config

            result = commands.cmd_config(args)

        assert result == 0


class TestCmdExportAdditional:
    """Additional tests for cmd_export command."""

    def test_export_success(self, tmp_path: Path) -> None:
        """Test successful export."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")
        output_file = tmp_path / "budget.xlsx"

        args = MagicMock()
        args.file = test_file
        args.output = output_file
        args.format = "xlsx"
        args.yes = True

        with patch("spreadsheet_dl.export.MultiFormatExporter") as mock_exporter:
            mock_instance = MagicMock()
            mock_exporter.return_value = mock_instance
            mock_instance.export.return_value = output_file

            result = commands.cmd_export(args)

        assert result == 0


class TestCmdAlertsAdditional:
    """Additional tests for cmd_alerts command."""

    def test_alerts_with_json(self, tmp_path: Path) -> None:
        """Test alerts with JSON output."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")

        args = MagicMock()
        args.file = test_file
        args.json = True
        args.critical_only = False

        with (
            patch(
                "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
            ) as mock_analyzer,
            patch("spreadsheet_dl.domains.finance.alerts.AlertMonitor") as mock_monitor,
        ):
            mock_analyzer_instance = MagicMock()
            mock_analyzer.return_value = mock_analyzer_instance

            mock_monitor_instance = MagicMock()
            mock_monitor.return_value = mock_monitor_instance
            mock_monitor_instance.check_all.return_value = []
            mock_monitor_instance.to_json.return_value = "{}"

            result = commands.cmd_alerts(args)

        assert result == 0


class TestCmdVisualizeAdditional:
    """Additional tests for cmd_visualize command."""

    def test_visualize_dashboard(self, tmp_path: Path) -> None:
        """Test visualize with dashboard type."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")
        output_file = tmp_path / "dashboard.html"

        args = MagicMock()
        args.file = test_file
        args.output = output_file
        args.type = "dashboard"
        args.theme = "default"
        args.json = False

        with patch(
            "spreadsheet_dl.visualization.create_budget_dashboard"
        ) as mock_create:
            mock_create.return_value = "<html>dashboard</html>"

            result = commands.cmd_visualize(args)

        assert result == 0

    def test_visualize_pie_chart(self, tmp_path: Path) -> None:
        """Test visualize with pie chart."""
        test_file = tmp_path / "budget.ods"
        test_file.write_bytes(b"test")
        output_file = tmp_path / "chart.html"

        args = MagicMock()
        args.file = test_file
        args.output = output_file
        args.type = "pie"
        args.theme = "default"
        args.json = False

        with (
            patch(
                "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
            ) as mock_analyzer,
            patch("spreadsheet_dl.visualization.ChartGenerator") as mock_gen,
        ):
            mock_analyzer_instance = MagicMock()
            mock_analyzer.return_value = mock_analyzer_instance
            mock_analyzer_instance.get_category_breakdown.return_value = {
                "Groceries": 100.0
            }

            mock_gen_instance = MagicMock()
            mock_gen.return_value = mock_gen_instance
            mock_gen_instance.create_pie_chart.return_value = "<html>pie</html>"

            result = commands.cmd_visualize(args)

        assert result == 0
