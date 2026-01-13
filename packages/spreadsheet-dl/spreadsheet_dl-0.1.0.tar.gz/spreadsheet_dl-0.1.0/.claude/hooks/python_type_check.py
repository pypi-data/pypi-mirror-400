#!/usr/bin/env python3
"""Type-check Python files with mypy after writes/edits.

PostToolUse hook that runs mypy type checking on Python files.

Behavior:
- INFO mode (default): Show type errors but don't block
- STRICT mode: Block on type errors (exit 2)

Set MYPY_STRICT=1 in environment to enable strict blocking.

Exit codes:
- 0: Success (no type errors or INFO mode)
- 2: BLOCK operation (type errors in STRICT mode)

This helps maintain type safety across the codebase without being overly
restrictive during development.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Maximum type errors to display
MAX_ERRORS_DISPLAY = 15


def run_mypy(file_path: str, project_root: str) -> tuple[int, str]:
    """Run mypy on a Python file.

    Args:
        file_path: Path to Python file
        project_root: Project root directory

    Returns:
        Tuple of (returncode, output)
    """
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "mypy",
                str(file_path),
                "--no-error-summary",
                "--show-error-codes",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        return 1, "Mypy timeout after 60s"
    except Exception as e:
        return 1, f"Mypy error: {e}"


def parse_mypy_output(output: str) -> list[str]:
    """Parse mypy output into error lines."""
    errors = []
    for line in output.strip().split("\n"):
        # Filter out summary lines
        if line and not line.startswith("Found ") and not line.startswith("Success:"):
            errors.append(line.strip())
    return errors


def should_block_on_type_errors() -> bool:
    """Check if we should block on type errors."""
    # Check environment variable
    return os.getenv("MYPY_STRICT", "0") == "1"


def validate_python_types(file_path: str, project_root: str) -> int:
    """Type-check Python file with mypy.

    Args:
        file_path: Path to Python file
        project_root: Project root directory

    Returns:
        Exit code (0 = success, 2 = block in strict mode)
    """
    path = Path(file_path)

    # Only validate Python files
    if not path.exists() or path.suffix != ".py":
        return 0

    # Skip excluded directories
    excluded = {".venv", "__pycache__", ".mypy_cache", ".ruff_cache", "node_modules"}
    if any(exc in path.parts for exc in excluded):
        return 0

    # Skip test files in INFO mode (too strict for tests)
    if not should_block_on_type_errors() and "test" in path.parts:
        return 0

    # Run mypy
    returncode, output = run_mypy(file_path, project_root)

    if returncode == 0:
        # No type errors!
        filename = path.name
        print(f"✓ Type check passed: {filename}", file=sys.stderr)
        return 0

    # Parse errors
    errors = parse_mypy_output(output)

    if not errors:
        return 0

    # Display errors
    filename = path.name
    strict_mode = should_block_on_type_errors()

    if strict_mode:
        print(f"\n❌ TYPE ERRORS in {filename}:", file=sys.stderr)
        print("Cannot proceed until these are fixed:\n", file=sys.stderr)
    else:
        print(f"\n[i] Type hints in {filename}:", file=sys.stderr)

    # Show first N errors
    for error in errors[:MAX_ERRORS_DISPLAY]:
        print(f"  {error}", file=sys.stderr)

    if len(errors) > MAX_ERRORS_DISPLAY:
        remaining = len(errors) - MAX_ERRORS_DISPLAY
        print(f"\n  ... and {remaining} more type errors", file=sys.stderr)

    if strict_mode:
        print(
            "\nSuggestion: Fix type errors or disable MYPY_STRICT mode.",
            file=sys.stderr,
        )
        return 2  # BLOCK in strict mode
    else:
        print(
            "\nNote: These are informational. Set MYPY_STRICT=1 to block on type errors.",
            file=sys.stderr,
        )
        return 0  # INFO mode - don't block


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
        project_root = os.getenv("CLAUDE_PROJECT_DIR", str(Path.cwd()))

        # Type-check and potentially block
        exit_code = validate_python_types(file_path, project_root)
        sys.exit(exit_code)

    except json.JSONDecodeError:
        # Invalid input - allow operation
        sys.exit(0)
    except Exception as e:
        # Unexpected error - log but allow operation
        print(f"⚠ Type check error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
