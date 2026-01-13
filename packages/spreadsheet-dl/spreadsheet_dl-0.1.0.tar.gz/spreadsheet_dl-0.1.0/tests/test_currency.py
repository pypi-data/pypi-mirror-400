"""
Tests for Multi-Currency Support module.

: Multi-Currency Support
"""

from __future__ import annotations

import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from spreadsheet_dl import (
    CURRENCIES,
    CurrencyCode,
    CurrencyConverter,
    ExchangeRate,
    ExchangeRateProvider,
    MoneyAmount,
    convert,
    format_currency,
    get_currency,
    list_currencies,
    money,
)

pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestCurrencyCode:
    """Tests for CurrencyCode enum."""

    def test_common_currencies_exist(self) -> None:
        """Test that common currencies are defined."""
        assert CurrencyCode.USD.value == "USD"
        assert CurrencyCode.EUR.value == "EUR"
        assert CurrencyCode.GBP.value == "GBP"
        assert CurrencyCode.JPY.value == "JPY"

    def test_all_codes_are_strings(self) -> None:
        """Test all currency codes are 3-letter strings."""
        for code in CurrencyCode:
            assert isinstance(code.value, str)
            assert len(code.value) == 3


class TestCurrency:
    """Tests for Currency class."""

    def test_format_usd(self) -> None:
        """Test formatting USD amounts."""
        usd = CURRENCIES["USD"]

        assert usd.format(Decimal("1234.56")) == "$1,234.56"
        assert usd.format(Decimal("100")) == "$100.00"
        assert usd.format(Decimal("0.50")) == "$0.50"
        assert usd.format(Decimal("-50")) == "-$50.00"

    def test_format_jpy_no_decimals(self) -> None:
        """Test formatting JPY (no decimal places)."""
        jpy = CURRENCIES["JPY"]

        assert jpy.format(Decimal("1234")) == "\xa51,234"
        assert jpy.format(Decimal("1234.56")) == "\xa51,235"  # Rounded

    def test_format_eur(self) -> None:
        """Test formatting EUR amounts."""
        eur = CURRENCIES["EUR"]

        formatted = eur.format(Decimal("1234.56"))
        assert "\u20ac" in formatted or "EUR" in formatted
        assert "1,234.56" in formatted

    def test_format_with_symbol_position_after(self) -> None:
        """Test currencies with symbol after amount."""
        sek = CURRENCIES["SEK"]

        formatted = sek.format(Decimal("100"))
        assert "kr" in formatted
        # Symbol should be after the amount
        assert formatted.endswith("kr") or formatted.endswith(" kr")

    def test_format_without_symbol(self) -> None:
        """Test formatting without symbol."""
        usd = CURRENCIES["USD"]

        formatted = usd.format(Decimal("100"), show_symbol=False)
        assert "$" not in formatted
        assert "100.00" in formatted

    def test_format_with_code(self) -> None:
        """Test formatting with currency code."""
        usd = CURRENCIES["USD"]

        formatted = usd.format(Decimal("100"), show_code=True)
        assert "USD" in formatted

    def test_parse_usd(self) -> None:
        """Test parsing USD amounts."""
        usd = CURRENCIES["USD"]

        assert usd.parse("$1,234.56") == Decimal("1234.56")
        assert usd.parse("$100.00") == Decimal("100.00")
        assert usd.parse("-$50.00") == Decimal("-50.00")
        assert usd.parse("1234.56") == Decimal("1234.56")

    def test_format_large_numbers(self) -> None:
        """Test formatting large numbers with thousands separators."""
        usd = CURRENCIES["USD"]

        assert usd.format(Decimal("1000000")) == "$1,000,000.00"
        assert usd.format(Decimal("999999999.99")) == "$999,999,999.99"

    def test_format_small_numbers(self) -> None:
        """Test formatting small numbers."""
        usd = CURRENCIES["USD"]

        assert usd.format(Decimal("0.01")) == "$0.01"
        assert usd.format(Decimal("0.001")) == "$0.00"  # Rounded


class TestGetCurrency:
    """Tests for get_currency function."""

    def test_get_valid_currency(self) -> None:
        """Test getting valid currencies."""
        usd = get_currency("USD")
        assert usd.code == "USD"
        assert usd.symbol == "$"

        eur = get_currency("eur")  # Case insensitive
        assert eur.code == "EUR"

    def test_get_invalid_currency(self) -> None:
        """Test getting invalid currency raises error."""
        with pytest.raises(ValueError, match="Unknown currency"):
            get_currency("XXX")


class TestListCurrencies:
    """Tests for list_currencies function."""

    def test_list_currencies(self) -> None:
        """Test listing all currencies."""
        currencies = list_currencies()

        assert len(currencies) > 20
        codes = [c.code for c in currencies]
        assert "USD" in codes
        assert "EUR" in codes
        assert "GBP" in codes


