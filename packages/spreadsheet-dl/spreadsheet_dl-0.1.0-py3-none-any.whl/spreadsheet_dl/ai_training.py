"""AI training data export with anonymization.

Provides functionality to export budget data in a format suitable for
AI/ML training while ensuring privacy through anonymization.

Requirements implemented:

Features:
    - PII detection and removal
    - Configurable anonymization levels
    - Statistical preservation
    - Multiple export formats (JSON, CSV, JSONL)
    - Data augmentation options
    - Schema versioning
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from spreadsheet_dl.exceptions import SpreadsheetDLError, ValidationError

if TYPE_CHECKING:
    from collections.abc import Iterator


class AnonymizationError(SpreadsheetDLError):
    """Raised when anonymization fails."""

    error_code = "FT-ANON-2000"


class AnonymizationLevel(Enum):
    """Levels of data anonymization."""

    NONE = "none"  # No anonymization (for testing only)
    MINIMAL = "minimal"  # Hash identifiers, keep amounts
    STANDARD = "standard"  # Generalize amounts, remove descriptions
    STRICT = "strict"  # Maximum anonymization, bucketize all values


class TrainingDataFormat(Enum):
    """Supported export formats for AI training data."""

    JSON = "json"
    JSONL = "jsonl"  # JSON Lines format
    CSV = "csv"
    PARQUET = "parquet"


@dataclass
class PIIPattern:
    """Pattern for detecting PII in text."""

    name: str
    pattern: str
    replacement: str
    flags: int = re.IGNORECASE

    def compile(self) -> re.Pattern[str]:
        """Compile the regex pattern.

        Note: Pattern is hardcoded or explicitly set by config, not user-provided.
        Safe from ReDoS as patterns are controlled by application developers.
        """
        return re.compile(self.pattern, self.flags)


@dataclass
class AnonymizationConfig:
    """Configuration for data anonymization.

    Attributes:
        level: Anonymization level to apply.
        hash_salt: Salt for hashing identifiers.
        amount_buckets: Bucket boundaries for amount generalization.
        preserve_categories: Whether to keep original category names.
        preserve_dates: Whether to keep exact dates vs. relative.
        add_noise_percent: Percentage of noise to add to amounts.
        include_statistics: Whether to include aggregate statistics.
        pii_patterns: Custom PII detection patterns.
    """

    level: AnonymizationLevel = AnonymizationLevel.STANDARD
    hash_salt: str = ""
    amount_buckets: list[float] = field(
        default_factory=lambda: [0, 10, 25, 50, 100, 250, 500, 1000, 5000]
    )
    preserve_categories: bool = True
    preserve_dates: bool = False
    add_noise_percent: float = 0.0
    include_statistics: bool = True
    pii_patterns: list[PIIPattern] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Set default PII patterns."""
        if not self.pii_patterns:
            self.pii_patterns = [
                PIIPattern(
                    "email",
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                    "[EMAIL]",
                ),
                PIIPattern(
                    "phone",
                    r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
                    "[PHONE]",
                ),
                PIIPattern(
                    "ssn",
                    r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
                    "[SSN]",
                ),
                PIIPattern(
                    "credit_card",
                    r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                    "[CARD]",
                ),
                PIIPattern(
                    "account_number",
                    r"\b\d{8,17}\b",
                    "[ACCOUNT]",
                ),
                PIIPattern(
                    "address",
                    r"\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|court|ct|circle|cir)\b",
                    "[ADDRESS]",
                ),
                PIIPattern(
                    "zip_code",
                    r"\b\d{5}(?:-\d{4})?\b",
                    "[ZIP]",
                ),
            ]

        # Generate random salt if not provided
        if not self.hash_salt:
            self.hash_salt = hashlib.sha256(
                str(datetime.now().timestamp()).encode()
            ).hexdigest()


@dataclass
class AnonymizedTransaction:
    """A transaction record with anonymized data."""

    id: str
    date: str
    category: str
    amount_bucket: str
    amount_normalized: float | None = None
    day_of_week: int | None = None
    day_of_month: int | None = None
    month: int | None = None
    is_weekend: bool | None = None
    description_tokens: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "id": self.id,
            "date": self.date,
            "category": self.category,
            "amount_bucket": self.amount_bucket,
        }

        if self.amount_normalized is not None:
            result["amount_normalized"] = self.amount_normalized

        if self.day_of_week is not None:
            result["day_of_week"] = self.day_of_week

        if self.day_of_month is not None:
            result["day_of_month"] = self.day_of_month

        if self.month is not None:
            result["month"] = self.month

        if self.is_weekend is not None:
            result["is_weekend"] = self.is_weekend

        if self.description_tokens:
            result["description_tokens"] = self.description_tokens

        return result


