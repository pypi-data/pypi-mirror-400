# Accounts API Reference

Track multiple financial accounts and balances.

## Overview

The accounts module provides comprehensive account management including:

- Multiple account types (checking, savings, credit, investment, etc.)
- Running balance tracking
- Account transfers
- Transaction linking
- Net worth calculation

## Classes

### Account

Financial account representation.

```python
from spreadsheet_dl.accounts import Account, AccountType
from decimal import Decimal

# Create a new account
account = Account.create(
    name="Primary Checking",
    account_type=AccountType.CHECKING,
    institution="Chase",
    balance=Decimal("5000.00"),
    currency="USD",
    account_number_last4="1234"
)

# Update balance
account.update_balance(Decimal("5500.00"))

# Adjust balance
account.adjust_balance(Decimal("-100.00"))  # Deduct $100

# Serialize
data = account.to_dict()
restored = Account.from_dict(data)
```

#### Class Method: `create()`

Create a new account with auto-generated ID.

```python
account = Account.create(
    name: str,
    account_type: AccountType | str,
    institution: str = "",
    balance: Decimal | float | str = 0,
    currency: str = "USD",
    account_number_last4: str = "",
    notes: str = ""
)
```

#### Attributes

| Attribute              | Type          | Description                        |
| ---------------------- | ------------- | ---------------------------------- |
| `id`                   | `str`         | Unique identifier (auto-generated) |
| `name`                 | `str`         | Display name                       |
| `account_type`         | `AccountType` | Type of account                    |
| `institution`          | `str`         | Financial institution              |
| `balance`              | `Decimal`     | Current balance                    |
| `currency`             | `str`         | Currency code (e.g., "USD")        |
| `account_number_last4` | `str`         | Last 4 digits                      |
| `notes`                | `str`         | Additional notes                   |
| `is_active`            | `bool`        | Active status                      |
| `created_at`           | `datetime`    | Creation timestamp                 |
| `updated_at`           | `datetime`    | Last update timestamp              |

---

### AccountType

Enum of financial account types.

```python
from spreadsheet_dl.accounts import AccountType

AccountType.CHECKING     # Checking account
AccountType.SAVINGS      # Savings account
AccountType.CREDIT       # Credit card (liability)
AccountType.INVESTMENT   # Investment account
AccountType.CASH         # Cash on hand
AccountType.LOAN         # Personal loan (liability)
AccountType.MORTGAGE     # Mortgage (liability)
AccountType.RETIREMENT   # 401(k), IRA, etc.
AccountType.BROKERAGE    # Brokerage account
AccountType.OTHER        # Other account type

# Properties
AccountType.CHECKING.is_asset      # True
AccountType.CREDIT.is_liability    # True
```

---

### AccountManager

Manage multiple financial accounts.

```python
from spreadsheet_dl.accounts import AccountManager, AccountType
from decimal import Decimal
from datetime import date

manager = AccountManager("accounts.json")

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
manager.transfer(
    from_account_id=checking.id,
    to_account_id=savings.id,
    amount=Decimal("500"),
    description="Monthly savings"
)

# Add transaction
manager.add_transaction(
    account_id=checking.id,
    transaction_date=date.today(),
    description="Grocery Store",
    amount=Decimal("-75.50"),
    category="Groceries"
)

# Calculate net worth
net_worth = manager.calculate_net_worth()
print(f"Net worth: ${net_worth.net_worth:,.2f}")
```

#### Constructor

```python
AccountManager(data_file: Path | str | None = None)
```

**Parameters:**

- `data_file`: Optional path to JSON file for persistence

#### Account Operations

##### `add_account()`

Add a new account.

```python
account = manager.add_account(
    name: str,
    account_type: AccountType | str,
    institution: str = "",
    balance: Decimal | float | str = 0,
    currency: str = "USD",
    account_number_last4: str = "",
    notes: str = ""
)
```

##### `get_account()` / `get_account_by_name()`

```python
account = manager.get_account(account_id)
account = manager.get_account_by_name("Primary Checking")
```

##### `list_accounts()`

List all accounts with optional filtering.

```python
accounts = manager.list_accounts(
    account_type: AccountType | None = None,
    active_only: bool = True
)
```

##### `update_account()`

