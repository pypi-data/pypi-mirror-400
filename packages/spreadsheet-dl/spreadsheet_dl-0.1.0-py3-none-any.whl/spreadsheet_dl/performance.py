"""Performance optimization module.

Provides:
    - Caching layer for frequently accessed data
    - Lazy loading for expensive operations
    - Batch processing for bulk operations
    - Performance benchmarking utilities
"""

from __future__ import annotations

import functools
import hashlib
import json
import threading
import time
import weakref
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# =============================================================================
# Caching Layer
# =============================================================================


class LRUCache[K, V]:
    """Thread-safe Least Recently Used (LRU) cache.

    Implements Caching layer for frequently accessed data.

    Example:
        cache = LRUCache(maxsize=100)
        cache.set("key", "value")
        value = cache.get("key")

        # With TTL
        cache = LRUCache(maxsize=100, ttl=3600)  # 1 hour
    """

    def __init__(
        self,
        maxsize: int = 128,
        ttl: float | None = None,
    ) -> None:
        """Initialize LRU cache.

        Args:
            maxsize: Maximum number of items to cache
            ttl: Time-to-live in seconds (None for no expiration)
        """
        self._maxsize = maxsize
        self._ttl = ttl
        self._cache: OrderedDict[K, tuple[V, float]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get a value from the cache.

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default

            value, timestamp = self._cache[key]

            # Check TTL
            if self._ttl is not None and time.time() - timestamp > self._ttl:
                del self._cache[key]
                self._misses += 1
                return default

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: K, value: V) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            if key in self._cache:
                # Update existing
                self._cache.move_to_end(key)
            elif len(self._cache) >= self._maxsize:
                # Remove oldest
                self._cache.popitem(last=False)

            self._cache[key] = (value, time.time())

    def delete(self, key: K) -> bool:
        """Delete a key from the cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def __contains__(self, key: K) -> bool:
        """Check if key is in cache."""
        with self._lock:
            if key not in self._cache:
                return False
            if self._ttl is not None:
                _, timestamp = self._cache[key]
                if time.time() - timestamp > self._ttl:
                    return False
            return True

    def __len__(self) -> int:
        """Return number of cached items."""
        return len(self._cache)

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "size": len(self._cache),
                "maxsize": self._maxsize,
            }


def cached(
    maxsize: int = 128,
    ttl: float | None = None,
    key_func: Callable[..., str] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for caching function results.

    Example:
        @cached(maxsize=100, ttl=3600)
        def expensive_operation(param):
            # ... expensive work ...
            return result

        # Custom key function
        @cached(key_func=lambda x, y: f"{x}:{y}")
        def another_function(x, y):
            return x + y
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: LRUCache[str, T] = LRUCache(maxsize=maxsize, ttl=ttl)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = _make_cache_key(args, kwargs)

            # Check cache
            result = cache.get(key)
            if result is not None:
                return result

            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        # Attach cache to function for introspection
        # Note: Dynamic attributes not recognized by type checker, but safe at runtime
        wrapper.cache = cache  # type: ignore[attr-defined]
        wrapper.cache_clear = cache.clear  # type: ignore[attr-defined]
        wrapper.cache_stats = lambda: cache.stats  # type: ignore[attr-defined]

        return wrapper

    return decorator


def _make_cache_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Create a cache key from function arguments."""
    # Handle unhashable types
    key_parts = []
    for arg in args:
        try:
            key_parts.append(repr(arg))
        except Exception:  # Intentionally broad: repr() can raise any exception
            key_parts.append(str(id(arg)))

    for k, v in sorted(kwargs.items()):
        try:
            key_parts.append(f"{k}={v!r}")
        except Exception:  # Intentionally broad: repr() can raise any exception
            key_parts.append(f"{k}={id(v)}")

    key_str = ":".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()


# =============================================================================
# Lazy Loading
# =============================================================================


class Lazy[T]:
    """Lazy evaluation wrapper.

    Example:
        def load_large_data():
            # Expensive operation
            return data

        lazy_data = Lazy(load_large_data)

        # Data is only loaded when accessed
        print(lazy_data.value)  # Loads now
        print(lazy_data.value)  # Uses cached value
    """

    def __init__(self, factory: Callable[[], T]) -> None:
        """Initialize lazy wrapper.

        Args:
            factory: Function that creates the value
        """
        self._factory = factory
        self._value: T | None = None
        self._loaded = False
        self._lock = threading.Lock()

    @property
    def value(self) -> T:
        """Get the lazily-loaded value."""
        if not self._loaded:
            with self._lock:
                if not self._loaded:
                    self._value = self._factory()
                    self._loaded = True
        # Value guaranteed to be loaded (non-None) after the check above
        assert self._value is not None
        return self._value

    @property
    def is_loaded(self) -> bool:
        """Check if value has been loaded."""
        return self._loaded

    def reset(self) -> None:
        """Reset the lazy value to be reloaded on next access."""
        with self._lock:
            self._value = None
            self._loaded = False

    def __repr__(self) -> str:
        """Return repr string."""
        if self._loaded:
            return f"Lazy(loaded={self._value!r})"
        return "Lazy(not loaded)"


