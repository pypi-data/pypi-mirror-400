"""Multi-Currency Support Module.

Provides comprehensive currency handling including:
- Currency definitions with symbols and decimal places
- Exchange rate management
- Currency conversion
- Multi-currency display formatting

"""

from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar


class CurrencyCode(Enum):
    """ISO 4217 Currency Codes.

    Common currencies supported by the system.
    """

    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CHF = "CHF"  # Swiss Franc
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    NZD = "NZD"  # New Zealand Dollar
    CNY = "CNY"  # Chinese Yuan
    HKD = "HKD"  # Hong Kong Dollar
    SGD = "SGD"  # Singapore Dollar
    INR = "INR"  # Indian Rupee
    MXN = "MXN"  # Mexican Peso
    BRL = "BRL"  # Brazilian Real
    KRW = "KRW"  # South Korean Won
    SEK = "SEK"  # Swedish Krona
    NOK = "NOK"  # Norwegian Krone
    DKK = "DKK"  # Danish Krone
    PLN = "PLN"  # Polish Zloty
    ZAR = "ZAR"  # South African Rand
    RUB = "RUB"  # Russian Ruble
    TRY = "TRY"  # Turkish Lira
    THB = "THB"  # Thai Baht
    IDR = "IDR"  # Indonesian Rupiah
    MYR = "MYR"  # Malaysian Ringgit
    PHP = "PHP"  # Philippine Peso
    TWD = "TWD"  # Taiwan Dollar
    ILS = "ILS"  # Israeli Shekel
    AED = "AED"  # UAE Dirham
    SAR = "SAR"  # Saudi Riyal


@dataclass(frozen=True)
class Currency:
    """Currency definition with formatting information.

    Attributes:
        code: ISO 4217 currency code.
        name: Full currency name.
        symbol: Currency symbol (e.g., $, EUR, GBP).
        decimal_places: Number of decimal places (usually 2, 0 for JPY).
        symbol_position: 'before' or 'after' the amount.
        thousand_separator: Character for thousands grouping.
        decimal_separator: Character for decimal point.
    """

    code: str
    name: str
    symbol: str
    decimal_places: int = 2
    symbol_position: str = "before"  # 'before' or 'after'
    thousand_separator: str = ","
    decimal_separator: str = "."

    def format(
        self,
        amount: Decimal | float | str,
        *,
        show_symbol: bool = True,
        show_code: bool = False,
    ) -> str:
        """Format an amount in this currency.

        Args:
            amount: Amount to format.
            show_symbol: Include currency symbol.
            show_code: Include currency code.

        Returns:
            Formatted currency string.
        """
        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        # Round to appropriate decimal places
        quantize_str = (
            "1." + "0" * self.decimal_places if self.decimal_places > 0 else "1"
        )
        rounded = amount.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

        # Format with separators
        is_negative = rounded < 0
        abs_amount = abs(rounded)

        # Split integer and decimal parts
        str_amount = str(abs_amount)
        if "." in str_amount:
            int_part, dec_part = str_amount.split(".")
        else:
            int_part = str_amount
            dec_part = "0" * self.decimal_places

        # Pad decimal places if needed
        dec_part = dec_part.ljust(self.decimal_places, "0")[: self.decimal_places]

        # Add thousand separators
        if self.thousand_separator:
            int_part = self._add_thousands(int_part)

        # Combine
        if self.decimal_places > 0:
            formatted = f"{int_part}{self.decimal_separator}{dec_part}"
        else:
            formatted = int_part

        # Add symbol
        if show_symbol:
            if self.symbol_position == "before":
                formatted = f"{self.symbol}{formatted}"
            else:
                formatted = f"{formatted} {self.symbol}"

        # Add code
        if show_code:
            formatted = f"{formatted} {self.code}"

        # Handle negative
        if is_negative:
            formatted = f"-{formatted}"

        return formatted

    def _add_thousands(self, int_part: str) -> str:
        """Add thousand separators to integer part."""
        result = ""
        for i, char in enumerate(reversed(int_part)):
            if i > 0 and i % 3 == 0:
                result = self.thousand_separator + result
            result = char + result
        return result

    def parse(self, formatted: str) -> Decimal:
        """Parse a formatted currency string to Decimal.

        Args:
            formatted: Formatted currency string.

        Returns:
            Decimal amount.
        """
        # Remove currency symbol and code
        cleaned = formatted.replace(self.symbol, "")
        cleaned = cleaned.replace(self.code, "")
        cleaned = cleaned.strip()

        # Handle negative
        is_negative = cleaned.startswith("-") or cleaned.startswith("(")
        cleaned = cleaned.lstrip("-").strip("()")

        # Remove thousand separators
        cleaned = cleaned.replace(self.thousand_separator, "")

        # Normalize decimal separator
        if self.decimal_separator != ".":
            cleaned = cleaned.replace(self.decimal_separator, ".")

        # Parse
        amount = Decimal(cleaned)
        if is_negative:
            amount = -amount

        return amount


