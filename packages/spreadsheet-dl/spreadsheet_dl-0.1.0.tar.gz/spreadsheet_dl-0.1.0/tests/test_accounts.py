"""
Tests for Account Management module.

: Account Management
"""

from __future__ import annotations

import json
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from spreadsheet_dl import (
    Account,
    AccountManager,
    AccountTransaction,
    AccountType,
    NetWorth,
    Transfer,
    get_default_accounts,
)

pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestAccountType:
    """Tests for AccountType enum."""

    def test_liability_types(self) -> None:
        """Test that liability types are correctly identified."""
        assert AccountType.CREDIT.is_liability
        assert AccountType.LOAN.is_liability
        assert AccountType.MORTGAGE.is_liability

    def test_asset_types(self) -> None:
        """Test that asset types are correctly identified."""
        assert AccountType.CHECKING.is_asset
        assert AccountType.SAVINGS.is_asset
        assert AccountType.INVESTMENT.is_asset
        assert AccountType.RETIREMENT.is_asset
        assert AccountType.CASH.is_asset

    def test_all_types_have_values(self) -> None:
        """Test that all account types have display values."""
        for account_type in AccountType:
            assert account_type.value
            assert isinstance(account_type.value, str)


class TestAccount:
    """Tests for Account dataclass."""

    def test_create_account(self) -> None:
        """Test creating an account with factory method."""
        account = Account.create(
            name="Test Checking",
            account_type=AccountType.CHECKING,
            institution="Test Bank",
            balance=Decimal("1000.00"),
        )

        assert account.id
        assert len(account.id) == 8
        assert account.name == "Test Checking"
        assert account.account_type == AccountType.CHECKING
        assert account.institution == "Test Bank"
        assert account.balance == Decimal("1000.00")
        assert account.currency == "USD"
        assert account.is_active

    def test_create_account_with_string_type(self) -> None:
        """Test creating account with string type."""
        account = Account.create(
            name="Test Savings",
            account_type="Savings",
            balance="500.00",
        )

        assert account.account_type == AccountType.SAVINGS
        assert account.balance == Decimal("500.00")

    def test_create_account_with_float_balance(self) -> None:
        """Test creating account with float balance."""
        account = Account.create(
            name="Test",
            account_type=AccountType.CHECKING,
            balance=1234.56,
        )

        assert account.balance == Decimal("1234.56")

    def test_update_balance(self) -> None:
        """Test updating account balance."""
        account = Account.create(
            name="Test",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000"),
        )

        original_updated = account.updated_at
        account.update_balance(Decimal("1500"))

        assert account.balance == Decimal("1500")
        assert account.updated_at > original_updated

    def test_adjust_balance(self) -> None:
        """Test adjusting account balance."""
        account = Account.create(
            name="Test",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000"),
        )

        account.adjust_balance(Decimal("250"))
        assert account.balance == Decimal("1250")

        account.adjust_balance(Decimal("-100"))
        assert account.balance == Decimal("1150")

    def test_to_dict(self) -> None:
        """Test account serialization."""
        account = Account.create(
            name="Test",
            account_type=AccountType.CHECKING,
            institution="Bank",
            balance=Decimal("1000"),
        )

        data = account.to_dict()

        assert data["id"] == account.id
        assert data["name"] == "Test"
        assert data["account_type"] == "Checking"
        assert data["institution"] == "Bank"
        assert data["balance"] == "1000"
        assert data["currency"] == "USD"
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict(self) -> None:
        """Test account deserialization."""
        data = {
            "id": "abc12345",
            "name": "Test Account",
            "account_type": "Savings",
            "institution": "Test Bank",
            "balance": "5000.00",
            "currency": "USD",
            "is_active": True,
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-15T12:00:00",
        }

        account = Account.from_dict(data)

        assert account.id == "abc12345"
        assert account.name == "Test Account"
        assert account.account_type == AccountType.SAVINGS
        assert account.balance == Decimal("5000.00")


