#!/usr/bin/env python3
"""Batch File Processor.

Processes files in batches to reduce context overhead from individual file operations.
Instead of loading each file separately, processes groups of files and returns summaries.

Usage:
    python batch_file_processor.py <directory> <pattern> [--batch-size N] [--output FORMAT]

Examples:
    # Process all .wfm files in test_data/
    python batch_file_processor.py test_data "*.wfm" --batch-size 20

    # Get summary of JSON files
    python batch_file_processor.py .coordination "*.json" --output summary

    # List files by size (for cleanup planning)
    python batch_file_processor.py . "*.md" --output sizes
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def get_file_info(path: Path) -> dict[str, Any]:
    """Get basic file information without reading contents."""
    try:
        stat = path.stat()
        return {
            "path": str(path),
            "name": path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": path.suffix,
        }
    except (OSError, PermissionError) as e:
        return {
            "path": str(path),
            "name": path.name,
            "error": str(e),
        }


def process_batch(
    files: list[Path], batch_num: int, total_batches: int
) -> dict[str, Any]:
    """Process a batch of files and return summary."""
    extensions: defaultdict[str, int] = defaultdict(int)
    batch_info: dict[str, Any] = {
        "batch": batch_num,
        "total_batches": total_batches,
        "file_count": len(files),
        "files": [],
        "total_size": 0,
        "extensions": extensions,
    }

    file_list: list[dict[str, Any]] = []
    total_size = 0

    for f in files:
        info = get_file_info(f)
        file_list.append(info)
        if "size" in info:
            total_size += info["size"]
        if "extension" in info:
            extensions[info["extension"]] += 1

    batch_info["files"] = file_list
    batch_info["total_size"] = total_size
    batch_info["extensions"] = dict(extensions)
    return batch_info


def format_size(size: int) -> str:
    """Format size in human-readable format."""
    size_float = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024
    return f"{size_float:.1f} TB"


def output_summary(batches: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate overall summary from all batches."""
    total_files = sum(b["file_count"] for b in batches)
    total_size = sum(b["total_size"] for b in batches)

    all_extensions: dict[str, int] = defaultdict(int)
    for batch in batches:
        for ext, count in batch["extensions"].items():
            all_extensions[ext] += count

    # Find largest files
    all_files = []
    for batch in batches:
        all_files.extend(batch["files"])

    largest = sorted(
        [f for f in all_files if "size" in f],
        key=lambda x: x["size"],
        reverse=True,
    )[:10]

    return {
        "summary": {
            "total_files": total_files,
            "total_size": total_size,
            "total_size_human": format_size(total_size),
            "batch_count": len(batches),
        },
        "extensions": dict(all_extensions),
        "largest_files": [
            {"path": f["path"], "size": format_size(f["size"])} for f in largest
        ],
    }


def output_sizes(batches: list[dict[str, Any]]) -> dict[str, Any]:
    """Output files sorted by size for cleanup planning."""
    all_files = []
    for batch in batches:
        all_files.extend(batch["files"])

    sorted_files = sorted(
        [f for f in all_files if "size" in f],
        key=lambda x: x["size"],
        reverse=True,
    )

    size_brackets: dict[str, list[dict[str, str]]] = {
        "over_1mb": [],
        "100kb_to_1mb": [],
        "10kb_to_100kb": [],
        "under_10kb": [],
    }

    for f in sorted_files:
        size = f["size"]
        entry = {"path": f["path"], "size": format_size(size)}

        if size > 1024 * 1024:
            size_brackets["over_1mb"].append(entry)
        elif size > 100 * 1024:
            size_brackets["100kb_to_1mb"].append(entry)
        elif size > 10 * 1024:
            size_brackets["10kb_to_100kb"].append(entry)
        else:
            size_brackets["under_10kb"].append(entry)

    return {
        "size_analysis": {
            "total_files": len(sorted_files),
            "over_1mb_count": len(size_brackets["over_1mb"]),
            "100kb_to_1mb_count": len(size_brackets["100kb_to_1mb"]),
        },
        "large_files": size_brackets["over_1mb"][:20],
        "medium_files": size_brackets["100kb_to_1mb"][:20],
    }


def main() -> None:
    """Process files in batches to reduce context overhead."""
    parser = argparse.ArgumentParser(
        description="Process files in batches to reduce context overhead"
    )
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("pattern", help="Glob pattern (e.g., '*.json', '**/*.md')")
    parser.add_argument(
        "--batch-size", "-b", type=int, default=50, help="Files per batch (default: 50)"
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["full", "summary", "sizes", "count"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument(
        "--max-batches",
        "-m",
        type=int,
        default=0,
        help="Max batches to process (0=all)",
    )

    args = parser.parse_args()

    # Find files
    base_path = Path(args.directory)
    if not base_path.exists():
        print(json.dumps({"error": f"Directory not found: {args.directory}"}))
        sys.exit(1)

    files = list(base_path.glob(args.pattern))
    total_files = len(files)

    if total_files == 0:
        print(
            json.dumps(
                {
                    "message": "No files found",
                    "directory": str(base_path),
                    "pattern": args.pattern,
                }
            )
        )
        return

    # Quick count mode
    if args.output == "count":
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        print(
            json.dumps(
                {
                    "file_count": total_files,
                    "total_size": total_size,
                    "total_size_human": format_size(total_size),
                }
            )
        )
        return

    # Process in batches
    batches = []
    batch_size = args.batch_size
    total_batches = (total_files + batch_size - 1) // batch_size

    if args.max_batches > 0:
        total_batches = min(total_batches, args.max_batches)

    for i in range(total_batches):
        start = i * batch_size
        end = min(start + batch_size, total_files)
        batch_files = files[start:end]
        batch_result = process_batch(batch_files, i + 1, total_batches)
        batches.append(batch_result)

    # Output based on format
    if args.output == "full":
        result = {
            "directory": str(base_path),
            "pattern": args.pattern,
            "batches": batches,
        }
    elif args.output == "sizes":
        result = output_sizes(batches)
    else:  # summary
        result = output_summary(batches)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
