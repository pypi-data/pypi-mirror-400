"""Stress and strain formulas for mechanical engineering.

Stress/strain formulas (STRESS, STRAIN, YOUNGS_MODULUS)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class StressFormula(BaseFormula):
    """Stress formula: sigma = F / A.

    Calculates normal stress given force and area.

        STRESS formula

    Example:
        >>> formula = StressFormula()
        >>> formula.build("1000", "100")
        '1000/100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="STRESS",
            category="mechanical_engineering",
            description="Calculate normal stress from force and area: sigma = F / A",
            arguments=(
                FormulaArgument(
                    name="force",
                    type="number",
                    required=True,
                    description="Force in newtons (N)",
                ),
                FormulaArgument(
                    name="area",
                    type="number",
                    required=True,
                    description="Cross-sectional area in mm²",
                ),
            ),
            return_type="number",
            examples=(
                "=STRESS(1000; 100)  # 10 MPa",
                "=STRESS(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: force, area

        Returns:
            ODF formula string: force/area
        """
        self.validate_arguments(args)
        force, area = args
        return f"of:={force}/{area}"


@dataclass(slots=True, frozen=True)
class StrainFormula(BaseFormula):
    """Strain formula: epsilon = DeltaL / L.

    Calculates engineering strain given elongation and original length.

        STRAIN formula

    Example:
        >>> formula = StrainFormula()
        >>> formula.build("0.5", "100")
        '0.5/100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="STRAIN",
            category="mechanical_engineering",
            description="Calculate engineering strain: epsilon = DeltaL / L",
            arguments=(
                FormulaArgument(
                    name="elongation",
                    type="number",
                    required=True,
                    description="Change in length (DeltaL) in mm",
                ),
                FormulaArgument(
                    name="original_length",
                    type="number",
                    required=True,
                    description="Original length (L) in mm",
                ),
            ),
            return_type="number",
            examples=(
                "=STRAIN(0.5; 100)  # 0.005 strain",
                "=STRAIN(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: elongation, original_length

        Returns:
            ODF formula string: elongation/original_length
        """
        self.validate_arguments(args)
        elongation, original_length = args
        return f"of:={elongation}/{original_length}"


@dataclass(slots=True, frozen=True)
class YoungsModulusFormula(BaseFormula):
    """Young's Modulus formula: E = sigma / epsilon.

    Calculates Young's modulus (elastic modulus) from stress and strain.

        YOUNGS_MODULUS formula

    Example:
        >>> formula = YoungsModulusFormula()
        >>> formula.build("200", "0.001")
        '200/0.001'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="YOUNGS_MODULUS",
            category="mechanical_engineering",
            description="Calculate Young's modulus (elastic modulus): E = sigma / epsilon",
            arguments=(
                FormulaArgument(
                    name="stress",
                    type="number",
                    required=True,
                    description="Normal stress (sigma) in MPa",
                ),
                FormulaArgument(
                    name="strain",
                    type="number",
                    required=True,
                    description="Engineering strain (epsilon) dimensionless",
                ),
            ),
            return_type="number",
            examples=(
                "=YOUNGS_MODULUS(200; 0.001)  # 200000 MPa = 200 GPa",
                "=YOUNGS_MODULUS(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: stress, strain

        Returns:
            ODF formula string: stress/strain
        """
        self.validate_arguments(args)
        stress, strain = args
        return f"of:={stress}/{strain}"


__all__ = [
    "StrainFormula",
    "StressFormula",
    "YoungsModulusFormula",
]
