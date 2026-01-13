# Plaid Integration API Reference

## Overview

The `plaid_integration` module provides direct bank connection and transaction synchronization via Plaid API or similar bank aggregation services. It handles OAuth-based authentication, automatic transaction syncing, and multi-factor authentication.

**Key Features:**

- OAuth-based bank connection flow
- Transaction auto-sync with configurable schedule
- Multi-factor authentication handling
- Secure credential storage
- Multiple institution support
- Transaction categorization mapping
- Sandbox mode for development

**Module Location:** `spreadsheet_dl.domains.finance.plaid_integration`

---

## Enumerations

### PlaidEnvironment

API environments for Plaid.

```python
class PlaidEnvironment(Enum):
    SANDBOX = "sandbox"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
```

### PlaidProduct

Plaid API products.

```python
class PlaidProduct(Enum):
    TRANSACTIONS = "transactions"
    AUTH = "auth"
    IDENTITY = "identity"
    BALANCE = "balance"
    INVESTMENTS = "investments"
    LIABILITIES = "liabilities"
```

### LinkStatus

Status of a Plaid Link connection.

```python
class LinkStatus(Enum):
    PENDING = "pending"
    CONNECTED = "connected"
    REQUIRES_REAUTH = "requires_reauth"
    DISCONNECTED = "disconnected"
    ERROR = "error"
```

### SyncStatus

Status of a transaction sync operation.

```python
class SyncStatus(Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## Configuration

### PlaidConfig

Configuration for Plaid API integration.

```python
@dataclass
class PlaidConfig:
    client_id: str
    secret: str
    environment: PlaidEnvironment = PlaidEnvironment.SANDBOX
    webhook_url: str | None = None
    products: list[PlaidProduct] = field(default_factory=lambda: [PlaidProduct.TRANSACTIONS])
```

#### Methods

##### `from_env() -> PlaidConfig`

Load configuration from environment variables.

**Environment Variables:**

- `PLAID_CLIENT_ID` - Client ID (required)
- `PLAID_SECRET` - Secret key (required)
- `PLAID_ENV` - Environment (sandbox/development/production)
- `PLAID_WEBHOOK_URL` - Optional webhook URL

```python
import os
os.environ["PLAID_CLIENT_ID"] = "your_client_id"
os.environ["PLAID_SECRET"] = "your_secret"

config = PlaidConfig.from_env()
```

##### `base_url -> str`

Get the API base URL for the configured environment.

```python
url = config.base_url  # "https://sandbox.plaid.com"
```

---

## Data Models

### PlaidInstitution

Represents a financial institution in Plaid.

```python
@dataclass
class PlaidInstitution:
    institution_id: str
    name: str
    products: list[str] = field(default_factory=list)
    logo_url: str | None = None
    primary_color: str | None = None
    url: str | None = None
```

#### Methods

##### `to_dict() -> dict[str, Any]`

Convert to dictionary.

---

### PlaidAccount

Represents a bank account from Plaid.

```python
@dataclass
class PlaidAccount:
    account_id: str
    name: str
    official_name: str | None = None
    type: str = "depository"
    subtype: str = "checking"
    mask: str | None = None
    current_balance: Decimal | None = None
    available_balance: Decimal | None = None
    currency: str = "USD"
```

#### Methods

##### `to_dict() -> dict[str, Any]`

Convert to dictionary.

---

### PlaidTransaction

Represents a transaction from Plaid.

```python
@dataclass
class PlaidTransaction:
    transaction_id: str
    account_id: str
    amount: Decimal
    date: date
    name: str
    merchant_name: str | None = None
    category: list[str] = field(default_factory=list)
    pending: bool = False
    payment_channel: str = "other"
    location: dict[str, Any] = field(default_factory=dict)
    iso_currency_code: str = "USD"
```

#### Methods

##### `to_dict() -> dict[str, Any]`

Convert to dictionary.

---

### LinkToken

Plaid Link token for initiating connections.

```python
@dataclass
class LinkToken:
    link_token: str
    expiration: datetime
    request_id: str
```

#### Methods

##### `is_expired -> bool`

Check if token is expired.

---

### AccessToken

Plaid access token for a connected institution.

```python
@dataclass
class AccessToken:
    access_token: str
    item_id: str
    institution: PlaidInstitution
    accounts: list[PlaidAccount] = field(default_factory=list)
    status: LinkStatus = LinkStatus.CONNECTED
    last_sync: datetime | None = None
    error: str | None = None
