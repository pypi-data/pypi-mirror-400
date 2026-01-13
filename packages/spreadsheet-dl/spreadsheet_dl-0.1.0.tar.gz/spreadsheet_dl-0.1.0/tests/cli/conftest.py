"""CLI test fixtures and configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def mock_args() -> MagicMock:
    """Create a mock argparse.Namespace for CLI testing."""
    return MagicMock()


@pytest.fixture
def cli_test_file(tmp_path: Path) -> Path:
    """Create a test ODS file for CLI command testing."""
    test_file = tmp_path / "test_budget.ods"
    test_file.write_bytes(b"test")
    return test_file
