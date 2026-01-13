#!/usr/bin/env python3
"""Archive Old Checkpoints Hook.

Removes checkpoint archives older than retention period (30 days).

Version: 1.0.0
Created: 2025-12-25
"""

import json
import os
import shutil
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", str(REPO_ROOT)))
LOG_FILE = PROJECT_DIR / ".claude/hooks/hook.log"

RETENTION_DAYS = 30


def log(message: str) -> None:
    """Log to hook log file."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now(UTC).isoformat()}] ARCHIVE_CHECKPOINTS: {message}\n")


def archive_old_checkpoints() -> dict:
    """Remove checkpoints older than retention period."""
    log("Starting checkpoint archive cleanup")

    checkpoint_dirs = [
        PROJECT_DIR / ".coordination/checkpoints/.archive",
        PROJECT_DIR / ".claude/checkpoints",
    ]

    removed_count = 0
    cutoff_time = datetime.now(UTC) - timedelta(days=RETENTION_DAYS)

    for checkpoint_dir in checkpoint_dirs:
        if not checkpoint_dir.exists():
            continue

        for item in checkpoint_dir.iterdir():
            try:
                # Get modification time
                mtime = datetime.fromtimestamp(item.stat().st_mtime, tz=UTC)

                if mtime < cutoff_time:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

                    log(f"Removed old checkpoint: {item.name}")
                    removed_count += 1
            except Exception as e:
                log(f"Error removing {item}: {e}")

    log(f"Cleanup complete: {removed_count} old checkpoints removed")

    return {
        "ok": True,
        "removed": removed_count,
        "retention_days": RETENTION_DAYS,
        "message": f"Removed {removed_count} checkpoints older than {RETENTION_DAYS} days",
    }


def main() -> None:
    """Main entry point."""
    result = archive_old_checkpoints()
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
