"""Configuration and utility CLI commands tests (banks, currency, alerts, templates, themes, config, plugin)."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from spreadsheet_dl._cli import commands

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestCmdBanks:
    """Tests for cmd_banks command."""

    def test_banks_detect(self, tmp_path: Path) -> None:
        """Test banks detect command."""
        csv_file = tmp_path / "transactions.csv"
        csv_file.write_text("dummy")

        args = argparse.Namespace(
            detect=csv_file,
            search=None,
            type=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.bank_formats.BankFormatRegistry"
        ) as mock_registry_cls:
            mock_registry = Mock()
            mock_registry_cls.return_value = mock_registry

            mock_fmt = Mock()
            mock_fmt.name = "Chase Checking"
            mock_fmt.id = "chase_checking"
            mock_fmt.institution = "Chase"
            mock_fmt.format_type = "csv"
            mock_registry.detect_format.return_value = mock_fmt

            result = commands.cmd_banks(args)

            assert result == 0

    def test_banks_detect_not_found(self, tmp_path: Path) -> None:
        """Test banks detect with no match."""
        csv_file = tmp_path / "transactions.csv"
        csv_file.write_text("dummy")

        args = argparse.Namespace(
            detect=csv_file,
            search=None,
            type=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.bank_formats.BankFormatRegistry"
        ) as mock_registry_cls:
            mock_registry = Mock()
            mock_registry_cls.return_value = mock_registry
            mock_registry.detect_format.return_value = None

            result = commands.cmd_banks(args)

            assert result == 0

    def test_banks_detect_file_not_found(self, tmp_path: Path) -> None:
        """Test banks detect with non-existent file."""
        args = argparse.Namespace(
            detect=tmp_path / "nonexistent.csv",
            search=None,
            type=None,
            json=False,
        )

        result = commands.cmd_banks(args)

        assert result == 1

    def test_banks_list(self, tmp_path: Path) -> None:
        """Test banks list command."""
        args = argparse.Namespace(
            detect=None,
            search=None,
            type=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.bank_formats.BankFormatRegistry"
        ) as mock_registry_cls:
            mock_registry = Mock()
            mock_registry_cls.return_value = mock_registry

            mock_fmt1 = Mock()
            mock_fmt1.name = "Chase Checking"
            mock_fmt1.id = "chase_checking"
            mock_fmt1.institution = "Chase"
            mock_fmt1.format_type = "csv"

            mock_fmt2 = Mock()
            mock_fmt2.name = "Wells Fargo"
            mock_fmt2.id = "wells_fargo"
            mock_fmt2.institution = "Wells Fargo"
            mock_fmt2.format_type = "csv"

            mock_registry.list_formats.return_value = [mock_fmt1, mock_fmt2]

            with patch(
                "spreadsheet_dl.domains.finance.bank_formats.count_formats"
            ) as mock_count:
                mock_count.return_value = 2

                result = commands.cmd_banks(args)

                assert result == 0

    def test_banks_list_json(self, tmp_path: Path) -> None:
        """Test banks list with JSON output."""
        args = argparse.Namespace(
            detect=None,
            search=None,
            type=None,
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.bank_formats.BankFormatRegistry"
        ) as mock_registry_cls:
            mock_registry = Mock()
            mock_registry_cls.return_value = mock_registry

            mock_fmt = Mock()
            mock_fmt.to_dict = Mock(
                return_value={"id": "chase_checking", "name": "Chase Checking"}
            )
            mock_registry.list_formats.return_value = [mock_fmt]

            result = commands.cmd_banks(args)

            assert result == 0

    def test_banks_search(self, tmp_path: Path) -> None:
        """Test banks search command."""
        args = argparse.Namespace(
            detect=None,
            search="Chase",
            type=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.bank_formats.BankFormatRegistry"
        ) as mock_registry_cls:
            mock_registry = Mock()
            mock_registry_cls.return_value = mock_registry

            mock_fmt = Mock()
            mock_fmt.name = "Chase Checking"
            mock_fmt.id = "chase_checking"
            mock_fmt.institution = "Chase"
            mock_fmt.format_type = "csv"

            mock_registry.list_formats.return_value = [mock_fmt]

            with patch(
                "spreadsheet_dl.domains.finance.bank_formats.count_formats"
            ) as mock_count:
                mock_count.return_value = 1

                result = commands.cmd_banks(args)

                assert result == 0


class TestCmdCurrency:
    """Tests for cmd_currency command."""

    def test_currency_list(self, tmp_path: Path) -> None:
        """Test currency list command."""
        args = argparse.Namespace(
            list=True,
            amount=None,
            from_currency="USD",
            to_currency=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.currency.list_currencies"
        ) as mock_list:
            from spreadsheet_dl.domains.finance.currency import Currency

            currencies = [
                Currency(code="USD", name="US Dollar", symbol="$"),
                Currency(code="EUR", name="Euro", symbol="€"),
            ]
            mock_list.return_value = currencies

            result = commands.cmd_currency(args)

            assert result == 0

    def test_currency_list_json(self, tmp_path: Path) -> None:
        """Test currency list with JSON output."""
        args = argparse.Namespace(
            list=True,
            amount=None,
            from_currency="USD",
            to_currency=None,
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.currency.list_currencies"
        ) as mock_list:
            from spreadsheet_dl.domains.finance.currency import Currency

            currencies = [
                Currency(code="USD", name="US Dollar", symbol="$"),
            ]
            mock_list.return_value = currencies

            result = commands.cmd_currency(args)

            assert result == 0

    def test_currency_convert(self, tmp_path: Path) -> None:
        """Test currency conversion."""
        from decimal import Decimal

        args = argparse.Namespace(
            list=False,
            amount="100.00",
            from_currency="USD",
            to_currency="EUR",
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.currency.CurrencyConverter"
        ) as mock_conv_cls:
            mock_conv = Mock()
            mock_conv_cls.return_value = mock_conv
            mock_conv.convert.return_value = Decimal("85.00")

            with patch(
                "spreadsheet_dl.domains.finance.currency.get_currency"
            ) as mock_get:
                from spreadsheet_dl.domains.finance.currency import Currency

                mock_get.side_effect = [
                    Currency(code="USD", name="US Dollar", symbol="$"),
                    Currency(code="EUR", name="Euro", symbol="€"),
                ]

                result = commands.cmd_currency(args)

                assert result == 0

    def test_currency_convert_json(self, tmp_path: Path) -> None:
        """Test currency conversion with JSON output."""
        from decimal import Decimal

        args = argparse.Namespace(
            list=False,
            amount="100.00",
            from_currency="USD",
            to_currency="EUR",
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.currency.CurrencyConverter"
        ) as mock_conv_cls:
            mock_conv = Mock()
            mock_conv_cls.return_value = mock_conv
            mock_conv.convert.return_value = Decimal("85.00")

            with patch(
                "spreadsheet_dl.domains.finance.currency.get_currency"
            ) as mock_get:
                from spreadsheet_dl.domains.finance.currency import Currency

                mock_get.side_effect = [
                    Currency(code="USD", name="US Dollar", symbol="$"),
                    Currency(code="EUR", name="Euro", symbol="€"),
                ]

                result = commands.cmd_currency(args)

                assert result == 0

    def test_currency_help(self, tmp_path: Path) -> None:
        """Test currency help/default."""
        args = argparse.Namespace(
            list=False,
            amount=None,
            from_currency="USD",
            to_currency=None,
            json=False,
        )

        result = commands.cmd_currency(args)

        assert result == 0


class TestCmdAlerts:
    """Tests for cmd_alerts command."""

    def test_alerts_file_not_found(self, tmp_path: Path) -> None:
        """Test alerts with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            critical_only=False,
            json=False,
        )

        result = commands.cmd_alerts(args)

        assert result == 1

    def test_alerts_none(self, tmp_path: Path) -> None:
        """Test alerts with no alerts."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            critical_only=False,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer

            with patch(
                "spreadsheet_dl.domains.finance.alerts.AlertMonitor"
            ) as mock_monitor_cls:
                mock_monitor = Mock()
                mock_monitor_cls.return_value = mock_monitor
                mock_monitor.check_all.return_value = []

                result = commands.cmd_alerts(args)

                assert result == 0

    def test_alerts_with_alerts(self, tmp_path: Path) -> None:
        """Test alerts with alerts."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            critical_only=False,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            from spreadsheet_dl.domains.finance.alerts import (
                Alert,
                AlertSeverity,
                AlertType,
            )

            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer

            with patch(
                "spreadsheet_dl.domains.finance.alerts.AlertMonitor"
            ) as mock_monitor_cls:
                mock_monitor = Mock()
                mock_monitor_cls.return_value = mock_monitor

                alerts = [
                    Alert(
                        type=AlertType.CATEGORY_OVER,
                        severity=AlertSeverity.WARNING,
                        title="Over budget",
                        category="Dining Out",
                        message="Over budget",
                    )
                ]
                mock_monitor.check_all.return_value = alerts
                mock_monitor.format_text.return_value = "Alerts:\n  - Over budget"

                result = commands.cmd_alerts(args)

                assert result == 0

    def test_alerts_critical_only(self, tmp_path: Path) -> None:
        """Test alerts with critical_only filter."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            critical_only=True,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            from spreadsheet_dl.domains.finance.alerts import (
                Alert,
                AlertSeverity,
                AlertType,
            )

            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer

            with patch(
                "spreadsheet_dl.domains.finance.alerts.AlertMonitor"
            ) as mock_monitor_cls:
                mock_monitor = Mock()
                mock_monitor_cls.return_value = mock_monitor

                alerts = [
                    Alert(
                        type=AlertType.CATEGORY_OVER,
                        severity=AlertSeverity.WARNING,
                        title="Over budget",
                        category="Dining Out",
                        message="Over budget",
                    ),
                    Alert(
                        type=AlertType.CATEGORY_OVER,
                        severity=AlertSeverity.CRITICAL,
                        title="Critical alert",
                        category="Housing",
                        message="Critical overspend",
                    ),
                ]
                mock_monitor.check_all.return_value = alerts
                mock_monitor.format_text.return_value = "Critical alerts"

                result = commands.cmd_alerts(args)

                assert result == 0

    def test_alerts_json(self, tmp_path: Path) -> None:
        """Test alerts with JSON output."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            critical_only=False,
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer

            with patch(
                "spreadsheet_dl.domains.finance.alerts.AlertMonitor"
            ) as mock_monitor_cls:
                mock_monitor = Mock()
                mock_monitor_cls.return_value = mock_monitor
                mock_monitor.check_all.return_value = []
                mock_monitor.to_json.return_value = '{"alerts": []}'

                result = commands.cmd_alerts(args)

                assert result == 0


