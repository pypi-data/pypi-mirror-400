"""Tests for bond analytics formulas.

Test suite for bond pricing and analytics formulas including bond price,
yield to maturity, Macaulay duration, modified duration, and convexity.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.finance.formulas.bonds import (
    BondPrice,
    Convexity,
    MacDuration,
    ModifiedDuration,
    YieldToMaturity,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.finance]


class TestBondPrice:
    """Test BondPrice formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = BondPrice()
        metadata = formula.metadata

        assert metadata.name == "BOND_PRICE"
        assert metadata.category == "bonds"
        assert len(metadata.arguments) == 5
        assert metadata.arguments[4].default == 2
        assert metadata.return_type == "number"

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = BondPrice()
        result = formula.build("1000", "0.05", "0.06", "10", "2")

        assert result.startswith("of:=")
        assert "1000" in result
        assert "0.05" in result
        assert "0.06" in result
        assert "10" in result
        assert "2" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = BondPrice()
        result = formula.build("A1", "A2", "A3", "A4", "A5")

        assert result.startswith("of:=")
        assert "A1" in result
        assert "A5" in result

    def test_build_default_frequency(self) -> None:
        """Test formula with default frequency."""
        formula = BondPrice()
        result = formula.build("1000", "0.05", "0.06", "10")

        assert result.startswith("of:=")
        assert "1000" in result

    def test_validation_missing_args(self) -> None:
        """Test validation with missing arguments."""
        formula = BondPrice()
        with pytest.raises(ValueError, match="requires at least 4 arguments"):
            formula.build("1000", "0.05", "0.06")


class TestYieldToMaturity:
    """Test YieldToMaturity formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = YieldToMaturity()
        metadata = formula.metadata

        assert metadata.name == "YTM"
        assert metadata.category == "bonds"
        assert len(metadata.arguments) == 5
        assert metadata.arguments[4].default == 2

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = YieldToMaturity()
        result = formula.build("950", "1000", "0.05", "10", "2")

        assert result.startswith("of:=")
        assert "950" in result
        assert "1000" in result
        assert "0.05" in result
        assert "10" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = YieldToMaturity()
        result = formula.build("A1", "A2", "A3", "A4", "A5")

        assert result.startswith("of:=")
        assert "A1" in result
        assert "A4" in result

    def test_build_default_frequency(self) -> None:
        """Test formula with default frequency."""
        formula = YieldToMaturity()
        result = formula.build("950", "1000", "0.05", "10")

        assert result.startswith("of:=")
        assert "950" in result


class TestMacDuration:
    """Test MacDuration formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = MacDuration()
        metadata = formula.metadata

        assert metadata.name == "MACDURATION"
        assert metadata.category == "bonds"
        assert len(metadata.arguments) == 5

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = MacDuration()
        result = formula.build("1000", "0.05", "0.06", "10", "2")

        assert result.startswith("of:=")
        assert "DURATION" in result
        assert "TODAY" in result
        assert "0.05" in result
        assert "0.06" in result
        assert "10" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = MacDuration()
        result = formula.build("A1", "A2", "A3", "A4", "A5")

        assert result.startswith("of:=")
        assert "DURATION" in result

    def test_build_default_frequency(self) -> None:
        """Test formula with default frequency."""
        formula = MacDuration()
        result = formula.build("1000", "0.05", "0.06", "10")

        assert result.startswith("of:=")
        assert "DURATION" in result


class TestModifiedDuration:
    """Test ModifiedDuration formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = ModifiedDuration()
        metadata = formula.metadata

        assert metadata.name == "MODDURATION"
        assert metadata.category == "bonds"
        assert len(metadata.arguments) == 5

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = ModifiedDuration()
        result = formula.build("1000", "0.05", "0.06", "10", "2")

        assert result.startswith("of:=")
        assert "MDURATION" in result
        assert "TODAY" in result
        assert "0.05" in result
        assert "0.06" in result
        assert "10" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = ModifiedDuration()
        result = formula.build("A1", "A2", "A3", "A4", "A5")

        assert result.startswith("of:=")
        assert "MDURATION" in result

    def test_build_default_frequency(self) -> None:
        """Test formula with default frequency."""
        formula = ModifiedDuration()
        result = formula.build("1000", "0.05", "0.06", "10")

        assert result.startswith("of:=")
        assert "MDURATION" in result


class TestConvexity:
    """Test Convexity formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = Convexity()
        metadata = formula.metadata

        assert metadata.name == "CONVEXITY"
        assert metadata.category == "bonds"
        assert len(metadata.arguments) == 5

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = Convexity()
        result = formula.build("1000", "0.05", "0.06", "10", "2")

        assert result.startswith("of:=")
        assert "DURATION" in result
        assert "0.05" in result
        assert "0.06" in result
        assert "10" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = Convexity()
        result = formula.build("A1", "A2", "A3", "A4", "A5")

        assert result.startswith("of:=")
        assert "DURATION" in result

    def test_build_default_frequency(self) -> None:
        """Test formula with default frequency."""
        formula = Convexity()
        result = formula.build("1000", "0.05", "0.06", "10")

        assert result.startswith("of:=")
        assert "DURATION" in result


class TestBondsFormulasIntegration:
    """Integration tests for bond formulas."""

    def test_all_formulas_have_metadata(self) -> None:
        """Test all bond formulas have valid metadata."""
        formulas = [
            BondPrice(),
            YieldToMaturity(),
            MacDuration(),
            ModifiedDuration(),
            Convexity(),
        ]

        for formula in formulas:
            metadata = formula.metadata
            assert metadata.name
            assert metadata.category == "bonds"
            assert metadata.description
            assert len(metadata.arguments) > 0
            assert len(metadata.examples) > 0

    def test_all_formulas_build_valid_strings(self) -> None:
        """Test all bond formulas build valid ODF strings."""
        test_cases = [
            (BondPrice(), ["1000", "0.05", "0.06", "10", "2"]),
            (YieldToMaturity(), ["950", "1000", "0.05", "10", "2"]),
            (MacDuration(), ["1000", "0.05", "0.06", "10", "2"]),
            (ModifiedDuration(), ["1000", "0.05", "0.06", "10", "2"]),
            (Convexity(), ["1000", "0.05", "0.06", "10", "2"]),
        ]

        for formula, args in test_cases:
            result = formula.build(*args)
            assert result.startswith("of:=")
            assert len(result) > 5

    def test_formulas_accept_default_frequency(self) -> None:
        """Test all bond formulas accept default frequency."""
        test_cases = [
            (BondPrice(), ["1000", "0.05", "0.06", "10"]),
            (YieldToMaturity(), ["950", "1000", "0.05", "10"]),
            (MacDuration(), ["1000", "0.05", "0.06", "10"]),
            (ModifiedDuration(), ["1000", "0.05", "0.06", "10"]),
            (Convexity(), ["1000", "0.05", "0.06", "10"]),
        ]

        for formula, args in test_cases:
            result = formula.build(*args)
            assert result.startswith("of:=")

    def test_duration_formulas_consistency(self) -> None:
        """Test duration formulas use consistent parameters."""
        params = ["1000", "0.05", "0.06", "10", "2"]

        # Macaulay Duration
        mac_formula = MacDuration()
        mac_result = mac_formula.build(*params)
        assert "DURATION" in mac_result

        # Modified Duration
        mod_formula = ModifiedDuration()
        mod_result = mod_formula.build(*params)
        assert "MDURATION" in mod_result

        # Both should use TODAY() for settlement date
        assert "TODAY" in mac_result
        assert "TODAY" in mod_result
