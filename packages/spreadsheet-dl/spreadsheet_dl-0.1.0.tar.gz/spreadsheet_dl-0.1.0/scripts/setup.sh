#!/usr/bin/env bash
# =============================================================================
# Environment Setup Script for Workspace Template
# =============================================================================
# Initializes development environment with all required dependencies
# Usage: ./scripts/setup.sh [--dev] [--check-only]
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Flags
DEV_MODE=false
CHECK_ONLY=false

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    command -v "$1" &>/dev/null
}

# =============================================================================
# Argument Parsing
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
    --dev)
        DEV_MODE=true
        shift
        ;;
    --check-only)
        CHECK_ONLY=true
        shift
        ;;
    -h | --help)
        echo "Usage: $0 [--dev] [--check-only]"
        echo ""
        echo "Options:"
        echo "  --dev        Install development dependencies"
        echo "  --check-only Only check dependencies, don't install"
        echo "  -h, --help   Show this help message"
        exit 0
        ;;
    *)
        log_error "Unknown option: $1"
        exit 1
        ;;
    esac
done

# =============================================================================
# Dependency Checks
# =============================================================================

log_info "Checking required dependencies..."

MISSING_DEPS=()

# Python 3.11+
if check_command python3; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo "${PYTHON_VERSION}" | cut -d. -f1)
    PYTHON_MINOR=$(echo "${PYTHON_VERSION}" | cut -d. -f2)
    if [[ "${PYTHON_MAJOR}" -ge 3 && "${PYTHON_MINOR}" -ge 11 ]]; then
        log_success "Python ${PYTHON_VERSION}"
    else
        log_warning "Python ${PYTHON_VERSION} (3.11+ recommended)"
    fi
else
    log_error "Python 3 not found"
    MISSING_DEPS+=("python3")
fi

# uv package manager
if check_command uv; then
    UV_VERSION=$(uv --version 2>/dev/null | head -1)
    log_success "uv: ${UV_VERSION}"
else
    log_error "uv not found"
    MISSING_DEPS+=("uv")
fi

# Git
if check_command git; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    log_success "Git ${GIT_VERSION}"
else
    log_error "Git not found"
    MISSING_DEPS+=("git")
fi

# Optional: pre-commit
if check_command pre-commit; then
    PRECOMMIT_VERSION=$(pre-commit --version | cut -d' ' -f2)
    log_success "pre-commit ${PRECOMMIT_VERSION}"
else
    log_warning "pre-commit not found (optional, install with: uv tool install pre-commit)"
fi

# Optional: check-jsonschema (for VS Code settings validation)
if check_command check-jsonschema; then
    JSONSCHEMA_VERSION=$(check-jsonschema --version 2>/dev/null | head -1)
    log_success "check-jsonschema ${JSONSCHEMA_VERSION}"
else
    log_warning "check-jsonschema not found (optional, will be installed with --dev)"
fi

# Optional: prettier (for markdown formatting)
if check_command prettier; then
    PRETTIER_VERSION=$(prettier --version 2>/dev/null)
    log_success "prettier ${PRETTIER_VERSION}"
else
    log_warning "prettier not found (optional, install with: npm install -g prettier)"
fi

# Optional: markdownlint-cli2 (for markdown linting)
if check_command markdownlint-cli2; then
    log_success "markdownlint-cli2 installed"
else
    log_warning "markdownlint-cli2 not found (optional, install with: npm install -g markdownlint-cli2)"
fi

# Optional: shellcheck (for shell script linting)
if check_command shellcheck; then
    SHELLCHECK_VERSION=$(shellcheck --version | grep version: | cut -d' ' -f2)
    log_success "shellcheck ${SHELLCHECK_VERSION}"
else
    log_warning "shellcheck not found (optional, install with: apt install shellcheck)"
fi

# =============================================================================
# Check for Missing Critical Dependencies
# =============================================================================

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    log_error "Missing critical dependencies: ${MISSING_DEPS[*]}"
    echo ""
    echo "Installation instructions:"
    for dep in "${MISSING_DEPS[@]}"; do
        case ${dep} in
        python3)
            echo "  Python 3.11+: https://www.python.org/downloads/"
            ;;
        uv)
            echo "  uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
            ;;
        git)
            echo "  Git: apt install git (or equivalent for your OS)"
            ;;
        esac
    done
    exit 1
fi

if [[ "${CHECK_ONLY}" == "true" ]]; then
    log_success "All critical dependencies present"
    exit 0
fi

# =============================================================================
# Environment Setup
# =============================================================================

log_info "Setting up Python environment..."

cd "${REPO_ROOT}"

# Create virtual environment and install dependencies
if [[ "${DEV_MODE}" == "true" ]]; then
    log_info "Installing with development dependencies..."
    uv sync --dev

    # Ensure check-jsonschema is available (included in dev dependencies)
    if ! check_command check-jsonschema; then
        log_info "Installing check-jsonschema..."
        uv pip install check-jsonschema
    fi
else
    log_info "Installing production dependencies..."
    uv sync
fi

log_success "Dependencies installed"

# =============================================================================
# Validation
# =============================================================================

log_info "Validating installation..."

# Run tests to verify everything works
if uv run pytest -q --tb=no 2>/dev/null; then
    log_success "All tests passed"
else
    log_warning "Some tests failed (run 'uv run pytest -v' for details)"
fi

# Verify scripts are executable
log_info "Checking script executability..."
for script in "${REPO_ROOT}"/.claude/hooks/*.sh; do
    if [[ -f "${script}" ]]; then
        if [[ -x "${script}" ]]; then
            log_success "$(basename "${script}") is executable"
        else
            chmod +x "${script}"
            log_info "Made $(basename "${script}") executable"
        fi
    fi
done

for script in "${REPO_ROOT}"/.claude/hooks/*.py; do
    if [[ -f "${script}" ]]; then
        if [[ -x "${script}" ]]; then
            log_success "$(basename "${script}") is executable"
        else
            chmod +x "${script}"
            log_info "Made $(basename "${script}") executable"
        fi
    fi
done

# =============================================================================
# Pre-commit Setup (Optional)
# =============================================================================

if [[ "${DEV_MODE}" == "true" ]] && check_command pre-commit; then
    log_info "Setting up pre-commit hooks..."
    if [[ -f "${REPO_ROOT}/.pre-commit-config.yaml" ]]; then
        pre-commit install
        log_success "Pre-commit hooks installed"
    else
        log_warning "No .pre-commit-config.yaml found, skipping pre-commit setup"
    fi
fi

# =============================================================================
# Summary
# =============================================================================

echo ""
echo "=============================================="
log_success "Setup complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Run tests:        uv run pytest -v"
echo "  2. Run quality check: ./scripts/check.sh"
echo "  3. View CLI help:    uv run spreadsheet-dl --help"
echo ""
