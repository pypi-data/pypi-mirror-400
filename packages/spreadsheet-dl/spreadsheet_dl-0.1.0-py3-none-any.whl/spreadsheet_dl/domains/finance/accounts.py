"""Account Management Module - Track multiple accounts and balances.

Provides comprehensive account management including:
- Multiple account types (checking, savings, credit, investment)
- Running balance tracking
- Account transfers
- Transaction linking
- Net worth calculation

"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator


class AccountType(Enum):
    """Types of financial accounts."""

    CHECKING = "Checking"
    SAVINGS = "Savings"
    CREDIT = "Credit Card"
    INVESTMENT = "Investment"
    CASH = "Cash"
    LOAN = "Loan"
    MORTGAGE = "Mortgage"
    RETIREMENT = "Retirement"
    BROKERAGE = "Brokerage"
    OTHER = "Other"

    @property
    def is_liability(self) -> bool:
        """Return True if account type represents a liability."""
        return self in (
            AccountType.CREDIT,
            AccountType.LOAN,
            AccountType.MORTGAGE,
        )

    @property
    def is_asset(self) -> bool:
        """Return True if account type represents an asset."""
        return not self.is_liability


@dataclass
class Account:
    """Financial account representation.

    Attributes:
        id: Unique identifier for the account.
        name: Display name (e.g., "Primary Checking").
        account_type: Type of account (checking, savings, etc.).
        institution: Name of the financial institution.
        balance: Current balance (positive for assets, negative OK for credit).
        currency: Currency code (default: USD).
        account_number_last4: Last 4 digits of account number (optional).
        notes: Additional notes about the account.
        is_active: Whether account is currently active.
        created_at: When the account was created.
        updated_at: When the account was last updated.
    """

    id: str
    name: str
    account_type: AccountType
    institution: str = ""
    balance: Decimal = Decimal("0.00")
    currency: str = "USD"
    account_number_last4: str = ""
    notes: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        name: str,
        account_type: AccountType | str,
        institution: str = "",
        balance: Decimal | float | str = 0,
        currency: str = "USD",
        account_number_last4: str = "",
        notes: str = "",
    ) -> Account:
        """Create a new account with auto-generated ID.

        Args:
            name: Display name for the account.
            account_type: Type of account.
            institution: Financial institution name.
            balance: Opening balance.
            currency: Currency code.
            account_number_last4: Last 4 digits of account.
            notes: Additional notes.

        Returns:
            New Account instance.
        """
        if isinstance(account_type, str):
            account_type = AccountType(account_type)

        if isinstance(balance, (float, int)):
            balance = Decimal(str(balance))
        elif isinstance(balance, str):
            balance = Decimal(balance)

        return cls(
            id=str(uuid.uuid4())[:8],
            name=name,
            account_type=account_type,
            institution=institution,
            balance=balance,
            currency=currency,
            account_number_last4=account_number_last4,
            notes=notes,
        )

    def update_balance(self, new_balance: Decimal | float | str) -> None:
        """Update the account balance.

        Args:
            new_balance: New balance value.
        """
        if isinstance(new_balance, (float, int)):
            new_balance = Decimal(str(new_balance))
        elif isinstance(new_balance, str):
            new_balance = Decimal(new_balance)

        self.balance = new_balance
        self.updated_at = datetime.now()

    def adjust_balance(self, amount: Decimal | float | str) -> None:
        """Adjust balance by a given amount.

        Args:
            amount: Amount to add (negative to subtract).
        """
        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        self.balance += amount
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert account to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "account_type": self.account_type.value,
            "institution": self.institution,
            "balance": str(self.balance),
            "currency": self.currency,
            "account_number_last4": self.account_number_last4,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Account:
        """Create account from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            account_type=AccountType(data["account_type"]),
            institution=data.get("institution", ""),
            balance=Decimal(data.get("balance", "0")),
            currency=data.get("currency", "USD"),
            account_number_last4=data.get("account_number_last4", ""),
            notes=data.get("notes", ""),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data
            else datetime.now(),
        )


