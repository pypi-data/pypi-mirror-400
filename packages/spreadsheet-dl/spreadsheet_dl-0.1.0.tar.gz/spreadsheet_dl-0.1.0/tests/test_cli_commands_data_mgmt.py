"""Data management CLI commands tests (upload, dashboard, visualize, account, category)."""

from __future__ import annotations

import argparse
from decimal import Decimal
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from spreadsheet_dl._cli import commands
from spreadsheet_dl.exceptions import OperationCancelledError

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestCmdUpload:
    """Tests for cmd_upload command."""

    def test_upload_file_not_found(self, tmp_path: Path) -> None:
        """Test upload with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
        )

        result = commands.cmd_upload(args)

        assert result == 1

    def test_upload_config_error(self, tmp_path: Path) -> None:
        """Test upload with configuration error."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
        )

        with patch("spreadsheet_dl.webdav_upload.NextcloudConfig.from_env") as mock_cfg:
            mock_cfg.side_effect = ValueError("Missing config")

            result = commands.cmd_upload(args)

            assert result == 1

    def test_upload_success(self, tmp_path: Path) -> None:
        """Test successful upload."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
        )

        with patch("spreadsheet_dl.webdav_upload.NextcloudConfig.from_env") as mock_cfg:
            mock_config = Mock()
            mock_config.server_url = "https://cloud.example.com"
            mock_cfg.return_value = mock_config

            with patch("spreadsheet_dl.webdav_upload.upload_budget") as mock_upload:
                mock_upload.return_value = "https://cloud.example.com/files/budget.ods"

                result = commands.cmd_upload(args)

                assert result == 0


class TestCmdDashboard:
    """Tests for cmd_dashboard command."""

    def test_dashboard_file_not_found(self, tmp_path: Path) -> None:
        """Test dashboard with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            json=False,
        )

        result = commands.cmd_dashboard(args)

        assert result == 1

    def test_dashboard_json_output(self, tmp_path: Path) -> None:
        """Test dashboard with JSON output."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.analytics.generate_dashboard"
        ) as mock_gen:
            mock_gen.return_value = {
                "budget_status": "healthy",
                "status_message": "On track",
                "total_budget": 1000.0,
                "total_spent": 500.0,
                "total_remaining": 500.0,
                "percent_used": 50.0,
                "days_remaining": 15,
                "daily_budget_remaining": 33.33,
                "top_spending": [("Groceries", 200.0)],
                "alerts": [],
                "recommendations": [],
            }

            result = commands.cmd_dashboard(args)

            assert result == 0

    def test_dashboard_text_output(self, tmp_path: Path) -> None:
        """Test dashboard with text output."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.analytics.generate_dashboard"
        ) as mock_gen:
            mock_gen.return_value = {
                "budget_status": "caution",
                "status_message": "Watch spending",
                "total_budget": 1000.0,
                "total_spent": 750.0,
                "total_remaining": 250.0,
                "percent_used": 75.0,
                "days_remaining": 10,
                "daily_budget_remaining": 25.0,
                "top_spending": [
                    ("Groceries", 300.0),
                    ("Dining Out", 250.0),
                ],
                "alerts": ["Approaching budget limit"],
                "recommendations": ["Reduce dining out expenses"],
            }

            result = commands.cmd_dashboard(args)

            assert result == 0


class TestCmdVisualize:
    """Tests for cmd_visualize command."""

    def test_visualize_file_not_found(self, tmp_path: Path) -> None:
        """Test visualize with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            output=None,
            type="dashboard",
            theme="default",
        )

        result = commands.cmd_visualize(args)

        assert result == 1

    def test_visualize_dashboard(self, tmp_path: Path) -> None:
        """Test visualize dashboard creation."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")
        output_file = tmp_path / "dashboard.html"

        args = argparse.Namespace(
            file=test_file,
            output=output_file,
            type="dashboard",
            theme="modern",
        )

        with patch(
            "spreadsheet_dl.visualization.create_budget_dashboard"
        ) as mock_create:
            mock_create.return_value = "<html>Dashboard</html>"

            result = commands.cmd_visualize(args)

            assert result == 0

    def test_visualize_pie_chart(self, tmp_path: Path) -> None:
        """Test visualize pie chart."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            output=None,
            type="pie",
            theme="default",
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer
            mock_analyzer.get_category_breakdown.return_value = {
                "Groceries": 200.0,
                "Dining Out": 150.0,
            }

            with patch("spreadsheet_dl.visualization.ChartGenerator") as mock_gen_cls:
                mock_gen = Mock()
                mock_gen_cls.return_value = mock_gen
                mock_gen.create_pie_chart.return_value = "<html>Pie chart</html>"

                result = commands.cmd_visualize(args)

                assert result == 0

    def test_visualize_bar_chart(self, tmp_path: Path) -> None:
        """Test visualize bar chart."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            output=None,
            type="bar",
            theme="dark",
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer
            mock_analyzer.get_category_breakdown.return_value = {
                "Groceries": 200.0,
            }

            with patch("spreadsheet_dl.visualization.ChartGenerator") as mock_gen_cls:
                mock_gen = Mock()
                mock_gen_cls.return_value = mock_gen
                mock_gen.create_bar_chart.return_value = "<html>Bar chart</html>"

                result = commands.cmd_visualize(args)

                assert result == 0


