#!/usr/bin/env python3
"""Context Optimizer.

Analyzes project structure and suggests optimizations for context-limited environments.
Identifies large files, redundant content, and provides actionable recommendations.

Usage:
    python context_optimizer.py [--directory DIR] [--report] [--fix]

Examples:
    # Analyze current project
    python context_optimizer.py

    # Generate detailed report
    python context_optimizer.py --report

    # Show suggested fixes
    python context_optimizer.py --suggestions
"""

import argparse
import contextlib
import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Thresholds for recommendations
LARGE_FILE_THRESHOLD = 100 * 1024  # 100KB
OLD_FILE_DAYS = 7
MAX_CONTEXT_ESTIMATE = 200000  # tokens


def format_size(size: int) -> str:
    """Format size in human-readable format."""
    size_float = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024
    return f"{size_float:.1f} TB"


def estimate_tokens(text: str) -> int:
    """Rough estimate of tokens (4 chars per token)."""
    return len(text) // 4


def get_file_hash(path: Path, sample_size: int = 8192) -> str:
    """Get hash of file (first N bytes for speed)."""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read(sample_size)).hexdigest()
    except (OSError, PermissionError):
        return ""


def analyze_directory(directory: Path) -> dict[str, Any]:
    """Analyze a directory for context optimization opportunities."""
    analysis: dict[str, Any] = {
        "directory": str(directory),
        "timestamp": datetime.now().isoformat(),
        "files": {
            "total": 0,
            "by_extension": defaultdict(int),
            "by_size_bracket": {
                "large": [],  # >100KB
                "medium": [],  # 10-100KB
                "small": [],  # <10KB
            },
        },
        "issues": [],
        "suggestions": [],
        "summary": {},
    }

    # File patterns that are usually safe to exclude from context
    EXCLUDABLE_PATTERNS = {
        ".pyc",
        ".pyo",
        ".so",
        ".o",
        ".a",
        ".dll",
        ".exe",
        ".bin",
        ".cache",
        ".log",
        ".bak",
        ".tmp",
        ".swp",
    }

    # Directories typically excluded
    EXCLUDABLE_DIRS = {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "dist",
        "build",
        ".tox",
        "htmlcov",
        ".coverage",
    }

    total_size = 0
    excludable_size = 0
    large_files = []
    old_json_files = []
    duplicate_hashes: dict[str, list[str]] = defaultdict(list)
    now = datetime.now()

    # Walk directory
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDABLE_DIRS]

        root_path = Path(root)

        for filename in files:
            file_path = root_path / filename
            analysis["files"]["total"] += 1

            try:
                stat = file_path.stat()
                size = stat.st_size
                total_size += size
                ext = file_path.suffix.lower()
                age_days = (now - datetime.fromtimestamp(stat.st_mtime)).days

                analysis["files"]["by_extension"][ext] += 1

                # Check if excludable
                if ext in EXCLUDABLE_PATTERNS:
                    excludable_size += size

                # Categorize by size
                file_info = {
                    "path": str(file_path.relative_to(directory)),
                    "size": size,
                    "size_human": format_size(size),
                    "age_days": age_days,
                }

                if size > LARGE_FILE_THRESHOLD:
                    analysis["files"]["by_size_bracket"]["large"].append(file_info)
                    large_files.append(file_info)
                elif size > 10 * 1024:
                    analysis["files"]["by_size_bracket"]["medium"].append(file_info)
                else:
                    analysis["files"]["by_size_bracket"]["small"].append(file_info)

                # Check for old JSON files (potential cleanup candidates)
                if ext == ".json" and age_days > OLD_FILE_DAYS and size > 10 * 1024:
                    old_json_files.append(file_info)

                # Track duplicates
                if size > 1024:  # Only check files > 1KB
                    file_hash = get_file_hash(file_path)
                    if file_hash:
                        duplicate_hashes[file_hash].append(str(file_path))

            except (OSError, PermissionError):
                continue

    # Identify duplicates
    duplicates = {h: paths for h, paths in duplicate_hashes.items() if len(paths) > 1}

    # Build summary
    analysis["summary"] = {
        "total_files": analysis["files"]["total"],
        "total_size": total_size,
        "total_size_human": format_size(total_size),
        "estimated_tokens": estimate_tokens(str(total_size)),  # Very rough
        "excludable_size": excludable_size,
        "excludable_size_human": format_size(excludable_size),
        "large_file_count": len(large_files),
        "duplicate_groups": len(duplicates),
    }

    # Generate issues and suggestions
    if large_files:
        analysis["issues"].append(
            {
                "type": "large_files",
                "severity": "medium",
                "count": len(large_files),
                "description": f"Found {len(large_files)} files over {format_size(LARGE_FILE_THRESHOLD)}",
            }
        )
        analysis["suggestions"].append(
            {
                "action": "compress_large_json",
                "command": "gzip -k <file>",
                "files": [
                    f["path"]
                    for f in large_files[:10]
                    if isinstance(f["path"], str) and f["path"].endswith(".json")
                ],
            }
        )

    if old_json_files:
        analysis["issues"].append(
            {
                "type": "old_json_files",
                "severity": "low",
                "count": len(old_json_files),
                "description": f"Found {len(old_json_files)} JSON files over {OLD_FILE_DAYS} days old",
            }
        )
        analysis["suggestions"].append(
            {
                "action": "archive_old_json",
                "command": "mv <file> .coordination/archive/",
                "files": [f["path"] for f in old_json_files[:10]],
            }
        )

    if duplicates:
        total_dupe_size = 0
        for paths in duplicates.values():
            if len(paths) > 1:
                with contextlib.suppress(OSError, AttributeError):
                    total_dupe_size += Path(paths[0]).stat().st_size * (len(paths) - 1)

        analysis["issues"].append(
            {
                "type": "duplicate_files",
                "severity": "low",
                "count": len(duplicates),
                "wasted_space": format_size(total_dupe_size),
                "description": f"Found {len(duplicates)} groups of duplicate files",
            }
        )
        analysis["duplicates"] = {
            h[:8]: paths for h, paths in list(duplicates.items())[:5]
        }

    if excludable_size > 0:
        analysis["suggestions"].append(
            {
                "action": "add_to_ignore",
                "description": f"Add excludable patterns to .gitignore to save {format_size(excludable_size)}",
                "patterns": list(EXCLUDABLE_PATTERNS),
            }
        )

    # Sort large files
    analysis["files"]["by_size_bracket"]["large"].sort(
        key=lambda x: x["size"], reverse=True
    )
    analysis["files"]["by_size_bracket"]["large"] = analysis["files"][
        "by_size_bracket"
    ]["large"][:20]

    return analysis


