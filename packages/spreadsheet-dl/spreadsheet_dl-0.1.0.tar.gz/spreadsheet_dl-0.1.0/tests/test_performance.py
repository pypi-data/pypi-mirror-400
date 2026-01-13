"""Tests for the performance module."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.performance import (
    BatchProcessor,
    Benchmark,
    FileCache,
    Lazy,
    LazyProperty,
    LRUCache,
    batch_process,
    cached,
    clear_cache,
    get_cache,
    timed,
)

if TYPE_CHECKING:
    from pathlib import Path

# =============================================================================
# LRUCache Tests
# =============================================================================


pytestmark = [pytest.mark.unit, pytest.mark.benchmark]


class TestLRUCache:
    """Tests for LRUCache."""

    def test_basic_operations(self) -> None:
        """Test basic get/set operations."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10)

        cache.set("a", 1)
        cache.set("b", 2)

        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.get("c") is None
        assert cache.get("c", default=99) == 99

    def test_maxsize_eviction(self) -> None:
        """Test LRU eviction when maxsize is reached."""
        cache: LRUCache[str, int] = LRUCache(maxsize=3)

        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # Should evict "a"

        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_lru_ordering(self) -> None:
        """Test that accessing moves item to end."""
        cache: LRUCache[str, int] = LRUCache(maxsize=3)

        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)

        # Access "a" to move it to end
        cache.get("a")

        # Now "b" should be evicted
        cache.set("d", 4)

        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_ttl_expiration(self) -> None:
        """Test TTL-based expiration."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10, ttl=0.1)

        cache.set("a", 1)
        assert cache.get("a") == 1

        # Wait for expiration
        time.sleep(0.15)

        assert cache.get("a") is None

    def test_delete(self) -> None:
        """Test delete operation."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10)

        cache.set("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") is None
        assert cache.delete("a") is False

    def test_clear(self) -> None:
        """Test clear operation."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10)

        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()

        assert len(cache) == 0
        assert cache.get("a") is None

    def test_contains(self) -> None:
        """Test contains check."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10)

        cache.set("a", 1)

        assert "a" in cache
        assert "b" not in cache

    def test_stats(self) -> None:
        """Test cache statistics."""
        cache: LRUCache[str, int] = LRUCache(maxsize=10)

        cache.set("a", 1)
        cache.get("a")  # Hit
        cache.get("a")  # Hit
        cache.get("b")  # Miss

        stats = cache.stats
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["size"] == 1
        assert stats["maxsize"] == 10
        assert stats["hit_rate"] == 2 / 3


# =============================================================================
# cached Decorator Tests
# =============================================================================


class TestCachedDecorator:
    """Tests for cached decorator."""

    def test_caches_results(self) -> None:
        """Test that results are cached."""
        call_count = 0

        @cached(maxsize=10)
        def expensive_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive_func(5) == 10
        assert expensive_func(5) == 10  # Cached
        assert expensive_func(5) == 10  # Cached

        assert call_count == 1

    def test_different_args(self) -> None:
        """Test that different args are cached separately."""
        call_count = 0

        @cached(maxsize=10)
        def func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        assert func(1) == 1
        assert func(2) == 2
        assert func(1) == 1  # Cached

        assert call_count == 2

    def test_cache_clear(self) -> None:
        """Test cache clearing."""
        call_count = 0

        @cached(maxsize=10)
        def func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        func(1)
        func.cache_clear()  # type: ignore[attr-defined]
        func(1)

        assert call_count == 2

    def test_custom_key_func(self) -> None:
        """Test custom key function."""

        @cached(key_func=lambda x, y: f"{x}:{y}")
        def func(x: int, y: int) -> int:
            return x + y

        assert func(1, 2) == 3
        assert func(1, 2) == 3


# =============================================================================
# Lazy Tests
# =============================================================================


