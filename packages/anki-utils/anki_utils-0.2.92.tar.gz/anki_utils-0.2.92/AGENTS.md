# AGENTS.md

> Context for AI coding agents working on this repository.

## Strict Issue Checklist (Must Follow Exactly)

Before picking up any new issue:
1. Re-read this file and state: “Issue checklist ready.”
2. Present the checklist and wait for explicit user OK:
   - branch created (name)
   - tests planned (or why not)
   - CHANGELOG/MIGRATIONS impact reviewed

At the end of the issue:
3. Present the same checklist with results (branch, tests run, changelog/migrations updated).
If any step is skipped, stop and ask to restart the issue.

## Getting Started (For New Agents)

If you've been given this repository URL and asked to work on it, follow this workflow:

### 1. Clone the Repository

```bash
# Clone into your workspace
git clone https://github.com/Gilbetrar/anki-package.git
cd anki-package

# Install in dev mode
pip install -e ".[dev]"

# Verify tests pass before making changes
pytest -v
```

### 2. Find an Issue to Work On

Check [GitHub Issues with `ready` label](https://github.com/Gilbetrar/anki-package/issues?q=is%3Aissue+is%3Aopen+label%3Aready) for available tasks.

```bash
# Or via CLI
gh issue list --label ready
```

Pick one issue. Read it carefully. Understand the success criteria before starting.

### 3. Create a Branch

```bash
# Branch naming: <type>/issue-<number>-<short-description>
git checkout -b feat/issue-42-add-dark-mode
# or: fix/issue-7-theme-loading
# or: refactor/issue-15-simplify-exporter
```

### 4. Do the Work

1. Read relevant source files before modifying (see [Key Files by Task](#key-files-by-task))
2. Make focused changes (avoid over-engineering)
3. Add/update tests for your changes
4. Run `pytest -v` to verify all tests pass
5. Add a changelog fragment if user-visible (see [Changelog Fragments](#changelog-fragments-critical))
6. Update `anki_utils/MIGRATIONS.md` under `## [Unreleased]` if you changed the package API

### 5. Commit and Push

```bash
# Commit with conventional message
git add .
git commit -m "feat: add dark mode support

Closes #42"

# Push your branch
git push -u origin feat/issue-42-add-dark-mode
```

### 6. Open a Pull Request

```bash
gh pr create --title "feat: add dark mode support" --body "Closes #42

## Summary
- Added dark mode toggle
- Updated theme system

## Test plan
- [ ] Run pytest -v
- [ ] Manual verification of dark mode"
```

The PR will run CI tests. Wait for the owner to review and merge.

### 7. Clean Up After Work

After your PR is created, clean up your worktree (see Multi-Agent Coordination below).

---

## Multi-Agent Coordination (CRITICAL)

**Multiple Claude instances work on this repo in parallel.** Follow these rules strictly to avoid conflicts.

### Why Worktrees?

We use git worktrees instead of separate clones because:
- **Instant setup** - No re-downloading the repo
- **Less disk space** - Shared git objects
- **Scales well** - Supports many parallel agents efficiently

### Step 1: Ensure Base Clone Exists

```bash
# Only needed once - check if base clone exists
if [ ! -d ~/Claude/anki-package ]; then
  git clone https://github.com/Gilbetrar/anki-package.git ~/Claude/anki-package
fi
cd ~/Claude/anki-package
git fetch origin
```

### Step 2: Check If Issue Is Available

**Do ALL of these checks before picking an issue:**

```bash
# Check if issue is assigned or has "agent working" comment
gh issue view <NUMBER> --json assignees,comments

# Check if a branch already exists on remote
git ls-remote --heads origin | grep "issue-<NUMBER>"

# Check for existing PRs
gh pr list | grep "issue-<NUMBER>"
```

**If ANY check shows activity → pick a different issue.** Don't duplicate work.

### Step 3: Claim the Issue Immediately

Before writing any code, claim the issue so other agents see it:

```bash
# Comment on the issue to claim it
gh issue comment <NUMBER> --body "🤖 Agent starting work on this issue"
```

### Step 4: Create Your Worktree

```bash
# From the base clone, create a worktree for your issue
cd ~/Claude/anki-package
git fetch origin
git worktree add ~/Claude/anki-issue-<NUMBER> -b test/issue-<NUMBER>-description origin/main

# Push branch immediately to signal you're working on it
cd ~/Claude/anki-issue-<NUMBER>
git commit --allow-empty -m "WIP: starting work on issue #<NUMBER>"
git push -u origin test/issue-<NUMBER>-description

# Install and verify
pip install -e ".[dev]"
pytest -v
```

### Step 5: Do Your Work

Work entirely in `~/Claude/anki-issue-<NUMBER>/`. This is your isolated workspace.

### Step 6: Clean Up After PR

```bash
# After PR is created, remove your worktree
cd ~/Claude/anki-package
git worktree remove ~/Claude/anki-issue-<NUMBER>

# Optionally delete the local branch
git branch -d test/issue-<NUMBER>-description
```

### Directory Structure

```
~/Claude/
  anki-package/          # Base clone (stays on main, don't work here)
  anki-issue-75/         # Agent 1's worktree for issue 75
  anki-issue-76/         # Agent 2's worktree for issue 76
  anki-issue-77/         # Agent 3's worktree for issue 77
```

### Quick Reference Checklist

Before starting:
- [ ] `gh issue view <N>` - not assigned/commented by another agent
- [ ] `git ls-remote | grep issue-<N>` - no remote branch exists
- [ ] `gh pr list | grep issue-<N>` - no PR exists

When starting:
- [ ] `gh issue comment <N>` - claim the issue
- [ ] `git worktree add` - create isolated workspace
- [ ] `git push` - push branch immediately

After PR created:
- [ ] `git worktree remove` - clean up workspace

---

## What This Is

`anki-utils` is a Python package for creating Anki flashcards. It handles deterministic code execution while AI agents (Claude skills, ChatGPT, etc.) handle natural language understanding.

- **Distribution**: PyPI (`pip install anki-utils`)
- **Primary consumer**: A Claude skill that calls this package via CLI
- **Owner**: Non-technical, relies on agents for development

## Repository Structure

```
anki_utils/              # PyPI package (this gets published)
  ├── exporter.py        # Core .apkg generation, validation
  ├── markdown.py        # Markdown to HTML conversion
  ├── themes.py          # CSS for 4 themes (source of truth)
  ├── occlusion.py       # Image occlusion detection (OCR)
  ├── cli.py             # CLI interface
  ├── CHANGELOG.md       # History (query: anki-utils changelog)
  └── MIGRATIONS.md      # Skill update instructions

changelog.d/             # Changelog fragments (towncrier) - add your changes here!
tests/                   # pytest suite
skill-reference/         # Snapshot of consuming Claude skill (read-only)
developer/tools/         # Theme designer, test scripts
```

## Key Files by Task

| Task | Read These |
|------|------------|
| Card generation | `anki_utils/exporter.py` |
| Theme/CSS changes | `anki_utils/themes.py` (source of truth) |
| Markdown conversion | `anki_utils/markdown.py` |
| Image occlusion | `anki_utils/occlusion.py` |
| CLI commands | `anki_utils/cli.py` |
| Skill integration | `skill-reference/`, `anki_utils/MIGRATIONS.md` |

## Commands

```bash
pip install -e ".[dev]"         # Install in dev mode
pytest -v                       # Run tests (required before committing)
anki-utils changelog            # Check current state
```

## Boundaries

### Always Do
- Run `pytest -v` before committing
- Add a changelog fragment for user-visible changes (see [Changelog Fragments](#changelog-fragments-critical))
- Update MIGRATIONS.md when changing package API
- Keep changes focused and minimal
- Open a PR (don't push directly to main)

### Ask First
- Architectural changes affecting multiple modules
- New dependencies
- Changes to card type structure (affects existing user decks)

### Never Do
- Push directly to `main` branch
- Modify `skill-reference/` (read-only snapshot)
- Commit secrets or credentials
- Skip tests
- Make breaking API changes without migration instructions

## If You Change the Package API

1. Add entry to `anki_utils/MIGRATIONS.md` under the `## [Unreleased]` section with:
   - What changed
   - **Skill Instructions**: Steps the skill should follow to adapt
2. **Do NOT add version numbers** - the release workflow automatically converts `[Unreleased]` to the released version
3. The consuming skill checks migrations at startup via:
   ```bash
   anki-utils migrations --since <version> --json
   ```

## Source of Truth

| Concern | Location |
|---------|----------|
| Theme CSS | `anki_utils/themes.py` |
| Card templates | `anki_utils/exporter.py` |
| Tasks/Roadmap | [GitHub Issues](https://github.com/Gilbetrar/anki-package/issues) |
| Changelog | `anki_utils/CHANGELOG.md` (compiled from `changelog.d/` fragments) |
| Changelog fragments | `changelog.d/<issue>.<type>.md` |
| Migrations | `anki_utils/MIGRATIONS.md` |

## Testing

```bash
pytest                          # All tests
pytest -v                       # Verbose
pytest --cov=anki_utils         # With coverage
pytest tests/test_exporter.py   # Specific module
```

Tests live in `tests/test_<module>.py`. Add tests for:
- All public functions
- Edge cases in markdown conversion
- Each card type generation
- CLI commands

## Changelog Fragments (CRITICAL)

**DO NOT edit `anki_utils/CHANGELOG.md` directly.** Multiple agents work in parallel, and direct edits cause merge conflicts.

Instead, use **towncrier fragments**:

### Adding a Fragment

Create a file in `changelog.d/` named `<issue-number>.<type>.md`:

```bash
# Example: you're working on issue #42, adding a feature
echo "Preview tool: Added dark mode toggle" > changelog.d/42.added.md
```

**Fragment types:**
| Type | Use for |
|------|---------|
| `added` | New features |
| `changed` | Changes to existing functionality |
| `fixed` | Bug fixes |
| `deprecated` | Features marked for removal |
| `removed` | Removed features |

**Content:** One line describing the change from the user's perspective.

### Multiple Changes Per Issue

If your PR has multiple distinct changes, use suffixes:

```bash
changelog.d/42.added.md      # "Added dark mode toggle"
changelog.d/42-2.fixed.md    # "Fixed theme persistence bug"
```

### At Release Time

The maintainer runs:
```bash
towncrier build --version X.Y.Z
```

This compiles all fragments into `CHANGELOG.md` and deletes the fragment files.

### Preview Without Deleting

```bash
towncrier build --draft --version X.Y.Z
```

## Test Launcher

The repository includes a "Test Launcher" at `developer/test-launcher.html`. This is a standalone HTML tool used to preview changes to user-facing code without launching the full consuming skill.

**Key Context:**
- **Bundling**: The launcher relies on React code located in `anki_utils/assets/` (`preview-template.jsx`, `theme-designer.jsx`).
- **Workflow**: A GitHub Action (`refresh-test-launcher.yml`) automatically bundles these assets and updates `developer/test-launcher.html` whenever changes are pushed to `main`.
- **Manual update**: If you modify the React assets and want to verify changes locally, you can run:
  ```bash
  python developer/tools/generate-test-launcher.py
  ```

## Frontend Asset Bundling (CRITICAL)

**Claude Skills serves `preview-template.jsx` as a standalone file.** There is no module loader or build system at runtime. This means:

1. **Source files in `anki_utils/assets/`** use placeholders and `window` imports
2. **Bundled files in `anki_utils/assets/bundled/`** are self-contained (no external dependencies)
3. **Claude Skills deploys the bundled versions**

### How Bundling Works

```
Source files (development):
├── pure-functions.js      → Shared utilities (ES module exports)
├── shared-preview.jsx     → Shared React component (window export)
├── preview-template.jsx   → Uses window.PureFunctions and window.SharedCardPreview
└── theme-designer.jsx     → Uses window.SharedCardPreview

Bundler inlines dependencies:
$ python developer/tools/bundle-artifacts.py

Bundled files (deployment):
└── bundled/
    ├── preview-template.jsx  → Self-contained (includes inlined pure-functions + shared-preview)
    └── theme-designer.jsx    → Self-contained (includes inlined shared-preview)
```

### Adding Shared Code

**DO NOT add ES module imports to JSX files** - they won't work in Claude Skills.

Instead:
1. Add code to `pure-functions.js` or `shared-preview.jsx`
2. Export via `window.YourThing` for runtime use
3. Also add ES module export for tests (`export { ... }`)
4. Update `bundle-artifacts.py` to inline the new code
5. Run `python developer/tools/bundle-artifacts.py` to regenerate bundled files

### Testing Shared Code

Tests import directly from source files:
```javascript
import { getCardCSS, escapeHtml } from '../../anki_utils/assets/pure-functions.js';
```

This ensures tests always verify the actual production code, not copies.

### Common Mistakes

❌ Adding `import X from './module.js'` to JSX files (won't work in Claude Skills)
❌ Forgetting to run the bundler after changing shared code
❌ Copying functions into test files (use imports instead)

✅ Use `window.X` pattern for runtime imports
✅ Run bundler when modifying shared code
✅ Test imports from source files

## Principles

1. **Determinism**: Package does predictable things. No guessing or inference.
2. **Fail loudly**: Invalid input produces clear errors, not silent failures.
3. **Single source of truth**: No duplicated code. One place for each concern.
4. **Token efficiency**: Concise, queryable docs. Don't read thousands of lines.
