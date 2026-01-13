"""Soil mechanics formulas for civil engineering.

Soil formulas (BEARING_CAPACITY, SETTLEMENT, SOIL_PRESSURE)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class BearingCapacityFormula(BaseFormula):
    """Bearing capacity formula: q_ult = c*N_c + gamma*D*N_q + 0.5*gamma*B*N_gamma.

    Calculates ultimate bearing capacity of soil using Terzaghi's equation.

        BEARING_CAPACITY formula

    Example:
        >>> formula = BearingCapacityFormula()
        >>> formula.build("20", "5.14", "18", "2", "1.81", "1.5", "0.45")
        '20*5.14+18*2*1.81+0.5*18*1.5*0.45'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BEARING_CAPACITY",
            category="civil_engineering",
            description="Calculate ultimate bearing capacity: q_ult = c*N_c + gamma*D*N_q + 0.5*gamma*B*N_gamma",
            arguments=(
                FormulaArgument(
                    name="c",
                    type="number",
                    required=True,
                    description="Soil cohesion (kPa)",
                ),
                FormulaArgument(
                    name="Nc",
                    type="number",
                    required=True,
                    description="Bearing capacity factor N_c",
                ),
                FormulaArgument(
                    name="gamma",
                    type="number",
                    required=True,
                    description="Soil unit weight (kN/m³)",
                ),
                FormulaArgument(
                    name="D",
                    type="number",
                    required=True,
                    description="Foundation depth (m)",
                ),
                FormulaArgument(
                    name="Nq",
                    type="number",
                    required=True,
                    description="Bearing capacity factor N_q",
                ),
                FormulaArgument(
                    name="B",
                    type="number",
                    required=True,
                    description="Foundation width (m)",
                ),
                FormulaArgument(
                    name="Ngamma",
                    type="number",
                    required=True,
                    description="Bearing capacity factor N_gamma",
                ),
            ),
            return_type="number",
            examples=(
                "=BEARING_CAPACITY(20; 5.14; 18; 2; 1.81; 1.5; 0.45)  # Terzaghi bearing capacity",
                "=BEARING_CAPACITY(A2; B2; C2; D2; E2; F2; G2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: c, Nc, gamma, D, Nq, B, Ngamma

        Returns:
            ODF formula string: c*Nc+gamma*D*Nq+0.5*gamma*B*Ngamma
        """
        self.validate_arguments(args)
        c, Nc, gamma, D, Nq, B, Ngamma = args
        return f"of:={c}*{Nc}+{gamma}*{D}*{Nq}+0.5*{gamma}*{B}*{Ngamma}"


@dataclass(slots=True, frozen=True)
class SettlementFormula(BaseFormula):
    """Settlement formula: S = (H*delta_sigma)/E_s.

    Calculates soil settlement under applied stress.

        SETTLEMENT formula

    Example:
        >>> formula = SettlementFormula()
        >>> formula.build("3000", "100", "10000")
        '3000*100/10000'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SETTLEMENT",
            category="civil_engineering",
            description="Calculate soil settlement: S = (H*delta_sigma)/E_s",
            arguments=(
                FormulaArgument(
                    name="H",
                    type="number",
                    required=True,
                    description="Layer thickness (mm)",
                ),
                FormulaArgument(
                    name="delta_sigma",
                    type="number",
                    required=True,
                    description="Change in vertical stress (kPa)",
                ),
                FormulaArgument(
                    name="Es",
                    type="number",
                    required=True,
                    description="Soil modulus of elasticity (kPa)",
                ),
            ),
            return_type="number",
            examples=(
                "=SETTLEMENT(3000; 100; 10000)  # Elastic settlement calculation",
                "=SETTLEMENT(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: H, delta_sigma, Es

        Returns:
            ODF formula string: H*delta_sigma/Es
        """
        self.validate_arguments(args)
        H, delta_sigma, Es = args
        return f"of:={H}*{delta_sigma}/{Es}"


@dataclass(slots=True, frozen=True)
class SoilPressureFormula(BaseFormula):
    """Soil pressure formula: sigma = P/A.

    Calculates soil bearing pressure under applied load.

        SOIL_PRESSURE formula

    Example:
        >>> formula = SoilPressureFormula()
        >>> formula.build("1000", "4")
        '1000/4'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SOIL_PRESSURE",
            category="civil_engineering",
            description="Calculate soil bearing pressure: sigma = P/A",
            arguments=(
                FormulaArgument(
                    name="P",
                    type="number",
                    required=True,
                    description="Applied load (kN)",
                ),
                FormulaArgument(
                    name="A",
                    type="number",
                    required=True,
                    description="Footing area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=SOIL_PRESSURE(1000; 4)  # Bearing pressure = 250 kPa",
                "=SOIL_PRESSURE(A2; B2)  # Using cell references",
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


__all__ = [
    "BearingCapacityFormula",
    "SettlementFormula",
    "SoilPressureFormula",
]
