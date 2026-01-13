#!/usr/bin/env python3
"""
Demo script for progress indicators.

Shows progress bars, spinners, and batch progress in action.
"""

from __future__ import annotations

import time

from spreadsheet_dl.progress import BatchProgress, progress_bar, spinner


def demo_progress_bar() -> None:
    """Demo basic progress bar."""
    print("\n=== Progress Bar Demo ===")
    with progress_bar("Processing items", total=50) as task:
        if task is not None:
            # Progress is enabled - we can update it
            # (This won't run if NO_COLOR=1 or rich not available)
            pass
        # Simulate work
        for _ in range(50):
            time.sleep(0.02)


def demo_spinner() -> None:
    """Demo spinner for indeterminate operations."""
    print("\n=== Spinner Demo ===")
    with spinner("Loading data..."):
        time.sleep(2)
    print("Done!")


def demo_batch_progress() -> None:
    """Demo batch progress tracking."""
    print("\n=== Batch Progress Demo ===")
    items = list(range(100))

    with BatchProgress(len(items), "Processing batch") as bp:
        for item in items:
            # Simulate work
            _ = item * 2
            time.sleep(0.01)
            bp.update()


def demo_large_operation() -> None:
    """Demo progress with a larger operation."""
    print("\n=== Large Operation Demo ===")
    total = 200

    with BatchProgress(total, "Large operation") as bp:
        for i in range(total):
            # Simulate work
            time.sleep(0.005)
            bp.update()

            # Update description occasionally
            if i == 50:
                bp.set_description("Large operation (25% complete)")
            elif i == 100:
                bp.set_description("Large operation (50% complete)")
            elif i == 150:
                bp.set_description("Large operation (75% complete)")


def main() -> None:
    """Run all demos."""
    print("Progress Indicators Demo")
    print("=" * 50)
    print("\nNote: Set NO_COLOR=1 to disable progress indicators")
    print("      Progress is also disabled in non-TTY environments")

    demo_spinner()
    demo_progress_bar()
    demo_batch_progress()
    demo_large_operation()

    print("\n" + "=" * 50)
    print("Demo complete!")


if __name__ == "__main__":
    main()