@dataclass
class AccountTransaction:
    """Transaction linked to an account.

    Attributes:
        id: Unique transaction identifier.
        account_id: ID of the associated account.
        date: Transaction date.
        description: Transaction description.
        amount: Transaction amount (positive for credits, negative for debits).
        category: Expense/income category.
        balance_after: Running balance after transaction.
        transfer_to_account_id: For transfers, the destination account ID.
        reference: External reference number (check #, etc.).
        notes: Additional notes.
        created_at: When transaction was recorded.
    """

    id: str
    account_id: str
    date: date_type
    description: str
    amount: Decimal
    category: str = ""
    balance_after: Decimal = Decimal("0.00")
    transfer_to_account_id: str | None = None
    reference: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        account_id: str,
        transaction_date: date_type,
        description: str,
        amount: Decimal | float | str,
        category: str = "",
        transfer_to_account_id: str | None = None,
        reference: str = "",
        notes: str = "",
    ) -> AccountTransaction:
        """Create a new transaction with auto-generated ID."""
        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        return cls(
            id=str(uuid.uuid4())[:8],
            account_id=account_id,
            date=transaction_date,
            description=description,
            amount=amount,
            category=category,
            transfer_to_account_id=transfer_to_account_id,
            reference=reference,
            notes=notes,
        )

    @property
    def is_transfer(self) -> bool:
        """Return True if this is a transfer transaction."""
        return self.transfer_to_account_id is not None

    @property
    def is_credit(self) -> bool:
        """Return True if amount is positive (credit/deposit)."""
        return self.amount > 0

    @property
    def is_debit(self) -> bool:
        """Return True if amount is negative (debit/withdrawal)."""
        return self.amount < 0

    def to_dict(self) -> dict[str, Any]:
        """Convert transaction to dictionary representation."""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "date": self.date.isoformat(),
            "description": self.description,
            "amount": str(self.amount),
            "category": self.category,
            "balance_after": str(self.balance_after),
            "transfer_to_account_id": self.transfer_to_account_id,
            "reference": self.reference,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AccountTransaction:
        """Create transaction from dictionary representation."""
        return cls(
            id=data["id"],
            account_id=data["account_id"],
            date=date_type.fromisoformat(data["date"]),
            description=data["description"],
            amount=Decimal(data["amount"]),
            category=data.get("category", ""),
            balance_after=Decimal(data.get("balance_after", "0")),
            transfer_to_account_id=data.get("transfer_to_account_id"),
            reference=data.get("reference", ""),
            notes=data.get("notes", ""),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
        )


