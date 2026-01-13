#!/usr/bin/env bash
# Validation script for SpreadsheetDL
# Runs all quality checks and tests
# Usage: scripts/validate.sh [--json] [-v] [--help]

set -euo pipefail

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Parse arguments
JSON_OUTPUT=false
VERBOSE=false

show_help() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Run full validation suite including linting, formatting, type checking, and tests.

OPTIONS:
    --json          Output results in JSON format
    -v, --verbose   Enable verbose output
    -h, --help      Show this help message

EXAMPLES:
    $(basename "$0")              # Run validation suite
    $(basename "$0") --json       # Output in JSON format
    $(basename "$0") -v           # Verbose output

EOF
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  --json)
    JSON_OUTPUT=true
    shift
    ;;
  -v | --verbose)
    VERBOSE=true
    shift
    ;;
  -h | --help)
    show_help
    ;;
  *)
    echo "Error: Unknown option: $1" >&2
    echo "Run '$(basename "$0") --help' for usage information" >&2
    exit 1
    ;;
  esac
done

if [[ "${JSON_OUTPUT}" == "true" ]]; then
  # JSON output mode
  echo '{'
  echo '  "validation_suite": {'
  echo '    "checks": ['
fi

if [[ "${JSON_OUTPUT}" != "true" ]]; then
  echo "=== Validation Suite ==="
  echo ""
fi

# Track failures
FAILURES=0
declare -a CHECK_RESULTS

# Ruff check
echo "1. Ruff Lint Check"
echo "-------------------"
if uv run ruff check src/ tests/; then
  echo "PASS: Linting passed"
else
  echo "FAIL: Linting issues found"
  FAILURES=$((FAILURES + 1))
fi
echo ""

# Ruff format
echo "2. Ruff Format Check"
echo "--------------------"
if uv run ruff format --check src/ tests/; then
  echo "PASS: Formatting correct"
else
  echo "FAIL: Formatting issues found"
  FAILURES=$((FAILURES + 1))
fi
echo ""

# Mypy
echo "3. Mypy Type Check"
echo "------------------"
if uv run mypy src/; then
  echo "PASS: Type checking passed"
else
  echo "FAIL: Type errors found"
  FAILURES=$((FAILURES + 1))
fi
echo ""

# Pytest
echo "4. Pytest"
echo "---------"
if uv run pytest -v; then
  echo "PASS: All tests passed"
else
  echo "FAIL: Test failures"
  FAILURES=$((FAILURES + 1))
fi
echo ""

# SpreadsheetDL Integration Test
echo "5. SpreadsheetDL Integration Test"
echo "----------------------------------"
mkdir -p output
if uv run python -c "
from spreadsheet_dl import SpreadsheetBuilder
from pathlib import Path

# Create a simple test spreadsheet using correct API
builder = SpreadsheetBuilder()
builder.sheet('Test').header_row().data_rows(3)

# Save using builder's save method
path = Path('output/validation-test.ods')
builder.save(str(path))

assert path.exists(), 'File not created'
assert path.stat().st_size > 0, 'File is empty'
print(f'Generated: {path} ({path.stat().st_size} bytes)')
"; then
  echo "PASS: SpreadsheetDL integration works"
else
  echo "FAIL: SpreadsheetDL integration failed"
  FAILURES=$((FAILURES + 1))
fi
echo ""

# Streaming I/O Test
echo "6. Streaming I/O Test"
echo "---------------------"
if uv run python -c "
from spreadsheet_dl.streaming import StreamingWriter
from pathlib import Path

# Test streaming write using correct API
path = Path('output/streaming-test.ods')
writer = StreamingWriter(str(path))
writer.start_sheet('Data')
for i in range(50):
    writer.write_row([f'Row {i}', f'Value {i}', i * 10])
writer.end_sheet()
writer.close()

assert path.exists(), 'Streaming file not created'
assert path.stat().st_size > 0, 'Streaming file is empty'
print(f'Streaming test: {path} ({path.stat().st_size} bytes)')
"; then
  echo "PASS: Streaming I/O works"
else
  echo "FAIL: Streaming I/O failed"
  FAILURES=$((FAILURES + 1))
fi
echo ""

# Format Adapters Test
echo "7. Format Adapters Test"
echo "-----------------------"
if uv run python -c "
from spreadsheet_dl import SpreadsheetBuilder
from spreadsheet_dl.adapters import CsvAdapter, JsonAdapter
from pathlib import Path

# Create test data using correct API
builder = SpreadsheetBuilder()
builder.sheet('Export Test').header_row().data_rows(2)

# Test CSV export using adapter's export method
csv_path = Path('output/adapter-test.csv')
csv_adapter = CsvAdapter()
csv_adapter.export(builder._sheets, csv_path)
assert csv_path.exists(), 'CSV export failed'

# Test JSON export using adapter's export method
json_path = Path('output/adapter-test.json')
json_adapter = JsonAdapter()
json_adapter.export(builder._sheets, json_path)
assert json_path.exists(), 'JSON export failed'

print(f'CSV: {csv_path} ({csv_path.stat().st_size} bytes)')
print(f'JSON: {json_path} ({json_path.stat().st_size} bytes)')
"; then
  echo "PASS: Format adapters work"
else
  echo "FAIL: Format adapters failed"
  FAILURES=$((FAILURES + 1))
fi
echo ""

# Summary
echo "=== Summary ==="
if [[ ${FAILURES} -eq 0 ]]; then
  echo "All checks passed!"
  exit 0
else
  echo "${FAILURES} check(s) failed"
  exit 1
fi
