#!/usr/bin/env python3
"""Enforce Python code quality after writes/edits.

PostToolUse hook that validates Python files and BLOCKS if critical errors remain.

Quality enforcement workflow:
1. Auto-format with ruff format (non-blocking)
2. Auto-fix with ruff check --fix (non-blocking)
3. Validate remaining errors:
   - BLOCK on critical errors (syntax, undefined names, unused imports)
   - WARN on style issues (non-blocking)

Exit codes:
- 0: Success (no issues or only warnings)
- 2: BLOCK operation (critical errors remain)

This ensures all Python code written by Claude meets quality standards immediately,
preventing the accumulation of technical debt.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Critical error codes that should block operations
CRITICAL_ERROR_CODES = {
    "E9",  # Syntax errors (E901-E999)
    "F",  # Pyflakes errors (undefined names, unused imports, etc.)
    "F401",  # Module imported but unused (critical for clean code)
    "F821",  # Undefined name
    "F841",  # Local variable assigned but never used
}

# Errors to auto-fix but not block (will be fixed by --fix)
AUTO_FIXABLE_CODES = {
    "I",  # Import sorting
    "UP",  # Pyupgrade
}


def run_command(cmd: list[str], cwd: str, timeout: int = 30) -> tuple[int, str, str]:
    """Execute command and return output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timeout after {timeout}s"
    except Exception as e:
        return 1, "", f"Command error: {e}"


def parse_ruff_json(output: str) -> list[dict[str, Any]]:
    """Parse ruff JSON output into error list."""
    try:
        if not output.strip():
            return []
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def categorize_errors(
    errors: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Categorize errors into critical and non-critical.

    Returns:
        Tuple of (critical_errors, warnings)
    """
    critical = []
    warnings = []

    for error in errors:
        code = error.get("code", "")

        # Check if this is a critical error
        is_critical = any(code.startswith(prefix) for prefix in CRITICAL_ERROR_CODES)

        if is_critical:
            critical.append(error)
        else:
            warnings.append(error)

    return critical, warnings


def format_error(error: dict[str, Any]) -> str:
    """Format a single error for display."""
    location = error.get("location", {})
    line = location.get("row", "?")
    col = location.get("column", "?")
    code = error.get("code", "???")
    message = error.get("message", "Unknown error")

    return f"  Line {line}:{col} - {code}: {message}"


def validate_python_file(file_path: str, project_root: str) -> int:
    """Validate Python file with ruff and block on critical errors.

    Args:
        file_path: Path to Python file
        project_root: Project root directory

    Returns:
        Exit code (0 = success, 2 = block)
    """
    path = Path(file_path)

    # Only validate Python files
    if not path.exists() or path.suffix != ".py":
        return 0

    # Skip excluded directories
    excluded = {".venv", "__pycache__", ".mypy_cache", ".ruff_cache", "node_modules"}
    if any(exc in path.parts for exc in excluded):
        return 0

    # Step 1: Auto-format (always runs, non-blocking)
    run_command(
        ["uv", "run", "ruff", "format", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    # Step 2: Auto-fix linting issues (non-blocking)
    run_command(
        ["uv", "run", "ruff", "check", "--fix", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    # Step 3: Check for remaining errors
    _returncode, stdout, _stderr = run_command(
        [
            "uv",
            "run",
            "ruff",
            "check",
            "--output-format=json",
            str(file_path),
        ],
        cwd=project_root,
        timeout=30,
    )

    # Parse errors
    errors = parse_ruff_json(stdout)

    if not errors:
        # No errors - success!
        filename = path.name
        print(f"✓ Python quality check passed: {filename}", file=sys.stderr)
        return 0

    # Categorize errors
    critical, warnings = categorize_errors(errors)

    # Report warnings (non-blocking)
    if warnings:
        filename = path.name
        print(f"! Python warnings in {filename}:", file=sys.stderr)
        for warning in warnings[:5]:
            print(format_error(warning), file=sys.stderr)
        if len(warnings) > 5:
            print(f"  ... and {len(warnings) - 5} more warnings", file=sys.stderr)

    # Block on critical errors
    if critical:
        filename = path.name
        print(f"\n❌ CRITICAL ERRORS in {filename}:", file=sys.stderr)
        print("Cannot proceed until these are fixed:\n", file=sys.stderr)

        for error in critical[:10]:
            print(format_error(error), file=sys.stderr)

        if len(critical) > 10:
            print(
                f"\n  ... and {len(critical) - 10} more critical errors",
                file=sys.stderr,
            )

        print(
            "\nSuggestion: Review the code and fix these errors before writing.",
            file=sys.stderr,
        )
        return 2  # BLOCK the operation

    return 0  # Only warnings, allow operation


def main() -> None:
    """Main entry point for PostToolUse hook."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only process Write/Edit tools
        if tool_name not in {"Write", "Edit"}:
            sys.exit(0)

        # Extract file path
        file_path = tool_input.get("file_path")
        if not file_path:
            sys.exit(0)

        # Get project root
        import os

        project_root = os.getenv("CLAUDE_PROJECT_DIR", str(Path.cwd()))

        # Validate and potentially block
        exit_code = validate_python_file(file_path, project_root)
        sys.exit(exit_code)

    except json.JSONDecodeError:
        # Invalid input - allow operation
        sys.exit(0)
    except Exception as e:
        # Unexpected error - log but allow operation
        print(f"⚠ Quality enforcement error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
