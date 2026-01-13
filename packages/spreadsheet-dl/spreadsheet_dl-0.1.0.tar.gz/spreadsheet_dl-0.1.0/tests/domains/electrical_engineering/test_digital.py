"""Tests for digital electronics formulas in electrical engineering.

Implements:
    Tests for logic gates and binary conversion formulas
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.electrical_engineering.formulas.digital import (
    BinaryToDecimalFormula,
    DecimalToBinaryFormula,
    LogicNANDFormula,
    LogicNORFormula,
    LogicXORFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.engineering]


# ============================================================================
# Logic Gate Formula Tests
# ============================================================================


def test_logic_xor_formula() -> None:
    """Test XOR logic gate formula."""
    formula = LogicXORFormula()

    # Test metadata
    assert formula.metadata.name == "LOGIC_XOR"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "boolean"

    # Test formula building
    result = formula.build("A1", "B1")
    assert "A1" in result
    assert "B1" in result


def test_logic_nand_formula() -> None:
    """Test NAND logic gate formula."""
    formula = LogicNANDFormula()

    # Test metadata
    assert formula.metadata.name == "LOGIC_NAND"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "boolean"

    # Test formula building
    result = formula.build("A1", "B1")
    assert "A1" in result
    assert "B1" in result


def test_logic_nor_formula() -> None:
    """Test NOR logic gate formula."""
    formula = LogicNORFormula()

    # Test metadata
    assert formula.metadata.name == "LOGIC_NOR"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "boolean"

    # Test formula building
    result = formula.build("A1", "B1")
    assert "A1" in result
    assert "B1" in result


# ============================================================================
# Binary Conversion Formula Tests
# ============================================================================


def test_binary_to_decimal_formula() -> None:
    """Test binary to decimal conversion formula."""
    formula = BinaryToDecimalFormula()

    # Test metadata
    assert formula.metadata.name == "BINARY_TO_DECIMAL"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) >= 1
    assert formula.metadata.return_type == "number"

    # Test formula building with cell reference
    result = formula.build("A1")
    assert "A1" in result


def test_decimal_to_binary_formula() -> None:
    """Test decimal to binary conversion formula."""
    formula = DecimalToBinaryFormula()

    # Test metadata
    assert formula.metadata.name == "DECIMAL_TO_BINARY"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) >= 1
    assert formula.metadata.return_type == "text"

    # Test formula building with cell reference
    result = formula.build("A1")
    assert "A1" in result


# ============================================================================
# Validation Tests
# ============================================================================


def test_logic_xor_validation() -> None:
    """Test XOR formula argument validation."""
    formula = LogicXORFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("1")


def test_logic_nand_validation() -> None:
    """Test NAND formula argument validation."""
    formula = LogicNANDFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("1")


def test_logic_nor_validation() -> None:
    """Test NOR formula argument validation."""
    formula = LogicNORFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("1")


def test_binary_to_decimal_validation() -> None:
    """Test binary to decimal formula argument validation."""
    formula = BinaryToDecimalFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 1 argument"):
        formula.build()


def test_decimal_to_binary_validation() -> None:
    """Test decimal to binary formula argument validation."""
    formula = DecimalToBinaryFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 1 argument"):
        formula.build()


# ============================================================================
# Metadata Completeness Tests
# ============================================================================


def test_all_digital_formulas_have_complete_metadata() -> None:
    """Ensure all digital formulas have proper metadata."""
    formulas = [
        LogicXORFormula,
        LogicNANDFormula,
        LogicNORFormula,
        BinaryToDecimalFormula,
        DecimalToBinaryFormula,
    ]

    for formula_class in formulas:
        formula = formula_class()  # type: ignore[abstract]
        metadata = formula.metadata

        # Check required metadata fields
        assert metadata.name
        assert metadata.category == "electrical_engineering"
        assert metadata.description
        assert len(metadata.arguments) > 0
        assert metadata.return_type
        assert len(metadata.examples) > 0


# ============================================================================
# Integration Tests
# ============================================================================


def test_digital_workflow() -> None:
    """Test complete digital electronics workflow using formulas."""
    xor = LogicXORFormula()
    nand = LogicNANDFormula()
    nor = LogicNORFormula()

    # Build logic gate formulas with cell references
    xor_result = xor.build("A1", "B1")
    nand_result = nand.build("A1", "B1")
    nor_result = nor.build("A1", "B1")

    # All should contain the cell references
    assert "A1" in xor_result
    assert "A1" in nand_result
    assert "A1" in nor_result


def test_binary_conversion_workflow() -> None:
    """Test binary conversion workflow."""
    bin_to_dec = BinaryToDecimalFormula()
    dec_to_bin = DecimalToBinaryFormula()

    # Build conversion formulas
    b2d_result = bin_to_dec.build("A1")
    d2b_result = dec_to_bin.build("B1")

    # Both should produce valid formulas
    assert "A1" in b2d_result
    assert "B1" in d2b_result
