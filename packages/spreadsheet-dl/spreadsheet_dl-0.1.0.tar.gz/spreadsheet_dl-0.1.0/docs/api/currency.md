# Currency API Reference

## Overview

The `currency` module provides comprehensive multi-currency support including currency definitions, exchange rate management, currency conversion, and multi-currency display formatting.

**Key Features:**

- 30+ currency definitions with ISO 4217 codes
- Exchange rate management and conversion
- Custom currency formatting with symbols
- Money amount type for type-safe operations
- Default exchange rates (late 2024)
- Persistent custom rate storage

**Module Location:** `spreadsheet_dl.domains.finance.currency`

---

## Enumerations

### CurrencyCode

ISO 4217 Currency Codes.

```python
class CurrencyCode(Enum):
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CHF = "CHF"  # Swiss Franc
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    # ... 30+ currencies
```

---

## Core Classes

### Currency

Currency definition with formatting information.

```python
@dataclass(frozen=True)
class Currency:
    code: str
    name: str
    symbol: str
    decimal_places: int = 2
    symbol_position: str = "before"  # 'before' or 'after'
    thousand_separator: str = ","
    decimal_separator: str = "."
```

#### Methods

##### `format(amount: Decimal | float | str, *, show_symbol: bool = True, show_code: bool = False) -> str`

Format an amount in this currency.

```python
from spreadsheet_dl.domains.finance.currency import get_currency
from decimal import Decimal

usd = get_currency("USD")
formatted = usd.format(Decimal("1234.56"))
print(formatted)  # "$1,234.56"

# Without symbol
formatted = usd.format(Decimal("1234.56"), show_symbol=False)
print(formatted)  # "1,234.56"

# With code
formatted = usd.format(Decimal("1234.56"), show_code=True)
print(formatted)  # "$1,234.56 USD"
```

##### `parse(formatted: str) -> Decimal`

Parse a formatted currency string to Decimal.

```python
amount = usd.parse("$1,234.56")
print(amount)  # Decimal('1234.56')

# Handles negative
amount = usd.parse("-$500.00")
print(amount)  # Decimal('-500.00')
```

---

### ExchangeRate

Exchange rate between two currencies.

```python
@dataclass
class ExchangeRate:
    from_currency: str
    to_currency: str
    rate: Decimal
    date: date = field(default_factory=date.today)
    source: str = "manual"
```

#### Methods

##### `reverse() -> ExchangeRate`

Get the reverse exchange rate.

```python
from decimal import Decimal

rate = ExchangeRate("USD", "EUR", Decimal("0.92"))
reverse = rate.reverse()
print(f"1 EUR = {reverse.rate} USD")  # 1 EUR = 1.087 USD
```

##### `to_dict() -> dict[str, Any]`

##### `from_dict(data: dict[str, Any]) -> ExchangeRate`

Serialize/deserialize exchange rates.

---

### ExchangeRateProvider

Provides exchange rates between currencies.

```python
class ExchangeRateProvider:
    DEFAULT_RATES: ClassVar[dict[str, Decimal]] = {...}  # ~30 currencies

    def __init__(
        self,
        base_currency: str = "USD",
        data_file: Path | str | None = None,
    ) -> None
```

#### Methods

##### `get_rate(from_currency: str, to_currency: str) -> ExchangeRate | None`

Get exchange rate between two currencies.

```python
from spreadsheet_dl.domains.finance.currency import ExchangeRateProvider

provider = ExchangeRateProvider()
rate = provider.get_rate("USD", "EUR")
print(f"1 USD = {rate.rate} EUR")  # 1 USD = 0.92 EUR
```

##### `set_rate(from_currency: str, to_currency: str, rate: Decimal | float | str, rate_date: date | None = None) -> ExchangeRate`

Set a custom exchange rate.

```python
from decimal import Decimal

provider.set_rate("USD", "BTC", Decimal("0.000025"))
```

##### `remove_rate(from_currency: str, to_currency: str) -> bool`

Remove a custom exchange rate.

##### `list_rates() -> list[ExchangeRate]`

List all available rates (custom + defaults).

---

### CurrencyConverter

Convert amounts between currencies.

```python
class CurrencyConverter:
    def __init__(
        self,
        rate_provider: ExchangeRateProvider | None = None,
    ) -> None
```

