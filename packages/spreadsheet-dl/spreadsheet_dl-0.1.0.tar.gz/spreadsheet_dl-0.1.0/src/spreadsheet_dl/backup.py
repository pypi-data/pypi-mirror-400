"""Backup and restore module for SpreadsheetDL.

Provides automated backup creation before destructive operations,
backup management with configurable retention, and restore functionality
with integrity verification.

Requirements implemented:
    - DR-STORE-002: Backup/Restore Functionality

Features:
    - Auto-backup before destructive operations
    - Configurable backup retention (default 30 days)
    - Manual backup triggers
    - Compressed backup files (gzip)
    - Restore from backup with validation
    - Backup integrity verification
"""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spreadsheet_dl.exceptions import (
    FileError,
    SpreadsheetDLError,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class BackupReason(Enum):
    """Reasons for creating a backup."""

    MANUAL = "manual"
    AUTO_BEFORE_EDIT = "auto_before_edit"
    AUTO_BEFORE_DELETE = "auto_before_delete"
    AUTO_BEFORE_IMPORT = "auto_before_import"
    AUTO_BEFORE_OVERWRITE = "auto_before_overwrite"
    SCHEDULED = "scheduled"


class BackupCompression(Enum):
    """Supported compression algorithms."""

    NONE = "none"
    GZIP = "gzip"


# Exception classes for backup module
class BackupError(SpreadsheetDLError):
    """Base exception for backup-related errors."""

    error_code = "FT-BAK-1100"


class BackupNotFoundError(BackupError):
    """Raised when a backup file is not found."""

    error_code = "FT-BAK-1101"

    def __init__(
        self,
        backup_path: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.backup_path = backup_path
        super().__init__(
            f"Backup not found: {backup_path}",
            suggestion="Check the backup directory or list available backups.",
            **kwargs,
        )


class BackupCorruptError(BackupError):
    """Raised when a backup file is corrupted."""

    error_code = "FT-BAK-1102"

    def __init__(
        self,
        backup_path: str,
        reason: str = "Integrity check failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        self.backup_path = backup_path
        self.reason = reason
        super().__init__(
            f"Backup corrupted: {backup_path}",
            details=reason,
            suggestion="The backup file may be damaged. Try an earlier backup.",
            **kwargs,
        )


class RestoreError(BackupError):
    """Raised when restore operation fails."""

    error_code = "FT-BAK-1103"

    def __init__(
        self,
        message: str = "Restore failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the instance."""
        super().__init__(
            message,
            suggestion="Check file permissions and disk space.",
            **kwargs,
        )


@dataclass
class BackupMetadata:
    """Metadata stored with backups."""

    version: str = "1.0"
    original_path: str = ""
    original_filename: str = ""
    backup_time: str = ""
    reason: str = BackupReason.MANUAL.value
    compression: str = BackupCompression.GZIP.value
    content_hash: str = ""  # SHA-256 of original content
    file_size: int = 0  # Original file size in bytes
    user: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize metadata to JSON."""
        return json.dumps(
            {
                "version": self.version,
                "original_path": self.original_path,
                "original_filename": self.original_filename,
                "backup_time": self.backup_time,
                "reason": self.reason,
                "compression": self.compression,
                "content_hash": self.content_hash,
                "file_size": self.file_size,
                "user": self.user,
                "extra": self.extra,
            },
            indent=2,
        )

    @classmethod
    def from_json(cls, json_str: str) -> BackupMetadata:
        """Deserialize metadata from JSON."""
        data = json.loads(json_str)
        return cls(
            version=data.get("version", "1.0"),
            original_path=data.get("original_path", ""),
            original_filename=data.get("original_filename", ""),
            backup_time=data.get("backup_time", ""),
            reason=data.get("reason", BackupReason.MANUAL.value),
            compression=data.get("compression", BackupCompression.GZIP.value),
            content_hash=data.get("content_hash", ""),
            file_size=data.get("file_size", 0),
            user=data.get("user", ""),
            extra=data.get("extra", {}),
        )

    @classmethod
    def from_file(cls, metadata_path: Path) -> BackupMetadata:
        """Load metadata from a JSON file."""
        with open(metadata_path) as f:
            return cls.from_json(f.read())


@dataclass
class BackupInfo:
    """Information about a backup file."""

    backup_path: Path
    metadata_path: Path
    metadata: BackupMetadata
    created: datetime

    def __repr__(self) -> str:
        """Return repr string."""
        return (
            f"BackupInfo(file={self.metadata.original_filename}, "
            f"created={self.created.isoformat()}, "
            f"reason={self.metadata.reason})"
        )


class BackupManager:
    """Manage backups for SpreadsheetDL files.

    Provides automatic and manual backup creation, retention management,
    and restore functionality with integrity verification.

    Example:
        >>> import tempfile
        >>> manager = BackupManager(backup_dir=tempfile.mkdtemp())
        >>> manager.backup_dir.exists()
        True
        >>> manager.retention_days
        30
    """

    DEFAULT_BACKUP_DIR = ".spreadsheet-dl-backups"
    DEFAULT_RETENTION_DAYS = 30
    METADATA_SUFFIX = ".meta.json"
    BACKUP_SUFFIX = ".bak"
    COMPRESSED_SUFFIX = ".gz"

    def __init__(
        self,
        backup_dir: Path | str | None = None,
        retention_days: int = DEFAULT_RETENTION_DAYS,
        compression: BackupCompression = BackupCompression.GZIP,
    ) -> None:
        """Initialize backup manager.

        Args:
            backup_dir: Directory for storing backups. If None, uses
                        ~/.spreadsheet-dl-backups/ or project-local directory.
            retention_days: Number of days to keep backups (default 30).
            compression: Compression algorithm to use.
        """
        if backup_dir is None:
            # Default to user's home directory backup location
            backup_dir = Path.home() / self.DEFAULT_BACKUP_DIR
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.compression = compression

        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        file_path: str | Path,
        reason: BackupReason = BackupReason.MANUAL,
        extra_metadata: dict[str, Any] | None = None,
    ) -> BackupInfo:
        """Create a backup of a file.

        Args:
            file_path: Path to the file to back up.
            reason: Reason for the backup.
            extra_metadata: Additional metadata to store with backup.

        Returns:
            BackupInfo with details about the created backup.

        Raises:
            FileError: If the source file doesn't exist or can't be read.
            BackupError: If backup creation fails.
        """
        import getpass

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileError(f"Cannot backup: file not found: {file_path}")

        if not file_path.is_file():
            raise FileError(f"Cannot backup: not a file: {file_path}")

        try:
            # Read original file and compute hash
            with open(file_path, "rb") as f:
                content = f.read()

            content_hash = hashlib.sha256(content).hexdigest()
            file_size = len(content)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            safe_filename = self._safe_filename(file_path.name)
            backup_name = f"{safe_filename}_{timestamp}{self.BACKUP_SUFFIX}"

            if self.compression == BackupCompression.GZIP:
                backup_name += self.COMPRESSED_SUFFIX

            backup_path = self.backup_dir / backup_name
            metadata_path = backup_path.with_suffix(
                backup_path.suffix + self.METADATA_SUFFIX
            )

            # Create backup (compressed or raw)
            if self.compression == BackupCompression.GZIP:
                with gzip.open(backup_path, "wb") as f:
                    f.write(content)
            else:
                with open(backup_path, "wb") as f:
                    f.write(content)

            # Create metadata
            metadata = BackupMetadata(
                original_path=str(file_path.absolute()),
                original_filename=file_path.name,
                backup_time=datetime.now().isoformat(),
                reason=reason.value,
                compression=self.compression.value,
                content_hash=content_hash,
                file_size=file_size,
                user=getpass.getuser(),
                extra=extra_metadata or {},
            )

            # Write metadata file
            with open(metadata_path, "w") as f:
                f.write(metadata.to_json())

            return BackupInfo(
                backup_path=backup_path,
                metadata_path=metadata_path,
                metadata=metadata,
                created=datetime.now(),
            )

        except SpreadsheetDLError:
            raise
        except (OSError, ValueError, gzip.BadGzipFile) as e:
            # OSError: File I/O errors, ValueError: JSON/encoding errors, gzip errors
            raise BackupError(f"Failed to create backup: {e}") from e

    def restore_backup(
        self,
        backup: BackupInfo | Path | str,
        target_path: Path | str | None = None,
        *,
        verify: bool = True,
        overwrite: bool = False,
    ) -> Path:
        """Restore a file from backup.

        Args:
            backup: BackupInfo object or path to backup file.
            target_path: Path to restore to. If None, uses original path.
            verify: Whether to verify integrity after restore.
            overwrite: Whether to overwrite existing file.

        Returns:
            Path to the restored file.

        Raises:
            BackupNotFoundError: If backup doesn't exist.
            BackupCorruptError: If backup is corrupted.
            RestoreError: If restore fails.
        """
        # Handle different input types
        if isinstance(backup, (str, Path)):
            backup_path = Path(backup)
            metadata_path = backup_path.with_suffix(
                backup_path.suffix + self.METADATA_SUFFIX
            )
            if metadata_path.exists():
                metadata = BackupMetadata.from_file(metadata_path)
            else:
                # Try to infer compression from filename
                compression = (
                    BackupCompression.GZIP
                    if backup_path.suffix == self.COMPRESSED_SUFFIX
                    else BackupCompression.NONE
                )
                metadata = BackupMetadata(compression=compression.value)
        else:
            backup_path = backup.backup_path
            metadata = backup.metadata

        if not backup_path.exists():
            raise BackupNotFoundError(str(backup_path))

        # Determine target path
        if target_path is None:
            if metadata.original_path:
                target_path = Path(metadata.original_path)
            else:
                raise RestoreError("No target path specified and original path unknown")
        else:
            target_path = Path(target_path)

        # Check if target exists
        if target_path.exists() and not overwrite:
            raise RestoreError(
                f"Target file already exists: {target_path}. Use overwrite=True to replace."
            )

        try:
            # Read backup content
            compression = BackupCompression(metadata.compression)
            if compression == BackupCompression.GZIP:
                with gzip.open(backup_path, "rb") as f:
                    content = f.read()
            else:
                with open(backup_path, "rb") as f:
                    content = f.read()

            # Verify integrity if requested
            if verify and metadata.content_hash:
                actual_hash = hashlib.sha256(content).hexdigest()
                if actual_hash != metadata.content_hash:
                    raise BackupCorruptError(
                        str(backup_path),
                        f"Hash mismatch: expected {metadata.content_hash[:16]}..., "
                        f"got {actual_hash[:16]}...",
                    )

            # Create parent directories if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Write restored file
            with open(target_path, "wb") as f:
                f.write(content)

            return target_path

        except SpreadsheetDLError:
            raise
        except (OSError, ValueError, gzip.BadGzipFile, KeyError) as e:
            # OSError: File I/O errors, ValueError: JSON/encoding, gzip errors, KeyError: metadata
            raise RestoreError(f"Failed to restore backup: {e}") from e

    def list_backups(
        self,
        file_path: str | Path | None = None,
        *,
        include_expired: bool = False,
    ) -> list[BackupInfo]:
        """List available backups.

        Args:
            file_path: Filter by original file path. If None, lists all backups.
            include_expired: Include backups older than retention period.

        Returns:
            List of BackupInfo objects, sorted by creation time (newest first).
        """
        backups: list[BackupInfo] = []
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        # Find all metadata files
        for metadata_path in self.backup_dir.glob(f"*{self.METADATA_SUFFIX}"):
            try:
                metadata = BackupMetadata.from_file(metadata_path)

                # Parse creation time
                backup_time = datetime.fromisoformat(metadata.backup_time)

                # Skip expired backups unless requested
                if not include_expired and backup_time < cutoff_date:
                    continue

                # Filter by file path if specified
                if file_path is not None:
                    file_path = Path(file_path)
                    if (
                        metadata.original_filename != file_path.name
                        and metadata.original_path != str(file_path.absolute())
                    ):
                        continue

                # Find the actual backup file
                possible_path = Path(
                    str(metadata_path).replace(self.METADATA_SUFFIX, "")
                )
                if possible_path.exists():
                    backup_path = possible_path
                else:
                    # Skip if backup file is missing
                    continue

                backups.append(
                    BackupInfo(
                        backup_path=backup_path,
                        metadata_path=metadata_path,
                        metadata=metadata,
                        created=backup_time,
                    )
                )

            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid metadata files
                continue

        # Sort by creation time, newest first
        backups.sort(key=lambda b: b.created, reverse=True)
        return backups

    def verify_backup(self, backup: BackupInfo | Path | str) -> dict[str, Any]:
        """Verify backup integrity.

        Args:
            backup: BackupInfo object or path to backup file.

        Returns:
            Dictionary with verification results:
            - valid: bool - Whether backup is valid
            - backup_path: str - Path to backup file
            - file_exists: bool - Whether backup file exists
            - metadata_exists: bool - Whether metadata file exists
            - hash_valid: bool - Whether content hash matches
            - size_valid: bool - Whether file size matches
            - issues: list[str] - List of any issues found
        """
        issues: list[str] = []

        # Handle different input types
        if isinstance(backup, (str, Path)):
            backup_path = Path(backup)
            metadata_path = backup_path.with_suffix(
                backup_path.suffix + self.METADATA_SUFFIX
            )
        else:
            backup_path = backup.backup_path
            metadata_path = backup.metadata_path

        result: dict[str, Any] = {
            "valid": True,
            "backup_path": str(backup_path),
            "file_exists": backup_path.exists(),
            "metadata_exists": metadata_path.exists(),
            "hash_valid": False,
            "size_valid": False,
            "issues": issues,
        }

        if not result["file_exists"]:
            issues.append(f"Backup file not found: {backup_path}")
            result["valid"] = False
            return result

        if not result["metadata_exists"]:
            issues.append(f"Metadata file not found: {metadata_path}")
            result["valid"] = False
            return result

        try:
            metadata = BackupMetadata.from_file(metadata_path)

            # Read and decompress backup
            compression = BackupCompression(metadata.compression)
            if compression == BackupCompression.GZIP:
                with gzip.open(backup_path, "rb") as f:
                    content = f.read()
            else:
                with open(backup_path, "rb") as f:
                    content = f.read()

            # Verify hash
            if metadata.content_hash:
                actual_hash = hashlib.sha256(content).hexdigest()
                result["hash_valid"] = actual_hash == metadata.content_hash
                if not result["hash_valid"]:
                    issues.append(
                        f"Hash mismatch: expected {metadata.content_hash[:16]}..., "
                        f"got {actual_hash[:16]}..."
                    )
                    result["valid"] = False
            else:
                result["hash_valid"] = True  # No hash to verify
                issues.append("No content hash in metadata (cannot verify integrity)")

            # Verify size
            if metadata.file_size:
                result["size_valid"] = len(content) == metadata.file_size
                if not result["size_valid"]:
                    issues.append(
                        f"Size mismatch: expected {metadata.file_size}, "
                        f"got {len(content)}"
                    )
                    result["valid"] = False
            else:
                result["size_valid"] = True  # No size to verify

        except gzip.BadGzipFile:
            issues.append("Backup file is not valid gzip data")
            result["valid"] = False
        except (OSError, ValueError, KeyError) as e:
            # OSError: File I/O, ValueError: JSON/hash, KeyError: metadata fields
            issues.append(f"Verification error: {e}")
            result["valid"] = False

        return result

    def cleanup_old_backups(
        self,
        days: int | None = None,
        *,
        dry_run: bool = False,
    ) -> list[BackupInfo]:
        """Remove backups older than the retention period.

        Args:
            days: Override retention days. If None, uses configured value.
            dry_run: If True, only report what would be deleted.

        Returns:
            List of BackupInfo objects that were (or would be) deleted.
        """
        if days is None:
            days = self.retention_days

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted: list[BackupInfo] = []

        for backup in self.list_backups(include_expired=True):
            if backup.created < cutoff_date:
                if not dry_run:
                    # Delete backup and metadata files
                    try:
                        backup.backup_path.unlink(missing_ok=True)
                        backup.metadata_path.unlink(missing_ok=True)
                    except OSError:
                        pass
                deleted.append(backup)

        return deleted

    def get_backup_stats(self) -> dict[str, Any]:
        """Get statistics about backups.

        Returns:
            Dictionary with backup statistics:
            - total_backups: int
            - total_size_bytes: int
            - oldest_backup: str (ISO date) or None
            - newest_backup: str (ISO date) or None
            - by_reason: dict[str, int]
            - by_file: dict[str, int]
        """
        backups = self.list_backups(include_expired=True)

        total_size = 0
        by_reason: dict[str, int] = {}
        by_file: dict[str, int] = {}

        for backup in backups:
            # Track size
            if backup.backup_path.exists():
                total_size += backup.backup_path.stat().st_size

            # Track by reason
            reason = backup.metadata.reason
            by_reason[reason] = by_reason.get(reason, 0) + 1

            # Track by file
            filename = backup.metadata.original_filename
            by_file[filename] = by_file.get(filename, 0) + 1

        oldest = backups[-1].created.isoformat() if backups else None
        newest = backups[0].created.isoformat() if backups else None

        return {
            "total_backups": len(backups),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_backup": oldest,
            "newest_backup": newest,
            "by_reason": by_reason,
            "by_file": by_file,
        }

    def _safe_filename(self, filename: str) -> str:
        """Convert filename to safe backup filename."""
        # Replace potentially problematic characters
        safe = filename.replace("/", "_").replace("\\", "_")
        safe = safe.replace(":", "_").replace(" ", "_")
        return safe


def auto_backup(
    file_path: str | Path,
    reason: BackupReason,
    backup_manager: BackupManager | None = None,
) -> BackupInfo | None:
    """Create an automatic backup of a file.

    Convenience function for creating backups before destructive operations.

    Args:
        file_path: Path to the file to back up.
        reason: Reason for the backup.
        backup_manager: Optional BackupManager to use.

    Returns:
        BackupInfo if backup was created, None if file doesn't exist.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None

    manager = backup_manager or BackupManager()
    return manager.create_backup(file_path, reason)


def backup_decorator(
    reason: BackupReason = BackupReason.AUTO_BEFORE_EDIT,
    file_arg: str = "file_path",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to automatically backup files before operations.

    Args:
        reason: Backup reason to use.
        file_arg: Name of the argument containing the file path.

    Returns:
        Decorator function.

    Example:
        @backup_decorator(BackupReason.AUTO_BEFORE_EDIT, file_arg="ods_file")
        def edit_budget(ods_file: Path, changes: dict) -> None:
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Try to get file path from kwargs or args
            import inspect

            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            file_path = None
            if file_arg in kwargs:
                file_path = kwargs[file_arg]
            elif file_arg in params:
                arg_index = params.index(file_arg)
                if arg_index < len(args):
                    file_path = args[arg_index]

            # Create backup if we found the file
            if file_path is not None:
                auto_backup(file_path, reason)

            return func(*args, **kwargs)

        return wrapper

    return decorator
