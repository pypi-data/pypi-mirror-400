"""Classical mechanics formulas for physics.

Physics classical mechanics formulas (7 formulas)
BATCH-5: Physics domain creation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class NewtonSecondLawFormula(BaseFormula):
    """Calculate force using Newton's second law.

        NEWTON_SECOND_LAW formula (F = ma)
        BATCH-5: Physics mechanics

    Example:
        >>> formula = NewtonSecondLawFormula()
        >>> result = formula.build("10", "2")
        >>> # Returns: "of:=10*2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for NEWTON_SECOND_LAW
        """
        return FormulaMetadata(
            name="NEWTON_SECOND_LAW",
            category="mechanics",
            description="Calculate force using Newton's second law (F = ma)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (kg)",
                ),
                FormulaArgument(
                    "acceleration",
                    "number",
                    required=True,
                    description="Acceleration (m/s²)",
                ),
            ),
            return_type="number",
            examples=(
                "=NEWTON_SECOND_LAW(10;2)",
                "=NEWTON_SECOND_LAW(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build NEWTON_SECOND_LAW formula string.

        Args:
            *args: mass, acceleration
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mass = args[0]
        acceleration = args[1]

        # F = ma
        return f"of:={mass}*{acceleration}"


@dataclass(slots=True, frozen=True)
class KineticEnergyFormula(BaseFormula):
    """Calculate kinetic energy.

        KINETIC_ENERGY formula (KE = 0.5*m*v²)
        BATCH-5: Physics mechanics

    Example:
        >>> formula = KineticEnergyFormula()
        >>> result = formula.build("10", "5")
        >>> # Returns: "of:=0.5*10*5^2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for KINETIC_ENERGY
        """
        return FormulaMetadata(
            name="KINETIC_ENERGY",
            category="mechanics",
            description="Calculate kinetic energy (KE = 0.5*m*v²)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (kg)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Velocity (m/s)",
                ),
            ),
            return_type="number",
            examples=(
                "=KINETIC_ENERGY(10;5)",
                "=KINETIC_ENERGY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build KINETIC_ENERGY formula string.

        Args:
            *args: mass, velocity
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mass = args[0]
        velocity = args[1]

        # KE = 0.5*m*v²
        return f"of:=0.5*{mass}*{velocity}^2"


@dataclass(slots=True, frozen=True)
class PotentialEnergyFormula(BaseFormula):
    """Calculate gravitational potential energy.

        POTENTIAL_ENERGY formula (PE = mgh)
        BATCH-5: Physics mechanics

    Example:
        >>> formula = PotentialEnergyFormula()
        >>> result = formula.build("10", "5")
        >>> # Returns: "of:=10*9.81*5"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for POTENTIAL_ENERGY
        """
        return FormulaMetadata(
            name="POTENTIAL_ENERGY",
            category="mechanics",
            description="Calculate gravitational potential energy (PE = mgh)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (kg)",
                ),
                FormulaArgument(
                    "height",
                    "number",
                    required=True,
                    description="Height (m)",
                ),
                FormulaArgument(
                    "gravity",
                    "number",
                    required=False,
                    description="Gravitational acceleration (m/s²)",
                    default=9.81,
                ),
            ),
            return_type="number",
            examples=(
                "=POTENTIAL_ENERGY(10;5)",
                "=POTENTIAL_ENERGY(A1;B1;9.81)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build POTENTIAL_ENERGY formula string.

        Args:
            *args: mass, height, [gravity]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mass = args[0]
        height = args[1]
        gravity = args[2] if len(args) > 2 else 9.81

        # PE = mgh
        return f"of:={mass}*{gravity}*{height}"


@dataclass(slots=True, frozen=True)
class WorkEnergyFormula(BaseFormula):
    """Calculate work done by a force.

        WORK_ENERGY formula (W = F*d*cos(θ))
        BATCH-5: Physics mechanics

    Example:
        >>> formula = WorkEnergyFormula()
        >>> result = formula.build("100", "5", "0")
        >>> # Returns: "of:=100*5*COS(RADIANS(0))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WORK_ENERGY
        """
        return FormulaMetadata(
            name="WORK_ENERGY",
            category="mechanics",
            description="Calculate work done by force (W = F*d*cos(θ))",
            arguments=(
                FormulaArgument(
                    "force",
                    "number",
                    required=True,
                    description="Force (N)",
                ),
                FormulaArgument(
                    "distance",
                    "number",
                    required=True,
                    description="Distance (m)",
                ),
                FormulaArgument(
                    "angle",
                    "number",
                    required=False,
                    description="Angle between force and displacement (degrees)",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=WORK_ENERGY(100;5;0)",
                "=WORK_ENERGY(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WORK_ENERGY formula string.

        Args:
            *args: force, distance, [angle]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        force = args[0]
        distance = args[1]
        angle = args[2] if len(args) > 2 else 0

        # W = F*d*cos(θ)
        return f"of:={force}*{distance}*COS(RADIANS({angle}))"


@dataclass(slots=True, frozen=True)
class MomentumFormula(BaseFormula):
    """Calculate linear momentum.

        MOMENTUM formula (p = mv)
        BATCH-5: Physics mechanics

    Example:
        >>> formula = MomentumFormula()
        >>> result = formula.build("10", "5")
        >>> # Returns: "of:=10*5"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MOMENTUM
        """
        return FormulaMetadata(
            name="MOMENTUM",
            category="mechanics",
            description="Calculate linear momentum (p = mv)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (kg)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Velocity (m/s)",
                ),
            ),
            return_type="number",
            examples=(
                "=MOMENTUM(10;5)",
                "=MOMENTUM(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MOMENTUM formula string.

        Args:
            *args: mass, velocity
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mass = args[0]
        velocity = args[1]

        # p = mv
        return f"of:={mass}*{velocity}"


@dataclass(slots=True, frozen=True)
class AngularMomentumFormula(BaseFormula):
    """Calculate angular momentum.

        ANGULAR_MOMENTUM formula (L = Iω)
        BATCH-5: Physics mechanics

    Example:
        >>> formula = AngularMomentumFormula()
        >>> result = formula.build("5", "10")
        >>> # Returns: "of:=5*10"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ANGULAR_MOMENTUM
        """
        return FormulaMetadata(
            name="ANGULAR_MOMENTUM",
            category="mechanics",
            description="Calculate angular momentum (L = Iω)",
            arguments=(
                FormulaArgument(
                    "moment_inertia",
                    "number",
                    required=True,
                    description="Moment of inertia (kg·m²)",
                ),
                FormulaArgument(
                    "angular_velocity",
                    "number",
                    required=True,
                    description="Angular velocity (rad/s)",
                ),
            ),
            return_type="number",
            examples=(
                "=ANGULAR_MOMENTUM(5;10)",
                "=ANGULAR_MOMENTUM(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ANGULAR_MOMENTUM formula string.

        Args:
            *args: moment_inertia, angular_velocity
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        moment_inertia = args[0]
        angular_velocity = args[1]

        # L = Iω
        return f"of:={moment_inertia}*{angular_velocity}"


@dataclass(slots=True, frozen=True)
class CentripetalForceFormula(BaseFormula):
    """Calculate centripetal force.

        CENTRIPETAL_FORCE formula (Fc = mv²/r)
        BATCH-5: Physics mechanics

    Example:
        >>> formula = CentripetalForceFormula()
        >>> result = formula.build("10", "5", "2")
        >>> # Returns: "of:=10*5^2/2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CENTRIPETAL_FORCE
        """
        return FormulaMetadata(
            name="CENTRIPETAL_FORCE",
            category="mechanics",
            description="Calculate centripetal force (Fc = mv²/r)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (kg)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Velocity (m/s)",
                ),
                FormulaArgument(
                    "radius",
                    "number",
                    required=True,
                    description="Radius (m)",
                ),
            ),
            return_type="number",
            examples=(
                "=CENTRIPETAL_FORCE(10;5;2)",
                "=CENTRIPETAL_FORCE(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CENTRIPETAL_FORCE formula string.

        Args:
            *args: mass, velocity, radius
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mass = args[0]
        velocity = args[1]
        radius = args[2]

        # Fc = mv²/r
        return f"of:={mass}*{velocity}^2/{radius}"


__all__ = [
    "AngularMomentumFormula",
    "CentripetalForceFormula",
    "KineticEnergyFormula",
    "MomentumFormula",
    "NewtonSecondLawFormula",
    "PotentialEnergyFormula",
    "WorkEnergyFormula",
]
