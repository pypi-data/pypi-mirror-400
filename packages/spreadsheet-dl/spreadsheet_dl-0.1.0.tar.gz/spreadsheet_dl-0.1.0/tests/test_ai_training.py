"""
Tests for AI training data export module.

: AI training data export (anonymized).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.ai_training import (
    AnonymizationConfig,
    AnonymizationLevel,
    AnonymizedTransaction,
    DataAnonymizer,
    PIIDetector,
    PIIPattern,
    TrainingDataExporter,
    TrainingDataFormat,
    TrainingDataset,
    TrainingDataStatistics,
)

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


class TestAnonymizationConfig:
    """Tests for AnonymizationConfig."""

    def test_default_level(self) -> None:
        """Test default anonymization level."""
        config = AnonymizationConfig()
        assert config.level == AnonymizationLevel.STANDARD

    def test_default_buckets(self) -> None:
        """Test default amount buckets."""
        config = AnonymizationConfig()
        assert 0 in config.amount_buckets
        assert 100 in config.amount_buckets
        assert 1000 in config.amount_buckets

    def test_default_pii_patterns(self) -> None:
        """Test default PII patterns are set."""
        config = AnonymizationConfig()

        pattern_names = [p.name for p in config.pii_patterns]
        assert "email" in pattern_names
        assert "phone" in pattern_names
        assert "credit_card" in pattern_names

    def test_hash_salt_generated(self) -> None:
        """Test hash salt is auto-generated."""
        config = AnonymizationConfig()
        assert config.hash_salt != ""
        assert len(config.hash_salt) > 0


class TestPIIDetector:
    """Tests for PIIDetector."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a test detector."""
        config = AnonymizationConfig()
        return PIIDetector(config)

    def test_detect_email(self, detector: PIIDetector) -> None:
        """Test email detection."""
        text = "Contact john.doe@example.com for info"
        findings = detector.detect_pii(text)

        assert len(findings) > 0
        assert any(f[0] == "email" for f in findings)
        assert any("john.doe@example.com" in f[1] for f in findings)

    def test_detect_phone(self, detector: PIIDetector) -> None:
        """Test phone number detection."""
        text = "Call me at 555-123-4567"
        findings = detector.detect_pii(text)

        assert len(findings) > 0
        assert any(f[0] == "phone" for f in findings)

    def test_detect_credit_card(self, detector: PIIDetector) -> None:
        """Test credit card detection."""
        text = "Card number 4111-1111-1111-1111"
        findings = detector.detect_pii(text)

        assert len(findings) > 0
        assert any(f[0] == "credit_card" for f in findings)

    def test_remove_pii(self, detector: PIIDetector) -> None:
        """Test PII removal."""
        text = "Email: test@example.com, Phone: 555-123-4567"
        clean = detector.remove_pii(text)

        assert "test@example.com" not in clean
        assert "555-123-4567" not in clean
        assert "[EMAIL]" in clean
        assert "[PHONE]" in clean

    def test_tokenize_description(self, detector: PIIDetector) -> None:
        """Test description tokenization."""
        description = "AMAZON PURCHASE 123456789"
        tokens = detector.tokenize_description(description)

        assert "amazon" in tokens
        assert "purchase" in tokens
        # Account number should be removed
        assert "123456789" not in tokens

    def test_no_pii_in_clean_text(self, detector: PIIDetector) -> None:
        """Test no false positives in clean text."""
        text = "Coffee at Starbucks"
        findings = detector.detect_pii(text)
        assert len(findings) == 0