# Pre-defined currency objects
CURRENCIES: dict[str, Currency] = {
    "USD": Currency("USD", "US Dollar", "$", 2, "before"),
    "EUR": Currency("EUR", "Euro", "\u20ac", 2, "before"),
    "GBP": Currency("GBP", "British Pound", "\xa3", 2, "before"),
    "JPY": Currency("JPY", "Japanese Yen", "\xa5", 0, "before"),
    "CHF": Currency("CHF", "Swiss Franc", "CHF", 2, "before"),
    "CAD": Currency("CAD", "Canadian Dollar", "C$", 2, "before"),
    "AUD": Currency("AUD", "Australian Dollar", "A$", 2, "before"),
    "NZD": Currency("NZD", "New Zealand Dollar", "NZ$", 2, "before"),
    "CNY": Currency("CNY", "Chinese Yuan", "\xa5", 2, "before"),
    "HKD": Currency("HKD", "Hong Kong Dollar", "HK$", 2, "before"),
    "SGD": Currency("SGD", "Singapore Dollar", "S$", 2, "before"),
    "INR": Currency("INR", "Indian Rupee", "\u20b9", 2, "before"),
    "MXN": Currency("MXN", "Mexican Peso", "MX$", 2, "before"),
    "BRL": Currency("BRL", "Brazilian Real", "R$", 2, "before"),
    "KRW": Currency("KRW", "South Korean Won", "\u20a9", 0, "before"),
    "SEK": Currency("SEK", "Swedish Krona", "kr", 2, "after"),
    "NOK": Currency("NOK", "Norwegian Krone", "kr", 2, "after"),
    "DKK": Currency("DKK", "Danish Krone", "kr", 2, "after"),
    "PLN": Currency("PLN", "Polish Zloty", "z\u0142", 2, "after"),
    "ZAR": Currency("ZAR", "South African Rand", "R", 2, "before"),
    "RUB": Currency("RUB", "Russian Ruble", "\u20bd", 2, "after"),
    "TRY": Currency("TRY", "Turkish Lira", "\u20ba", 2, "before"),
    "THB": Currency("THB", "Thai Baht", "\u0e3f", 2, "before"),
    "IDR": Currency("IDR", "Indonesian Rupiah", "Rp", 0, "before"),
    "MYR": Currency("MYR", "Malaysian Ringgit", "RM", 2, "before"),
    "PHP": Currency("PHP", "Philippine Peso", "\u20b1", 2, "before"),
    "TWD": Currency("TWD", "Taiwan Dollar", "NT$", 0, "before"),
    "ILS": Currency("ILS", "Israeli Shekel", "\u20aa", 2, "before"),
    "AED": Currency("AED", "UAE Dirham", "AED", 2, "before"),
    "SAR": Currency("SAR", "Saudi Riyal", "SAR", 2, "before"),
}


def get_currency(code: str) -> Currency:
    """Get currency by code.

    Args:
        code: ISO 4217 currency code.

    Returns:
        Currency object.

    Raises:
        ValueError: If currency code is unknown.
    """
    code_upper = code.upper()
    if code_upper not in CURRENCIES:
        raise ValueError(f"Unknown currency code: {code}")
    return CURRENCIES[code_upper]


