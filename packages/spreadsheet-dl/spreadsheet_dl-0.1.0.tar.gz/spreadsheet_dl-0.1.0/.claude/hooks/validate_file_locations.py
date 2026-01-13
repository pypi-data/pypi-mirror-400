#!/usr/bin/env python3
"""File Location Validation Script for Claude Code PostToolUse Hook.

Detects when intermediate/analysis files are created in project directories
instead of .coordination/ and provides guidance to move them.

This helps prevent:
1. Project directory clutter from intermediate analysis files
2. Confusion between final artifacts and working documents
3. Accidental commit of temporary analysis files

VALIDATION RULES:
- Files matching analysis patterns in src/ or docs/ -> warn
- Files matching temp patterns outside .coordination/ -> warn
- New .md files in project root that look like working docs -> warn

Author: TraceKit Orchestration System
Version: 1.0.0
Date: 2025-12-21
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Patterns that indicate intermediate/analysis files
INTERMEDIATE_PATTERNS = [
    r".*ANALYSIS.*\.md$",
    r".*TROUBLESHOOT.*\.md$",
    r".*PLAN\.md$",
    r".*SUMMARY\.md$",
    r".*ROOT_CAUSE.*\.md$",
    r".*INVESTIGATION.*\.md$",
    r".*DEBUG.*\.md$",
    r".*NOTES\.md$",
    r".*TODO\.md$",
    r".*SCRATCH.*\.md$",
    r".*DRAFT.*\.md$",
    r".*WIP.*\.md$",
]

# Directories where intermediate files are allowed
ALLOWED_INTERMEDIATE_DIRS = [
    ".coordination",
    ".claude",
    ".git",
]

# Directories where intermediate files should NOT be created
PROTECTED_DIRS = [
    "src",
    "docs",
    "tests",
]


def log_info(message: str) -> None:
    """Log info message to stderr."""
    print(f"[validate_location] {message}", file=sys.stderr)


def parse_hook_input() -> dict[str, Any]:
    """Parse the hook input JSON from stdin."""
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def get_project_dir(input_data: dict[str, Any]) -> Path:
    """Extract project directory from hook input."""
    project_dir = input_data.get("project_dir") or os.environ.get(
        "CLAUDE_PROJECT_DIR", "."
    )
    return Path(project_dir)


def is_intermediate_file(filename: str) -> bool:
    """Check if filename matches intermediate file patterns."""
    for pattern in INTERMEDIATE_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    return False


def is_in_allowed_dir(filepath: Path, project_dir: Path) -> bool:
    """Check if file is in an allowed intermediate directory."""
    try:
        relative = filepath.relative_to(project_dir)
        parts = relative.parts
        if parts:
            return parts[0] in ALLOWED_INTERMEDIATE_DIRS
    except ValueError:
        pass
    return False


def is_in_protected_dir(filepath: Path, project_dir: Path) -> bool:
    """Check if file is in a protected directory."""
    try:
        relative = filepath.relative_to(project_dir)
        parts = relative.parts
        if parts:
            return parts[0] in PROTECTED_DIRS
    except ValueError:
        pass
    return False


def validate_write_location(
    input_data: dict[str, Any], project_dir: Path
) -> tuple[bool, str]:
    """Validate if a Write tool is creating a file in an appropriate location.

    Returns:
        (is_valid, warning_message)
    """
    # Get the file path from the tool call
    tool_input = input_data.get("tool_input", {})
    file_path_str = tool_input.get("file_path", "")

    if not file_path_str:
        return True, ""

    filepath = Path(file_path_str)
    filename = filepath.name

    # Check if it's an intermediate file
    if not is_intermediate_file(filename):
        return True, ""

    # Check if it's in an allowed location
    if is_in_allowed_dir(filepath, project_dir):
        return True, ""

    # Check if it's in a protected directory
    if is_in_protected_dir(filepath, project_dir):
        return False, (
            f"Intermediate file '{filename}' should not be in {filepath.parent}. "
            f"Move to .coordination/ instead: .coordination/{filename}"
        )

    # File is at project root or other location
    return False, (
        f"Intermediate file '{filename}' detected outside .coordination/. "
        f"Consider moving to: .coordination/{filename}"
    )


def main() -> None:
    """Main entry point for location validation."""
    input_data = parse_hook_input()

    # Only validate Write tool calls
    tool_name = input_data.get("tool_name", "")
    if tool_name != "Write":
        print(json.dumps({"ok": True}))
        sys.exit(0)

    project_dir = get_project_dir(input_data)

    is_valid, warning = validate_write_location(input_data, project_dir)

    if not is_valid:
        log_info(f"WARNING: {warning}")
        # We warn but don't block - just inform
        print(json.dumps({"ok": True, "warning": warning}))
    else:
        print(json.dumps({"ok": True}))

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_info(f"Validation error (non-fatal): {e}")
        print(json.dumps({"ok": True}))
        sys.exit(0)
