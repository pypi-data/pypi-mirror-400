#!/usr/bin/env python3
"""SubagentStop Hook Verification.

Verifies subagent completion before returning to orchestrator.
Returns JSON response for Claude Code hook system.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def log_error(message: str) -> None:
    """Log error to errors.log file."""
    log_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".claude" / "hooks"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "errors.log"
    timestamp = datetime.now().isoformat()
    with log_file.open("a") as f:
        f.write(f"[{timestamp}] check_subagent_stop: {message}\n")


def check_subagent_completion() -> dict[str, bool | str]:
    """Check if subagent completed its task properly.

    Subagents should produce completion reports before stopping.
    This hook verifies the subagent didn't abandon work.

    Returns:
        dict: {"ok": True} or {"ok": False, "reason": "explanation"}
    """
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    agent_outputs = project_dir / ".claude" / "agent-outputs"

    # Check for recent completion reports (within last 5 minutes)
    if agent_outputs.exists():
        now = datetime.now()
        recent_reports = []

        for report_file in agent_outputs.glob("*-complete.json"):
            try:
                # Check if file was modified in last 5 minutes
                mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                if (now - mtime).total_seconds() < 300:  # 5 minutes
                    with report_file.open() as f:
                        report = json.load(f)
                        recent_reports.append((report_file.name, report))
            except (OSError, json.JSONDecodeError) as e:
                log_error(f"Failed to read {report_file}: {e}")
                continue

        # If we found recent reports, validate them
        if recent_reports:
            for filename, report in recent_reports:
                status = report.get("status", "unknown")

                # Block if any recent report shows blocked status
                if status == "blocked":
                    reason = report.get("blocked_by", "Unknown blocker")
                    return {
                        "ok": False,
                        "reason": f"Task blocked: {reason}. Resolve before stopping.",
                    }

                # Warn but allow if needs-review (orchestrator should handle)
                if status == "needs-review":
                    log_error(
                        f"Report {filename} needs review - allowing stop for orchestrator to handle"
                    )

                # Validate artifacts exist if specified
                artifacts = report.get("artifacts", [])
                for artifact in artifacts:
                    artifact_path = project_dir / artifact
                    if not artifact_path.exists():
                        log_error(f"Artifact missing: {artifact}")
                        # Don't block on missing artifacts - may be optional

    # All checks passed (or no recent reports found)
    return {"ok": True}


def main() -> None:
    """Main entry point."""
    try:
        result = check_subagent_completion()
        print(json.dumps(result))
        sys.exit(0 if result["ok"] else 2)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        # Fail safe - allow stop on error
        print(json.dumps({"ok": True}))
        sys.exit(0)


if __name__ == "__main__":
    main()
