#!/usr/bin/env python3
"""SSOT Validation Hook.

Ensures no duplicate configuration exists across the repository.
Validates against .claude/project-metadata.yaml as single source of truth.

Version: 1.0.0
Created: 2025-12-25
"""

import json
import os
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
        f.write(f"[{datetime.now().isoformat()}] VALIDATE_SSOT: {message}\n")


def check_duplicate_configs() -> dict[str, Any]:
    """Check for duplicate configuration files."""
    errors = []

    # Check for duplicate example configs
    PROJECT_DIR / "examples/configs"
    duplicate_locations = [
        PROJECT_DIR / ".coordination/spec/spreadsheet-dl/example-configs",
    ]

    for dup_loc in duplicate_locations:
        if dup_loc.exists():
            errors.append(
                f"Duplicate config directory exists: {dup_loc.relative_to(PROJECT_DIR)}"
            )

    return {"ok": len(errors) == 0, "errors": errors}


def check_metadata_sync() -> dict[str, Any]:
    """Check that project metadata is synchronized."""
    errors = []
    warnings = []

    metadata_file = PROJECT_DIR / ".claude/project-metadata.yaml"
    if not metadata_file.exists():
        errors.append("project-metadata.yaml not found")
        return {"ok": False, "errors": errors}

    try:
        import yaml

        with open(metadata_file) as f:
            metadata = yaml.safe_load(f)
    except ImportError:
        warnings.append("PyYAML not available - skipping metadata validation")
        return {"ok": True, "warnings": warnings}
    except Exception as e:
        errors.append(f"Failed to parse project-metadata.yaml: {e}")
        return {"ok": False, "errors": errors}

    # Extract expected GitHub org
    expected_org = metadata.get("project", {}).get("github", {}).get("org")
    if not expected_org:
        errors.append("GitHub org not defined in project-metadata.yaml")
        return {"ok": False, "errors": errors}

    # Check files that should have consistent GitHub URLs
    url_locations = metadata.get("project", {}).get("url_locations", [])
    for file_path in url_locations:
        full_path = PROJECT_DIR / file_path
        if not full_path.exists():
            continue

        try:
            content = full_path.read_text()
            # Check for old/wrong org names
            wrong_orgs = ["allenjd1", "allenjd"]
            for wrong_org in wrong_orgs:
                if wrong_org in content and file_path not in [
                    "CHANGELOG.md"
                ]:  # Allow in changelog
                    errors.append(
                        f"{file_path} contains '{wrong_org}', expected '{expected_org}'"
                    )
        except Exception:
            pass

    return {"ok": len(errors) == 0, "errors": errors, "warnings": warnings}


def main() -> None:
    """Main entry point."""
    # Check for bypass
    if os.environ.get("CLAUDE_BYPASS_HOOKS") == "1":
        print(json.dumps({"ok": True, "bypassed": True}))
        sys.exit(0)

    log("Starting SSOT validation")

    all_errors = []
    all_warnings = []

    # Run checks
    dup_result = check_duplicate_configs()
    all_errors.extend(dup_result.get("errors", []))

    meta_result = check_metadata_sync()
    all_errors.extend(meta_result.get("errors", []))
    all_warnings.extend(meta_result.get("warnings", []))

    # Output result
    result = {
        "ok": len(all_errors) == 0,
        "errors": len(all_errors),
        "warnings": len(all_warnings),
        "details": all_errors + all_warnings,
    }

    print(json.dumps(result, indent=2))

    if len(all_errors) > 0:
        log(f"SSOT validation failed: {len(all_errors)} errors")
        sys.exit(1)
    else:
        log("SSOT validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
