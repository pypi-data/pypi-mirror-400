"""Biochemistry and protein formulas.

Biochemistry formulas
(BRADFORD_ASSAY, ENZYME_ACTIVITY, MICHAELIS_MENTEN, DILUTION_FACTOR)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class BradfordAssayFormula(BaseFormula):
    """Calculate protein concentration from Bradford assay.

        BRADFORD_ASSAY formula for protein quantification

    Example:
        >>> formula = BradfordAssayFormula()
        >>> result = formula.build("A1", "B1", "C1")
        >>> # Returns: "B1*A1+C1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BRADFORD_ASSAY

            Formula metadata
        """
        return FormulaMetadata(
            name="BRADFORD_ASSAY",
            category="biochemistry",
            description=(
                "Calculate protein concentration from Bradford assay absorbance"
            ),
            arguments=(
                FormulaArgument(
                    "absorbance",
                    "number",
                    required=True,
                    description="Absorbance at 595nm",
                ),
                FormulaArgument(
                    "slope",
                    "number",
                    required=True,
                    description="Standard curve slope",
                ),
                FormulaArgument(
                    "intercept",
                    "number",
                    required=True,
                    description="Standard curve intercept",
                ),
                FormulaArgument(
                    "dilution",
                    "number",
                    required=False,
                    description="Sample dilution factor",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=BRADFORD_ASSAY(A1;slope;intercept)",
                "=BRADFORD_ASSAY(A1;0.0015;0.02;10)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BRADFORD_ASSAY formula string.

        Args:
            *args: absorbance, slope, intercept, [dilution]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            BRADFORD_ASSAY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        absorbance = args[0]
        slope = args[1]
        intercept = args[2]
        dilution = args[3] if len(args) > 3 else 1

        # Concentration = (slope * absorbance + intercept) * dilution
        return f"of:=({slope}*{absorbance}+{intercept})*{dilution}"


@dataclass(slots=True, frozen=True)
class EnzymeActivityFormula(BaseFormula):
    """Calculate enzyme specific activity.

        ENZYME_ACTIVITY formula for enzyme kinetics

    Example:
        >>> formula = EnzymeActivityFormula()
        >>> result = formula.build("A1", "B1", "C1", "D1")
        >>> # Returns: "(A1*B1)/(C1*D1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ENZYME_ACTIVITY

            Formula metadata
        """
        return FormulaMetadata(
            name="ENZYME_ACTIVITY",
            category="biochemistry",
            description="Calculate enzyme specific activity (units/mg protein)",
            arguments=(
                FormulaArgument(
                    "delta_abs",
                    "number",
                    required=True,
                    description="Change in absorbance per minute",
                ),
                FormulaArgument(
                    "volume",
                    "number",
                    required=True,
                    description="Total reaction volume (mL)",
                ),
                FormulaArgument(
                    "protein_conc",
                    "number",
                    required=True,
                    description="Protein concentration (mg/mL)",
                ),
                FormulaArgument(
                    "extinction_coef",
                    "number",
                    required=False,
                    description="Extinction coefficient",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=ENZYME_ACTIVITY(A1;B1;C1;6220)",
                "=ENZYME_ACTIVITY(delta_abs;volume;protein;extinction)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ENZYME_ACTIVITY formula string.

        Args:
            *args: delta_abs, volume, protein_conc, [extinction_coef]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ENZYME_ACTIVITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        delta_abs = args[0]
        volume = args[1]
        protein_conc = args[2]
        extinction_coef = args[3] if len(args) > 3 else 1

        # Activity = (ΔA/min * total_volume) / (extinction_coef * protein_amount)
        # Simplified: (delta_abs * volume) / (extinction_coef * protein_conc)
        return f"of:=({delta_abs}*{volume})/({extinction_coef}*{protein_conc})"


@dataclass(slots=True, frozen=True)
class MichaelisMentenFormula(BaseFormula):
    """Calculate reaction velocity using Michaelis-Menten kinetics.

        MICHAELIS_MENTEN formula for enzyme kinetics

    Example:
        >>> formula = MichaelisMentenFormula()
        >>> result = formula.build("A1", "B1", "C1")
        >>> # Returns: "(B1*A1)/(C1+A1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MICHAELIS_MENTEN

            Formula metadata
        """
        return FormulaMetadata(
            name="MICHAELIS_MENTEN",
            category="biochemistry",
            description="Calculate reaction velocity using Michaelis-Menten equation",
            arguments=(
                FormulaArgument(
                    "substrate",
                    "number",
                    required=True,
                    description="Substrate concentration [S]",
                ),
                FormulaArgument(
                    "vmax",
                    "number",
                    required=True,
                    description="Maximum velocity Vmax",
                ),
                FormulaArgument(
                    "km",
                    "number",
                    required=True,
                    description="Michaelis constant Km",
                ),
            ),
            return_type="number",
            examples=(
                "=MICHAELIS_MENTEN(A1;vmax;km)",
                "=MICHAELIS_MENTEN(substrate;10;2.5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MICHAELIS_MENTEN formula string.

        Args:
            *args: substrate, vmax, km
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MICHAELIS_MENTEN formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        substrate = args[0]
        vmax = args[1]
        km = args[2]

        # V = (Vmax * [S]) / (Km + [S])
        return f"of:=({vmax}*{substrate})/({km}+{substrate})"


@dataclass(slots=True, frozen=True)
class DilutionFactorFormula(BaseFormula):
    """Calculate serial dilution factor.

        DILUTION_FACTOR formula for serial dilutions

    Example:
        >>> formula = DilutionFactorFormula()
        >>> result = formula.build(10, 3)
        >>> # Returns: "POWER(10;3)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DILUTION_FACTOR

            Formula metadata
        """
        return FormulaMetadata(
            name="DILUTION_FACTOR",
            category="biochemistry",
            description="Calculate total dilution factor for serial dilutions",
            arguments=(
                FormulaArgument(
                    "dilution_ratio",
                    "number",
                    required=True,
                    description="Dilution ratio per step (e.g., 10 for 1:10)",
                ),
                FormulaArgument(
                    "num_steps",
                    "number",
                    required=True,
                    description="Number of dilution steps",
                ),
            ),
            return_type="number",
            examples=(
                "=DILUTION_FACTOR(10;3)",
                "=DILUTION_FACTOR(2;5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DILUTION_FACTOR formula string.

        Args:
            *args: dilution_ratio, num_steps
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            DILUTION_FACTOR formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        dilution_ratio = args[0]
        num_steps = args[1]

        # Total dilution = ratio ^ steps
        return f"of:=POWER({dilution_ratio};{num_steps})"


__all__ = [
    "BradfordAssayFormula",
    "DilutionFactorFormula",
    "EnzymeActivityFormula",
    "MichaelisMentenFormula",
]
