"""Progress indicators for long-running operations.

Provides progress bars, spinners, and batch progress tracking using the
rich library with NO_COLOR environment variable support.
"""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

# Try to import rich at runtime, but make it optional
try:
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskID,
        TextColumn,
        TimeElapsedColumn,
    )

    RICH_AVAILABLE = True
except ImportError:
    # Rich not available - mypy will see the imports above in try block
    RICH_AVAILABLE = False

    # Provide fallback types at runtime only
    if not TYPE_CHECKING:
        TaskID = Any  # type: ignore[misc, no-redef]
        Progress = Any  # type: ignore[misc, no-redef]
        SpinnerColumn = Any  # type: ignore[misc, no-redef]
        TextColumn = Any  # type: ignore[misc, no-redef]
        BarColumn = Any  # type: ignore[misc, no-redef]
        TimeElapsedColumn = Any  # type: ignore[misc, no-redef]

# Check NO_COLOR environment variable and TTY status
ENABLE_PROGRESS = os.getenv("NO_COLOR") != "1" and sys.stdout.isatty()


@contextmanager
def progress_bar(
    description: str,
    total: int | None = None,
) -> Iterator[TaskID | None]:
    """Context manager for progress bar.

    Args:
        description: Task description
        total: Total items (None for indeterminate)

    Yields:
        Progress task for updating (None if progress disabled)

    Example:
        >>> with progress_bar("Processing rows", total=100) as task:
        ...     for i in range(100):
        ...         # do work
        ...         if task:
        ...             progress.update(task, advance=1)
    """
    if not ENABLE_PROGRESS or not RICH_AVAILABLE:
        yield None  # No-op when NO_COLOR is set or rich not available
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(description, total=total or 100)
        yield task


@contextmanager
def spinner(description: str) -> Iterator[None]:
    """Show spinner for indeterminate operations.

    Args:
        description: Operation description

    Yields:
        None

    Example:
        >>> with spinner("Loading data..."):
        ...     # do work
        ...     pass
    """
    if not ENABLE_PROGRESS or not RICH_AVAILABLE:
        yield  # No-op when NO_COLOR is set or rich not available
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
    ) as progress:
        progress.add_task(description)
        yield


class BatchProgress:
    """Progress tracking for batch operations.

    Example:
        >>> with BatchProgress(100, "Processing items") as bp:
        ...     for i in range(100):
        ...         # do work
        ...         bp.update()
    """

    def __init__(self, total: int, description: str = "Processing") -> None:
        """Initialize batch progress tracker.

        Args:
            total: Total number of items
            description: Progress description
        """
        self.total = total
        self.description = description
        self.current = 0
        self._progress: Progress | None = None
        self._task: TaskID | None = None

    def __enter__(self) -> BatchProgress:
        """Context manager entry."""
        if ENABLE_PROGRESS and RICH_AVAILABLE:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeElapsedColumn(),
            )
            self._progress.__enter__()
            self._task = self._progress.add_task(self.description, total=self.total)
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        if self._progress is not None:
            self._progress.__exit__(*args)
            self._progress = None
            self._task = None

    def update(self, n: int = 1) -> None:
        """Update progress by n items.

        Args:
            n: Number of items completed (default: 1)
        """
        self.current += n
        if self._progress is not None and self._task is not None:
            self._progress.update(self._task, advance=n)

    def set_description(self, description: str) -> None:
        """Update the progress description.

        Args:
            description: New description
        """
        self.description = description
        if self._progress is not None and self._task is not None:
            self._progress.update(self._task, description=description)


def is_progress_enabled() -> bool:
    """Check if progress indicators are enabled.

    Returns:
        True if progress indicators will be displayed
    """
    return ENABLE_PROGRESS and RICH_AVAILABLE


def require_rich() -> None:
    """Raise ImportError if rich is not available.

    Raises:
        ImportError: If rich library is not installed
    """
    if not RICH_AVAILABLE:
        raise ImportError(
            "The 'rich' library is required for progress indicators. "
            "Install with: pip install rich>=13.0.0"
        )
