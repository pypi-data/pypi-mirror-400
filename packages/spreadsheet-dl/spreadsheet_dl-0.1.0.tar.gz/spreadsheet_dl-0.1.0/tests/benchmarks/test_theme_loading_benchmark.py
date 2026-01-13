"""Benchmarks for theme loading performance.

Target: <50ms for 10 themes (from current ~200ms baseline)
Goal: 4x improvement through caching and lazy loading

    - PERF-THEME-001: Theme loading optimization
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_benchmark.fixture import BenchmarkFixture

pytestmark = [pytest.mark.benchmark, pytest.mark.requires_yaml]


class TestThemeLoadingBenchmarks:
    """Benchmark tests for theme loading performance."""

    def test_theme_parse_from_yaml(
        self,
        benchmark: BenchmarkFixture,
        tmp_path: Path,
    ) -> None:
        """
        Benchmark YAML theme parsing.

        Target: <50ms for 10 themes
        Current baseline: ~200ms

        Implements: PERF-THEME-001
        """
        # Create test theme YAML
        theme_yaml = """
meta:
  name: "benchmark_theme"
  version: "1.0"
  description: "Benchmark test theme"
  author: "Benchmark Suite"

colors:
  primary: "#0066CC"
  secondary: "#00CC66"
  accent: "#CC6600"
  text: "#333333"
  background: "#FFFFFF"
  border: "#CCCCCC"
  header: "#003366"
  success: "#00AA00"
  warning: "#FF9900"
  error: "#CC0000"

styles:
  default:
    font:
      name: "Liberation Sans"
      size: 11.0
      color: text
    fill: background

  header:
    font:
      name: "Liberation Sans"
      size: 12.0
      bold: true
      color: "#FFFFFF"
    fill: header
    border:
      top:
        style: thin
        color: border
      bottom:
        style: medium
        color: border

  highlight:
    font:
      bold: true
      color: primary
    fill: "#E6F2FF"

  currency:
    font:
      color: text
    number_format: "$#,##0.00"
    alignment:
      horizontal: right

  percentage:
    font:
      color: text
    number_format: "0.00%"
    alignment:
      horizontal: right

  date:
    number_format: "YYYY-MM-DD"
    alignment:
      horizontal: left
"""

        # Write theme files
        theme_dir = tmp_path / "themes"
        theme_dir.mkdir(exist_ok=True)

        for i in range(10):
            theme_path = theme_dir / f"theme_{i}.yaml"
            theme_path.write_text(theme_yaml.replace("benchmark_theme", f"theme_{i}"))

        # Benchmark: Load all themes
        def load_themes() -> int:
            from spreadsheet_dl.schema.loader import ThemeLoader

            loader = ThemeLoader(theme_dir)
            count = 0
            for i in range(10):
                theme = loader.load(f"theme_{i}")
                if theme:
                    count += 1
            return count

        result = benchmark(load_themes)
        assert result == 10

    def test_theme_cache_effectiveness(
        self,
        benchmark: BenchmarkFixture,
        tmp_path: Path,
    ) -> None:
        """
        Benchmark theme caching effectiveness.

        Tests repeated loading of same theme (should be fast with cache).
        """
        theme_yaml = """
meta:
  name: "cached_theme"
  version: "1.0"
  description: "Cached test theme"
  author: "Benchmark Suite"

colors:
  primary: "#0066CC"
  text: "#333333"

styles:
  default:
    font:
      size: 11.0
"""
        theme_dir = tmp_path / "themes"
        theme_dir.mkdir(exist_ok=True)
        (theme_dir / "cached.yaml").write_text(theme_yaml)

        # Benchmark: Load same theme 100 times
        def load_cached_theme() -> int:
            from spreadsheet_dl.schema.loader import ThemeLoader

            loader = ThemeLoader(theme_dir)
            count = 0
            for _ in range(100):
                theme = loader.load("cached")
                if theme:
                    count += 1
            return count

        result = benchmark(load_cached_theme)
        assert result == 100

    def test_theme_inheritance_resolution(
        self,
        benchmark: BenchmarkFixture,
        tmp_path: Path,
    ) -> None:
        """
        Benchmark theme inheritance resolution.

        Tests performance of loading themes with parent extends.
        """
        # Parent theme
        parent_yaml = """
