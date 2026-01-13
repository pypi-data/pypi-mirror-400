"""Electromagnetism formulas for physics.

Physics electromagnetism formulas (6 formulas)
BATCH-5: Physics domain creation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class CoulombLawFormula(BaseFormula):
    """Calculate electrostatic force using Coulomb's law.

        COULOMB_LAW formula (F = k*q1*q2/r²)
        BATCH-5: Physics electromagnetism

    Example:
        >>> formula = CoulombLawFormula()
        >>> result = formula.build("1e-6", "2e-6", "0.1")
        >>> # Returns: "of:=8.99e9*1e-6*2e-6/0.1^2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for COULOMB_LAW
        """
        return FormulaMetadata(
            name="COULOMB_LAW",
            category="electromagnetism",
            description="Calculate electrostatic force (F = k*q1*q2/r²)",
            arguments=(
                FormulaArgument(
                    "charge1",
                    "number",
                    required=True,
                    description="First charge (C)",
                ),
                FormulaArgument(
                    "charge2",
                    "number",
                    required=True,
                    description="Second charge (C)",
                ),
                FormulaArgument(
                    "distance",
                    "number",
                    required=True,
                    description="Distance between charges (m)",
                ),
                FormulaArgument(
                    "k_constant",
                    "number",
                    required=False,
                    description="Coulomb constant (N·m²/C²)",
                    default=8.99e9,
                ),
            ),
            return_type="number",
            examples=(
                "=COULOMB_LAW(1e-6;2e-6;0.1)",
                "=COULOMB_LAW(A1;B1;C1;8.99e9)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build COULOMB_LAW formula string.

        Args:
            *args: charge1, charge2, distance, [k_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        charge1 = args[0]
        charge2 = args[1]
        distance = args[2]
        k_constant = args[3] if len(args) > 3 else 8.99e9

        # F = k*q1*q2/r²
        return f"of:={k_constant}*{charge1}*{charge2}/{distance}^2"


@dataclass(slots=True, frozen=True)
class ElectricFieldFormula(BaseFormula):
    """Calculate electric field strength.

        ELECTRIC_FIELD formula (E = F/q)
        BATCH-5: Physics electromagnetism

    Example:
        >>> formula = ElectricFieldFormula()
        >>> result = formula.build("100", "1e-6")
        >>> # Returns: "of:=100/1e-6"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ELECTRIC_FIELD
        """
        return FormulaMetadata(
            name="ELECTRIC_FIELD",
            category="electromagnetism",
            description="Calculate electric field strength (E = F/q)",
            arguments=(
                FormulaArgument(
                    "force",
                    "number",
                    required=True,
                    description="Force (N)",
                ),
                FormulaArgument(
                    "charge",
                    "number",
                    required=True,
                    description="Test charge (C)",
                ),
            ),
            return_type="number",
            examples=(
                "=ELECTRIC_FIELD(100;1e-6)",
                "=ELECTRIC_FIELD(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ELECTRIC_FIELD formula string.

        Args:
            *args: force, charge
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        force = args[0]
        charge = args[1]

        # E = F/q
        return f"of:={force}/{charge}"


@dataclass(slots=True, frozen=True)
class MagneticForceFormula(BaseFormula):
    """Calculate magnetic force on moving charge.

        MAGNETIC_FORCE formula (F = qvB*sin(θ))
        BATCH-5: Physics electromagnetism

    Example:
        >>> formula = MagneticForceFormula()
        >>> result = formula.build("1e-6", "1e6", "0.5", "90")
        >>> # Returns: "of:=1e-6*1e6*0.5*SIN(RADIANS(90))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MAGNETIC_FORCE
        """
        return FormulaMetadata(
            name="MAGNETIC_FORCE",
            category="electromagnetism",
            description="Calculate magnetic force (F = qvB*sin(θ))",
            arguments=(
                FormulaArgument(
                    "charge",
                    "number",
                    required=True,
                    description="Charge (C)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Velocity (m/s)",
                ),
                FormulaArgument(
                    "magnetic_field",
                    "number",
                    required=True,
                    description="Magnetic field strength (T)",
                ),
                FormulaArgument(
                    "angle",
                    "number",
                    required=False,
                    description="Angle between velocity and field (degrees)",
                    default=90,
                ),
            ),
            return_type="number",
            examples=(
                "=MAGNETIC_FORCE(1e-6;1e6;0.5;90)",
                "=MAGNETIC_FORCE(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MAGNETIC_FORCE formula string.

        Args:
            *args: charge, velocity, magnetic_field, [angle]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        charge = args[0]
        velocity = args[1]
        magnetic_field = args[2]
        angle = args[3] if len(args) > 3 else 90

        # F = qvB*sin(θ)
        return f"of:={charge}*{velocity}*{magnetic_field}*SIN(RADIANS({angle}))"


@dataclass(slots=True, frozen=True)
class FaradayLawFormula(BaseFormula):
    """Calculate induced EMF (simplified form).

        FARADAY_LAW formula (EMF = -N*ΔΦ/Δt, simplified)
        BATCH-5: Physics electromagnetism

    Example:
        >>> formula = FaradayLawFormula()
        >>> result = formula.build("100", "0.5", "0.1")
        >>> # Returns: "of:=100*0.5/0.1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for FARADAY_LAW
        """
        return FormulaMetadata(
            name="FARADAY_LAW",
            category="electromagnetism",
            description="Calculate induced EMF (EMF = N*ΔΦ/Δt)",
            arguments=(
                FormulaArgument(
                    "turns",
                    "number",
                    required=True,
                    description="Number of turns in coil",
                ),
                FormulaArgument(
                    "flux_change",
                    "number",
                    required=True,
                    description="Change in magnetic flux (Wb)",
                ),
                FormulaArgument(
                    "time_interval",
                    "number",
                    required=True,
                    description="Time interval (s)",
                ),
            ),
            return_type="number",
            examples=(
                "=FARADAY_LAW(100;0.5;0.1)",
                "=FARADAY_LAW(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build FARADAY_LAW formula string.

        Args:
            *args: turns, flux_change, time_interval
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        turns = args[0]
        flux_change = args[1]
        time_interval = args[2]

        # EMF = N*ΔΦ/Δt (magnitude)
        return f"of:={turns}*{flux_change}/{time_interval}"


@dataclass(slots=True, frozen=True)
class LorentzForceFormula(BaseFormula):
    """Calculate total Lorentz force.

        LORENTZ_FORCE formula (F = q*(E + v*B))
        BATCH-5: Physics electromagnetism

    Example:
        >>> formula = LorentzForceFormula()
        >>> result = formula.build("1e-6", "1000", "1e5", "0.5")
        >>> # Returns: "of:=1e-6*(1000+1e5*0.5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LORENTZ_FORCE
        """
        return FormulaMetadata(
            name="LORENTZ_FORCE",
            category="electromagnetism",
            description="Calculate Lorentz force (F = q*(E + v*B))",
            arguments=(
                FormulaArgument(
                    "charge",
                    "number",
                    required=True,
                    description="Charge (C)",
                ),
                FormulaArgument(
                    "electric_field",
                    "number",
                    required=True,
                    description="Electric field (N/C)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Velocity (m/s)",
                ),
                FormulaArgument(
                    "magnetic_field",
                    "number",
                    required=True,
                    description="Magnetic field (T)",
                ),
            ),
            return_type="number",
            examples=(
                "=LORENTZ_FORCE(1e-6;1000;1e5;0.5)",
                "=LORENTZ_FORCE(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LORENTZ_FORCE formula string.

        Args:
            *args: charge, electric_field, velocity, magnetic_field
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        charge = args[0]
        electric_field = args[1]
        velocity = args[2]
        magnetic_field = args[3]

        # F = q*(E + v*B) (simplified scalar form)
        return f"of:={charge}*({electric_field}+{velocity}*{magnetic_field})"


@dataclass(slots=True, frozen=True)
class PoyntingVectorFormula(BaseFormula):
    """Calculate electromagnetic power flow (Poynting vector magnitude).

        POYNTING_VECTOR formula (S = E*H)
        BATCH-5: Physics electromagnetism

    Example:
        >>> formula = PoyntingVectorFormula()
        >>> result = formula.build("100", "0.1")
        >>> # Returns: "of:=100*0.1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for POYNTING_VECTOR
        """
        return FormulaMetadata(
            name="POYNTING_VECTOR",
            category="electromagnetism",
            description="Calculate EM power flow (S = E*H)",
            arguments=(
                FormulaArgument(
                    "electric_field",
                    "number",
                    required=True,
                    description="Electric field amplitude (V/m)",
                ),
                FormulaArgument(
                    "magnetic_field",
                    "number",
                    required=True,
                    description="Magnetic field amplitude (A/m)",
                ),
            ),
            return_type="number",
            examples=(
                "=POYNTING_VECTOR(100;0.1)",
                "=POYNTING_VECTOR(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build POYNTING_VECTOR formula string.

        Args:
            *args: electric_field, magnetic_field
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        electric_field = args[0]
        magnetic_field = args[1]

        # S = E*H (magnitude)
        return f"of:={electric_field}*{magnetic_field}"


__all__ = [
    "CoulombLawFormula",
    "ElectricFieldFormula",
    "FaradayLawFormula",
    "LorentzForceFormula",
    "MagneticForceFormula",
    "PoyntingVectorFormula",
]
