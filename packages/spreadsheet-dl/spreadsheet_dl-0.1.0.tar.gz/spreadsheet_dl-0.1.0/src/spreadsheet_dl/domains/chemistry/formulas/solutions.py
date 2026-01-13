"""Solutions chemistry formulas.

Chemistry solutions formulas (7 formulas)
BATCH-4: Chemistry domain creation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class MolarityFormula(BaseFormula):
    """Calculate molarity (moles per liter).

        MOLARITY formula for concentration
        BATCH-4: Chemistry solutions

    Example:
        >>> formula = MolarityFormula()
        >>> result = formula.build("2", "0.5")
        >>> # Returns: "of:=2/0.5"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MOLARITY
        """
        return FormulaMetadata(
            name="MOLARITY",
            category="solutions",
            description="Calculate molarity (M = moles/L)",
            arguments=(
                FormulaArgument(
                    "moles",
                    "number",
                    required=True,
                    description="Number of moles",
                ),
                FormulaArgument(
                    "volume_liters",
                    "number",
                    required=True,
                    description="Volume in liters",
                ),
            ),
            return_type="number",
            examples=(
                "=MOLARITY(2;0.5)",
                "=MOLARITY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MOLARITY formula string.

        Args:
            *args: moles, volume_liters
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        moles = args[0]
        volume_liters = args[1]

        return f"of:={moles}/{volume_liters}"


@dataclass(slots=True, frozen=True)
class MolalityFormula(BaseFormula):
    """Calculate molality (moles per kg solvent).

        MOLALITY formula for concentration
        BATCH-4: Chemistry solutions

    Example:
        >>> formula = MolalityFormula()
        >>> result = formula.build("1.5", "2")
        >>> # Returns: "of:=1.5/2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MOLALITY
        """
        return FormulaMetadata(
            name="MOLALITY",
            category="solutions",
            description="Calculate molality (m = moles/kg solvent)",
            arguments=(
                FormulaArgument(
                    "moles",
                    "number",
                    required=True,
                    description="Number of moles",
                ),
                FormulaArgument(
                    "mass_solvent_kg",
                    "number",
                    required=True,
                    description="Mass of solvent (kg)",
                ),
            ),
            return_type="number",
            examples=(
                "=MOLALITY(1.5;2)",
                "=MOLALITY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MOLALITY formula string.

        Args:
            *args: moles, mass_solvent_kg
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        moles = args[0]
        mass_solvent_kg = args[1]

        return f"of:={moles}/{mass_solvent_kg}"


@dataclass(slots=True, frozen=True)
class MoleFractionFormula(BaseFormula):
    """Calculate mole fraction.

        MOLE_FRACTION formula for component ratio
        BATCH-4: Chemistry solutions

    Example:
        >>> formula = MoleFractionFormula()
        >>> result = formula.build("3", "10")
        >>> # Returns: "of:=3/10"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MOLE_FRACTION
        """
        return FormulaMetadata(
            name="MOLE_FRACTION",
            category="solutions",
            description="Calculate mole fraction (χ = n_component/n_total)",
            arguments=(
                FormulaArgument(
                    "moles_component",
                    "number",
                    required=True,
                    description="Moles of component",
                ),
                FormulaArgument(
                    "moles_total",
                    "number",
                    required=True,
                    description="Total moles",
                ),
            ),
            return_type="number",
            examples=(
                "=MOLE_FRACTION(3;10)",
                "=MOLE_FRACTION(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MOLE_FRACTION formula string.

        Args:
            *args: moles_component, moles_total
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        moles_component = args[0]
        moles_total = args[1]

        return f"of:={moles_component}/{moles_total}"


@dataclass(slots=True, frozen=True)
class RaoultsLawFormula(BaseFormula):
    """Calculate vapor pressure lowering using Raoult's law.

        RAOULTS_LAW formula for vapor pressure
        BATCH-4: Chemistry solutions

    Example:
        >>> formula = RaoultsLawFormula()
        >>> result = formula.build("100", "0.8")
        >>> # Returns: "of:=100*0.8"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RAOULTS_LAW
        """
        return FormulaMetadata(
            name="RAOULTS_LAW",
            category="solutions",
            description="Calculate vapor pressure using Raoult's law (P = P°χ)",
            arguments=(
                FormulaArgument(
                    "vapor_pressure_pure",
                    "number",
                    required=True,
                    description="Vapor pressure of pure solvent (kPa)",
                ),
                FormulaArgument(
                    "mole_fraction_solvent",
                    "number",
                    required=True,
                    description="Mole fraction of solvent",
                ),
            ),
            return_type="number",
            examples=(
                "=RAOULTS_LAW(100;0.8)",
                "=RAOULTS_LAW(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RAOULTS_LAW formula string.

        Args:
            *args: vapor_pressure_pure, mole_fraction_solvent
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        vapor_pressure_pure = args[0]
        mole_fraction_solvent = args[1]

        return f"of:={vapor_pressure_pure}*{mole_fraction_solvent}"


@dataclass(slots=True, frozen=True)
class OsmoticPressureFormula(BaseFormula):
    """Calculate osmotic pressure.

        OSMOTIC_PRESSURE formula for colligative property
        BATCH-4: Chemistry solutions

    Example:
        >>> formula = OsmoticPressureFormula()
        >>> result = formula.build("1.5", "298")
        >>> # Returns: "of:=1.5*0.0821*298"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for OSMOTIC_PRESSURE
        """
        return FormulaMetadata(
            name="OSMOTIC_PRESSURE",
            category="solutions",
            description="Calculate osmotic pressure (π = MRT)",
            arguments=(
                FormulaArgument(
                    "molarity",
                    "number",
                    required=True,
                    description="Molarity (M)",
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
                "=OSMOTIC_PRESSURE(1.5;298)",
                "=OSMOTIC_PRESSURE(A1;B1;0.0821)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OSMOTIC_PRESSURE formula string.

        Args:
            *args: molarity, temperature, [gas_constant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        molarity = args[0]
        temperature = args[1]
        gas_constant = args[2] if len(args) > 2 else 0.0821

        # π = MRT
        return f"of:={molarity}*{gas_constant}*{temperature}"


@dataclass(slots=True, frozen=True)
class pHCalculationFormula(BaseFormula):
    """Calculate pH from H+ concentration.

        PH_CALCULATION formula for acidity measure
        BATCH-4: Chemistry solutions

    Example:
        >>> formula = pHCalculationFormula()
        >>> result = formula.build("0.001")
        >>> # Returns: "of:=-LOG10(0.001)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PH_CALCULATION
        """
        return FormulaMetadata(
            name="PH_CALCULATION",
            category="solutions",
            description="Calculate pH from H+ concentration (pH = -log[H+])",
            arguments=(
                FormulaArgument(
                    "h_concentration",
                    "number",
                    required=True,
                    description="H+ concentration (M)",
                ),
            ),
            return_type="number",
            examples=(
                "=PH_CALCULATION(0.001)",
                "=PH_CALCULATION(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PH_CALCULATION formula string.

        Args:
            *args: h_concentration
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        h_concentration = args[0]

        return f"of:=-LOG10({h_concentration})"


@dataclass(slots=True, frozen=True)
class BufferCapacityFormula(BaseFormula):
    """Calculate buffer capacity.

        BUFFER_CAPACITY formula for pH resistance
        BATCH-4: Chemistry solutions

    Example:
        >>> formula = BufferCapacityFormula()
        >>> result = formula.build("0.1", "1.8e-5", "4.74")
        >>> # Returns: "of:=2.303*0.1*1.8e-5*10^(-4.74)/(1.8e-5+10^(-4.74))^2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BUFFER_CAPACITY
        """
        return FormulaMetadata(
            name="BUFFER_CAPACITY",
            category="solutions",
            description="Calculate buffer capacity β",
            arguments=(
                FormulaArgument(
                    "buffer_conc",
                    "number",
                    required=True,
                    description="Buffer concentration (M)",
                ),
                FormulaArgument(
                    "ka",
                    "number",
                    required=True,
                    description="Acid dissociation constant Ka",
                ),
                FormulaArgument(
                    "pH",
                    "number",
                    required=True,
                    description="pH value",
                ),
            ),
            return_type="number",
            examples=(
                "=BUFFER_CAPACITY(0.1;1.8E-5;4.74)",
                "=BUFFER_CAPACITY(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BUFFER_CAPACITY formula string.

        Args:
            *args: buffer_conc, ka, pH
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        buffer_conc = args[0]
        ka = args[1]
        pH = args[2]

        # β = 2.303 * C * Ka * [H+] / (Ka + [H+])²
        # where [H+] = 10^(-pH)
        return f"of:=2.303*{buffer_conc}*{ka}*10^(-{pH})/({ka}+10^(-{pH}))^2"


__all__ = [
    "BufferCapacityFormula",
    "MolalityFormula",
    "MolarityFormula",
    "MoleFractionFormula",
    "OsmoticPressureFormula",
    "RaoultsLawFormula",
    "pHCalculationFormula",
]
