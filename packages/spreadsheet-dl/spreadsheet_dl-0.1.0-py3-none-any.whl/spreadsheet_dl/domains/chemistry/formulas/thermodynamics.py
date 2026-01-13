"""Thermodynamics formulas for chemistry.

Chemistry thermodynamics formulas (8 formulas)
BATCH-4: Chemistry domain creation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class GibbsFreeEnergyFormula(BaseFormula):
    """Calculate Gibbs free energy change.

        GIBBS_FREE_ENERGY formula for spontaneity prediction
        BATCH-4: Chemistry thermodynamics

    Example:
        >>> formula = GibbsFreeEnergyFormula()
        >>> result = formula.build("100", "298", "0.5")
        >>> # Returns: "of:=100-298*0.5"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GIBBS_FREE_ENERGY
        """
        return FormulaMetadata(
            name="GIBBS_FREE_ENERGY",
            category="thermodynamics",
            description="Calculate Gibbs free energy change (ΔG = ΔH - TΔS)",
            arguments=(
                FormulaArgument(
                    "enthalpy",
                    "number",
                    required=True,
                    description="Enthalpy change (kJ/mol)",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
                FormulaArgument(
                    "entropy",
                    "number",
                    required=True,
                    description="Entropy change (kJ/(mol·K))",
                ),
            ),
            return_type="number",
            examples=(
                "=GIBBS_FREE_ENERGY(100;298;0.5)",
                "=GIBBS_FREE_ENERGY(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GIBBS_FREE_ENERGY formula string.

        Args:
            *args: enthalpy, temperature, entropy
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        enthalpy = args[0]
        temperature = args[1]
        entropy = args[2]

        # ΔG = ΔH - TΔS
        return f"of:={enthalpy}-{temperature}*{entropy}"


@dataclass(slots=True, frozen=True)
class EnthalpyChangeFormula(BaseFormula):
    """Calculate enthalpy change for reaction.

        ENTHALPY_CHANGE formula for heat of reaction
        BATCH-4: Chemistry thermodynamics

    Example:
        >>> formula = EnthalpyChangeFormula()
        >>> result = formula.build("200", "150")
        >>> # Returns: "of:=200-150"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ENTHALPY_CHANGE
        """
        return FormulaMetadata(
            name="ENTHALPY_CHANGE",
            category="thermodynamics",
            description="Calculate enthalpy change (ΔH = H_products - H_reactants)",
            arguments=(
                FormulaArgument(
                    "products_enthalpy",
                    "number",
                    required=True,
                    description="Enthalpy of products (kJ/mol)",
                ),
                FormulaArgument(
                    "reactants_enthalpy",
                    "number",
                    required=True,
                    description="Enthalpy of reactants (kJ/mol)",
                ),
            ),
            return_type="number",
            examples=(
                "=ENTHALPY_CHANGE(200;150)",
                "=ENTHALPY_CHANGE(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ENTHALPY_CHANGE formula string.

        Args:
            *args: products_enthalpy, reactants_enthalpy
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        products_enthalpy = args[0]
        reactants_enthalpy = args[1]

        return f"of:={products_enthalpy}-{reactants_enthalpy}"


@dataclass(slots=True, frozen=True)
class ReactionEntropyChangeFormula(BaseFormula):
    """Calculate entropy change for chemical reaction.

        REACTION_ENTROPY_CHANGE formula for disorder change
        BATCH-4: Chemistry thermodynamics

    Example:
        >>> formula = ReactionEntropyChangeFormula()
        >>> result = formula.build("0.5", "0.3")
        >>> # Returns: "of:=0.5-0.3"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for REACTION_ENTROPY_CHANGE
        """
        return FormulaMetadata(
            name="REACTION_ENTROPY_CHANGE",
            category="thermodynamics",
            description="Calculate reaction entropy change (ΔS = S_products - S_reactants)",
            arguments=(
                FormulaArgument(
                    "products_entropy",
                    "number",
                    required=True,
                    description="Entropy of products (kJ/(mol·K))",
                ),
                FormulaArgument(
                    "reactants_entropy",
                    "number",
                    required=True,
                    description="Entropy of reactants (kJ/(mol·K))",
                ),
            ),
            return_type="number",
            examples=(
                "=ENTROPY_CHANGE(0.5;0.3)",
                "=ENTROPY_CHANGE(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ENTROPY_CHANGE formula string.

        Args:
            *args: products_entropy, reactants_entropy
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        products_entropy = args[0]
        reactants_entropy = args[1]

        return f"of:={products_entropy}-{reactants_entropy}"


@dataclass(slots=True, frozen=True)
class EquilibriumConstantFormula(BaseFormula):
    """Calculate equilibrium constant from Gibbs energy.

        EQUILIBRIUM_CONSTANT formula for reaction equilibrium
        BATCH-4: Chemistry thermodynamics

    Example:
        >>> formula = EquilibriumConstantFormula()
        >>> result = formula.build("-10", "298")
        >>> # Returns: "of:=EXP(-(-10)/(8.314*298))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for EQUILIBRIUM_CONSTANT
        """
        return FormulaMetadata(
            name="EQUILIBRIUM_CONSTANT",
            category="thermodynamics",
            description="Calculate equilibrium constant K (K = exp(-ΔG/RT))",
            arguments=(
                FormulaArgument(
                    "delta_g",
                    "number",
                    required=True,
                    description="Gibbs free energy change (kJ/mol)",
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
                "=EQUILIBRIUM_CONSTANT(-10;298)",
                "=EQUILIBRIUM_CONSTANT(A1;B1;8.314)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build EQUILIBRIUM_CONSTANT formula string.

        Args:
            *args: delta_g, temperature, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        delta_g = args[0]
        temperature = args[1]
        gas_constant = args[2] if len(args) > 2 else 8.314

        # K = exp(-ΔG/RT)
        return f"of:=EXP(-({delta_g})/({gas_constant}*{temperature}))"


@dataclass(slots=True, frozen=True)
class VantHoffEquationFormula(BaseFormula):
    """Calculate equilibrium constant at different temperature.

        VANT_HOFF_EQUATION formula for temperature dependence
        BATCH-4: Chemistry thermodynamics

    Example:
        >>> formula = VantHoffEquationFormula()
        >>> result = formula.build("1.5", "298", "323", "-50")
        >>> # Returns: "of:=1.5*EXP((-50/8.314)*(1/298-1/323))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for VANT_HOFF_EQUATION
        """
        return FormulaMetadata(
            name="VANT_HOFF_EQUATION",
            category="thermodynamics",
            description="Temperature dependence of equilibrium constant",
            arguments=(
                FormulaArgument(
                    "k1",
                    "number",
                    required=True,
                    description="Equilibrium constant at T1",
                ),
                FormulaArgument(
                    "t1",
                    "number",
                    required=True,
                    description="Initial temperature (K)",
                ),
                FormulaArgument(
                    "t2",
                    "number",
                    required=True,
                    description="Final temperature (K)",
                ),
                FormulaArgument(
                    "delta_h",
                    "number",
                    required=True,
                    description="Enthalpy change (kJ/mol)",
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
                "=VANT_HOFF_EQUATION(1.5;298;323;-50)",
                "=VANT_HOFF_EQUATION(A1;B1;C1;D1;8.314)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build VANT_HOFF_EQUATION formula string.

        Args:
            *args: k1, t1, t2, delta_h, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        k1 = args[0]
        t1 = args[1]
        t2 = args[2]
        delta_h = args[3]
        gas_constant = args[4] if len(args) > 4 else 8.314

        # K2 = K1 * exp((ΔH/R)*(1/T1 - 1/T2))
        return f"of:={k1}*EXP(({delta_h}/{gas_constant})*(1/{t1}-1/{t2}))"


@dataclass(slots=True, frozen=True)
class ClausiusClapeyronFormula(BaseFormula):
    """Calculate vapor pressure at temperature.

        CLAUSIUS_CLAPEYRON formula for vapor pressure
        BATCH-4: Chemistry thermodynamics

    Example:
        >>> formula = ClausiusClapeyronFormula()
        >>> result = formula.build("100", "373", "400", "40.7")
        >>> # Returns: "of:=100*EXP((40.7/8.314)*(1/373-1/400))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CLAUSIUS_CLAPEYRON
        """
        return FormulaMetadata(
            name="CLAUSIUS_CLAPEYRON",
            category="thermodynamics",
            description="Calculate vapor pressure at temperature",
            arguments=(
                FormulaArgument(
                    "p1",
                    "number",
                    required=True,
                    description="Vapor pressure at T1 (kPa)",
                ),
                FormulaArgument(
                    "t1",
                    "number",
                    required=True,
                    description="Initial temperature (K)",
                ),
                FormulaArgument(
                    "t2",
                    "number",
                    required=True,
                    description="Final temperature (K)",
                ),
                FormulaArgument(
                    "delta_hvap",
                    "number",
                    required=True,
                    description="Enthalpy of vaporization (kJ/mol)",
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
                "=CLAUSIUS_CLAPEYRON(100;373;400;40.7)",
                "=CLAUSIUS_CLAPEYRON(A1;B1;C1;D1;8.314)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CLAUSIUS_CLAPEYRON formula string.

        Args:
            *args: p1, t1, t2, delta_hvap, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        p1 = args[0]
        t1 = args[1]
        t2 = args[2]
        delta_hvap = args[3]
        gas_constant = args[4] if len(args) > 4 else 8.314

        # P2 = P1 * exp((ΔHvap/R)*(1/T1 - 1/T2))
        return f"of:={p1}*EXP(({delta_hvap}/{gas_constant})*(1/{t1}-1/{t2}))"


@dataclass(slots=True, frozen=True)
class GasIdealityCheckFormula(BaseFormula):
    """Verify ideal gas behavior by checking PV/(nRT) ratio.

        GAS_IDEALITY_CHECK formula - verifies PV=nRT holds
        BATCH-4: Chemistry thermodynamics

    Returns PV/(nRT) which should equal 1 for ideal gas behavior.

    Example:
        >>> formula = GasIdealityCheckFormula()
        >>> result = formula.build("2", "10", "1", "298")
        >>> # Returns: "of:=(2*10)/(1*0.0821*298)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GAS_IDEALITY_CHECK
        """
        return FormulaMetadata(
            name="GAS_IDEALITY_CHECK",
            category="thermodynamics",
            description="Check ideal gas behavior: PV/(nRT) = 1 for ideal gas",
            arguments=(
                FormulaArgument(
                    "pressure",
                    "number",
                    required=True,
                    description="Pressure (atm)",
                ),
                FormulaArgument(
                    "volume",
                    "number",
                    required=True,
                    description="Volume (L)",
                ),
                FormulaArgument(
                    "n_moles",
                    "number",
                    required=True,
                    description="Number of moles",
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
                    description="Gas constant (L·atm/(mol·K))",
                    default=0.0821,
                ),
            ),
            return_type="number",
            examples=(
                "=IDEAL_GAS_LAW(2;10;1;298)",
                "=IDEAL_GAS_LAW(A1;B1;C1;D1;0.0821)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build IDEAL_GAS_LAW formula string.

        Args:
            *args: pressure, volume, n_moles, temperature, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (returns ratio for verification)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        pressure = args[0]
        volume = args[1]
        n_moles = args[2]
        temperature = args[3]
        gas_constant = args[4] if len(args) > 4 else 0.0821

        # Returns PV/(nRT) = 1 for ideal gas
        return f"of:=({pressure}*{volume})/({n_moles}*{gas_constant}*{temperature})"


@dataclass(slots=True, frozen=True)
class RealGasVanDerWaalsFormula(BaseFormula):
    """Calculate Van der Waals equation for real gas.

        REAL_GAS_VAN_DER_WAALS formula for non-ideal behavior
        BATCH-4: Chemistry thermodynamics

    Example:
        >>> formula = RealGasVanDerWaalsFormula()
        >>> result = formula.build("10", "2", "1", "300", "1.36", "0.0318")
        >>> # Returns: "of:=(10+1.36*1^2/2^2)*(2-1*0.0318)/(1*0.0821*300)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for REAL_GAS_VAN_DER_WAALS
        """
        return FormulaMetadata(
            name="REAL_GAS_VAN_DER_WAALS",
            category="thermodynamics",
            description="Van der Waals equation for real gas behavior",
            arguments=(
                FormulaArgument(
                    "pressure",
                    "number",
                    required=True,
                    description="Pressure (atm)",
                ),
                FormulaArgument(
                    "volume",
                    "number",
                    required=True,
                    description="Volume (L)",
                ),
                FormulaArgument(
                    "n_moles",
                    "number",
                    required=True,
                    description="Number of moles",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
                FormulaArgument(
                    "a_const",
                    "number",
                    required=True,
                    description="Van der Waals constant a",
                ),
                FormulaArgument(
                    "b_const",
                    "number",
                    required=True,
                    description="Van der Waals constant b",
                ),
                FormulaArgument(
                    "gas_constant",
                    "number",
                    required=False,
                    description="Gas constant (L·atm/(mol·K))",
                    default=0.0821,
                ),
            ),
            return_type="number",
            examples=(
                "=REAL_GAS_VAN_DER_WAALS(10;2;1;300;1.36;0.0318)",
                "=REAL_GAS_VAN_DER_WAALS(A1;B1;C1;D1;E1;F1;0.0821)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build REAL_GAS_VAN_DER_WAALS formula string.

        Args:
            *args: pressure, volume, n_moles, temperature, a_const, b_const, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        pressure = args[0]
        volume = args[1]
        n_moles = args[2]
        temperature = args[3]
        a_const = args[4]
        b_const = args[5]
        gas_constant = args[6] if len(args) > 6 else 0.0821

        # (P + an²/V²)(V - nb) = nRT
        # Returns (P + an²/V²)(V - nb)/(nRT) = 1 for verification
        return (
            f"of:=({pressure}+{a_const}*{n_moles}^2/{volume}^2)*"
            f"({volume}-{n_moles}*{b_const})/({n_moles}*{gas_constant}*{temperature})"
        )


__all__ = [
    "ClausiusClapeyronFormula",
    "EnthalpyChangeFormula",
    "EquilibriumConstantFormula",
    "GasIdealityCheckFormula",
    "GibbsFreeEnergyFormula",
    "ReactionEntropyChangeFormula",
    "RealGasVanDerWaalsFormula",
    "VantHoffEquationFormula",
]
