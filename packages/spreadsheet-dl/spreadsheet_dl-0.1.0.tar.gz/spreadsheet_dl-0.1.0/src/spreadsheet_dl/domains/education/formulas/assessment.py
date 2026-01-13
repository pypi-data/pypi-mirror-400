"""Educational assessment and psychometric formulas.

Education formulas for test analysis and reliability
(ItemDifficulty, ItemDiscrimination, CronbachAlpha)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ItemDifficulty(BaseFormula):
    """Calculate test item difficulty index.

        Item difficulty calculation (proportion correct)

    Example:
        >>> formula = ItemDifficulty()
        >>> result = formula.build("25", "30")
        >>> # Returns: "25/30"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ItemDifficulty

            Formula metadata
        """
        return FormulaMetadata(
            name="ITEM_DIFFICULTY",
            category="assessment",
            description="Calculate item difficulty index (p-value)",
            arguments=(
                FormulaArgument(
                    "correct_responses",
                    "number",
                    required=True,
                    description="Number of correct responses",
                ),
                FormulaArgument(
                    "total_responses",
                    "number",
                    required=True,
                    description="Total number of responses",
                ),
            ),
            return_type="number",
            examples=(
                "=ITEM_DIFFICULTY(25;30)",
                "=ITEM_DIFFICULTY(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ItemDifficulty formula string.

        Args:
            *args: correct_responses, total_responses
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ItemDifficulty formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        correct_responses = args[0]
        total_responses = args[1]

        # p = Correct / Total
        return f"of:={correct_responses}/{total_responses}"


@dataclass(slots=True, frozen=True)
class ItemDiscrimination(BaseFormula):
    """Calculate item discrimination power.

        Item discrimination index (upper-lower difference)

    Example:
        >>> formula = ItemDiscrimination()
        >>> result = formula.build("0.80", "0.40")
        >>> # Returns: "0.80-0.40"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ItemDiscrimination

            Formula metadata
        """
        return FormulaMetadata(
            name="ITEM_DISCRIMINATION",
            category="assessment",
            description="Calculate item discrimination index (D)",
            arguments=(
                FormulaArgument(
                    "upper_group_p",
                    "number",
                    required=True,
                    description="Proportion correct in upper group",
                ),
                FormulaArgument(
                    "lower_group_p",
                    "number",
                    required=True,
                    description="Proportion correct in lower group",
                ),
            ),
            return_type="number",
            examples=(
                "=ITEM_DISCRIMINATION(0.80;0.40)",
                "=ITEM_DISCRIMINATION(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ItemDiscrimination formula string.

        Args:
            *args: upper_group_p, lower_group_p
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ItemDiscrimination formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        upper_group_p = args[0]
        lower_group_p = args[1]

        # D = PU - PL
        return f"of:={upper_group_p}-{lower_group_p}"


@dataclass(slots=True, frozen=True)
class CronbachAlpha(BaseFormula):
    """Calculate Cronbach's alpha reliability coefficient.

        Cronbach's alpha for test reliability

    Example:
        >>> formula = CronbachAlpha()
        >>> result = formula.build("10", "25", "100")
        >>> # Returns: "of:=(10/(10-1))*(1-25/100)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CronbachAlpha

            Formula metadata
        """
        return FormulaMetadata(
            name="CRONBACH_ALPHA",
            category="assessment",
            description="Calculate Cronbach's alpha reliability coefficient",
            arguments=(
                FormulaArgument(
                    "k",
                    "number",
                    required=True,
                    description="Number of items",
                ),
                FormulaArgument(
                    "sum_item_variance",
                    "number",
                    required=True,
                    description="Sum of item variances",
                ),
                FormulaArgument(
                    "total_variance",
                    "number",
                    required=True,
                    description="Total test variance",
                ),
            ),
            return_type="number",
            examples=(
                "=CRONBACH_ALPHA(10;25;100)",
                "=CRONBACH_ALPHA(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CronbachAlpha formula string.

        Args:
            *args: k, sum_item_variance, total_variance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CronbachAlpha formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        k = args[0]
        sum_item_variance = args[1]
        total_variance = args[2]

        # alpha = (k/(k-1)) * (1 - (sum_variance/total_variance))
        return f"of:=({k}/({k}-1))*(1-{sum_item_variance}/{total_variance})"


@dataclass(slots=True, frozen=True)
class KR20Formula(BaseFormula):
    """Calculate Kuder-Richardson 20 reliability coefficient.

        KR20 reliability for dichotomous items

    Example:
        >>> formula = KR20Formula()
        >>> result = formula.build("20", "10", "36")
        >>> # Returns KR20 reliability coefficient formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for KR20

            Formula metadata
        """
        return FormulaMetadata(
            name="KR20",
            category="assessment",
            description="Calculate Kuder-Richardson 20 reliability coefficient",
            arguments=(
                FormulaArgument(
                    "k",
                    "number",
                    required=True,
                    description="Number of items",
                ),
                FormulaArgument(
                    "sum_pq",
                    "number",
                    required=True,
                    description="Sum of p*q for all items (p=proportion correct, q=1-p)",
                ),
                FormulaArgument(
                    "total_variance",
                    "number",
                    required=True,
                    description="Total test variance",
                ),
            ),
            return_type="number",
            examples=(
                "=KR20(20;10;36)",
                "=KR20(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build KR20 formula string.

        Args:
            *args: k, sum_pq, total_variance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            KR20 formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        k = args[0]
        sum_pq = args[1]
        total_variance = args[2]

        # KR20 = (k/(k-1)) * (1 - sum_pq/variance)
        return f"of:=({k}/({k}-1))*(1-{sum_pq}/{total_variance})"


@dataclass(slots=True, frozen=True)
class KR21Formula(BaseFormula):
    """Calculate Kuder-Richardson 21 reliability coefficient.

        Simplified KR20 assuming equal item difficulty

    Example:
        >>> formula = KR21Formula()
        >>> result = formula.build("20", "15", "36")
        >>> # Returns KR21 reliability coefficient formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for KR21

            Formula metadata
        """
        return FormulaMetadata(
            name="KR21",
            category="assessment",
            description="Calculate Kuder-Richardson 21 reliability (simplified KR20)",
            arguments=(
                FormulaArgument(
                    "k",
                    "number",
                    required=True,
                    description="Number of items",
                ),
                FormulaArgument(
                    "mean",
                    "number",
                    required=True,
                    description="Mean test score",
                ),
                FormulaArgument(
                    "variance",
                    "number",
                    required=True,
                    description="Test score variance",
                ),
            ),
            return_type="number",
            examples=(
                "=KR21(20;15;36)",
                "=KR21(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build KR21 formula string.

        Args:
            *args: k, mean, variance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            KR21 formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        k = args[0]
        mean = args[1]
        variance = args[2]

        # KR21 = (k/(k-1)) * (1 - (mean*(k-mean))/(k*variance))
        return f"of:=({k}/({k}-1))*(1-({mean}*({k}-{mean}))/({k}*{variance}))"


@dataclass(slots=True, frozen=True)
class SpearmanBrownFormula(BaseFormula):
    """Calculate Spearman-Brown prophecy formula for test length adjustment.

        Adjust reliability based on test length changes

    Example:
        >>> formula = SpearmanBrownFormula()
        >>> result = formula.build("0.75", "2")
        >>> # Returns adjusted reliability for doubled test length
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SpearmanBrown

            Formula metadata
        """
        return FormulaMetadata(
            name="SPEARMAN_BROWN",
            category="assessment",
            description="Adjust reliability for test length change (Spearman-Brown)",
            arguments=(
                FormulaArgument(
                    "original_reliability",
                    "number",
                    required=True,
                    description="Original reliability coefficient",
                ),
                FormulaArgument(
                    "length_factor",
                    "number",
                    required=True,
                    description="Test length multiplier (e.g., 2 for doubling)",
                ),
            ),
            return_type="number",
            examples=(
                "=SPEARMAN_BROWN(0.75;2)",
                "=SPEARMAN_BROWN(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SpearmanBrown formula string.

        Args:
            *args: original_reliability, length_factor
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SpearmanBrown formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        reliability = args[0]
        factor = args[1]

        # Adjusted = (n*r) / (1 + (n-1)*r)
        return f"of:=({factor}*{reliability})/(1+({factor}-1)*{reliability})"


@dataclass(slots=True, frozen=True)
class StandardErrorMeasurementFormula(BaseFormula):
    """Calculate standard error of measurement.

        SEM = SD * sqrt(1 - reliability)

    Example:
        >>> formula = StandardErrorMeasurementFormula()
        >>> result = formula.build("10", "0.85")
        >>> # Returns SEM formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SEM

            Formula metadata
        """
        return FormulaMetadata(
            name="STANDARD_ERROR_MEASUREMENT",
            category="assessment",
            description="Calculate standard error of measurement (SEM)",
            arguments=(
                FormulaArgument(
                    "standard_deviation",
                    "number",
                    required=True,
                    description="Test score standard deviation",
                ),
                FormulaArgument(
                    "reliability",
                    "number",
                    required=True,
                    description="Test reliability coefficient",
                ),
            ),
            return_type="number",
            examples=(
                "=STANDARD_ERROR_MEASUREMENT(10;0.85)",
                "=STANDARD_ERROR_MEASUREMENT(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SEM formula string.

        Args:
            *args: standard_deviation, reliability
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SEM formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        sd = args[0]
        reliability = args[1]

        # SEM = SD * sqrt(1 - reliability)
        return f"of:={sd}*SQRT(1-{reliability})"


@dataclass(slots=True, frozen=True)
class TrueScoreFormula(BaseFormula):
    """Calculate estimated true score from observed score.

        True score = mean + reliability * (observed - mean)

    Example:
        >>> formula = TrueScoreFormula()
        >>> result = formula.build("85", "75", "0.85")
        >>> # Returns estimated true score
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for TrueScore

            Formula metadata
        """
        return FormulaMetadata(
            name="TRUE_SCORE",
            category="assessment",
            description="Calculate estimated true score from observed score",
            arguments=(
                FormulaArgument(
                    "observed_score",
                    "number",
                    required=True,
                    description="Observed test score",
                ),
                FormulaArgument(
                    "mean_score",
                    "number",
                    required=True,
                    description="Mean score of test",
                ),
                FormulaArgument(
                    "reliability",
                    "number",
                    required=True,
                    description="Test reliability coefficient",
                ),
            ),
            return_type="number",
            examples=(
                "=TRUE_SCORE(85;75;0.85)",
                "=TRUE_SCORE(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TrueScore formula string.

        Args:
            *args: observed_score, mean_score, reliability
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            TrueScore formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        observed = args[0]
        mean = args[1]
        reliability = args[2]

        # True = mean + reliability * (observed - mean)
        return f"of:={mean}+{reliability}*({observed}-{mean})"