Update account properties.

```python
account = manager.update_account(
    account_id: str,
    *,
    name: str | None = None,
    institution: str | None = None,
    notes: str | None = None,
    is_active: bool | None = None
)
```

##### `delete_account()` / `permanently_delete_account()`

```python
# Soft delete (marks inactive)
manager.delete_account(account_id)

# Hard delete (removes account and transactions)
manager.permanently_delete_account(account_id)
```

#### Transaction Operations

##### `add_transaction()`

Add a transaction to an account.

```python
transaction = manager.add_transaction(
    account_id: str,
    transaction_date: date,
    description: str,
    amount: Decimal | float | str,  # Positive=credit, negative=debit
    category: str = "",
    reference: str = "",
    notes: str = "",
    update_balance: bool = True
)
```

##### `get_transactions()`

Get transactions for an account.

```python
transactions = manager.get_transactions(
    account_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = None
)
```

#### Transfer Operations

##### `transfer()`

Transfer funds between accounts.

```python
transfer = manager.transfer(
    from_account_id: str,
    to_account_id: str,
    amount: Decimal | float | str,
    transfer_date: date | None = None,
    description: str = "Transfer",
    notes: str = ""
)
```

Creates linked transactions on both accounts.

##### `list_transfers()`

List transfers with optional filtering.

```python
transfers = manager.list_transfers(
    account_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None
)
```

#### Net Worth

##### `calculate_net_worth()`

Calculate net worth across all accounts.

```python
net_worth = manager.calculate_net_worth(active_only: bool = True)
# Returns NetWorth object
```

##### `get_total_balance()`

Get total balance across accounts.

```python
total = manager.get_total_balance(
    account_type: AccountType | None = None,
    currency: str | None = None
)
```

#### Export

```python
# To dictionary
data = manager.to_dict()

# To JSON string
json_str = manager.to_json(indent=2)
```

---

### AccountTransaction

Transaction linked to an account.

```python
from spreadsheet_dl.accounts import AccountTransaction
from decimal import Decimal
from datetime import date

transaction = AccountTransaction.create(
    account_id="abc123",
    transaction_date=date.today(),
    description="Coffee Shop",
    amount=Decimal("-5.50"),
    category="Dining Out"
)

# Properties
transaction.is_credit    # False (negative amount)
transaction.is_debit     # True
transaction.is_transfer  # False
```

#### Attributes

| Attribute                | Type      | Description             |
| ------------------------ | --------- | ----------------------- | ------------- |
| `id`                     | `str`     | Transaction ID          |
| `account_id`             | `str`     | Account ID              |
| `date`                   | `date`    | Transaction date        |
| `description`            | `str`     | Description             |
| `amount`                 | `Decimal` | Amount (+credit/-debit) |
| `category`               | `str`     | Category name           |
| `balance_after`          | `Decimal` | Running balance         |
| `transfer_to_account_id` | `str      | None`                   | For transfers |
| `reference`              | `str`     | Reference number        |
| `notes`                  | `str`     | Notes                   |

---

### Transfer

Account transfer representation.

```python
from spreadsheet_dl.accounts import Transfer
from decimal import Decimal
from datetime import date

transfer = Transfer.create(
    from_account_id="checking123",
    to_account_id="savings456",
    amount=Decimal("500"),
    transfer_date=date.today(),
    description="Monthly savings"
)
```

#### Attributes

| Attribute             | Type      | Description               |
| --------------------- | --------- | ------------------------- |
| `id`                  | `str`     | Transfer ID               |
| `from_account_id`     | `str`     | Source account            |
| `to_account_id`       | `str`     | Destination account       |
| `amount`              | `Decimal` | Transfer amount           |
| `date`                | `date`    | Transfer date             |
| `description`         | `str`     | Description               |
| `from_transaction_id` | `str`     | Linked debit transaction  |
| `to_transaction_id`   | `str`     | Linked credit transaction |

---

### NetWorth

Net worth calculation result.

```python
from spreadsheet_dl.accounts import NetWorth

# Returned by AccountManager.calculate_net_worth()
net_worth = manager.calculate_net_worth()

print(f"Assets: ${net_worth.total_assets:,.2f}")
print(f"Liabilities: ${net_worth.total_liabilities:,.2f}")
print(f"Net Worth: ${net_worth.net_worth:,.2f}")

# Breakdown by type
for acc_type, amount in net_worth.assets_by_type.items():
    print(f"  {acc_type.value}: ${amount:,.2f}")
```

