"""Theme definitions package.

Contains YAML theme files and provides access to built-in themes.
"""

from pathlib import Path

# Theme directory location
THEMES_DIR = Path(__file__).parent

# List of built-in themes
BUILTIN_THEMES = [
    "default",
    "corporate",
    "minimal",
    "dark",
    "high_contrast",
]


def get_theme_path(name: str) -> Path:
    """Get the path to a theme file.

    Args:
        name: Theme name

    Returns:
        Path to theme YAML file

    Raises:
        FileNotFoundError: If theme not found
    """
    path = THEMES_DIR / f"{name}.yaml"
    if path.exists():
        return path

    # Try .yml extension
    path = THEMES_DIR / f"{name}.yml"
    if path.exists():
        return path

    raise FileNotFoundError(f"Theme not found: {name}")


def list_builtin_themes() -> list[str]:
    """List all built-in theme names.

    Returns:
        List of theme names
    """
    themes = []
    for path in THEMES_DIR.glob("*.yaml"):
        themes.append(path.stem)
    for path in THEMES_DIR.glob("*.yml"):
        if path.stem not in themes:
            themes.append(path.stem)
    return sorted(themes)
