"""CLI package - Command-line interface for SpreadsheetDL.

This package contains the modularized implementation of the CLI:
    - utils.py: Validation, confirmation, and utility functions
    - commands.py: Command handler implementations
    - app.py: Main application setup and argument parsing

All public APIs are exported here for backward compatibility and clean imports.

Public API:
    - main(): Main CLI entry point
    - confirm_action(): General confirmation prompt
    - confirm_overwrite(): File overwrite confirmation
    - confirm_delete(): File deletion confirmation
    - confirm_destructive_operation(): Generic destructive operation confirmation
    - validate_amount(): Parse and validate monetary amounts
    - validate_date(): Parse and validate date strings
"""

from __future__ import annotations

# Main entry point
from spreadsheet_dl._cli.app import main

# Utility functions (confirmation and validation)
from spreadsheet_dl._cli.utils import (
    confirm_action,
    confirm_delete,
    confirm_destructive_operation,
    confirm_overwrite,
    validate_amount,
    validate_date,
)

__all__ = [
    "confirm_action",
    "confirm_delete",
    "confirm_destructive_operation",
    "confirm_overwrite",
    "main",
    "validate_amount",
    "validate_date",
]
