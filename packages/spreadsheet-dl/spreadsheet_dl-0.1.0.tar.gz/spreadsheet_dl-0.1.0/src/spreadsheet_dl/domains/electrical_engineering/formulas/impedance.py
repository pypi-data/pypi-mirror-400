"""Impedance calculation formulas for electrical engineering.

Impedance formulas (PARALLEL_R, SERIES_R, CAPACITANCE, INDUCTANCE)
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


class ParallelResistanceFormula(BaseFormula):
    """Parallel resistance formula: 1/R_total = 1/R1 + 1/R2 + ...

    Calculates total resistance of resistors in parallel.

        PARALLEL_RESISTANCE formula

    Example:
        >>> formula = ParallelResistanceFormula()
        >>> formula.build("100", "100")
        'of:=1/(1/100+1/100)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="PARALLEL_RESISTANCE",
            category="electrical_engineering",
            description="Calculate parallel resistance: 1/R_total = 1/R1 + 1/R2 + ...",
            arguments=(
                FormulaArgument(
                    name="r1",
                    type="number",
                    required=True,
                    description="First resistance in ohms (Ω)",
                ),
                FormulaArgument(
                    name="r2",
                    type="number",
                    required=True,
                    description="Second resistance in ohms (Ω)",
                ),
                FormulaArgument(
                    name="r3",
                    type="number",
                    required=False,
                    description="Additional resistance in ohms (Ω)",
                ),
            ),
            return_type="number",
            examples=(
                "=PARALLEL_RESISTANCE(100, 100)  # 50 ohms",
                "=PARALLEL_RESISTANCE(A2, B2)  # Two resistors",
                "=PARALLEL_RESISTANCE(A2, B2, C2)  # Three resistors",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: r1, r2, r3, ... (variable number of resistances)

        Returns:
            ODF formula string: of:=1/(1/r1+1/r2+...)
        """
        if len(args) < 2:
            msg = f"{self.metadata.name} requires at least 2 arguments, got {len(args)}"
            raise ValueError(msg)

        # Build reciprocal sum
        reciprocals = "+".join(f"1/{r}" for r in args)
        return f"of:=1/({reciprocals})"


class SeriesResistanceFormula(BaseFormula):
    """Series resistance formula: R_total = R1 + R2 + ...

    Calculates total resistance of resistors in series.

        SERIES_RESISTANCE formula

    Example:
        >>> formula = SeriesResistanceFormula()
        >>> formula.build("100", "100")
        'of:=100+100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SERIES_RESISTANCE",
            category="electrical_engineering",
            description="Calculate series resistance: R_total = R1 + R2 + ...",
            arguments=(
                FormulaArgument(
                    name="r1",
                    type="number",
                    required=True,
                    description="First resistance in ohms (Ω)",
                ),
                FormulaArgument(
                    name="r2",
                    type="number",
                    required=True,
                    description="Second resistance in ohms (Ω)",
                ),
                FormulaArgument(
                    name="r3",
                    type="number",
                    required=False,
                    description="Additional resistance in ohms (Ω)",
                ),
            ),
            return_type="number",
            examples=(
                "=SERIES_RESISTANCE(100, 100)  # 200 ohms",
                "=SERIES_RESISTANCE(A2, B2)  # Two resistors",
                "=SERIES_RESISTANCE(A2, B2, C2, D2)  # Four resistors",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: r1, r2, r3, ... (variable number of resistances)

        Returns:
            ODF formula string: of:=r1+r2+...
        """
        if len(args) < 2:
            msg = f"{self.metadata.name} requires at least 2 arguments, got {len(args)}"
            raise ValueError(msg)

        return "of:=" + "+".join(str(r) for r in args)


class CapacitanceFormula(BaseFormula):
    """Capacitance formula: C = 1 / (2*pi * f * X_C).

    Calculates capacitance from frequency and capacitive reactance.

        CAPACITANCE formula

    Example:
        >>> formula = CapacitanceFormula()
        >>> formula.build("1000", "159.15")
        'of:=1/(2*PI()*1000*159.15)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CAPACITANCE",
            category="electrical_engineering",
            description="Calculate capacitance from frequency and reactance: C = 1 / (2*pi * f * X_C)",
            arguments=(
                FormulaArgument(
                    name="frequency",
                    type="number",
                    required=True,
                    description="Frequency in hertz (Hz)",
                ),
                FormulaArgument(
                    name="reactance",
                    type="number",
                    required=True,
                    description="Capacitive reactance in ohms (Ω)",
                ),
            ),
            return_type="number",
            examples=(
                "=CAPACITANCE(1000, 159.15)  # ~1μF at 1kHz",
                "=CAPACITANCE(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: frequency, reactance

        Returns:
            ODF formula string: of:=1/(2*PI()*frequency*reactance)
        """
        self.validate_arguments(args)
        frequency, reactance = args
        return f"of:=1/(2*PI()*{frequency}*{reactance})"


class InductanceFormula(BaseFormula):
    """Inductance formula: L = X_L / (2*pi * f).

    Calculates inductance from frequency and inductive reactance.

        INDUCTANCE formula

    Example:
        >>> formula = InductanceFormula()
        >>> formula.build("1000", "628.3")
        'of:=628.3/(2*PI()*1000)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="INDUCTANCE",
            category="electrical_engineering",
            description="Calculate inductance from frequency and reactance: L = X_L / (2*pi * f)",
            arguments=(
                FormulaArgument(
                    name="frequency",
                    type="number",
                    required=True,
                    description="Frequency in hertz (Hz)",
                ),
                FormulaArgument(
                    name="reactance",
                    type="number",
                    required=True,
                    description="Inductive reactance in ohms (Ω)",
                ),
            ),
            return_type="number",
            examples=(
                "=INDUCTANCE(1000, 628.3)  # ~100mH at 1kHz",
                "=INDUCTANCE(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: frequency, reactance

        Returns:
            ODF formula string: of:=reactance/(2*PI()*frequency)
        """
        self.validate_arguments(args)
        frequency, reactance = args
        return f"of:={reactance}/(2*PI()*{frequency})"


__all__ = [
    "CapacitanceFormula",
    "InductanceFormula",
    "ParallelResistanceFormula",
    "SeriesResistanceFormula",
]