#### Attributes

| Attribute             | Type                         | Description               |
| --------------------- | ---------------------------- | ------------------------- |
| `total_assets`        | `Decimal`                    | Sum of asset accounts     |
| `total_liabilities`   | `Decimal`                    | Sum of liability accounts |
| `net_worth`           | `Decimal`                    | Assets - Liabilities      |
| `assets_by_type`      | `dict[AccountType, Decimal]` | Asset breakdown           |
| `liabilities_by_type` | `dict[AccountType, Decimal]` | Liability breakdown       |
| `calculation_date`    | `date`                       | When calculated           |

---

## Module Functions

### `get_default_accounts()`

Get a list of common default account configurations.

```python
from spreadsheet_dl.accounts import get_default_accounts

defaults = get_default_accounts()
# [
#     {"name": "Primary Checking", "account_type": AccountType.CHECKING, ...},
#     {"name": "Savings", "account_type": AccountType.SAVINGS, ...},
#     {"name": "Emergency Fund", "account_type": AccountType.SAVINGS, ...},
#     {"name": "Credit Card", "account_type": AccountType.CREDIT, ...},
#     {"name": "401(k)", "account_type": AccountType.RETIREMENT, ...},
# ]
```

---

## Complete Example

```python
from spreadsheet_dl.accounts import AccountManager, AccountType
from decimal import Decimal
from datetime import date, timedelta

# Initialize with persistence
manager = AccountManager("my_accounts.json")

# Set up accounts
checking = manager.add_account(
    name="Chase Checking",
    account_type=AccountType.CHECKING,
    institution="Chase Bank",
    balance=Decimal("2500.00"),
    account_number_last4="4567"
)

savings = manager.add_account(
    name="Ally Savings",
    account_type=AccountType.SAVINGS,
    institution="Ally Bank",
    balance=Decimal("15000.00")
)

credit_card = manager.add_account(
    name="Chase Sapphire",
    account_type=AccountType.CREDIT,
    institution="Chase Bank",
    balance=Decimal("-1200.00")  # Amount owed
)

retirement = manager.add_account(
    name="Fidelity 401(k)",
    account_type=AccountType.RETIREMENT,
    institution="Fidelity",
    balance=Decimal("85000.00")
)

# Add some transactions
manager.add_transaction(
    account_id=checking.id,
    transaction_date=date.today(),
    description="Paycheck",
    amount=Decimal("3500.00"),
    category="Income"
)

manager.add_transaction(
    account_id=checking.id,
    transaction_date=date.today(),
    description="Rent",
    amount=Decimal("-1500.00"),
    category="Housing"
)

# Transfer to savings
manager.transfer(
    from_account_id=checking.id,
    to_account_id=savings.id,
    amount=Decimal("500.00"),
    description="Monthly savings contribution"
)

# Pay credit card
manager.transfer(
    from_account_id=checking.id,
    to_account_id=credit_card.id,
    amount=Decimal("600.00"),
    description="Credit card payment"
)

# Calculate net worth
net_worth = manager.calculate_net_worth()
print(f"\nNet Worth Summary ({net_worth.calculation_date})")
print(f"{'='*40}")
print(f"Total Assets:      ${net_worth.total_assets:>12,.2f}")
print(f"Total Liabilities: ${net_worth.total_liabilities:>12,.2f}")
print(f"{'='*40}")
print(f"Net Worth:         ${net_worth.net_worth:>12,.2f}")

print("\nAssets by Type:")
for acc_type, amount in net_worth.assets_by_type.items():
    print(f"  {acc_type.value}: ${amount:,.2f}")

print("\nLiabilities by Type:")
for acc_type, amount in net_worth.liabilities_by_type.items():
    print(f"  {acc_type.value}: ${amount:,.2f}")

# List recent transactions
print("\nRecent Transactions:")
for tx in manager.get_transactions(checking.id, limit=5):
    print(f"  {tx.date}: {tx.description} ${tx.amount:,.2f}")
```
