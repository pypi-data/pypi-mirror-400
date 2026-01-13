"""Dynamics and vibration formulas.

Mechanical engineering formulas for dynamics and vibration analysis
(NaturalFrequency, CriticalDamping, SpringConstant, AngularVelocity)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class NaturalFrequency(BaseFormula):
    """Calculate natural frequency of vibration.

        Natural frequency formula for mass-spring systems

    Example:
        >>> formula = NaturalFrequency()
        >>> result = formula.build("1000", "10")
        >>> # Returns: "of:=SQRT(1000/10)/(2*PI())"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for NaturalFrequency

            Formula metadata
        """
        return FormulaMetadata(
            name="NATURAL_FREQUENCY",
            category="dynamics",
            description="Calculate natural frequency of mass-spring system",
            arguments=(
                FormulaArgument(
                    "stiffness",
                    "number",
                    required=True,
                    description="Spring stiffness k (N/m)",
                ),
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass m (kg)",
                ),
            ),
            return_type="number",
            examples=(
                "=NATURAL_FREQUENCY(1000;10)",
                "=NATURAL_FREQUENCY(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build NaturalFrequency formula string.

        Args:
            *args: stiffness, mass
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            NaturalFrequency formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        stiffness = args[0]
        mass = args[1]

        # fn = (1/2π) * sqrt(k/m)
        return f"of:=SQRT({stiffness}/{mass})/(2*PI())"


@dataclass(slots=True, frozen=True)
class CriticalDamping(BaseFormula):
    """Calculate critical damping coefficient.

        Critical damping formula

    Example:
        >>> formula = CriticalDamping()
        >>> result = formula.build("1000", "10")
        >>> # Returns: "2*SQRT(1000*10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CriticalDamping

            Formula metadata
        """
        return FormulaMetadata(
            name="CRITICAL_DAMPING",
            category="dynamics",
            description="Calculate critical damping coefficient",
            arguments=(
                FormulaArgument(
                    "stiffness",
                    "number",
                    required=True,
                    description="Spring stiffness k (N/m)",
                ),
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass m (kg)",
                ),
            ),
            return_type="number",
            examples=(
                "=CRITICAL_DAMPING(1000;10)",
                "=CRITICAL_DAMPING(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CriticalDamping formula string.

        Args:
            *args: stiffness, mass
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CriticalDamping formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        stiffness = args[0]
        mass = args[1]

        # cc = 2 * sqrt(k*m)
        return f"of:=2*SQRT({stiffness}*{mass})"


@dataclass(slots=True, frozen=True)
class SpringConstant(BaseFormula):
    """Calculate spring constant from force and displacement.

        Hooke's law for spring constant

    Example:
        >>> formula = SpringConstant()
        >>> result = formula.build("500", "0.05")
        >>> # Returns: "500/0.05"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SpringConstant

            Formula metadata
        """
        return FormulaMetadata(
            name="SPRING_CONSTANT",
            category="dynamics",
            description="Calculate spring constant (k = F/x)",
            arguments=(
                FormulaArgument(
                    "force",
                    "number",
                    required=True,
                    description="Applied force F (N)",
                ),
                FormulaArgument(
                    "displacement",
                    "number",
                    required=True,
                    description="Displacement x (m)",
                ),
            ),
            return_type="number",
            examples=(
                "=SPRING_CONSTANT(500;0.05)",
                "=SPRING_CONSTANT(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SpringConstant formula string.

        Args:
            *args: force, displacement
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SpringConstant formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        force = args[0]
        displacement = args[1]

        # k = F / x
        return f"of:={force}/{displacement}"


@dataclass(slots=True, frozen=True)
class AngularVelocity(BaseFormula):
    """Calculate angular velocity from rotational speed.

        Angular velocity conversion from RPM

    Example:
        >>> formula = AngularVelocity()
        >>> result = formula.build("1200")
        >>> # Returns: "of:=1200*2*PI()/60"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for AngularVelocity

            Formula metadata
        """
        return FormulaMetadata(
            name="ANGULAR_VELOCITY",
            category="dynamics",
            description="Calculate angular velocity from RPM",
            arguments=(
                FormulaArgument(
                    "rpm",
                    "number",
                    required=True,
                    description="Rotational speed (RPM)",
                ),
            ),
            return_type="number",
            examples=(
                "=ANGULAR_VELOCITY(1200)",
                "=ANGULAR_VELOCITY(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build AngularVelocity formula string.

        Args:
            *args: rpm
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            AngularVelocity formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rpm = args[0]

        # ω = RPM * 2π / 60 (rad/s)
        return f"of:={rpm}*2*PI()/60"
