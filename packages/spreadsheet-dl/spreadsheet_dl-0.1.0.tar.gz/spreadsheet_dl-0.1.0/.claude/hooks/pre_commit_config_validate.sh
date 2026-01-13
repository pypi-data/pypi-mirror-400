#!/usr/bin/env bash
# Pre-commit hook for configuration validation
# Run this hook before commits to catch config inconsistencies early
#
# Installation:
#   ln -sf ../../.claude/hooks/pre_commit_config_validate.sh .git/hooks/pre-commit
#
# Or add to existing pre-commit:
#   .claude/hooks/pre_commit_config_validate.sh || exit 1

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
HOOKS_DIR="${PROJECT_DIR}/.claude/hooks"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running pre-commit config validation...${NC}"

# Check if validation script exists
if [[ ! -f "${HOOKS_DIR}/validate_config_consistency.py" ]]; then
    echo -e "${RED}ERROR: validate_config_consistency.py not found${NC}"
    exit 1
fi

# Run config consistency validation
echo "  Checking config consistency..."
if ! python3 "${HOOKS_DIR}/validate_config_consistency.py" 2>&1 | grep -q "Errors: 0"; then
    echo -e "${RED}ERROR: Configuration validation failed${NC}"
    echo "Run: python3 .claude/hooks/validate_config_consistency.py"
    exit 1
fi
echo -e "  ${GREEN}✓ Config consistency OK${NC}"

# Run SSOT validation
echo "  Checking SSOT..."
if ! python3 "${HOOKS_DIR}/validate_ssot.py" 2>&1 | grep -q '"ok": true'; then
    echo -e "${RED}ERROR: SSOT validation failed${NC}"
    echo "Run: python3 .claude/hooks/validate_ssot.py"
    exit 1
fi
echo -e "  ${GREEN}✓ SSOT validation OK${NC}"

# Check for staged changes to orchestration files
STAGED_ORCH_FILES=$(git diff --cached --name-only 2>/dev/null | grep -E "\.claude/(orchestration-config|agents|commands)" || true)

if [[ -n "${STAGED_ORCH_FILES}" ]]; then
    echo -e "  ${YELLOW}Orchestration files modified:${NC}"
    while IFS= read -r file; do
        echo "    ${file}"
    done <<<"${STAGED_ORCH_FILES}"

    # Run hook tests if orchestration files changed
    echo "  Running hook tests..."
    if ! python3 "${HOOKS_DIR}/test_hooks.py" 2>&1 | grep -q "All tests passed"; then
        echo -e "${YELLOW}WARNING: Some hook tests failed${NC}"
        # Don't block commit, just warn
    else
        echo -e "  ${GREEN}✓ Hook tests passed${NC}"
    fi
fi

echo -e "${GREEN}Pre-commit validation passed!${NC}"
exit 0
