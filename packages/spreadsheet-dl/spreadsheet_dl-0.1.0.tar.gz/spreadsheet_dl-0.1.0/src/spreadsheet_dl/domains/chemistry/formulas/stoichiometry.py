"""Stoichiometry formulas for chemistry.

Chemistry stoichiometry formulas (10 formulas)
BATCH-4.2: Chemistry domain expansion
"""

# ruff: noqa: RUF001, RUF003
# Mathematical symbols (×) are intentional scientific notation

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class MolarMassFormula(BaseFormula):
    """Calculate molar mass from mass and moles.

    MOLAR_MASS formula for molecular weight
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="MOLAR_MASS",
            category="stoichiometry",
            description="Calculate molar mass (M = m/n)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (g)",
                ),
                FormulaArgument(
                    "moles",
                    "number",
                    required=True,
                    description="Number of moles",
                ),
            ),
            return_type="number",
            examples=(
                "=MOLAR_MASS(58.44;1)",
                "=MOLAR_MASS(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MOLAR_MASS formula string."""
        self.validate_arguments(args)

        mass = args[0]
        moles = args[1]

        return f"of:={mass}/{moles}"


@dataclass(slots=True, frozen=True)
class MassFromMolesFormula(BaseFormula):
    """Calculate mass from moles and molar mass.

    MASS_FROM_MOLES formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="MASS_FROM_MOLES",
            category="stoichiometry",
            description="Calculate mass (m = n × M)",
            arguments=(
                FormulaArgument(
                    "moles",
                    "number",
                    required=True,
                    description="Number of moles",
                ),
                FormulaArgument(
                    "molar_mass",
                    "number",
                    required=True,
                    description="Molar mass (g/mol)",
                ),
            ),
            return_type="number",
            examples=(
                "=MASS_FROM_MOLES(2;18.015)",
                "=MASS_FROM_MOLES(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MASS_FROM_MOLES formula string."""
        self.validate_arguments(args)

        moles = args[0]
        molar_mass = args[1]

        return f"of:={moles}*{molar_mass}"


@dataclass(slots=True, frozen=True)
class MolesFromMassFormula(BaseFormula):
    """Calculate moles from mass and molar mass.

    MOLES_FROM_MASS formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="MOLES_FROM_MASS",
            category="stoichiometry",
            description="Calculate moles (n = m/M)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (g)",
                ),
                FormulaArgument(
                    "molar_mass",
                    "number",
                    required=True,
                    description="Molar mass (g/mol)",
                ),
            ),
            return_type="number",
            examples=(
                "=MOLES_FROM_MASS(36.03;18.015)",
                "=MOLES_FROM_MASS(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MOLES_FROM_MASS formula string."""
        self.validate_arguments(args)

        mass = args[0]
        molar_mass = args[1]

        return f"of:={mass}/{molar_mass}"


@dataclass(slots=True, frozen=True)
class LimitingReagentFormula(BaseFormula):
    """Calculate limiting reagent comparison.

    LIMITING_REAGENT formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LIMITING_REAGENT",
            category="stoichiometry",
            description="Compare reagent ratios to find limiting (moles_A/coef_A vs moles_B/coef_B)",
            arguments=(
                FormulaArgument(
                    "moles_a",
                    "number",
                    required=True,
                    description="Moles of reagent A",
                ),
                FormulaArgument(
                    "coef_a",
                    "number",
                    required=True,
                    description="Stoichiometric coefficient of A",
                ),
                FormulaArgument(
                    "moles_b",
                    "number",
                    required=True,
                    description="Moles of reagent B",
                ),
                FormulaArgument(
                    "coef_b",
                    "number",
                    required=True,
                    description="Stoichiometric coefficient of B",
                ),
            ),
            return_type="number",
            examples=(
                '=LIMITING_REAGENT(2;1;3;2) -> returns "A" or "B"',
                "=LIMITING_REAGENT(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LIMITING_REAGENT formula string."""
        self.validate_arguments(args)

        moles_a = args[0]
        coef_a = args[1]
        moles_b = args[2]
        coef_b = args[3]

        # Returns the smaller ratio (limiting reagent ratio)
        return f'of:=IF({moles_a}/{coef_a}<{moles_b}/{coef_b},"A","B")'


@dataclass(slots=True, frozen=True)
class TheoreticalYieldFormula(BaseFormula):
    """Calculate theoretical yield from limiting reagent.

    THEORETICAL_YIELD formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="THEORETICAL_YIELD",
            category="stoichiometry",
            description="Calculate theoretical yield (moles_limiting × ratio × M_product)",
            arguments=(
                FormulaArgument(
                    "moles_limiting",
                    "number",
                    required=True,
                    description="Moles of limiting reagent",
                ),
                FormulaArgument(
                    "stoich_ratio",
                    "number",
                    required=True,
                    description="Stoichiometric ratio (product/limiting)",
                ),
                FormulaArgument(
                    "product_molar_mass",
                    "number",
                    required=True,
                    description="Molar mass of product (g/mol)",
                ),
            ),
            return_type="number",
            examples=(
                "=THEORETICAL_YIELD(2;1;18.015)",
                "=THEORETICAL_YIELD(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build THEORETICAL_YIELD formula string."""
        self.validate_arguments(args)

        moles_limiting = args[0]
        stoich_ratio = args[1]
        product_molar_mass = args[2]

        return f"of:={moles_limiting}*{stoich_ratio}*{product_molar_mass}"