def list_currencies() -> list[Currency]:
    """List all supported currencies.

    Returns:
        List of Currency objects.
    """
    return list(CURRENCIES.values())


@dataclass
class ExchangeRate:
    """Exchange rate between two currencies.

    Attributes:
        from_currency: Source currency code.
        to_currency: Target currency code.
        rate: Exchange rate (1 from_currency = rate to_currency).
        date: Date of the rate.
        source: Source of the rate (e.g., "manual", "api").
    """

    from_currency: str
    to_currency: str
    rate: Decimal
    date: date = field(default_factory=date.today)
    source: str = "manual"

    def reverse(self) -> ExchangeRate:
        """Get the reverse exchange rate."""
        return ExchangeRate(
            from_currency=self.to_currency,
            to_currency=self.from_currency,
            rate=Decimal("1") / self.rate,
            date=self.date,
            source=self.source,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "rate": str(self.rate),
            "date": self.date.isoformat(),
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExchangeRate:
        """Create from dictionary."""
        return cls(
            from_currency=data["from_currency"],
            to_currency=data["to_currency"],
            rate=Decimal(data["rate"]),
            date=date.fromisoformat(data["date"]) if "date" in data else date.today(),
            source=data.get("source", "manual"),
        )


class ExchangeRateProvider:
    """Provides exchange rates between currencies.

    Supports both hardcoded rates and custom rates.
    Future versions can integrate with APIs like Open Exchange Rates.

    Example:
        ```python
        provider = ExchangeRateProvider()

        # Get rate
        rate = provider.get_rate("USD", "EUR")
        print(f"1 USD = {rate.rate} EUR")

        # Add custom rate
        provider.set_rate("USD", "BTC", Decimal("0.000025"))
        ```
    """

    # Default rates relative to USD (approximate as of late 2024)
    DEFAULT_RATES: ClassVar[dict[str, Decimal]] = {
        "USD": Decimal("1.0"),
        "EUR": Decimal("0.92"),
        "GBP": Decimal("0.79"),
        "JPY": Decimal("149.50"),
        "CHF": Decimal("0.88"),
        "CAD": Decimal("1.36"),
        "AUD": Decimal("1.53"),
        "NZD": Decimal("1.65"),
        "CNY": Decimal("7.24"),
        "HKD": Decimal("7.82"),
        "SGD": Decimal("1.34"),
        "INR": Decimal("83.50"),
        "MXN": Decimal("17.25"),
        "BRL": Decimal("4.97"),
        "KRW": Decimal("1330"),
        "SEK": Decimal("10.55"),
        "NOK": Decimal("10.75"),
        "DKK": Decimal("6.90"),
        "PLN": Decimal("4.05"),
        "ZAR": Decimal("18.50"),
        "RUB": Decimal("92.00"),
        "TRY": Decimal("29.00"),
        "THB": Decimal("35.50"),
        "IDR": Decimal("15700"),
        "MYR": Decimal("4.72"),
        "PHP": Decimal("56.50"),
        "TWD": Decimal("31.80"),
        "ILS": Decimal("3.70"),
        "AED": Decimal("3.67"),
        "SAR": Decimal("3.75"),
    }

    def __init__(
        self,
        base_currency: str = "USD",
        data_file: Path | str | None = None,
    ) -> None:
        """Initialize exchange rate provider.

        Args:
            base_currency: Base currency for rates.
            data_file: Optional file for persisting custom rates.
        """
        self.base_currency = base_currency.upper()
        self._custom_rates: dict[str, ExchangeRate] = {}
        self._data_file = Path(data_file) if data_file else None

        if self._data_file and self._data_file.exists():
            self._load()

    def _get_rate_key(self, from_currency: str, to_currency: str) -> str:
        """Get dictionary key for rate pair."""
        return f"{from_currency.upper()}-{to_currency.upper()}"

    def _load(self) -> None:
        """Load custom rates from file."""
        if not self._data_file or not self._data_file.exists():
            return

        with open(self._data_file) as f:
            data = json.load(f)

        for rate_data in data.get("rates", []):
            rate = ExchangeRate.from_dict(rate_data)
            key = self._get_rate_key(rate.from_currency, rate.to_currency)
            self._custom_rates[key] = rate

    def _save(self) -> None:
        """Save custom rates to file."""
        if not self._data_file:
            return

        self._data_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "base_currency": self.base_currency,
            "rates": [rate.to_dict() for rate in self._custom_rates.values()],
            "updated_at": datetime.now().isoformat(),
        }

        with open(self._data_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> ExchangeRate | None:
        """Get exchange rate between two currencies.

        Args:
            from_currency: Source currency code.
            to_currency: Target currency code.

        Returns:
            ExchangeRate or None if not available.
        """
        from_code = from_currency.upper()
        to_code = to_currency.upper()

        # Same currency = 1:1
        if from_code == to_code:
            return ExchangeRate(from_code, to_code, Decimal("1"))

        # Check custom rates first
        key = self._get_rate_key(from_code, to_code)
        if key in self._custom_rates:
            return self._custom_rates[key]

        # Check reverse custom rate
        reverse_key = self._get_rate_key(to_code, from_code)
        if reverse_key in self._custom_rates:
            return self._custom_rates[reverse_key].reverse()

        # Calculate from default rates (via USD)
        if from_code in self.DEFAULT_RATES and to_code in self.DEFAULT_RATES:
            from_usd_rate = self.DEFAULT_RATES[from_code]
            to_usd_rate = self.DEFAULT_RATES[to_code]
            # from_currency -> USD -> to_currency
            rate = to_usd_rate / from_usd_rate
            return ExchangeRate(from_code, to_code, rate, source="default")

        return None

    def set_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate: Decimal | float | str,
        rate_date: date | None = None,
    ) -> ExchangeRate:
        """Set a custom exchange rate.

        Args:
            from_currency: Source currency code.
            to_currency: Target currency code.
            rate: Exchange rate.
            rate_date: Date of rate.

        Returns:
            Created ExchangeRate.
        """
        if isinstance(rate, (float, int)):
            rate = Decimal(str(rate))
        elif isinstance(rate, str):
            rate = Decimal(rate)

        exchange_rate = ExchangeRate(
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
            rate=rate,
            date=rate_date or date.today(),
            source="custom",
        )

        key = self._get_rate_key(from_currency, to_currency)
        self._custom_rates[key] = exchange_rate
        self._save()

        return exchange_rate

    def remove_rate(self, from_currency: str, to_currency: str) -> bool:
        """Remove a custom exchange rate.

        Args:
            from_currency: Source currency code.
            to_currency: Target currency code.

        Returns:
            True if removed, False if not found.
        """
        key = self._get_rate_key(from_currency, to_currency)
        if key in self._custom_rates:
            del self._custom_rates[key]
            self._save()
            return True
        return False

    def list_rates(self) -> list[ExchangeRate]:
        """List all available rates (custom + defaults)."""
        rates = list(self._custom_rates.values())

        # Add default rates from USD
        for code, rate in self.DEFAULT_RATES.items():
            if code != "USD":
                rates.append(ExchangeRate("USD", code, rate, source="default"))

        return rates