```

#### Methods

##### `to_dict(include_token: bool = False) -> dict[str, Any]`

Convert to dictionary.

**Args:**

- `include_token` - Whether to include the access token (default: False for security)

---

### SyncResult

Result of a transaction sync operation.

```python
@dataclass
class SyncResult:
    status: SyncStatus
    added: int = 0
    modified: int = 0
    removed: int = 0
    transactions: list[PlaidTransaction] = field(default_factory=list)
    next_cursor: str | None = None
    has_more: bool = False
    error: str | None = None
```

#### Methods

##### `to_dict() -> dict[str, Any]`

Convert to dictionary.

---

## Core Classes

### PlaidClient

Client for Plaid API integration.

```python
class PlaidClient:
    def __init__(
        self,
        config: PlaidConfig,
        credential_store: Any | None = None,
    ) -> None
```

**Note:** This is a reference implementation that simulates Plaid API behavior in sandbox mode. For production use, install the official `plaid-python` package.

#### Methods

##### `create_link_token(user_id: str, *, products: list[PlaidProduct] | None = None, country_codes: list[str] | None = None, language: str = "en") -> LinkToken`

Create a Link token for initiating Plaid Link.

```python
client = PlaidClient(config)
link_token = client.create_link_token("user_123")
print(link_token.link_token)  # Pass to frontend
```

##### `exchange_public_token(public_token: str) -> AccessToken`

Exchange a public token for an access token (called after user completes Plaid Link flow).

```python
# After user completes Plaid Link
access_token = client.exchange_public_token(public_token)
print(f"Connected to {access_token.institution.name}")
```

##### `get_accounts(access_token: str) -> list[PlaidAccount]`

Get accounts for an access token.

```python
accounts = client.get_accounts(access_token.access_token)
for account in accounts:
    print(f"{account.name}: {account.current_balance}")
```

##### `get_balances(access_token: str, account_ids: list[str] | None = None) -> list[PlaidAccount]`

Get account balances.

```python
balances = client.get_balances(access_token.access_token)
```

##### `sync_transactions(access_token: str, cursor: str | None = None, count: int = 100) -> SyncResult`

Sync transactions using cursor-based pagination for incremental sync.

```python
result = client.sync_transactions(access_token.access_token)
print(f"Added: {result.added}, Modified: {result.modified}")
for tx in result.transactions:
    print(f"{tx.date}: {tx.name} - ${tx.amount}")
```

##### `get_transactions(access_token: str, start_date: date, end_date: date, account_ids: list[str] | None = None) -> list[PlaidTransaction]`

Get transactions for a date range.

```python
from datetime import date, timedelta

end = date.today()
start = end - timedelta(days=30)
transactions = client.get_transactions(access_token.access_token, start, end)
```

##### `refresh_transactions(access_token: str) -> bool`

Request a refresh of transactions from the institution.

```python
success = client.refresh_transactions(access_token.access_token)
```

##### `remove_item(access_token: str) -> bool`

Remove a connected item (bank connection).

```python
client.remove_item(access_token.access_token)
```

##### `search_institutions(query: str, country_codes: list[str] | None = None) -> list[PlaidInstitution]`

Search for financial institutions.

```python
results = client.search_institutions("Chase")
for inst in results:
    print(f"{inst.name} ({inst.institution_id})")
```

---

### PlaidSyncManager

Manager for Plaid sync operations.

```python
class PlaidSyncManager:
    def __init__(
        self,
        config: PlaidConfig,
        data_dir: Path | None = None,
    ) -> None
```

Handles scheduling automatic syncs, managing multiple connected items, and converting Plaid transactions to spreadsheet-dl format.

#### Methods

##### `add_connection(access_token: AccessToken) -> None`

Add a new bank connection.

```python
manager = PlaidSyncManager(config)
manager.add_connection(access_token)
```

##### `remove_connection(item_id: str) -> bool`

Remove a bank connection.

```python
removed = manager.remove_connection("item_123")
```

##### `list_connections() -> list[dict[str, Any]]`

List all bank connections.

```python
connections = manager.list_connections()
for conn in connections:
    print(f"{conn['institution']['name']}: {conn['status']}")
```

##### `sync_all() -> dict[str, SyncResult]`

Sync transactions for all connections.

```python
results = manager.sync_all()
for item_id, result in results.items():
    print(f"{item_id}: {result.added} new transactions")
