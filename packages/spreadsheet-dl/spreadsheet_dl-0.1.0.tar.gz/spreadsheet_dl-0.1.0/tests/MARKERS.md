# Pytest Markers Guide

**This document has been consolidated into the main testing guide.**

For complete and up-to-date documentation on pytest markers, test organization, usage patterns, and best practices, please see:

**→ [tests/README.md](../tests/README.md)**

## Quick Links

- [Available Markers](../tests/README.md#available-markers) - Complete list of all markers with descriptions
- [Common Usage Patterns](../tests/README.md#common-usage-patterns) - Examples of marker combinations
- [Writing Tests](../tests/README.md#writing-tests) - Guidelines for adding markers to new tests
- [Understanding "N deselected"](../tests/README.md#understanding-n-deselected) - Why you see deselected tests
- [CI/CD Integration](../tests/README.md#cicd-integration) - Using markers in continuous integration
- [Debugging](../tests/README.md#debugging) - Tips for test debugging and troubleshooting

## Quick Reference

For a concise quick reference of common commands, see [TESTING.md](../TESTING.md) in the root directory.

## Dynamic Statistics

To get current test counts (always up-to-date):

```bash
scripts/test_stats.sh
```
