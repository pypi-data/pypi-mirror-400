#!/usr/bin/env python3
"""TODO Policy Enforcement Hook.

Validates TODO comments follow the taxonomy defined in coding-standards.yaml

Version: 1.0.0
Created: 2025-12-25
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", str(REPO_ROOT)))
LOG_FILE = PROJECT_DIR / ".claude/hooks/hook.log"


def log(message: str) -> None:
    """Log to hook log file."""
    from datetime import datetime

    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] LINT_TODOS: {message}\n")


def check_forbidden_markers() -> dict[str, Any]:
    """Check for forbidden TODO markers."""
    forbidden = ["TODO:", "FIXME:", "XXX:", "HACK:"]
    errors = []

    for py_file in (PROJECT_DIR / "src").rglob("*.py"):
        try:
            content = py_file.read_text()
            for line_num, line in enumerate(content.splitlines(), 1):
                for marker in forbidden:
                    if marker in line and not line.strip().startswith("#"):
                        continue  # Only check comments
                    if f"# {marker}" in line or f"#{marker}" in line:
                        rel_path = py_file.relative_to(PROJECT_DIR)
                        errors.append(
                            f"{rel_path}:{line_num} - Use TODO(dev), USER:, FUTURE:, or NOTE: instead of {marker}"
                        )
        except Exception:
            pass

    return {"ok": len(errors) == 0, "errors": errors}


def check_future_markers() -> dict[str, Any]:
    """Check FUTURE markers have issue IDs."""
    warnings = []

    for py_file in (PROJECT_DIR / "src").rglob("*.py"):
        try:
            content = py_file.read_text()
            for line_num, line in enumerate(content.splitlines(), 1):
                if "# FUTURE:" in line and not re.search(r"# FUTURE-\d+", line):
                    rel_path = py_file.relative_to(PROJECT_DIR)
                    warnings.append(
                        f"{rel_path}:{line_num} - FUTURE marker should have ID (e.g., FUTURE-001)"
                    )
        except Exception:
            pass

    return {"ok": True, "warnings": warnings}


def main() -> None:
    """Main entry point."""
    # Check for bypass
    if os.environ.get("CLAUDE_BYPASS_HOOKS") == "1":
        print(json.dumps({"ok": True, "bypassed": True}))
        sys.exit(0)

    log("Starting TODO linting")

    all_errors = []
    all_warnings = []

    # Run checks
    forbidden_result = check_forbidden_markers()
    all_errors.extend(forbidden_result.get("errors", []))

    future_result = check_future_markers()
    all_warnings.extend(future_result.get("warnings", []))

    # Output result
    result = {
        "ok": len(all_errors) == 0,
        "errors": len(all_errors),
        "warnings": len(all_warnings),
        "details": all_errors + all_warnings,
    }

    print(json.dumps(result, indent=2))

    if len(all_errors) > 0:
        log(f"TODO linting failed: {len(all_errors)} errors")
        sys.exit(1)
    else:
        log(f"TODO linting passed ({len(all_warnings)} warnings)")
        sys.exit(0)


if __name__ == "__main__":
    main()