class TestExchangeRate:
    """Tests for ExchangeRate class."""

    def test_create_rate(self) -> None:
        """Test creating an exchange rate."""
        rate = ExchangeRate(
            from_currency="USD",
            to_currency="EUR",
            rate=Decimal("0.92"),
        )

        assert rate.from_currency == "USD"
        assert rate.to_currency == "EUR"
        assert rate.rate == Decimal("0.92")

    def test_reverse_rate(self) -> None:
        """Test getting reverse exchange rate."""
        rate = ExchangeRate(
            from_currency="USD",
            to_currency="EUR",
            rate=Decimal("0.92"),
        )

        reversed_rate = rate.reverse()

        assert reversed_rate.from_currency == "EUR"
        assert reversed_rate.to_currency == "USD"
        # 1 / 0.92 = approximately 1.087
        assert reversed_rate.rate > Decimal("1.08")
        assert reversed_rate.rate < Decimal("1.09")

    def test_serialization(self) -> None:
        """Test rate serialization."""
        rate = ExchangeRate(
            from_currency="USD",
            to_currency="EUR",
            rate=Decimal("0.92"),
            date=date(2024, 1, 15),
            source="test",
        )

        data = rate.to_dict()
        restored = ExchangeRate.from_dict(data)

        assert restored.from_currency == rate.from_currency
        assert restored.to_currency == rate.to_currency
        assert restored.rate == rate.rate
        assert restored.date == rate.date


