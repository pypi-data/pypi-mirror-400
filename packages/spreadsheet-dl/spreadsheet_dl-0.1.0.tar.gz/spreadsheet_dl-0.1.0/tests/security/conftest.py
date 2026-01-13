"""Security test fixtures and configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def malicious_test_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for security test files."""
    security_dir = tmp_path / "security_tests"
    security_dir.mkdir(exist_ok=True)
    return security_dir


@pytest.fixture
def safe_test_dir(tmp_path: Path) -> Path:
    """Create a safe temporary directory that should be accessible."""
    safe_dir = tmp_path / "safe"
    safe_dir.mkdir(exist_ok=True)
    return safe_dir
