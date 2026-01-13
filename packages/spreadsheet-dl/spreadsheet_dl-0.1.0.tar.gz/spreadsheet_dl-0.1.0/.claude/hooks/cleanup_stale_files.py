#!/usr/bin/env python3
"""Stale File Cleanup Script for Claude Code SessionStart Hook.

Automatically archives or removes stale intermediate files to prevent:
1. Context pollution from outdated coordination files
2. Drift between actual state and stale reports
3. Accumulation of vestigial intermediate files

CLEANUP RULES:
- .coordination/*.json files older than 7 days -> archive
- .claude/agent-outputs/*.json older than 14 days -> archive
- .coordination/*.md temp files older than 3 days -> archive
- Empty or zero-byte files in .coordination/ -> remove

Author: TraceKit Orchestration System
Version: 1.0.0
Date: 2025-12-21
"""

import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path


def log_info(message: str) -> None:
    """Log info message to stderr."""
    print(f"[cleanup] {message}", file=sys.stderr)


def get_project_dir() -> Path:
    """Get project directory from environment or current directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    return Path(project_dir)


def ensure_archive_dir(project_dir: Path) -> Path:
    """Create archive directory structure if it doesn't exist."""
    archive_dir = project_dir / ".claude" / "agent-outputs" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir


def get_file_age_days(filepath: Path) -> float:
    """Get file age in days."""
    try:
        mtime = filepath.stat().st_mtime
        mtime_dt = datetime.fromtimestamp(mtime, tz=UTC)
        now = datetime.now(tz=UTC)
        return (now - mtime_dt).total_seconds() / 86400
    except Exception:
        return 0


def archive_file(filepath: Path, archive_dir: Path) -> bool:
    """Move file to archive directory with date prefix."""
    try:
        date_prefix = datetime.now().strftime("%Y-%m-%d")
        archive_name = f"{date_prefix}-{filepath.name}"
        archive_path = archive_dir / archive_name

        # Handle name collision
        counter = 1
        while archive_path.exists():
            archive_name = f"{date_prefix}-{counter}-{filepath.name}"
            archive_path = archive_dir / archive_name
            counter += 1

        shutil.move(str(filepath), str(archive_path))
        log_info(f"Archived: {filepath.name} -> archive/{archive_name}")
        return True
    except Exception as e:
        log_info(f"Failed to archive {filepath}: {e}")
        return False


def remove_empty_file(filepath: Path) -> bool:
    """Remove empty or zero-byte files."""
    try:
        if filepath.stat().st_size == 0:
            filepath.unlink()
            log_info(f"Removed empty file: {filepath.name}")
            return True
        return False
    except Exception as e:
        log_info(f"Failed to remove {filepath}: {e}")
        return False


def cleanup_coordination_files(project_dir: Path, archive_dir: Path) -> dict:
    """Clean up stale coordination files."""
    stats = {"archived": 0, "removed": 0, "kept": 0}

    coordination_dir = project_dir / ".coordination"
    if not coordination_dir.exists():
        return stats

    # Clean up JSON files older than 7 days (except spec files)
    for json_file in coordination_dir.glob("*.json"):
        if get_file_age_days(json_file) > 7:
            if archive_file(json_file, archive_dir):
                stats["archived"] += 1
        else:
            stats["kept"] += 1

    # Clean up temp MD files older than 3 days (not in spec/)
    for md_file in coordination_dir.glob("*.md"):
        # Skip if in a subdirectory like spec/
        if md_file.parent != coordination_dir:
            continue
        if get_file_age_days(md_file) > 3:
            if archive_file(md_file, archive_dir):
                stats["archived"] += 1
        else:
            stats["kept"] += 1

    # Remove empty files
    for any_file in coordination_dir.glob("*"):
        if any_file.is_file() and remove_empty_file(any_file):
            stats["removed"] += 1

    return stats


def cleanup_agent_outputs(project_dir: Path, archive_dir: Path) -> dict:
    """Clean up old agent output files."""
    stats = {"archived": 0, "kept": 0}

    outputs_dir = project_dir / ".claude" / "agent-outputs"
    if not outputs_dir.exists():
        return stats

    # Archive completion reports older than 14 days
    for json_file in outputs_dir.glob("*-complete.json"):
        if get_file_age_days(json_file) > 14:
            if archive_file(json_file, archive_dir):
                stats["archived"] += 1
        else:
            stats["kept"] += 1

    # Archive other outputs older than 14 days
    for output_file in outputs_dir.glob("*.md"):
        if get_file_age_days(output_file) > 14:
            if archive_file(output_file, archive_dir):
                stats["archived"] += 1
        else:
            stats["kept"] += 1

    return stats


def cleanup_archive(archive_dir: Path, max_days: int = 60) -> int:
    """Remove very old archived files (older than max_days)."""
    removed = 0
    for archived_file in archive_dir.glob("*"):
        if archived_file.is_file() and get_file_age_days(archived_file) > max_days:
            try:
                archived_file.unlink()
                removed += 1
            except Exception:
                pass
    return removed


def main() -> None:
    """Main entry point for cleanup script."""
    project_dir = get_project_dir()

    # Ensure archive directory exists
    archive_dir = ensure_archive_dir(project_dir)

    # Run cleanup operations
    coord_stats = cleanup_coordination_files(project_dir, archive_dir)
    output_stats = cleanup_agent_outputs(project_dir, archive_dir)
    archive_removed = cleanup_archive(archive_dir)

    # Summary
    total_archived = coord_stats["archived"] + output_stats["archived"]
    total_removed = coord_stats["removed"] + archive_removed

    if total_archived > 0 or total_removed > 0:
        log_info(
            f"Cleanup complete: {total_archived} archived, {total_removed} removed"
        )

    # Always succeed - cleanup is best-effort
    print(
        json.dumps(
            {
                "ok": True,
                "cleanup": {"archived": total_archived, "removed": total_removed},
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_info(f"Cleanup error (non-fatal): {e}")
        print(json.dumps({"ok": True}))
        sys.exit(0)
