"""Electrochemistry formulas for chemistry.

Chemistry electrochemistry formulas (10 formulas)
BATCH-4.2: Chemistry domain expansion
"""

# ruff: noqa: RUF001, RUF003
# Greek letters (α, ρ, etc.) and mathematical symbols (×) are intentional scientific notation

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class NernstEquationFormula(BaseFormula):
    """Calculate cell potential using Nernst equation.

        NERNST_EQUATION formula for electrochemistry
        BATCH-4.2: Chemistry electrochemistry

    Example:
        >>> formula = NernstEquationFormula()
        >>> result = formula.build("0.76", "2", "0.1", "1", "298")
        >>> # Returns: "of:=0.76-(0.0592/2)*LOG10(0.1/1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="NERNST_EQUATION",
            category="electrochemistry",
            description="Calculate cell potential (E = E° - (RT/nF)ln(Q))",
            arguments=(
                FormulaArgument(
                    "standard_potential",
                    "number",
                    required=True,
                    description="Standard cell potential E° (V)",
                ),
                FormulaArgument(
                    "n_electrons",
                    "number",
                    required=True,
                    description="Number of electrons transferred",
                ),
                FormulaArgument(
                    "products_activity",
                    "number",
                    required=True,
                    description="Activity of products",
                ),
                FormulaArgument(
                    "reactants_activity",
                    "number",
                    required=True,
                    description="Activity of reactants",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=False,
                    description="Temperature (K)",
                    default=298,
                ),
            ),
            return_type="number",
            examples=(
                "=NERNST_EQUATION(0.76;2;0.1;1;298)",
                "=NERNST_EQUATION(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build NERNST_EQUATION formula string."""
        self.validate_arguments(args)

        standard_potential = args[0]
        n_electrons = args[1]
        products_activity = args[2]
        reactants_activity = args[3]
        temperature = args[4] if len(args) > 4 else 298

        # E = E° - (0.0592/n)*log(Q) at 298K, or (RT/nF)*ln(Q) general
        # Using simplified form with LOG10 at 298K
        return (
            f"of:={standard_potential}-(0.0592*{temperature}/298/{n_electrons})*"
            f"LOG10({products_activity}/{reactants_activity})"
        )


@dataclass(slots=True, frozen=True)
class FaradayElectrolysisFormula(BaseFormula):
    """Calculate mass deposited in electrolysis using Faraday's law.

    FARADAY_ELECTROLYSIS formula for mass calculation
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="FARADAY_ELECTROLYSIS",
            category="electrochemistry",
            description="Calculate mass deposited (m = ItM/nF)",
            arguments=(
                FormulaArgument(
                    "current",
                    "number",
                    required=True,
                    description="Current (A)",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time (s)",
                ),
                FormulaArgument(
                    "molar_mass",
                    "number",
                    required=True,
                    description="Molar mass (g/mol)",
                ),
                FormulaArgument(
                    "n_electrons",
                    "number",
                    required=True,
                    description="Electrons per ion",
                ),
                FormulaArgument(
                    "faraday_const",
                    "number",
                    required=False,
                    description="Faraday constant (C/mol)",
                    default=96485,
                ),
            ),
            return_type="number",
            examples=(
                "=FARADAY_ELECTROLYSIS(2;3600;63.5;2)",
                "=FARADAY_ELECTROLYSIS(A1;B1;C1;D1;96485)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build FARADAY_ELECTROLYSIS formula string."""
        self.validate_arguments(args)

        current = args[0]
        time = args[1]
        molar_mass = args[2]
        n_electrons = args[3]
        faraday_const = args[4] if len(args) > 4 else 96485

        # m = ItM/(nF)
        return f"of:={current}*{time}*{molar_mass}/({n_electrons}*{faraday_const})"


@dataclass(slots=True, frozen=True)
class StandardCellPotentialFormula(BaseFormula):
    """Calculate standard cell potential from half-reactions.

    STANDARD_CELL_POTENTIAL formula
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="STANDARD_CELL_POTENTIAL",
            category="electrochemistry",
            description="Calculate E°cell = E°cathode - E°anode",
            arguments=(
                FormulaArgument(
                    "cathode_potential",
                    "number",
                    required=True,
                    description="Standard reduction potential of cathode (V)",
                ),
                FormulaArgument(
                    "anode_potential",
                    "number",
                    required=True,
                    description="Standard reduction potential of anode (V)",
                ),
            ),
            return_type="number",
            examples=(
                "=STANDARD_CELL_POTENTIAL(0.34;-0.76)",
                "=STANDARD_CELL_POTENTIAL(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build STANDARD_CELL_POTENTIAL formula string."""
        self.validate_arguments(args)

        cathode_potential = args[0]
        anode_potential = args[1]

        return f"of:={cathode_potential}-{anode_potential}"


