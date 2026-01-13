# Migrations

> Query via CLI: `anki-utils migrations`
>
> For consuming agents: Check this file when your cached version differs from `anki-utils version`.
> If there are entries newer than your last sync, follow the instructions in each entry.

## How This Works

1. Each version entry below contains changes and **Skill Instructions**
2. The Claude skill tracks which version it last synced to
3. When the skill detects a newer version, it reads instructions here
4. The skill follows the instructions to update itself
5. The skill updates its tracked version

---

## [Unreleased]

---

## [0.2.9] - 2026-01-04

### What Changed
- Image occlusion cards now accept `image_data` (base64 data URL) as an alternative to `image_path`
- New optional fields: `image_width` and `image_height` for explicit dimension control
- Dimensions are automatically extracted from base64 data when not explicitly provided
- Cards now fail loudly with a clear `ValidationError` if neither `image_path` nor `image_data` is usable

### Schema Changes
For `image-occlusion` card type:

**New optional fields:**
```json
{
  "type": "image-occlusion",
  "image_path": "/path/to/image.png",  // Preferred if file exists
  "image_data": "data:image/png;base64,...",  // Fallback if file unavailable
  "image_width": 800,  // Optional: explicit width in pixels
  "image_height": 600,  // Optional: explicit height in pixels
  "occlusions": [...]
}
```

**Priority order:**
1. If `image_path` exists and is readable → read file and encode
2. If file unavailable but `image_data` provided → use base64 directly
3. If neither usable → `ValidationError` (no more silent failures)

**Dimensions priority:**
1. Explicit `image_width`/`image_height` if provided
2. Read from file if `image_path` exists
3. Extract from base64 `image_data` if available
4. Fall back to 1:1 aspect ratio

### Skill Instructions
This is a **backwards-compatible enhancement** that prevents silent failures.

**If you preprocess images for preview:**
When preprocessing card data for preview (converting `image_path` to base64), preserve BOTH fields:

```python
# When preprocessing for preview
if 'image_path' in card and os.path.exists(card['image_path']):
    with open(card['image_path'], 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    mime = 'image/png'  # or detect from extension
    card['image_data'] = f"data:{mime};base64,{data}"
    # KEEP image_path for export - don't delete it!
    # Export will prefer the file if it still exists
```

**If your image files might become unavailable:**
Pass `image_data` as a fallback when the file might not exist at export time:

```python
card = {
    "type": "image-occlusion",
    "image_path": temp_file_path,  # Might be gone later
    "image_data": base64_from_earlier,  # Guaranteed backup
    "occlusions": [...]
}
```

**No action required if:**
- Your `image_path` values always point to files that exist at export time
- You're not experiencing broken image icons in Anki

---

## [0.2.2] - 2025-01-01

### What Changed
- `preview-template.jsx` now uses `__THEMES_PLACEHOLDER__` for theme CSS injection
- Removed 939 lines of duplicated CSS from the template (file reduced from 2668 to 1737 lines)
- Theme CSS is now single-source-of-truth in `themes.py`
- Added helper functions: `getImageSource()`, `CLOZE_PATTERN` constant
- Theme dropdown now dynamically generated from available themes
- **Theme Redesign**: Three themes renamed and restyled for better differentiation:
  - `rich` → `classic`: Serif typography (Georgia), warm cream backgrounds, scholarly feel
  - `bold` → `high-contrast`: WCAG AA compliant, 20px text, accessibility-focused
  - `ios` → `calm`: Muted pastels, soft shadows, relaxed feel for long study sessions
  - `minimal`: Unchanged (remains the default)

### Schema Changes
- **Breaking**: Theme identifiers changed. Old names (`rich`, `bold`, `ios`) are no longer valid.
- The `create_package()` function will fall back to `minimal` with a warning if old theme names are used.

### Skill Instructions

**Theme Name Updates Required:**
If your skill references themes by name, update all occurrences:
- `"rich"` → `"classic"`
- `"bold"` → `"high-contrast"`
- `"ios"` → `"calm"`
- `"minimal"` → no change

