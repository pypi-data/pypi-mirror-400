#!/usr/bin/env python3
"""JSON Summarizer.

Extracts key metrics from large JSON files without loading entire contents into context.
Provides compact summaries suitable for context-limited environments.

Usage:
    python json_summarizer.py <file.json> [--keys key1,key2] [--max-depth N]

Examples:
    # Get summary of a validation report
    python json_summarizer.py validation_report.json

    # Extract specific keys
    python json_summarizer.py report.json --keys status,error_count,pass_rate

    # Limit depth for nested structures
    python json_summarizer.py complex.json --max-depth 2
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def format_size(size: int) -> str:
    """Format size in human-readable format."""
    size_float = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024
    return f"{size_float:.1f} TB"


def get_type_name(value: Any) -> str:
    """Get a simple type name for a value."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        return f"array[{len(value)}]"
    elif isinstance(value, dict):
        return f"object[{len(value)} keys]"
    return type(value).__name__


def summarize_value(value: Any, max_depth: int = 2, current_depth: int = 0) -> Any:
    """Create a compact summary of a value."""
    if current_depth >= max_depth:
        return f"<{get_type_name(value)}>"

    if value is None or isinstance(value, (bool, int, float)):
        return value
    elif isinstance(value, str):
        if len(value) > 100:
            return f"{value[:100]}... ({len(value)} chars)"
        return value
    elif isinstance(value, list):
        if len(value) == 0:
            return []
        if len(value) <= 3:
            return [summarize_value(v, max_depth, current_depth + 1) for v in value]
        # Show first item and count
        first = summarize_value(value[0], max_depth, current_depth + 1)
        return [first, f"... and {len(value) - 1} more items"]
    elif isinstance(value, dict):
        if len(value) == 0:
            return {}
        if len(value) <= 5:
            return {
                k: summarize_value(v, max_depth, current_depth + 1)
                for k, v in list(value.items())[:5]
            }
        # Show first few keys
        summary = {
            k: summarize_value(v, max_depth, current_depth + 1)
            for k, v in list(value.items())[:3]
        }
        summary["__remaining__"] = f"{len(value) - 3} more keys"
        return summary
    return f"<{get_type_name(value)}>"


def extract_metrics(data: Any, prefix: str = "") -> dict[str, Any]:
    """Extract metrics-like values from JSON structure."""
    metrics = {}

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # Check if this looks like a metric
            metric_keywords = [
                "count",
                "total",
                "rate",
                "percentage",
                "percent",
                "error",
                "success",
                "fail",
                "pass",
                "score",
                "size",
                "time",
                "duration",
                "status",
            ]

            key_lower = key.lower()
            is_metric = any(kw in key_lower for kw in metric_keywords)

            if is_metric and isinstance(value, (int, float, str, bool)):
                metrics[full_key] = value
            elif isinstance(value, dict):
                metrics.update(extract_metrics(value, full_key))
            elif isinstance(value, list) and len(value) > 0 and is_metric:
                # For lists, just note the count
                metrics[f"{full_key}_count"] = len(value)

    return metrics


def analyze_structure(
    data: Any, max_depth: int = 3, current_depth: int = 0
) -> dict[str, Any]:
    """Analyze the structure of JSON data."""
    if current_depth >= max_depth:
        return {"type": get_type_name(data)}

    if isinstance(data, dict):
        return {
            "type": "object",
            "key_count": len(data),
            "keys": list(data.keys())[:20],
            "sample_structure": {
                k: analyze_structure(v, max_depth, current_depth + 1)
                for k, v in list(data.items())[:5]
            },
        }
    elif isinstance(data, list):
        if len(data) == 0:
            return {"type": "array", "length": 0}
        return {
            "type": "array",
            "length": len(data),
            "item_type": get_type_name(data[0]),
            "sample_item": analyze_structure(data[0], max_depth, current_depth + 1)
            if len(data) > 0
            else None,
        }
    else:
        return {"type": get_type_name(data), "value": summarize_value(data, 1)}


def extract_keys(data: Any, keys: list[str]) -> dict[str, Any]:
    """Extract specific keys from JSON data."""
    result = {}

    for key in keys:
        parts = key.split(".")
        current = data

        try:
            for part in parts:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list) and part.isdigit():
                    current = current[int(part)]
                else:
                    current = None
                    break

            if current is not None:
                result[key] = summarize_value(current, max_depth=2)
        except (KeyError, IndexError, TypeError):
            result[key] = "<not found>"

    return result


def summarize_json_file(
    file_path: Path, keys: list[str] | None = None, max_depth: int = 2
) -> dict[str, Any]:
    """Generate a summary of a JSON file."""
    # File info
    stat = file_path.stat()
    file_info = {
        "file": str(file_path),
        "size": stat.st_size,
        "size_human": format_size(stat.st_size),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }

    # Load and analyze
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            **file_info,
            "error": f"Invalid JSON: {e}",
        }
    except Exception as e:
        return {
            **file_info,
            "error": str(e),
        }

    # Build summary
    summary: dict[str, Any] = {
        **file_info,
        "root_type": get_type_name(data),
    }

    # Extract specific keys if requested
    if keys:
        summary["extracted_keys"] = extract_keys(data, keys)
    else:
        # Auto-extract metrics
        metrics = extract_metrics(data)
        if metrics:
            summary["metrics"] = metrics

    # Structure analysis
    summary["structure"] = analyze_structure(data, max_depth)

    # Compact preview
    summary["preview"] = summarize_value(data, max_depth)

    return summary


def main() -> None:
    """Extract key metrics from large JSON files."""
    parser = argparse.ArgumentParser(
        description="Extract key metrics from large JSON files"
    )
    parser.add_argument("file", help="JSON file to summarize")
    parser.add_argument(
        "--keys",
        "-k",
        help="Comma-separated list of keys to extract (supports dot notation)",
    )
    parser.add_argument(
        "--max-depth",
        "-d",
        type=int,
        default=2,
        help="Maximum depth for structure analysis (default: 2)",
    )
    parser.add_argument(
        "--metrics-only",
        "-m",
        action="store_true",
        help="Only output extracted metrics",
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(json.dumps({"error": f"File not found: {args.file}"}))
        sys.exit(1)

    keys = args.keys.split(",") if args.keys else None
    summary = summarize_json_file(file_path, keys, args.max_depth)

    if args.metrics_only and "metrics" in summary:
        print(json.dumps(summary["metrics"], indent=2))
    else:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
