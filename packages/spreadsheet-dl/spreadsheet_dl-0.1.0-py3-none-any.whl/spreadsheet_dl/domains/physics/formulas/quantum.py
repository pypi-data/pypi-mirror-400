"""Quantum mechanics formulas for physics.

Physics quantum mechanics formulas (6 formulas)
BATCH-5: Physics domain creation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class PlanckEnergyFormula(BaseFormula):
    """Calculate photon energy using Planck's equation.

        PLANCK_ENERGY formula (E = hf)
        BATCH-5: Physics quantum mechanics

    Example:
        >>> formula = PlanckEnergyFormula()
        >>> result = formula.build("5e14")
        >>> # Returns: "of:=6.626e-34*5e14"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PLANCK_ENERGY
        """
        return FormulaMetadata(
            name="PLANCK_ENERGY",
            category="quantum",
            description="Calculate photon energy (E = hf)",
            arguments=(
                FormulaArgument(
                    "frequency",
                    "number",
                    required=True,
                    description="Frequency (Hz)",
                ),
                FormulaArgument(
                    "planck_constant",
                    "number",
                    required=False,
                    description="Planck constant (J·s)",
                    default=6.626e-34,
                ),
            ),
            return_type="number",
            examples=(
                "=PLANCK_ENERGY(5e14)",
                "=PLANCK_ENERGY(A1;6.626e-34)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PLANCK_ENERGY formula string.

        Args:
            *args: frequency, [planck_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        frequency = args[0]
        planck_constant = args[1] if len(args) > 1 else 6.626e-34

        # E = hf
        return f"of:={planck_constant}*{frequency}"


@dataclass(slots=True, frozen=True)
class DeBroglieWavelengthFormula(BaseFormula):
    """Calculate de Broglie wavelength.

        DE_BROGLIE_WAVELENGTH formula (λ = h/p)
        BATCH-5: Physics quantum mechanics

    Example:
        >>> formula = DeBroglieWavelengthFormula()
        >>> result = formula.build("1e-24")
        >>> # Returns: "of:=6.626e-34/1e-24"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DE_BROGLIE_WAVELENGTH
        """
        return FormulaMetadata(
            name="DE_BROGLIE_WAVELENGTH",
            category="quantum",
            description="Calculate de Broglie wavelength (λ = h/p)",
            arguments=(
                FormulaArgument(
                    "momentum",
                    "number",
                    required=True,
                    description="Momentum (kg·m/s)",
                ),
                FormulaArgument(
                    "planck_constant",
                    "number",
                    required=False,
                    description="Planck constant (J·s)",
                    default=6.626e-34,
                ),
            ),
            return_type="number",
            examples=(
                "=DE_BROGLIE_WAVELENGTH(1e-24)",
                "=DE_BROGLIE_WAVELENGTH(A1;6.626e-34)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DE_BROGLIE_WAVELENGTH formula string.

        Args:
            *args: momentum, [planck_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        momentum = args[0]
        planck_constant = args[1] if len(args) > 1 else 6.626e-34

        # λ = h/p
        return f"of:={planck_constant}/{momentum}"


@dataclass(slots=True, frozen=True)
class HeisenbergUncertaintyFormula(BaseFormula):
    """Calculate Heisenberg uncertainty principle.

        HEISENBERG_UNCERTAINTY formula (Δx*Δp ≥ ℏ/2)
        BATCH-5: Physics quantum mechanics

    Example:
        >>> formula = HeisenbergUncertaintyFormula()
        >>> result = formula.build("1e-10")
        >>> # Returns: "of:=1.055e-34/(2*1e-10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for HEISENBERG_UNCERTAINTY
        """
        return FormulaMetadata(
            name="HEISENBERG_UNCERTAINTY",
            category="quantum",
            description="Calculate minimum uncertainty (Δp = ℏ/(2*Δx))",
            arguments=(
                FormulaArgument(
                    "position_uncertainty",
                    "number",
                    required=True,
                    description="Position uncertainty Δx (m)",
                ),
                FormulaArgument(
                    "hbar",
                    "number",
                    required=False,
                    description="Reduced Planck constant (J·s)",
                    default=1.055e-34,
                ),
            ),
            return_type="number",
            examples=(
                "=HEISENBERG_UNCERTAINTY(1e-10)",
                "=HEISENBERG_UNCERTAINTY(A1;1.055e-34)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build HEISENBERG_UNCERTAINTY formula string.

        Args:
            *args: position_uncertainty, [hbar]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns minimum momentum uncertainty)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        position_uncertainty = args[0]
        hbar = args[1] if len(args) > 1 else 1.055e-34

        # Δp = ℏ/(2*Δx)
        return f"of:={hbar}/(2*{position_uncertainty})"


@dataclass(slots=True, frozen=True)
class PhotoelectricEffectFormula(BaseFormula):
    """Calculate kinetic energy in photoelectric effect.

        PHOTOELECTRIC_EFFECT formula (KE = hf - W)
        BATCH-5: Physics quantum mechanics

    Example:
        >>> formula = PhotoelectricEffectFormula()
        >>> result = formula.build("5e14", "2e-19")
        >>> # Returns: "of:=6.626e-34*5e14-2e-19"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PHOTOELECTRIC_EFFECT
        """
        return FormulaMetadata(
            name="PHOTOELECTRIC_EFFECT",
            category="quantum",
            description="Calculate max kinetic energy (KE = hf - W)",
            arguments=(
                FormulaArgument(
                    "frequency",
                    "number",
                    required=True,
                    description="Photon frequency (Hz)",
                ),
                FormulaArgument(
                    "work_function",
                    "number",
                    required=True,
                    description="Work function (J)",
                ),
                FormulaArgument(
                    "planck_constant",
                    "number",
                    required=False,
                    description="Planck constant (J·s)",
                    default=6.626e-34,
                ),
            ),
            return_type="number",
            examples=(
                "=PHOTOELECTRIC_EFFECT(5e14;2e-19)",
                "=PHOTOELECTRIC_EFFECT(A1;B1;6.626e-34)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PHOTOELECTRIC_EFFECT formula string.

        Args:
            *args: frequency, work_function, [planck_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        frequency = args[0]
        work_function = args[1]
        planck_constant = args[2] if len(args) > 2 else 6.626e-34

        # KE = hf - W
        return f"of:={planck_constant}*{frequency}-{work_function}"


@dataclass(slots=True, frozen=True)
class BohrRadiusFormula(BaseFormula):
    """Calculate Bohr model atomic radius.

        BOHR_RADIUS formula (r_n = n²*a₀)
        BATCH-5: Physics quantum mechanics

    Example:
        >>> formula = BohrRadiusFormula()
        >>> result = formula.build("2")
        >>> # Returns: "of:=2^2*5.29e-11"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BOHR_RADIUS
        """
        return FormulaMetadata(
            name="BOHR_RADIUS",
            category="quantum",
            description="Calculate Bohr orbit radius (r_n = n²*a₀)",
            arguments=(
                FormulaArgument(
                    "quantum_number",
                    "number",
                    required=True,
                    description="Principal quantum number (n)",
                ),
                FormulaArgument(
                    "bohr_radius",
                    "number",
                    required=False,
                    description="Bohr radius constant (m)",
                    default=5.29e-11,
                ),
            ),
            return_type="number",
            examples=(
                "=BOHR_RADIUS(2)",
                "=BOHR_RADIUS(A1;5.29e-11)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BOHR_RADIUS formula string.

        Args:
            *args: quantum_number, [bohr_radius]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        quantum_number = args[0]
        bohr_radius = args[1] if len(args) > 1 else 5.29e-11

        # r_n = n²*a₀
        return f"of:={quantum_number}^2*{bohr_radius}"


@dataclass(slots=True, frozen=True)
class RydbergFormulaFormula(BaseFormula):
    """Calculate wavelength using Rydberg formula.

        RYDBERG_FORMULA (1/λ = R*(1/n₁² - 1/n₂²))
        BATCH-5: Physics quantum mechanics

    Example:
        >>> formula = RydbergFormulaFormula()
        >>> result = formula.build("1", "2")
        >>> # Returns: "of:=1/(1.097e7*(1/1^2-1/2^2))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RYDBERG_FORMULA
        """
        return FormulaMetadata(
            name="RYDBERG_FORMULA",
            category="quantum",
            description="Calculate wavelength (1/λ = R*(1/n₁² - 1/n₂²))",
            arguments=(
                FormulaArgument(
                    "n1",
                    "number",
                    required=True,
                    description="Lower energy level",
                ),
                FormulaArgument(
                    "n2",
                    "number",
                    required=True,
                    description="Higher energy level",
                ),
                FormulaArgument(
                    "rydberg_constant",
                    "number",
                    required=False,
                    description="Rydberg constant (m⁻¹)",
                    default=1.097e7,
                ),
            ),
            return_type="number",
            examples=(
                "=RYDBERG_FORMULA(1;2)",
                "=RYDBERG_FORMULA(A1;B1;1.097e7)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RYDBERG_FORMULA formula string.

        Args:
            *args: n1, n2, [rydberg_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns wavelength)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        n1 = args[0]
        n2 = args[1]
        rydberg_constant = args[2] if len(args) > 2 else 1.097e7

        # λ = 1/(R*(1/n₁² - 1/n₂²))
        return f"of:=1/({rydberg_constant}*(1/{n1}^2-1/{n2}^2))"


__all__ = [
    "BohrRadiusFormula",
    "DeBroglieWavelengthFormula",
    "HeisenbergUncertaintyFormula",
    "PhotoelectricEffectFormula",
    "PlanckEnergyFormula",
    "RydbergFormulaFormula",
]
