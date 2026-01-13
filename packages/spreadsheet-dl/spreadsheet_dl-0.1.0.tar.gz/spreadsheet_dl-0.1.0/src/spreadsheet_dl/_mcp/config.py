"""MCP server configuration classes.

Part of the modular MCP server implementation.
Defines configuration, capabilities, and protocol versions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class MCPVersion(Enum):
    """MCP protocol versions."""

    V1 = "2024-11-05"  # Current stable version


@dataclass
class MCPCapabilities:
    """Server capabilities declaration."""

    tools: bool = True
    resources: bool = False
    prompts: bool = False
    logging: bool = True


@dataclass
class MCPConfig:
    """Configuration for MCP server."""

    name: str = "spreadsheet-dl"
    version: str = "1.0.0"
    allowed_paths: list[Path] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    enable_audit_log: bool = True
    audit_log_path: Path | None = None

    def __post_init__(self) -> None:
        """Set default allowed paths."""
        if not self.allowed_paths:
            # Default to common budget locations
            self.allowed_paths = [
                Path.cwd(),
                Path.home() / "Documents",
                Path.home() / "Finance",
            ]
