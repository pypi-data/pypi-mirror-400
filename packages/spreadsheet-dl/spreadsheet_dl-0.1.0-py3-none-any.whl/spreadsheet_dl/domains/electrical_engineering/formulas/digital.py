"""Digital circuit formulas for electrical engineering.

Digital logic formulas (NAND, NOR, XOR, binary conversions)
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


class LogicNANDFormula(BaseFormula):
    """NAND gate truth table logic: NOT(AND(A, B)).

    Calculates NAND gate output given two boolean inputs.

        LOGIC_NAND formula

    Example:
        >>> formula = LogicNANDFormula()
        >>> formula.build("TRUE", "FALSE")
        'NOT(AND(TRUE,FALSE))'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LOGIC_NAND",
            category="electrical_engineering",
            description="NAND gate logic: NOT(AND(input_a, input_b))",
            arguments=(
                FormulaArgument(
                    name="input_a",
                    type="boolean",
                    required=True,
                    description="First boolean input",
                ),
                FormulaArgument(
                    name="input_b",
                    type="boolean",
                    required=True,
                    description="Second boolean input",
                ),
            ),
            return_type="boolean",
            examples=(
                "=LOGIC_NAND(TRUE, TRUE)  # FALSE",
                "=LOGIC_NAND(TRUE, FALSE)  # TRUE",
                "=LOGIC_NAND(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: input_a, input_b

        Returns:
            ODF formula string: NOT(AND(input_a,input_b))
        """
        self.validate_arguments(args)
        input_a, input_b = args
        return f"of:=NOT(AND({input_a},{input_b}))"


class LogicNORFormula(BaseFormula):
    """NOR gate truth table logic: NOT(OR(A, B)).

    Calculates NOR gate output given two boolean inputs.

        LOGIC_NOR formula

    Example:
        >>> formula = LogicNORFormula()
        >>> formula.build("FALSE", "FALSE")
        'NOT(OR(FALSE,FALSE))'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LOGIC_NOR",
            category="electrical_engineering",
            description="NOR gate logic: NOT(OR(input_a, input_b))",
            arguments=(
                FormulaArgument(
                    name="input_a",
                    type="boolean",
                    required=True,
                    description="First boolean input",
                ),
                FormulaArgument(
                    name="input_b",
                    type="boolean",
                    required=True,
                    description="Second boolean input",
                ),
            ),
            return_type="boolean",
            examples=(
                "=LOGIC_NOR(FALSE, FALSE)  # TRUE",
                "=LOGIC_NOR(TRUE, FALSE)  # FALSE",
                "=LOGIC_NOR(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: input_a, input_b

        Returns:
            ODF formula string: NOT(OR(input_a,input_b))
        """
        self.validate_arguments(args)
        input_a, input_b = args
        return f"of:=NOT(OR({input_a},{input_b}))"


class LogicXORFormula(BaseFormula):
    """XOR gate truth table logic.

    Calculates XOR gate output: (A AND NOT B) OR (NOT A AND B).

        LOGIC_XOR formula

    Example:
        >>> formula = LogicXORFormula()
        >>> formula.build("TRUE", "FALSE")
        'OR(AND(TRUE,NOT(FALSE)),AND(NOT(TRUE),FALSE))'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LOGIC_XOR",
            category="electrical_engineering",
            description="XOR gate logic: (A AND NOT B) OR (NOT A AND B)",
            arguments=(
                FormulaArgument(
                    name="input_a",
                    type="boolean",
                    required=True,
                    description="First boolean input",
                ),
                FormulaArgument(
                    name="input_b",
                    type="boolean",
                    required=True,
                    description="Second boolean input",
                ),
            ),
            return_type="boolean",
            examples=(
                "=LOGIC_XOR(TRUE, FALSE)  # TRUE",
                "=LOGIC_XOR(TRUE, TRUE)  # FALSE",
                "=LOGIC_XOR(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: input_a, input_b

        Returns:
            ODF formula string: OR(AND(input_a,NOT(input_b)),AND(NOT(input_a),input_b))
        """
        self.validate_arguments(args)
        input_a, input_b = args
        return f"of:=OR(AND({input_a},NOT({input_b})),AND(NOT({input_a}),{input_b}))"


class BinaryToDecimalFormula(BaseFormula):
    """Binary to decimal conversion.

    Converts a binary string to decimal number.

        BINARY_TO_DECIMAL formula

    Example:
        >>> formula = BinaryToDecimalFormula()
        >>> formula.build('"1010"')
        'BIN2DEC("1010")'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BINARY_TO_DECIMAL",
            category="electrical_engineering",
            description="Convert binary string to decimal: BIN2DEC(binary_value)",
            arguments=(
                FormulaArgument(
                    name="binary_value",
                    type="text",
                    required=True,
                    description="Binary string (e.g., '1010')",
                ),
            ),
            return_type="number",
            examples=(
                '=BINARY_TO_DECIMAL("1010")  # 10',
                '=BINARY_TO_DECIMAL("11111111")  # 255',
                "=BINARY_TO_DECIMAL(A2)  # Using cell reference",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: binary_value

        Returns:
            ODF formula string: BIN2DEC(binary_value)
        """
        self.validate_arguments(args)
        binary_value = args[0]
        return f"of:=BIN2DEC({binary_value})"


class DecimalToBinaryFormula(BaseFormula):
    """Decimal to binary conversion.

    Converts a decimal number to binary string.

        DECIMAL_TO_BINARY formula

    Example:
        >>> formula = DecimalToBinaryFormula()
        >>> formula.build("10")
        'DEC2BIN(10)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="DECIMAL_TO_BINARY",
            category="electrical_engineering",
            description="Convert decimal to binary string: DEC2BIN(decimal_value)",
            arguments=(
                FormulaArgument(
                    name="decimal_value",
                    type="number",
                    required=True,
                    description="Decimal number",
                ),
            ),
            return_type="text",
            examples=(
                "=DECIMAL_TO_BINARY(10)  # '1010'",
                "=DECIMAL_TO_BINARY(255)  # '11111111'",
                "=DECIMAL_TO_BINARY(A2)  # Using cell reference",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: decimal_value

        Returns:
            ODF formula string: DEC2BIN(decimal_value)
        """
        self.validate_arguments(args)
        decimal_value = args[0]
        return f"of:=DEC2BIN({decimal_value})"


__all__ = [
    "BinaryToDecimalFormula",
    "DecimalToBinaryFormula",
    "LogicNANDFormula",
    "LogicNORFormula",
    "LogicXORFormula",
]
