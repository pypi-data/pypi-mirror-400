"""Generate API reference pages automatically from source code.

This script is used by mkdocs-gen-files to automatically generate
API documentation pages from the Python source code. It creates
markdown files with mkdocstrings directives for each public module.

The generated pages follow the structure of the source code and
create a literate navigation structure via SUMMARY.md.
"""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()  # type: ignore[attr-defined, no-untyped-call]

# Source directory containing the package
src = Path(__file__).parent.parent / "src" / "spreadsheet_dl"

# Skip these patterns (internal/private modules)
SKIP_PATTERNS = {
    "__pycache__",
    ".pyc",
}

# Modules to explicitly include at top level
TOP_LEVEL_MODULES = {
    "__init__",
    "builder",
    "charts",
    "export",
    "streaming",
    "mcp_server",
    "exceptions",
    "plugins",
    "adapters",
    "serialization",
    "renderer",
    "performance",
    "config",
    "templates",
    "visualization",
}


def should_skip(path: Path) -> bool:
    """Check if a path should be skipped."""
    name = path.name
    # Skip private modules (except __init__)
    if name.startswith("_") and name != "__init__.py":
        return True
    # Skip pycache and compiled files
    return any(pattern in str(path) for pattern in SKIP_PATTERNS)


def get_module_identifier(path: Path, base: Path) -> str:
    """Get the full module identifier from a path."""
    relative = path.relative_to(base)
    parts = list(relative.with_suffix("").parts)
    return ".".join(["spreadsheet_dl", *parts])


# Process all Python files
for path in sorted(src.rglob("*.py")):
    if should_skip(path):
        continue

    # Get relative path from src
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("api", doc_path)

    parts = tuple(module_path.parts)

    # Handle __init__.py files - use parent directory name
    if parts[-1] == "__init__":
        parts = parts[:-1]
        if not parts:
            # Root __init__ -> api/index.md
            full_doc_path = Path("api", "module.md")
            doc_path = Path("module.md")
            parts = ("spreadsheet_dl",)

    # Skip empty parts
    if not parts:
        continue

    # Add to navigation
    nav[parts] = doc_path.as_posix()

    # Generate the documentation page
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = get_module_identifier(path, src)
        # Clean up identifier for __init__ files
        if identifier.endswith(".__init__"):
            identifier = identifier[:-9]

        fd.write(f"# `{identifier}`\n\n")
        fd.write(f"::: {identifier}\n")

    # Set edit path to the source file
    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(src.parent.parent))

# Write the navigation file
with mkdocs_gen_files.open("api/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
