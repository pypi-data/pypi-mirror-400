#!/usr/bin/env bash
# =============================================================================
# Dependency Checker for Workspace Template
# =============================================================================
# Verifies all required and optional tools are available
# Usage: ./scripts/check_dependencies.sh [--verbose]
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

log_ok() {
  local tool=$1
  local version=${2:-""}
  if [[ -n "${version}" ]]; then
    echo -e "  ${GREEN}+${NC} ${tool} ${CYAN}(${version})${NC}"
  else
    echo -e "  ${GREEN}+${NC} ${tool}"
  fi
}

log_missing() {
  local tool=$1
  echo -e "  ${RED}x${NC} ${tool} ${RED}(not found)${NC}"
}

log_optional() {
  local tool=$1
  echo -e "  ${YELLOW}o${NC} ${tool} ${YELLOW}(optional, not found)${NC}"
}

check_command() {
  command -v "$1" &>/dev/null
}

get_version() {
  local cmd=$1
  local version_flag=${2:---version}
  "${cmd}" "${version_flag}" 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "unknown"
}

# =============================================================================
# Parse Arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
  case $1 in
  -h | --help)
    echo "Usage: $0"
    echo ""
    echo "Checks for required and optional development tools."
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    exit 0
    ;;
  *)
    echo "Unknown option: $1"
    exit 1
    ;;
  esac
done

# =============================================================================
# Required Dependencies
# =============================================================================

echo ""
echo -e "${BLUE}Required Dependencies${NC}"
echo "─────────────────────────────────────────"

REQUIRED_MISSING=0

# Python
if check_command python3; then
  VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
  log_ok "Python 3" "${VERSION}"
else
  log_missing "Python 3"
  ((REQUIRED_MISSING++))
fi

# uv
if check_command uv; then
  VERSION=$(get_version uv)
  log_ok "uv" "${VERSION}"
else
  log_missing "uv"
  ((REQUIRED_MISSING++))
fi

# Git
if check_command git; then
  VERSION=$(get_version git)
  log_ok "Git" "${VERSION}"
else
  log_missing "Git"
  ((REQUIRED_MISSING++))
fi

# =============================================================================
# Python Packages (via uv)
# =============================================================================

echo ""
echo -e "${BLUE}Python Packages${NC}"
echo "─────────────────────────────────────────"

if check_command uv; then
  # Check if virtual environment exists and packages are installed
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

  if [[ -d "${REPO_ROOT}/.venv" ]]; then
    # pyyaml
    if uv run python -c "import yaml" 2>/dev/null; then
      VERSION=$(uv run python -c "import yaml; print(yaml.__version__)" 2>/dev/null || echo "unknown")
      log_ok "pyyaml" "${VERSION}"
    else
      log_missing "pyyaml"
    fi

    # jinja2
    if uv run python -c "import jinja2" 2>/dev/null; then
      VERSION=$(uv run python -c "import jinja2; print(jinja2.__version__)" 2>/dev/null || echo "unknown")
      log_ok "jinja2" "${VERSION}"
    else
      log_missing "jinja2"
    fi

    # pytest (dev)
    if uv run python -c "import pytest" 2>/dev/null; then
      VERSION=$(uv run python -c "import pytest; print(pytest.__version__)" 2>/dev/null || echo "unknown")
      log_ok "pytest" "${VERSION}"
    else
      log_optional "pytest (dev dependency)"
    fi
  else
    echo -e "  ${YELLOW}o${NC} Virtual environment not found. Run: ./scripts/setup.sh"
  fi
else
  echo -e "  ${RED}x${NC} Cannot check packages without uv"
fi

# =============================================================================
# Text Search & PDF Tools (optional)
# =============================================================================

echo ""
echo -e "${BLUE}Text Search & PDF Tools${NC}"
echo "─────────────────────────────────────────"

