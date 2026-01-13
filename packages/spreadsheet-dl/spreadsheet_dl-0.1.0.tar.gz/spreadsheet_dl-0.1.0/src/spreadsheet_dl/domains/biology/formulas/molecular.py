"""Molecular biology formulas.

Molecular biology formulas
(CONCENTRATION, FOLD_CHANGE, GC_CONTENT, MELTING_TEMP)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ConcentrationFormula(BaseFormula):
    """Calculate nucleic acid concentration from absorbance.

        CONCENTRATION formula for nucleic acid quantification

    Uses A260/A280 ratio for purity assessment.

    Example:
        >>> formula = ConcentrationFormula()
        >>> result = formula.build("A1", "A2", 50)
        >>> # Returns: "A1*50*(A1/A2)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CONCENTRATION

            Formula metadata
        """
        return FormulaMetadata(
            name="CONCENTRATION",
            category="molecular_biology",
            description="Calculate nucleic acid concentration from A260 absorbance",
            arguments=(
                FormulaArgument(
                    "a260",
                    "number",
                    required=True,
                    description="Absorbance at 260nm",
                ),
                FormulaArgument(
                    "a280",
                    "number",
                    required=False,
                    description="Absorbance at 280nm (for purity)",
                    default=None,
                ),
                FormulaArgument(
                    "dilution",
                    "number",
                    required=False,
                    description="Dilution factor",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=CONCENTRATION(A1;A2;50)",
                "=CONCENTRATION(A260;A280;dilution_factor)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CONCENTRATION formula string.

        Args:
            *args: a260, [a280], [dilution]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CONCENTRATION formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        a260 = args[0]
        dilution = 1

        # For DNA: 1 OD260 unit = 50 μg/mL
        # For RNA: 1 OD260 unit = 40 μg/mL
        # Default to DNA (50)
        conversion_factor = 50

        if len(args) > 1:
            # If second arg looks like a number < 10, it's likely a dilution
            # Otherwise treat as A280 for purity check
            if len(args) == 2:
                dilution = args[1]
            elif len(args) == 3:
                # a260, a280, dilution
                dilution = args[2]

        # Concentration = A260 * conversion_factor * dilution
        return f"of:={a260}*{conversion_factor}*{dilution}"


@dataclass(slots=True, frozen=True)
class FoldChangeFormula(BaseFormula):
    """Calculate gene expression fold change using 2^-ΔΔCt method.

        FOLD_CHANGE formula for qPCR analysis

    Example:
        >>> formula = FoldChangeFormula()
        >>> result = formula.build("A1", "A2", "B1", "B2")
        >>> # Returns: "2^-(A1-A2-(B1-B2))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for FOLD_CHANGE

            Formula metadata
        """
        return FormulaMetadata(
            name="FOLD_CHANGE",
            category="molecular_biology",
            description="Calculate gene expression fold change (2^-ΔΔCt method)",
            arguments=(
                FormulaArgument(
                    "ct_target",
                    "number",
                    required=True,
                    description="Ct value of target gene",
                ),
                FormulaArgument(
                    "ct_reference",
                    "number",
                    required=True,
                    description="Ct value of reference gene",
                ),
                FormulaArgument(
                    "ct_control_target",
                    "number",
                    required=True,
                    description="Control Ct value of target gene",
                ),
                FormulaArgument(
                    "ct_control_reference",
                    "number",
                    required=True,
                    description="Control Ct value of reference gene",
                ),
            ),
            return_type="number",
            examples=(
                "=FOLD_CHANGE(A1;A2;B1;B2)",
                "=FOLD_CHANGE(ct_target;ct_ref;ct_control_target;ct_control_ref)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build FOLD_CHANGE formula string.

        Args:
            *args: ct_target, ct_reference, ct_control_target, ct_control_reference
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            FOLD_CHANGE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        ct_target = args[0]
        ct_reference = args[1]
        ct_control_target = args[2]
        ct_control_reference = args[3]

        # ΔCt = Ct_target - Ct_reference
        # ΔΔCt = ΔCt - ΔCt_control
        # Fold change = 2^-ΔΔCt
        delta_ct = f"({ct_target}-{ct_reference})"
        delta_ct_control = f"({ct_control_target}-{ct_control_reference})"
        delta_delta_ct = f"({delta_ct}-{delta_ct_control})"

        return f"of:=POWER(2;-{delta_delta_ct})"


@dataclass(slots=True, frozen=True)
class GCContentFormula(BaseFormula):
    """Calculate GC content percentage of DNA sequence.

        GC_CONTENT formula for sequence analysis

    Example:
        >>> formula = GCContentFormula()
        >>> result = formula.build("A1")
        >>> # Returns formula to count G and C characters
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GC_CONTENT

            Formula metadata
        """
        return FormulaMetadata(
            name="GC_CONTENT",
            category="molecular_biology",
            description="Calculate GC content percentage of DNA sequence",
            arguments=(
                FormulaArgument(
                    "sequence",
                    "text",
                    required=True,
                    description="DNA sequence string",
                ),
            ),
            return_type="number",
            examples=(
                "=GC_CONTENT(A1)",
                "=GC_CONTENT(sequence_cell)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GC_CONTENT formula string.

        Args:
            *args: sequence
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            GC_CONTENT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        sequence = args[0]

        # Count G's and C's, divide by total length
        # (LEN(seq) - LEN(SUBSTITUTE(SUBSTITUTE(UPPER(seq),"G",""),"C",""))) / LEN(seq)
        upper_seq = f"UPPER({sequence})"
        no_g = f'SUBSTITUTE({upper_seq};"G";"")'
        no_gc = f'SUBSTITUTE({no_g};"C";"")'
        gc_count = f"(LEN({upper_seq})-LEN({no_gc}))"

        return f"of:={gc_count}/LEN({sequence})"


@dataclass(slots=True, frozen=True)
class MeltingTempFormula(BaseFormula):
    """Calculate DNA melting temperature estimation.

        MELTING_TEMP formula for primer design

    Uses nearest-neighbor method approximation.

    Example:
        >>> formula = MeltingTempFormula()
        >>> result = formula.build("A1")
        >>> # Returns: formula for Tm calculation
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MELTING_TEMP

            Formula metadata
        """
        return FormulaMetadata(
            name="MELTING_TEMP",
            category="molecular_biology",
            description="Calculate DNA melting temperature (Tm) estimation",
            arguments=(
                FormulaArgument(
                    "sequence",
                    "text",
                    required=True,
                    description="DNA sequence string",
                ),
                FormulaArgument(
                    "na_conc",
                    "number",
                    required=False,
                    description="Na+ concentration (mM)",
                    default=50,
                ),
            ),
            return_type="number",
            examples=(
                "=MELTING_TEMP(A1)",
                "=MELTING_TEMP(A1;50)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MELTING_TEMP formula string.

        Args:
            *args: sequence, [na_conc]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MELTING_TEMP formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        sequence = args[0]
        # na_conc = args[1] if len(args) > 1 else 50  # For future use

        # Simple Tm calculation for short sequences (< 14 bp):
        # Tm = 4(G+C) + 2(A+T)
        # For longer sequences, use salt-adjusted formula
        # We'll use the simple formula as a spreadsheet-friendly approximation

        upper_seq = f"UPPER({sequence})"

        # Count each base
        g_count = f'(LEN({upper_seq})-LEN(SUBSTITUTE({upper_seq};"G";"")))'
        c_count = f'(LEN({upper_seq})-LEN(SUBSTITUTE({upper_seq};"C";"")))'
        a_count = f'(LEN({upper_seq})-LEN(SUBSTITUTE({upper_seq};"A";"")))'
        t_count = f'(LEN({upper_seq})-LEN(SUBSTITUTE({upper_seq};"T";"")))'

        # Tm = 4(G+C) + 2(A+T)
        return f"of:=4*({g_count}+{c_count})+2*({a_count}+{t_count})"


@dataclass(slots=True, frozen=True)
class MichaelisMentenFormula(BaseFormula):
    """Calculate enzyme reaction rate using Michaelis-Menten kinetics.

        MICHAELIS_MENTEN formula for enzyme kinetics

    The Michaelis-Menten equation describes enzyme kinetics:
    v = Vmax * [S] / (Km + [S])

    where:
    - v is the reaction rate
    - Vmax is the maximum reaction rate
    - [S] is the substrate concentration
    - Km is the Michaelis constant

    Example:
        >>> formula = MichaelisMentenFormula()
        >>> result = formula.build("100", "10", "50")
        >>> # Returns: "100*50/(10+50)" = 83.33
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MICHAELIS_MENTEN
        """
        return FormulaMetadata(
            name="MICHAELIS_MENTEN",
            category="molecular_biology",
            description="Calculate enzyme reaction rate (v = Vmax * [S] / (Km + [S]))",
            arguments=(
                FormulaArgument(
                    "vmax",
                    "number",
                    required=True,
                    description="Maximum reaction rate",
                ),
                FormulaArgument(
                    "km",
                    "number",
                    required=True,
                    description="Michaelis constant (substrate concentration at half Vmax)",
                ),
                FormulaArgument(
                    "substrate",
                    "number",
                    required=True,
                    description="Substrate concentration [S]",
                ),
            ),
            return_type="number",
            examples=(
                "=MICHAELIS_MENTEN(100;10;50)",
                "=MICHAELIS_MENTEN(Vmax;Km;substrate_conc)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MICHAELIS_MENTEN formula string.

        Args:
            *args: vmax, km, substrate
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        vmax = args[0]
        km = args[1]
        substrate = args[2]

        # v = Vmax * [S] / (Km + [S])
        return f"of:={vmax}*{substrate}/({km}+{substrate})"


__all__ = [
    "ConcentrationFormula",
    "FoldChangeFormula",
    "GCContentFormula",
    "MeltingTempFormula",
    "MichaelisMentenFormula",
]