```

##### `sync_connection(item_id: str) -> SyncResult`

Sync transactions for a specific connection.

```python
result = manager.sync_connection("item_123")
```

##### `convert_to_expenses(transactions: list[PlaidTransaction]) -> list[dict[str, Any]]`

Convert Plaid transactions to expense entries compatible with spreadsheet-dl.

```python
result = manager.sync_connection("item_123")
expenses = manager.convert_to_expenses(result.transactions)

for expense in expenses:
    print(f"{expense['date']}: {expense['description']} - ${expense['amount']}")
```

---

## Exceptions

### PlaidError

Base exception for Plaid integration errors.

**Error Code:** `FT-PLAID-1800`

### PlaidConnectionError

Raised when connection to Plaid fails.

**Error Code:** `FT-PLAID-1801`

```python
try:
    link_token = client.create_link_token("user_123")
except PlaidConnectionError as e:
    print(f"Connection failed: {e}")
```

### PlaidAuthError

Raised when authentication fails.

**Error Code:** `FT-PLAID-1802`

```python
try:
    access = client.exchange_public_token(bad_token)
except PlaidAuthError as e:
    print(f"Auth failed: {e}")
    if e.institution:
        print(f"Re-authenticate with {e.institution}")
```

### PlaidSyncError

Raised when transaction sync fails.

**Error Code:** `FT-PLAID-1803`

---

## Usage Examples

### Example 1: Basic Connection Flow

```python
from spreadsheet_dl.domains.finance.plaid_integration import (
    PlaidConfig,
    PlaidClient,
    PlaidEnvironment,
)

# Configure
config = PlaidConfig(
    client_id="your_client_id",
    secret="your_secret",
    environment=PlaidEnvironment.SANDBOX,
)

# Create client
client = PlaidClient(config)

# Step 1: Create Link token
link_token = client.create_link_token("user_123")

# Step 2: User completes Plaid Link in frontend
# (This would be done in your UI)

# Step 3: Exchange public token
public_token = "public-sandbox-xxx"  # From Plaid Link
access_token = client.exchange_public_token(public_token)

print(f"Connected to: {access_token.institution.name}")
print(f"Accounts: {len(access_token.accounts)}")
```

### Example 2: Sync Transactions

```python
from spreadsheet_dl.domains.finance.plaid_integration import PlaidClient

client = PlaidClient(config)

# Initial sync
result = client.sync_transactions(access_token.access_token)
print(f"Synced {result.added} transactions")

# Store cursor for next sync
cursor = result.next_cursor

# Later: incremental sync
result = client.sync_transactions(access_token.access_token, cursor=cursor)
print(f"New: {result.added}, Modified: {result.modified}")
```

### Example 3: Multi-Account Management

```python
from spreadsheet_dl.domains.finance.plaid_integration import PlaidSyncManager

manager = PlaidSyncManager(config)

# Add multiple connections
manager.add_connection(chase_access)
manager.add_connection(bofa_access)

# Sync all at once
results = manager.sync_all()

for item_id, result in results.items():
    conn = [c for c in manager.list_connections() if c['item_id'] == item_id][0]
    print(f"{conn['institution']['name']}: {result.added} new transactions")
```

### Example 4: Convert to Expenses

```python
from spreadsheet_dl.domains.finance.plaid_integration import PlaidSyncManager

manager = PlaidSyncManager(config)
result = manager.sync_connection("item_123")

# Convert to spreadsheet-dl format
expenses = manager.convert_to_expenses(result.transactions)

# Save to ODS
from spreadsheet_dl.domains.finance.ods_generator import MonthlyBudget

budget = MonthlyBudget(month=12, year=2024)
for expense in expenses:
    budget.add_expense(
        date=expense['date'],
        category=expense['category'],
        description=expense['description'],
        amount=Decimal(str(expense['amount'])),
    )
```

### Example 5: Environment Configuration

```python
import os
from spreadsheet_dl.domains.finance.plaid_integration import PlaidConfig

# Set environment variables
os.environ["PLAID_CLIENT_ID"] = "your_client_id"
os.environ["PLAID_SECRET"] = "your_secret"
os.environ["PLAID_ENV"] = "production"
os.environ["PLAID_WEBHOOK_URL"] = "https://your-domain.com/plaid-webhook"

# Load from environment
config = PlaidConfig.from_env()
print(f"Environment: {config.environment}")
print(f"Base URL: {config.base_url}")
```

### Example 6: Search Institutions

```python
client = PlaidClient(config)