# ripgrep (fastest text search)
if check_command rg; then
  VERSION=$(rg --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "ripgrep (rg)" "${VERSION}"
else
  log_optional "ripgrep (recommended for fast search)"
fi

# The Silver Searcher
if check_command ag; then
  VERSION=$(ag --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "ag (silver_searcher)" "${VERSION}"
else
  log_optional "ag (alternative to ripgrep)"
fi

# pdfgrep
if check_command pdfgrep; then
  VERSION=$(pdfgrep --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "pdfgrep" "${VERSION}"
else
  log_optional "pdfgrep (PDF text search)"
fi

# poppler-utils (pdftotext, pdfinfo)
if check_command pdftotext; then
  VERSION=$(pdftotext -v 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "pdftotext (poppler)" "${VERSION}"
else
  log_optional "pdftotext (PDF text extraction)"
fi

if check_command pdfinfo; then
  log_ok "pdfinfo (poppler)"
else
  log_optional "pdfinfo (PDF metadata)"
fi

# OCR tools
if check_command ocrmypdf; then
  VERSION=$(ocrmypdf --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "ocrmypdf" "${VERSION}"
else
  log_optional "ocrmypdf (PDF OCR)"
fi

if check_command tesseract; then
  VERSION=$(tesseract --version 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "tesseract" "${VERSION}"
else
  log_optional "tesseract (OCR engine)"
fi

# =============================================================================
# Optional Tools (for development)
# =============================================================================

echo ""
echo -e "${BLUE}Optional Development Tools${NC}"
echo "─────────────────────────────────────────"

# pre-commit
if check_command pre-commit; then
  VERSION=$(get_version pre-commit)
  log_ok "pre-commit" "${VERSION}"
else
  log_optional "pre-commit"
fi

# prettier
if check_command prettier; then
  VERSION=$(get_version prettier)
  log_ok "prettier" "${VERSION}"
else
  log_optional "prettier"
fi

# markdownlint-cli2
if check_command markdownlint-cli2; then
  log_ok "markdownlint-cli2"
else
  log_optional "markdownlint-cli2"
fi

# yamllint
if check_command yamllint; then
  VERSION=$(yamllint --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "yamllint" "${VERSION}"
else
  log_optional "yamllint"
fi

# ShellCheck (shell script linter)
if check_command shellcheck; then
  VERSION=$(shellcheck --version 2>/dev/null | grep version: | awk '{print $2}' || echo "unknown")
  log_ok "shellcheck" "${VERSION}"
else
  log_optional "shellcheck"
fi

# ruff (standalone)
if check_command ruff; then
  VERSION=$(get_version ruff)
  log_ok "ruff (standalone)" "${VERSION}"
else
  log_optional "ruff (standalone)"
fi

# jq (JSON processor)
if check_command jq; then
  VERSION=$(jq --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "jq" "${VERSION}"
else
  log_optional "jq"
fi

# xmllint (XML validation)
if check_command xmllint; then
  VERSION=$(xmllint --version 2>&1 | grep -oE '[0-9]+' | head -1 || echo "unknown")
  log_ok "xmllint" "${VERSION}"
else
  log_optional "xmllint"
fi

# =============================================================================
# Diagram Tools (optional)
# =============================================================================

echo ""
echo -e "${BLUE}Diagram Tools${NC}"
echo "─────────────────────────────────────────"

# PlantUML
if check_command plantuml; then
  VERSION=$(plantuml -version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "unknown")
  log_ok "plantuml" "${VERSION}"
else
  log_optional "plantuml"
fi

# Mermaid CLI
if check_command mmdc; then
  VERSION=$(mmdc --version 2>/dev/null || echo "unknown")
  log_ok "mermaid-cli (mmdc)" "${VERSION}"
else
  log_optional "mermaid-cli"
fi

# Graphviz (used by PlantUML)
if check_command dot; then
  VERSION=$(dot -V 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "graphviz (dot)" "${VERSION}"
else
  log_optional "graphviz"
fi

# =============================================================================
# Image Processing Tools (optional)
# =============================================================================

echo ""
echo -e "${BLUE}Image Processing Tools${NC}"
echo "─────────────────────────────────────────"

# ImageMagick (magick or convert)
if check_command magick; then
  VERSION=$(magick --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+-[0-9]+' | head -1 || echo "unknown")
  log_ok "ImageMagick 7 (magick)" "${VERSION}"
elif check_command convert; then
  VERSION=$(convert --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+-[0-9]+' | head -1 || echo "unknown")
  log_ok "ImageMagick 6 (convert)" "${VERSION}"
else
  log_optional "ImageMagick"
fi

# Inkscape
if check_command inkscape; then
  VERSION=$(inkscape --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1 || echo "unknown")
  log_ok "Inkscape" "${VERSION}"
else
  log_optional "Inkscape"
fi

# VTracer (bitmap to vector)
if check_command vtracer; then
  VERSION=$(vtracer --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "vtracer" "${VERSION}"
else
  log_optional "vtracer (bitmap vectorization)"
fi

# SVGO (SVG optimizer)
if check_command svgo; then
  VERSION=$(svgo --version 2>/dev/null || echo "unknown")
  log_ok "svgo" "${VERSION}"
else
  log_optional "svgo"
fi

# potrace (bitmap tracing)
if check_command potrace; then
  VERSION=$(potrace --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+' || echo "unknown")
  log_ok "potrace" "${VERSION}"
else
  log_optional "potrace"
fi

# ExifTool (metadata)
if check_command exiftool; then
  VERSION=$(exiftool -ver 2>/dev/null || echo "unknown")
  log_ok "exiftool" "${VERSION}"
else
  log_optional "exiftool"
fi

# =============================================================================
# VS Code (for extension installation)
# =============================================================================

echo ""
echo -e "${BLUE}VS Code / Editor${NC}"
echo "─────────────────────────────────────────"

if check_command code; then
  VERSION=$(code --version 2>/dev/null | head -1 || echo "unknown")
  log_ok "VS Code" "${VERSION}"
elif check_command code-insiders; then
  VERSION=$(code-insiders --version 2>/dev/null | head -1 || echo "unknown")
  log_ok "VS Code Insiders" "${VERSION}"
elif check_command codium; then
  VERSION=$(codium --version 2>/dev/null | head -1 || echo "unknown")
  log_ok "VSCodium" "${VERSION}"
else
  log_optional "VS Code / VSCodium"
fi

# =============================================================================
# Summary
# =============================================================================

echo ""
echo "─────────────────────────────────────────"

if [[ ${REQUIRED_MISSING} -eq 0 ]]; then
  echo -e "${GREEN}All required dependencies are installed!${NC}"
  echo ""
  echo "To install optional tools:"
  echo "  pre-commit:       uv tool install pre-commit"
  echo "  prettier:         npm install -g prettier"
  echo "  markdownlint:     npm install -g markdownlint-cli2"
  echo "  yamllint:         uv tool install yamllint"
  echo "  shellcheck:       apt install shellcheck"
  echo "  jq:               apt install jq"
  echo "  xmllint:          apt install libxml2-utils"
  echo ""
  echo "Text search & PDF tools:"
  echo "  ripgrep:          apt install ripgrep"
  echo "  pdfgrep:          apt install pdfgrep"
  echo "  poppler-utils:    apt install poppler-utils"
  echo "  ocrmypdf:         apt install ocrmypdf (or pip install ocrmypdf)"
  echo "  tesseract:        apt install tesseract-ocr tesseract-ocr-eng"
  echo ""
  echo "Diagram tools:"
  echo "  plantuml:         apt install plantuml"
  echo "  mermaid-cli:      npm install -g @mermaid-js/mermaid-cli"
  echo "  graphviz:         apt install graphviz"
  echo ""
  echo "Image processing:"
  echo "  ImageMagick:      apt install imagemagick"
  echo "  Inkscape:         apt install inkscape"
  echo "  vtracer:          cargo install vtracer (or pip install vtracer)"
  echo "  svgo:             npm install -g svgo"
  echo "  potrace:          apt install potrace"
  echo "  exiftool:         apt install libimage-exiftool-perl"
  exit 0
else
  echo -e "${RED}Missing ${REQUIRED_MISSING} required dependencies!${NC}"
  echo ""
  echo "Installation instructions:"
  echo "  Python 3.11+:  https://www.python.org/downloads/"
  echo "  uv:            curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "  Git:           apt install git (or equivalent)"
  exit 1
fi