@dataclass(slots=True, frozen=True)
class PercentYieldFormula(BaseFormula):
    """Calculate percent yield.

    PERCENT_YIELD formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="PERCENT_YIELD",
            category="stoichiometry",
            description="Calculate percent yield (actual/theoretical × 100)",
            arguments=(
                FormulaArgument(
                    "actual_yield",
                    "number",
                    required=True,
                    description="Actual yield obtained (g)",
                ),
                FormulaArgument(
                    "theoretical_yield",
                    "number",
                    required=True,
                    description="Theoretical yield (g)",
                ),
            ),
            return_type="number",
            examples=(
                "=PERCENT_YIELD(85;100)",
                "=PERCENT_YIELD(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PERCENT_YIELD formula string."""
        self.validate_arguments(args)

        actual_yield = args[0]
        theoretical_yield = args[1]

        return f"of:=({actual_yield}/{theoretical_yield})*100"


@dataclass(slots=True, frozen=True)
class PercentCompositionFormula(BaseFormula):
    """Calculate percent composition of element in compound.

    PERCENT_COMPOSITION formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="PERCENT_COMPOSITION",
            category="stoichiometry",
            description="Calculate percent composition ((n × atomic_mass)/molar_mass × 100)",
            arguments=(
                FormulaArgument(
                    "n_atoms",
                    "number",
                    required=True,
                    description="Number of atoms in formula",
                ),
                FormulaArgument(
                    "atomic_mass",
                    "number",
                    required=True,
                    description="Atomic mass of element (g/mol)",
                ),
                FormulaArgument(
                    "compound_molar_mass",
                    "number",
                    required=True,
                    description="Molar mass of compound (g/mol)",
                ),
            ),
            return_type="number",
            examples=(
                "=PERCENT_COMPOSITION(2;1.008;18.015)",
                "=PERCENT_COMPOSITION(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PERCENT_COMPOSITION formula string."""
        self.validate_arguments(args)

        n_atoms = args[0]
        atomic_mass = args[1]
        compound_molar_mass = args[2]

        return f"of:=({n_atoms}*{atomic_mass}/{compound_molar_mass})*100"


@dataclass(slots=True, frozen=True)
class EmpiricalFormulaRatioFormula(BaseFormula):
    """Calculate mole ratio for empirical formula.

    EMPIRICAL_FORMULA_RATIO formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="EMPIRICAL_FORMULA_RATIO",
            category="stoichiometry",
            description="Calculate mole ratio (mass/atomic_mass)/smallest_moles",
            arguments=(
                FormulaArgument(
                    "element_mass",
                    "number",
                    required=True,
                    description="Mass of element (g)",
                ),
                FormulaArgument(
                    "atomic_mass",
                    "number",
                    required=True,
                    description="Atomic mass (g/mol)",
                ),
                FormulaArgument(
                    "smallest_moles",
                    "number",
                    required=True,
                    description="Smallest mole value among elements",
                ),
            ),
            return_type="number",
            examples=(
                "=EMPIRICAL_FORMULA_RATIO(40;12;0.833)",
                "=EMPIRICAL_FORMULA_RATIO(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build EMPIRICAL_FORMULA_RATIO formula string."""
        self.validate_arguments(args)

        element_mass = args[0]
        atomic_mass = args[1]
        smallest_moles = args[2]

        return f"of:=({element_mass}/{atomic_mass})/{smallest_moles}"


@dataclass(slots=True, frozen=True)
class DilutionFormula(BaseFormula):
    """Calculate dilution using M1V1 = M2V2.

    DILUTION formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="DILUTION",
            category="stoichiometry",
            description="Calculate dilution M2 = M1V1/V2",
            arguments=(
                FormulaArgument(
                    "initial_concentration",
                    "number",
                    required=True,
                    description="Initial concentration M1 (M)",
                ),
                FormulaArgument(
                    "initial_volume",
                    "number",
                    required=True,
                    description="Initial volume V1 (L)",
                ),
                FormulaArgument(
                    "final_volume",
                    "number",
                    required=True,
                    description="Final volume V2 (L)",
                ),
            ),
            return_type="number",
            examples=(
                "=DILUTION(6;0.1;1)",
                "=DILUTION(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DILUTION formula string."""
        self.validate_arguments(args)

        initial_concentration = args[0]
        initial_volume = args[1]
        final_volume = args[2]

        return f"of:={initial_concentration}*{initial_volume}/{final_volume}"


@dataclass(slots=True, frozen=True)
class AvogadroParticlesFormula(BaseFormula):
    """Calculate number of particles using Avogadro's number.

    AVOGADRO_PARTICLES formula
    BATCH-4.2: Chemistry stoichiometry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="AVOGADRO_PARTICLES",
            category="stoichiometry",
            description="Calculate particles (N = n × NA)",
            arguments=(
                FormulaArgument(
                    "moles",
                    "number",
                    required=True,
                    description="Number of moles",
                ),
                FormulaArgument(
                    "avogadro",
                    "number",
                    required=False,
                    description="Avogadro's number",
                    default=6.022e23,
                ),
            ),
            return_type="number",
            examples=(
                "=AVOGADRO_PARTICLES(2)",
                "=AVOGADRO_PARTICLES(A1;6.022E23)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build AVOGADRO_PARTICLES formula string."""
        self.validate_arguments(args)

        moles = args[0]
        avogadro = args[1] if len(args) > 1 else "6.022E23"

        return f"of:={moles}*{avogadro}"


__all__ = [
    "AvogadroParticlesFormula",
    "DilutionFormula",
    "EmpiricalFormulaRatioFormula",
    "LimitingReagentFormula",
    "MassFromMolesFormula",
    "MolarMassFormula",
    "MolesFromMassFormula",
    "PercentCompositionFormula",
    "PercentYieldFormula",
    "TheoreticalYieldFormula",
]
