"""CLI utility functions for SpreadsheetDL.

Contains validation, formatting, and confirmation utilities used across CLI commands.

"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

from spreadsheet_dl.exceptions import InvalidAmountError, InvalidDateError

if TYPE_CHECKING:
    from pathlib import Path

# =============================================================================
# Confirmation Prompt Utilities
# =============================================================================


def confirm_action(
    message: str,
    *,
    default: bool = False,
    skip_confirm: bool = False,
) -> bool:
    """Prompt user for confirmation before destructive actions.

    Args:
        message: Description of the action to confirm.
        default: Default response if user just presses Enter.
        skip_confirm: If True, skip confirmation and return True.

    Returns:
        True if action is confirmed, False otherwise.

    """
    if skip_confirm:
        return True

    # Non-interactive mode check
    if not sys.stdin.isatty():
        return default

    prompt_suffix = " [Y/n]" if default else " [y/N]"
    full_prompt = f"{message}{prompt_suffix}: "

    try:
        response = input(full_prompt).strip().lower()
        if not response:
            return default
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def confirm_overwrite(file_path: Path, *, skip_confirm: bool = False) -> bool:
    """Confirm overwriting an existing file.

    Args:
        file_path: Path to the file that would be overwritten.
        skip_confirm: If True, skip confirmation.

    Returns:
        True if overwrite is confirmed.
    """
    if not file_path.exists():
        return True

    return confirm_action(
        f"File '{file_path}' already exists. Overwrite?",
        default=False,
        skip_confirm=skip_confirm,
    )


def confirm_delete(file_path: Path, *, skip_confirm: bool = False) -> bool:
    """Confirm deleting a file.

    Args:
        file_path: Path to the file to delete.
        skip_confirm: If True, skip confirmation.

    Returns:
        True if deletion is confirmed.
    """
    return confirm_action(
        f"Delete '{file_path}'? This cannot be undone.",
        default=False,
        skip_confirm=skip_confirm,
    )


def confirm_destructive_operation(
    operation: str,
    details: str | None = None,
    *,
    skip_confirm: bool = False,
) -> bool:
    """Confirm a potentially destructive operation.

    Args:
        operation: Name of the operation.
        details: Additional details about what will happen.
        skip_confirm: If True, skip confirmation.

    Returns:
        True if operation is confirmed.
    """
    message = f"Proceed with {operation}?"
    if details:
        print(f"\n{details}")
    return confirm_action(message, default=False, skip_confirm=skip_confirm)


# =============================================================================
# Validation Functions
# =============================================================================


def validate_amount(amount_str: str) -> Decimal:
    """Validate and parse an amount string.

    Args:
        amount_str: Amount string (may include $ and commas)

    Returns:
        Parsed Decimal amount

    Raises:
        InvalidAmountError: If amount is invalid
    """
    cleaned = amount_str.replace("$", "").replace(",", "").strip()

    if not cleaned:
        raise InvalidAmountError(amount_str, "Empty value")

    try:
        amount = Decimal(cleaned)
    except InvalidOperation as e:
        raise InvalidAmountError(amount_str, "Not a valid number") from e

    if amount < 0:
        raise InvalidAmountError(amount_str, "Amount cannot be negative")

    return amount


def validate_date(date_str: str) -> date:
    """Validate and parse a date string.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        Parsed date object

    Raises:
        InvalidDateError: If date is invalid
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError as e:
        raise InvalidDateError(date_str) from e
