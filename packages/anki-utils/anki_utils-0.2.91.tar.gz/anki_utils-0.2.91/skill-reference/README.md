# Skill Reference

This directory contains **snapshots** of the Claude skill files that consume this package. These are for **reference only** - the actual skill lives in Claude's skill system.

**These files may be out of date.** The skill evolves independently, and there's no automatic sync back to this repo. Ben manually copies files here when relevant.

## Files

| File | Last Updated | Description |
|------|--------------|-------------|
| `SKILL.md` | 2025-01-01 | Main skill router (runs on every invocation) |
| `claude-guide.md` | 2025-01-01 | Developer documentation for the skill |

## Purpose

Having these snapshots helps us:
1. Understand how the skill uses anki-utils
2. See how the migration system is integrated
3. Write appropriate migration instructions when making changes

## Important Limitations

- **Not authoritative** - The actual skill may have changed since these were copied
- **One-way sync** - Changes to the skill don't automatically appear here
- **Use for context only** - Don't assume these reflect current skill behavior

## Key Integration Points

The skill checks for package updates at startup:

```bash
anki-utils migrations --since 0.2.1 --json
```

If `has_updates` is true, it reads `claude-guide.md#external-package-sync-anki-utils` for instructions.

## Updating These Files

When the skill is updated, copy the new versions here for reference. These don't need to stay perfectly in sync - they're just for context.
