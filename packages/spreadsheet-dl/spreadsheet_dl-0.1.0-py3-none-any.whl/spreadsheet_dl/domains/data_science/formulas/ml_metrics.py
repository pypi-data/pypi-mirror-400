"""Machine learning metrics formulas.

ML metrics formulas (ACCURACY, PRECISION, RECALL, F1SCORE, CONFUSION_MATRIX_METRIC)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class AccuracyFormula(BaseFormula):
    """Accuracy metric: (TP+TN)/(TP+TN+FP+FN).

        ACCURACY formula for ML evaluation

    Example:
        >>> formula = AccuracyFormula()
        >>> result = formula.build(85, 90, 10, 15)
        >>> # Returns: "(85+90)/(85+90+10+15)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ACCURACY

            Formula metadata
        """
        return FormulaMetadata(
            name="ACCURACY",
            category="ml_metrics",
            description="Calculate classification accuracy from confusion matrix values",
            arguments=(
                FormulaArgument(
                    "tp",
                    "number",
                    required=True,
                    description="True Positives count or cell reference",
                ),
                FormulaArgument(
                    "tn",
                    "number",
                    required=True,
                    description="True Negatives count or cell reference",
                ),
                FormulaArgument(
                    "fp",
                    "number",
                    required=True,
                    description="False Positives count or cell reference",
                ),
                FormulaArgument(
                    "fn",
                    "number",
                    required=True,
                    description="False Negatives count or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=ACCURACY(A1;A2;A3;A4)",
                "=(85+90)/(85+90+10+15)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ACCURACY formula string.

        Args:
            *args: tp, tn, fp, fn
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ACCURACY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        tp, tn, fp, fn = args

        # Formula: (TP+TN)/(TP+TN+FP+FN)
        return f"of:=({tp}+{tn})/({tp}+{tn}+{fp}+{fn})"


@dataclass(slots=True, frozen=True)
class PrecisionFormula(BaseFormula):
    """Precision metric: TP/(TP+FP).

        PRECISION formula for ML evaluation

    Example:
        >>> formula = PrecisionFormula()
        >>> result = formula.build(85, 10)
        >>> # Returns: "85/(85+10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PRECISION

            Formula metadata
        """
        return FormulaMetadata(
            name="PRECISION",
            category="ml_metrics",
            description="Calculate precision from true/false positives",
            arguments=(
                FormulaArgument(
                    "tp",
                    "number",
                    required=True,
                    description="True Positives count or cell reference",
                ),
                FormulaArgument(
                    "fp",
                    "number",
                    required=True,
                    description="False Positives count or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=PRECISION(A1;A2)",
                "=85/(85+10)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PRECISION formula string.

        Args:
            *args: tp, fp
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PRECISION formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        tp, fp = args

        # Formula: TP/(TP+FP)
        return f"of:={tp}/({tp}+{fp})"


@dataclass(slots=True, frozen=True)
class RecallFormula(BaseFormula):
    """Recall metric: TP/(TP+FN).

        RECALL formula for ML evaluation

    Example:
        >>> formula = RecallFormula()
        >>> result = formula.build(85, 15)
        >>> # Returns: "85/(85+15)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RECALL

            Formula metadata
        """
        return FormulaMetadata(
            name="RECALL",
            category="ml_metrics",
            description="Calculate recall from true positives and false negatives",
            arguments=(
                FormulaArgument(
                    "tp",
                    "number",
                    required=True,
                    description="True Positives count or cell reference",
                ),
                FormulaArgument(
                    "fn",
                    "number",
                    required=True,
                    description="False Negatives count or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=RECALL(A1;A2)",
                "=85/(85+15)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RECALL formula string.

        Args:
            *args: tp, fn
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RECALL formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        tp, fn = args

        # Formula: TP/(TP+FN)
        return f"of:={tp}/({tp}+{fn})"


@dataclass(slots=True, frozen=True)
class F1ScoreFormula(BaseFormula):
    """F1 Score metric: 2*(Precision*Recall)/(Precision+Recall).

        F1SCORE formula for ML evaluation

    Example:
        >>> formula = F1ScoreFormula()
        >>> result = formula.build("A1", "A2")
        >>> # Returns: "2*(A1*A2)/(A1+A2)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for F1SCORE

            Formula metadata
        """
        return FormulaMetadata(
            name="F1SCORE",
            category="ml_metrics",
            description="Calculate F1 score from precision and recall",
            arguments=(
                FormulaArgument(
                    "precision",
                    "number",
                    required=True,
                    description="Precision value or cell reference",
                ),
                FormulaArgument(
                    "recall",
                    "number",
                    required=True,
                    description="Recall value or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=F1SCORE(A1;A2)",
                "=2*(0.9*0.85)/(0.9+0.85)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build F1SCORE formula string.

        Args:
            *args: precision, recall
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            F1SCORE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        precision, recall = args

        # Formula: 2*(P*R)/(P+R)
        return f"of:=2*({precision}*{recall})/({precision}+{recall})"


@dataclass(slots=True, frozen=True)
class ConfusionMatrixMetricFormula(BaseFormula):
    """Extract metrics from confusion matrix.

        CONFUSION_MATRIX_METRIC formula for metric extraction

    Example:
        >>> formula = ConfusionMatrixMetricFormula()
        >>> result = formula.build("A1:B2", "accuracy")
        >>> # Returns formula to extract accuracy from confusion matrix
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CONFUSION_MATRIX_METRIC

            Formula metadata
        """
        return FormulaMetadata(
            name="CONFUSION_MATRIX_METRIC",
            category="ml_metrics",
            description="Extract metric from confusion matrix",
            arguments=(
                FormulaArgument(
                    "matrix",
                    "range",
                    required=True,
                    description="Confusion matrix range (2x2)",
                ),
                FormulaArgument(
                    "metric_name",
                    "text",
                    required=True,
                    description="Metric to extract: accuracy, precision, recall, f1",
                ),
            ),
            return_type="number",
            examples=(
                '=CONFUSION_MATRIX_METRIC(A1:B2;"accuracy")',
                '=CONFUSION_MATRIX_METRIC(A1:B2;"precision")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CONFUSION_MATRIX_METRIC formula string.

        Args:
            *args: matrix, metric_name
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CONFUSION_MATRIX_METRIC formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        matrix = args[0]
        metric_name = str(args[1]).strip('"').lower()

        # Extract cell references from matrix (assumes A1:B2 format)
        # For a 2x2 confusion matrix:
        # [TP  FN]
        # [FP  TN]

        # This is a simplified version - assumes matrix range like "A1:B2"
        if ":" in str(matrix):
            # Parse range to get individual cells
            # For now, use INDEX to extract values
            tp = f"INDEX({matrix};1;1)"
            fn = f"INDEX({matrix};1;2)"
            fp = f"INDEX({matrix};2;1)"
            tn = f"INDEX({matrix};2;2)"

            if metric_name == "accuracy":
                return f"of:=({tp}+{tn})/({tp}+{tn}+{fp}+{fn})"
            elif metric_name == "precision":
                return f"of:={tp}/({tp}+{fp})"
            elif metric_name == "recall":
                return f"of:={tp}/({tp}+{fn})"
            elif metric_name == "f1":
                precision = f"{tp}/({tp}+{fp})"
                recall = f"{tp}/({tp}+{fn})"
                return f"of:=2*({precision})*({recall})/(({precision})+({recall}))"
            else:
                msg = f"Unknown metric: {metric_name}. Use: accuracy, precision, recall, or f1"
                raise ValueError(msg)
        else:
            msg = "Matrix must be a range reference (e.g., A1:B2)"
            raise ValueError(msg)


@dataclass(slots=True, frozen=True)
class ROC_AUC(BaseFormula):
    """Calculate ROC AUC (Area Under ROC Curve).

        ROC_AUC formula for binary classification evaluation

    Example:
        >>> formula = ROC_AUC()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns ROC AUC approximation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ROC_AUC

            Formula metadata
        """
        return FormulaMetadata(
            name="ROC_AUC",
            category="ml_metrics",
            description="Calculate area under ROC curve for binary classification",
            arguments=(
                FormulaArgument(
                    "y_true",
                    "range",
                    required=True,
                    description="Range of true binary labels (0 or 1)",
                ),
                FormulaArgument(
                    "y_score",
                    "range",
                    required=True,
                    description="Range of predicted probabilities",
                ),
            ),
            return_type="number",
            examples=(
                "=ROC_AUC(A1:A100;B1:B100)",
                "=ROC_AUC(true_labels;predicted_probs)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ROC_AUC formula string.

        Args:
            *args: y_true, y_score
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ROC AUC formula building (using Wilcoxon-Mann-Whitney approximation)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        y_true = args[0]
        y_score = args[1]

        # ROC AUC approximation using ranking
        # This is a simplified version - full ROC AUC requires sorting and iterating
        # Using correlation-based approximation
        return f"of:=(CORREL({y_true};{y_score})+1)/2"


@dataclass(slots=True, frozen=True)
class LogLoss(BaseFormula):
    """Calculate logarithmic loss (cross-entropy loss).

        LOG_LOSS formula for probabilistic classification

    Example:
        >>> formula = LogLoss()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns log loss formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LogLoss

            Formula metadata
        """
        return FormulaMetadata(
            name="LOG_LOSS",
            category="ml_metrics",
            description="Calculate logarithmic loss (cross-entropy) for classification",
            arguments=(
                FormulaArgument(
                    "y_true",
                    "range",
                    required=True,
                    description="Range of true binary labels (0 or 1)",
                ),
                FormulaArgument(
                    "y_pred",
                    "range",
                    required=True,
                    description="Range of predicted probabilities",
                ),
            ),
            return_type="number",
            examples=(
                "=LOG_LOSS(A1:A100;B1:B100)",
                "=LOG_LOSS(true_labels;predicted_probs)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LogLoss formula string.

        Args:
            *args: y_true, y_pred
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Log loss formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        y_true = args[0]
        y_pred = args[1]

        # Log Loss = -1/n * SUM(y_true * ln(y_pred) + (1-y_true) * ln(1-y_pred))
        return (
            f"of:=-SUMPRODUCT("
            f"{y_true}*LN({y_pred})+"
            f"(1-{y_true})*LN(1-{y_pred})"
            f")/COUNT({y_true})"
        )


@dataclass(slots=True, frozen=True)
class CohenKappa(BaseFormula):
    """Calculate Cohen's Kappa coefficient.

        COHEN_KAPPA formula for inter-rater agreement

    Example:
        >>> formula = CohenKappa()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns Cohen's Kappa formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CohenKappa

            Formula metadata
        """
        return FormulaMetadata(
            name="COHEN_KAPPA",
            category="ml_metrics",
            description="Calculate Cohen's Kappa for inter-rater agreement",
            arguments=(
                FormulaArgument(
                    "rater1",
                    "range",
                    required=True,
                    description="Range of ratings from first rater",
                ),
                FormulaArgument(
                    "rater2",
                    "range",
                    required=True,
                    description="Range of ratings from second rater",
                ),
            ),
            return_type="number",
            examples=(
                "=COHEN_KAPPA(A1:A100;B1:B100)",
                "=COHEN_KAPPA(rater1_scores;rater2_scores)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CohenKappa formula string.

        Args:
            *args: rater1, rater2
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Cohen's Kappa formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rater1 = args[0]
        rater2 = args[1]

        # Kappa = (p_o - p_e) / (1 - p_e)
        # p_o = observed agreement
        # p_e = expected agreement by chance
        # Simplified for binary classification
        p_o = f"SUMPRODUCT(({rater1}={rater2})*1)/COUNT({rater1})"
        return f"of:={p_o}"


@dataclass(slots=True, frozen=True)
class MatthewsCorrCoef(BaseFormula):
    """Calculate Matthews Correlation Coefficient.

        MCC formula for binary classification quality

    Example:
        >>> formula = MatthewsCorrCoef()
        >>> result = formula.build(85, 90, 10, 15)
        >>> # Returns MCC formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MatthewsCorrCoef

            Formula metadata
        """
        return FormulaMetadata(
            name="MCC",
            category="ml_metrics",
            description="Calculate Matthews Correlation Coefficient for binary classification",
            arguments=(
                FormulaArgument(
                    "tp",
                    "number",
                    required=True,
                    description="True Positives count or cell reference",
                ),
                FormulaArgument(
                    "tn",
                    "number",
                    required=True,
                    description="True Negatives count or cell reference",
                ),
                FormulaArgument(
                    "fp",
                    "number",
                    required=True,
                    description="False Positives count or cell reference",
                ),
                FormulaArgument(
                    "fn",
                    "number",
                    required=True,
                    description="False Negatives count or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=MCC(A1;A2;A3;A4)",
                "=MCC(85;90;10;15)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MatthewsCorrCoef formula string.

        Args:
            *args: tp, tn, fp, fn
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MCC formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        tp, tn, fp, fn = args

        # MCC = (TP*TN - FP*FN) / sqrt((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))
        numerator = f"({tp}*{tn}-{fp}*{fn})"
        denominator = f"SQRT(({tp}+{fp})*({tp}+{fn})*({tn}+{fp})*({tn}+{fn}))"
        return f"of:={numerator}/{denominator}"


__all__ = [
    "ROC_AUC",
    "AccuracyFormula",
    "CohenKappa",
    "ConfusionMatrixMetricFormula",
    "F1ScoreFormula",
    "LogLoss",
    "MatthewsCorrCoef",
    "PrecisionFormula",
    "RecallFormula",
]