class CurrencyConverter:
    """Convert amounts between currencies.

    Example:
        ```python
        converter = CurrencyConverter()

        # Convert $100 to EUR
        eur_amount = converter.convert(
            Decimal("100"),
            from_currency="USD",
            to_currency="EUR"
        )
        print(f"$100 = {eur_amount:.2f} EUR")

        # Format result
        formatted = converter.convert_and_format(
            Decimal("100"), "USD", "EUR"
        )
        print(formatted)  # "EUR92.00"
        ```
    """

    def __init__(
        self,
        rate_provider: ExchangeRateProvider | None = None,
    ) -> None:
        """Initialize converter.

        Args:
            rate_provider: Exchange rate provider (creates default if None).
        """
        self.rate_provider = rate_provider or ExchangeRateProvider()

    def convert(
        self,
        amount: Decimal | float | str,
        from_currency: str,
        to_currency: str,
        rate: Decimal | None = None,
    ) -> Decimal:
        """Convert amount between currencies.

        Args:
            amount: Amount to convert.
            from_currency: Source currency code.
            to_currency: Target currency code.
            rate: Optional specific rate to use.

        Returns:
            Converted amount.

        Raises:
            ValueError: If conversion rate not available.
        """
        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        from_code = from_currency.upper()
        to_code = to_currency.upper()

        if from_code == to_code:
            return amount

        if rate is None:
            exchange_rate = self.rate_provider.get_rate(from_code, to_code)
            if exchange_rate is None:
                raise ValueError(
                    f"No exchange rate available for {from_code} to {to_code}"
                )
            rate = exchange_rate.rate

        return amount * rate

    def convert_and_format(
        self,
        amount: Decimal | float | str,
        from_currency: str,
        to_currency: str,
        *,
        show_symbol: bool = True,
        rate: Decimal | None = None,
    ) -> str:
        """Convert and format amount.

        Args:
            amount: Amount to convert.
            from_currency: Source currency code.
            to_currency: Target currency code.
            show_symbol: Include currency symbol.
            rate: Optional specific rate to use.

        Returns:
            Formatted converted amount.
        """
        converted = self.convert(amount, from_currency, to_currency, rate)
        currency = get_currency(to_currency)
        return currency.format(converted, show_symbol=show_symbol)

    def get_equivalent_amounts(
        self,
        amount: Decimal | float | str,
        base_currency: str,
        target_currencies: list[str] | None = None,
    ) -> dict[str, Decimal]:
        """Get equivalent amounts in multiple currencies.

        Args:
            amount: Base amount.
            base_currency: Base currency code.
            target_currencies: List of target currencies (all if None).

        Returns:
            Dictionary of currency code to converted amount.
        """
        if isinstance(amount, (float, int)):
            amount = Decimal(str(amount))
        elif isinstance(amount, str):
            amount = Decimal(amount)

        if target_currencies is None:
            target_currencies = list(CURRENCIES.keys())

        result: dict[str, Decimal] = {}
        for target in target_currencies:
            with contextlib.suppress(ValueError):
                # Skip currencies without rates
                result[target] = self.convert(amount, base_currency, target)

        return result


