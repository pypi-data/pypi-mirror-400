#!/usr/bin/env python3
"""STRICT quality enforcement - Block ALL errors and warnings.

PostToolUse hook that enforces zero-tolerance quality standards:
- Python: ruff (all errors), mypy (type errors)
- Shell: shellcheck (all warnings)
- YAML: yamllint (all warnings)
- Markdown: markdownlint (all warnings)
- JSON: validate syntax

Workflow:
1. Auto-format files (ruff format, prettier, shfmt, etc.)
2. Auto-fix issues where possible (ruff check --fix)
3. Validate remaining issues
4. BLOCK if ANY issues remain (exit code 2)

This prevents ALL quality issues from accumulating, ensuring every file
written meets full quality standards immediately.

Exit codes:
- 0: Success (no issues)
- 2: BLOCK (issues found)
"""

import json
import subprocess
import sys
from pathlib import Path

# Maximum issues to display before truncating
MAX_DISPLAY = 20


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


def validate_python(file_path: Path, project_root: str) -> tuple[bool, list[str]]:
    """Validate Python file with ruff and mypy.

    Returns:
        Tuple of (passed: bool, errors: list[str])
    """
    errors = []

    # Step 1: Auto-format
    run_command(
        ["uv", "run", "ruff", "format", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    # Step 2: Auto-fix
    run_command(
        ["uv", "run", "ruff", "check", "--fix", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    # Step 3: Check for remaining ruff issues
    returncode, stdout, _ = run_command(
        [
            "uv",
            "run",
            "ruff",
            "check",
            "--output-format=concise",
            str(file_path),
        ],
        cwd=project_root,
        timeout=30,
    )

    if returncode != 0 and stdout.strip():
        for line in stdout.strip().split("\n"):
            if line and not line.startswith("Found"):
                errors.append(f"[ruff] {line}")

    # Step 4: Type check with mypy
    returncode, stdout, _ = run_command(
        ["uv", "run", "mypy", str(file_path), "--no-error-summary"],
        cwd=project_root,
        timeout=60,
    )
    if returncode != 0 and stdout.strip():
        for line in stdout.strip().split("\n"):
            if line and not line.startswith("Found") and not line.startswith("Success"):
                errors.append(f"[mypy] {line}")

    return len(errors) == 0, errors


def validate_shell(file_path: Path, project_root: str) -> tuple[bool, list[str]]:
    """Validate shell script with shellcheck.

    Returns:
        Tuple of (passed: bool, errors: list[str])
    """
    errors = []

    # Auto-format with shfmt if available
    run_command(
        ["shfmt", "-i", "2", "-w", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    # Validate with shellcheck (enable ALL checks including style)
    # -S style: Include style warnings (stricter than -S warning)
    # This respects .shellcheckrc configuration while enforcing all enabled checks
    returncode, stdout, _ = run_command(
        ["shellcheck", "-f", "gcc", "-S", "style", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    if returncode != 0 and stdout.strip():
        for line in stdout.strip().split("\n"):
            if line and ":" in line:
                errors.append(f"[shellcheck] {line}")

    return len(errors) == 0, errors


def validate_yaml(file_path: Path, project_root: str) -> tuple[bool, list[str]]:
    """Validate YAML file with yamllint.

    Returns:
        Tuple of (passed: bool, errors: list[str])
    """
    errors = []

    # Auto-format with prettier if available
    run_command(
        ["npx", "prettier", "--write", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    # Validate with yamllint
    returncode, stdout, _ = run_command(
        ["yamllint", "-f", "parsable", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    if returncode != 0 and stdout.strip():
        for line in stdout.strip().split("\n"):
            if line:
                errors.append(f"[yamllint] {line}")

    return len(errors) == 0, errors


def validate_markdown(file_path: Path, project_root: str) -> tuple[bool, list[str]]:
    """Validate Markdown file with markdownlint.

    Returns:
        Tuple of (passed: bool, errors: list[str])
    """
    errors = []

    # Auto-format with prettier if available
    run_command(
        ["npx", "prettier", "--write", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    # Validate with markdownlint
    returncode, stdout, _ = run_command(
        ["npx", "markdownlint", str(file_path)],
        cwd=project_root,
        timeout=30,
    )

    if returncode != 0 and stdout.strip():
        for line in stdout.strip().split("\n"):
            if line and ":" in line:
                errors.append(f"[markdownlint] {line}")

    return len(errors) == 0, errors


def validate_json(file_path: Path, project_root: str) -> tuple[bool, list[str]]:
    """Validate JSON file syntax.

    Returns:
        Tuple of (passed: bool, errors: list[str])
    """
    errors = []

    # First validate JSON syntax (before prettier fixes it)
    try:
        with open(file_path) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"[json] Line {e.lineno}: {e.msg}")
    except Exception as e:
        errors.append(f"[json] {e!s}")

    # If valid, auto-format with prettier
    if not errors:
        run_command(
            ["npx", "prettier", "--write", str(file_path)],
            cwd=project_root,
            timeout=30,
        )

    return len(errors) == 0, errors


def validate_file(file_path: str, project_root: str) -> int:
    """Validate file and block if ANY issues found.

    Args:
        file_path: Path to file to validate
        project_root: Project root directory

    Returns:
        Exit code (0 = success, 2 = block)
    """
    path = Path(file_path)

    # Skip if file doesn't exist
    if not path.exists():
        return 0

    # Skip excluded directories
    excluded = {
        ".venv",
        "node_modules",
        "__pycache__",
        ".git",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "dist",
        "build",
        ".eggs",
        ".tox",
        ".nox",
    }
    if any(exc in path.parts for exc in excluded):
        return 0

    # Skip VS Code config files (use JSONC format with comments)
    if ".vscode" in path.parts and path.suffix == ".json":
        return 0

    # Validate based on file type
    passed = True
    errors: list[str] = []

    if path.suffix == ".py":
        passed, errors = validate_python(path, project_root)
    elif path.suffix == ".sh":
        passed, errors = validate_shell(path, project_root)
    elif path.suffix in {".yaml", ".yml"}:
        passed, errors = validate_yaml(path, project_root)
    elif path.suffix == ".md":
        passed, errors = validate_markdown(path, project_root)
    elif path.suffix == ".json":
        passed, errors = validate_json(path, project_root)
    else:
        # Unknown file type - allow
        return 0

    # Report results
    filename = path.name

    if passed:
        print(f"✓ Quality check passed: {filename}", file=sys.stderr)
        return 0

    # BLOCK - issues found
    print(f"\n❌ QUALITY ISSUES in {filename}:", file=sys.stderr)
    print("All issues must be fixed before proceeding.\n", file=sys.stderr)

    # Display errors (truncate if too many)
    for error in errors[:MAX_DISPLAY]:
        print(f"  {error}", file=sys.stderr)

    if len(errors) > MAX_DISPLAY:
        remaining = len(errors) - MAX_DISPLAY
        print(f"\n  ... and {remaining} more issues", file=sys.stderr)

    print(
        "\n💡 Suggestion: Fix all issues above, then try writing again.",
        file=sys.stderr,
    )
    print(
        "   Most issues can be auto-fixed - the tool will attempt this first.",
        file=sys.stderr,
    )

    return 2  # BLOCK the operation


def main() -> None:
    """Main entry point for PostToolUse hook."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only process Write/Edit/NotebookEdit tools
        if tool_name not in {"Write", "Edit", "NotebookEdit"}:
            sys.exit(0)

        # Extract file path
        file_path = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not file_path:
            sys.exit(0)

        # Get project root
        import os

        project_root = os.getenv("CLAUDE_PROJECT_DIR", str(Path.cwd()))

        # Validate and potentially block
        exit_code = validate_file(file_path, project_root)
        sys.exit(exit_code)

    except json.JSONDecodeError:
        # Invalid input - allow operation
        sys.exit(0)
    except Exception as e:
        # Unexpected error - log but allow operation
        print(f"⚠ Strict quality enforcement error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
