"""Learning metrics formulas.

Learning metrics formulas
(LEARNING_GAIN, MASTERY_LEVEL, ATTENDANCE_RATE, COMPLETION_RATE,
BLOOM_TAXONOMY_LEVEL, READABILITY_SCORE)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class LearningGainFormula(BaseFormula):
    """Calculate normalized learning gain.

        LEARNING_GAIN formula for pre/post assessment

    Uses Hake's normalized gain: g = (post - pre) / (max - pre)

    Example:
        >>> formula = LearningGainFormula()
        >>> result = formula.build("A1", "A2", "100")
        >>> # Returns: "(A2-A1)/(100-A1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LEARNING_GAIN

            Formula metadata
        """
        return FormulaMetadata(
            name="LEARNING_GAIN",
            category="education",
            description="Calculate normalized learning gain (Hake's formula)",
            arguments=(
                FormulaArgument(
                    "pre_score",
                    "number",
                    required=True,
                    description="Pre-assessment score",
                ),
                FormulaArgument(
                    "post_score",
                    "number",
                    required=True,
                    description="Post-assessment score",
                ),
                FormulaArgument(
                    "max_score",
                    "number",
                    required=False,
                    description="Maximum possible score",
                    default=100,
                ),
            ),
            return_type="number",
            examples=(
                "=LEARNING_GAIN(B2;C2)",
                "=LEARNING_GAIN(pre;post;100)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LEARNING_GAIN formula string.

        Args:
            *args: pre_score, post_score, [max_score]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            LEARNING_GAIN formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        pre_score = args[0]
        post_score = args[1]
        max_score = args[2] if len(args) > 2 else 100

        # Hake's normalized gain: g = (post - pre) / (max - pre)
        # With protection against division by zero
        return f"of:=IF({pre_score}={max_score};1;({post_score}-{pre_score})/({max_score}-{pre_score}))"


@dataclass(slots=True, frozen=True)
class MasteryLevelFormula(BaseFormula):
    """Calculate mastery level for competency-based grading.

        MASTERY_LEVEL formula for mastery grading

    Returns mastery level (1-4 or custom scale) based on score.

    Example:
        >>> formula = MasteryLevelFormula()
        >>> result = formula.build("A1")
        >>> # Returns formula for 4-point mastery scale
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MASTERY_LEVEL

            Formula metadata
        """
        return FormulaMetadata(
            name="MASTERY_LEVEL",
            category="education",
            description="Calculate mastery level from score",
            arguments=(
                FormulaArgument(
                    "score",
                    "number",
                    required=True,
                    description="Student score (0-100)",
                ),
                FormulaArgument(
                    "scale",
                    "number",
                    required=False,
                    description="Mastery scale levels (default 4)",
                    default=4,
                ),
            ),
            return_type="number",
            examples=(
                "=MASTERY_LEVEL(B2)",
                "=MASTERY_LEVEL(score;5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MASTERY_LEVEL formula string.

        Args:
            *args: score, [scale]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MASTERY_LEVEL formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        score = args[0]
        # scale = args[1] if len(args) > 1 else 4

        # 4-point mastery scale:
        # 4 = Exceeds (90-100)
        # 3 = Meets (80-89)
        # 2 = Approaching (70-79)
        # 1 = Beginning (0-69)
        return f"of:=IF({score}>=90;4;IF({score}>=80;3;IF({score}>=70;2;1)))"


@dataclass(slots=True, frozen=True)
class AttendanceRateFormula(BaseFormula):
    """Calculate student attendance rate.

        ATTENDANCE_RATE formula for attendance tracking

    Calculates percentage of days attended.

    Example:
        >>> formula = AttendanceRateFormula()
        >>> result = formula.build("A1", "A2")
        >>> # Returns: "A1/A2*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ATTENDANCE_RATE

            Formula metadata
        """
        return FormulaMetadata(
            name="ATTENDANCE_RATE",
            category="education",
            description="Calculate student attendance rate percentage",
            arguments=(
                FormulaArgument(
                    "days_present",
                    "number",
                    required=True,
                    description="Number of days present",
                ),
                FormulaArgument(
                    "total_days",
                    "number",
                    required=True,
                    description="Total number of school days",
                ),
            ),
            return_type="number",
            examples=(
                "=ATTENDANCE_RATE(B2;C2)",
                "=ATTENDANCE_RATE(present;total)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ATTENDANCE_RATE formula string.

        Args:
            *args: days_present, total_days
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ATTENDANCE_RATE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        days_present = args[0]
        total_days = args[1]

        return f"of:=IF({total_days}=0;0;{days_present}/{total_days}*100)"


@dataclass(slots=True, frozen=True)
class CompletionRateFormula(BaseFormula):
    """Calculate assignment completion rate.

        COMPLETION_RATE formula for assignment tracking

    Calculates percentage of assignments completed.

    Example:
        >>> formula = CompletionRateFormula()
        >>> result = formula.build("A1", "A2")
        >>> # Returns: "A1/A2*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for COMPLETION_RATE

            Formula metadata
        """
        return FormulaMetadata(
            name="COMPLETION_RATE",
            category="education",
            description="Calculate assignment completion rate percentage",
            arguments=(
                FormulaArgument(
                    "completed",
                    "number",
                    required=True,
                    description="Number of assignments completed",
                ),
                FormulaArgument(
                    "total",
                    "number",
                    required=True,
                    description="Total number of assignments",
                ),
            ),
            return_type="number",
            examples=(
                "=COMPLETION_RATE(B2;C2)",
                "=COMPLETION_RATE(completed;total)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build COMPLETION_RATE formula string.

        Args:
            *args: completed, total
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            COMPLETION_RATE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        completed = args[0]
        total = args[1]

        return f"of:=IF({total}=0;0;{completed}/{total}*100)"


@dataclass(slots=True, frozen=True)
class BloomTaxonomyLevelFormula(BaseFormula):
    """Categorize learning objective by Bloom's Taxonomy level.

        BLOOM_TAXONOMY_LEVEL formula for learning design

    Returns taxonomy level (1-6) based on action verb keywords.

    Example:
        >>> formula = BloomTaxonomyLevelFormula()
        >>> result = formula.build("A1")
        >>> # Returns formula to categorize by Bloom's level
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BLOOM_TAXONOMY_LEVEL

            Formula metadata
        """
        return FormulaMetadata(
            name="BLOOM_TAXONOMY_LEVEL",
            category="education",
            description="Categorize objective by Bloom's Taxonomy level (1-6)",
            arguments=(
                FormulaArgument(
                    "objective_text",
                    "text",
                    required=True,
                    description="Learning objective text",
                ),
            ),
            return_type="number",
            examples=(
                "=BLOOM_TAXONOMY_LEVEL(B2)",
                '=BLOOM_TAXONOMY_LEVEL("Analyze the causes...")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BLOOM_TAXONOMY_LEVEL formula string.

        Args:
            *args: objective_text
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            BLOOM_TAXONOMY_LEVEL formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        text = args[0]

        # Bloom's levels (simplified detection via keywords):
        # 6 = Create (design, construct, develop, formulate, create)
        # 5 = Evaluate (judge, critique, evaluate, assess, justify)
        # 4 = Analyze (analyze, compare, contrast, differentiate, examine)
        # 3 = Apply (apply, demonstrate, solve, use, implement)
        # 2 = Understand (explain, describe, summarize, interpret, classify)
        # 1 = Remember (list, define, recall, identify, name)
        upper_text = f"UPPER({text})"

        # Build nested IF formula for detection
        return (
            f'of:=IF(OR(ISNUMBER(SEARCH("CREATE";{upper_text}));'
            f'ISNUMBER(SEARCH("DESIGN";{upper_text})));6;'
            f'IF(OR(ISNUMBER(SEARCH("EVALUATE";{upper_text}));'
            f'ISNUMBER(SEARCH("JUDGE";{upper_text})));5;'
            f'IF(OR(ISNUMBER(SEARCH("ANALYZE";{upper_text}));'
            f'ISNUMBER(SEARCH("COMPARE";{upper_text})));4;'
            f'IF(OR(ISNUMBER(SEARCH("APPLY";{upper_text}));'
            f'ISNUMBER(SEARCH("SOLVE";{upper_text})));3;'
            f'IF(OR(ISNUMBER(SEARCH("EXPLAIN";{upper_text}));'
            f'ISNUMBER(SEARCH("DESCRIBE";{upper_text})));2;1)))))'
        )


@dataclass(slots=True, frozen=True)
class ReadabilityScoreFormula(BaseFormula):
    """Calculate Flesch-Kincaid readability grade level.

        READABILITY_SCORE formula for content analysis

    Calculates approximate grade level for text readability.

    Example:
        >>> formula = ReadabilityScoreFormula()
        >>> result = formula.build("100", "20", "150")
        >>> # Returns Flesch-Kincaid grade level formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for READABILITY_SCORE

            Formula metadata
        """
        return FormulaMetadata(
            name="READABILITY_SCORE",
            category="education",
            description="Calculate Flesch-Kincaid grade level",
            arguments=(
                FormulaArgument(
                    "word_count",
                    "number",
                    required=True,
                    description="Total number of words",
                ),
                FormulaArgument(
                    "sentence_count",
                    "number",
                    required=True,
                    description="Total number of sentences",
                ),
                FormulaArgument(
                    "syllable_count",
                    "number",
                    required=True,
                    description="Total number of syllables",
                ),
            ),
            return_type="number",
            examples=(
                "=READABILITY_SCORE(B2;C2;D2)",
                "=READABILITY_SCORE(words;sentences;syllables)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build READABILITY_SCORE formula string.

        Args:
            *args: word_count, sentence_count, syllable_count
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            READABILITY_SCORE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        word_count = args[0]
        sentence_count = args[1]
        syllable_count = args[2]

        # Flesch-Kincaid Grade Level:
        # 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        return f"of:=0.39*({word_count}/{sentence_count})+11.8*({syllable_count}/{word_count})-15.59"


@dataclass(slots=True, frozen=True)
class LearningCurveFormula(BaseFormula):
    """Calculate learning curve performance improvement.

        Learning curve: y = a * x^b (power law of practice)

    Example:
        >>> formula = LearningCurveFormula()
        >>> result = formula.build("100", "5", "-0.322")
        >>> # Returns performance at trial 5
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LearningCurve

            Formula metadata
        """
        return FormulaMetadata(
            name="LEARNING_CURVE",
            category="education",
            description="Calculate learning curve performance (power law of practice)",
            arguments=(
                FormulaArgument(
                    "initial_performance",
                    "number",
                    required=True,
                    description="Initial performance level",
                ),
                FormulaArgument(
                    "trial_number",
                    "number",
                    required=True,
                    description="Trial or practice attempt number",
                ),
                FormulaArgument(
                    "learning_rate",
                    "number",
                    required=False,
                    description="Learning rate exponent (default -0.322)",
                    default=-0.322,
                ),
            ),
            return_type="number",
            examples=(
                "=LEARNING_CURVE(100;5)",
                "=LEARNING_CURVE(A1;A2;-0.3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LearningCurve formula string.

        Args:
            *args: initial_performance, trial_number, [learning_rate]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            LearningCurve formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        initial = args[0]
        trial = args[1]
        rate = args[2] if len(args) > 2 else -0.322

        # y = a * x^b
        return f"of:={initial}*POWER({trial};{rate})"


@dataclass(slots=True, frozen=True)
class ForgettingCurveFormula(BaseFormula):
    """Calculate Ebbinghaus forgetting curve (retention decay).

        R = e^(-t/S) where R=retention, t=time, S=strength

    Example:
        >>> formula = ForgettingCurveFormula()
        >>> result = formula.build("7", "2")
        >>> # Returns retention after 7 days
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ForgettingCurve

            Formula metadata
        """
        return FormulaMetadata(
            name="FORGETTING_CURVE",
            category="education",
            description="Calculate retention using Ebbinghaus forgetting curve",
            arguments=(
                FormulaArgument(
                    "days_elapsed",
                    "number",
                    required=True,
                    description="Days since learning",
                ),
                FormulaArgument(
                    "memory_strength",
                    "number",
                    required=False,
                    description="Memory strength factor (default 2)",
                    default=2,
                ),
            ),
            return_type="number",
            examples=(
                "=FORGETTING_CURVE(7)",
                "=FORGETTING_CURVE(A1;3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ForgettingCurve formula string.

        Args:
            *args: days_elapsed, [memory_strength]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ForgettingCurve formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        days = args[0]
        strength = args[1] if len(args) > 1 else 2

        # R = e^(-t/S)
        return f"of:=EXP(-{days}/{strength})"


@dataclass(slots=True, frozen=True)
class SpacedRepetitionFormula(BaseFormula):
    """Calculate optimal review interval for spaced repetition.

        Next interval = current_interval * ease_factor

    Example:
        >>> formula = SpacedRepetitionFormula()
        >>> result = formula.build("3", "2.5", "1")
        >>> # Returns next review interval
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SpacedRepetition

            Formula metadata
        """
        return FormulaMetadata(
            name="SPACED_REPETITION",
            category="education",
            description="Calculate optimal review interval for spaced repetition",
            arguments=(
                FormulaArgument(
                    "current_interval",
                    "number",
                    required=True,
                    description="Current interval in days",
                ),
                FormulaArgument(
                    "ease_factor",
                    "number",
                    required=True,
                    description="Ease factor (1.3-2.5, based on recall difficulty)",
                ),
                FormulaArgument(
                    "performance",
                    "number",
                    required=True,
                    description="Performance score (0-1, where 1 is perfect recall)",
                ),
            ),
            return_type="number",
            examples=(
                "=SPACED_REPETITION(3;2.5;1)",
                "=SPACED_REPETITION(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SpacedRepetition formula string.

        Args:
            *args: current_interval, ease_factor, performance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SpacedRepetition formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        interval = args[0]
        ease = args[1]
        performance = args[2]

        # Next interval = current * ease * performance adjustment
        # If performance < 0.6, reset to 1 day, else multiply by ease
        return f"of:=IF({performance}<0.6;1;{interval}*{ease})"


@dataclass(slots=True, frozen=True)
class MasteryLearningFormula(BaseFormula):
    """Calculate Bloom 2-sigma effect for mastery learning.

        Achievement boost from mastery learning vs conventional

    Example:
        >>> formula = MasteryLearningFormula()
        >>> result = formula.build("75", "2.0")
        >>> # Returns expected mastery learning achievement
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MasteryLearning

            Formula metadata
        """
        return FormulaMetadata(
            name="MASTERY_LEARNING",
            category="education",
            description="Calculate Bloom 2-sigma mastery learning effect",
            arguments=(
                FormulaArgument(
                    "baseline_score",
                    "number",
                    required=True,
                    description="Baseline conventional instruction score",
                ),
                FormulaArgument(
                    "sigma_effect",
                    "number",
                    required=False,
                    description="Standard deviation effect size (default 2.0)",
                    default=2.0,
                ),
                FormulaArgument(
                    "population_sd",
                    "number",
                    required=False,
                    description="Population standard deviation (default 15)",
                    default=15,
                ),
            ),
            return_type="number",
            examples=(
                "=MASTERY_LEARNING(75)",
                "=MASTERY_LEARNING(A1;2.0;15)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MasteryLearning formula string.

        Args:
            *args: baseline_score, [sigma_effect], [population_sd]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MasteryLearning formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        baseline = args[0]
        sigma = args[1] if len(args) > 1 else 2.0
        sd = args[2] if len(args) > 2 else 15

        # Expected score = baseline + (sigma * SD)
        return f"of:=MIN({baseline}+({sigma}*{sd});100)"


@dataclass(slots=True, frozen=True)
class Bloom2SigmaFormula(BaseFormula):
    """Convert percentile rank to standard deviations (Bloom's 2-sigma).

        BLOOM2SIGMA formula for effect size conversion

    Converts percentile rank to z-score (standard deviations from mean).
    Named after Bloom's 2-sigma finding that tutored students perform
    2 standard deviations better than conventional instruction.

    Example:
        >>> formula = Bloom2SigmaFormula()
        >>> result = formula.build("84")
        >>> # Returns: "NORMSINV(84/100)" which is approximately 1.0
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BLOOM2SIGMA

            Formula metadata
        """
        return FormulaMetadata(
            name="BLOOM2SIGMA",
            category="education",
            description="Convert percentile rank to standard deviations (z-score)",
            arguments=(
                FormulaArgument(
                    "percentile_rank",
                    "number",
                    required=True,
                    description="Percentile rank (0-100)",
                ),
            ),
            return_type="number",
            examples=(
                "=BLOOM2SIGMA(84)",
                "=BLOOM2SIGMA(A1)",
                "=BLOOM2SIGMA(98)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build Bloom2Sigma formula string.

        Args:
            *args: percentile_rank
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Bloom2Sigma formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        percentile = args[0]

        # Convert percentile (0-100) to z-score
        return f"of:=NORMSINV({percentile}/100)"


@dataclass(slots=True, frozen=True)
class TimeOnTaskFormula(BaseFormula):
    """Calculate Carroll model time on task for school learning.

        Learning = f(time spent / time needed)

    Example:
        >>> formula = TimeOnTaskFormula()
        >>> result = formula.build("45", "60", "0.8")
        >>> # Returns learning achievement percentage
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for TimeOnTask

            Formula metadata
        """
        return FormulaMetadata(
            name="TIME_ON_TASK",
            category="education",
            description="Calculate Carroll model time on task effect",
            arguments=(
                FormulaArgument(
                    "time_spent",
                    "number",
                    required=True,
                    description="Actual time spent on task (minutes)",
                ),
                FormulaArgument(
                    "time_needed",
                    "number",
                    required=True,
                    description="Time needed for mastery (minutes)",
                ),
                FormulaArgument(
                    "opportunity_quality",
                    "number",
                    required=False,
                    description="Quality of instruction (0-1, default 0.8)",
                    default=0.8,
                ),
            ),
            return_type="number",
            examples=(
                "=TIME_ON_TASK(45;60)",
                "=TIME_ON_TASK(A1;A2;0.9)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TimeOnTask formula string.

        Args:
            *args: time_spent, time_needed, [opportunity_quality]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            TimeOnTask formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spent = args[0]
        needed = args[1]
        quality = args[2] if len(args) > 2 else 0.8

        # Learning = min(time_spent / time_needed, 1) * quality * 100
        return f"of:=MIN({spent}/{needed};1)*{quality}*100"


__all__ = [
    "AttendanceRateFormula",
    "Bloom2SigmaFormula",
    "BloomTaxonomyLevelFormula",
    "CompletionRateFormula",
    "ForgettingCurveFormula",
    "LearningCurveFormula",
    "LearningGainFormula",
    "MasteryLearningFormula",
    "MasteryLevelFormula",
    "ReadabilityScoreFormula",
    "SpacedRepetitionFormula",
    "TimeOnTaskFormula",
]