#### Methods

##### `convert(amount: Decimal | float | str, from_currency: str, to_currency: str, rate: Decimal | None = None) -> Decimal`

Convert amount between currencies.

```python
from spreadsheet_dl.domains.finance.currency import CurrencyConverter
from decimal import Decimal

converter = CurrencyConverter()
eur_amount = converter.convert(
    Decimal("100"),
    from_currency="USD",
    to_currency="EUR"
)
print(f"$100 = EUR{eur_amount}")  # $100 = EUR92.00
```

##### `convert_and_format(amount: Decimal | float | str, from_currency: str, to_currency: str, *, show_symbol: bool = True, rate: Decimal | None = None) -> str`

Convert and format amount.

```python
formatted = converter.convert_and_format(
    Decimal("100"), "USD", "EUR"
)
print(formatted)  # "€92.00"
```

##### `get_equivalent_amounts(amount: Decimal | float | str, base_currency: str, target_currencies: list[str] | None = None) -> dict[str, Decimal]`

Get equivalent amounts in multiple currencies.

```python
equivalents = converter.get_equivalent_amounts(
    Decimal("100"),
    base_currency="USD",
    target_currencies=["EUR", "GBP", "JPY"]
)

for currency, amount in equivalents.items():
    print(f"{currency}: {amount}")
```

---

### MoneyAmount

Represents a monetary amount with currency (type-safe operations).

```python
@dataclass
class MoneyAmount:
    amount: Decimal
    currency_code: str
```

#### Properties

##### `currency -> Currency`

Get the Currency object.

#### Methods

##### `format(*, show_symbol: bool = True, show_code: bool = False) -> str`

Format the amount.

```python
from spreadsheet_dl.domains.finance.currency import MoneyAmount
from decimal import Decimal

usd = MoneyAmount(Decimal("100"), "USD")
print(usd.format())  # "$100.00"
```

##### `convert_to(target_currency: str, converter: CurrencyConverter | None = None) -> MoneyAmount`

Convert to another currency.

```python
eur = usd.convert_to("EUR")
print(eur.format())  # "€92.00"
```

#### Arithmetic Operations

##### `__add__(other: MoneyAmount) -> MoneyAmount`

##### `__sub__(other: MoneyAmount) -> MoneyAmount`

Add/subtract money amounts (must be same currency).

```python
total = MoneyAmount(Decimal("100"), "USD") + MoneyAmount(Decimal("50"), "USD")
print(total.format())  # "$150.00"
```

##### `__mul__(factor: Decimal | float | int) -> MoneyAmount`

##### `__truediv__(divisor: Decimal | float | int) -> MoneyAmount`

Multiply/divide amounts.

```python
doubled = usd * 2
print(doubled.format())  # "$200.00"

half = usd / 2
print(half.format())  # "$50.00"
```

##### `__neg__() -> MoneyAmount`

##### `__abs__() -> MoneyAmount`

Negate/absolute value.

#### Comparison Operations

##### `__eq__(other: MoneyAmount) -> bool`

##### `__lt__(other: MoneyAmount) -> bool`

##### `__le__(other: MoneyAmount) -> bool`

##### `__gt__(other: MoneyAmount) -> bool`

##### `__ge__(other: MoneyAmount) -> bool`

Compare money amounts (same currency only).

```python
if MoneyAmount(Decimal("100"), "USD") > MoneyAmount(Decimal("50"), "USD"):
    print("First is larger")
```

##### `to_dict() -> dict[str, Any]`

##### `from_dict(data: dict[str, Any]) -> MoneyAmount`

Serialize/deserialize.

---

## Functions

### `get_currency(code: str) -> Currency`

Get currency by code.

```python
from spreadsheet_dl.domains.finance.currency import get_currency

usd = get_currency("USD")
print(f"{usd.name}: {usd.symbol}")  # US Dollar: $
```

**Raises:** `ValueError` if currency code is unknown.

---

### `list_currencies() -> list[Currency]`

List all supported currencies.

```python
from spreadsheet_dl.domains.finance.currency import list_currencies

for currency in list_currencies():
    print(f"{currency.code}: {currency.name}")
```

---

### `money(amount: Decimal | float | str, currency: str = "USD") -> MoneyAmount`

Create a MoneyAmount (convenience function).