class TestLazy:
    """Tests for Lazy evaluation."""

    def test_lazy_evaluation(self) -> None:
        """Test that factory is only called on access."""
        call_count = 0

        def factory() -> str:
            nonlocal call_count
            call_count += 1
            return "value"

        lazy = Lazy(factory)

        assert call_count == 0
        assert not lazy.is_loaded

        value = lazy.value

        assert value == "value"
        assert call_count == 1
        assert lazy.is_loaded

        # Second access doesn't call factory
        value2 = lazy.value
        assert value2 == "value"
        assert call_count == 1

    def test_reset(self) -> None:
        """Test reset functionality."""
        call_count = 0

        def factory() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        lazy = Lazy(factory)

        assert lazy.value == 1
        lazy.reset()
        assert lazy.value == 2

    def test_repr(self) -> None:
        """Test string representation."""
        lazy = Lazy(lambda: "test")

        assert "not loaded" in repr(lazy)

        _ = lazy.value  # Load it

        assert "test" in repr(lazy)


class TestLazyProperty:
    """Tests for LazyProperty descriptor."""

    def test_lazy_property(self) -> None:
        """Test lazy property evaluation."""
        call_count = 0

        class MyClass:
            @LazyProperty
            def data(self) -> str:
                nonlocal call_count
                call_count += 1
                return "computed"

        obj = MyClass()

        assert call_count == 0

        value = obj.data
        assert value == "computed"
        assert call_count == 1

        value2 = obj.data
        assert value2 == "computed"
        assert call_count == 1  # Not called again

    def test_per_instance_caching(self) -> None:
        """Test that each instance has its own cache."""
        call_count = 0

        class MyClass:
            @LazyProperty
            def data(self) -> int:
                nonlocal call_count
                call_count += 1
                return call_count

        obj1 = MyClass()
        obj2 = MyClass()

        assert obj1.data == 1
        assert obj2.data == 2
        assert obj1.data == 1  # Still cached


# =============================================================================
# BatchProcessor Tests
# =============================================================================


class TestBatchProcessor:
    """Tests for BatchProcessor."""

    def test_process_all(self) -> None:
        """Test basic batch processing."""
        items = list(range(10))
        processor: BatchProcessor[int] = BatchProcessor(lambda x: x * 2, batch_size=3)

        result = processor.process_all(items)

        assert result.success_count == 10
        assert result.error_count == 0
        assert result.items == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

    def test_error_handling_continue(self) -> None:
        """Test error handling with continue strategy."""

        def process(x: int) -> int:
            if x == 5:
                raise ValueError("Error on 5")
            return x

        processor = BatchProcessor(process, batch_size=10, on_error="continue")
        result = processor.process_all(list(range(10)))

        assert result.success_count == 9
        assert result.error_count == 1
        assert len(result.errors) == 1
        assert result.errors[0][0] == 5

    def test_error_handling_stop(self) -> None:
        """Test error handling with stop strategy."""

        def process(x: int) -> int:
            if x == 5:
                raise ValueError("Error on 5")
            return x

        processor = BatchProcessor(process, batch_size=10, on_error="stop")
        result = processor.process_all(list(range(10)))

        assert result.success_count == 5
        assert result.error_count == 1

    def test_progress_callback(self) -> None:
        """Test progress callback."""
        progress_calls: list[tuple[int, int]] = []

        def callback(processed: int, total: int) -> None:
            progress_calls.append((processed, total))

        items = list(range(10))
        processor = BatchProcessor(lambda x: x, batch_size=3)
        processor.process_all(items, progress_callback=callback)

        assert (3, 10) in progress_calls
        assert (6, 10) in progress_calls
        assert (9, 10) in progress_calls
        assert (10, 10) in progress_calls

    def test_process_batches_iterator(self) -> None:
        """Test batch-by-batch processing."""
        items = list(range(10))
        processor = BatchProcessor(lambda x: x, batch_size=3)

        batches = list(processor.process_batches(items))

        assert len(batches) == 4
        assert batches[0].success_count == 3
        assert batches[-1].success_count == 1


class TestBatchProcess:
    """Tests for batch_process convenience function."""

    def test_batch_process(self) -> None:
        """Test batch_process function."""
        result = batch_process(
            items=[1, 2, 3, 4, 5],
            processor=lambda x: x * 2,
            batch_size=2,
        )

        assert result.success_count == 5
        assert result.items == [2, 4, 6, 8, 10]