@dataclass
class TrainingDataStatistics:
    """Statistics about the training dataset."""

    total_records: int = 0
    categories: dict[str, int] = field(default_factory=dict)
    amount_distribution: dict[str, int] = field(default_factory=dict)
    date_range: tuple[str, str] | None = None
    monthly_totals: dict[str, float] = field(default_factory=dict)
    category_averages: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_records": self.total_records,
            "categories": self.categories,
            "amount_distribution": self.amount_distribution,
            "date_range": self.date_range,
            "monthly_totals": self.monthly_totals,
            "category_averages": self.category_averages,
        }


@dataclass
class TrainingDataset:
    """Container for anonymized training data."""

    version: str = "1.0"
    schema_version: str = "1.0"
    created_at: str = ""
    anonymization_level: str = ""
    records: list[AnonymizedTransaction] = field(default_factory=list)
    statistics: TrainingDataStatistics | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set creation timestamp."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "version": self.version,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "anonymization_level": self.anonymization_level,
            "record_count": len(self.records),
            "records": [r.to_dict() for r in self.records],
        }

        if self.statistics:
            result["statistics"] = self.statistics.to_dict()

        if self.metadata:
            result["metadata"] = self.metadata

        return result


class PIIDetector:
    """Detects and removes PII from text.

    Uses configurable patterns to identify and redact personal
    information from transaction descriptions and other text fields.
    """

    # Common merchant name variations to preserve
    SAFE_MERCHANTS: ClassVar[set[str]] = {
        "amazon",
        "walmart",
        "target",
        "costco",
        "starbucks",
        "mcdonalds",
        "uber",
        "lyft",
        "netflix",
        "spotify",
        "whole foods",
        "trader joes",
        "chipotle",
        "subway",
    }

    # Words that likely indicate PII
    PII_INDICATORS: ClassVar[set[str]] = {
        "account",
        "acct",
        "card",
        "member",
        "id",
        "number",
        "reference",
        "ref",
        "confirmation",
        "conf",
    }

    def __init__(self, config: AnonymizationConfig) -> None:
        """Initialize PII detector.

        Args:
            config: Anonymization configuration.
        """
        self.config = config
        self._compiled_patterns = [
            (p.name, p.compile(), p.replacement) for p in config.pii_patterns
        ]

    def detect_pii(self, text: str) -> list[tuple[str, str, int, int]]:
        """Detect PII in text.

        Args:
            text: Text to scan.

        Returns:
            List of (pattern_name, matched_text, start, end) tuples.
        """
        findings: list[tuple[str, str, int, int]] = []

        for name, pattern, _ in self._compiled_patterns:
            for match in pattern.finditer(text):
                findings.append((name, match.group(), match.start(), match.end()))

        return findings

    def remove_pii(self, text: str) -> str:
        """Remove PII from text.

        Args:
            text: Text to clean.

        Returns:
            Text with PII replaced by placeholders.
        """
        result = text

        for _, pattern, replacement in self._compiled_patterns:
            result = pattern.sub(replacement, result)

        return result

    def tokenize_description(self, description: str) -> list[str]:
        """Tokenize description into safe tokens.

        Removes PII and extracts meaningful, non-identifying tokens.

        Args:
            description: Transaction description.

        Returns:
            List of safe tokens.
        """
        # Remove PII first
        clean = self.remove_pii(description.lower())

        # Extract tokens
        tokens = re.findall(r"\b[a-z]{3,}\b", clean)

        # Filter out PII indicators
        safe_tokens = [t for t in tokens if t not in self.PII_INDICATORS]

        return safe_tokens[:5]  # Limit tokens


