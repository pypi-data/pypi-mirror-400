"""Tests for options pricing formulas.

Test suite for options pricing formulas including Black-Scholes model,
implied volatility, and Greeks (Delta, Gamma, Theta, Vega, Rho).
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.finance.formulas.options import (
    BlackScholesCall,
    BlackScholesPut,
    ImpliedVolatility,
    OptionDelta,
    OptionGamma,
    OptionRho,
    OptionTheta,
    OptionVega,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.finance]


class TestBlackScholesCall:
    """Test BlackScholesCall formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = BlackScholesCall()
        metadata = formula.metadata

        assert metadata.name == "BS_CALL"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 5
        assert metadata.return_type == "number"

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = BlackScholesCall()
        result = formula.build("100", "105", "0.05", "1", "0.2")

        assert result.startswith("of:=")
        assert "NORMSDIST" in result
        assert "LN" in result
        assert "EXP" in result
        assert "SQRT" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = BlackScholesCall()
        result = formula.build("A1", "A2", "A3", "A4", "A5")

        assert result.startswith("of:=")
        assert "A1" in result
        assert "A5" in result

    def test_validation_missing_args(self) -> None:
        """Test validation with missing arguments."""
        formula = BlackScholesCall()
        with pytest.raises(ValueError, match="requires at least 5 arguments"):
            formula.build("100", "105", "0.05")


class TestBlackScholesPut:
    """Test BlackScholesPut formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = BlackScholesPut()
        metadata = formula.metadata

        assert metadata.name == "BS_PUT"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 5

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = BlackScholesPut()
        result = formula.build("100", "105", "0.05", "1", "0.2")

        assert result.startswith("of:=")
        assert "NORMSDIST" in result
        assert "LN" in result
        assert "EXP" in result
        assert "SQRT" in result


class TestImpliedVolatility:
    """Test ImpliedVolatility formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = ImpliedVolatility()
        metadata = formula.metadata

        assert metadata.name == "IMPLIED_VOL"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 6

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = ImpliedVolatility()
        result = formula.build("10", "100", "105", "0.05", "1", "call")

        assert result.startswith("of:=")
        assert "SQRT" in result
        assert "PI" in result


class TestOptionDelta:
    """Test OptionDelta formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = OptionDelta()
        metadata = formula.metadata

        assert metadata.name == "OPTION_DELTA"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 6

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = OptionDelta()
        result = formula.build("100", "105", "0.05", "1", "0.2", "call")

        assert result.startswith("of:=")
        assert "NORMSDIST" in result
        assert "IF" in result
        assert "call" in result

    def test_build_put_option(self) -> None:
        """Test formula for put option."""
        formula = OptionDelta()
        result = formula.build("100", "105", "0.05", "1", "0.2", "put")

        assert result.startswith("of:=")
        assert "put" in result


class TestOptionGamma:
    """Test OptionGamma formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = OptionGamma()
        metadata = formula.metadata

        assert metadata.name == "OPTION_GAMMA"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 5

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = OptionGamma()
        result = formula.build("100", "105", "0.05", "1", "0.2")

        assert result.startswith("of:=")
        assert "EXP" in result
        assert "SQRT" in result
        assert "PI" in result


class TestOptionTheta:
    """Test OptionTheta formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = OptionTheta()
        metadata = formula.metadata

        assert metadata.name == "OPTION_THETA"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 6

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = OptionTheta()
        result = formula.build("100", "105", "0.05", "1", "0.2", "call")

        assert result.startswith("of:=")
        assert "IF" in result
        assert "NORMSDIST" in result
        assert "365" in result  # Daily decay

    def test_build_put_option(self) -> None:
        """Test formula for put option."""
        formula = OptionTheta()
        result = formula.build("100", "105", "0.05", "1", "0.2", "put")

        assert result.startswith("of:=")
        assert "put" in result


class TestOptionVega:
    """Test OptionVega formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = OptionVega()
        metadata = formula.metadata

        assert metadata.name == "OPTION_VEGA"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 5

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = OptionVega()
        result = formula.build("100", "105", "0.05", "1", "0.2")

        assert result.startswith("of:=")
        assert "SQRT" in result
        assert "EXP" in result
        assert "PI" in result
        assert "100" in result  # Scaling factor


class TestOptionRho:
    """Test OptionRho formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = OptionRho()
        metadata = formula.metadata

        assert metadata.name == "OPTION_RHO"
        assert metadata.category == "options"
        assert len(metadata.arguments) == 6

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = OptionRho()
        result = formula.build("100", "105", "0.05", "1", "0.2", "call")

        assert result.startswith("of:=")
        assert "IF" in result
        assert "NORMSDIST" in result
        assert "EXP" in result
        assert "call" in result

    def test_build_put_option(self) -> None:
        """Test formula for put option."""
        formula = OptionRho()
        result = formula.build("100", "105", "0.05", "1", "0.2", "put")

        assert result.startswith("of:=")
        assert "put" in result


class TestOptionsFormulasIntegration:
    """Integration tests for options formulas."""

    def test_all_formulas_have_metadata(self) -> None:
        """Test all options formulas have valid metadata."""
        formulas = [
            BlackScholesCall(),
            BlackScholesPut(),
            ImpliedVolatility(),
            OptionDelta(),
            OptionGamma(),
            OptionTheta(),
            OptionVega(),
            OptionRho(),
        ]

        for formula in formulas:
            metadata = formula.metadata
            assert metadata.name
            assert metadata.category == "options"
            assert metadata.description
            assert len(metadata.arguments) > 0
            assert len(metadata.examples) > 0

    def test_all_formulas_build_valid_strings(self) -> None:
        """Test all options formulas build valid ODF strings."""
        test_cases = [
            (BlackScholesCall(), ["100", "105", "0.05", "1", "0.2"]),
            (BlackScholesPut(), ["100", "105", "0.05", "1", "0.2"]),
            (ImpliedVolatility(), ["10", "100", "105", "0.05", "1", "call"]),
            (OptionDelta(), ["100", "105", "0.05", "1", "0.2", "call"]),
            (OptionGamma(), ["100", "105", "0.05", "1", "0.2"]),
            (OptionTheta(), ["100", "105", "0.05", "1", "0.2", "call"]),
            (OptionVega(), ["100", "105", "0.05", "1", "0.2"]),
            (OptionRho(), ["100", "105", "0.05", "1", "0.2", "call"]),
        ]

        for formula, args in test_cases:
            result = formula.build(*args)
            assert result.startswith("of:=")
            assert len(result) > 5

    def test_greeks_consistency(self) -> None:
        """Test Greeks formulas use consistent parameters."""
        # All Greeks should accept same base parameters
        params = ["100", "105", "0.05", "1", "0.2"]

        # These don't need option_type
        for formula_class in [OptionGamma, OptionVega]:
            formula = formula_class()
            result = formula.build(*params)
            assert result.startswith("of:=")

        # These need option_type
        params_with_type = [*params, "call"]
        for formula_class in [OptionDelta, OptionTheta, OptionRho]:
            formula = formula_class()
            result = formula.build(*params_with_type)
            assert result.startswith("of:=")