# =============================================================================
# Benchmark Tests
# =============================================================================


class TestBenchmark:
    """Tests for Benchmark utility."""

    def test_basic_benchmark(self) -> None:
        """Test basic benchmarking."""
        bench = Benchmark("test")

        def fast_func() -> None:
            pass

        result = bench.run(fast_func, iterations=10, warmup=2)

        assert result.name == "test"
        assert result.iterations == 10
        assert result.total_time_ms >= 0
        assert result.avg_time_ms >= 0
        assert result.min_time_ms >= 0
        assert result.max_time_ms >= 0
        assert result.ops_per_second > 0

    def test_compare(self) -> None:
        """Test comparing implementations."""
        bench = Benchmark()

        def slow() -> None:
            time.sleep(0.001)

        def fast() -> None:
            pass

        results = bench.compare(
            [("slow", slow), ("fast", fast)],
            iterations=5,
        )

        # Fast should be first (sorted by time)
        assert results[0].name == "fast"
        assert results[1].name == "slow"

    def test_format_results(self) -> None:
        """Test result formatting."""
        bench = Benchmark("test")
        result = bench.run(lambda: None, iterations=5)

        formatted = Benchmark.format_results([result])

        assert "test" in formatted
        assert "Iterations" in formatted

    def test_to_dict(self) -> None:
        """Test BenchmarkResult.to_dict()."""
        bench = Benchmark("test")
        result = bench.run(lambda: None, iterations=5)

        data = result.to_dict()

        assert data["name"] == "test"
        assert data["iterations"] == 5
        assert "avg_time_ms" in data


class TestTimedDecorator:
    """Tests for timed decorator."""

    def test_timed_decorator(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test timed decorator output."""

        @timed
        def my_func() -> int:
            return 42

        result = my_func()

        assert result == 42
        captured = capsys.readouterr()
        assert "my_func took" in captured.out
        assert "ms" in captured.out


# =============================================================================
# FileCache Tests
# =============================================================================


class TestFileCache:
    """Tests for FileCache."""

    def test_basic_operations(self, tmp_path: Path) -> None:
        """Test basic file cache operations."""
        cache = FileCache(tmp_path, ttl=3600)

        cache.set("key1", {"data": "value"})

        result = cache.get("key1")
        assert result == {"data": "value"}

        assert cache.get("nonexistent") is None
        assert cache.get("nonexistent", default="default") == "default"

    def test_delete(self, tmp_path: Path) -> None:
        """Test delete operation."""
        cache = FileCache(tmp_path)

        cache.set("key1", "value")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("key1") is False

    def test_clear(self, tmp_path: Path) -> None:
        """Test clear operation."""
        cache = FileCache(tmp_path)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        count = cache.clear()

        assert count == 2
        assert cache.get("key1") is None

    def test_ttl_expiration(self, tmp_path: Path) -> None:
        """Test TTL expiration."""
        cache = FileCache(tmp_path, ttl=0.1)

        cache.set("key1", "value")
        assert cache.get("key1") == "value"

        time.sleep(0.15)

        assert cache.get("key1") is None

    def test_cleanup_expired(self, tmp_path: Path) -> None:
        """Test cleanup of expired entries."""
        cache = FileCache(tmp_path, ttl=0.1)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        time.sleep(0.15)

        deleted = cache.cleanup_expired()
        assert deleted == 2


# =============================================================================
# Global Cache Tests
# =============================================================================


class TestGlobalCache:
    """Tests for global cache functions."""

    def test_get_cache(self) -> None:
        """Test getting global cache."""
        cache = get_cache()
        assert isinstance(cache, LRUCache)

        # Same instance returned
        cache2 = get_cache()
        assert cache is cache2

    def test_clear_cache(self) -> None:
        """Test clearing global cache."""
        cache = get_cache()
        cache.set("test", "value")

        clear_cache()

        # Should be empty after clear
        assert cache.get("test") is None
