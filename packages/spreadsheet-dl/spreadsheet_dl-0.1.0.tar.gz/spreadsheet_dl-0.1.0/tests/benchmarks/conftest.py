"""Benchmark configuration and fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture
def benchmark_data_dir(tmp_path: Path) -> Iterator[Path]:
    """Create temporary directory for benchmark data."""
    data_dir = tmp_path / "benchmark_data"
    data_dir.mkdir(exist_ok=True)
    yield data_dir


@pytest.fixture
def large_dataset() -> list[dict[str, str | int | float]]:
    """Generate large dataset for benchmarking (10K rows)."""
    return [
        {
            "id": i,
            "name": f"Item {i}",
            "value": float(i * 1.5),
            "category": f"Category {i % 10}",
            "description": f"Description for item {i} with some text",
        }
        for i in range(10000)
    ]


@pytest.fixture
def medium_dataset() -> list[dict[str, str | int | float]]:
    """Generate medium dataset for benchmarking (1K rows)."""
    return [
        {
            "id": i,
            "name": f"Item {i}",
            "value": float(i * 1.5),
            "category": f"Category {i % 10}",
        }
        for i in range(1000)
    ]