def generate_report(analysis: dict[str, Any]) -> str:
    """Generate human-readable report."""
    lines = [
        "=" * 70,
        "CONTEXT OPTIMIZATION REPORT",
        "=" * 70,
        f"Directory: {analysis['directory']}",
        f"Generated: {analysis['timestamp']}",
        "",
        "SUMMARY",
        "-" * 70,
        f"Total Files: {analysis['summary']['total_files']}",
        f"Total Size: {analysis['summary']['total_size_human']}",
        f"Large Files (>{format_size(LARGE_FILE_THRESHOLD)}): {analysis['summary']['large_file_count']}",
        f"Duplicate Groups: {analysis['summary']['duplicate_groups']}",
        f"Excludable Size: {analysis['summary']['excludable_size_human']}",
        "",
    ]

    if analysis["issues"]:
        lines.extend(["ISSUES", "-" * 70])
        for issue in analysis["issues"]:
            lines.append(f"[{issue['severity'].upper()}] {issue['description']}")
        lines.append("")

    if analysis["suggestions"]:
        lines.extend(["SUGGESTIONS", "-" * 70])
        for i, suggestion in enumerate(analysis["suggestions"], 1):
            lines.append(f"{i}. {suggestion['action']}")
            if "description" in suggestion:
                lines.append(f"   {suggestion['description']}")
            if "command" in suggestion:
                lines.append(f"   Command: {suggestion['command']}")
            if suggestion.get("files"):
                lines.append(f"   Files: {', '.join(suggestion['files'][:5])}")
        lines.append("")

    if analysis["files"]["by_size_bracket"]["large"]:
        lines.extend(["LARGE FILES (Top 10)", "-" * 70])
        for f in analysis["files"]["by_size_bracket"]["large"][:10]:
            lines.append(f"  {f['size_human']:>10}  {f['path']}")
        lines.append("")

    if "duplicates" in analysis:
        lines.extend(["DUPLICATE FILES (Sample)", "-" * 70])
        for hash_prefix, paths in analysis["duplicates"].items():
            lines.append(f"  Hash {hash_prefix}...:")
            for p in paths[:3]:
                lines.append(f"    - {p}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> None:
    """Analyze project for context optimization opportunities."""
    parser = argparse.ArgumentParser(
        description="Analyze project for context optimization opportunities"
    )
    parser.add_argument(
        "--directory",
        "-d",
        default=".",
        help="Directory to analyze (default: current)",
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate human-readable report",
    )
    parser.add_argument(
        "--suggestions",
        "-s",
        action="store_true",
        help="Show only suggestions",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)

    analysis = analyze_directory(directory)

    if args.suggestions:
        if analysis["suggestions"]:
            print("Optimization Suggestions:")
            print("-" * 40)
            for i, s in enumerate(analysis["suggestions"], 1):
                print(f"{i}. {s['action']}")
                if "description" in s:
                    print(f"   {s['description']}")
                if s.get("files"):
                    print(f"   Affected: {len(s['files'])} files")
        else:
            print("No optimization suggestions.")
    elif args.report:
        print(generate_report(analysis))
    else:
        # Default: JSON output
        # Simplify for output
        output = {
            "summary": analysis["summary"],
            "issues": analysis["issues"],
            "suggestions": analysis["suggestions"],
            "large_files": [
                {"path": f["path"], "size": f["size_human"]}
                for f in analysis["files"]["by_size_bracket"]["large"][:10]
            ],
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
