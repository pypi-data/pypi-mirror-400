"""Benchmarks for large spreadsheet rendering.

Target: <5 seconds for 10K rows (from current ~10s baseline)
Goal: 2x improvement through batching and optimization

    - PERF-RENDER-001: Large file rendering optimization
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.builder import SpreadsheetBuilder

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_benchmark.fixture import BenchmarkFixture


pytestmark = [pytest.mark.benchmark, pytest.mark.slow]


class TestRenderingBenchmarks:
    """Benchmark tests for ODS rendering performance."""

    def test_render_10k_rows_baseline(
        self,
        benchmark: BenchmarkFixture,
        large_dataset: list[dict[str, str | int | float]],
        tmp_path: Path,
    ) -> None:
        """
        Benchmark rendering 10,000 rows to ODS.

        Current baseline: ~10 seconds
        Target: <5 seconds (2x improvement)

        Implements: PERF-RENDER-001
        """

        def render_large_spreadsheet() -> Path:
            builder = SpreadsheetBuilder()
            builder.sheet("LargeData")

            # Add header row
            builder.row()
            builder.cells("ID", "Name", "Value", "Category", "Description")

            # Add data rows
            for item in large_dataset:
                builder.row()
                builder.cells(
                    item["id"],
                    item["name"],
                    item["value"],
                    item["category"],
                    item["description"],
                )

            output_path = tmp_path / "large_benchmark.ods"
            return builder.save(output_path)

        # Run benchmark
        result = benchmark(render_large_spreadsheet)
        assert result.exists()
        assert result.stat().st_size > 0

    def test_render_1k_rows_medium(
        self,
        benchmark: BenchmarkFixture,
        medium_dataset: list[dict[str, str | int | float]],
        tmp_path: Path,
    ) -> None:
        """
        Benchmark rendering 1,000 rows (medium file).

        Used to measure overhead vs data volume.
        """

        def render_medium_spreadsheet() -> Path:
            builder = SpreadsheetBuilder()
            builder.sheet("MediumData")

            # Add header
            builder.row()
            builder.cells("ID", "Name", "Value", "Category")

            # Add data
            for item in medium_dataset:
                builder.row()
                builder.cells(item["id"], item["name"], item["value"], item["category"])

            output_path = tmp_path / "medium_benchmark.ods"
            return builder.save(output_path)

        result = benchmark(render_medium_spreadsheet)
        assert result.exists()

    def test_render_with_styles(
        self,
        benchmark: BenchmarkFixture,
        medium_dataset: list[dict[str, str | int | float]],
        tmp_path: Path,
    ) -> None:
        """
        Benchmark rendering with cell styles applied.

        Tests style application overhead.
        """

        def render_with_styles() -> Path:
            builder = SpreadsheetBuilder()
            builder.sheet("StyledData")

            # Add styled header
            builder.row()
            builder.cells("ID", "Name", "Value", "Category", style="header")

            # Add data with alternating row styles
            for i, item in enumerate(medium_dataset):
                style = "row_even" if i % 2 == 0 else "row_odd"
                builder.row(style=style)
                builder.cells(item["id"], item["name"], item["value"], item["category"])

            output_path = tmp_path / "styled_benchmark.ods"
            return builder.save(output_path)

        result = benchmark(render_with_styles)
        assert result.exists()

    def test_render_multiple_sheets(
        self,
        benchmark: BenchmarkFixture,
        medium_dataset: list[dict[str, str | int | float]],
        tmp_path: Path,
    ) -> None:
        """
        Benchmark rendering multiple sheets.

        Tests multi-sheet overhead.
        """

        def render_multi_sheet() -> Path:
            builder = SpreadsheetBuilder()

            # Create 5 sheets with 1K rows each
            for sheet_num in range(5):
                builder.sheet(f"Sheet{sheet_num}")

                # Add header
                builder.row()
                builder.cells("ID", "Name", "Value")

                # Add data
                for item in medium_dataset:
                    builder.row()
                    builder.cells(item["id"], item["name"], item["value"])

            output_path = tmp_path / "multisheet_benchmark.ods"
            return builder.save(output_path)

        result = benchmark(render_multi_sheet)
        assert result.exists()

    def test_render_with_formulas(
        self,
        benchmark: BenchmarkFixture,
        tmp_path: Path,
    ) -> None:
        """
        Benchmark rendering with formulas.

        Tests formula generation overhead.
        """

        def render_with_formulas() -> Path:
            builder = SpreadsheetBuilder()
            builder.sheet("Formulas")

            # Add data rows
            for i in range(100):
                builder.row()
                builder.cell(i)
                builder.cell(i * 2)
                builder.cell(formula=f"=A{i + 1}+B{i + 1}")

            # Add summary row with aggregate formulas
            builder.row()
            builder.cell("Total")
            builder.cell(formula="=SUM(A1:A100)")
            builder.cell(formula="=SUM(C1:C100)")

            output_path = tmp_path / "formulas_benchmark.ods"
            return builder.save(output_path)

        result = benchmark(render_with_formulas)
        assert result.exists()
