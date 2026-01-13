"""Moment and bending formulas for mechanical engineering.

Moment formulas (MOMENT_OF_INERTIA, BENDING_STRESS, TORSIONAL_STRESS)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class MomentOfInertiaFormula(BaseFormula):
    """Moment of Inertia formula for rectangular cross-section: I = b * h³ / 12.

    Calculates second moment of area for bending calculations.

        MOMENT_OF_INERTIA formula

    Example:
        >>> formula = MomentOfInertiaFormula()
        >>> formula.build("10", "20")
        '10*POWER(20;3)/12'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="MOMENT_OF_INERTIA",
            category="mechanical_engineering",
            description="Calculate second moment of area for rectangular section: I = b * h³ / 12",
            arguments=(
                FormulaArgument(
                    name="width",
                    type="number",
                    required=True,
                    description="Width (b) in mm",
                ),
                FormulaArgument(
                    name="height",
                    type="number",
                    required=True,
                    description="Height (h) in mm",
                ),
            ),
            return_type="number",
            examples=(
                "=MOMENT_OF_INERTIA(10; 20)  # 6666.67 mm⁴",
                "=MOMENT_OF_INERTIA(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: width, height

        Returns:
            ODF formula string: width*height^3/12
        """
        self.validate_arguments(args)
        width, height = args
        return f"of:={width}*POWER({height};3)/12"


@dataclass(slots=True, frozen=True)
class BendingStressFormula(BaseFormula):
    """Bending Stress formula: sigma = M * y / I.

    Calculates bending stress in a beam given bending moment, distance from
    neutral axis, and moment of inertia.

        BENDING_STRESS formula

    Example:
        >>> formula = BendingStressFormula()
        >>> formula.build("1000000", "10", "6666.67")
        '1000000*10/6666.67'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BENDING_STRESS",
            category="mechanical_engineering",
            description="Calculate bending stress: sigma = M * y / I",
            arguments=(
                FormulaArgument(
                    name="moment",
                    type="number",
                    required=True,
                    description="Bending moment (M) in N·mm",
                ),
                FormulaArgument(
                    name="distance",
                    type="number",
                    required=True,
                    description="Distance from neutral axis (y) in mm",
                ),
                FormulaArgument(
                    name="inertia",
                    type="number",
                    required=True,
                    description="Moment of inertia (I) in mm⁴",
                ),
            ),
            return_type="number",
            examples=(
                "=BENDING_STRESS(1000000; 10; 6666.67)  # 1500 MPa",
                "=BENDING_STRESS(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: moment, distance, inertia

        Returns:
            ODF formula string: moment*distance/inertia
        """
        self.validate_arguments(args)
        moment, distance, inertia = args
        return f"of:={moment}*{distance}/{inertia}"


@dataclass(slots=True, frozen=True)
class TorsionalStressFormula(BaseFormula):
    """Torsional Stress formula: tau = T * r / J.

    Calculates torsional shear stress in a shaft given torque, radius,
    and polar moment of inertia.

        TORSIONAL_STRESS formula

    Example:
        >>> formula = TorsionalStressFormula()
        >>> formula.build("500000", "10", "15707.96")
        '500000*10/15707.96'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="TORSIONAL_STRESS",
            category="mechanical_engineering",
            description="Calculate torsional shear stress: tau = T * r / J",
            arguments=(
                FormulaArgument(
                    name="torque",
                    type="number",
                    required=True,
                    description="Torque (T) in N·mm",
                ),
                FormulaArgument(
                    name="radius",
                    type="number",
                    required=True,
                    description="Radius (r) in mm",
                ),
                FormulaArgument(
                    name="polar_inertia",
                    type="number",
                    required=True,
                    description="Polar moment of inertia (J) in mm⁴",
                ),
            ),
            return_type="number",
            examples=(
                "=TORSIONAL_STRESS(500000; 10; 15707.96)  # 318.3 MPa",
                "=TORSIONAL_STRESS(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: torque, radius, polar_inertia

        Returns:
            ODF formula string: torque*radius/polar_inertia
        """
        self.validate_arguments(args)
        torque, radius, polar_inertia = args
        return f"of:={torque}*{radius}/{polar_inertia}"


__all__ = [
    "BendingStressFormula",
    "MomentOfInertiaFormula",
    "TorsionalStressFormula",
]