class TestAccountTransaction:
    """Tests for AccountTransaction dataclass."""

    def test_create_transaction(self) -> None:
        """Test creating a transaction."""
        tx = AccountTransaction.create(
            account_id="acc123",
            transaction_date=date(2024, 1, 15),
            description="Test purchase",
            amount=Decimal("-50.00"),
            category="Shopping",
        )

        assert tx.id
        assert tx.account_id == "acc123"
        assert tx.date == date(2024, 1, 15)
        assert tx.description == "Test purchase"
        assert tx.amount == Decimal("-50.00")
        assert tx.category == "Shopping"

    def test_is_credit_debit(self) -> None:
        """Test credit/debit identification."""
        credit = AccountTransaction.create(
            account_id="acc",
            transaction_date=date.today(),
            description="Deposit",
            amount=Decimal("100"),
        )
        assert credit.is_credit
        assert not credit.is_debit

        debit = AccountTransaction.create(
            account_id="acc",
            transaction_date=date.today(),
            description="Withdrawal",
            amount=Decimal("-50"),
        )
        assert debit.is_debit
        assert not debit.is_credit

    def test_is_transfer(self) -> None:
        """Test transfer identification."""
        regular = AccountTransaction.create(
            account_id="acc",
            transaction_date=date.today(),
            description="Purchase",
            amount=Decimal("-25"),
        )
        assert not regular.is_transfer

        transfer = AccountTransaction.create(
            account_id="acc1",
            transaction_date=date.today(),
            description="Transfer",
            amount=Decimal("-100"),
            transfer_to_account_id="acc2",
        )
        assert transfer.is_transfer


class TestTransfer:
    """Tests for Transfer dataclass."""

    def test_create_transfer(self) -> None:
        """Test creating a transfer."""
        transfer = Transfer.create(
            from_account_id="acc1",
            to_account_id="acc2",
            amount=Decimal("500"),
            transfer_date=date(2024, 1, 15),
            description="Monthly savings",
        )

        assert transfer.id
        assert transfer.from_account_id == "acc1"
        assert transfer.to_account_id == "acc2"
        assert transfer.amount == Decimal("500")
        assert transfer.date == date(2024, 1, 15)
        assert transfer.description == "Monthly savings"

    def test_create_transfer_requires_positive_amount(self) -> None:
        """Test that transfer requires positive amount."""
        with pytest.raises(ValueError, match="positive"):
            Transfer.create(
                from_account_id="acc1",
                to_account_id="acc2",
                amount=Decimal("-100"),
            )

    def test_create_transfer_default_date(self) -> None:
        """Test transfer with default date."""
        transfer = Transfer.create(
            from_account_id="acc1",
            to_account_id="acc2",
            amount=Decimal("100"),
        )

        assert transfer.date == date.today()