class DataAnonymizer:
    """Anonymizes financial data for AI training.

    Provides multiple anonymization levels and techniques to
    protect privacy while preserving statistical properties.

    Example:
        >>> config = AnonymizationConfig(level=AnonymizationLevel.STANDARD)
        >>> config.level == AnonymizationLevel.STANDARD
        True
        >>> anonymizer = DataAnonymizer(config)
        >>> anonymizer is not None
        True
        >>> anon_tx = anonymizer.anonymize_transaction(transaction)  # doctest: +SKIP
    """

    def __init__(self, config: AnonymizationConfig) -> None:
        """Initialize anonymizer.

        Args:
            config: Anonymization configuration.
        """
        self.config = config
        self.pii_detector = PIIDetector(config)
        self._reference_date: date | None = None

    def anonymize_transaction(
        self,
        tx: dict[str, Any],
        index: int = 0,
    ) -> AnonymizedTransaction:
        """Anonymize a single transaction.

        Args:
            tx: Transaction dictionary with date, category, description, amount.
            index: Transaction index for ID generation.

        Returns:
            AnonymizedTransaction with anonymized data.
        """
        # Generate anonymous ID
        tx_id = self._hash_id(f"{index}-{tx.get('date', '')}")

        # Handle date
        tx_date = tx.get("date")
        if isinstance(tx_date, str):
            tx_date = date.fromisoformat(tx_date)
        elif isinstance(tx_date, datetime):
            tx_date = tx_date.date()

        # Anonymize date based on config
        if self.config.preserve_dates:
            date_str = tx_date.isoformat() if tx_date else ""
        else:
            date_str = self._relative_date(tx_date) if tx_date else ""

        # Handle category
        category = tx.get("category", "Unknown")
        if not self.config.preserve_categories:
            category = self._generalize_category(category)

        # Handle amount
        amount = tx.get("amount", 0)
        if isinstance(amount, str):
            amount = float(amount.replace("$", "").replace(",", ""))
        amount = float(amount)

        # Add noise if configured
        if self.config.add_noise_percent > 0:
            noise = amount * (
                random.uniform(-1, 1) * self.config.add_noise_percent / 100
            )
            amount += noise

        # Bucket amount
        amount_bucket = self._bucketize_amount(amount)

        # Normalize amount (0-1 scale based on buckets)
        amount_normalized = None
        if self.config.level != AnonymizationLevel.STRICT:
            max_bucket = max(self.config.amount_buckets)
            amount_normalized = min(amount / max_bucket, 1.0) if max_bucket > 0 else 0

        # Extract temporal features
        day_of_week = tx_date.weekday() if tx_date else None
        day_of_month = tx_date.day if tx_date else None
        month = tx_date.month if tx_date else None
        is_weekend = day_of_week in (5, 6) if day_of_week is not None else None

        # Tokenize description
        description = tx.get("description", "")
        description_tokens: list[str] = []
        if self.config.level in (AnonymizationLevel.NONE, AnonymizationLevel.MINIMAL):
            description_tokens = self.pii_detector.tokenize_description(description)

        return AnonymizedTransaction(
            id=tx_id,
            date=date_str,
            category=category,
            amount_bucket=amount_bucket,
            amount_normalized=amount_normalized,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month=month,
            is_weekend=is_weekend,
            description_tokens=description_tokens,
        )

    def anonymize_dataset(
        self,
        transactions: list[dict[str, Any]],
    ) -> TrainingDataset:
        """Anonymize a dataset of transactions.

        Args:
            transactions: List of transaction dictionaries.

        Returns:
            TrainingDataset with anonymized records.
        """
        # Set reference date for relative dating
        if transactions:
            dates = [
                date.fromisoformat(tx["date"])
                if isinstance(tx.get("date"), str)
                else tx.get("date")
                for tx in transactions
                if tx.get("date")
            ]
            if dates:
                self._reference_date = min(d for d in dates if d)

        # Anonymize transactions
        records = [
            self.anonymize_transaction(tx, i) for i, tx in enumerate(transactions)
        ]

        # Compute statistics if configured
        statistics = None
        if self.config.include_statistics:
            statistics = self._compute_statistics(transactions, records)

        return TrainingDataset(
            anonymization_level=self.config.level.value,
            records=records,
            statistics=statistics,
            metadata={
                "anonymization_config": {
                    "level": self.config.level.value,
                    "preserve_categories": self.config.preserve_categories,
                    "preserve_dates": self.config.preserve_dates,
                    "noise_percent": self.config.add_noise_percent,
                },
            },
        )

    def _hash_id(self, value: str) -> str:
        """Generate a hashed identifier."""
        salted = f"{self.config.hash_salt}{value}"
        return hashlib.sha256(salted.encode()).hexdigest()[:12]

    def _relative_date(self, tx_date: date) -> str:
        """Convert date to relative format."""
        if self._reference_date is None:
            return f"day-{tx_date.timetuple().tm_yday}"

        delta = (tx_date - self._reference_date).days
        return f"day-{delta}"

    def _bucketize_amount(self, amount: float) -> str:
        """Put amount into a bucket range."""
        buckets = sorted(self.config.amount_buckets)

        for i, threshold in enumerate(buckets):
            if amount <= threshold:
                if i == 0:
                    return f"0-{threshold}"
                return f"{buckets[i - 1]}-{threshold}"

        # Above all buckets
        return f"{buckets[-1]}+"

    def _generalize_category(self, category: str) -> str:
        """Generalize category to broader group."""
        category_lower = category.lower()

        # Category groupings
        groups = {
            "food": ["groceries", "dining", "restaurant", "food", "coffee"],
            "transport": ["transportation", "gas", "uber", "lyft", "parking"],
            "housing": ["rent", "mortgage", "housing", "utilities"],
            "entertainment": ["entertainment", "streaming", "games", "movies"],
            "shopping": ["shopping", "clothing", "electronics", "amazon"],
            "health": ["healthcare", "pharmacy", "medical", "insurance"],
            "bills": ["utilities", "phone", "internet", "subscription"],
        }

        for group, keywords in groups.items():
            if any(kw in category_lower for kw in keywords):
                return group

        return "other"

    def _compute_statistics(
        self,
        original: list[dict[str, Any]],
        anonymized: list[AnonymizedTransaction],
    ) -> TrainingDataStatistics:
        """Compute aggregate statistics."""
        stats = TrainingDataStatistics(total_records=len(anonymized))

        # Category counts
        for record in anonymized:
            stats.categories[record.category] = (
                stats.categories.get(record.category, 0) + 1
            )

        # Amount distribution
        for record in anonymized:
            stats.amount_distribution[record.amount_bucket] = (
                stats.amount_distribution.get(record.amount_bucket, 0) + 1
            )

        # Date range (if dates preserved)
        if self.config.preserve_dates:
            dates = [r.date for r in anonymized if r.date]
            if dates:
                stats.date_range = (min(dates), max(dates))

        # Monthly totals and category averages from original data
        monthly: dict[str, float] = {}
        category_totals: dict[str, list[float]] = {}

        for tx in original:
            amount = float(tx.get("amount", 0))
            category = tx.get("category", "Unknown")

            # Monthly
            tx_date = tx.get("date")
            if tx_date:
                if isinstance(tx_date, str):
                    tx_date = date.fromisoformat(tx_date)
                month_key = f"{tx_date.year}-{tx_date.month:02d}"
                monthly[month_key] = monthly.get(month_key, 0) + amount

            # Category
            if category not in category_totals:
                category_totals[category] = []
            category_totals[category].append(amount)

        stats.monthly_totals = monthly
        stats.category_averages = {
            cat: sum(amounts) / len(amounts)
            for cat, amounts in category_totals.items()
            if amounts
        }

        return stats