@dataclass(slots=True, frozen=True)
class GibbsElectrochemicalFormula(BaseFormula):
    """Calculate Gibbs free energy from cell potential.

    GIBBS_ELECTROCHEMICAL formula
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="GIBBS_ELECTROCHEMICAL",
            category="electrochemistry",
            description="Calculate ΔG = -nFE",
            arguments=(
                FormulaArgument(
                    "n_electrons",
                    "number",
                    required=True,
                    description="Number of electrons transferred",
                ),
                FormulaArgument(
                    "cell_potential",
                    "number",
                    required=True,
                    description="Cell potential (V)",
                ),
                FormulaArgument(
                    "faraday_const",
                    "number",
                    required=False,
                    description="Faraday constant (C/mol)",
                    default=96485,
                ),
            ),
            return_type="number",
            examples=(
                "=GIBBS_ELECTROCHEMICAL(2;1.1)",
                "=GIBBS_ELECTROCHEMICAL(A1;B1;96485)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GIBBS_ELECTROCHEMICAL formula string."""
        self.validate_arguments(args)

        n_electrons = args[0]
        cell_potential = args[1]
        faraday_const = args[2] if len(args) > 2 else 96485

        # ΔG = -nFE (in J/mol, divide by 1000 for kJ/mol)
        return f"of:=-{n_electrons}*{faraday_const}*{cell_potential}/1000"


@dataclass(slots=True, frozen=True)
class EquilibriumConstantElectroFormula(BaseFormula):
    """Calculate equilibrium constant from cell potential.

    EQUILIBRIUM_CONSTANT_ELECTRO formula
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="EQUILIBRIUM_CONSTANT_ELECTRO",
            category="electrochemistry",
            description="Calculate K from E° (ln(K) = nFE°/RT)",
            arguments=(
                FormulaArgument(
                    "n_electrons",
                    "number",
                    required=True,
                    description="Number of electrons transferred",
                ),
                FormulaArgument(
                    "cell_potential",
                    "number",
                    required=True,
                    description="Standard cell potential E° (V)",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=False,
                    description="Temperature (K)",
                    default=298,
                ),
            ),
            return_type="number",
            examples=(
                "=EQUILIBRIUM_CONSTANT_ELECTRO(2;1.1)",
                "=EQUILIBRIUM_CONSTANT_ELECTRO(A1;B1;298)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build EQUILIBRIUM_CONSTANT_ELECTRO formula string."""
        self.validate_arguments(args)

        n_electrons = args[0]
        cell_potential = args[1]
        temperature = args[2] if len(args) > 2 else 298

        # K = exp(nFE°/RT), F=96485, R=8.314
        return f"of:=EXP({n_electrons}*96485*{cell_potential}/(8.314*{temperature}))"


@dataclass(slots=True, frozen=True)
class OhmicResistanceFormula(BaseFormula):
    """Calculate ohmic resistance loss in electrochemical cell.

    OHMIC_RESISTANCE formula
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="OHMIC_RESISTANCE",
            category="electrochemistry",
            description="Calculate IR drop (V = IR)",
            arguments=(
                FormulaArgument(
                    "current",
                    "number",
                    required=True,
                    description="Current (A)",
                ),
                FormulaArgument(
                    "resistance",
                    "number",
                    required=True,
                    description="Resistance (Ω)",
                ),
            ),
            return_type="number",
            examples=(
                "=OHMIC_RESISTANCE(0.5;10)",
                "=OHMIC_RESISTANCE(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OHMIC_RESISTANCE formula string."""
        self.validate_arguments(args)

        current = args[0]
        resistance = args[1]

        return f"of:={current}*{resistance}"


@dataclass(slots=True, frozen=True)
class OverpotentialFormula(BaseFormula):
    """Calculate overpotential in electrochemical process.

    OVERPOTENTIAL formula
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="OVERPOTENTIAL",
            category="electrochemistry",
            description="Calculate η = E_applied - E_equilibrium",
            arguments=(
                FormulaArgument(
                    "applied_potential",
                    "number",
                    required=True,
                    description="Applied potential (V)",
                ),
                FormulaArgument(
                    "equilibrium_potential",
                    "number",
                    required=True,
                    description="Equilibrium potential (V)",
                ),
            ),
            return_type="number",
            examples=(
                "=OVERPOTENTIAL(1.5;1.23)",
                "=OVERPOTENTIAL(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OVERPOTENTIAL formula string."""
        self.validate_arguments(args)

        applied_potential = args[0]
        equilibrium_potential = args[1]

        return f"of:={applied_potential}-{equilibrium_potential}"


