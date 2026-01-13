#!/usr/bin/env python3
"""Post-write validation hook - Quick lint checks.

PostToolUse hook that validates files after Claude writes/edits them:
- Python: ruff check (quick mode)
- Shell: shellcheck
- YAML: yamllint
- Markdown: markdownlint (if available)

Reports first 3-5 issues to agent (non-blocking, informational).
Always exits 0 to avoid disrupting workflows.

Configuration:
- Detects tools dynamically (graceful degradation if missing)
- Respects excluded directories (.venv, node_modules, __pycache__, .git)
- Validates paths are within project root (security)
- 30s timeout per validator (prevents hangs)
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Excluded directories (skip validation)
EXCLUDED_DIRS = {
    ".venv",
    "node_modules",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".ruff_cache",
}

# Maximum issues to report per file
MAX_ISSUES = 5

# Tool availability cache (avoid repeated lookups)
_tool_cache: dict[str, bool] = {}


def has_tool(tool: str) -> bool:
    """Check if tool is available on PATH (cached)."""
    if tool not in _tool_cache:
        _tool_cache[tool] = shutil.which(tool) is not None
    return _tool_cache[tool]


def parse_ruff_output(output: str) -> list[str]:
    """Parse ruff check output into issue strings."""
    issues = []
    for line in output.strip().split("\n"):
        if line and not line.startswith("Found"):
            # Format: file:line:col: CODE message
            issues.append(line.strip())
            if len(issues) >= MAX_ISSUES:
                break
    return issues


def parse_shellcheck_output(output: str) -> list[str]:
    """Parse shellcheck gcc-format output into issue strings."""
    issues = []
    for line in output.strip().split("\n"):
        if line and ": " in line:
            # Format: file:line:col: type: message
            issues.append(line.strip())
            if len(issues) >= MAX_ISSUES:
                break
    return issues


def parse_yamllint_output(output: str) -> list[str]:
    """Parse yamllint parsable output into issue strings."""
    issues = []
    for line in output.strip().split("\n"):
        if line:
            # Format: file:line:col: [level] message (rule)
            issues.append(line.strip())
            if len(issues) >= MAX_ISSUES:
                break
    return issues


def parse_markdownlint_output(output: str) -> list[str]:
    """Parse markdownlint output into issue strings."""
    issues = []
    for line in output.strip().split("\n"):
        if line and ":" in line:
            issues.append(line.strip())
            if len(issues) >= MAX_ISSUES:
                break
    return issues


def validate_file(file_path: str, project_root: str) -> list[str]:
    """Run quick validation on file, return issues.

    Args:
        file_path: Path to file to validate
        project_root: Project root directory (for security validation)

    Returns:
        List of issue strings (max MAX_ISSUES)
    """
    path = Path(file_path)

    # Skip if file doesn't exist
    if not path.exists():
        return []

    # Skip excluded directories
    if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
        return []

    # Skip if outside project root (security check)
    try:
        path.resolve().relative_to(Path(project_root).resolve())
    except ValueError:
        return []

    validator_timeout = 30

    try:
        # Python files: ruff check
        if path.suffix == ".py":
            if not has_tool("uv"):
                return []
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "ruff",
                    "check",
                    "--output-format=concise",
                    str(file_path),
                ],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=validator_timeout,
                check=False,
            )
            if result.returncode != 0 and result.stdout:
                return parse_ruff_output(result.stdout)

        # Shell scripts: shellcheck
        elif path.suffix == ".sh":
            if not has_tool("shellcheck"):
                return []
            result = subprocess.run(
                ["shellcheck", "-f", "gcc", str(file_path)],
                capture_output=True,
                text=True,
                timeout=validator_timeout,
                check=False,
            )
            if result.returncode != 0 and result.stdout:
                return parse_shellcheck_output(result.stdout)

        # YAML files: yamllint
        elif path.suffix in {".yaml", ".yml"}:
            if not has_tool("yamllint"):
                return []
            result = subprocess.run(
                ["yamllint", "-f", "parsable", str(file_path)],
                capture_output=True,
                text=True,
                timeout=validator_timeout,
                check=False,
            )
            if result.returncode != 0 and result.stdout:
                return parse_yamllint_output(result.stdout)

        # Markdown files: markdownlint (if available)
        elif path.suffix == ".md":
            if not has_tool("npx"):
                return []
            result = subprocess.run(
                ["npx", "markdownlint", str(file_path)],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=validator_timeout,
                check=False,
            )
            if result.returncode != 0 and result.stdout:
                return parse_markdownlint_output(result.stdout)

    except subprocess.TimeoutExpired:
        return [f"Validation timeout (>{validator_timeout}s)"]
    except Exception:
        # Silently skip on errors - non-blocking hook
        pass

    return []


def main() -> None:
    """Main entry point for PostToolUse hook."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        # Extract tool name and file path
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only process Write, Edit, and NotebookEdit tools
        if tool_name not in {"Write", "Edit", "NotebookEdit"}:
            sys.exit(0)

        # Extract file path from tool input
        file_path = tool_input.get("file_path", "") or tool_input.get(
            "notebook_path", ""
        )

        if not file_path:
            sys.exit(0)

        # Get project root from environment
        project_root = os.getenv("CLAUDE_PROJECT_DIR", str(Path.cwd()))

        # Validate the file
        issues = validate_file(file_path, project_root)

        # Report issues to stderr (visible to agent, non-blocking)
        if issues:
            filename = Path(file_path).name
            print(f"! Validation issues in {filename}:", file=sys.stderr)
            for issue in issues[:MAX_ISSUES]:
                print(f"  {issue}", file=sys.stderr)
            if len(issues) >= MAX_ISSUES:
                print(f"  ... (showing first {MAX_ISSUES} issues)", file=sys.stderr)

    except json.JSONDecodeError:
        # Invalid JSON input - fail silently
        pass
    except Exception as e:
        # Log errors to stderr but don't block
        print(f"! Auto-validate hook error: {e}", file=sys.stderr)

    # ALWAYS exit 0 (non-blocking hook)
    sys.exit(0)


if __name__ == "__main__":
    main()
