"""Fatigue and safety formulas for mechanical engineering.

Fatigue formulas (FATIGUE_LIFE, SAFETY_FACTOR, STRESS_CONCENTRATION)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class FatigueLifeFormula(BaseFormula):
    """Fatigue Life formula (S-N curve): N = C / (Deltasigma)^m.

    Calculates number of cycles to failure given stress range and S-N curve parameters.

        FATIGUE_LIFE formula

    Example:
        >>> formula = FatigueLifeFormula()
        >>> formula.build("1e12", "100", "3")
        '1e12/POWER(100;3)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="FATIGUE_LIFE",
            category="mechanical_engineering",
            description="Calculate fatigue life using S-N curve: N = C / (Deltasigma)^m",
            arguments=(
                FormulaArgument(
                    name="constant_c",
                    type="number",
                    required=True,
                    description="Material constant C (from S-N curve)",
                ),
                FormulaArgument(
                    name="stress_range",
                    type="number",
                    required=True,
                    description="Stress range (Deltasigma) in MPa",
                ),
                FormulaArgument(
                    name="exponent_m",
                    type="number",
                    required=True,
                    description="Material exponent m (typically 3-5)",
                ),
            ),
            return_type="number",
            examples=(
                "=FATIGUE_LIFE(1E12; 100; 3)  # 1,000,000 cycles",
                "=FATIGUE_LIFE(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: constant_c, stress_range, exponent_m

        Returns:
            ODF formula string: constant_c/POWER(stress_range;exponent_m)
        """
        self.validate_arguments(args)
        constant_c, stress_range, exponent_m = args
        return f"of:={constant_c}/POWER({stress_range};{exponent_m})"


@dataclass(slots=True, frozen=True)
class SafetyFactorFormula(BaseFormula):
    """Safety Factor formula: SF = sigma_yield / sigma_applied.

    Calculates safety factor given yield strength and applied stress.

        SAFETY_FACTOR formula

    Example:
        >>> formula = SafetyFactorFormula()
        >>> formula.build("250", "100")
        '250/100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SAFETY_FACTOR",
            category="mechanical_engineering",
            description="Calculate safety factor: SF = sigma_yield / sigma_applied",
            arguments=(
                FormulaArgument(
                    name="yield_strength",
                    type="number",
                    required=True,
                    description="Material yield strength (sigma_yield) in MPa",
                ),
                FormulaArgument(
                    name="applied_stress",
                    type="number",
                    required=True,
                    description="Applied stress (sigma_applied) in MPa",
                ),
            ),
            return_type="number",
            examples=(
                "=SAFETY_FACTOR(250; 100)  # 2.5",
                "=SAFETY_FACTOR(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: yield_strength, applied_stress

        Returns:
            ODF formula string: yield_strength/applied_stress
        """
        self.validate_arguments(args)
        yield_strength, applied_stress = args
        return f"of:={yield_strength}/{applied_stress}"


@dataclass(slots=True, frozen=True)
class StressConcentrationFormula(BaseFormula):
    """Stress Concentration formula: sigma_max = K_t * sigma_nominal.

    Calculates maximum stress at a discontinuity given stress concentration factor
    and nominal stress.

        STRESS_CONCENTRATION formula

    Example:
        >>> formula = StressConcentrationFormula()
        >>> formula.build("3.0", "50")
        '3.0*50'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="STRESS_CONCENTRATION",
            category="mechanical_engineering",
            description="Calculate maximum stress at discontinuity: sigma_max = K_t * sigma_nominal",
            arguments=(
                FormulaArgument(
                    name="kt_factor",
                    type="number",
                    required=True,
                    description="Stress concentration factor (K_t) dimensionless",
                ),
                FormulaArgument(
                    name="nominal_stress",
                    type="number",
                    required=True,
                    description="Nominal stress (sigma_nominal) in MPa",
                ),
            ),
            return_type="number",
            examples=(
                "=STRESS_CONCENTRATION(3.0; 50)  # 150 MPa",
                "=STRESS_CONCENTRATION(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: kt_factor, nominal_stress

        Returns:
            ODF formula string: kt_factor*nominal_stress
        """
        self.validate_arguments(args)
        kt_factor, nominal_stress = args
        return f"of:={kt_factor}*{nominal_stress}"


__all__ = [
    "FatigueLifeFormula",
    "SafetyFactorFormula",
    "StressConcentrationFormula",
]
