"""
Tests for progress indicators module.

Tests:
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from spreadsheet_dl import progress
from spreadsheet_dl.progress import (
    BatchProgress,
    is_progress_enabled,
    progress_bar,
    require_rich,
    spinner,
)

pytestmark = [pytest.mark.unit]


class TestProgressBar:
    """Test progress_bar context manager."""

    def test_progress_bar_with_total(self) -> None:
        """Test progress bar with total items."""
        # Progress is enabled if RICH_AVAILABLE and NO_COLOR not set
        with progress_bar("Test task", total=100) as task:
            # Should return None if progress disabled, or TaskID if enabled
            if progress.ENABLE_PROGRESS and progress.RICH_AVAILABLE:
                assert task is not None
            else:
                assert task is None

    def test_progress_bar_indeterminate(self) -> None:
        """Test progress bar without total (indeterminate)."""
        with progress_bar("Test task") as task:
            # Should work with or without rich
            if progress.ENABLE_PROGRESS and progress.RICH_AVAILABLE:
                assert task is not None
            else:
                assert task is None

    def test_progress_bar_with_no_color(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test progress bar respects NO_COLOR environment variable."""
        # Set NO_COLOR
        monkeypatch.setenv("NO_COLOR", "1")

        # Need to reload module to pick up env var
        import importlib

        importlib.reload(progress)

        with progress.progress_bar("Test task", total=100) as task:
            # Should be disabled with NO_COLOR
            assert task is None

        # Clean up
        monkeypatch.delenv("NO_COLOR")
        importlib.reload(progress)

    def test_progress_bar_non_tty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test progress bar disabled when not a TTY."""
        # Mock sys.stdout.isatty to return False
        mock_stdout = MagicMock()
        mock_stdout.isatty.return_value = False
        monkeypatch.setattr(sys, "stdout", mock_stdout)

        # Need to reload module to pick up TTY status
        import importlib

        importlib.reload(progress)

        with progress.progress_bar("Test task", total=100) as task:
            # Should be disabled when not a TTY
            assert task is None

        # Restore
        importlib.reload(progress)


class TestSpinner:
    """Test spinner context manager."""

    def test_spinner_basic(self) -> None:
        """Test spinner for indeterminate operations."""
        with spinner("Loading..."):
            # Should complete without error
            pass

    def test_spinner_with_no_color(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test spinner respects NO_COLOR."""
        monkeypatch.setenv("NO_COLOR", "1")

        import importlib

        importlib.reload(progress)

        with progress.spinner("Loading..."):
            # Should be no-op with NO_COLOR
            pass

        monkeypatch.delenv("NO_COLOR")
        importlib.reload(progress)


class TestBatchProgress:
    """Test BatchProgress class."""

    def test_batch_progress_basic(self) -> None:
        """Test basic batch progress tracking."""
        with BatchProgress(10, "Processing items") as bp:
            assert bp.total == 10
            assert bp.current == 0
            assert bp.description == "Processing items"

            # Update progress
            bp.update()
            assert bp.current == 1

            bp.update(5)
            assert bp.current == 6

    def test_batch_progress_with_updates(self) -> None:
        """Test batch progress with multiple updates."""
        total = 100
        with BatchProgress(total, "Test batch") as bp:
            for _ in range(total):
                bp.update()

            assert bp.current == total

    def test_batch_progress_set_description(self) -> None:
        """Test updating batch progress description."""
        with BatchProgress(10, "Initial") as bp:
            assert bp.description == "Initial"

            bp.set_description("Updated")
            assert bp.description == "Updated"

    def test_batch_progress_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test batch progress when disabled."""
        monkeypatch.setenv("NO_COLOR", "1")

        import importlib

        importlib.reload(progress)

        with progress.BatchProgress(10, "Test") as bp:
            # Should work but without rich progress
            bp.update()
            assert bp.current == 1

        monkeypatch.delenv("NO_COLOR")
        importlib.reload(progress)


class TestProgressHelpers:
    """Test helper functions."""

    def test_is_progress_enabled(self) -> None:
        """Test is_progress_enabled function."""
        enabled = is_progress_enabled()
        # Should match module state
        assert enabled == (progress.ENABLE_PROGRESS and progress.RICH_AVAILABLE)

    def test_is_progress_enabled_with_no_color(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test is_progress_enabled with NO_COLOR."""
        monkeypatch.setenv("NO_COLOR", "1")

        import importlib

        importlib.reload(progress)

        enabled = progress.is_progress_enabled()
        assert enabled is False

        monkeypatch.delenv("NO_COLOR")
        importlib.reload(progress)

    def test_require_rich_available(self) -> None:
        """Test require_rich when rich is available."""
        if progress.RICH_AVAILABLE:
            # Should not raise
            require_rich()
        else:
            # Should raise ImportError
            with pytest.raises(ImportError, match=r"rich.*required"):
                require_rich()

    def test_require_rich_unavailable(self) -> None:
        """Test require_rich when rich is not available."""
        # Mock RICH_AVAILABLE to False
        original = progress.RICH_AVAILABLE

        with (
            patch.object(progress, "RICH_AVAILABLE", False),
            pytest.raises(ImportError, match=r"rich.*required"),
        ):
            progress.require_rich()

        # Restore
        progress.RICH_AVAILABLE = original


