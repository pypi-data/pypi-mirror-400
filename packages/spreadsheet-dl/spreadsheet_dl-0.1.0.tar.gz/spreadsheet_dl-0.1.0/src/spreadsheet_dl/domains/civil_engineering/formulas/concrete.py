"""Concrete design formulas for civil engineering.

Concrete formulas (CONCRETE_STRENGTH, REINFORCEMENT_RATIO, CRACK_WIDTH)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ConcreteStrengthFormula(BaseFormula):
    """Concrete compressive strength formula: f'_c = P/A.

    Calculates concrete compressive strength from test cylinder results.

        CONCRETE_STRENGTH formula

    Example:
        >>> formula = ConcreteStrengthFormula()
        >>> formula.build("400000", "19635")
        '400000/19635'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CONCRETE_STRENGTH",
            category="civil_engineering",
            description="Calculate concrete compressive strength: f'_c = P/A",
            arguments=(
                FormulaArgument(
                    name="P",
                    type="number",
                    required=True,
                    description="Maximum load at failure (N)",
                ),
                FormulaArgument(
                    name="A",
                    type="number",
                    required=True,
                    description="Cross-sectional area of specimen (mm²)",
                ),
            ),
            return_type="number",
            examples=(
                "=CONCRETE_STRENGTH(400000; 19635)  # 150mm diameter cylinder",
                "=CONCRETE_STRENGTH(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: P, A

        Returns:
            ODF formula string: P/A
        """
        self.validate_arguments(args)
        P, A = args
        return f"of:={P}/{A}"


@dataclass(slots=True, frozen=True)
class ReinforcementRatioFormula(BaseFormula):
    """Reinforcement ratio formula: rho = A_s/(b*d).

    Calculates reinforcement ratio for concrete beam design.

        REINFORCEMENT_RATIO formula

    Example:
        >>> formula = ReinforcementRatioFormula()
        >>> formula.build("1256", "300", "450")
        '1256/(300*450)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="REINFORCEMENT_RATIO",
            category="civil_engineering",
            description="Calculate reinforcement ratio: rho = A_s/(b*d)",
            arguments=(
                FormulaArgument(
                    name="As",
                    type="number",
                    required=True,
                    description="Area of steel reinforcement (mm²)",
                ),
                FormulaArgument(
                    name="b",
                    type="number",
                    required=True,
                    description="Beam width (mm)",
                ),
                FormulaArgument(
                    name="d",
                    type="number",
                    required=True,
                    description="Effective depth (mm)",
                ),
            ),
            return_type="number",
            examples=(
                "=REINFORCEMENT_RATIO(1256; 300; 450)  # 4-20mm bars in 300x500 beam",
                "=REINFORCEMENT_RATIO(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: As, b, d

        Returns:
            ODF formula string: As/(b*d)
        """
        self.validate_arguments(args)
        As, b, d = args
        return f"of:={As}/({b}*{d})"


@dataclass(slots=True, frozen=True)
class CrackWidthFormula(BaseFormula):
    """Crack width formula: w = s_r*epsilon_m.

    Calculates maximum crack width in reinforced concrete.

        CRACK_WIDTH formula

    Example:
        >>> formula = CrackWidthFormula()
        >>> formula.build("150", "0.0002")
        '150*0.0002'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CRACK_WIDTH",
            category="civil_engineering",
            description="Calculate crack width: w = s_r*epsilon_m",
            arguments=(
                FormulaArgument(
                    name="sr",
                    type="number",
                    required=True,
                    description="Maximum crack spacing (mm)",
                ),
                FormulaArgument(
                    name="epsilon_m",
                    type="number",
                    required=True,
                    description="Mean strain at crack location",
                ),
            ),
            return_type="number",
            examples=(
                "=CRACK_WIDTH(150; 0.0002)  # Crack width calculation",
                "=CRACK_WIDTH(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: sr, epsilon_m

        Returns:
            ODF formula string: sr*epsilon_m
        """
        self.validate_arguments(args)
        sr, epsilon_m = args
        return f"of:={sr}*{epsilon_m}"


__all__ = [
    "ConcreteStrengthFormula",
    "CrackWidthFormula",
    "ReinforcementRatioFormula",
]