class TestAccountManager:
    """Tests for AccountManager class."""

    def test_add_account(self) -> None:
        """Test adding an account."""
        manager = AccountManager()

        account = manager.add_account(
            name="Test Checking",
            account_type=AccountType.CHECKING,
            institution="Test Bank",
            balance=Decimal("1000"),
        )

        assert account.id
        assert account.name == "Test Checking"
        assert len(manager) == 1

    def test_get_account(self) -> None:
        """Test getting an account by ID."""
        manager = AccountManager()
        account = manager.add_account(
            name="Test",
            account_type=AccountType.CHECKING,
        )

        retrieved = manager.get_account(account.id)
        assert retrieved is account

        assert manager.get_account("nonexistent") is None

    def test_get_account_by_name(self) -> None:
        """Test getting an account by name."""
        manager = AccountManager()
        manager.add_account(name="Primary Checking", account_type=AccountType.CHECKING)

        account = manager.get_account_by_name("primary checking")
        assert account is not None
        assert account.name == "Primary Checking"

        assert manager.get_account_by_name("nonexistent") is None

    def test_list_accounts(self) -> None:
        """Test listing accounts."""
        manager = AccountManager()
        manager.add_account(name="Checking", account_type=AccountType.CHECKING)
        manager.add_account(name="Savings", account_type=AccountType.SAVINGS)
        manager.add_account(name="Credit", account_type=AccountType.CREDIT)

        all_accounts = manager.list_accounts()
        assert len(all_accounts) == 3

        checking_only = manager.list_accounts(account_type=AccountType.CHECKING)
        assert len(checking_only) == 1
        assert checking_only[0].account_type == AccountType.CHECKING

    def test_list_accounts_active_only(self) -> None:
        """Test listing only active accounts."""
        manager = AccountManager()
        active = manager.add_account(name="Active", account_type=AccountType.CHECKING)
        inactive = manager.add_account(
            name="Inactive", account_type=AccountType.CHECKING
        )
        manager.delete_account(inactive.id)

        accounts = manager.list_accounts(active_only=True)
        assert len(accounts) == 1
        assert accounts[0].id == active.id

        all_accounts = manager.list_accounts(active_only=False)
        assert len(all_accounts) == 2

    def test_update_account(self) -> None:
        """Test updating an account."""
        manager = AccountManager()
        account = manager.add_account(
            name="Original",
            account_type=AccountType.CHECKING,
            institution="Original Bank",
        )

        updated = manager.update_account(
            account.id,
            name="Updated Name",
            institution="New Bank",
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.institution == "New Bank"

    def test_delete_account(self) -> None:
        """Test soft deleting an account."""
        manager = AccountManager()
        account = manager.add_account(name="Test", account_type=AccountType.CHECKING)

        result = manager.delete_account(account.id)
        assert result is True

        # Account still exists but is inactive
        retrieved = manager.get_account(account.id)
        assert retrieved is not None
        assert not retrieved.is_active

    def test_permanently_delete_account(self) -> None:
        """Test permanently deleting an account."""
        manager = AccountManager()
        account = manager.add_account(name="Test", account_type=AccountType.CHECKING)
        manager.add_transaction(
            account.id,
            date.today(),
            "Test transaction",
            Decimal("-50"),
        )

        result = manager.permanently_delete_account(account.id)
        assert result is True
        assert manager.get_account(account.id) is None
        assert len(manager) == 0

    def test_add_transaction(self) -> None:
        """Test adding a transaction."""
        manager = AccountManager()
        account = manager.add_account(
            name="Test",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000"),
        )

        tx = manager.add_transaction(
            account_id=account.id,
            transaction_date=date(2024, 1, 15),
            description="Purchase",
            amount=Decimal("-50"),
            category="Shopping",
        )

        assert tx is not None
        assert tx.amount == Decimal("-50")
        assert tx.balance_after == Decimal("950")

        # Check account balance was updated
        assert account.balance == Decimal("950")

    def test_add_transaction_invalid_account(self) -> None:
        """Test adding transaction to nonexistent account."""
        manager = AccountManager()

        tx = manager.add_transaction(
            account_id="nonexistent",
            transaction_date=date.today(),
            description="Test",
            amount=Decimal("-50"),
        )

        assert tx is None

    def test_get_transactions(self) -> None:
        """Test getting transactions for an account."""
        manager = AccountManager()
        account = manager.add_account(name="Test", account_type=AccountType.CHECKING)

        manager.add_transaction(account.id, date(2024, 1, 10), "Tx 1", Decimal("-10"))
        manager.add_transaction(account.id, date(2024, 1, 15), "Tx 2", Decimal("-20"))
        manager.add_transaction(account.id, date(2024, 1, 20), "Tx 3", Decimal("-30"))

        all_tx = manager.get_transactions(account.id)
        assert len(all_tx) == 3
        # Should be sorted newest first
        assert all_tx[0].date == date(2024, 1, 20)

        # Filter by date range
        filtered = manager.get_transactions(
            account.id,
            start_date=date(2024, 1, 12),
            end_date=date(2024, 1, 18),
        )
        assert len(filtered) == 1
        assert filtered[0].description == "Tx 2"

        # Limit results
        limited = manager.get_transactions(account.id, limit=2)
        assert len(limited) == 2

    def test_transfer(self) -> None:
        """Test transferring funds between accounts."""
        manager = AccountManager()
        checking = manager.add_account(
            name="Checking",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000"),
        )
        savings = manager.add_account(
            name="Savings",
            account_type=AccountType.SAVINGS,
            balance=Decimal("5000"),
        )

        transfer = manager.transfer(
            from_account_id=checking.id,
            to_account_id=savings.id,
            amount=Decimal("500"),
            description="Monthly savings transfer",
        )

        assert transfer is not None
        assert transfer.amount == Decimal("500")

        # Check balances updated
        assert checking.balance == Decimal("500")
        assert savings.balance == Decimal("5500")

        # Check transactions created
        checking_tx = manager.get_transactions(checking.id)
        assert len(checking_tx) == 1
        assert checking_tx[0].amount == Decimal("-500")
        assert checking_tx[0].is_transfer

        savings_tx = manager.get_transactions(savings.id)
        assert len(savings_tx) == 1
        assert savings_tx[0].amount == Decimal("500")

    def test_transfer_invalid_amount(self) -> None:
        """Test transfer with invalid amount."""
        manager = AccountManager()
        acc1 = manager.add_account(name="A1", account_type=AccountType.CHECKING)
        acc2 = manager.add_account(name="A2", account_type=AccountType.SAVINGS)

        with pytest.raises(ValueError, match="positive"):
            manager.transfer(acc1.id, acc2.id, Decimal("-100"))

    def test_transfer_invalid_account(self) -> None:
        """Test transfer with nonexistent account."""
        manager = AccountManager()
        acc = manager.add_account(name="Test", account_type=AccountType.CHECKING)

        result = manager.transfer(acc.id, "nonexistent", Decimal("100"))
        assert result is None

    def test_list_transfers(self) -> None:
        """Test listing transfers."""
        manager = AccountManager()
        acc1 = manager.add_account(
            name="A1", account_type=AccountType.CHECKING, balance=Decimal("1000")
        )
        acc2 = manager.add_account(name="A2", account_type=AccountType.SAVINGS)
        acc3 = manager.add_account(name="A3", account_type=AccountType.SAVINGS)

        manager.transfer(acc1.id, acc2.id, Decimal("100"), date(2024, 1, 10))
        manager.transfer(acc1.id, acc3.id, Decimal("200"), date(2024, 1, 15))

        all_transfers = manager.list_transfers()
        assert len(all_transfers) == 2

        acc1_transfers = manager.list_transfers(account_id=acc1.id)
        assert len(acc1_transfers) == 2

        acc2_transfers = manager.list_transfers(account_id=acc2.id)
        assert len(acc2_transfers) == 1

    def test_calculate_net_worth(self) -> None:
        """Test net worth calculation."""
        manager = AccountManager()
        manager.add_account(
            name="Checking",
            account_type=AccountType.CHECKING,
            balance=Decimal("5000"),
        )
        manager.add_account(
            name="Savings",
            account_type=AccountType.SAVINGS,
            balance=Decimal("10000"),
        )
        manager.add_account(
            name="Credit Card",
            account_type=AccountType.CREDIT,
            balance=Decimal("-2000"),  # Owed
        )
        manager.add_account(
            name="Mortgage",
            account_type=AccountType.MORTGAGE,
            balance=Decimal("-200000"),
        )

        net_worth = manager.calculate_net_worth()

        assert net_worth.total_assets == Decimal("15000")
        assert net_worth.total_liabilities == Decimal("202000")
        assert net_worth.net_worth == Decimal("-187000")

        assert AccountType.CHECKING in net_worth.assets_by_type
        assert AccountType.CREDIT in net_worth.liabilities_by_type

    def test_get_total_balance(self) -> None:
        """Test getting total balance."""
        manager = AccountManager()
        manager.add_account(
            name="Checking 1",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000"),
        )
        manager.add_account(
            name="Checking 2",
            account_type=AccountType.CHECKING,
            balance=Decimal("2000"),
        )
        manager.add_account(
            name="Savings",
            account_type=AccountType.SAVINGS,
            balance=Decimal("5000"),
        )

        total = manager.get_total_balance()
        assert total == Decimal("8000")

        checking_total = manager.get_total_balance(account_type=AccountType.CHECKING)
        assert checking_total == Decimal("3000")

    def test_persistence(self) -> None:
        """Test saving and loading data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "accounts.json"

            # Create and save
            manager1 = AccountManager(data_file=data_file)
            acc = manager1.add_account(
                name="Test Account",
                account_type=AccountType.CHECKING,
                balance=Decimal("1000"),
            )
            manager1.add_transaction(acc.id, date.today(), "Test", Decimal("-50"))

            # Load in new manager
            manager2 = AccountManager(data_file=data_file)
            assert len(manager2) == 1

            loaded_acc = manager2.get_account(acc.id)
            assert loaded_acc is not None
            assert loaded_acc.name == "Test Account"
            assert loaded_acc.balance == Decimal("950")

    def test_iteration(self) -> None:
        """Test iterating over accounts."""
        manager = AccountManager()
        manager.add_account(name="A1", account_type=AccountType.CHECKING)
        manager.add_account(name="A2", account_type=AccountType.SAVINGS)

        names = [acc.name for acc in manager]
        assert "A1" in names
        assert "A2" in names

    def test_to_json(self) -> None:
        """Test JSON export."""
        manager = AccountManager()
        manager.add_account(
            name="Test",
            account_type=AccountType.CHECKING,
            balance=Decimal("1000"),
        )

        json_str = manager.to_json()
        data = json.loads(json_str)

        assert "accounts" in data
        assert "transactions" in data
        assert "transfers" in data
        assert "net_worth" in data


class TestNetWorth:
    """Tests for NetWorth dataclass."""

    def test_to_dict(self) -> None:
        """Test net worth serialization."""
        net_worth = NetWorth(
            total_assets=Decimal("100000"),
            total_liabilities=Decimal("50000"),
            net_worth=Decimal("50000"),
            assets_by_type={AccountType.CHECKING: Decimal("100000")},
            liabilities_by_type={AccountType.CREDIT: Decimal("50000")},
        )

        data = net_worth.to_dict()

        assert data["total_assets"] == "100000"
        assert data["total_liabilities"] == "50000"
        assert data["net_worth"] == "50000"
        assert "Checking" in data["assets_by_type"]


class TestDefaultAccounts:
    """Tests for default account configurations."""

    def test_get_default_accounts(self) -> None:
        """Test getting default account configs."""
        defaults = get_default_accounts()

        assert len(defaults) > 0
        for config in defaults:
            assert "name" in config
            assert "account_type" in config
            assert isinstance(config["account_type"], AccountType)
