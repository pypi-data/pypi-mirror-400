"""Benchmarks for formula parsing performance.

Target: <100ms for 1000 formulas
Goal: Fast parsing through regex compilation and caching

    - PERF-FORMULA-001: Formula parsing optimization
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl._builder.formulas import FormulaBuilder

if TYPE_CHECKING:
    from pytest_benchmark.fixture import BenchmarkFixture

pytestmark = [pytest.mark.benchmark, pytest.mark.builder]


class TestFormulaParsingBenchmarks:
    """Benchmark tests for formula parsing performance."""

    def test_simple_formula_generation(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark simple formula generation.

        Target: <100ms for 1000 formulas
        Implements: PERF-FORMULA-001
        """

        def generate_formulas() -> list[str]:
            formulas = []
            for i in range(1000):
                fb = FormulaBuilder()
                # Simple addition formula
                formula = fb.sum(f"A{i}:A{i + 10}")
                formulas.append(formula)
            return formulas

        result = benchmark(generate_formulas)
        assert len(result) == 1000

    def test_complex_formula_generation(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark complex nested formula generation.

        Tests performance with function nesting.
        """

        def generate_complex_formulas() -> list[str]:
            formulas = []
            for i in range(100):
                fb = FormulaBuilder()
                # Nested formula: IF(SUM(A1:A10)>100, AVERAGE(B1:B10), MAX(C1:C10))
                formula = fb.if_expr(
                    condition=f"SUM(A{i}:A{i + 10})>100",
                    true_value=f"AVERAGE(B{i}:B{i + 10})",
                    false_value=f"MAX(C{i}:C{i + 10})",
                )
                formulas.append(formula)
            return formulas

        result = benchmark(generate_complex_formulas)
        assert len(result) == 100

    def test_cell_reference_parsing(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark cell reference parsing.

        Tests performance of parsing various cell reference formats.
        """

        def parse_references() -> int:
            fb = FormulaBuilder()
            count = 0

            # Mix of reference styles
            references = [
                "A1",
                "B10",
                "C100",
                "AA1",
                "AB10",
                "$A$1",
                "$B$10",
                "A$1",
                "$A1",
                "A1:B10",
                "$A$1:$B$10",
                "A:Z",
                "C:E",
                "$A:$Z",
            ]

            for _ in range(100):
                for ref in references:
                    # Just create formula with reference
                    formula = fb.sum(ref)
                    if formula:
                        count += 1

            return count

        result = benchmark(parse_references)
        assert result > 0

    def test_function_call_generation(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark formula function call generation.

        Tests common statistical and math functions.
        """

        def generate_function_calls() -> list[str]:
            formulas = []
            fb = FormulaBuilder()

            functions = [
                lambda: fb.sum("A1:A10"),
                lambda: fb.average("B1:B10"),
                lambda: fb.max("C1:C10"),
                lambda: fb.min("D1:D10"),
                lambda: fb.count("E1:E10"),
                lambda: fb.countif("F1:F10", ">5"),
                lambda: fb.sumif("G1:G10", ">100", "H1:H10"),
                lambda: fb.vlookup("H1", "Table!A1:C100", 2, exact=False),
                lambda: fb.round("I1", 2),
                lambda: fb.abs("J1"),
            ]

            for _ in range(100):
                for func in functions:
                    formula = func()  # type: ignore[no-untyped-call]
                    formulas.append(formula)

            return formulas

        result = benchmark(generate_function_calls)
        assert len(result) == 1000  # 100 iterations * 10 functions

    def test_range_expansion(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark range expansion for formulas.

        Tests performance of handling large cell ranges.
        """

        def expand_ranges() -> list[str]:
            formulas = []
            fb = FormulaBuilder()

            # Various range sizes
            for i in range(100):
                # Small range
                formulas.append(fb.sum(f"A{i}:A{i + 10}"))
                # Medium range
                formulas.append(fb.average(f"B{i}:B{i + 50}"))
                # Large range
                formulas.append(fb.max(f"C{i}:C{i + 100}"))
                # Multi-column range
                formulas.append(fb.sum(f"D{i}:F{i + 10}"))

            return formulas

        result = benchmark(expand_ranges)
        assert len(result) == 400

    def test_formula_string_building(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark raw formula string construction.

        Tests string manipulation performance.
        """

        def build_formula_strings() -> list[str]:
            formulas = []

            for i in range(1000):
                # Build formula string directly
                formula = f"=SUM(A{i}:A{i + 10})+AVERAGE(B{i}:B{i + 10})"
                formulas.append(formula)

            return formulas

        result = benchmark(build_formula_strings)
        assert len(result) == 1000

    def test_array_formula_generation(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark array formula generation.

        Tests performance with array formulas and multiple arguments.
        """

        def generate_array_formulas() -> list[str]:
            formulas = []
            fb = FormulaBuilder()

            for i in range(100):
                # Array formulas with multiple ranges
                formula = fb.sumproduct(f"A{i}:A{i + 10}", f"B{i}:B{i + 10}")
                formulas.append(formula)

                # Multiple calls to max (since it only takes one range)
                formula = fb.max(f"C{i}:C{i + 10}")
                formulas.append(formula)

            return formulas

        result = benchmark(generate_array_formulas)
        assert len(result) == 200

    def test_conditional_formula_generation(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark conditional formula generation.

        Tests IF, AND, OR, and nested conditionals.
        """

        def generate_conditional_formulas() -> list[str]:
            formulas = []
            fb = FormulaBuilder()

            for i in range(100):
                # Simple IF
                formulas.append(fb.if_expr(f"A{i}>10", "Yes", "No"))

                # Nested IF
                formulas.append(
                    fb.if_expr(
                        f"B{i}>100",
                        "High",
                        fb.if_expr(f"B{i}>50", "Medium", "Low"),
                    )
                )

                # IF with AND
                formulas.append(fb.if_expr(f"AND(C{i}>0,D{i}<100)", "Valid", "Invalid"))

            return formulas

        result = benchmark(generate_conditional_formulas)
        assert len(result) == 300

    def test_text_formula_generation(
        self,
        benchmark: BenchmarkFixture,
    ) -> None:
        """
        Benchmark text formula generation.

        Tests CONCATENATE, LEFT, RIGHT, MID, etc.
        """

        def generate_text_formulas() -> list[str]:
            formulas = []
            fb = FormulaBuilder()

            for i in range(100):
                # String concatenation
                formulas.append(fb.concatenate(f"A{i}", " - ", f"B{i}"))

                # Text extraction
                formulas.append(fb.left(f"C{i}", 5))
                formulas.append(fb.right(f"D{i}", 3))
                formulas.append(fb.mid(f"E{i}", 2, 4))

                # Text search
                formulas.append(fb.find("@", f"F{i}"))

            return formulas

        result = benchmark(generate_text_formulas)
        assert len(result) == 500
