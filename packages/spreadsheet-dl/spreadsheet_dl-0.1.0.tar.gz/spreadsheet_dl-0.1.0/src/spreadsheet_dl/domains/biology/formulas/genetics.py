"""Genetics formulas for population genetics and inheritance.

Genetics formulas for allele frequencies, linkage, and statistical tests
(HARDY_WEINBERG, LINKAGE_DISEQUILIBRIUM, RECOMBINATION_FREQUENCY,
CHI2_GENETICS, INBREEDING_COEFFICIENT)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class HardyWeinbergFormula(BaseFormula):
    """Calculate expected genotype frequencies under Hardy-Weinberg equilibrium.

        HARDY_WEINBERG formula for allele frequency equilibrium

    Example:
        >>> formula = HardyWeinbergFormula()
        >>> result = formula.build("A1", "B1")
        >>> # Returns: "A1^2 + 2*A1*B1 + B1^2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for HARDY_WEINBERG

            Formula metadata for Hardy-Weinberg equilibrium
        """
        return FormulaMetadata(
            name="HARDY_WEINBERG",
            category="genetics",
            description="Expected genotype frequencies under HW equilibrium",
            arguments=(
                FormulaArgument(
                    "p_freq",
                    "number",
                    required=True,
                    description="Frequency of allele p (0-1)",
                ),
                FormulaArgument(
                    "q_freq",
                    "number",
                    required=True,
                    description="Frequency of allele q (0-1)",
                ),
            ),
            return_type="number",
            examples=(
                "=HARDY_WEINBERG(A1;B1)",
                "=HARDY_WEINBERG(0.6;0.4)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build HARDY_WEINBERG formula string.

        Args:
            *args: p_freq, q_freq
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            HARDY_WEINBERG formula building (p² + 2pq + q²)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        p_freq = args[0]
        q_freq = args[1]

        # Hardy-Weinberg: p² + 2pq + q²
        return f"of:={p_freq}^2 + 2*{p_freq}*{q_freq} + {q_freq}^2"


@dataclass(slots=True, frozen=True)
class LinkageDisequilibriumFormula(BaseFormula):
    """Calculate linkage disequilibrium between two loci.

        LINKAGE_DISEQUILIBRIUM formula for non-random association

    Example:
        >>> formula = LinkageDisequilibriumFormula()
        >>> result = formula.build("A1", "B1", "C1")
        >>> # Returns: "A1 - (B1 * C1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LINKAGE_DISEQUILIBRIUM

            Formula metadata for linkage disequilibrium
        """
        return FormulaMetadata(
            name="LINKAGE_DISEQUILIBRIUM",
            category="genetics",
            description="Measure of LD between two loci",
            arguments=(
                FormulaArgument(
                    "freq_ab",
                    "number",
                    required=True,
                    description="Frequency of haplotype AB",
                ),
                FormulaArgument(
                    "freq_a",
                    "number",
                    required=True,
                    description="Frequency of allele A",
                ),
                FormulaArgument(
                    "freq_b",
                    "number",
                    required=True,
                    description="Frequency of allele B",
                ),
            ),
            return_type="number",
            examples=(
                "=LINKAGE_DISEQUILIBRIUM(A1;B1;C1)",
                "=LINKAGE_DISEQUILIBRIUM(0.3;0.5;0.6)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LINKAGE_DISEQUILIBRIUM formula string.

        Args:
            *args: freq_ab, freq_a, freq_b
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            LINKAGE_DISEQUILIBRIUM formula building (D = PAB - PA*PB)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        freq_ab = args[0]
        freq_a = args[1]
        freq_b = args[2]

        # Linkage disequilibrium = freq_AB - (freq_A * freq_B)
        return f"of:={freq_ab} - ({freq_a} * {freq_b})"


@dataclass(slots=True, frozen=True)
class RecombinationFrequencyFormula(BaseFormula):
    """Calculate recombination frequency between loci.

        RECOMBINATION_FREQUENCY formula for genetic distance

    Example:
        >>> formula = RecombinationFrequencyFormula()
        >>> result = formula.build("A1", "B1")
        >>> # Returns: "A1/B1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RECOMBINATION_FREQUENCY

            Formula metadata for recombination frequency
        """
        return FormulaMetadata(
            name="RECOMBINATION_FREQUENCY",
            category="genetics",
            description="Recombination frequency between loci",
            arguments=(
                FormulaArgument(
                    "recombinants",
                    "number",
                    required=True,
                    description="Number of recombinant offspring",
                ),
                FormulaArgument(
                    "total_offspring",
                    "number",
                    required=True,
                    description="Total number of offspring",
                ),
            ),
            return_type="number",
            examples=(
                "=RECOMBINATION_FREQUENCY(A1;B1)",
                "=RECOMBINATION_FREQUENCY(15;100)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RECOMBINATION_FREQUENCY formula string.

        Args:
            *args: recombinants, total_offspring
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RECOMBINATION_FREQUENCY formula building (RF = recombinants / total)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        recombinants = args[0]
        total_offspring = args[1]

        # Recombination frequency = recombinants / total
        return f"of:={recombinants}/{total_offspring}"


@dataclass(slots=True, frozen=True)
class Chi2GeneticsFormula(BaseFormula):
    """Calculate chi-square test for genetic ratios.

        CHI2_GENETICS formula for goodness of fit test

    Example:
        >>> formula = Chi2GeneticsFormula()
        >>> result = formula.build("A1:A4", "B1:B4")
        >>> # Returns: "SUMPRODUCT((A1:A4 - B1:B4)^2 / B1:B4)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CHI2_GENETICS

            Formula metadata for chi-square genetics test
        """
        return FormulaMetadata(
            name="CHI2_GENETICS",
            category="genetics",
            description="Chi-square test for genetic ratios",
            arguments=(
                FormulaArgument(
                    "observed_range",
                    "range",
                    required=True,
                    description="Range of observed values",
                ),
                FormulaArgument(
                    "expected_range",
                    "range",
                    required=True,
                    description="Range of expected values",
                ),
            ),
            return_type="number",
            examples=(
                "=CHI2_GENETICS(A1:A4;B1:B4)",
                "=CHI2_GENETICS(observed;expected)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CHI2_GENETICS formula string.

        Args:
            *args: observed_range, expected_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CHI2_GENETICS formula building (χ² = Σ((O-E)²/E))

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        observed_range = args[0]
        expected_range = args[1]

        # Chi-square = SUMPRODUCT((observed - expected)^2 / expected)
        return f"of:=SUMPRODUCT(({observed_range} - {expected_range})^2 / {expected_range})"


@dataclass(slots=True, frozen=True)
class InbreedingCoefficientFormula(BaseFormula):
    """Calculate inbreeding coefficient F.

        INBREEDING_COEFFICIENT formula for relatedness measure

    Example:
        >>> formula = InbreedingCoefficientFormula()
        >>> result = formula.build("A1", "B1")
        >>> # Returns: "1 - (A1/B1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for INBREEDING_COEFFICIENT

            Formula metadata for inbreeding coefficient
        """
        return FormulaMetadata(
            name="INBREEDING_COEFFICIENT",
            category="genetics",
            description="Inbreeding coefficient F",
            arguments=(
                FormulaArgument(
                    "observed_heterozygosity",
                    "number",
                    required=True,
                    description="Observed heterozygosity (Ho)",
                ),
                FormulaArgument(
                    "expected_heterozygosity",
                    "number",
                    required=True,
                    description="Expected heterozygosity (He)",
                ),
            ),
            return_type="number",
            examples=(
                "=INBREEDING_COEFFICIENT(A1;B1)",
                "=INBREEDING_COEFFICIENT(0.25;0.5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build INBREEDING_COEFFICIENT formula string.

        Args:
            *args: observed_heterozygosity, expected_heterozygosity
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            INBREEDING_COEFFICIENT formula building (F = 1 - Ho/He)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        observed_heterozygosity = args[0]
        expected_heterozygosity = args[1]

        # Inbreeding coefficient = 1 - (observed / expected)
        return f"of:=1 - ({observed_heterozygosity}/{expected_heterozygosity})"


__all__ = [
    "Chi2GeneticsFormula",
    "HardyWeinbergFormula",
    "InbreedingCoefficientFormula",
    "LinkageDisequilibriumFormula",
    "RecombinationFrequencyFormula",
]