class TestCmdAccount:
    """Tests for cmd_account command."""

    def test_account_add(self, tmp_path: Path) -> None:
        """Test account add command."""
        args = argparse.Namespace(
            account_action="add",
            name="Primary Checking",
            type="checking",
            institution="Chase",
            balance="1000.00",
            currency="USD",
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            mock_account = Account(
                id="acc-123",
                name="Primary Checking",
                account_type=AccountType.CHECKING,
                institution="Chase",
                balance=Decimal("1000.00"),
                currency="USD",
            )
            mock_mgr.add_account.return_value = mock_account

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_list(self, tmp_path: Path) -> None:
        """Test account list command."""
        args = argparse.Namespace(
            account_action="list",
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.list_accounts.return_value = []

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_list_with_accounts(self, tmp_path: Path) -> None:
        """Test account list with accounts."""
        args = argparse.Namespace(
            account_action="list",
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            mock_account = Account(
                id="acc-123",
                name="Primary Checking",
                account_type=AccountType.CHECKING,
                institution="Chase",
                balance=Decimal("1000.00"),
                currency="USD",
            )
            mock_mgr.list_accounts.return_value = [mock_account]

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_list_json(self, tmp_path: Path) -> None:
        """Test account list with JSON output."""
        args = argparse.Namespace(
            account_action="list",
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            mock_account = Account(
                id="acc-123",
                name="Primary Checking",
                account_type=AccountType.CHECKING,
                balance=Decimal("1000.00"),
            )
            mock_account.to_dict = Mock(  # type: ignore[method-assign]
                return_value={"name": "Primary Checking", "balance": 1000.0}
            )
            mock_mgr.list_accounts.return_value = [mock_account]

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_balance(self, tmp_path: Path) -> None:
        """Test account balance command."""
        args = argparse.Namespace(
            account_action="balance",
            name="Primary Checking",
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            mock_account = Account(
                id="acc-123",
                name="Primary Checking",
                account_type=AccountType.CHECKING,
                balance=Decimal("1500.00"),
            )
            mock_mgr.get_account_by_name.return_value = mock_account

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_balance_not_found(self, tmp_path: Path) -> None:
        """Test account balance for non-existent account."""
        args = argparse.Namespace(
            account_action="balance",
            name="Nonexistent",
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.get_account_by_name.return_value = None

            result = commands.cmd_account(args)

            assert result == 1

    def test_account_balance_all(self, tmp_path: Path) -> None:
        """Test account balance for all accounts."""
        args = argparse.Namespace(
            account_action="balance",
            name=None,
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            accounts = [
                Account(
                    id=f"acc-{i}",
                    name=f"Account {i}",
                    account_type=AccountType.CHECKING,
                    balance=Decimal(str(1000.0 * i)),
                )
                for i in range(1, 4)
            ]
            mock_mgr.list_accounts.return_value = accounts

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_transfer(self, tmp_path: Path) -> None:
        """Test account transfer command."""
        args = argparse.Namespace(
            account_action="transfer",
            from_account="Checking",
            to_account="Savings",
            amount="500.00",
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            from_acc = Account(
                id="acc-1",
                name="Checking",
                account_type=AccountType.CHECKING,
                balance=Decimal("500.00"),
            )
            to_acc = Account(
                id="acc-2",
                name="Savings",
                account_type=AccountType.SAVINGS,
                balance=Decimal("1500.00"),
            )
            mock_mgr.get_account_by_name.side_effect = [from_acc, to_acc]
            mock_mgr.transfer.return_value = True

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_transfer_from_not_found(self, tmp_path: Path) -> None:
        """Test account transfer with non-existent source."""
        args = argparse.Namespace(
            account_action="transfer",
            from_account="Nonexistent",
            to_account="Savings",
            amount="500.00",
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.get_account_by_name.return_value = None

            result = commands.cmd_account(args)

            assert result == 1

    def test_account_transfer_to_not_found(self, tmp_path: Path) -> None:
        """Test account transfer with non-existent destination."""
        args = argparse.Namespace(
            account_action="transfer",
            from_account="Checking",
            to_account="Nonexistent",
            amount="500.00",
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            from_acc = Account(
                id="acc-1",
                name="Checking",
                account_type=AccountType.CHECKING,
                balance=Decimal("1000.00"),
            )
            mock_mgr.get_account_by_name.side_effect = [from_acc, None]

            result = commands.cmd_account(args)

            assert result == 1

    def test_account_transfer_failed(self, tmp_path: Path) -> None:
        """Test failed account transfer."""
        args = argparse.Namespace(
            account_action="transfer",
            from_account="Checking",
            to_account="Savings",
            amount="500.00",
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import Account, AccountType

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            from_acc = Account(
                id="acc-1",
                name="Checking",
                account_type=AccountType.CHECKING,
                balance=Decimal("1000.00"),
            )
            to_acc = Account(
                id="acc-2",
                name="Savings",
                account_type=AccountType.SAVINGS,
                balance=Decimal("500.00"),
            )
            mock_mgr.get_account_by_name.side_effect = [from_acc, to_acc]
            mock_mgr.transfer.return_value = False

            result = commands.cmd_account(args)

            assert result == 1

    def test_account_net_worth(self, tmp_path: Path) -> None:
        """Test account net-worth command."""
        args = argparse.Namespace(
            account_action="net-worth",
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import (
                AccountType,
                NetWorth,
            )

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            net_worth = NetWorth(
                total_assets=Decimal("10000.00"),
                total_liabilities=Decimal("3000.00"),
                net_worth=Decimal("7000.00"),
                assets_by_type={AccountType.CHECKING: Decimal("5000.00")},
                liabilities_by_type={AccountType.CREDIT: Decimal("3000.00")},
            )
            mock_mgr.calculate_net_worth.return_value = net_worth

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_net_worth_json(self, tmp_path: Path) -> None:
        """Test account net-worth with JSON output."""
        args = argparse.Namespace(
            account_action="net-worth",
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.accounts.AccountManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.accounts import NetWorth

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            net_worth = NetWorth(
                total_assets=Decimal("10000.00"),
                total_liabilities=Decimal("3000.00"),
                net_worth=Decimal("7000.00"),
                assets_by_type={},
                liabilities_by_type={},
            )
            net_worth.to_dict = Mock(  # type: ignore[method-assign]
                return_value={
                    "total_assets": 10000.0,
                    "total_liabilities": 3000.0,
                    "net_worth": 7000.0,
                }
            )
            mock_mgr.calculate_net_worth.return_value = net_worth

            result = commands.cmd_account(args)

            assert result == 0

    def test_account_unknown_action(self, tmp_path: Path) -> None:
        """Test account with unknown action."""
        args = argparse.Namespace(
            account_action="unknown",
        )

        result = commands.cmd_account(args)

        assert result == 0  # Shows help


class TestCmdCategory:
    """Tests for cmd_category command."""

    def test_category_add(self, tmp_path: Path) -> None:
        """Test category add command."""
        args = argparse.Namespace(
            category_action="add",
            name="Pet Care",
            color="#795548",
            icon="🐾",
            description="Pet-related expenses",
            parent=None,
            budget=100.0,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.categories import Category

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            Category(
                name="Pet Care",
                color="#795548",
                icon="🐾",
                description="Pet-related expenses",
            )
            mock_mgr.add_category.return_value = None

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_add_error(self, tmp_path: Path) -> None:
        """Test category add with error."""
        args = argparse.Namespace(
            category_action="add",
            name="Invalid",
            color="not-a-color",
            icon="",
            description="",
            parent=None,
            budget=None,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            # Simulate ValueError during Category creation
            with patch(
                "spreadsheet_dl.domains.finance.categories.Category"
            ) as mock_cat_cls:
                mock_cat_cls.side_effect = ValueError("Invalid color")

                result = commands.cmd_category(args)

                assert result == 1

    def test_category_list(self, tmp_path: Path) -> None:
        """Test category list command."""
        args = argparse.Namespace(
            category_action="list",
            json=False,
            include_hidden=False,
            custom_only=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.categories import Category

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            categories = [
                Category(name="Groceries", color="#4CAF50", is_custom=False),
                Category(name="Pet Care", color="#795548", is_custom=True),
            ]
            mock_mgr.list_categories.return_value = categories

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_list_json(self, tmp_path: Path) -> None:
        """Test category list with JSON output."""
        args = argparse.Namespace(
            category_action="list",
            json=True,
            include_hidden=False,
            custom_only=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.categories import Category

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            cat = Category(name="Groceries", color="#4CAF50")
            cat.to_dict = Mock(  # type: ignore[method-assign]
                return_value={"name": "Groceries", "color": "#4CAF50"}
            )
            mock_mgr.list_categories.return_value = [cat]

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_update(self, tmp_path: Path) -> None:
        """Test category update command."""
        args = argparse.Namespace(
            category_action="update",
            name="Pet Care",
            color="#8B4513",
            icon="🐕",
            description="Updated",
            rename=None,
            hide=False,
            unhide=False,
            budget=150.0,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.categories import Category

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            updated_cat = Category(name="Pet Care", color="#8B4513")
            mock_mgr.update_category.return_value = updated_cat

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_update_error(self, tmp_path: Path) -> None:
        """Test category update with error."""
        args = argparse.Namespace(
            category_action="update",
            name="Nonexistent",
            color=None,
            icon=None,
            description=None,
            rename=None,
            hide=False,
            unhide=False,
            budget=None,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.update_category.side_effect = KeyError("Not found")

            result = commands.cmd_category(args)

            assert result == 1

    def test_category_delete(self, tmp_path: Path) -> None:
        """Test category delete command."""
        args = argparse.Namespace(
            category_action="delete",
            name="Pet Care",
            force=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.delete_category.return_value = True

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_delete_not_found(self, tmp_path: Path) -> None:
        """Test category delete for non-existent category."""
        args = argparse.Namespace(
            category_action="delete",
            name="Nonexistent",
            force=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.delete_category.return_value = False

            result = commands.cmd_category(args)

            assert result == 1

    def test_category_delete_cancelled(self, tmp_path: Path) -> None:
        """Test category delete cancelled by user."""
        args = argparse.Namespace(
            category_action="delete",
            name="Pet Care",
            force=False,
        )

        with patch("spreadsheet_dl._cli.commands.confirm_action") as mock_confirm:
            mock_confirm.return_value = False

            with pytest.raises(OperationCancelledError):
                commands.cmd_category(args)

    def test_category_search(self, tmp_path: Path) -> None:
        """Test category search command."""
        args = argparse.Namespace(
            category_action="search",
            query="pet",
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.categories import Category

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            results = [
                Category(name="Pet Care", color="#795548", is_custom=True),
            ]
            mock_mgr.search_categories.return_value = results

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_search_no_results(self, tmp_path: Path) -> None:
        """Test category search with no results."""
        args = argparse.Namespace(
            category_action="search",
            query="nonexistent",
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.search_categories.return_value = []

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_suggest(self, tmp_path: Path) -> None:
        """Test category suggest command."""
        args = argparse.Namespace(
            category_action="suggest",
            description="vet bill for dog",
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            from spreadsheet_dl.domains.finance.categories import Category

            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            suggested = Category(name="Pet Care", color="#795548")
            mock_mgr.suggest_category.return_value = suggested

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_suggest_no_match(self, tmp_path: Path) -> None:
        """Test category suggest with no match."""
        args = argparse.Namespace(
            category_action="suggest",
            description="random text",
        )

        with patch(
            "spreadsheet_dl.domains.finance.categories.CategoryManager"
        ) as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.suggest_category.return_value = None

            result = commands.cmd_category(args)

            assert result == 0

    def test_category_unknown_action(self, tmp_path: Path) -> None:
        """Test category with unknown action."""
        args = argparse.Namespace(
            category_action="unknown",
        )

        result = commands.cmd_category(args)

        assert result == 0  # Shows help