class TestExchangeRateProvider:
    """Tests for ExchangeRateProvider class."""

    def test_get_default_rate(self) -> None:
        """Test getting default rates."""
        provider = ExchangeRateProvider()

        rate = provider.get_rate("USD", "EUR")
        assert rate is not None
        assert rate.from_currency == "USD"
        assert rate.to_currency == "EUR"
        assert Decimal("0.8") < rate.rate < Decimal("1.0")

    def test_get_rate_same_currency(self) -> None:
        """Test rate for same currency is 1."""
        provider = ExchangeRateProvider()

        rate = provider.get_rate("USD", "USD")
        assert rate is not None
        assert rate.rate == Decimal("1")

    def test_get_rate_cross(self) -> None:
        """Test cross-rate calculation."""
        provider = ExchangeRateProvider()

        # EUR to GBP (via USD)
        rate = provider.get_rate("EUR", "GBP")
        assert rate is not None
        assert rate.from_currency == "EUR"
        assert rate.to_currency == "GBP"

    def test_set_custom_rate(self) -> None:
        """Test setting custom rate."""
        provider = ExchangeRateProvider()

        custom_rate = provider.set_rate("USD", "BTC", Decimal("0.000025"))

        assert custom_rate.rate == Decimal("0.000025")

        rate = provider.get_rate("USD", "BTC")
        assert rate is not None
        assert rate.rate == Decimal("0.000025")

    def test_custom_rate_overrides_default(self) -> None:
        """Test custom rate overrides default."""
        provider = ExchangeRateProvider()

        # Get default
        default_rate = provider.get_rate("USD", "EUR")
        assert default_rate is not None

        # Set custom
        provider.set_rate("USD", "EUR", Decimal("0.85"))

        custom_rate = provider.get_rate("USD", "EUR")
        assert custom_rate is not None
        assert custom_rate.rate == Decimal("0.85")

    def test_remove_custom_rate(self) -> None:
        """Test removing custom rate."""
        provider = ExchangeRateProvider()

        provider.set_rate("USD", "XYZ", Decimal("100"))
        assert provider.get_rate("USD", "XYZ") is not None

        result = provider.remove_rate("USD", "XYZ")
        assert result is True

        assert provider.get_rate("USD", "XYZ") is None

    def test_persistence(self) -> None:
        """Test rate persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_file = Path(tmpdir) / "rates.json"

            # Create and save
            provider1 = ExchangeRateProvider(data_file=data_file)
            provider1.set_rate("USD", "BTC", Decimal("0.000025"))

            # Load in new provider
            provider2 = ExchangeRateProvider(data_file=data_file)
            rate = provider2.get_rate("USD", "BTC")

            assert rate is not None
            assert rate.rate == Decimal("0.000025")


class TestCurrencyConverter:
    """Tests for CurrencyConverter class."""

    def test_convert_same_currency(self) -> None:
        """Test conversion within same currency."""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("100"), "USD", "USD")
        assert result == Decimal("100")

    def test_convert_usd_to_eur(self) -> None:
        """Test USD to EUR conversion."""
        converter = CurrencyConverter()

        result = converter.convert(Decimal("100"), "USD", "EUR")

        # Should be around 92 EUR
        assert Decimal("80") < result < Decimal("100")

    def test_convert_with_specific_rate(self) -> None:
        """Test conversion with specific rate."""
        converter = CurrencyConverter()

        result = converter.convert(
            Decimal("100"),
            "USD",
            "EUR",
            rate=Decimal("0.90"),
        )

        assert result == Decimal("90")

    def test_convert_and_format(self) -> None:
        """Test convert and format."""
        converter = CurrencyConverter()

        result = converter.convert_and_format(
            Decimal("100"),
            "USD",
            "EUR",
        )

        assert "\u20ac" in result or "EUR" in result

    def test_get_equivalent_amounts(self) -> None:
        """Test getting equivalent amounts in multiple currencies."""
        converter = CurrencyConverter()

        amounts = converter.get_equivalent_amounts(
            Decimal("100"),
            "USD",
            ["EUR", "GBP", "JPY"],
        )

        assert "EUR" in amounts
        assert "GBP" in amounts
        assert "JPY" in amounts

        # JPY should be much larger (around 14950)
        assert amounts["JPY"] > Decimal("100")


class TestMoneyAmount:
    """Tests for MoneyAmount class."""

    def test_create_money(self) -> None:
        """Test creating a money amount."""
        m = MoneyAmount(Decimal("100"), "USD")

        assert m.amount == Decimal("100")
        assert m.currency_code == "USD"

    def test_create_from_float(self) -> None:
        """Test creating from float."""
        m = MoneyAmount(100.50, "USD")  # type: ignore

        assert m.amount == Decimal("100.5")

    def test_format(self) -> None:
        """Test formatting."""
        m = MoneyAmount(Decimal("1234.56"), "USD")

        formatted = m.format()
        assert "$" in formatted
        assert "1,234.56" in formatted

    def test_convert_to(self) -> None:
        """Test currency conversion."""
        usd = MoneyAmount(Decimal("100"), "USD")

        eur = usd.convert_to("EUR")

        assert eur.currency_code == "EUR"
        assert eur.amount < Decimal("100")

    def test_addition(self) -> None:
        """Test adding money amounts."""
        m1 = MoneyAmount(Decimal("100"), "USD")
        m2 = MoneyAmount(Decimal("50"), "USD")

        result = m1 + m2

        assert result.amount == Decimal("150")
        assert result.currency_code == "USD"

    def test_addition_different_currencies_raises(self) -> None:
        """Test adding different currencies raises error."""
        m1 = MoneyAmount(Decimal("100"), "USD")
        m2 = MoneyAmount(Decimal("50"), "EUR")

        with pytest.raises(ValueError, match="Cannot add"):
            _ = m1 + m2

    def test_subtraction(self) -> None:
        """Test subtracting money amounts."""
        m1 = MoneyAmount(Decimal("100"), "USD")
        m2 = MoneyAmount(Decimal("30"), "USD")

        result = m1 - m2

        assert result.amount == Decimal("70")

    def test_multiplication(self) -> None:
        """Test multiplying by a factor."""
        m = MoneyAmount(Decimal("100"), "USD")

        result = m * 2

        assert result.amount == Decimal("200")
        assert result.currency_code == "USD"

    def test_division(self) -> None:
        """Test dividing by a factor."""
        m = MoneyAmount(Decimal("100"), "USD")

        result = m / 4

        assert result.amount == Decimal("25")

    def test_negation(self) -> None:
        """Test negation."""
        m = MoneyAmount(Decimal("100"), "USD")

        result = -m

        assert result.amount == Decimal("-100")

    def test_abs(self) -> None:
        """Test absolute value."""
        m = MoneyAmount(Decimal("-100"), "USD")

        result = abs(m)

        assert result.amount == Decimal("100")

    def test_comparison(self) -> None:
        """Test comparison operators."""
        m1 = MoneyAmount(Decimal("100"), "USD")
        m2 = MoneyAmount(Decimal("50"), "USD")
        m3 = MoneyAmount(Decimal("100"), "USD")

        assert m1 > m2
        assert m2 < m1
        assert m1 >= m3
        assert m1 <= m3
        assert m1 == m3
        assert m1 != m2

    def test_comparison_different_currencies_raises(self) -> None:
        """Test comparing different currencies raises error."""
        m1 = MoneyAmount(Decimal("100"), "USD")
        m2 = MoneyAmount(Decimal("100"), "EUR")

        with pytest.raises(ValueError, match="Cannot compare"):
            _ = m1 < m2

    def test_str(self) -> None:
        """Test string representation."""
        m = MoneyAmount(Decimal("100"), "USD")

        assert "$100.00" in str(m)

    def test_repr(self) -> None:
        """Test debug representation."""
        m = MoneyAmount(Decimal("100"), "USD")

        assert "MoneyAmount" in repr(m)
        assert "100" in repr(m)
        assert "USD" in repr(m)

    def test_serialization(self) -> None:
        """Test serialization."""
        m = MoneyAmount(Decimal("100.50"), "EUR")

        data = m.to_dict()
        restored = MoneyAmount.from_dict(data)

        assert restored == m


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_money_function(self) -> None:
        """Test money() convenience function."""
        m = money(100, "USD")

        assert isinstance(m, MoneyAmount)
        assert m.amount == Decimal("100")
        assert m.currency_code == "USD"

    def test_money_with_float(self) -> None:
        """Test money() with float."""
        m = money(99.99)

        assert m.amount == Decimal("99.99")
        assert m.currency_code == "USD"

    def test_format_currency_function(self) -> None:
        """Test format_currency() convenience function."""
        formatted = format_currency(1234.56, "USD")

        assert "$" in formatted
        assert "1,234.56" in formatted

    def test_convert_function(self) -> None:
        """Test convert() convenience function."""
        result = convert(100, "USD", "EUR")

        assert isinstance(result, Decimal)
        assert Decimal("80") < result < Decimal("100")