@dataclass
class MoneyAmount:
    """Represents a monetary amount with currency.

    Combines an amount with its currency for type-safe operations.

    Example:
        ```python
        usd = MoneyAmount(Decimal("100"), "USD")
        print(usd.format())  # "$100.00"

        eur = usd.convert_to("EUR")
        print(eur.format())  # "EUR92.00"
        ```
    """

    amount: Decimal
    currency_code: str

    def __post_init__(self) -> None:
        """Validate currency code."""
        if isinstance(self.amount, (float, int)):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        elif isinstance(self.amount, str):
            object.__setattr__(self, "amount", Decimal(self.amount))
        self.currency_code = self.currency_code.upper()

    @property
    def currency(self) -> Currency:
        """Get the Currency object."""
        return get_currency(self.currency_code)

    def format(
        self,
        *,
        show_symbol: bool = True,
        show_code: bool = False,
    ) -> str:
        """Format the amount."""
        return self.currency.format(
            self.amount,
            show_symbol=show_symbol,
            show_code=show_code,
        )

    def convert_to(
        self,
        target_currency: str,
        converter: CurrencyConverter | None = None,
    ) -> MoneyAmount:
        """Convert to another currency.

        Args:
            target_currency: Target currency code.
            converter: Currency converter (creates default if None).

        Returns:
            New MoneyAmount in target currency.
        """
        if converter is None:
            converter = CurrencyConverter()

        converted = converter.convert(
            self.amount,
            self.currency_code,
            target_currency,
        )

        return MoneyAmount(converted, target_currency)

    def __add__(self, other: MoneyAmount) -> MoneyAmount:
        """Add two money amounts (must be same currency)."""
        if self.currency_code != other.currency_code:
            raise ValueError(
                f"Cannot add {self.currency_code} and {other.currency_code}"
            )
        return MoneyAmount(self.amount + other.amount, self.currency_code)

    def __sub__(self, other: MoneyAmount) -> MoneyAmount:
        """Subtract two money amounts (must be same currency)."""
        if self.currency_code != other.currency_code:
            raise ValueError(
                f"Cannot subtract {self.currency_code} and {other.currency_code}"
            )
        return MoneyAmount(self.amount - other.amount, self.currency_code)

    def __mul__(self, factor: Decimal | float | int) -> MoneyAmount:
        """Multiply amount by a factor."""
        if isinstance(factor, (float, int)):
            factor = Decimal(str(factor))
        return MoneyAmount(self.amount * factor, self.currency_code)

    def __truediv__(self, divisor: Decimal | float | int) -> MoneyAmount:
        """Divide amount by a divisor."""
        if isinstance(divisor, (float, int)):
            divisor = Decimal(str(divisor))
        return MoneyAmount(self.amount / divisor, self.currency_code)

    def __neg__(self) -> MoneyAmount:
        """Negate the amount."""
        return MoneyAmount(-self.amount, self.currency_code)

    def __abs__(self) -> MoneyAmount:
        """Get absolute value."""
        return MoneyAmount(abs(self.amount), self.currency_code)

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, MoneyAmount):
            return NotImplemented
        return self.amount == other.amount and self.currency_code == other.currency_code

    def __lt__(self, other: MoneyAmount) -> bool:
        """Less than comparison (same currency only)."""
        if self.currency_code != other.currency_code:
            raise ValueError(
                f"Cannot compare {self.currency_code} and {other.currency_code}"
            )
        return self.amount < other.amount

    def __le__(self, other: MoneyAmount) -> bool:
        """Less than or equal comparison."""
        return self == other or self < other

    def __gt__(self, other: MoneyAmount) -> bool:
        """Greater than comparison."""
        if self.currency_code != other.currency_code:
            raise ValueError(
                f"Cannot compare {self.currency_code} and {other.currency_code}"
            )
        return self.amount > other.amount

    def __ge__(self, other: MoneyAmount) -> bool:
        """Greater than or equal comparison."""
        return self == other or self > other

    def __str__(self) -> str:
        """String representation."""
        return self.format()

    def __repr__(self) -> str:
        """Debug representation."""
        return f"MoneyAmount({self.amount}, '{self.currency_code}')"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "amount": str(self.amount),
            "currency": self.currency_code,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MoneyAmount:
        """Create from dictionary."""
        return cls(
            amount=Decimal(data["amount"]),
            currency_code=data["currency"],
        )


# Convenience functions


def money(
    amount: Decimal | float | str,
    currency: str = "USD",
) -> MoneyAmount:
    """Create a MoneyAmount.

    Args:
        amount: The amount.
        currency: Currency code.

    Returns:
        MoneyAmount instance.
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))
    elif isinstance(amount, str):
        amount = Decimal(amount)
    return MoneyAmount(amount, currency)


def format_currency(
    amount: Decimal | float | str,
    currency: str = "USD",
    *,
    show_symbol: bool = True,
) -> str:
    """Format an amount in a currency.

    Args:
        amount: Amount to format.
        currency: Currency code.
        show_symbol: Include currency symbol.

    Returns:
        Formatted string.
    """
    curr = get_currency(currency)
    return curr.format(amount, show_symbol=show_symbol)


def convert(
    amount: Decimal | float | str,
    from_currency: str,
    to_currency: str,
) -> Decimal:
    """Convert an amount between currencies.

    Args:
        amount: Amount to convert.
        from_currency: Source currency.
        to_currency: Target currency.

    Returns:
        Converted amount.
    """
    converter = CurrencyConverter()
    return converter.convert(amount, from_currency, to_currency)
