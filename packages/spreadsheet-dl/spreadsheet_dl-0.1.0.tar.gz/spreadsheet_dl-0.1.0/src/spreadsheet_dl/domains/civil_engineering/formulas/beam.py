"""Beam calculation formulas for civil engineering.

Beam formulas (BEAM_DEFLECTION, SHEAR_STRESS, MOMENT)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class BeamDeflectionFormula(BaseFormula):
    """Beam deflection formula: delta = (5*w*L^4)/(384*E*I).

    Calculates maximum deflection of a simply supported beam with
    uniformly distributed load.

        BEAM_DEFLECTION formula

    Example:
        >>> formula = BeamDeflectionFormula()
        >>> formula.build("10", "5000", "200000", "8.33e6")
        '(5*10*5000^4)/(384*200000*8.33e6)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BEAM_DEFLECTION",
            category="civil_engineering",
            description="Calculate beam deflection: delta = (5*w*L^4)/(384*E*I)",
            arguments=(
                FormulaArgument(
                    name="w",
                    type="number",
                    required=True,
                    description="Uniformly distributed load (kN/m)",
                ),
                FormulaArgument(
                    name="L",
                    type="number",
                    required=True,
                    description="Beam span length (mm)",
                ),
                FormulaArgument(
                    name="E",
                    type="number",
                    required=True,
                    description="Modulus of elasticity (MPa)",
                ),
                FormulaArgument(
                    name="I",
                    type="number",
                    required=True,
                    description="Moment of inertia (mm⁴)",
                ),
            ),
            return_type="number",
            examples=(
                "=BEAM_DEFLECTION(10; 5000; 200000; 8.33e6)  # Simply supported beam deflection",
                "=BEAM_DEFLECTION(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: w, L, E, I

        Returns:
            ODF formula string: (5*w*L^4)/(384*E*I)
        """
        self.validate_arguments(args)
        w, L, E, I = args  # noqa: E741 - I is standard notation for moment of inertia
        return f"of:=(5*{w}*{L}^4)/(384*{E}*{I})"


@dataclass(slots=True, frozen=True)
class ShearStressFormula(BaseFormula):
    """Shear stress formula: tau = V*Q/(I*b).

    Calculates shear stress in a beam cross-section.

        SHEAR_STRESS formula

    Example:
        >>> formula = ShearStressFormula()
        >>> formula.build("50000", "1e6", "8.33e6", "200")
        '50000*1e6/(8.33e6*200)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SHEAR_STRESS",
            category="civil_engineering",
            description="Calculate shear stress: tau = V*Q/(I*b)",
            arguments=(
                FormulaArgument(
                    name="V",
                    type="number",
                    required=True,
                    description="Shear force (N)",
                ),
                FormulaArgument(
                    name="Q",
                    type="number",
                    required=True,
                    description="First moment of area (mm³)",
                ),
                FormulaArgument(
                    name="I",
                    type="number",
                    required=True,
                    description="Moment of inertia (mm⁴)",
                ),
                FormulaArgument(
                    name="b",
                    type="number",
                    required=True,
                    description="Width at neutral axis (mm)",
                ),
            ),
            return_type="number",
            examples=(
                "=SHEAR_STRESS(50000; 1e6; 8.33e6; 200)  # Shear stress calculation",
                "=SHEAR_STRESS(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: V, Q, I, b

        Returns:
            ODF formula string: V*Q/(I*b)
        """
        self.validate_arguments(args)
        V, Q, I, b = args  # noqa: E741 - I is standard notation for moment of inertia
        return f"of:={V}*{Q}/({I}*{b})"


@dataclass(slots=True, frozen=True)
class MomentFormula(BaseFormula):
    """Bending moment formula: M = w*L^2/8.

    Calculates maximum bending moment for simply supported beam
    with uniformly distributed load.

        MOMENT formula

    Example:
        >>> formula = MomentFormula()
        >>> formula.build("10", "5000")
        '10*5000^2/8'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="MOMENT",
            category="civil_engineering",
            description="Calculate bending moment: M = w*L^2/8",
            arguments=(
                FormulaArgument(
                    name="w",
                    type="number",
                    required=True,
                    description="Uniformly distributed load (kN/m)",
                ),
                FormulaArgument(
                    name="L",
                    type="number",
                    required=True,
                    description="Beam span length (mm)",
                ),
            ),
            return_type="number",
            examples=(
                "=MOMENT(10; 5000)  # Maximum moment for simply supported beam",
                "=MOMENT(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: w, L

        Returns:
            ODF formula string: w*L^2/8
        """
        self.validate_arguments(args)
        w, L = args
        return f"of:={w}*{L}^2/8"


__all__ = [
    "BeamDeflectionFormula",
    "MomentFormula",
    "ShearStressFormula",
]