class TrainingDataExporter:
    """Exports anonymized data in various formats for AI training.

    Supports JSON, JSONL, CSV, and Parquet formats with configurable
    compression and partitioning.

    Example:
        >>> exporter = TrainingDataExporter()  # doctest: +SKIP
        >>> exporter.export_json(dataset, Path("training_data.json"))  # doctest: +SKIP
    """

    def __init__(
        self,
        config: AnonymizationConfig | None = None,
    ) -> None:
        """Initialize exporter.

        Args:
            config: Anonymization configuration.
        """
        self.config = config or AnonymizationConfig()
        self.anonymizer = DataAnonymizer(self.config)

    def export_from_ods(
        self,
        ods_path: Path,
        output_path: Path,
        format: TrainingDataFormat = TrainingDataFormat.JSON,
    ) -> Path:
        """Export anonymized data from an ODS budget file.

        Args:
            ods_path: Path to ODS file.
            output_path: Output file path.
            format: Export format.

        Returns:
            Path to exported file.
        """
        from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

        # Load transactions from ODS
        analyzer = BudgetAnalyzer(ods_path)
        expenses = analyzer.expenses

        if expenses.empty:
            raise ValidationError("No transactions found in budget file")

        # Convert to dictionaries
        transactions = []
        for _, row in expenses.iterrows():
            transactions.append(
                {
                    "date": row.get("Date"),
                    "category": row.get("Category", "Unknown"),
                    "description": row.get("Description", ""),
                    "amount": row.get("Amount", 0),
                }
            )

        # Anonymize
        dataset = self.anonymizer.anonymize_dataset(transactions)

        # Export
        return self._export_dataset(dataset, output_path, format)

    def export_dataset(
        self,
        dataset: TrainingDataset,
        output_path: Path,
        format: TrainingDataFormat = TrainingDataFormat.JSON,
    ) -> Path:
        """Export a training dataset to file.

        Args:
            dataset: Anonymized training dataset.
            output_path: Output file path.
            format: Export format.

        Returns:
            Path to exported file.
        """
        return self._export_dataset(dataset, output_path, format)

    def _export_dataset(
        self,
        dataset: TrainingDataset,
        output_path: Path,
        format: TrainingDataFormat,
    ) -> Path:
        """Export dataset to specified format."""
        output_path = Path(output_path)

        if format == TrainingDataFormat.JSON:
            return self._export_json(dataset, output_path)
        elif format == TrainingDataFormat.JSONL:
            return self._export_jsonl(dataset, output_path)
        elif format == TrainingDataFormat.CSV:
            return self._export_csv(dataset, output_path)
        elif format == TrainingDataFormat.PARQUET:
            return self._export_parquet(dataset, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json(
        self,
        dataset: TrainingDataset,
        output_path: Path,
    ) -> Path:
        """Export to JSON format."""
        with open(output_path, "w") as f:
            json.dump(dataset.to_dict(), f, indent=2, default=str)
        return output_path

    def _export_jsonl(
        self,
        dataset: TrainingDataset,
        output_path: Path,
    ) -> Path:
        """Export to JSON Lines format."""
        with open(output_path, "w") as f:
            # Write metadata line
            f.write(
                json.dumps(
                    {
                        "type": "metadata",
                        "version": dataset.version,
                        "schema_version": dataset.schema_version,
                        "created_at": dataset.created_at,
                        "anonymization_level": dataset.anonymization_level,
                        "record_count": len(dataset.records),
                    }
                )
                + "\n"
            )

            # Write statistics line
            if dataset.statistics:
                f.write(
                    json.dumps(
                        {
                            "type": "statistics",
                            **dataset.statistics.to_dict(),
                        },
                        default=str,
                    )
                    + "\n"
                )

            # Write records
            for record in dataset.records:
                f.write(
                    json.dumps(
                        {
                            "type": "record",
                            **record.to_dict(),
                        }
                    )
                    + "\n"
                )

        return output_path

    def _export_csv(
        self,
        dataset: TrainingDataset,
        output_path: Path,
    ) -> Path:
        """Export to CSV format."""
        if not dataset.records:
            raise ValidationError("No records to export")

        # Get all fields from first record
        sample = dataset.records[0].to_dict()
        fieldnames = list(sample.keys())

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for record in dataset.records:
                row = record.to_dict()
                # Convert lists to strings for CSV
                for key, value in row.items():
                    if isinstance(value, list):
                        row[key] = ";".join(str(v) for v in value)
                writer.writerow(row)

        return output_path

    def _export_parquet(
        self,
        dataset: TrainingDataset,
        output_path: Path,
    ) -> Path:
        """Export to Parquet format."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas required for Parquet export. "
                "Install with: pip install pandas pyarrow"
            ) from exc

        # Convert to DataFrame
        records = [r.to_dict() for r in dataset.records]
        df = pd.DataFrame(records)

        # Save to Parquet
        df.to_parquet(output_path, index=False)

        return output_path

    def stream_records(
        self,
        dataset: TrainingDataset,
    ) -> Iterator[dict[str, Any]]:
        """Stream records for processing.

        Args:
            dataset: Training dataset.

        Yields:
            Record dictionaries.
        """
        for record in dataset.records:
            yield record.to_dict()


def export_training_data(
    ods_path: str | Path,
    output_path: str | Path,
    *,
    level: str = "standard",
    format: str = "json",
) -> Path:
    """Convenience function to export anonymized training data.

    Args:
        ods_path: Path to ODS budget file.
        output_path: Output file path.
        level: Anonymization level (none, minimal, standard, strict).
        format: Export format (json, jsonl, csv, parquet).

    Returns:
        Path to exported file.
    """
    config = AnonymizationConfig(
        level=AnonymizationLevel(level.lower()),
    )

    exporter = TrainingDataExporter(config)
    return exporter.export_from_ods(
        Path(ods_path),
        Path(output_path),
        TrainingDataFormat(format.lower()),
    )