class TestDataAnonymizer:
    """Tests for DataAnonymizer."""

    @pytest.fixture
    def anonymizer(self) -> DataAnonymizer:
        """Create a test anonymizer."""
        config = AnonymizationConfig(level=AnonymizationLevel.STANDARD)
        return DataAnonymizer(config)

    def test_anonymize_transaction(self, anonymizer: DataAnonymizer) -> None:
        """Test single transaction anonymization."""
        tx = {
            "date": "2024-01-15",
            "category": "Groceries",
            "description": "Whole Foods Market",
            "amount": 75.50,
        }

        result = anonymizer.anonymize_transaction(tx)

        assert isinstance(result, AnonymizedTransaction)
        assert result.id != ""
        assert result.category == "Groceries"
        assert result.amount_bucket == "50-100"

    def test_anonymize_transaction_buckets(self, anonymizer: DataAnonymizer) -> None:
        """Test amount bucketing."""
        test_cases = [
            (5.00, "0-10"),
            (15.00, "10-25"),
            (75.00, "50-100"),
            (500.00, "250-500"),
            (10000.00, "5000+"),
        ]

        for amount, expected_bucket in test_cases:
            tx = {
                "date": "2024-01-01",
                "category": "Test",
                "description": "Test",
                "amount": amount,
            }
            result = anonymizer.anonymize_transaction(tx)
            assert result.amount_bucket == expected_bucket, (
                f"Amount {amount} got bucket {result.amount_bucket}"
            )

    def test_anonymize_transaction_date_relative(
        self, anonymizer: DataAnonymizer
    ) -> None:
        """Test date anonymization to relative format."""
        tx = {
            "date": "2024-01-15",
            "category": "Test",
            "description": "Test",
            "amount": 50.00,
        }

        result = anonymizer.anonymize_transaction(tx)

        # Date should not be the original format
        assert result.date != "2024-01-15"
        assert result.date.startswith("day-")

    def test_anonymize_transaction_temporal_features(
        self, anonymizer: DataAnonymizer
    ) -> None:
        """Test temporal feature extraction."""
        # Monday, January 15, 2024
        tx = {
            "date": "2024-01-15",
            "category": "Test",
            "description": "Test",
            "amount": 50.00,
        }

        result = anonymizer.anonymize_transaction(tx)

        assert result.day_of_week == 0  # Monday
        assert result.day_of_month == 15
        assert result.month == 1
        assert result.is_weekend is False

    def test_anonymize_dataset(self, anonymizer: DataAnonymizer) -> None:
        """Test dataset anonymization."""
        transactions = [
            {
                "date": "2024-01-15",
                "category": "Groceries",
                "description": "Whole Foods",
                "amount": 75.00,
            },
            {
                "date": "2024-01-16",
                "category": "Transportation",
                "description": "Gas Station",
                "amount": 45.00,
            },
            {
                "date": "2024-01-17",
                "category": "Dining Out",
                "description": "Restaurant",
                "amount": 35.00,
            },
        ]

        dataset = anonymizer.anonymize_dataset(transactions)

        assert isinstance(dataset, TrainingDataset)
        assert len(dataset.records) == 3
        assert dataset.anonymization_level == "standard"

    def test_dataset_statistics(self, anonymizer: DataAnonymizer) -> None:
        """Test statistics computation."""
        transactions = [
            {"date": "2024-01-15", "category": "Groceries", "amount": 100.00},
            {"date": "2024-01-16", "category": "Groceries", "amount": 50.00},
            {"date": "2024-01-17", "category": "Transportation", "amount": 30.00},
        ]

        dataset = anonymizer.anonymize_dataset(transactions)

        assert dataset.statistics is not None
        assert dataset.statistics.total_records == 3
        assert "Groceries" in dataset.statistics.categories
        assert dataset.statistics.categories["Groceries"] == 2


class TestAnonymizationLevels:
    """Tests for different anonymization levels."""

    def test_minimal_level(self) -> None:
        """Test minimal anonymization."""
        config = AnonymizationConfig(level=AnonymizationLevel.MINIMAL)
        anonymizer = DataAnonymizer(config)

        tx = {
            "date": "2024-01-15",
            "category": "Groceries",
            "description": "Whole Foods Market",
            "amount": 75.50,
        }

        result = anonymizer.anonymize_transaction(tx)

        # Should have description tokens
        assert len(result.description_tokens) > 0
        # Should have normalized amount
        assert result.amount_normalized is not None

    def test_strict_level(self) -> None:
        """Test strict anonymization."""
        config = AnonymizationConfig(level=AnonymizationLevel.STRICT)
        anonymizer = DataAnonymizer(config)

        tx = {
            "date": "2024-01-15",
            "category": "Groceries",
            "description": "Whole Foods Market",
            "amount": 75.50,
        }

        result = anonymizer.anonymize_transaction(tx)

        # Should NOT have normalized amount in strict mode
        assert result.amount_normalized is None
        # Should NOT have description tokens
        assert len(result.description_tokens) == 0


