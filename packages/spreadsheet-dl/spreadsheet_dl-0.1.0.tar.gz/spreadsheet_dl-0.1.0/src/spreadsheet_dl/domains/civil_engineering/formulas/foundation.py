"""Foundation design formulas for civil engineering.

CIVIL-FOUNDATION: Foundation design formulas (bearing capacity, settlement)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class BearingCapacityTerzaghi(BaseFormula):
    """Terzaghi bearing capacity formula: q_ult = c*N_c + gamma*D*N_q + 0.5*gamma*B*N_gamma.

    Calculates ultimate bearing capacity using Terzaghi's equation.

        CIVIL-FOUNDATION-001: Terzaghi bearing capacity equation

    Example:
        >>> formula = BearingCapacityTerzaghi()
        >>> formula.build("20", "18", "2", "1.5", "5.14", "1.81", "0.45")
        'of:=20*5.14+18*2*1.81+0.5*18*1.5*0.45'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BEARING_CAPACITY_TERZAGHI",
            category="civil_engineering",
            description="Calculate ultimate bearing capacity: q_ult = c*N_c + gamma*D*N_q + 0.5*gamma*B*N_gamma",
            arguments=(
                FormulaArgument(
                    name="cohesion",
                    type="number",
                    required=True,
                    description="Soil cohesion (kPa)",
                ),
                FormulaArgument(
                    name="unit_weight",
                    type="number",
                    required=True,
                    description="Soil unit weight (kN/m³)",
                ),
                FormulaArgument(
                    name="depth",
                    type="number",
                    required=True,
                    description="Foundation depth (m)",
                ),
                FormulaArgument(
                    name="width",
                    type="number",
                    required=True,
                    description="Foundation width (m)",
                ),
                FormulaArgument(
                    name="nc",
                    type="number",
                    required=True,
                    description="Bearing capacity factor N_c",
                ),
                FormulaArgument(
                    name="nq",
                    type="number",
                    required=True,
                    description="Bearing capacity factor N_q",
                ),
                FormulaArgument(
                    name="ng",
                    type="number",
                    required=True,
                    description="Bearing capacity factor N_gamma",
                ),
            ),
            return_type="number",
            examples=(
                "=BEARING_CAPACITY_TERZAGHI(20; 18; 2; 1.5; 5.14; 1.81; 0.45)  # Terzaghi bearing capacity",
                "=BEARING_CAPACITY_TERZAGHI(A2; B2; C2; D2; E2; F2; G2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: cohesion, unit_weight, depth, width, nc, nq, ng

        Returns:
            ODF formula string: of:=cohesion*nc+unit_weight*depth*nq+0.5*unit_weight*width*ng
        """
        self.validate_arguments(args)
        cohesion, unit_weight, depth, width, nc, nq, ng = args
        return f"of:={cohesion}*{nc}+{unit_weight}*{depth}*{nq}+0.5*{unit_weight}*{width}*{ng}"


@dataclass(slots=True, frozen=True)
class SettlementElastic(BaseFormula):
    """Elastic settlement formula: S = (stress_increase*B*(1-nu²))/E.

    Calculates immediate settlement under elastic conditions.

        CIVIL-FOUNDATION-002: Elastic settlement calculation

    Example:
        >>> formula = SettlementElastic()
        >>> formula.build("100", "2", "20000", "0.3")
        'of:=(100*2*(1-0.3^2))/20000'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SETTLEMENT_ELASTIC",
            category="civil_engineering",
            description="Calculate elastic settlement: S = (stress_increase*B*(1-nu²))/E",
            arguments=(
                FormulaArgument(
                    name="stress_increase",
                    type="number",
                    required=True,
                    description="Increase in vertical stress (kPa)",
                ),
                FormulaArgument(
                    name="width",
                    type="number",
                    required=True,
                    description="Foundation width (m)",
                ),
                FormulaArgument(
                    name="elastic_modulus",
                    type="number",
                    required=True,
                    description="Elastic modulus of soil (kPa)",
                ),
                FormulaArgument(
                    name="poisson_ratio",
                    type="number",
                    required=True,
                    description="Poisson's ratio (dimensionless)",
                ),
            ),
            return_type="number",
            examples=(
                "=SETTLEMENT_ELASTIC(100; 2; 20000; 0.3)  # Immediate settlement",
                "=SETTLEMENT_ELASTIC(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: stress_increase, width, elastic_modulus, poisson_ratio

        Returns:
            ODF formula string: of:=(stress_increase*width*(1-poisson_ratio^2))/elastic_modulus
        """
        self.validate_arguments(args)
        stress_increase, width, elastic_modulus, poisson_ratio = args
        return (
            f"of:=({stress_increase}*{width}*(1-{poisson_ratio}^2))/{elastic_modulus}"
        )


@dataclass(slots=True, frozen=True)
class ConsolidationSettlement(BaseFormula):
    """Consolidation settlement formula: S = (C_c*H/(1+e_0))*log10(p_f/p_0).

    Calculates primary consolidation settlement.

        CIVIL-FOUNDATION-003: Primary consolidation settlement

    Example:
        >>> formula = ConsolidationSettlement()
        >>> formula.build("0.3", "0.8", "5", "100", "150")
        'of:=(0.3*5/(1+0.8))*LOG10(150/100)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CONSOLIDATION_SETTLEMENT",
            category="civil_engineering",
            description="Calculate consolidation settlement: S = (C_c*H/(1+e_0))*log10(p_f/p_0)",
            arguments=(
                FormulaArgument(
                    name="compression_index",
                    type="number",
                    required=True,
                    description="Compression index C_c (dimensionless)",
                ),
                FormulaArgument(
                    name="initial_void_ratio",
                    type="number",
                    required=True,
                    description="Initial void ratio e_0 (dimensionless)",
                ),
                FormulaArgument(
                    name="thickness",
                    type="number",
                    required=True,
                    description="Layer thickness (m)",
                ),
                FormulaArgument(
                    name="initial_pressure",
                    type="number",
                    required=True,
                    description="Initial effective stress (kPa)",
                ),
                FormulaArgument(
                    name="final_pressure",
                    type="number",
                    required=True,
                    description="Final effective stress (kPa)",
                ),
            ),
            return_type="number",
            examples=(
                "=CONSOLIDATION_SETTLEMENT(0.3; 0.8; 5; 100; 150)  # Primary consolidation",
                "=CONSOLIDATION_SETTLEMENT(A2; B2; C2; D2; E2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: compression_index, initial_void_ratio, thickness, initial_pressure, final_pressure

        Returns:
            ODF formula string: of:=(compression_index*thickness/(1+initial_void_ratio))*LOG10(final_pressure/initial_pressure)
        """
        self.validate_arguments(args)
        (
            compression_index,
            initial_void_ratio,
            thickness,
            initial_pressure,
            final_pressure,
        ) = args
        return f"of:=({compression_index}*{thickness}/(1+{initial_void_ratio}))*LOG10({final_pressure}/{initial_pressure})"


__all__ = [
    "BearingCapacityTerzaghi",
    "ConsolidationSettlement",
    "SettlementElastic",
]