class TestCmdTemplates:
    """Tests for cmd_templates command (deprecated)."""

    def test_templates_shows_deprecation(self) -> None:
        """Test templates command shows deprecation message."""
        args = argparse.Namespace(json=False)
        result = commands.cmd_templates(args)
        assert result == 0

    def test_templates_json(self) -> None:
        """Test templates command JSON output."""
        args = argparse.Namespace(json=True)
        result = commands.cmd_templates(args)
        assert result == 0


class TestCmdThemes:
    """Tests for cmd_themes command."""

    def test_themes_list(self, tmp_path: Path) -> None:
        """Test themes list command."""
        args = argparse.Namespace(
            json=False,
        )

        result = commands.cmd_themes(args)

        assert result == 0

    def test_themes_list_json(self, tmp_path: Path) -> None:
        """Test themes list with JSON output."""
        args = argparse.Namespace(
            json=True,
        )

        result = commands.cmd_themes(args)

        assert result == 0


class TestCmdConfig:
    """Tests for cmd_config command."""

    def test_config_init(self, tmp_path: Path) -> None:
        """Test config init command."""
        config_file = tmp_path / "config.yaml"

        args = argparse.Namespace(
            init=True,
            show=False,
            path=config_file,
        )

        with patch("spreadsheet_dl.config.init_config_file") as mock_init:
            mock_init.return_value = config_file

            result = commands.cmd_config(args)

            assert result == 0

    def test_config_show(self, tmp_path: Path) -> None:
        """Test config show command."""
        args = argparse.Namespace(
            init=False,
            show=True,
            path=None,
        )

        with patch("spreadsheet_dl.config.get_config") as mock_get:
            mock_config = Mock()
            mock_config.to_dict = Mock(
                return_value={"theme": "default", "backup_enabled": True}
            )
            mock_get.return_value = mock_config

            result = commands.cmd_config(args)

            assert result == 0

    def test_config_help(self, tmp_path: Path) -> None:
        """Test config help/default."""
        args = argparse.Namespace(
            init=False,
            show=False,
            path=None,
        )

        result = commands.cmd_config(args)

        assert result == 0