class TestProgressIntegration:
    """Test progress indicators in realistic scenarios."""

    def test_large_batch_processing(self) -> None:
        """Test progress with a large batch operation."""
        items = list(range(150))

        with BatchProgress(len(items), "Processing large batch") as bp:
            for item in items:
                # Simulate work
                _ = item * 2
                bp.update()

            assert bp.current == len(items)

    def test_multiple_batches(self) -> None:
        """Test multiple sequential batch operations."""
        batches = [50, 75, 100]

        for batch_size in batches:
            with BatchProgress(batch_size, f"Batch of {batch_size}") as bp:
                for _ in range(batch_size):
                    bp.update()

                assert bp.current == batch_size

    def test_nested_progress_contexts(self) -> None:
        """Test that nested progress contexts work correctly."""
        # This tests that contexts don't interfere with each other
        with BatchProgress(10, "Outer") as outer:
            outer.update()

            with BatchProgress(5, "Inner") as inner:
                for _ in range(5):
                    inner.update()

                assert inner.current == 5

            outer.update()
            assert outer.current == 2

    def test_progress_with_errors(self) -> None:
        """Test that progress handles errors gracefully."""
        try:
            with BatchProgress(10, "Test with error") as bp:
                bp.update()
                raise ValueError("Test error")
        except ValueError:
            # Progress should clean up even on error
            pass


class TestProgressDisabled:
    """Test behavior when progress is disabled."""

    def test_progress_graceful_degradation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that all progress functions work even when disabled."""
        # Disable progress
        monkeypatch.setenv("NO_COLOR", "1")

        import importlib

        importlib.reload(progress)

        # All these should work without errors
        with progress.progress_bar("Test", total=10) as task:
            assert task is None

        with progress.spinner("Test"):
            pass

        with progress.BatchProgress(10, "Test") as bp:
            bp.update()
            bp.set_description("New")
            assert bp.current == 1

        assert progress.is_progress_enabled() is False

        # Cleanup
        monkeypatch.delenv("NO_COLOR")
        importlib.reload(progress)


class TestRichNotAvailable:
    """Test behavior when rich library is not available."""

    def test_all_functions_work_without_rich(self) -> None:
        """Test that progress functions work even if rich is not installed."""
        # Mock RICH_AVAILABLE to False
        original = progress.RICH_AVAILABLE

        with patch.object(progress, "RICH_AVAILABLE", False):
            # All these should work without errors, just no visual progress
            with progress_bar("Test", total=10) as task:
                assert task is None

            with spinner("Test"):
                pass

            with BatchProgress(10, "Test") as bp:
                bp.update()
                assert bp.current == 1

            assert is_progress_enabled() is False

            with pytest.raises(ImportError):
                require_rich()

        # Restore
        progress.RICH_AVAILABLE = original
