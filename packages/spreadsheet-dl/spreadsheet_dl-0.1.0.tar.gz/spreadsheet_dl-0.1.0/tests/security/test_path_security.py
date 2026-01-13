"""Tests for path security validation (path traversal prevention).

Tests the path_security module which prevents directory traversal attacks
and unauthorized file access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.path_security import (
    PathSecurityError,
    is_safe_path,
    safe_join,
    validate_path,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestPathValidation:
    """Test path validation security features."""

    def test_valid_relative_path(self, tmp_path: Path) -> None:
        """Test that valid relative paths are accepted."""
        base = tmp_path
        result = validate_path(base, "subdir/file.txt")
        assert result == base / "subdir/file.txt"

    def test_reject_parent_directory_traversal(self, tmp_path: Path) -> None:
        """Test that ../ path traversal is rejected."""
        base = tmp_path
        with pytest.raises(PathSecurityError, match="Path traversal detected"):
            validate_path(base, "../etc/passwd")

    def test_reject_absolute_path(self, tmp_path: Path) -> None:
        """Test that absolute paths are rejected."""
        base = tmp_path
        with pytest.raises(PathSecurityError, match="Absolute paths not allowed"):
            validate_path(base, "/etc/passwd")

    def test_reject_symlink_by_default(self, tmp_path: Path) -> None:
        """Test that symlinks are rejected by default."""
        base = tmp_path
        target = base / "target.txt"
        symlink = base / "link.txt"

        target.write_text("content")
        symlink.symlink_to(target)

        with pytest.raises(PathSecurityError, match="Symlink not allowed"):
            validate_path(base, "link.txt")

    def test_allow_symlink_when_enabled(self, tmp_path: Path) -> None:
        """Test that symlinks can be allowed explicitly."""
        base = tmp_path
        target = base / "target.txt"
        symlink = base / "link.txt"

        target.write_text("content")
        symlink.symlink_to(target)

        result = validate_path(base, "link.txt", allow_symlinks=True)
        assert result == symlink

    def test_nested_path_traversal(self, tmp_path: Path) -> None:
        """Test that nested ../  path traversal is detected."""
        base = tmp_path
        with pytest.raises(PathSecurityError):
            validate_path(base, "subdir/../../etc/passwd")

    def test_must_exist_validation(self, tmp_path: Path) -> None:
        """Test that must_exist parameter is enforced."""
        base = tmp_path
        with pytest.raises(FileNotFoundError):
            validate_path(base, "nonexistent.txt", must_exist=True)

    def test_must_exist_passes_for_existing_file(self, tmp_path: Path) -> None:
        """Test that must_exist passes for existing files."""
        base = tmp_path
        file_path = base / "existing.txt"
        file_path.write_text("content")

        result = validate_path(base, "existing.txt", must_exist=True)
        assert result == file_path


class TestSafeJoin:
    """Test safe_join helper function."""

    def test_safe_join_multiple_parts(self, tmp_path: Path) -> None:
        """Test joining multiple path components safely."""
        base = tmp_path
        result = safe_join(base, "sub1", "sub2", "file.txt")
        assert result == base / "sub1" / "sub2" / "file.txt"

    def test_safe_join_rejects_traversal(self, tmp_path: Path) -> None:
        """Test that safe_join rejects path traversal."""
        base = tmp_path
        with pytest.raises(PathSecurityError):
            safe_join(base, "..", "etc", "passwd")

    def test_safe_join_no_parts(self, tmp_path: Path) -> None:
        """Test safe_join with no path parts."""
        base = tmp_path
        result = safe_join(base)
        assert result == base.resolve()


class TestIsSafePath:
    """Test is_safe_path non-throwing validator."""

    def test_returns_true_for_safe_path(self, tmp_path: Path) -> None:
        """Test that safe paths return True."""
        base = tmp_path
        assert is_safe_path(base, "subdir/file.txt") is True

    def test_returns_false_for_unsafe_path(self, tmp_path: Path) -> None:
        """Test that unsafe paths return False."""
        base = tmp_path
        assert is_safe_path(base, "../etc/passwd") is False

    def test_returns_false_for_absolute_path(self, tmp_path: Path) -> None:
        """Test that absolute paths return False."""
        base = tmp_path
        assert is_safe_path(base, "/etc/passwd") is False

    def test_returns_false_for_symlink_by_default(self, tmp_path: Path) -> None:
        """Test that symlinks return False by default."""
        base = tmp_path
        target = base / "target.txt"
        symlink = base / "link.txt"

        target.write_text("content")
        symlink.symlink_to(target)

        assert is_safe_path(base, "link.txt") is False

    def test_returns_true_for_symlink_when_allowed(self, tmp_path: Path) -> None:
        """Test that symlinks return True when allowed."""
        base = tmp_path
        target = base / "target.txt"
        symlink = base / "link.txt"

        target.write_text("content")
        symlink.symlink_to(target)

        assert is_safe_path(base, "link.txt", allow_symlinks=True) is True


class TestPathSecurityIntegration:
    """Integration tests for path security."""

    def test_real_world_attack_scenarios(self, tmp_path: Path) -> None:
        """Test real-world path traversal attack patterns."""
        base = tmp_path

        # Common attack patterns that work cross-platform
        # Note: Backslashes and tildes are treated as literal characters on Unix
        attack_patterns = [
            "../../../etc/passwd",
            "subdir/../../../etc/shadow",
            "./../../etc/hosts",
            "../../../../../../etc/passwd",
            "./../.../../etc/hosts",
        ]

        for pattern in attack_patterns:
            with pytest.raises(PathSecurityError):
                validate_path(base, pattern)

    def test_case_sensitivity(self, tmp_path: Path) -> None:
        """Test that path validation is case-sensitive on Unix systems."""
        base = tmp_path

        # Create file
        file_path = base / "File.txt"
        file_path.write_text("content")

        # Exact case works
        result = validate_path(base, "File.txt")
        assert result == file_path

        # Different case should still validate (but may not exist)
        result2 = validate_path(base, "file.txt")  # No error, path is valid
        assert result2.name.lower() == "file.txt"