# Search for bank
results = client.search_institutions("Chase")
for inst in results:
    print(f"{inst.name}")
    print(f"  ID: {inst.institution_id}")
    print(f"  Products: {', '.join(inst.products)}")
    print(f"  URL: {inst.url}")
```

### Example 7: Get Account Balances

```python
client = PlaidClient(config)

accounts = client.get_balances(access_token.access_token)
for account in accounts:
    print(f"{account.name} (...{account.mask})")
    print(f"  Current: ${account.current_balance}")
    print(f"  Available: ${account.available_balance}")
```

### Example 8: Date Range Transactions

```python
from datetime import date, timedelta

client = PlaidClient(config)

# Last 30 days
end_date = date.today()
start_date = end_date - timedelta(days=30)

transactions = client.get_transactions(
    access_token.access_token,
    start_date,
    end_date,
)

print(f"Found {len(transactions)} transactions")
for tx in transactions[:10]:
    print(f"{tx.date}: {tx.name} - ${tx.amount}")
```

### Example 9: Handle Connection Errors

```python
from spreadsheet_dl.domains.finance.plaid_integration import (
    PlaidAuthError,
    LinkStatus,
)

manager = PlaidSyncManager(config)

try:
    result = manager.sync_connection("item_123")
except PlaidAuthError:
    # Update connection status
    for conn in manager.list_connections():
        if conn['item_id'] == "item_123":
            print(f"Re-authentication required for {conn['institution']['name']}")
            # Prompt user to re-auth via Plaid Link
```

### Example 10: Transaction Categorization

```python
manager = PlaidSyncManager(config)

result = manager.sync_connection("item_123")
expenses = manager.convert_to_expenses(result.transactions)

# Group by category
from collections import defaultdict
by_category = defaultdict(list)

for expense in expenses:
    by_category[expense['category']].append(expense)

for category, items in by_category.items():
    total = sum(item['amount'] for item in items)
    print(f"{category}: ${total:.2f} ({len(items)} transactions)")
```

---

## Category Mapping

Plaid categories are automatically mapped to spreadsheet-dl expense categories:

- `"food and drink"`, `"groceries"` → `GROCERIES`
- `"restaurants"`, `"coffee"`, `"fast food"` → `DINING_OUT`
- `"transportation"`, `"gas"`, `"ride share"` → `TRANSPORTATION`
- `"entertainment"` → `ENTERTAINMENT`
- `"streaming"`, `"music"` → `SUBSCRIPTIONS`
- `"utilities"` → `UTILITIES`
- `"housing"`, `"rent"`, `"mortgage"` → `HOUSING`
- `"healthcare"`, `"pharmacy"` → `HEALTHCARE`
- `"insurance"` → `INSURANCE`
- `"clothing"` → `CLOTHING`
- `"personal care"` → `PERSONAL`
- `"education"` → `EDUCATION`
- Other → `MISCELLANEOUS`

---

## Sandbox Mode

The module includes a full sandbox implementation for testing without real bank credentials:

```python
from spreadsheet_dl.domains.finance.plaid_integration import (
    PlaidConfig,
    PlaidEnvironment,
    PlaidClient,
)

config = PlaidConfig(
    client_id="test",
    secret="test",
    environment=PlaidEnvironment.SANDBOX,
)

client = PlaidClient(config)

# Sandbox generates sample data
link_token = client.create_link_token("user_123")
access = client.exchange_public_token("public-sandbox-token")

# Returns sample transactions
transactions = client.get_transactions(
    access.access_token,
    date.today() - timedelta(days=30),
    date.today(),
)
```

**Sandbox Features:**

- Sample institutions (Chase, Bank of America, etc.)
- 3 sample accounts (checking, savings, credit)
- Generated transactions with realistic data
- Supports all API methods

---

## Production Setup

For production use:

1. **Install official Plaid SDK:**

   ```bash
   uv add plaid-python
   ```

2. **Get Plaid credentials:**
   - Sign up at https://plaid.com
   - Get client_id and secret from dashboard

3. **Configure environment:**

   ```bash
   export PLAID_CLIENT_ID="your_client_id"
   export PLAID_SECRET="your_secret"
   export PLAID_ENV="production"
   ```

4. **Implement Link UI:**
   - Use Plaid Link JavaScript library in frontend
   - Exchange public token on backend

---

## Security Notes

- **Access tokens are sensitive** - store securely (encrypted at rest)
- **Use credential_store** parameter for secure token storage
- **Webhook URL** should use HTTPS
- **Token rotation** - refresh periodically
- **Remove unused connections** to minimize exposure