@dataclass
class Transfer:
    """Account transfer representation.

    Represents a movement of funds between two accounts.
    """

    id: str
    from_account_id: str
    to_account_id: str
    amount: Decimal
    date: date_type
    description: str = "Transfer"
    notes: str = ""
    from_transaction_id: str = ""
    to_transaction_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        from_account_id: str,
        to_account_id: str,
        amount: Decimal | float | str,
        transfer_date: date_type | None = None,
        description: str = "Transfer",
        notes: str = "",
    ) -> Transfer:
        """Create a new transfer."""
        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        return cls(
            id=str(uuid.uuid4())[:8],
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            date=transfer_date or date_type.today(),
            description=description,
            notes=notes,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert transfer to dictionary representation."""
        return {
            "id": self.id,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
            "amount": str(self.amount),
            "date": self.date.isoformat(),
            "description": self.description,
            "notes": self.notes,
            "from_transaction_id": self.from_transaction_id,
            "to_transaction_id": self.to_transaction_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transfer:
        """Create transfer from dictionary representation."""
        return cls(
            id=data["id"],
            from_account_id=data["from_account_id"],
            to_account_id=data["to_account_id"],
            amount=Decimal(data["amount"]),
            date=date_type.fromisoformat(data["date"]),
            description=data.get("description", "Transfer"),
            notes=data.get("notes", ""),
            from_transaction_id=data.get("from_transaction_id", ""),
            to_transaction_id=data.get("to_transaction_id", ""),
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
        )


@dataclass
class NetWorth:
    """Net worth calculation result.

    Provides breakdown of assets, liabilities, and net worth.
    """

    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    assets_by_type: dict[AccountType, Decimal]
    liabilities_by_type: dict[AccountType, Decimal]
    calculation_date: date_type = field(default_factory=date_type.today)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_assets": str(self.total_assets),
            "total_liabilities": str(self.total_liabilities),
            "net_worth": str(self.net_worth),
            "assets_by_type": {k.value: str(v) for k, v in self.assets_by_type.items()},
            "liabilities_by_type": {
                k.value: str(v) for k, v in self.liabilities_by_type.items()
            },
            "calculation_date": self.calculation_date.isoformat(),
        }


class AccountManager:
    """Manage multiple financial accounts.

    Provides CRUD operations for accounts, transaction tracking,
    transfers between accounts, and net worth calculation.

    Example:
        ```python
        manager = AccountManager()

        # Add accounts
        checking = manager.add_account(
            name="Primary Checking",
            account_type=AccountType.CHECKING,
            institution="Chase",
            balance=Decimal("5000")
        )

        savings = manager.add_account(
            name="Emergency Fund",
            account_type=AccountType.SAVINGS,
            institution="Ally",
            balance=Decimal("10000")
        )

        # Transfer between accounts
        manager.transfer(checking.id, savings.id, Decimal("500"))

        # Get net worth
        net_worth = manager.calculate_net_worth()
        print(f"Net worth: ${net_worth.net_worth:,.2f}")
        ```
    """

    def __init__(self, data_file: Path | str | None = None) -> None:
        """Initialize account manager.

        Args:
            data_file: Optional path to JSON file for persistence.
        """
        self._accounts: dict[str, Account] = {}
        self._transactions: dict[str, AccountTransaction] = {}
        self._transfers: dict[str, Transfer] = {}
        self._data_file = Path(data_file) if data_file else None

        if self._data_file and self._data_file.exists():
            self._load()

    def _load(self) -> None:
        """Load data from file."""
        if not self._data_file or not self._data_file.exists():
            return

        with open(self._data_file) as f:
            data = json.load(f)

        self._accounts = {
            acc_id: Account.from_dict(acc_data)
            for acc_id, acc_data in data.get("accounts", {}).items()
        }
        self._transactions = {
            tx_id: AccountTransaction.from_dict(tx_data)
            for tx_id, tx_data in data.get("transactions", {}).items()
        }
        self._transfers = {
            tf_id: Transfer.from_dict(tf_data)
            for tf_id, tf_data in data.get("transfers", {}).items()
        }

    def _save(self) -> None:
        """Save data to file."""
        if not self._data_file:
            return

        self._data_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "accounts": {
                acc_id: acc.to_dict() for acc_id, acc in self._accounts.items()
            },
            "transactions": {
                tx_id: tx.to_dict() for tx_id, tx in self._transactions.items()
            },
            "transfers": {tf_id: tf.to_dict() for tf_id, tf in self._transfers.items()},
        }

        with open(self._data_file, "w") as f:
            json.dump(data, f, indent=2)

    # Account CRUD Operations

    def add_account(
        self,
        name: str,
        account_type: AccountType | str,
        institution: str = "",
        balance: Decimal | float | str = 0,
        currency: str = "USD",
        account_number_last4: str = "",
        notes: str = "",
    ) -> Account:
        """Add a new account.

        Args:
            name: Account display name.
            account_type: Type of account.
            institution: Financial institution.
            balance: Opening balance.
            currency: Currency code.
            account_number_last4: Last 4 digits.
            notes: Additional notes.

        Returns:
            Created Account instance.
        """
        account = Account.create(
            name=name,
            account_type=account_type,
            institution=institution,
            balance=balance,
            currency=currency,
            account_number_last4=account_number_last4,
            notes=notes,
        )
        self._accounts[account.id] = account
        self._save()
        return account

    def get_account(self, account_id: str) -> Account | None:
        """Get account by ID."""
        return self._accounts.get(account_id)

    def get_account_by_name(self, name: str) -> Account | None:
        """Get account by name (case-insensitive)."""
        name_lower = name.lower()
        for account in self._accounts.values():
            if account.name.lower() == name_lower:
                return account
        return None

    def list_accounts(
        self,
        account_type: AccountType | None = None,
        active_only: bool = True,
    ) -> list[Account]:
        """List all accounts.

        Args:
            account_type: Filter by account type.
            active_only: Only return active accounts.

        Returns:
            List of matching accounts.
        """
        accounts = list(self._accounts.values())

        if active_only:
            accounts = [a for a in accounts if a.is_active]

        if account_type:
            accounts = [a for a in accounts if a.account_type == account_type]

        return sorted(accounts, key=lambda a: a.name)

    def update_account(
        self,
        account_id: str,
        *,
        name: str | None = None,
        institution: str | None = None,
        notes: str | None = None,
        is_active: bool | None = None,
    ) -> Account | None:
        """Update account properties.

        Args:
            account_id: ID of account to update.
            name: New name (optional).
            institution: New institution (optional).
            notes: New notes (optional).
            is_active: New active status (optional).

        Returns:
            Updated account or None if not found.
        """
        account = self._accounts.get(account_id)
        if not account:
            return None

        if name is not None:
            account.name = name
        if institution is not None:
            account.institution = institution
        if notes is not None:
            account.notes = notes
        if is_active is not None:
            account.is_active = is_active

        account.updated_at = datetime.now()
        self._save()
        return account

    def delete_account(self, account_id: str) -> bool:
        """Delete an account (soft delete - marks as inactive).

        Args:
            account_id: ID of account to delete.

        Returns:
            True if deleted, False if not found.
        """
        account = self._accounts.get(account_id)
        if not account:
            return False

        account.is_active = False
        account.updated_at = datetime.now()
        self._save()
        return True

    def permanently_delete_account(self, account_id: str) -> bool:
        """Permanently delete an account and its transactions.

        Args:
            account_id: ID of account to delete.

        Returns:
            True if deleted, False if not found.
        """
        if account_id not in self._accounts:
            return False

        # Remove transactions
        tx_ids_to_remove = [
            tx_id
            for tx_id, tx in self._transactions.items()
            if tx.account_id == account_id
        ]
        for tx_id in tx_ids_to_remove:
            del self._transactions[tx_id]

        # Remove account
        del self._accounts[account_id]
        self._save()
        return True

    # Transaction Operations

    def add_transaction(
        self,
        account_id: str,
        transaction_date: date_type,
        description: str,
        amount: Decimal | float | str,
        category: str = "",
        reference: str = "",
        notes: str = "",
        update_balance: bool = True,
    ) -> AccountTransaction | None:
        """Add a transaction to an account.

        Args:
            account_id: Account to add transaction to.
            transaction_date: Date of transaction.
            description: Transaction description.
            amount: Amount (positive for credit, negative for debit).
            category: Category name.
            reference: Reference number.
            notes: Additional notes.
            update_balance: Whether to update account balance.

        Returns:
            Created transaction or None if account not found.
        """
        account = self._accounts.get(account_id)
        if not account:
            return None

        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        transaction = AccountTransaction.create(
            account_id=account_id,
            transaction_date=transaction_date,
            description=description,
            amount=amount,
            category=category,
            reference=reference,
            notes=notes,
        )

        if update_balance:
            account.adjust_balance(amount)
            transaction.balance_after = account.balance

        self._transactions[transaction.id] = transaction
        self._save()
        return transaction

    def get_transactions(
        self,
        account_id: str,
        start_date: date_type | None = None,
        end_date: date_type | None = None,
        limit: int | None = None,
    ) -> list[AccountTransaction]:
        """Get transactions for an account.

        Args:
            account_id: Account ID.
            start_date: Filter from this date.
            end_date: Filter to this date.
            limit: Maximum number of transactions.

        Returns:
            List of transactions (newest first).
        """
        transactions = [
            tx for tx in self._transactions.values() if tx.account_id == account_id
        ]

        if start_date:
            transactions = [tx for tx in transactions if tx.date >= start_date]
        if end_date:
            transactions = [tx for tx in transactions if tx.date <= end_date]

        # Sort by date (newest first)
        transactions.sort(key=lambda tx: tx.date, reverse=True)

        if limit:
            transactions = transactions[:limit]

        return transactions

    # Transfer Operations

    def transfer(
        self,
        from_account_id: str,
        to_account_id: str,
        amount: Decimal | float | str,
        transfer_date: date_type | None = None,
        description: str = "Transfer",
        notes: str = "",
    ) -> Transfer | None:
        """Transfer funds between accounts.

        Args:
            from_account_id: Source account ID.
            to_account_id: Destination account ID.
            amount: Amount to transfer (positive).
            transfer_date: Date of transfer.
            description: Transfer description.
            notes: Additional notes.

        Returns:
            Created Transfer or None if accounts not found.
        """
        from_account = self._accounts.get(from_account_id)
        to_account = self._accounts.get(to_account_id)

        if not from_account or not to_account:
            return None

        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        transfer = Transfer.create(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            transfer_date=transfer_date,
            description=description,
            notes=notes,
        )

        # Create debit transaction on source account
        from_tx = self.add_transaction(
            account_id=from_account_id,
            transaction_date=transfer.date,
            description=f"Transfer to {to_account.name}",
            amount=-amount,
            category="Transfer",
            notes=notes,
        )

        # Create credit transaction on destination account
        to_tx = self.add_transaction(
            account_id=to_account_id,
            transaction_date=transfer.date,
            description=f"Transfer from {from_account.name}",
            amount=amount,
            category="Transfer",
            notes=notes,
        )

        if from_tx:
            transfer.from_transaction_id = from_tx.id
            from_tx.transfer_to_account_id = to_account_id

        if to_tx:
            transfer.to_transaction_id = to_tx.id
            to_tx.transfer_to_account_id = from_account_id

        self._transfers[transfer.id] = transfer
        self._save()
        return transfer

    def list_transfers(
        self,
        account_id: str | None = None,
        start_date: date_type | None = None,
        end_date: date_type | None = None,
    ) -> list[Transfer]:
        """List transfers.

        Args:
            account_id: Filter by account (source or destination).
            start_date: Filter from this date.
            end_date: Filter to this date.

        Returns:
            List of transfers.
        """
        transfers = list(self._transfers.values())

        if account_id:
            transfers = [
                t
                for t in transfers
                if t.from_account_id == account_id or t.to_account_id == account_id
            ]

        if start_date:
            transfers = [t for t in transfers if t.date >= start_date]
        if end_date:
            transfers = [t for t in transfers if t.date <= end_date]

        return sorted(transfers, key=lambda t: t.date, reverse=True)

    # Net Worth Calculation

    def calculate_net_worth(self, active_only: bool = True) -> NetWorth:
        """Calculate net worth across all accounts.

        Args:
            active_only: Only include active accounts.

        Returns:
            NetWorth calculation result.
        """
        accounts = self.list_accounts(active_only=active_only)

        total_assets = Decimal("0")
        total_liabilities = Decimal("0")
        assets_by_type: dict[AccountType, Decimal] = {}
        liabilities_by_type: dict[AccountType, Decimal] = {}

        for account in accounts:
            if account.account_type.is_asset:
                total_assets += account.balance
                assets_by_type.setdefault(account.account_type, Decimal("0"))
                assets_by_type[account.account_type] += account.balance
            else:
                # For liabilities, we store the absolute value
                # Credit cards typically have negative balance when you owe money
                liability_amount = abs(account.balance)
                total_liabilities += liability_amount
                liabilities_by_type.setdefault(account.account_type, Decimal("0"))
                liabilities_by_type[account.account_type] += liability_amount

        return NetWorth(
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=total_assets - total_liabilities,
            assets_by_type=assets_by_type,
            liabilities_by_type=liabilities_by_type,
        )

    def get_total_balance(
        self,
        account_type: AccountType | None = None,
        currency: str | None = None,
    ) -> Decimal:
        """Get total balance across accounts.

        Args:
            account_type: Filter by account type.
            currency: Filter by currency.

        Returns:
            Total balance.
        """
        accounts = self.list_accounts(account_type=account_type)

        if currency:
            accounts = [a for a in accounts if a.currency == currency]

        return sum((a.balance for a in accounts), Decimal("0"))

    # Iteration

    def __iter__(self) -> Iterator[Account]:
        """Iterate over all accounts."""
        return iter(self._accounts.values())

    def __len__(self) -> int:
        """Return number of accounts."""
        return len(self._accounts)

    # Export

    def to_dict(self) -> dict[str, Any]:
        """Export all data as dictionary."""
        return {
            "accounts": [a.to_dict() for a in self._accounts.values()],
            "transactions": [t.to_dict() for t in self._transactions.values()],
            "transfers": [t.to_dict() for t in self._transfers.values()],
            "net_worth": self.calculate_net_worth().to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Export all data as JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


def get_default_accounts() -> list[dict[str, Any]]:
    """Get a list of common default account configurations.

    Returns:
        List of account configuration dictionaries.
    """
    return [
        {
            "name": "Primary Checking",
            "account_type": AccountType.CHECKING,
            "notes": "Main checking account for daily expenses",
        },
        {
            "name": "Savings",
            "account_type": AccountType.SAVINGS,
            "notes": "General savings account",
        },
        {
            "name": "Emergency Fund",
            "account_type": AccountType.SAVINGS,
            "notes": "Emergency fund (3-6 months expenses)",
        },
        {
            "name": "Credit Card",
            "account_type": AccountType.CREDIT,
            "notes": "Primary credit card",
        },
        {
            "name": "401(k)",
            "account_type": AccountType.RETIREMENT,
            "notes": "Employer retirement account",
        },
    ]
