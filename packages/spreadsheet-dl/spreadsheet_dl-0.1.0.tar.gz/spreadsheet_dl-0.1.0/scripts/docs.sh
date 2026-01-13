#!/usr/bin/env bash
# Documentation build and serve script for SpreadsheetDL
#
# Usage:
#   scripts/docs.sh build    # Build documentation
#   scripts/docs.sh serve    # Serve documentation locally
#   scripts/docs.sh deploy   # Deploy to GitHub Pages
#   scripts/docs.sh lint     # Check docstring coverage
#   scripts/docs.sh check    # Full documentation quality check

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"

cd "${PROJECT_ROOT}"

# Ensure docs dependencies are installed
ensure_deps() {
    if ! uv run python -c "import mkdocs" 2>/dev/null; then
        echo -e "${YELLOW}Installing documentation dependencies...${NC}"
        uv sync --extra docs
    fi
}

# Build documentation
build() {
    echo -e "${GREEN}Building documentation...${NC}"
    ensure_deps
    uv run mkdocs build --strict
    echo -e "${GREEN}Documentation built successfully in site/${NC}"
}

# Serve documentation locally
serve() {
    echo -e "${GREEN}Starting documentation server...${NC}"
    ensure_deps
    echo -e "${YELLOW}Documentation available at http://127.0.0.1:8000${NC}"
    uv run mkdocs serve
}

# Deploy to GitHub Pages
deploy() {
    echo -e "${GREEN}Deploying documentation to GitHub Pages...${NC}"
    ensure_deps
    uv run mkdocs gh-deploy --force
    echo -e "${GREEN}Documentation deployed successfully${NC}"
}

# Check docstring coverage with interrogate
lint() {
    echo -e "${GREEN}Checking docstring coverage...${NC}"
    ensure_deps
    uv run interrogate -v src/spreadsheet_dl/
}

# Full documentation quality check
check() {
    local exit_code=0

    echo -e "${GREEN}Running full documentation quality check...${NC}"
    ensure_deps

    echo ""
    echo -e "${YELLOW}=== Docstring Coverage (interrogate) ===${NC}"
    if ! uv run interrogate -v src/spreadsheet_dl/; then
        echo -e "${RED}Docstring coverage check failed${NC}"
        exit_code=1
    fi

    echo ""
    echo -e "${YELLOW}=== Docstring Style (ruff) ===${NC}"
    if ! uv run ruff check --select=D src/; then
        echo -e "${RED}Docstring style check failed${NC}"
        exit_code=1
    fi

    echo ""
    echo -e "${YELLOW}=== Documentation Build ===${NC}"
    if ! uv run mkdocs build --strict; then
        echo -e "${RED}Documentation build failed${NC}"
        exit_code=1
    fi

    echo ""
    if [[ ${exit_code} -eq 0 ]]; then
        echo -e "${GREEN}All documentation checks passed${NC}"
    else
        echo -e "${RED}Some documentation checks failed${NC}"
    fi

    return ${exit_code}
}

# Show usage
usage() {
    echo "SpreadsheetDL Documentation Tools"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  build    Build documentation to site/"
    echo "  serve    Start local documentation server"
    echo "  deploy   Deploy to GitHub Pages"
    echo "  lint     Check docstring coverage"
    echo "  check    Full documentation quality check"
    echo ""
    echo "Examples:"
    echo "  $0 serve     # Start local server at http://127.0.0.1:8000"
    echo "  $0 check     # Run all documentation checks"
}

# Main entry point
main() {
    local command="${1:-}"

    case "${command}" in
    build)
        build
        ;;
    serve)
        serve
        ;;
    deploy)
        deploy
        ;;
    lint)
        lint
        ;;
    check)
        check
        ;;
    -h | --help | help)
        usage
        ;;
    *)
        if [[ -n "${command}" ]]; then
            echo -e "${RED}Unknown command: ${command}${NC}"
            echo ""
        fi
        usage
        exit 1
        ;;
    esac
}

main "$@"
