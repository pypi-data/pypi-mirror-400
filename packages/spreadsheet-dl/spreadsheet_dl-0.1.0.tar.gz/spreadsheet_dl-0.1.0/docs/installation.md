# Installation Guide

This guide covers installing SpreadsheetDL for development and production use.

## Requirements

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

## Quick Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/lair-click-bats/spreadsheet-dl.git
cd spreadsheet-dl

# Install dependencies
uv sync

# Verify installation
uv run spreadsheet-dl --version
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/lair-click-bats/spreadsheet-dl.git
cd spreadsheet-dl

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
uv pip install -e .

# Verify installation
spreadsheet-dl --version
```

## Optional Dependencies

### Theme Support

For YAML-based themes, install with the config extra:

```bash
uv sync --extra config
# or
uv pip install -e ".[config]"
```

### Development Dependencies

For development and testing:

```bash
uv sync --dev
# or
uv pip install -e ".[dev]"
```

This includes:

- pytest - Testing framework
- pytest-cov - Coverage reporting
- ruff - Linting and formatting
- mypy - Type checking

## Verification

After installation, verify everything works:

```bash
# Check version
uv run spreadsheet-dl --version

# Run tests
uv run pytest

# Generate a test budget
uv run spreadsheet-dl generate -o /tmp/test/
```

## Environment Configuration

### Nextcloud Integration

For WebDAV upload functionality, set these environment variables:

```bash
export NEXTCLOUD_URL=https://your-nextcloud.com
export NEXTCLOUD_USER=username
export NEXTCLOUD_PASSWORD=app-password
export NEXTCLOUD_PATH=/Finance  # Optional, default: /Finance
```

### Configuration File

Alternatively, create a configuration file:

```bash
uv run spreadsheet-dl config --init
```

This creates `~/.config/spreadsheet-dl/config.yaml`.

## Platform-Specific Notes

### Linux

No special requirements. Ensure Python 3.12+ is available:

```bash
python3 --version
```

### macOS

Install Python via Homebrew if needed:

```bash
brew install python@3.12
```

### Windows

Install Python from [python.org](https://www.python.org/downloads/) or via Windows Store.

Use PowerShell for commands:

```powershell
uv run spreadsheet-dl --version
```

## Troubleshooting

### Import Errors

If you see import errors, ensure the package is installed in development mode:

```bash
uv pip install -e .
```

### Missing Dependencies

If optional features fail, install extras:

```bash
# For theme support
uv sync --extra config

# For development
uv sync --dev
```

### Permission Issues

On Linux/macOS, if you get permission errors:

```bash
# Use user installation
uv pip install --user -e .
```

### Path Issues

Ensure the installed scripts are in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

## Next Steps

After installation:

1. Read the [User Guide](user-guide.md) for comprehensive usage
2. Check [Examples](examples/index.md) for practical use cases
3. Review the [API Reference](api/index.md) for programmatic access
