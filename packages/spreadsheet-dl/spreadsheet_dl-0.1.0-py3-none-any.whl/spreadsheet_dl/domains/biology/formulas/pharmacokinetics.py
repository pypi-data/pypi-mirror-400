"""Pharmacokinetics formulas for drug metabolism and dosing.

Pharmacokinetics formulas for drug clearance, distribution, and dosing
(CLEARANCE, VOLUME_OF_DISTRIBUTION, HALF_LIFE, LOADING_DOSE, MAINTENANCE_DOSE)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ClearanceFormula(BaseFormula):
    """Calculate total body clearance of drug.

        CLEARANCE formula for drug elimination rate

    Example:
        >>> formula = ClearanceFormula()
        >>> result = formula.build("A1", "B1")
        >>> # Returns: "A1/B1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CLEARANCE

            Formula metadata for drug clearance
        """
        return FormulaMetadata(
            name="CLEARANCE",
            category="pharmacokinetics",
            description="Total body clearance of drug",
            arguments=(
                FormulaArgument(
                    "dose",
                    "number",
                    required=True,
                    description="Drug dose administered",
                ),
                FormulaArgument(
                    "auc",
                    "number",
                    required=True,
                    description="Area under the curve (AUC)",
                ),
            ),
            return_type="number",
            examples=(
                "=CLEARANCE(A1;B1)",
                "=CLEARANCE(500;125)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CLEARANCE formula string.

        Args:
            *args: dose, auc
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CLEARANCE formula building (CL = Dose / AUC)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        dose = args[0]
        auc = args[1]

        # Clearance = Dose / AUC
        return f"of:={dose}/{auc}"


@dataclass(slots=True, frozen=True)
class VolumeOfDistributionFormula(BaseFormula):
    """Calculate apparent volume of distribution.

        VOLUME_OF_DISTRIBUTION formula for drug distribution

    Example:
        >>> formula = VolumeOfDistributionFormula()
        >>> result = formula.build("A1", "B1")
        >>> # Returns: "A1/B1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for VOLUME_OF_DISTRIBUTION

            Formula metadata for volume of distribution
        """
        return FormulaMetadata(
            name="VOLUME_OF_DISTRIBUTION",
            category="pharmacokinetics",
            description="Apparent volume of distribution",
            arguments=(
                FormulaArgument(
                    "dose",
                    "number",
                    required=True,
                    description="Drug dose administered",
                ),
                FormulaArgument(
                    "concentration",
                    "number",
                    required=True,
                    description="Plasma drug concentration",
                ),
            ),
            return_type="number",
            examples=(
                "=VOLUME_OF_DISTRIBUTION(A1;B1)",
                "=VOLUME_OF_DISTRIBUTION(500;10)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build VOLUME_OF_DISTRIBUTION formula string.

        Args:
            *args: dose, concentration
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            VOLUME_OF_DISTRIBUTION formula building (Vd = Dose / C0)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        dose = args[0]
        concentration = args[1]

        # Volume of distribution = Dose / Concentration
        return f"of:={dose}/{concentration}"


@dataclass(slots=True, frozen=True)
class HalfLifeFormula(BaseFormula):
    """Calculate elimination half-life.

        HALF_LIFE formula for drug elimination

    Example:
        >>> formula = HalfLifeFormula()
        >>> result = formula.build("A1", "B1")
        >>> # Returns: "0.693*A1/B1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for HALF_LIFE

            Formula metadata for elimination half-life
        """
        return FormulaMetadata(
            name="HALF_LIFE",
            category="pharmacokinetics",
            description="Time for concentration to decrease by half",
            arguments=(
                FormulaArgument(
                    "volume_dist",
                    "number",
                    required=True,
                    description="Volume of distribution",
                ),
                FormulaArgument(
                    "clearance",
                    "number",
                    required=True,
                    description="Total body clearance",
                ),
            ),
            return_type="number",
            examples=(
                "=HALF_LIFE(A1;B1)",
                "=HALF_LIFE(50;4)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build HALF_LIFE formula string.

        Args:
            *args: volume_dist, clearance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            HALF_LIFE formula building (t1/2 = 0.693 * Vd / CL)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        volume_dist = args[0]
        clearance = args[1]

        # Half-life = 0.693 * Vd / CL
        return f"of:=0.693*{volume_dist}/{clearance}"


@dataclass(slots=True, frozen=True)
class LoadingDoseFormula(BaseFormula):
    """Calculate initial loading dose.

        LOADING_DOSE formula for reaching target concentration

    Example:
        >>> formula = LoadingDoseFormula()
        >>> result = formula.build("A1", "B1")
        >>> # Returns: "A1*B1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LOADING_DOSE

            Formula metadata for loading dose calculation
        """
        return FormulaMetadata(
            name="LOADING_DOSE",
            category="pharmacokinetics",
            description="Initial loading dose to reach target concentration",
            arguments=(
                FormulaArgument(
                    "target_conc",
                    "number",
                    required=True,
                    description="Target plasma concentration",
                ),
                FormulaArgument(
                    "volume_dist",
                    "number",
                    required=True,
                    description="Volume of distribution",
                ),
            ),
            return_type="number",
            examples=(
                "=LOADING_DOSE(A1;B1)",
                "=LOADING_DOSE(10;50)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LOADING_DOSE formula string.

        Args:
            *args: target_conc, volume_dist
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            LOADING_DOSE formula building (LD = Css * Vd)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        target_conc = args[0]
        volume_dist = args[1]

        # Loading dose = Target concentration * Volume of distribution
        return f"of:={target_conc}*{volume_dist}"


@dataclass(slots=True, frozen=True)
class MaintenanceDoseFormula(BaseFormula):
    """Calculate maintenance dose for steady state.

        MAINTENANCE_DOSE formula for steady-state dosing

    Example:
        >>> formula = MaintenanceDoseFormula()
        >>> result = formula.build("A1", "B1", "C1")
        >>> # Returns: "A1*B1*C1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MAINTENANCE_DOSE

            Formula metadata for maintenance dose calculation
        """
        return FormulaMetadata(
            name="MAINTENANCE_DOSE",
            category="pharmacokinetics",
            description="Maintenance dose for steady state",
            arguments=(
                FormulaArgument(
                    "clearance",
                    "number",
                    required=True,
                    description="Total body clearance",
                ),
                FormulaArgument(
                    "target_conc",
                    "number",
                    required=True,
                    description="Target steady-state concentration",
                ),
                FormulaArgument(
                    "dosing_interval",
                    "number",
                    required=True,
                    description="Dosing interval (hours)",
                ),
            ),
            return_type="number",
            examples=(
                "=MAINTENANCE_DOSE(A1;B1;C1)",
                "=MAINTENANCE_DOSE(4;10;12)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MAINTENANCE_DOSE formula string.

        Args:
            *args: clearance, target_conc, dosing_interval
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MAINTENANCE_DOSE formula building (MD = CL * Css * τ)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        clearance = args[0]
        target_conc = args[1]
        dosing_interval = args[2]

        # Maintenance dose = Clearance * Target concentration * Dosing interval
        return f"of:={clearance}*{target_conc}*{dosing_interval}"


__all__ = [
    "ClearanceFormula",
    "HalfLifeFormula",
    "LoadingDoseFormula",
    "MaintenanceDoseFormula",
    "VolumeOfDistributionFormula",
]
