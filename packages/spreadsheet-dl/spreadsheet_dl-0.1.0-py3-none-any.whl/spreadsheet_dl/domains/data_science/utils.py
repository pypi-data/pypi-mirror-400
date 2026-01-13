"""Utility functions for data science domain.

Helper utilities for data science domain
"""

from __future__ import annotations

from typing import Any


def format_scientific_notation(value: float, precision: int = 2) -> str:
    """Format number in scientific notation.

    Args:
        value: Number to format
        precision: Decimal places

    Returns:
        Scientific notation string

    Example:
        >>> format_scientific_notation(0.00012345, 2)
        '1.23e-04'
    """
    return f"{value:.{precision}e}"


def parse_scientific_notation(value: str) -> float:
    """Parse scientific notation string to float.

    Args:
        value: Scientific notation string

    Returns:
        Float value

    Raises:
        ValueError: If value cannot be parsed

    Example:
        >>> parse_scientific_notation("1.23e-04")  # doctest: +ELLIPSIS
        0.0001...
    """
    try:
        return float(value)
    except ValueError as e:
        msg = f"Invalid scientific notation: {value}"
        raise ValueError(msg) from e


def calculate_confusion_matrix_metrics(
    tp: int | float,
    tn: int | float,
    fp: int | float,
    fn: int | float,
) -> dict[str, float]:
    """Calculate all metrics from confusion matrix.

    Args:
        tp: True Positives
        tn: True Negatives
        fp: False Positives
        fn: False Negatives

    Returns:
        Dictionary with accuracy, precision, recall, f1

    Example:
        >>> metrics = calculate_confusion_matrix_metrics(85, 90, 10, 15)
        >>> print(metrics['accuracy'])
        0.875
    """
    total = tp + tn + fp + fn

    if total == 0:
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
        }

    accuracy = (tp + tn) / total

    # Precision: TP / (TP + FP)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    # Recall: TP / (TP + FN)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # F1: 2 * (P * R) / (P + R)
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def infer_data_type(value: Any) -> str:
    """Infer spreadsheet data type from Python value.

    Args:
        value: Python value

    Returns:
        Type string: "number", "text", "date", "boolean"

    Example:
        >>> infer_data_type(123)
        'number'
        >>> infer_data_type("hello")
        'text'
    """
    if isinstance(value, bool):
        return "boolean"
    elif isinstance(value, (int, float)):
        return "number"
    elif hasattr(value, "year") and hasattr(value, "month"):  # datetime-like
        return "date"
    else:
        return "text"


__all__ = [
    "calculate_confusion_matrix_metrics",
    "format_scientific_notation",
    "infer_data_type",
    "parse_scientific_notation",
]
