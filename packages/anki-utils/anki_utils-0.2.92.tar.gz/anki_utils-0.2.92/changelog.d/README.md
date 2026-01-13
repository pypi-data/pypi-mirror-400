# Changelog Fragments

This directory contains changelog fragments for towncrier.

## How to add a fragment

Create a file named `<issue-number>.<type>.md` where type is one of:
- `added` - New features
- `changed` - Changes to existing functionality
- `fixed` - Bug fixes
- `deprecated` - Features marked for removal
- `removed` - Removed features

Example: `42.added.md`

The file should contain a single line describing the change:
```
Preview tool: Added dark mode toggle
```

## Building the changelog

At release time, run:
```bash
towncrier build --version X.Y.Z
```

This compiles all fragments into `anki_utils/CHANGELOG.md` and deletes the fragment files.

## Preview without deleting

```bash
towncrier build --draft --version X.Y.Z
```