@dataclass(slots=True, frozen=True)
class TafelEquationFormula(BaseFormula):
    """Calculate current density using Tafel equation.

    TAFEL_EQUATION formula for electrode kinetics
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="TAFEL_EQUATION",
            category="electrochemistry",
            description="Calculate η = a + b*log(i) (Tafel equation)",
            arguments=(
                FormulaArgument(
                    "exchange_current",
                    "number",
                    required=True,
                    description="Exchange current density i₀ (A/cm²)",
                ),
                FormulaArgument(
                    "current_density",
                    "number",
                    required=True,
                    description="Current density i (A/cm²)",
                ),
                FormulaArgument(
                    "tafel_slope",
                    "number",
                    required=True,
                    description="Tafel slope b (V/decade)",
                ),
            ),
            return_type="number",
            examples=(
                "=TAFEL_EQUATION(1E-6;0.01;0.12)",
                "=TAFEL_EQUATION(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TAFEL_EQUATION formula string."""
        self.validate_arguments(args)

        exchange_current = args[0]
        current_density = args[1]
        tafel_slope = args[2]

        # η = b * log(i/i₀)
        return f"of:={tafel_slope}*LOG10({current_density}/{exchange_current})"


@dataclass(slots=True, frozen=True)
class ButlerVolmerFormula(BaseFormula):
    """Calculate current using Butler-Volmer equation.

    BUTLER_VOLMER formula for electrode kinetics
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BUTLER_VOLMER",
            category="electrochemistry",
            description="Butler-Volmer equation for electrode kinetics",
            arguments=(
                FormulaArgument(
                    "exchange_current",
                    "number",
                    required=True,
                    description="Exchange current density i₀",
                ),
                FormulaArgument(
                    "overpotential",
                    "number",
                    required=True,
                    description="Overpotential η (V)",
                ),
                FormulaArgument(
                    "alpha",
                    "number",
                    required=False,
                    description="Transfer coefficient α",
                    default=0.5,
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=False,
                    description="Temperature (K)",
                    default=298,
                ),
            ),
            return_type="number",
            examples=(
                "=BUTLER_VOLMER(1E-6;0.1;0.5;298)",
                "=BUTLER_VOLMER(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BUTLER_VOLMER formula string."""
        self.validate_arguments(args)

        exchange_current = args[0]
        overpotential = args[1]
        alpha = args[2] if len(args) > 2 else 0.5
        temperature = args[3] if len(args) > 3 else 298

        # i = i₀ * [exp(αFη/RT) - exp(-(1-α)Fη/RT)]
        # F/R = 96485/8.314 = 11605
        f_over_r = 11605
        return (
            f"of:={exchange_current}*("
            f"EXP({alpha}*{f_over_r}*{overpotential}/{temperature})-"
            f"EXP(-(1-{alpha})*{f_over_r}*{overpotential}/{temperature}))"
        )


@dataclass(slots=True, frozen=True)
class ConductivityFormula(BaseFormula):
    """Calculate ionic conductivity.

    IONIC_CONDUCTIVITY formula
    BATCH-4.2: Chemistry electrochemistry
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="IONIC_CONDUCTIVITY",
            category="electrochemistry",
            description="Calculate conductivity κ = 1/(ρ*l/A)",
            arguments=(
                FormulaArgument(
                    "resistance",
                    "number",
                    required=True,
                    description="Measured resistance (Ω)",
                ),
                FormulaArgument(
                    "cell_constant",
                    "number",
                    required=True,
                    description="Cell constant (1/cm)",
                ),
            ),
            return_type="number",
            examples=(
                "=IONIC_CONDUCTIVITY(500;1.0)",
                "=IONIC_CONDUCTIVITY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build IONIC_CONDUCTIVITY formula string."""
        self.validate_arguments(args)

        resistance = args[0]
        cell_constant = args[1]

        # κ = cell_constant / R
        return f"of:={cell_constant}/{resistance}"


__all__ = [
    "ButlerVolmerFormula",
    "ConductivityFormula",
    "EquilibriumConstantElectroFormula",
    "FaradayElectrolysisFormula",
    "GibbsElectrochemicalFormula",
    "NernstEquationFormula",
    "OhmicResistanceFormula",
    "OverpotentialFormula",
    "StandardCellPotentialFormula",
    "TafelEquationFormula",
]
