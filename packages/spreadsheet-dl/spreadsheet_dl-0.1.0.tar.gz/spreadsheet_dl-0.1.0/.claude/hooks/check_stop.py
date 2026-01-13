#!/usr/bin/env python3
"""Stop Hook Verification.

Verifies task completion before allowing agent to stop.
Returns JSON response for Claude Code hook system.
"""

import contextlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def log_error(message: str) -> None:
    """Log error to errors.log file."""
    log_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".claude" / "hooks"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "errors.log"
    timestamp = datetime.now().isoformat()
    with log_file.open("a") as f:
        f.write(f"[{timestamp}] check_stop: {message}\n")


def is_stale(work: dict[str, Any], max_age_hours: int = 24) -> bool:
    """Check if active work is stale (no update in max_age_hours).

    Args:
        work: Active work dictionary from active_work.json
        max_age_hours: Maximum age in hours before considering stale (default: 24)

    Returns:
        True if work is stale or missing timestamp, False otherwise
    """
    last_update = work.get("last_update")
    if not last_update:
        return True  # No timestamp = stale

    try:
        # Parse the timestamp
        update_time = datetime.fromisoformat(last_update.replace("Z", "+00:00"))

        # Use naive datetime for consistency if no timezone, aware otherwise
        now = datetime.now() if update_time.tzinfo is None else datetime.now(UTC)

        age_hours = (now - update_time).total_seconds() / 3600
        return age_hours > max_age_hours
    except (ValueError, TypeError):
        return True  # Invalid timestamp = stale


def check_completion() -> dict[str, bool | str]:
    """Check if agent completed its task properly.

    Returns:
        dict: {"ok": True} or {"ok": False, "reason": "explanation"}
    """
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))

    # Check for active work that shouldn't be abandoned
    active_work = project_dir / ".coordination" / "active_work.json"
    if active_work.exists():
        try:
            with active_work.open() as f:
                work = json.load(f)
            if work.get("status") == "in_progress":
                # Check if work is stale (no update in 24+ hours)
                if is_stale(work):
                    task_id = work.get("task_id", "unknown")
                    log_error(
                        f"Stale active work detected for task '{task_id}'. "
                        "No update in 24+ hours. Allowing stop."
                    )
                    # Allow stop for stale work - likely crashed agent
                else:
                    # Fresh work still in progress - block stop
                    task_id = work.get("task_id", "unknown")
                    return {
                        "ok": False,
                        "reason": f"Active task '{task_id}' still in progress. Complete or hand off before stopping.",
                    }
        except (OSError, json.JSONDecodeError) as e:
            log_error(f"Failed to read active_work.json: {e}")

    # All checks passed
    return {"ok": True}


def main() -> None:
    """Main entry point."""
    try:
        # Read stdin for hook context (may include stop_hook_active flag)
        input_data = {}
        if not sys.stdin.isatty():
            with contextlib.suppress(json.JSONDecodeError):
                input_data = json.load(sys.stdin)

        # CRITICAL: Check stop_hook_active FIRST to prevent infinite loops
        if input_data.get("stop_hook_active"):
            print(json.dumps({"ok": True}))
            sys.exit(0)

        result = check_completion()
        print(json.dumps(result))
        sys.exit(0 if result["ok"] else 2)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        # Fail safe - allow stop on error
        print(json.dumps({"ok": True}))
        sys.exit(0)


if __name__ == "__main__":
    main()
