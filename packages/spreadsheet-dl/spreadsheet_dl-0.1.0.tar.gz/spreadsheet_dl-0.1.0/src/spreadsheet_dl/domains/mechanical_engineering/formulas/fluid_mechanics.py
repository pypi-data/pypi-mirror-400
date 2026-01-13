"""Fluid mechanics formulas for mechanical engineering.

BATCH2-MECH: Fluid mechanics formulas (6 formulas)
- ReynoldsNumber: Flow regime determination
- BernoulliEquation: Total energy per unit volume
- DarcyWeisbach: Pressure drop in pipes
- PoiseuilleLaw: Viscous flow rate
- DragForce: Fluid resistance force
- LiftForce: Aerodynamic lift
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ReynoldsNumber(BaseFormula):
    """Reynolds Number formula: Re = v*L/nu.

    Calculates Reynolds number for flow regime determination.

        BATCH2-MECH: ReynoldsNumber formula

    Example:
        >>> formula = ReynoldsNumber()
        >>> formula.build("10", "0.1", "1e-6")
        'of:=10*0.1/1e-6'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="REYNOLDS_NUMBER",
            category="mechanical_engineering",
            description="Calculate Reynolds number for flow regime: Re = v*L/nu",
            arguments=(
                FormulaArgument(
                    name="velocity",
                    type="number",
                    required=True,
                    description="Flow velocity (m/s)",
                ),
                FormulaArgument(
                    name="characteristic_length",
                    type="number",
                    required=True,
                    description="Characteristic length (m)",
                ),
                FormulaArgument(
                    name="kinematic_viscosity",
                    type="number",
                    required=True,
                    description="Kinematic viscosity (m²/s)",
                ),
            ),
            return_type="number",
            examples=(
                "=REYNOLDS_NUMBER(10; 0.1; 1E-6)  # Re = 1,000,000",
                "=REYNOLDS_NUMBER(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: velocity, characteristic_length, kinematic_viscosity

        Returns:
            ODF formula string: of:=velocity*characteristic_length/kinematic_viscosity
        """
        self.validate_arguments(args)
        velocity, characteristic_length, kinematic_viscosity = args
        return f"of:={velocity}*{characteristic_length}/{kinematic_viscosity}"


@dataclass(slots=True, frozen=True)
class BernoulliEquation(BaseFormula):
    """Bernoulli Equation formula: E = P + 0.5*rho*v^2 + rho*g*h.

    Calculates total energy per unit volume in fluid flow.

        BATCH2-MECH: BernoulliEquation formula

    Example:
        >>> formula = BernoulliEquation()
        >>> formula.build("100000", "10", "5", "1000", "9.81")
        'of:=100000+0.5*1000*10^2+1000*9.81*5'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BERNOULLI_EQUATION",
            category="mechanical_engineering",
            description="Calculate total energy per unit volume: P + 0.5*rho*v^2 + rho*g*h",
            arguments=(
                FormulaArgument(
                    name="pressure",
                    type="number",
                    required=True,
                    description="Static pressure (Pa)",
                ),
                FormulaArgument(
                    name="velocity",
                    type="number",
                    required=True,
                    description="Flow velocity (m/s)",
                ),
                FormulaArgument(
                    name="height",
                    type="number",
                    required=True,
                    description="Elevation height (m)",
                ),
                FormulaArgument(
                    name="density",
                    type="number",
                    required=True,
                    description="Fluid density (kg/m³)",
                ),
                FormulaArgument(
                    name="gravity",
                    type="number",
                    required=True,
                    description="Gravitational acceleration (m/s²)",
                ),
            ),
            return_type="number",
            examples=(
                "=BERNOULLI_EQUATION(100000; 10; 5; 1000; 9.81)  # Total energy",
                "=BERNOULLI_EQUATION(A2; B2; C2; D2; E2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: pressure, velocity, height, density, gravity

        Returns:
            ODF formula string: of:=pressure+0.5*density*velocity^2+density*gravity*height
        """
        self.validate_arguments(args)
        pressure, velocity, height, density, gravity = args
        return f"of:={pressure}+0.5*{density}*{velocity}^2+{density}*{gravity}*{height}"


@dataclass(slots=True, frozen=True)
class DarcyWeisbach(BaseFormula):
    """Darcy-Weisbach formula: deltaP = f*(L/D)*0.5*rho*v^2.

    Calculates pressure drop in pipes due to friction.

        BATCH2-MECH: DarcyWeisbach formula

    Example:
        >>> formula = DarcyWeisbach()
        >>> formula.build("0.02", "100", "0.1", "5", "1000")
        'of:=0.02*(100/0.1)*(0.5*1000*5^2)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="DARCY_WEISBACH",
            category="mechanical_engineering",
            description="Calculate pressure drop in pipes: f*(L/D)*0.5*rho*v^2",
            arguments=(
                FormulaArgument(
                    name="friction_factor",
                    type="number",
                    required=True,
                    description="Darcy friction factor (dimensionless)",
                ),
                FormulaArgument(
                    name="length",
                    type="number",
                    required=True,
                    description="Pipe length (m)",
                ),
                FormulaArgument(
                    name="diameter",
                    type="number",
                    required=True,
                    description="Pipe diameter (m)",
                ),
                FormulaArgument(
                    name="velocity",
                    type="number",
                    required=True,
                    description="Flow velocity (m/s)",
                ),
                FormulaArgument(
                    name="density",
                    type="number",
                    required=True,
                    description="Fluid density (kg/m³)",
                ),
            ),
            return_type="number",
            examples=(
                "=DARCY_WEISBACH(0.02; 100; 0.1; 5; 1000)  # Pressure drop in Pa",
                "=DARCY_WEISBACH(A2; B2; C2; D2; E2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: friction_factor, length, diameter, velocity, density

        Returns:
            ODF formula string: of:=friction_factor*(length/diameter)*(0.5*density*velocity^2)
        """
        self.validate_arguments(args)
        friction_factor, length, diameter, velocity, density = args
        return (
            f"of:={friction_factor}*({length}/{diameter})*(0.5*{density}*{velocity}^2)"
        )


@dataclass(slots=True, frozen=True)
class PoiseuilleLaw(BaseFormula):
    """Poiseuille's Law formula: Q = (pi*r^4*deltaP)/(8*mu*L).

    Calculates viscous flow rate in pipes.

        BATCH2-MECH: PoiseuilleLaw formula

    Example:
        >>> formula = PoiseuilleLaw()
        >>> formula.build("1000", "0.01", "1", "0.001")
        'of:=(PI()*0.01^4*1000)/(8*0.001*1)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="POISEUILLE_LAW",
            category="mechanical_engineering",
            description="Calculate viscous flow rate: (pi*r^4*deltaP)/(8*mu*L)",
            arguments=(
                FormulaArgument(
                    name="pressure_drop",
                    type="number",
                    required=True,
                    description="Pressure drop (Pa)",
                ),
                FormulaArgument(
                    name="radius",
                    type="number",
                    required=True,
                    description="Pipe radius (m)",
                ),
                FormulaArgument(
                    name="length",
                    type="number",
                    required=True,
                    description="Pipe length (m)",
                ),
                FormulaArgument(
                    name="viscosity",
                    type="number",
                    required=True,
                    description="Dynamic viscosity (Pa·s)",
                ),
            ),
            return_type="number",
            examples=(
                "=POISEUILLE_LAW(1000; 0.01; 1; 0.001)  # Flow rate m³/s",
                "=POISEUILLE_LAW(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: pressure_drop, radius, length, viscosity

        Returns:
            ODF formula string: of:=(PI()*radius^4*pressure_drop)/(8*viscosity*length)
        """
        self.validate_arguments(args)
        pressure_drop, radius, length, viscosity = args
        return f"of:=(PI()*{radius}^4*{pressure_drop})/(8*{viscosity}*{length})"


@dataclass(slots=True, frozen=True)
class DragForce(BaseFormula):
    """Drag Force formula: F_D = 0.5*C_D*rho*v^2*A.

    Calculates fluid resistance force on a body.

        BATCH2-MECH: DragForce formula

    Example:
        >>> formula = DragForce()
        >>> formula.build("0.5", "1.2", "30", "2.5")
        'of:=0.5*0.5*1.2*30^2*2.5'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="DRAG_FORCE",
            category="mechanical_engineering",
            description="Calculate fluid resistance force: 0.5*C_D*rho*v^2*A",
            arguments=(
                FormulaArgument(
                    name="drag_coeff",
                    type="number",
                    required=True,
                    description="Drag coefficient (dimensionless)",
                ),
                FormulaArgument(
                    name="density",
                    type="number",
                    required=True,
                    description="Fluid density (kg/m³)",
                ),
                FormulaArgument(
                    name="velocity",
                    type="number",
                    required=True,
                    description="Flow velocity (m/s)",
                ),
                FormulaArgument(
                    name="area",
                    type="number",
                    required=True,
                    description="Reference area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=DRAG_FORCE(0.5; 1.2; 30; 2.5)  # Drag force in N",
                "=DRAG_FORCE(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: drag_coeff, density, velocity, area

        Returns:
            ODF formula string: of:=0.5*drag_coeff*density*velocity^2*area
        """
        self.validate_arguments(args)
        drag_coeff, density, velocity, area = args
        return f"of:=0.5*{drag_coeff}*{density}*{velocity}^2*{area}"


@dataclass(slots=True, frozen=True)
class LiftForce(BaseFormula):
    """Lift Force formula: F_L = 0.5*C_L*rho*v^2*A.

    Calculates aerodynamic lift force on a body.

        BATCH2-MECH: LiftForce formula

    Example:
        >>> formula = LiftForce()
        >>> formula.build("1.2", "1.2", "50", "15")
        'of:=0.5*1.2*1.2*50^2*15'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LIFT_FORCE",
            category="mechanical_engineering",
            description="Calculate aerodynamic lift force: 0.5*C_L*rho*v^2*A",
            arguments=(
                FormulaArgument(
                    name="lift_coeff",
                    type="number",
                    required=True,
                    description="Lift coefficient (dimensionless)",
                ),
                FormulaArgument(
                    name="density",
                    type="number",
                    required=True,
                    description="Fluid density (kg/m³)",
                ),
                FormulaArgument(
                    name="velocity",
                    type="number",
                    required=True,
                    description="Flow velocity (m/s)",
                ),
                FormulaArgument(
                    name="area",
                    type="number",
                    required=True,
                    description="Wing/reference area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=LIFT_FORCE(1.2; 1.2; 50; 15)  # Lift force in N",
                "=LIFT_FORCE(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: lift_coeff, density, velocity, area

        Returns:
            ODF formula string: of:=0.5*lift_coeff*density*velocity^2*area
        """
        self.validate_arguments(args)
        lift_coeff, density, velocity, area = args
        return f"of:=0.5*{lift_coeff}*{density}*{velocity}^2*{area}"


__all__ = [
    "BernoulliEquation",
    "DarcyWeisbach",
    "DragForce",
    "LiftForce",
    "PoiseuilleLaw",
    "ReynoldsNumber",
]