meta:
  name: "parent"
  version: "1.0"
  description: "Parent test theme"
  author: "Benchmark Suite"

colors:
  primary: "#0066CC"
  text: "#333333"
  background: "#FFFFFF"

styles:
  default:
    font:
      size: 11.0
      color: text
"""

        # Child theme that extends parent
        child_yaml = """
meta:
  name: "child"
  version: "1.0"
  description: "Child test theme"
  author: "Benchmark Suite"

extends: parent

colors:
  accent: "#CC6600"

styles:
  highlight:
    font:
      bold: true
"""

        theme_dir = tmp_path / "themes"
        theme_dir.mkdir(exist_ok=True)
        (theme_dir / "parent.yaml").write_text(parent_yaml)
        (theme_dir / "child.yaml").write_text(child_yaml)

        # Benchmark: Load child theme with inheritance
        def load_with_inheritance() -> int:
            from spreadsheet_dl.schema.loader import ThemeLoader

            loader = ThemeLoader(theme_dir)
            count = 0
            for _ in range(50):
                theme = loader.load("child")
                if theme:
                    count += 1
            return count

        result = benchmark(load_with_inheritance)
        assert result == 50

    def test_color_reference_resolution(
        self,
        benchmark: BenchmarkFixture,
        tmp_path: Path,
    ) -> None:
        """
        Benchmark color reference resolution.

        Tests performance of resolving palette color references in styles.
        """
        theme_yaml = """
meta:
  name: "colors"
  version: "1.0"
  description: "Color test theme"
  author: "Benchmark Suite"

colors:
  primary: "#0066CC"
  secondary: "#00CC66"
  text: "#333333"
  background: "#FFFFFF"
  border: "#CCCCCC"

styles:
  style1:
    font:
      color: text
    fill: background
  style2:
    font:
      color: primary
    fill: "#E6F2FF"
  style3:
    font:
      color: secondary
    border:
      top:
        color: border
  style4:
    font:
      color: text
    fill: primary
  style5:
    font:
      color: "#FF0000"
    fill: secondary
"""

        theme_dir = tmp_path / "themes"
        theme_dir.mkdir(exist_ok=True)
        (theme_dir / "colors.yaml").write_text(theme_yaml)

        # Benchmark: Load theme with many color references
        def load_color_refs() -> int:
            from spreadsheet_dl.schema.loader import ThemeLoader

            loader = ThemeLoader(theme_dir)
            count = 0
            for _ in range(100):
                theme = loader.load("colors")
                if theme:
                    count += 1
            return count

        result = benchmark(load_color_refs)
        assert result == 100

    def test_complex_style_parsing(
        self,
        benchmark: BenchmarkFixture,
        tmp_path: Path,
    ) -> None:
        """
        Benchmark complex style definition parsing.

        Tests performance with all style properties defined.
        """
        theme_yaml = """
meta:
  name: "complex"
  version: "1.0"
  description: "Complex test theme"
  author: "Benchmark Suite"

colors:
  primary: "#0066CC"

styles:
  complex_style:
    font:
      name: "Liberation Sans"
      size: 12.0
      bold: true
      italic: true
      color: primary
      underline: single
    fill:
      type: pattern
      pattern: solid
      foreground_color: "#E6F2FF"
      background_color: "#FFFFFF"
    border:
      top:
        style: thin
        color: "#000000"
      right:
        style: thin
        color: "#000000"
      bottom:
        style: medium
        color: "#000000"
      left:
        style: thin
        color: "#000000"
    number_format: "#,##0.00"
    alignment:
      horizontal: center
      vertical: middle
      wrap_text: true
      indent: 1
"""

        theme_dir = tmp_path / "themes"
        theme_dir.mkdir(exist_ok=True)
        (theme_dir / "complex.yaml").write_text(theme_yaml)

        # Benchmark: Load complex theme
        def load_complex() -> int:
            from spreadsheet_dl.schema.loader import ThemeLoader

            loader = ThemeLoader(theme_dir)
            count = 0
            for _ in range(50):
                theme = loader.load("complex")
                if theme:
                    count += 1
            return count

        result = benchmark(load_complex)
        assert result == 50
