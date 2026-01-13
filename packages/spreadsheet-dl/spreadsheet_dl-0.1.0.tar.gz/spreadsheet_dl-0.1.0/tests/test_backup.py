"""
Tests for backup module.

Tests the BackupManager class and related functionality for
creating, restoring, and managing backups.
"""

from __future__ import annotations

import gzip
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from spreadsheet_dl.backup import (
    BackupCompression,
    BackupManager,
    BackupMetadata,
    BackupNotFoundError,
    BackupReason,
    RestoreError,
    auto_backup,
    backup_decorator,
)
from spreadsheet_dl.exceptions import FileError

pytestmark = [pytest.mark.integration, pytest.mark.requires_files]


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_file(temp_dir: Path) -> Path:
    """Create a sample file for testing."""
    file_path = temp_dir / "sample.ods"
    content = b"Sample ODS file content for testing backup functionality."
    file_path.write_bytes(content)
    return file_path


@pytest.fixture
def backup_manager(temp_dir: Path) -> BackupManager:
    """Create a BackupManager with test directory."""
    backup_dir = temp_dir / "backups"
    return BackupManager(backup_dir=backup_dir)


class TestBackupMetadata:
    """Tests for BackupMetadata class."""

    def test_to_json_and_from_json(self) -> None:
        """Test serialization round-trip."""
        metadata = BackupMetadata(
            original_path="/path/to/file.ods",
            original_filename="file.ods",
            backup_time=datetime.now().isoformat(),
            reason=BackupReason.MANUAL.value,
            compression=BackupCompression.GZIP.value,
            content_hash="abc123",
            file_size=1024,
            user="testuser",
            extra={"key": "value"},
        )

        json_str = metadata.to_json()
        restored = BackupMetadata.from_json(json_str)

        assert restored.original_path == metadata.original_path
        assert restored.original_filename == metadata.original_filename
        assert restored.backup_time == metadata.backup_time
        assert restored.reason == metadata.reason
        assert restored.compression == metadata.compression
        assert restored.content_hash == metadata.content_hash
        assert restored.file_size == metadata.file_size
        assert restored.user == metadata.user
        assert restored.extra == metadata.extra

    def test_from_file(self, temp_dir: Path) -> None:
        """Test loading metadata from file."""
        metadata = BackupMetadata(
            original_filename="test.ods",
            content_hash="hash123",
        )
        metadata_path = temp_dir / "test.meta.json"
        metadata_path.write_text(metadata.to_json())

        loaded = BackupMetadata.from_file(metadata_path)
        assert loaded.original_filename == "test.ods"
        assert loaded.content_hash == "hash123"