class LazyProperty[T]:
    """Lazy property descriptor.

    Example:
        class MyClass:
            @LazyProperty
            def expensive_data(self) -> list:
                # Only computed once per instance
                return compute_expensive_data()
    """

    def __init__(self, func: Callable[[Any], T]) -> None:
        """Initialize the instance."""
        self._func = func
        self._name = func.__name__
        self._cache: weakref.WeakKeyDictionary[Any, T] = weakref.WeakKeyDictionary()

    def __get__(self, obj: Any, objtype: type | None = None) -> T:
        """Get the lazy property value."""
        if obj is None:
            # Descriptor protocol: Return self when accessed from class
            # Type checker expects T but self is valid for this use case
            return self  # type: ignore[return-value]

        if obj in self._cache:
            return self._cache[obj]

        value = self._func(obj)
        self._cache[obj] = value
        return value

    def __set__(self, obj: Any, value: T) -> None:
        """Set the lazy property value."""
        self._cache[obj] = value

    def __delete__(self, obj: Any) -> None:
        """Delete the lazy property value."""
        if obj in self._cache:
            del self._cache[obj]


# =============================================================================
# Batch Processing
# =============================================================================


@dataclass
class BatchResult[T]:
    """Result of a batch operation."""

    items: list[T]
    success_count: int
    error_count: int
    errors: list[tuple[int, Exception]]
    duration_ms: float


class BatchProcessor[T]:
    """Batch processor for bulk operations.

    Example:
        def process_item(item):
            # Process single item
            return result

        processor = BatchProcessor(process_item, batch_size=100)

        results = processor.process_all(large_list_of_items)
        print(f"Processed {results.success_count} items")
    """

    def __init__(
        self,
        processor: Callable[[T], Any],
        batch_size: int = 100,
        max_workers: int | None = None,
        on_error: str = "continue",  # "continue", "stop", "skip"
    ) -> None:
        """Initialize batch processor.

        Args:
            processor: Function to process each item
            batch_size: Number of items per batch
            max_workers: Max parallel workers (None for sequential)
            on_error: Error handling strategy
        """
        self._processor = processor
        self._batch_size = batch_size
        self._max_workers = max_workers
        self._on_error = on_error

    def process_all(
        self,
        items: list[T],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> BatchResult[Any]:
        """Process all items in batches.

        Args:
            items: Items to process
            progress_callback: Optional callback(processed, total)

        Returns:
            BatchResult with results and statistics
        """
        start_time = time.time()
        results = []
        errors: list[tuple[int, Exception]] = []
        success_count = 0
        error_count = 0

        total = len(items)
        for i, item in enumerate(items):
            try:
                result = self._processor(item)
                results.append(result)
                success_count += 1
            except Exception as e:
                # Intentionally broad: user-provided processor can raise any exception
                errors.append((i, e))
                error_count += 1
                if self._on_error == "stop":
                    break

            if progress_callback and (i + 1) % self._batch_size == 0:
                progress_callback(i + 1, total)

        if progress_callback:
            progress_callback(total, total)

        duration_ms = (time.time() - start_time) * 1000

        return BatchResult(
            items=results,
            success_count=success_count,
            error_count=error_count,
            errors=errors,
            duration_ms=duration_ms,
        )

    def process_batches(
        self,
        items: list[T],
    ) -> Iterator[BatchResult[Any]]:
        """Process items and yield results batch by batch.

        Args:
            items: Items to process

        Yields:
            BatchResult for each batch
        """
        for i in range(0, len(items), self._batch_size):
            batch = items[i : i + self._batch_size]
            yield self.process_all(batch)


def batch_process(
    items: list[T],
    processor: Callable[[T], Any],
    batch_size: int = 100,
) -> BatchResult[Any]:
    """Convenience function for batch processing.

    Args:
        items: Items to process
        processor: Function to process each item
        batch_size: Batch size

    Returns:
        BatchResult with all results
    """
    bp = BatchProcessor(processor, batch_size=batch_size)
    return bp.process_all(items)


# =============================================================================
# Performance Benchmarking
# =============================================================================


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""

    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    ops_per_second: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time_ms": self.total_time_ms,
            "avg_time_ms": self.avg_time_ms,
            "min_time_ms": self.min_time_ms,
            "max_time_ms": self.max_time_ms,
            "ops_per_second": self.ops_per_second,
            "timestamp": self.timestamp.isoformat(),
        }


