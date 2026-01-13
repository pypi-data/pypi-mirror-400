"""Common handler utilities for MCP tools.

Provides shared functionality for parameter validation, error handling,
and response formatting used across all MCP tool categories.

"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spreadsheet_dl._mcp.exceptions import MCPSecurityError
from spreadsheet_dl.exceptions import FileError

if TYPE_CHECKING:
    import logging

    from spreadsheet_dl._mcp.config import MCPConfig
    from spreadsheet_dl._mcp.models import MCPToolResult


@dataclass
class ToolRateLimit:
    """Per-tool rate limit configuration.

    Attributes:
        requests_per_minute: Maximum requests per minute for this tool
        burst_limit: Maximum burst requests allowed (short-term spike)
        cooldown_seconds: Cooldown period after burst limit exceeded
    """

    requests_per_minute: int = 60
    burst_limit: int = 10
    cooldown_seconds: int = 30


# Default rate limits per tool category
# More sensitive operations have stricter limits
DEFAULT_TOOL_RATE_LIMITS: dict[str, ToolRateLimit] = {
    # File operations - moderate limits
    "file_read": ToolRateLimit(requests_per_minute=30, burst_limit=5),
    "file_write": ToolRateLimit(requests_per_minute=20, burst_limit=3),
    "file_delete": ToolRateLimit(requests_per_minute=10, burst_limit=2),
    # Cell operations - higher limits
    "cell_read": ToolRateLimit(requests_per_minute=120, burst_limit=20),
    "cell_write": ToolRateLimit(requests_per_minute=60, burst_limit=10),
    # Structure operations - moderate limits
    "sheet_create": ToolRateLimit(requests_per_minute=20, burst_limit=5),
    "sheet_delete": ToolRateLimit(requests_per_minute=10, burst_limit=2),
    # Chart operations - moderate limits
    "chart_create": ToolRateLimit(requests_per_minute=30, burst_limit=5),
    "chart_update": ToolRateLimit(requests_per_minute=30, burst_limit=5),
    # Export operations - stricter limits (resource intensive)
    "export_pdf": ToolRateLimit(
        requests_per_minute=10, burst_limit=2, cooldown_seconds=60
    ),
    "export_xlsx": ToolRateLimit(requests_per_minute=15, burst_limit=3),
    "export_csv": ToolRateLimit(requests_per_minute=30, burst_limit=5),
    # Import operations - stricter limits
    "import_data": ToolRateLimit(requests_per_minute=15, burst_limit=3),
    # Formula operations - higher limits
    "formula_evaluate": ToolRateLimit(requests_per_minute=60, burst_limit=15),
    "formula_validate": ToolRateLimit(requests_per_minute=120, burst_limit=30),
    # Default for unspecified tools
    "default": ToolRateLimit(requests_per_minute=60, burst_limit=10),
}


@dataclass
class ToolUsageStats:
    """Track usage statistics for a single tool."""

    request_count: int = 0
    burst_count: int = 0
    last_request: datetime | None = None
    last_reset: datetime = field(default_factory=datetime.now)
    cooldown_until: datetime | None = None

    def reset_if_needed(self) -> None:
        """Reset counters if a minute has passed."""
        now = datetime.now()
        if (now - self.last_reset).seconds >= 60:
            self.request_count = 0
            self.burst_count = 0
            self.last_reset = now

    def is_in_cooldown(self) -> bool:
        """Check if tool is in cooldown period."""
        if self.cooldown_until is None:
            return False
        return datetime.now() < self.cooldown_until


@dataclass
class AuditLogConfig:
    """Configuration for audit log rotation.

    Attributes:
        max_size_mb: Maximum log file size in megabytes before rotation
        max_files: Maximum number of rotated log files to keep
        compress: Whether to compress rotated logs
    """

    max_size_mb: float = 10.0
    max_files: int = 5
    compress: bool = True


class AuditLogRotator:
    """Handles automatic rotation of audit logs.

    Rotates logs when they exceed max_size_mb, keeping up to max_files
    rotated copies. Optionally compresses old logs.
    """

    def __init__(
        self,
        log_path: Path,
        config: AuditLogConfig | None = None,
    ) -> None:
        """Initialize audit log rotator.

        Args:
            log_path: Path to the audit log file
            config: Rotation configuration (uses defaults if not provided)
        """
        self.log_path = log_path
        self.config = config or AuditLogConfig()
        self._max_bytes = int(self.config.max_size_mb * 1024 * 1024)

    def should_rotate(self) -> bool:
        """Check if log file should be rotated.

        Returns:
            True if rotation is needed
        """
        if not self.log_path.exists():
            return False
        return self.log_path.stat().st_size >= self._max_bytes

    def rotate(self) -> None:
        """Rotate the log file.

        Creates numbered backup files (audit.log.1, audit.log.2, etc.)
        and optionally compresses them.
        """
        if not self.log_path.exists():
            return

        # Shift existing rotated logs
        for i in range(self.config.max_files - 1, 0, -1):
            old_path = self._get_rotated_path(i)
            new_path = self._get_rotated_path(i + 1)

            if old_path.exists():
                if i + 1 > self.config.max_files:
                    # Delete oldest log
                    old_path.unlink()
                else:
                    old_path.rename(new_path)

        # Rotate current log to .1
        first_rotated = self._get_rotated_path(1)
        self.log_path.rename(first_rotated)

        # Compress if configured
        if self.config.compress:
            self._compress_file(first_rotated)

        # Create new empty log
        self.log_path.touch()

    def _get_rotated_path(self, index: int) -> Path:
        """Get path for a rotated log file."""
        suffix = ".gz" if self.config.compress and index > 0 else ""
        return self.log_path.with_suffix(f".{index}{suffix}")

    def _compress_file(self, path: Path) -> None:
        """Compress a log file using gzip."""
        import gzip
        import shutil

        compressed_path = path.with_suffix(path.suffix + ".gz")
        try:
            with open(path, "rb") as f_in, gzip.open(compressed_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            path.unlink()
        except OSError:
            # Compression failed, keep uncompressed
            if compressed_path.exists():
                compressed_path.unlink()


class HandlerUtils:
    """Common utilities for MCP tool handlers."""

    def __init__(self, config: MCPConfig, logger: logging.Logger) -> None:
        """Initialize handler utilities."""
        self.config = config
        self.logger = logger

        # Per-tool rate limiting
        self._tool_stats: dict[str, ToolUsageStats] = defaultdict(ToolUsageStats)
        self._tool_limits: dict[str, ToolRateLimit] = DEFAULT_TOOL_RATE_LIMITS.copy()

        # Global rate limiting (backward compatibility)
        self._request_count = 0
        self._last_reset = datetime.now()

        # Audit log rotation
        self._log_rotator: AuditLogRotator | None = None
        if config.audit_log_path:
            self._log_rotator = AuditLogRotator(
                config.audit_log_path,
                AuditLogConfig(),
            )

    def configure_tool_rate_limit(
        self,
        tool_category: str,
        limit: ToolRateLimit,
    ) -> None:
        """Configure rate limit for a specific tool category.

        Args:
            tool_category: Tool category name (e.g., "file_write")
            limit: Rate limit configuration
        """
        self._tool_limits[tool_category] = limit

    def _validate_path(self, path: str | Path) -> Path:
        """Validate and resolve a file path.

        Args:
            path: Path to validate.

        Returns:
            Resolved Path object.

        Raises:
            MCPSecurityError: If path is not allowed.
            FileError: If file doesn't exist.
        """
        resolved = Path(path).resolve()

        # Check against allowed paths
        allowed = False
        for allowed_path in self.config.allowed_paths:
            try:
                resolved.relative_to(allowed_path.resolve())
                allowed = True
                break
            except ValueError:
                continue

        if not allowed:
            raise MCPSecurityError(
                f"Path not allowed: {path}. "
                f"Allowed paths: {[str(p) for p in self.config.allowed_paths]}"
            )

        if not resolved.exists():
            raise FileError(f"File not found: {resolved}")

        return resolved

    def _check_rate_limit(self, tool_category: str | None = None) -> bool:
        """Check if rate limit is exceeded for a tool.

        Args:
            tool_category: Tool category for per-tool limiting.
                          If None, uses global rate limit.

        Returns:
            True if request is allowed, False if rate limited

        """
        now = datetime.now()

        # Global rate limit check (backward compatibility)
        if (now - self._last_reset).seconds >= 60:
            self._request_count = 0
            self._last_reset = now
        self._request_count += 1

        if self._request_count > self.config.rate_limit_per_minute:
            return False

        # Per-tool rate limit check
        if tool_category:
            stats = self._tool_stats[tool_category]
            limit = self._tool_limits.get(
                tool_category,
                self._tool_limits["default"],
            )

            # Check cooldown
            if stats.is_in_cooldown():
                return False

            # Reset if minute passed
            stats.reset_if_needed()

            # Check burst limit
            if stats.last_request:
                time_since_last = (now - stats.last_request).total_seconds()
                if time_since_last < 1.0:  # Within 1 second
                    stats.burst_count += 1
                    if stats.burst_count > limit.burst_limit:
                        stats.cooldown_until = datetime.now()
                        stats.cooldown_until = datetime.fromtimestamp(
                            now.timestamp() + limit.cooldown_seconds
                        )
                        return False
                else:
                    stats.burst_count = 0

            # Check per-minute limit
            stats.request_count += 1
            stats.last_request = now

            if stats.request_count > limit.requests_per_minute:
                return False

        return True

    def get_rate_limit_status(self, tool_category: str | None = None) -> dict[str, Any]:
        """Get current rate limit status.

        Args:
            tool_category: Tool category to check

        Returns:
            Dictionary with rate limit status information
        """
        result: dict[str, Any] = {
            "global": {
                "requests_used": self._request_count,
                "limit": self.config.rate_limit_per_minute,
                "remaining": max(
                    0, self.config.rate_limit_per_minute - self._request_count
                ),
            }
        }

        if tool_category:
            stats = self._tool_stats[tool_category]
            limit = self._tool_limits.get(
                tool_category,
                self._tool_limits["default"],
            )
            result["tool"] = {
                "category": tool_category,
                "requests_used": stats.request_count,
                "limit": limit.requests_per_minute,
                "remaining": max(0, limit.requests_per_minute - stats.request_count),
                "burst_used": stats.burst_count,
                "burst_limit": limit.burst_limit,
                "in_cooldown": stats.is_in_cooldown(),
            }

        return result

    def _log_audit(
        self,
        tool: str,
        params: dict[str, Any],
        result: MCPToolResult,
    ) -> None:
        """Log tool invocation for audit.

        Args:
            tool: Tool name
            params: Tool parameters
            result: Tool execution result

        """
        if not self.config.enable_audit_log:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "params": {k: str(v) for k, v in params.items()},
            "success": not result.is_error,
        }

        self.logger.info(json.dumps(entry))

        if self.config.audit_log_path:
            # Check if rotation is needed before writing
            if self._log_rotator and self._log_rotator.should_rotate():
                self._log_rotator.rotate()

            try:
                with open(self.config.audit_log_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
            except OSError as e:
                self.logger.warning(f"Failed to write audit log: {e}")

    def rotate_audit_log(self) -> bool:
        """Manually trigger audit log rotation.

        Returns:
            True if rotation was performed, False otherwise
        """
        if self._log_rotator:
            self._log_rotator.rotate()
            return True
        return False

    # =========================================================================
    # Tool Handlers
    # =========================================================================


# Export utilities
__all__ = [
    "DEFAULT_TOOL_RATE_LIMITS",
    "AuditLogConfig",
    "AuditLogRotator",
    "HandlerUtils",
    "ToolRateLimit",
    "ToolUsageStats",
]
