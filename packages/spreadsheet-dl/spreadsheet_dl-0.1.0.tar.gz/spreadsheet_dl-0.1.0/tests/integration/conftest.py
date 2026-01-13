"""Integration test fixtures and configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def integration_temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for integration tests."""
    integration_dir = tmp_path / "integration"
    integration_dir.mkdir(exist_ok=True)
    return integration_dir