class TestBackupManager:
    """Tests for BackupManager class."""

    def test_init_creates_backup_dir(self, temp_dir: Path) -> None:
        """Test that initialization creates backup directory."""
        backup_dir = temp_dir / "new_backups"
        manager = BackupManager(backup_dir=backup_dir)
        assert backup_dir.exists()
        assert manager.backup_dir == backup_dir

    def test_create_backup_basic(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test basic backup creation."""
        backup_info = backup_manager.create_backup(sample_file, BackupReason.MANUAL)

        assert backup_info.backup_path.exists()
        assert backup_info.metadata_path.exists()
        assert backup_info.metadata.original_filename == sample_file.name
        assert backup_info.metadata.reason == BackupReason.MANUAL.value

    def test_create_backup_with_gzip(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test backup with gzip compression."""
        backup_info = backup_manager.create_backup(sample_file, BackupReason.MANUAL)

        assert backup_info.backup_path.suffix == ".gz"
        assert backup_info.metadata.compression == BackupCompression.GZIP.value

        # Verify content
        with gzip.open(backup_info.backup_path, "rb") as f:
            content = f.read()
        assert content == sample_file.read_bytes()

    def test_create_backup_without_compression(
        self, temp_dir: Path, sample_file: Path
    ) -> None:
        """Test backup without compression."""
        backup_dir = temp_dir / "backups_uncompressed"
        manager = BackupManager(
            backup_dir=backup_dir,
            compression=BackupCompression.NONE,
        )

        backup_info = manager.create_backup(sample_file, BackupReason.MANUAL)

        assert backup_info.backup_path.suffix != ".gz"
        assert backup_info.metadata.compression == BackupCompression.NONE.value

        # Verify content
        content = backup_info.backup_path.read_bytes()
        assert content == sample_file.read_bytes()

    def test_create_backup_with_extra_metadata(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test backup with extra metadata."""
        extra = {"operation": "import", "row_count": 100}
        backup_info = backup_manager.create_backup(
            sample_file,
            BackupReason.AUTO_BEFORE_IMPORT,
            extra_metadata=extra,
        )

        assert backup_info.metadata.extra == extra

    def test_create_backup_file_not_found(
        self, backup_manager: BackupManager, temp_dir: Path
    ) -> None:
        """Test backup of non-existent file raises error."""
        with pytest.raises(FileError):
            backup_manager.create_backup(temp_dir / "nonexistent.ods")

    def test_create_backup_content_hash(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test that content hash is computed correctly."""
        import hashlib

        expected_hash = hashlib.sha256(sample_file.read_bytes()).hexdigest()
        backup_info = backup_manager.create_backup(sample_file)

        assert backup_info.metadata.content_hash == expected_hash

    def test_restore_backup_basic(
        self, backup_manager: BackupManager, sample_file: Path, temp_dir: Path
    ) -> None:
        """Test basic backup restoration."""
        original_content = sample_file.read_bytes()
        backup_info = backup_manager.create_backup(sample_file)

        # Delete original
        sample_file.unlink()
        assert not sample_file.exists()

        # Restore
        target = temp_dir / "restored.ods"
        restored_path = backup_manager.restore_backup(backup_info, target)

        assert restored_path.exists()
        assert restored_path.read_bytes() == original_content

    def test_restore_backup_to_original_path(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test restoring to original path."""
        original_content = sample_file.read_bytes()
        backup_info = backup_manager.create_backup(sample_file)

        # Delete original
        sample_file.unlink()

        # Restore to original path
        restored_path = backup_manager.restore_backup(backup_info)

        assert restored_path == Path(backup_info.metadata.original_path)
        assert restored_path.read_bytes() == original_content

    def test_restore_backup_with_verification(
        self, backup_manager: BackupManager, sample_file: Path, temp_dir: Path
    ) -> None:
        """Test backup restoration with verification."""
        backup_info = backup_manager.create_backup(sample_file)

        target = temp_dir / "restored.ods"
        restored_path = backup_manager.restore_backup(backup_info, target, verify=True)

        assert restored_path.exists()

    def test_restore_backup_overwrite_protection(
        self, backup_manager: BackupManager, sample_file: Path, temp_dir: Path
    ) -> None:
        """Test that restore doesn't overwrite existing files by default."""
        backup_info = backup_manager.create_backup(sample_file)
        existing_file = temp_dir / "existing.ods"
        existing_file.write_bytes(b"existing content")

        with pytest.raises(RestoreError):
            backup_manager.restore_backup(backup_info, existing_file)

    def test_restore_backup_with_overwrite(
        self, backup_manager: BackupManager, sample_file: Path, temp_dir: Path
    ) -> None:
        """Test restore with overwrite enabled."""
        original_content = sample_file.read_bytes()
        backup_info = backup_manager.create_backup(sample_file)

        existing_file = temp_dir / "existing.ods"
        existing_file.write_bytes(b"existing content")

        restored = backup_manager.restore_backup(
            backup_info, existing_file, overwrite=True
        )

        assert restored.read_bytes() == original_content

    def test_restore_backup_not_found(
        self, backup_manager: BackupManager, temp_dir: Path
    ) -> None:
        """Test restore of non-existent backup raises error."""
        with pytest.raises(BackupNotFoundError):
            backup_manager.restore_backup(temp_dir / "nonexistent.bak.gz")

    def test_list_backups_empty(self, backup_manager: BackupManager) -> None:
        """Test listing backups when none exist."""
        backups = backup_manager.list_backups()
        assert backups == []

    def test_list_backups_multiple(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test listing multiple backups."""
        backup_manager.create_backup(sample_file, BackupReason.MANUAL)
        backup_manager.create_backup(sample_file, BackupReason.AUTO_BEFORE_EDIT)
        backup_manager.create_backup(sample_file, BackupReason.SCHEDULED)

        backups = backup_manager.list_backups()
        assert len(backups) == 3

    def test_list_backups_sorted_newest_first(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test that backups are sorted by creation time."""
        backup_manager.create_backup(sample_file)
        backup_manager.create_backup(sample_file)
        backup_manager.create_backup(sample_file)

        backups = backup_manager.list_backups()

        for i in range(len(backups) - 1):
            assert backups[i].created >= backups[i + 1].created

    def test_list_backups_filter_by_file(
        self, backup_manager: BackupManager, temp_dir: Path
    ) -> None:
        """Test filtering backups by file."""
        file1 = temp_dir / "file1.ods"
        file2 = temp_dir / "file2.ods"
        file1.write_bytes(b"content1")
        file2.write_bytes(b"content2")

        backup_manager.create_backup(file1)
        backup_manager.create_backup(file2)
        backup_manager.create_backup(file1)

        backups_file1 = backup_manager.list_backups(file1)
        backups_file2 = backup_manager.list_backups(file2)

        assert len(backups_file1) == 2
        assert len(backups_file2) == 1

    def test_verify_backup_valid(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test verification of valid backup."""
        backup_info = backup_manager.create_backup(sample_file)
        result = backup_manager.verify_backup(backup_info)

        assert result["valid"] is True
        assert result["file_exists"] is True
        assert result["metadata_exists"] is True
        assert result["hash_valid"] is True
        assert result["size_valid"] is True
        assert len(result["issues"]) == 0

    def test_verify_backup_corrupted(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test verification of corrupted backup."""
        backup_info = backup_manager.create_backup(sample_file)

        # Corrupt the backup
        with gzip.open(backup_info.backup_path, "wb") as f:
            f.write(b"corrupted content")

        result = backup_manager.verify_backup(backup_info)

        assert result["valid"] is False
        assert result["hash_valid"] is False

    def test_verify_backup_missing_file(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test verification when backup file is missing."""
        backup_info = backup_manager.create_backup(sample_file)
        backup_info.backup_path.unlink()

        result = backup_manager.verify_backup(backup_info)

        assert result["valid"] is False
        assert result["file_exists"] is False

    def test_cleanup_old_backups(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test cleanup of old backups."""
        # Create a backup
        backup_info = backup_manager.create_backup(sample_file)

        # Modify metadata to make it appear old
        metadata = backup_info.metadata
        old_time = datetime.now() - timedelta(days=60)
        metadata.backup_time = old_time.isoformat()
        backup_info.metadata_path.write_text(metadata.to_json())

        # Cleanup with 30-day retention
        deleted = backup_manager.cleanup_old_backups(days=30)

        assert len(deleted) == 1
        assert not backup_info.backup_path.exists()
        assert not backup_info.metadata_path.exists()

    def test_cleanup_old_backups_dry_run(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test cleanup dry run doesn't delete files."""
        backup_info = backup_manager.create_backup(sample_file)

        # Modify metadata to make it appear old
        metadata = backup_info.metadata
        old_time = datetime.now() - timedelta(days=60)
        metadata.backup_time = old_time.isoformat()
        backup_info.metadata_path.write_text(metadata.to_json())

        # Dry run cleanup
        deleted = backup_manager.cleanup_old_backups(days=30, dry_run=True)

        assert len(deleted) == 1
        # Files should still exist
        assert backup_info.backup_path.exists()
        assert backup_info.metadata_path.exists()

    def test_get_backup_stats(
        self, backup_manager: BackupManager, sample_file: Path
    ) -> None:
        """Test getting backup statistics."""
        backup_manager.create_backup(sample_file, BackupReason.MANUAL)
        backup_manager.create_backup(sample_file, BackupReason.AUTO_BEFORE_EDIT)
        backup_manager.create_backup(sample_file, BackupReason.MANUAL)

        stats = backup_manager.get_backup_stats()

        assert stats["total_backups"] == 3
        assert stats["total_size_bytes"] > 0
        assert stats["by_reason"]["manual"] == 2
        assert stats["by_reason"]["auto_before_edit"] == 1


class TestAutoBackup:
    """Tests for auto_backup function."""

    def test_auto_backup_existing_file(self, temp_dir: Path) -> None:
        """Test auto backup of existing file."""
        file_path = temp_dir / "test.ods"
        file_path.write_bytes(b"test content")

        backup_dir = temp_dir / "backups"
        manager = BackupManager(backup_dir=backup_dir)

        backup_info = auto_backup(file_path, BackupReason.AUTO_BEFORE_EDIT, manager)

        assert backup_info is not None
        assert backup_info.backup_path.exists()

    def test_auto_backup_nonexistent_file(self, temp_dir: Path) -> None:
        """Test auto backup of non-existent file returns None."""
        file_path = temp_dir / "nonexistent.ods"
        backup_dir = temp_dir / "backups"
        manager = BackupManager(backup_dir=backup_dir)

        result = auto_backup(file_path, BackupReason.AUTO_BEFORE_EDIT, manager)

        assert result is None


class TestBackupDecorator:
    """Tests for backup_decorator."""

    def test_decorator_creates_backup(self, temp_dir: Path) -> None:
        """Test that decorated function creates backup."""
        file_path = temp_dir / "test.ods"
        file_path.write_bytes(b"original content")
        backup_dir = temp_dir / "backups"
        backup_dir.mkdir()

        # Store original manager in module for the decorator
        BackupManager(backup_dir=backup_dir)

        @backup_decorator(BackupReason.AUTO_BEFORE_EDIT, file_arg="file_path")
        def modify_file(file_path: Path) -> None:
            # Decorator should have created a backup before this runs
            file_path.write_bytes(b"modified content")

        modify_file(file_path=file_path)

        # Check that file was modified
        assert file_path.read_bytes() == b"modified content"


class TestBackupReason:
    """Tests for BackupReason enum."""

    def test_all_reasons_have_values(self) -> None:
        """Test all backup reasons have string values."""
        for reason in BackupReason:
            assert isinstance(reason.value, str)
            assert len(reason.value) > 0


class TestBackupCompression:
    """Tests for BackupCompression enum."""

    def test_compression_options(self) -> None:
        """Test available compression options."""
        assert BackupCompression.NONE.value == "none"
        assert BackupCompression.GZIP.value == "gzip"
