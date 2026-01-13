"""Command-line interface for SpreadsheetDL.

PUBLIC API ENTRY POINT
----------------------
This module is the public API entry point for the CLI functionality.
It supports two invocation methods:

    1. Module invocation: `python -m spreadsheet_dl` (uses this file's __main__ block)
    2. Entry point: `spreadsheet-dl` command (uses _cli/app.py:main via pyproject.toml)

Implementation is modularized in the _cli package:

    - _cli/utils.py: Validation, confirmation, and utility functions
    - _cli/commands.py: Command handler implementations
    - _cli/app.py: Main application setup and argument parsing

New in v4.0.0:

New in v0.6.0 (Phase 3: Enhanced Features):

New in v0.5.0:
    - DR-STORE-002: Backup/restore functionality
"""

from __future__ import annotations

import sys

# Re-export everything from the modularized _cli package
from spreadsheet_dl._cli import (
    confirm_action,
    confirm_delete,
    confirm_destructive_operation,
    confirm_overwrite,
    main,
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


if __name__ == "__main__":
    sys.exit(main())