```python
from spreadsheet_dl.domains.finance.currency import money
from decimal import Decimal

usd = money(Decimal("100"), "USD")
eur = money(50.0, "EUR")
```

---

### `format_currency(amount: Decimal | float | str, currency: str = "USD", *, show_symbol: bool = True) -> str`

Format an amount in a currency.

```python
from spreadsheet_dl.domains.finance.currency import format_currency
from decimal import Decimal

formatted = format_currency(Decimal("1234.56"), "EUR")
print(formatted)  # "€1,234.56"
```

---

### `convert(amount: Decimal | float | str, from_currency: str, to_currency: str) -> Decimal`

Convert an amount between currencies.

```python
from spreadsheet_dl.domains.finance.currency import convert
from decimal import Decimal

eur_amount = convert(Decimal("100"), "USD", "EUR")
```

---

## Supported Currencies

### Major Currencies

- USD - US Dollar ($)
- EUR - Euro (€)
- GBP - British Pound (£)
- JPY - Japanese Yen (¥) - 0 decimal places
- CHF - Swiss Franc (CHF)
- CAD - Canadian Dollar (C$)
- AUD - Australian Dollar (A$)

### Asian Currencies

- CNY - Chinese Yuan (¥)
- HKD - Hong Kong Dollar (HK$)
- SGD - Singapore Dollar (S$)
- INR - Indian Rupee (₹)
- KRW - South Korean Won (₩) - 0 decimal places
- TWD - Taiwan Dollar (NT$) - 0 decimal places
- IDR - Indonesian Rupiah (Rp) - 0 decimal places
- MYR - Malaysian Ringgit (RM)
- PHP - Philippine Peso (₱)
- THB - Thai Baht (฿)

### European Currencies

- SEK - Swedish Krona (kr) - symbol after
- NOK - Norwegian Krone (kr) - symbol after
- DKK - Danish Krone (kr) - symbol after
- PLN - Polish Zloty (zł) - symbol after
- RUB - Russian Ruble (₽) - symbol after
- TRY - Turkish Lira (₺)

### Other Currencies

- NZD - New Zealand Dollar (NZ$)
- MXN - Mexican Peso (MX$)
- BRL - Brazilian Real (R$)
- ZAR - South African Rand (R)
- ILS - Israeli Shekel (₪)
- AED - UAE Dirham (AED)
- SAR - Saudi Riyal (SAR)

---

## Usage Examples

### Example 1: Format Currencies

```python
from spreadsheet_dl.domains.finance.currency import get_currency, list_currencies
from decimal import Decimal

amount = Decimal("1234.56")

# Format in different currencies
for code in ["USD", "EUR", "GBP", "JPY"]:
    currency = get_currency(code)
    formatted = currency.format(amount)
    print(f"{code}: {formatted}")

# Output:
# USD: $1,234.56
# EUR: €1,234.56
# GBP: £1,234.56
# JPY: ¥1,235  (no decimals)
```

### Example 2: Currency Conversion

```python
from spreadsheet_dl.domains.finance.currency import CurrencyConverter
from decimal import Decimal

converter = CurrencyConverter()

# Convert $100 to various currencies
usd_amount = Decimal("100")
for target in ["EUR", "GBP", "JPY", "CAD"]:
    converted = converter.convert(usd_amount, "USD", target)
    formatted = converter.convert_and_format(usd_amount, "USD", target)
    print(f"$100 = {formatted}")
```

### Example 3: Money Amount Operations

```python
from spreadsheet_dl.domains.finance.currency import MoneyAmount
from decimal import Decimal

# Create amounts
price1 = MoneyAmount(Decimal("29.99"), "USD")
price2 = MoneyAmount(Decimal("49.99"), "USD")

# Add
total = price1 + price2
print(f"Total: {total.format()}")  # Total: $79.98

# Multiply
bulk_price = price1 * 10
print(f"10x: {bulk_price.format()}")  # 10x: $299.90

# Compare
if price2 > price1:
    print("Price 2 is more expensive")
```

### Example 4: Custom Exchange Rates

