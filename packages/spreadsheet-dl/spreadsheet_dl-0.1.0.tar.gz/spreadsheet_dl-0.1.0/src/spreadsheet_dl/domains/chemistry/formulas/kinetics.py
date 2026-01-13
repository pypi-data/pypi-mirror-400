"""Chemical kinetics formulas.

Chemistry kinetics formulas (5 formulas)
BATCH-4: Chemistry domain creation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class RateConstantFormula(BaseFormula):
    """Calculate rate constant using Arrhenius equation.

        RATE_CONSTANT formula for reaction kinetics
        BATCH-4: Chemistry kinetics

    Example:
        >>> formula = RateConstantFormula()
        >>> result = formula.build("1e13", "50", "298")
        >>> # Returns: "of:=1e13*EXP(-50/(8.314*298))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RATE_CONSTANT
        """
        return FormulaMetadata(
            name="RATE_CONSTANT",
            category="kinetics",
            description="Calculate rate constant using Arrhenius equation (k = Ae^(-Ea/RT))",
            arguments=(
                FormulaArgument(
                    "pre_exponential",
                    "number",
                    required=True,
                    description="Pre-exponential factor A",
                ),
                FormulaArgument(
                    "activation_energy",
                    "number",
                    required=True,
                    description="Activation energy Ea (kJ/mol)",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
                FormulaArgument(
                    "gas_constant",
                    "number",
                    required=False,
                    description="Gas constant (kJ/(mol·K))",
                    default=8.314,
                ),
            ),
            return_type="number",
            examples=(
                "=RATE_CONSTANT(1E13;50;298)",
                "=RATE_CONSTANT(A1;B1;C1;8.314)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RATE_CONSTANT formula string.

        Args:
            *args: pre_exponential, activation_energy, temperature, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        pre_exponential = args[0]
        activation_energy = args[1]
        temperature = args[2]
        gas_constant = args[3] if len(args) > 3 else 8.314

        # k = A * exp(-Ea/RT)
        return f"of:={pre_exponential}*EXP(-{activation_energy}/({gas_constant}*{temperature}))"


@dataclass(slots=True, frozen=True)
class HalfLifeFirstOrderFormula(BaseFormula):
    """Calculate half-life for first-order reaction.

        HALF_LIFE_FIRST_ORDER formula for decay
        BATCH-4: Chemistry kinetics

    Example:
        >>> formula = HalfLifeFirstOrderFormula()
        >>> result = formula.build("0.0693")
        >>> # Returns: "of:=LN(2)/0.0693"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for HALF_LIFE_FIRST_ORDER
        """
        return FormulaMetadata(
            name="HALF_LIFE_FIRST_ORDER",
            category="kinetics",
            description="Calculate half-life for first-order reaction (t½ = ln(2)/k)",
            arguments=(
                FormulaArgument(
                    "rate_constant",
                    "number",
                    required=True,
                    description="Rate constant k (1/time)",
                ),
            ),
            return_type="number",
            examples=(
                "=HALF_LIFE_FIRST_ORDER(0.0693)",
                "=HALF_LIFE_FIRST_ORDER(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build HALF_LIFE_FIRST_ORDER formula string.

        Args:
            *args: rate_constant
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rate_constant = args[0]

        return f"of:=LN(2)/{rate_constant}"


@dataclass(slots=True, frozen=True)
class HalfLifeSecondOrderFormula(BaseFormula):
    """Calculate half-life for second-order reaction.

        HALF_LIFE_SECOND_ORDER formula for reaction kinetics
        BATCH-4: Chemistry kinetics

    Example:
        >>> formula = HalfLifeSecondOrderFormula()
        >>> result = formula.build("0.1", "2")
        >>> # Returns: "of:=1/(0.1*2)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for HALF_LIFE_SECOND_ORDER
        """
        return FormulaMetadata(
            name="HALF_LIFE_SECOND_ORDER",
            category="kinetics",
            description="Calculate half-life for second-order reaction (t½ = 1/(k[A]₀))",
            arguments=(
                FormulaArgument(
                    "rate_constant",
                    "number",
                    required=True,
                    description="Rate constant k (1/(M·time))",
                ),
                FormulaArgument(
                    "initial_concentration",
                    "number",
                    required=True,
                    description="Initial concentration [A]₀ (M)",
                ),
            ),
            return_type="number",
            examples=(
                "=HALF_LIFE_SECOND_ORDER(0.1;2)",
                "=HALF_LIFE_SECOND_ORDER(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build HALF_LIFE_SECOND_ORDER formula string.

        Args:
            *args: rate_constant, initial_concentration
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rate_constant = args[0]
        initial_concentration = args[1]

        return f"of:=1/({rate_constant}*{initial_concentration})"


@dataclass(slots=True, frozen=True)
class IntegratedRateLawFormula(BaseFormula):
    """Calculate concentration vs time using integrated rate law.

        INTEGRATED_RATE_LAW formula for concentration changes
        BATCH-4: Chemistry kinetics

    Example:
        >>> formula = IntegratedRateLawFormula()
        >>> result = formula.build("2", "0.1", "10", "1")
        >>> # Returns: "of:=2*EXP(-0.1*10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for INTEGRATED_RATE_LAW
        """
        return FormulaMetadata(
            name="INTEGRATED_RATE_LAW",
            category="kinetics",
            description="Calculate concentration vs time (first-order: [A]=[A]₀e^(-kt))",
            arguments=(
                FormulaArgument(
                    "initial_conc",
                    "number",
                    required=True,
                    description="Initial concentration [A]₀ (M)",
                ),
                FormulaArgument(
                    "rate_constant",
                    "number",
                    required=True,
                    description="Rate constant k",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time (same units as k⁻¹)",
                ),
                FormulaArgument(
                    "order",
                    "number",
                    required=False,
                    description="Reaction order (1 or 2)",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=INTEGRATED_RATE_LAW(2;0.1;10;1)",
                "=INTEGRATED_RATE_LAW(2;0.1;10;2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build INTEGRATED_RATE_LAW formula string.

        Args:
            *args: initial_conc, rate_constant, time, [order]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        initial_conc = args[0]
        rate_constant = args[1]
        time = args[2]
        order = args[3] if len(args) > 3 else 1

        # First order: [A] = [A]₀ * exp(-kt)
        # Second order: [A] = [A]₀ / (1 + k[A]₀t)
        # Use IF to select based on order
        return (
            f"of:=IF({order}=1,"
            f"{initial_conc}*EXP(-{rate_constant}*{time}),"
            f"{initial_conc}/(1+{rate_constant}*{initial_conc}*{time}))"
        )


@dataclass(slots=True, frozen=True)
class ActivationEnergyFormula(BaseFormula):
    """Calculate activation energy from Arrhenius equation.

        ACTIVATION_ENERGY formula for energy barrier
        BATCH-4: Chemistry kinetics

    Example:
        >>> formula = ActivationEnergyFormula()
        >>> result = formula.build("0.01", "0.05", "298", "323")
        >>> # Returns: "of:=8.314*LN(0.05/0.01)/(1/298-1/323)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ACTIVATION_ENERGY
        """
        return FormulaMetadata(
            name="ACTIVATION_ENERGY",
            category="kinetics",
            description="Calculate activation energy from rate constants at two temperatures",
            arguments=(
                FormulaArgument(
                    "k1",
                    "number",
                    required=True,
                    description="Rate constant at T1",
                ),
                FormulaArgument(
                    "k2",
                    "number",
                    required=True,
                    description="Rate constant at T2",
                ),
                FormulaArgument(
                    "t1",
                    "number",
                    required=True,
                    description="Temperature 1 (K)",
                ),
                FormulaArgument(
                    "t2",
                    "number",
                    required=True,
                    description="Temperature 2 (K)",
                ),
                FormulaArgument(
                    "gas_constant",
                    "number",
                    required=False,
                    description="Gas constant (kJ/(mol·K))",
                    default=8.314,
                ),
            ),
            return_type="number",
            examples=(
                "=ACTIVATION_ENERGY(0.01;0.05;298;323)",
                "=ACTIVATION_ENERGY(A1;B1;C1;D1;8.314)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ACTIVATION_ENERGY formula string.

        Args:
            *args: k1, k2, t1, t2, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        k1 = args[0]
        k2 = args[1]
        t1 = args[2]
        t2 = args[3]
        gas_constant = args[4] if len(args) > 4 else 8.314

        # Ea = R * ln(k2/k1) / (1/T1 - 1/T2)
        return f"of:={gas_constant}*LN({k2}/{k1})/(1/{t1}-1/{t2})"


__all__ = [
    "ActivationEnergyFormula",
    "HalfLifeFirstOrderFormula",
    "HalfLifeSecondOrderFormula",
    "IntegratedRateLawFormula",
    "RateConstantFormula",
]
