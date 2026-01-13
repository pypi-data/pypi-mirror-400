# Changelog Fragments

This directory contains changelog fragments for use with [towncrier](https://towncrier.readthedocs.io/).

## Adding a Changelog Entry

When you make a change that should be documented in the changelog, create a new file in this directory.

### File Naming Convention

```
<issue_number>.<type>.md
```

Or if there's no issue:

```
<description>.<type>.md
```

### Fragment Types

| Type             | Directory     | Description                        |
| ---------------- | ------------- | ---------------------------------- |
| Breaking Changes | `breaking`    | Backwards-incompatible changes     |
| New Features     | `feature`     | New functionality                  |
| Bug Fixes        | `fix`         | Bug fixes                          |
| Improvements     | `improvement` | Enhancements to existing features  |
| Documentation    | `doc`         | Documentation changes              |
| Deprecations     | `deprecation` | Features marked for future removal |
| Miscellaneous    | `misc`        | Other changes (refactoring, etc.)  |

### Examples

**Feature (with issue):**

```
123.feature.md
```

Content:

```
Added support for XLSX conditional formatting export.
```

**Bug fix (with issue):**

```
456.fix.md
```

Content:

```
Fixed incorrect formula reference resolution in cross-sheet lookups.
```

**Improvement (without issue):**

```
improve-streaming-perf.improvement.md
```

Content:

```
Improved streaming I/O performance by 40% for large files.
```

## Building the Changelog

To preview changes without modifying the changelog:

```bash
uv run towncrier build --draft
```

To build the changelog (removes fragments):

```bash
uv run towncrier build --version 4.1.0
```

## Notes

- Keep entries concise (one line if possible)
- Start with a verb (Added, Fixed, Improved, Removed, etc.)
- Reference issues/PRs when applicable
- Fragments are deleted after a release is published