```python
from spreadsheet_dl.domains.finance.currency import ExchangeRateProvider
from decimal import Decimal

provider = ExchangeRateProvider()

# Set custom rate
provider.set_rate("USD", "EUR", Decimal("0.95"))

# Get rate
rate = provider.get_rate("USD", "EUR")
print(f"Custom rate: 1 USD = {rate.rate} EUR")

# Persist to file
provider_with_file = ExchangeRateProvider(
    data_file="my_rates.json"
)
provider_with_file.set_rate("USD", "EUR", Decimal("0.95"))
# Saved to file for next time
```

### Example 5: Multi-Currency Display

```python
from spreadsheet_dl.domains.finance.currency import CurrencyConverter
from decimal import Decimal

converter = CurrencyConverter()

base_amount = Decimal("1000")
base_currency = "USD"

print(f"${base_amount} USD equals:")

currencies = ["EUR", "GBP", "JPY", "CAD", "AUD"]
for target in currencies:
    formatted = converter.convert_and_format(
        base_amount,
        base_currency,
        target
    )
    print(f"  {formatted}")
```

### Example 6: Parse Formatted Amounts

```python
from spreadsheet_dl.domains.finance.currency import get_currency

usd = get_currency("USD")

# Parse different formats
amounts = [
    "$1,234.56",
    "$-500.00",
    "-$250.75",
]

for formatted in amounts:
    parsed = usd.parse(formatted)
    print(f"{formatted} → {parsed}")
```

### Example 7: Currency with Different Separators

```python
from spreadsheet_dl.domains.finance.currency import Currency
from decimal import Decimal

# European format (comma as decimal, period as thousands)
eur_custom = Currency(
    code="EUR",
    name="Euro",
    symbol="€",
    decimal_places=2,
    symbol_position="before",
    thousand_separator=".",
    decimal_separator=",",
)

formatted = eur_custom.format(Decimal("1234.56"))
print(formatted)  # €1.234,56
```

### Example 8: MoneyAmount Conversion Chain

```python
from spreadsheet_dl.domains.finance.currency import money
from decimal import Decimal

# Start with USD
usd = money(Decimal("100"), "USD")
print(f"Start: {usd.format()}")

# Convert to EUR
eur = usd.convert_to("EUR")
print(f"EUR: {eur.format()}")

# Convert to GBP
gbp = eur.convert_to("GBP")
print(f"GBP: {gbp.format()}")

# Convert back to USD
usd_back = gbp.convert_to("USD")
print(f"Back to USD: {usd_back.format()}")
```

### Example 9: Equivalent Amounts

```python
from spreadsheet_dl.domains.finance.currency import CurrencyConverter
from decimal import Decimal

converter = CurrencyConverter()

# Show $100 in all currencies
equivalents = converter.get_equivalent_amounts(
    Decimal("100"),
    base_currency="USD"
)

print("$100 USD in all currencies:")
for code in sorted(equivalents.keys())[:10]:
    amount = equivalents[code]
    from spreadsheet_dl.domains.finance.currency import format_currency
    formatted = format_currency(amount, code)
    print(f"  {formatted}")
```

### Example 10: Budget in Multiple Currencies

```python
from spreadsheet_dl.domains.finance.currency import money, MoneyAmount
from decimal import Decimal

# Budget items in USD
items = [
    money(Decimal("1500"), "USD"),  # Rent
    money(Decimal("400"), "USD"),   # Groceries
    money(Decimal("200"), "USD"),   # Utilities
]

# Total in USD
total_usd = sum(items[1:], items[0])
print(f"Total USD: {total_usd.format()}")

# Convert to EUR
total_eur = total_usd.convert_to("EUR")
print(f"Total EUR: {total_eur.format()}")
```

---

## Default Exchange Rates

Default rates are relative to USD (approximate as of late 2024):

- EUR: 0.92
- GBP: 0.79
- JPY: 149.50
- CHF: 0.88
- CAD: 1.36
- AUD: 1.53
- (See `ExchangeRateProvider.DEFAULT_RATES` for complete list)

---

## Notes

- **All amounts use Decimal** for precision (avoid floating-point errors)
- **Exchange rates can be customized** and persisted to file
- **MoneyAmount provides type safety** - prevents mixing currencies
- **Zero decimal currencies** (JPY, KRW, TWD, IDR) automatically round to whole numbers
- **Symbol position varies** by currency (e.g., Swedish Krona shows "kr" after amount)
- **Custom separators supported** for international formats
