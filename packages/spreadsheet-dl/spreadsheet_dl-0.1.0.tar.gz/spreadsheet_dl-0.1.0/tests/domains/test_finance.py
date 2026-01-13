"""
Tests for Finance domain.

The finance domain provides comprehensive finance-specific functionality
including account management, budget analysis, multi-currency support,
bank transaction import, and financial reporting.

Note: Finance domain uses a different architecture than plugin-based domains.
It does not have a DomainPlugin class but provides modules and utilities.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from spreadsheet_dl.domains.finance import (
    BUILTIN_FORMATS,
    Account,
    AccountManager,
    AccountType,
    Alert,
    AlertConfig,
    AlertMonitor,
    AlertSeverity,
    AlertType,
    BankFormatRegistry,
    Category,
    CategoryManager,
    CurrencyConverter,
    ExpenseCategory,
    get_default_accounts,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.finance]

# ============================================================================
# Account Management Tests
# ============================================================================


class TestAccountManagement:
    """Test account management functionality."""

    def test_account_creation(self) -> None:
        """Test creating an account."""
        account = Account.create(
            name="Checking Account",
            account_type=AccountType.CHECKING,
            balance=1000.0,
        )

        assert account.name == "Checking Account"
        assert account.account_type == AccountType.CHECKING
        assert account.balance == Decimal("1000.0")

    def test_default_accounts(self) -> None:
        """Test getting default accounts."""
        accounts = get_default_accounts()

        assert isinstance(accounts, list)
        assert len(accounts) > 0
        assert all(isinstance(acc, dict) for acc in accounts)


class TestAccountManager:
    """Test AccountManager."""

    def test_manager_initialization(self) -> None:
        """Test manager initializes correctly."""
        manager = AccountManager()

        assert isinstance(manager, AccountManager)
        assert len(manager.list_accounts()) >= 0

    def test_add_account(self) -> None:
        """Test adding an account."""
        manager = AccountManager()
        account = manager.add_account(
            name="Savings",
            account_type=AccountType.SAVINGS,
            balance=Decimal("5000.0"),
        )

        accounts = manager.list_accounts()

        assert "Savings" in [acc.name for acc in accounts]
        assert account.balance == Decimal("5000.0")


# ============================================================================
# Category Tests
# ============================================================================


class TestCategories:
    """Test category management."""

    def test_expense_category_enum(self) -> None:
        """Test ExpenseCategory enum."""
        assert ExpenseCategory.GROCERIES
        assert ExpenseCategory.HOUSING
        assert ExpenseCategory.TRANSPORTATION

    def test_category_creation(self) -> None:
        """Test creating a category."""
        category = Category(
            name="Groceries",
            budget_default=500.0,
        )

        assert category.name == "Groceries"
        assert category.budget_default == 500.0

    def test_category_manager(self) -> None:
        """Test CategoryManager."""
        manager = CategoryManager()

        assert isinstance(manager, CategoryManager)
        categories = manager.list_categories()
        assert isinstance(categories, list)


# ============================================================================
# Bank Format Tests
# ============================================================================


class TestBankFormats:
    """Test bank format registry."""

    def test_builtin_formats_exist(self) -> None:
        """Test builtin formats are available."""
        assert BUILTIN_FORMATS is not None
        assert isinstance(BUILTIN_FORMATS, dict)
        assert len(BUILTIN_FORMATS) > 0

    def test_bank_format_registry(self) -> None:
        """Test BankFormatRegistry."""
        registry = BankFormatRegistry()

        assert isinstance(registry, BankFormatRegistry)
        formats = registry.list_formats()
        assert isinstance(formats, list)


# ============================================================================
# Currency Tests
# ============================================================================


class TestCurrency:
    """Test currency conversion."""

    def test_currency_converter_initialization(self) -> None:
        """Test CurrencyConverter initializes."""
        converter = CurrencyConverter()

        assert isinstance(converter, CurrencyConverter)


# ============================================================================
# Alert Tests
# ============================================================================


class TestAlerts:
    """Test alert system."""

    def test_alert_creation(self) -> None:
        """Test creating an alert."""
        # Create alert with specific type and severity
        alert_type = AlertType.BUDGET_THRESHOLD
        alert_severity = AlertSeverity.WARNING

        alert = Alert(
            type=alert_type,
            title="Budget Alert",
            message="Budget exceeded",
            severity=alert_severity,
        )

        assert alert.message == "Budget exceeded"
        assert alert.severity == alert_severity
        assert alert.type == alert_type

    def test_alert_monitor_initialization(self) -> None:
        """Test AlertMonitor initializes."""
        import tempfile
        from pathlib import Path

        from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

        # Create a temporary ODS file path for testing
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Note: BudgetAnalyzer requires an actual ODS file, so we just test the type
            # In a real scenario, the file would need to exist
            analyzer = BudgetAnalyzer(tmp_path)
            config = AlertConfig()
            monitor = AlertMonitor(analyzer, config)

            assert isinstance(monitor, AlertMonitor)
        finally:
            # Clean up temp file
            if tmp_path.exists():
                tmp_path.unlink()


# ============================================================================
# Integration Tests
# ============================================================================


class TestFinanceIntegration:
    """Test finance domain integration."""

    def test_finance_imports_available(self) -> None:
        """Test all major finance components can be imported."""

        # If we got here, all imports succeeded
        assert True

    def test_finance_domain_comprehensive(self) -> None:
        """Test finance domain provides comprehensive functionality."""
        # Account management
        manager = AccountManager()
        assert manager is not None

        # Categories
        cat_manager = CategoryManager()
        assert cat_manager is not None

        # Bank formats
        registry = BankFormatRegistry()
        assert registry is not None

        # All core components available
        assert True
