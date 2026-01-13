"""Path validation utilities for preventing path traversal attacks.

Provides secure path handling to prevent directory traversal, symlink attacks,
and unauthorized file access.

Security Features:
    - Path traversal prevention (../ attacks)
    - Symlink attack detection
    - Absolute path validation
    - Base directory enforcement
"""

from __future__ import annotations

from pathlib import Path

__all__ = [
    "PathSecurityError",
    "is_safe_path",
    "safe_join",
    "validate_path",
]


class PathSecurityError(ValueError):
    """Raised when a path fails security validation.

    This exception indicates a potential security attack such as:
    - Path traversal (../../etc/passwd)
    - Symlink attack
    - Access outside allowed base directory
    """

    pass


def validate_path(
    base_dir: Path | str,
    user_path: Path | str,
    *,
    allow_symlinks: bool = False,
    must_exist: bool = False,
) -> Path:
    """Validate that a user-provided path is safe to use.

    Prevents path traversal attacks by ensuring the resolved path
    is within the base directory.

    Args:
        base_dir: Base directory that user_path must be within
        user_path: User-provided path to validate
        allow_symlinks: Whether to allow symlink paths (default: False)
        must_exist: Whether the path must already exist (default: False)

    Returns:
        Validated absolute Path object

    Raises:
        PathSecurityError: If path fails security validation
        FileNotFoundError: If must_exist=True and path doesn't exist

    Examples:
        >>> validate_path("/data", "file.txt")  # doctest: +SKIP
        PosixPath('/data/file.txt')

        >>> validate_path("/data", "../etc/passwd")  # doctest: +SKIP
        PathSecurityError: Path traversal detected

        >>> validate_path("/data", "/etc/passwd")  # doctest: +SKIP
        PathSecurityError: Absolute paths not allowed
    """
    base_dir = Path(base_dir).resolve()
    user_path = Path(user_path)

    # Reject absolute paths from user input
    if user_path.is_absolute():
        raise PathSecurityError(
            f"Absolute paths not allowed: {user_path}. "
            "Use relative paths within the base directory."
        )

    # Combine to get the path (don't resolve yet to check for symlinks)
    combined_path = base_dir / user_path

    # Check for symlinks if not allowed (before resolving)
    if not allow_symlinks and combined_path.is_symlink():
        raise PathSecurityError(
            f"Symlink not allowed: {user_path}. "
            "Symlinks can be used for directory traversal attacks."
        )

    # Resolve to check if path would be within base directory
    resolved_path = combined_path.resolve()
    try:
        resolved_path.relative_to(base_dir)
    except ValueError as e:
        raise PathSecurityError(
            f"Path traversal detected: {user_path} resolves outside base directory"
        ) from e

    # Check existence if required
    if must_exist and not combined_path.exists():
        raise FileNotFoundError(f"Path does not exist: {combined_path}")

    # Return the combined path (not resolved, to preserve symlinks if allowed)
    return combined_path


def safe_join(base_dir: Path | str, *parts: str, allow_symlinks: bool = False) -> Path:
    """Safely join path components, preventing traversal attacks.

    Similar to Path.joinpath() but with security validation.

    Args:
        base_dir: Base directory
        *parts: Path components to join
        allow_symlinks: Whether to allow symlinks (default: False)

    Returns:
        Validated absolute Path object

    Raises:
        PathSecurityError: If resulting path is outside base directory

    Examples:
        >>> safe_join("/data", "subdir", "file.txt")  # doctest: +SKIP
        PosixPath('/data/subdir/file.txt')

        >>> safe_join("/data", "..", "etc", "passwd")  # doctest: +SKIP
        PathSecurityError: Path traversal detected
    """
    if not parts:
        return Path(base_dir).resolve()

    # Join all parts
    user_path = Path(*parts)

    # Validate the combined path
    return validate_path(base_dir, user_path, allow_symlinks=allow_symlinks)


def is_safe_path(
    base_dir: Path | str,
    user_path: Path | str,
    *,
    allow_symlinks: bool = False,
) -> bool:
    """Check if a path is safe without raising an exception.

    Non-throwing version of validate_path() for conditional checks.

    Args:
        base_dir: Base directory
        user_path: User-provided path
        allow_symlinks: Whether to allow symlinks (default: False)

    Returns:
        True if path is safe, False otherwise

    Examples:
        >>> is_safe_path("/data", "file.txt")  # doctest: +SKIP
        True

        >>> is_safe_path("/data", "../etc/passwd")  # doctest: +SKIP
        False
    """
    try:
        validate_path(base_dir, user_path, allow_symlinks=allow_symlinks)
        return True
    except (PathSecurityError, ValueError):
        return False
