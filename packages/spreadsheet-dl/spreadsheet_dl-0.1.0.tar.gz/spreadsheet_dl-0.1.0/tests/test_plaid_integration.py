"""
Tests for Plaid API integration module.

: Bank API Integration.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from spreadsheet_dl import (
    AccessToken,
    LinkStatus,
    LinkToken,
    PlaidAccount,
    PlaidAuthError,
    PlaidClient,
    PlaidConfig,
    PlaidConnectionError,
    PlaidEnvironment,
    PlaidInstitution,
    PlaidProduct,
    PlaidSyncManager,
    PlaidTransaction,
    SyncResult,
    SyncStatus,
)

pytestmark = [pytest.mark.integration, pytest.mark.finance]


class TestPlaidConfig:
    """Tests for PlaidConfig."""

    def test_default_environment(self) -> None:
        """Test default environment is sandbox."""
        config = PlaidConfig(
            client_id="test_client",
            secret="test_secret",
        )
        assert config.environment == PlaidEnvironment.SANDBOX

    def test_base_url_sandbox(self) -> None:
        """Test sandbox URL."""
        config = PlaidConfig(
            client_id="test",
            secret="test",
            environment=PlaidEnvironment.SANDBOX,
        )
        assert config.base_url == "https://sandbox.plaid.com"

    def test_base_url_production(self) -> None:
        """Test production URL."""
        config = PlaidConfig(
            client_id="test",
            secret="test",
            environment=PlaidEnvironment.PRODUCTION,
        )
        assert config.base_url == "https://production.plaid.com"

    def test_default_products(self) -> None:
        """Test default products include transactions."""
        config = PlaidConfig(
            client_id="test",
            secret="test",
        )
        assert PlaidProduct.TRANSACTIONS in config.products


class TestPlaidClient:
    """Tests for PlaidClient sandbox mode."""

    @pytest.fixture
    def client(self) -> PlaidClient:
        """Create a test client."""
        config = PlaidConfig(
            client_id="test_client_id",
            secret="test_secret",
            environment=PlaidEnvironment.SANDBOX,
        )
        return PlaidClient(config)

    def test_create_link_token(self, client: PlaidClient) -> None:
        """Test link token creation in sandbox."""
        token = client.create_link_token("user_123")

        assert isinstance(token, LinkToken)
        assert token.link_token.startswith("link-sandbox-")
        assert not token.is_expired
        assert token.expiration > datetime.now()

    def test_exchange_public_token(self, client: PlaidClient) -> None:
        """Test public token exchange in sandbox."""
        access = client.exchange_public_token("public-sandbox-test")

        assert isinstance(access, AccessToken)
        assert access.access_token.startswith("access-sandbox-")
        assert access.item_id.startswith("item-sandbox-")
        assert access.status == LinkStatus.CONNECTED
        assert len(access.accounts) > 0

    def test_get_accounts(self, client: PlaidClient) -> None:
        """Test account retrieval in sandbox."""
        accounts = client.get_accounts("access-sandbox-test")

        assert isinstance(accounts, list)
        assert len(accounts) > 0
        assert all(isinstance(a, PlaidAccount) for a in accounts)

        # Check first account
        first = accounts[0]
        assert first.account_id
        assert first.name
        assert first.type in ("depository", "credit")

    def test_get_balances(self, client: PlaidClient) -> None:
        """Test balance retrieval in sandbox."""
        accounts = client.get_balances("access-sandbox-test")

        assert isinstance(accounts, list)
        for account in accounts:
            assert account.current_balance is not None
            assert isinstance(account.current_balance, Decimal)

    def test_sync_transactions(self, client: PlaidClient) -> None:
        """Test transaction sync in sandbox."""
        result = client.sync_transactions("access-sandbox-test")

        assert isinstance(result, SyncResult)
        assert result.status == SyncStatus.COMPLETED
        assert result.added >= 0
        assert isinstance(result.transactions, list)

    def test_get_transactions(self, client: PlaidClient) -> None:
        """Test transaction retrieval in sandbox."""
        start = date.today() - timedelta(days=30)
        end = date.today()

        transactions = client.get_transactions("access-sandbox-test", start, end)

        assert isinstance(transactions, list)
        assert all(isinstance(t, PlaidTransaction) for t in transactions)

        if transactions:
            tx = transactions[0]
            assert tx.transaction_id
            assert tx.account_id
            assert isinstance(tx.amount, Decimal)
            assert isinstance(tx.date, date)

    def test_search_institutions(self, client: PlaidClient) -> None:
        """Test institution search in sandbox."""
        results = client.search_institutions("Chase")

        assert isinstance(results, list)
        assert len(results) > 0

        inst = results[0]
        assert isinstance(inst, PlaidInstitution)
        assert "chase" in inst.name.lower()

    def test_search_institutions_no_match(self, client: PlaidClient) -> None:
        """Test institution search with no results."""
        results = client.search_institutions("NonExistentBank12345")
        assert results == []


class TestPlaidAccount:
    """Tests for PlaidAccount."""

    def test_to_dict(self) -> None:
        """Test account serialization."""
        account = PlaidAccount(
            account_id="acc_123",
            name="Test Checking",
            official_name="Test Official Name",
            type="depository",
            subtype="checking",
            mask="1234",
            current_balance=Decimal("1500.50"),
            available_balance=Decimal("1400.00"),
            currency="USD",
        )

        data = account.to_dict()

        assert data["account_id"] == "acc_123"
        assert data["name"] == "Test Checking"
        assert data["current_balance"] == 1500.50
        assert data["available_balance"] == 1400.00
        assert data["currency"] == "USD"


class TestPlaidTransaction:
    """Tests for PlaidTransaction."""

    def test_to_dict(self) -> None:
        """Test transaction serialization."""
        tx = PlaidTransaction(
            transaction_id="tx_123",
            account_id="acc_123",
            amount=Decimal("25.50"),
            date=date(2024, 1, 15),
            name="STARBUCKS",
            merchant_name="Starbucks",
            category=["Food and Drink", "Coffee"],
            pending=False,
            payment_channel="in_store",
        )

        data = tx.to_dict()

        assert data["transaction_id"] == "tx_123"
        assert data["amount"] == 25.50
        assert data["date"] == "2024-01-15"
        assert data["merchant_name"] == "Starbucks"
        assert "Coffee" in data["category"]


class TestPlaidSyncManager:
    """Tests for PlaidSyncManager."""

    @pytest.fixture
    def manager(self, tmp_path) -> PlaidSyncManager:  # type: ignore[no-untyped-def]
        """Create a test sync manager."""
        config = PlaidConfig(
            client_id="test",
            secret="test",
            environment=PlaidEnvironment.SANDBOX,
        )
        return PlaidSyncManager(config, data_dir=tmp_path)

    def test_add_connection(self, manager: PlaidSyncManager) -> None:
        """Test adding a connection."""
        access = AccessToken(
            access_token="access-test",
            item_id="item-test",
            institution=PlaidInstitution(
                institution_id="ins_1",
                name="Test Bank",
            ),
        )

        manager.add_connection(access)

        connections = manager.list_connections()
        assert len(connections) == 1
        assert connections[0]["item_id"] == "item-test"

    def test_remove_connection(self, manager: PlaidSyncManager) -> None:
        """Test removing a connection."""
        access = AccessToken(
            access_token="access-test",
            item_id="item-remove",
            institution=PlaidInstitution(
                institution_id="ins_1",
                name="Test Bank",
            ),
        )

        manager.add_connection(access)
        assert len(manager.list_connections()) == 1

        result = manager.remove_connection("item-remove")
        assert result is True
        assert len(manager.list_connections()) == 0

    def test_sync_all(self, manager: PlaidSyncManager) -> None:
        """Test syncing all connections."""
        access = AccessToken(
            access_token="access-sync-test",
            item_id="item-sync",
            institution=PlaidInstitution(
                institution_id="ins_1",
                name="Test Bank",
            ),
        )

        manager.add_connection(access)
        results = manager.sync_all()

        assert "item-sync" in results
        assert results["item-sync"].status == SyncStatus.COMPLETED

    def test_convert_to_expenses(self, manager: PlaidSyncManager) -> None:
        """Test converting Plaid transactions to expenses."""
        transactions = [
            PlaidTransaction(
                transaction_id="tx_1",
                account_id="acc_1",
                amount=Decimal("45.00"),
                date=date.today(),
                name="SHELL GAS",
                merchant_name="Shell",
                category=["Transportation", "Gas"],
            ),
            PlaidTransaction(
                transaction_id="tx_2",
                account_id="acc_1",
                amount=Decimal("12.50"),
                date=date.today(),
                name="STARBUCKS",
                merchant_name="Starbucks",
                category=["Food and Drink", "Coffee"],
            ),
        ]

        expenses = manager.convert_to_expenses(transactions)

        assert len(expenses) == 2
        assert expenses[0]["amount"] == 45.00
        assert expenses[0]["description"] == "Shell"
        assert "plaid_transaction_id" in expenses[0]


class TestPlaidErrors:
    """Tests for Plaid error handling."""

    def test_connection_error(self) -> None:
        """Test connection error."""
        error = PlaidConnectionError("Failed to connect")
        assert error.error_code == "FT-PLAID-1801"
        assert "connect" in str(error).lower()

    def test_auth_error(self) -> None:
        """Test auth error with institution."""
        error = PlaidAuthError(
            "Authentication failed",
            institution="Chase",
        )
        assert error.error_code == "FT-PLAID-1802"
        assert error.institution == "Chase"