class TestCmdPlugin:
    """Tests for cmd_plugin command."""

    def test_plugin_list(self, tmp_path: Path) -> None:
        """Test plugin list command."""
        args = argparse.Namespace(
            plugin_action="list",
            enabled_only=False,
            json=False,
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr

            plugins = [
                {
                    "name": "test_plugin",
                    "version": "1.0.0",
                    "enabled": True,
                    "description": "Test plugin",
                    "author": "Test Author",
                }
            ]
            mock_mgr.list_plugins.return_value = plugins

            result = commands.cmd_plugin(args)

            assert result == 0

    def test_plugin_list_empty(self, tmp_path: Path) -> None:
        """Test plugin list with no plugins."""
        args = argparse.Namespace(
            plugin_action="list",
            enabled_only=False,
            json=False,
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr
            mock_mgr.list_plugins.return_value = []

            result = commands.cmd_plugin(args)

            assert result == 0

    def test_plugin_list_json(self, tmp_path: Path) -> None:
        """Test plugin list with JSON output."""
        args = argparse.Namespace(
            plugin_action="list",
            enabled_only=False,
            json=True,
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr

            plugins = [
                {
                    "name": "test_plugin",
                    "version": "1.0.0",
                    "enabled": True,
                }
            ]
            mock_mgr.list_plugins.return_value = plugins

            result = commands.cmd_plugin(args)

            assert result == 0

    def test_plugin_enable(self, tmp_path: Path) -> None:
        """Test plugin enable command."""
        args = argparse.Namespace(
            plugin_action="enable",
            name="test_plugin",
            config=None,
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr

            result = commands.cmd_plugin(args)

            assert result == 0

    def test_plugin_enable_with_config(self, tmp_path: Path) -> None:
        """Test plugin enable with config."""
        args = argparse.Namespace(
            plugin_action="enable",
            name="test_plugin",
            config='{"key": "value"}',
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr

            result = commands.cmd_plugin(args)

            assert result == 0

    def test_plugin_enable_error(self, tmp_path: Path) -> None:
        """Test plugin enable with error."""
        args = argparse.Namespace(
            plugin_action="enable",
            name="nonexistent",
            config=None,
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr
            mock_mgr.enable.side_effect = ValueError("Plugin not found")

            result = commands.cmd_plugin(args)

            assert result == 1

    def test_plugin_enable_invalid_json(self, tmp_path: Path) -> None:
        """Test plugin enable with invalid JSON config."""
        args = argparse.Namespace(
            plugin_action="enable",
            name="test_plugin",
            config="not valid json",
        )

        result = commands.cmd_plugin(args)

        assert result == 1

    def test_plugin_disable(self, tmp_path: Path) -> None:
        """Test plugin disable command."""
        args = argparse.Namespace(
            plugin_action="disable",
            name="test_plugin",
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr

            result = commands.cmd_plugin(args)

            assert result == 0

    def test_plugin_info(self, tmp_path: Path) -> None:
        """Test plugin info command."""
        args = argparse.Namespace(
            plugin_action="info",
            name="test_plugin",
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr

            mock_plugin = Mock()
            mock_plugin.name = "test_plugin"
            mock_plugin.version = "1.0.0"
            mock_plugin.author = "Test Author"
            mock_plugin.description = "Test plugin"
            mock_mgr.get_plugin.return_value = mock_plugin
            mock_mgr.list_plugins.return_value = [
                {"name": "test_plugin", "enabled": True}
            ]

            result = commands.cmd_plugin(args)

            assert result == 0

    def test_plugin_info_not_found(self, tmp_path: Path) -> None:
        """Test plugin info for non-existent plugin."""
        args = argparse.Namespace(
            plugin_action="info",
            name="nonexistent",
        )

        with patch("spreadsheet_dl.plugins.get_plugin_manager") as mock_get_mgr:
            mock_mgr = Mock()
            mock_get_mgr.return_value = mock_mgr
            mock_mgr.get_plugin.return_value = None

            result = commands.cmd_plugin(args)

            assert result == 1

    def test_plugin_unknown_action(self, tmp_path: Path) -> None:
        """Test plugin with unknown action."""
        args = argparse.Namespace(
            plugin_action="unknown",
        )

        result = commands.cmd_plugin(args)

        assert result == 0  # Shows help