class TestTrainingDataExporter:
    """Tests for TrainingDataExporter."""

    @pytest.fixture
    def exporter(self) -> TrainingDataExporter:
        """Create a test exporter."""
        config = AnonymizationConfig(level=AnonymizationLevel.STANDARD)
        return TrainingDataExporter(config)

    @pytest.fixture
    def sample_dataset(self) -> TrainingDataset:
        """Create a sample dataset."""
        records = [
            AnonymizedTransaction(
                id="tx_001",
                date="day-0",
                category="Groceries",
                amount_bucket="50-100",
                amount_normalized=0.075,
                day_of_week=1,
                day_of_month=15,
                month=1,
                is_weekend=False,
            ),
            AnonymizedTransaction(
                id="tx_002",
                date="day-1",
                category="Transportation",
                amount_bucket="25-50",
                amount_normalized=0.045,
                day_of_week=2,
                day_of_month=16,
                month=1,
                is_weekend=False,
            ),
        ]

        return TrainingDataset(
            anonymization_level="standard",
            records=records,
            statistics=TrainingDataStatistics(total_records=2),
        )

    def test_export_json(
        self,
        exporter: TrainingDataExporter,
        sample_dataset: TrainingDataset,
        tmp_path: Path,
    ) -> None:
        """Test JSON export."""
        output_path = tmp_path / "training_data.json"
        result = exporter.export_dataset(
            sample_dataset, output_path, TrainingDataFormat.JSON
        )

        assert result.exists()

        with open(result) as f:
            data = json.load(f)

        assert data["version"] == "1.0"
        assert data["record_count"] == 2
        assert len(data["records"]) == 2

    def test_export_jsonl(
        self,
        exporter: TrainingDataExporter,
        sample_dataset: TrainingDataset,
        tmp_path: Path,
    ) -> None:
        """Test JSONL export."""
        output_path = tmp_path / "training_data.jsonl"
        result = exporter.export_dataset(
            sample_dataset, output_path, TrainingDataFormat.JSONL
        )

        assert result.exists()

        with open(result) as f:
            lines = f.readlines()

        # Should have metadata + statistics + records
        assert len(lines) >= 2

        # First line should be metadata
        metadata = json.loads(lines[0])
        assert metadata["type"] == "metadata"

    def test_export_csv(
        self,
        exporter: TrainingDataExporter,
        sample_dataset: TrainingDataset,
        tmp_path: Path,
    ) -> None:
        """Test CSV export."""
        output_path = tmp_path / "training_data.csv"
        result = exporter.export_dataset(
            sample_dataset, output_path, TrainingDataFormat.CSV
        )

        assert result.exists()

        with open(result) as f:
            content = f.read()

        assert "id" in content
        assert "category" in content
        assert "amount_bucket" in content
        assert "tx_001" in content

    def test_stream_records(
        self, exporter: TrainingDataExporter, sample_dataset: TrainingDataset
    ) -> None:
        """Test record streaming."""
        records = list(exporter.stream_records(sample_dataset))

        assert len(records) == 2
        assert records[0]["id"] == "tx_001"
        assert records[1]["id"] == "tx_002"


class TestTrainingDataset:
    """Tests for TrainingDataset."""

    def test_to_dict(self) -> None:
        """Test dataset serialization."""
        records = [
            AnonymizedTransaction(
                id="tx_001",
                date="day-0",
                category="Test",
                amount_bucket="0-10",
            ),
        ]

        dataset = TrainingDataset(
            anonymization_level="standard",
            records=records,
        )

        data = dataset.to_dict()

        assert "version" in data
        assert "schema_version" in data
        assert "created_at" in data
        assert "record_count" in data
        assert data["record_count"] == 1


class TestAnonymizedTransaction:
    """Tests for AnonymizedTransaction."""

    def test_to_dict(self) -> None:
        """Test transaction serialization."""
        tx = AnonymizedTransaction(
            id="tx_001",
            date="day-5",
            category="Groceries",
            amount_bucket="50-100",
            amount_normalized=0.075,
            day_of_week=1,
            day_of_month=15,
            month=1,
            is_weekend=False,
            description_tokens=["whole", "foods"],
        )

        data = tx.to_dict()

        assert data["id"] == "tx_001"
        assert data["date"] == "day-5"
        assert data["category"] == "Groceries"
        assert data["amount_bucket"] == "50-100"
        assert data["amount_normalized"] == 0.075
        assert data["day_of_week"] == 1
        assert data["is_weekend"] is False
        assert data["description_tokens"] == ["whole", "foods"]

    def test_to_dict_minimal(self) -> None:
        """Test minimal transaction serialization."""
        tx = AnonymizedTransaction(
            id="tx_001",
            date="day-0",
            category="Test",
            amount_bucket="0-10",
        )

        data = tx.to_dict()

        # Should only include set fields
        assert "amount_normalized" not in data
        assert "description_tokens" not in data


class TestPIIPattern:
    """Tests for PIIPattern."""

    def test_compile(self) -> None:
        """Test pattern compilation."""
        pattern = PIIPattern(
            name="test",
            pattern=r"\d{4}",
            replacement="[REDACTED]",
        )

        compiled = pattern.compile()
        match = compiled.search("test 1234 test")

        assert match is not None
        assert match.group() == "1234"

    def test_case_insensitive(self) -> None:
        """Test case insensitive matching."""
        pattern = PIIPattern(
            name="test",
            pattern=r"secret",
            replacement="[SECRET]",
            flags=2,  # re.IGNORECASE
        )

        compiled = pattern.compile()
        assert compiled.search("SECRET") is not None
        assert compiled.search("Secret") is not None
        assert compiled.search("secret") is not None
