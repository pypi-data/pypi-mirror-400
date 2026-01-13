#!/usr/bin/env bash
# Setup Claude Code configuration for SpreadsheetDL development
# Usage: ./scripts/setup_claude_config.sh [--full] [--force]
#
# Options:
#   --full   Install full hook infrastructure
#   --force  Overwrite existing configuration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
TARGET_DIR="${PROJECT_ROOT}/.claude"

# Parse arguments
FULL_INSTALL=false
FORCE=false
for arg in "$@"; do
  case ${arg} in
  --full)
    FULL_INSTALL=true
    ;;
  --force)
    FORCE=true
    ;;
  --help | -h)
    echo "Usage: $0 [--full] [--force]"
    echo ""
    echo "Options:"
    echo "  --full   Install full hook infrastructure"
    echo "  --force  Overwrite existing configuration"
    echo ""
    echo "This script sets up Claude Code configuration for development."
    exit 0
    ;;
  esac
done

echo "🔧 Setting up Claude Code configuration..."
echo ""

# Check if configuration exists
if [[ -f "${TARGET_DIR}/settings.json" ]] && [[ "${FORCE}" != "true" ]]; then
  echo "ℹ️  Configuration already exists at .claude/"
  echo "   Use --force to reset to defaults."
  echo ""
  echo "Current configuration:"
  find "${TARGET_DIR}/" -maxdepth 1 -type f -o -type d | sort | head -15
  exit 0
fi

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "${TARGET_DIR}/agent-outputs"
mkdir -p "${TARGET_DIR}/checkpoints"
mkdir -p "${TARGET_DIR}/summaries"

# Create .gitkeep files
touch "${TARGET_DIR}/agent-outputs/.gitkeep"
touch "${TARGET_DIR}/checkpoints/.gitkeep"
touch "${TARGET_DIR}/summaries/.gitkeep"

# Ensure hooks are executable
if [[ -d "${TARGET_DIR}/hooks" ]]; then
  echo "🔐 Setting hook permissions..."
  chmod +x "${TARGET_DIR}/hooks/"*.sh 2>/dev/null || true
  chmod +x "${TARGET_DIR}/hooks/"*.py 2>/dev/null || true
fi

# Verify configuration
echo ""
echo "✅ Claude Code configuration ready!"
echo ""
echo "Directory structure:"
find "${TARGET_DIR}" -maxdepth 2 -type f -name "*.md" -o -name "*.yaml" -o -name "*.json" 2>/dev/null | head -20 | sed 's|'"${PROJECT_ROOT}"'/||'
echo ""

# Show usage
echo "Usage:"
echo "  /ai <task>       Route task to appropriate agent"
echo "  /git             Smart conventional commits"
echo "  /implement       Implement from specification"
echo "  /spec            Specification workflow"
echo "  /swarm           Parallel agent coordination"
echo ""
echo "See .claude/README.md for full documentation."

# Full install info
if [[ "${FULL_INSTALL}" == "true" ]]; then
  echo ""
  echo "Full installation includes:"
  echo "  - All lifecycle hooks (security, quality, context management)"
  echo "  - Agent swarm orchestration"
  echo "  - Coding standards enforcement"
  echo ""
fi
