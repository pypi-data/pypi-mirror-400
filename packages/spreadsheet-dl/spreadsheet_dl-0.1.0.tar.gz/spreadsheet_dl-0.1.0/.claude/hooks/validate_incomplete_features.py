#!/usr/bin/env python3
"""Validate FUTURE markers against incomplete-features.yaml registry.

Ensures bidirectional consistency:
1. All FUTURE-XXX markers in code have entries in the registry
2. All registry entries have corresponding markers in code

Version: 1.0.0
Created: 2025-12-25
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", str(REPO_ROOT)))

REGISTRY_FILE = PROJECT_DIR / ".coordination" / "spec" / "incomplete-features.yaml"
SRC_DIR = PROJECT_DIR / "src"
TESTS_DIR = PROJECT_DIR / "tests"
LOG_FILE = PROJECT_DIR / ".claude" / "hooks" / "hook.log"

# Pattern to match FUTURE markers in code
FUTURE_PATTERN = re.compile(r"#\s*FUTURE-(\d+)")

# =============================================================================
# Logging Setup
# =============================================================================

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("validate_incomplete_features")


# =============================================================================
# YAML Loading
# =============================================================================


def load_yaml(file_path: Path) -> dict[str, Any]:
    """Load YAML file."""
    try:
        import yaml

        with open(file_path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        logger.error("PyYAML not installed. Install with: uv add pyyaml")
        return {}
    except Exception as e:
        logger.error(f"Failed to load YAML: {e}")
        return {}


# =============================================================================
# Validation Logic
# =============================================================================


def find_future_markers_in_code() -> dict[str, list[dict[str, Any]]]:
    """Find all FUTURE-XXX markers in source code.

    Returns:
        Dict mapping FUTURE-XXX ids to list of occurrences
    """
    markers: dict[str, list[dict[str, Any]]] = {}

    # Search directories
    search_dirs = [SRC_DIR, TESTS_DIR]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        for py_file in search_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for line_num, line in enumerate(content.splitlines(), 1):
                    for match in FUTURE_PATTERN.finditer(line):
                        future_id = f"FUTURE-{match.group(1)}"
                        if future_id not in markers:
                            markers[future_id] = []
                        markers[future_id].append(
                            {
                                "file": str(py_file.relative_to(PROJECT_DIR)),
                                "line": line_num,
                                "context": line.strip()[:100],
                            }
                        )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")

    return markers


def get_registered_features() -> dict[str, dict[str, Any]]:
    """Get all features registered in incomplete-features.yaml.

    Returns:
        Dict mapping FUTURE-XXX ids to feature info
    """
    if not REGISTRY_FILE.exists():
        logger.warning(f"Registry file not found: {REGISTRY_FILE}")
        return {}

    data = load_yaml(REGISTRY_FILE)
    features = data.get("incomplete_features", [])

    return {f.get("id", ""): f for f in features if f.get("id")}


def validate_markers() -> dict[str, Any]:
    """Validate FUTURE markers against registry.

    Returns:
        Validation result with issues found
    """
    code_markers = find_future_markers_in_code()
    registered = get_registered_features()

    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    # Check code markers not in registry
    for future_id, occurrences in code_markers.items():
        if future_id not in registered:
            issues.append(
                {
                    "type": "unregistered_marker",
                    "future_id": future_id,
                    "message": f"Code has {future_id} but it's not in incomplete-features.yaml",
                    "occurrences": occurrences,
                    "severity": "error",
                }
            )

    # Check registry entries not in code
    for future_id, feature in registered.items():
        if future_id not in code_markers:
            warnings.append(
                {
                    "type": "orphaned_registration",
                    "future_id": future_id,
                    "message": f"Registry has {future_id} but no marker found in code",
                    "feature": feature.get("feature", "Unknown"),
                    "expected_file": feature.get("file", "Unknown"),
                    "severity": "warning",
                }
            )

    # Check file paths match
    for future_id, occurrences in code_markers.items():
        if future_id in registered:
            expected_file = registered[future_id].get("file", "")
            actual_files = {o["file"] for o in occurrences}

            if expected_file and expected_file not in actual_files:
                warnings.append(
                    {
                        "type": "file_mismatch",
                        "future_id": future_id,
                        "message": f"{future_id} registered for {expected_file} but found in {actual_files}",
                        "expected": expected_file,
                        "actual": list(actual_files),
                        "severity": "warning",
                    }
                )

    # Summary
    all_valid = len(issues) == 0

    result = {
        "ok": all_valid,
        "code_markers_found": len(code_markers),
        "registered_features": len(registered),
        "errors": len(issues),
        "warnings": len(warnings),
        "issues": issues,
        "warnings_list": warnings,
        "code_markers": {k: len(v) for k, v in code_markers.items()},
        "registered_ids": list(registered.keys()),
    }

    if all_valid:
        if warnings:
            logger.info(f"Validation passed with {len(warnings)} warnings")
        else:
            logger.info("All FUTURE markers match registry")
    else:
        logger.error(
            f"Validation failed: {len(issues)} errors, {len(warnings)} warnings"
        )

    return result


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate FUTURE markers against incomplete-features.yaml"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    args = parser.parse_args()

    try:
        result = validate_markers()

        # In strict mode, warnings count as failures
        if args.strict and result["warnings"] > 0:
            result["ok"] = False
            result["message"] = "Strict mode: warnings treated as errors"

        if args.verbose:
            print(json.dumps(result, indent=2))
        else:
            # Compact output
            summary = {
                "ok": result["ok"],
                "errors": result["errors"],
                "warnings": result["warnings"],
                "code_markers": result["code_markers_found"],
                "registered": result["registered_features"],
            }
            print(json.dumps(summary))

        sys.exit(0 if result["ok"] else 1)

    except Exception as e:
        logger.exception("Validation failed")
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