class Benchmark:
    """Performance benchmarking utility.

    Example:
        bench = Benchmark("MyOperation")

        # Run benchmark
        result = bench.run(my_function, iterations=1000)
        print(f"Average: {result.avg_time_ms:.3f}ms")

        # Compare implementations
        results = bench.compare([impl_a, impl_b], iterations=100)
    """

    def __init__(self, name: str = "Benchmark") -> None:
        """Initialize benchmark.

        Args:
            name: Benchmark name for reporting
        """
        self.name = name
        self._results: list[BenchmarkResult] = []

    def run(
        self,
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 5,
    ) -> BenchmarkResult:
        """Run a benchmark.

        Args:
            func: Function to benchmark
            iterations: Number of iterations
            warmup: Warmup iterations (not counted)

        Returns:
            BenchmarkResult with timing statistics
        """
        # Warmup
        for _ in range(warmup):
            func()

        # Benchmark
        times: list[float] = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        total_time = sum(times)
        avg_time = total_time / iterations
        min_time = min(times)
        max_time = max(times)
        ops_per_second = 1000 / avg_time if avg_time > 0 else 0

        result = BenchmarkResult(
            name=self.name,
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            ops_per_second=ops_per_second,
        )

        self._results.append(result)
        return result

    def compare(
        self,
        functions: list[tuple[str, Callable[[], Any]]],
        iterations: int = 100,
    ) -> list[BenchmarkResult]:
        """Compare multiple implementations.

        Args:
            functions: List of (name, function) tuples
            iterations: Iterations per function

        Returns:
            List of BenchmarkResults, sorted by performance
        """
        results = []
        for name, func in functions:
            bench = Benchmark(name)
            result = bench.run(func, iterations)
            results.append(result)

        # Sort by average time (fastest first)
        results.sort(key=lambda r: r.avg_time_ms)
        return results

    @staticmethod
    def format_results(results: list[BenchmarkResult]) -> str:
        """Format benchmark results as a table."""
        if not results:
            return "No results"

        lines = [
            "| Name | Iterations | Avg (ms) | Min (ms) | Max (ms) | Ops/sec |",
            "|------|------------|----------|----------|----------|---------|",
        ]

        for r in results:
            lines.append(
                f"| {r.name[:20]} | {r.iterations:>10} | "
                f"{r.avg_time_ms:>8.3f} | {r.min_time_ms:>8.3f} | "
                f"{r.max_time_ms:>8.3f} | {r.ops_per_second:>7.1f} |"
            )

        return "\n".join(lines)


def timed[T](func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to time function execution.

    Example:
        @timed
        def slow_function():
            time.sleep(1)

        slow_function()
        # Logs: slow_function took 1000.123ms
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} took {elapsed:.3f}ms")
        return result

    return wrapper


# =============================================================================
# File-based Caching
# =============================================================================


class FileCache:
    """File-based persistent cache.

    Example:
        cache = FileCache("~/.cache/spreadsheet-dl")
        cache.set("analysis_result", result)

        # Later...
        cached = cache.get("analysis_result")
    """

    def __init__(
        self,
        cache_dir: Path | str,
        ttl: float | None = 3600,
    ) -> None:
        """Initialize file cache.

        Args:
            cache_dir: Directory for cache files
            ttl: Time-to-live in seconds
        """
        self._cache_dir = Path(cache_dir).expanduser()
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._ttl = ttl

    def _get_path(self, key: str) -> Path:
        """Get cache file path for key."""
        # Hash key to create safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self._cache_dir / f"{key_hash}.json"

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the cache."""
        path = self._get_path(key)
        if not path.exists():
            return default

        try:
            data = json.loads(path.read_text())
            timestamp = data.get("timestamp", 0)

            if self._ttl is not None and time.time() - timestamp > self._ttl:
                path.unlink(missing_ok=True)
                return default

            return data.get("value")
        except (json.JSONDecodeError, OSError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        path = self._get_path(key)
        data = {
            "key": key,
            "value": value,
            "timestamp": time.time(),
        }
        path.write_text(json.dumps(data))

    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        path = self._get_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self) -> int:
        """Clear all cached items. Returns count of deleted items."""
        count = 0
        for path in self._cache_dir.glob("*.json"):
            path.unlink()
            count += 1
        return count

    def cleanup_expired(self) -> int:
        """Remove expired cache entries. Returns count of deleted items."""
        if self._ttl is None:
            return 0

        count = 0
        now = time.time()
        for path in self._cache_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                timestamp = data.get("timestamp", 0)
                if now - timestamp > self._ttl:
                    path.unlink()
                    count += 1
            except (json.JSONDecodeError, OSError):
                pass

        return count


# =============================================================================
# Global Cache Instance
# =============================================================================

_global_cache: LRUCache[str, Any] | None = None


def get_cache() -> LRUCache[str, Any]:
    """Get the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = LRUCache(maxsize=1000, ttl=3600)
    return _global_cache


def clear_cache() -> None:
    """Clear the global cache."""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear()
