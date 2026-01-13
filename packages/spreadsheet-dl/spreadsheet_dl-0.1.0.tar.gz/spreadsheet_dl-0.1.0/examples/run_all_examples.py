#!/usr/bin/env python3
"""
Run All Examples Script

Executes all example scripts to verify they work correctly.
Useful for testing and validation.
"""

import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class ExampleResult(NamedTuple):
    """Result of running an example."""

    path: Path
    success: bool
    error: str | None = None


def run_example(example_path: Path) -> ExampleResult:
    """Run a single example script.

    Args:
        example_path: Path to the example script

    Returns:
        ExampleResult with success status
    """
    try:
        result = subprocess.run(
            ["uv", "run", "python", str(example_path)],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        if result.returncode == 0:
            return ExampleResult(path=example_path, success=True)
        else:
            return ExampleResult(
                path=example_path,
                success=False,
                error=result.stderr or result.stdout,
            )

    except subprocess.TimeoutExpired:
        return ExampleResult(
            path=example_path,
            success=False,
            error="Timeout (60s exceeded)",
        )
    except Exception as e:
        return ExampleResult(
            path=example_path,
            success=False,
            error=str(e),
        )


def main() -> int:
    """Run all examples and report results."""
    print("=" * 70)
    print("Running All SpreadsheetDL Examples")
    print("=" * 70)
    print()

    examples_dir = Path(__file__).parent

    # Find all example Python files (excluding this script)
    example_files = sorted(
        [
            f
            for f in examples_dir.rglob("*.py")
            if f.name != "run_all_examples.py"
            and "__pycache__" not in str(f)
            and f.name != "__init__.py"
        ]
    )

    if not example_files:
        print("No example files found!")
        return 1

    print(f"Found {len(example_files)} examples to run\n")

    results: list[ExampleResult] = []
    failed_count = 0

    for i, example_file in enumerate(example_files, 1):
        rel_path = example_file.relative_to(examples_dir)
        print(f"[{i}/{len(example_files)}] Running {rel_path}...", end=" ")
        sys.stdout.flush()

        result = run_example(example_file)
        results.append(result)

        if result.success:
            print("✓")
        else:
            print("✗")
            failed_count += 1

    # Print summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total examples: {len(results)}")
    print(f"Passed: {len(results) - failed_count}")
    print(f"Failed: {failed_count}")

    # Print failed examples with errors
    if failed_count > 0:
        print()
        print("Failed Examples:")
        print("-" * 70)
        for result in results:
            if not result.success:
                rel_path = result.path.relative_to(examples_dir)
                print(f"\n{rel_path}")
                if result.error:
                    # Print first few lines of error
                    error_lines = result.error.split("\n")[:10]
                    for line in error_lines:
                        print(f"  {line}")
                    if len(result.error.split("\n")) > 10:
                        print("  ...")

    print()
    print("=" * 70)

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