**Preview Template Injection:**
When launching `preview-template.jsx`, you must now inject theme CSS in addition to card data:

1. Get theme CSS as JSON:
   ```bash
   anki-utils themes --all-json
   ```

2. Inject both placeholders before rendering:
   ```python
   # Get theme data from CLI
   import subprocess
   themes_json = subprocess.check_output(['anki-utils', 'themes', '--all-json']).decode()

   # Read template
   with open('preview-template.jsx', 'r') as f:
       content = f.read()

   # Inject both placeholders
   content = content.replace('__THEMES_PLACEHOLDER__', themes_json)
   content = content.replace('__CARD_DATA_PLACEHOLDER__', card_data_json)
   ```

**Note:** If `__THEMES_PLACEHOLDER__` is not replaced, the preview will fail to render. The placeholder must be replaced with the JSON object from `anki-utils themes --all-json`.

3. After updating, run validation tests:
   ```bash
   anki-utils skill-update-protocol
   ```
   This outputs the full validation test suite. Run each test to confirm everything works.

---

## [0.2.3] - 2025-01-01

### What Changed
- Preview feedback export now emits explicit note/card identifiers.
- Feedback is grouped by note with `cardInstances`, each including `cardInstanceId` and `templateKey`.
- Structured edit payloads replace freeform edit notes (field/action/value) for unambiguous changes.
- Legacy flat feedback output is still included for backward compatibility.

### Schema Changes
- Preview feedback export JSON now includes:
  - `notes[]` grouped by note with `noteId`, `cardInstances[]`, `templateKey`, and `cardInstanceId`
  - `edit` object with `field`, `action`, and optional `value` (plus cloze context when relevant)
- `legacyFeedback` remains for older consumers.

### Skill Instructions
If your agent parses preview feedback JSON:

1. Prefer the `notes[]` output when present.
2. Use `notes[].noteId` + `cardInstances[].cardInstanceId` to identify the exact derived card.
3. Apply edits via `edit.field`, `edit.action`, and `edit.value` instead of freeform notes.
4. Continue to support `legacyFeedback` for older preview artifacts.

No changes are required to card generation input schemas.

---

## [0.2.1] - 2025-01-01

### What Changed
- Added `anki-utils migrations` CLI command for querying migration instructions
- Added `anki-utils version` CLI command to check current package version
- Added `anki-utils roadmap --html` flag for styled HTML output
- Migration system introduced for agent-to-agent update communication

### Schema Changes
None.

### Skill Instructions
This is the first migration-aware release. To adopt the migration system:

1. After installing/updating anki-utils, call `anki-utils version` to get the current version
2. Store this version in your skill's configuration or memory
3. Periodically (or on errors), call `anki-utils migrations --since <your-stored-version> --json`
4. If the response contains entries, follow the instructions in each
5. Update your stored version to the current version

Example check pattern:
```python
# Pseudocode for skill update check
current = run("anki-utils version --json")["version"]
if current != stored_version:
    migrations = run(f"anki-utils migrations --since {stored_version} --json")
    for entry in migrations["entries"]:
        # Follow entry["skill_instructions"]
        pass
    stored_version = current
```

---

## [0.2.0] - 2025-01-01

### What Changed
- Repository restructured for agent-driven development
- Added `anki-utils roadmap` and `anki-utils changelog` CLI commands
- Documentation reorganized into `docs/` directory
- Legacy files archived to `archive/`

### Schema Changes
None. The `create_package()` API remains unchanged.

### Skill Instructions
No action required. This release adds developer tooling without changing the public API.

---

## Template for Future Entries

When adding a new version, copy this template:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### What Changed
- Brief description of changes

### Schema Changes
Describe any changes to the JSON input format for `create_package()` or other functions.
Use "None." if no schema changes.

### Skill Instructions
Step-by-step instructions for what the consuming skill needs to change.
Use "No action required." if backwards compatible.
```
