# Claude Guide to Anki Flashcards Skill

This document helps Claude understand the skill structure, know what to read for different tasks, and follow development workflow conventions.

---

## Quick Reference: What to Read When

| Task | Read These Files |
|------|------------------|
| **General card creation** | SKILL.md → appropriate workflow file |
| **Theme iteration** | Run theme-designer-launch.sh, use Theme Designer artifact |
| **Theme/CSS changes** | themes.py + preview-template.jsx (must sync both) |
| **Adding card types** | apkg-export.md + create_anki_package.py + preview-template.jsx |
| **Quality issues** | quality-fixes.md |
| **Card type selection** | choosing-card-type.md |
| **Developer mode tasks** | portal.html (architecture), roadmap.html (priorities) |
| **Packaging** | Run dev-launch.sh, use skill-creator |

---

## File Structure Overview

```
anki-flashcards/
├── SKILL.md                    # ROUTER - ~100 lines, intent detection only
├── workflows/                  # USER FLOWS - read based on intent
│   ├── quick-cards.md          # Vocab, acronyms, pre-formatted, person, image
│   ├── document-extraction.md  # PDF/doc → cards (multi-turn)
│   ├── review-cycle.md         # Preview → feedback → iterate
│   └── batch-import.md         # CSV/JSON structured data
├── references/                 # GUIDANCE - read for specific questions
│   ├── apkg-export.md          # JSON schema, card types, export script usage
│   ├── quality-fixes.md        # How to fix common card problems
│   ├── choosing-card-type.md   # Decision tree for card type selection
│   ├── drafting-guidance.md    # Writing good cards
│   ├── image-occlusion.md      # Image occlusion card specifics
│   ├── people-cards.md         # Person card field details
│   ├── obsidian-templates.md   # Alternative Obsidian output format
│   └── worked-examples.md      # Example transformations
├── scripts/                    # EXECUTION - Python for generation
│   ├── create_anki_package.py  # .apkg generation (main script)
│   ├── detect_occlusion_regions.py  # OCR-based region detection for IO cards
│   └── themes.py               # CSS theme definitions (SOURCE OF TRUTH)
├── artifacts/                  # USER-FACING COMPONENTS
│   ├── preview-template.jsx    # React preview (2299 lines) - THEME CSS DUPLICATED HERE
│   ├── theme-designer.jsx      # Theme iteration tool (template, populated by launch script)
│   └── onboarding.html         # User guide / help
├── developer/                  # DEV TOOLS
│   ├── portal.html             # Main dev documentation
│   ├── roadmap.html            # Priorities and feature specs
│   ├── changelog.html          # Version history
│   ├── claude-guide.md         # THIS FILE
│   └── tools/
│       ├── dev-launch.sh       # Enter developer mode
│       ├── package-skill.sh    # Create .skill bundle
│       ├── test-preview.sh     # Test preview with sample data
│       ├── preprocess_test_data.py  # Convert image paths to base64 for preview
│       └── theme-designer-launch.sh  # Generate theme designer artifact
└── assets/
    └── test-data/
        ├── test-cards.json     # Sample cards for testing
        ├── heart-anatomy.jpg   # Test image for IO cards
        └── sample-person.png
```

---

## File Details

### SKILL.md (Router)

**Purpose:** Intent detection and routing. This is what Claude reads first when the skill is invoked.

**Contains:**
- Quick command table (dev, debug, /anki-help)
- Intent detection table (quick cards, document extraction, batch import, review)
- Core principle ("retrieval practice")
- Card types reference table
- Quality checklist (5 checks)
- Onboarding trigger

**When to reference:** Start of every Anki task. Then route to appropriate workflow.

**Key insight:** This file is intentionally slim (~100 lines) to minimize token cost. Real logic lives in workflow files.

---

### Workflows

#### quick-cards.md
**Purpose:** One-turn card creation for simple requests.

**Handles:** Vocabulary, acronyms, pre-formatted Q&A, person cards, image recognition.

**Pattern:** User asks → Claude creates cards → outputs .apkg + preview in ONE response.

**Key content:**
- Output pattern (both outputs in one turn)
- 5 quick card types with JSON examples
- Quality checks to apply silently
- Bash commands for generating preview + package

#### document-extraction.md
**Purpose:** Multi-turn flow for extracting cards from uploaded documents.

**Pattern:** Analyze → propose breakdown → draft → preview → iterate → export.

**Key content:**
- Knowledge type → card type mapping
- Batch size guidelines

#### review-cycle.md
**Purpose:** Preview → feedback → iterate loop.

**Key content:**
- Feedback JSON schema
- Feedback processing rules
- Card number mapping (_displayId vs _originalIndex)

#### batch-import.md
**Purpose:** Transform structured data (CSV/JSON) into cards.

**Key content:**
- Supported input formats
- Transformation process
- Large batch handling

---

### References

#### apkg-export.md (CRITICAL)
**Purpose:** JSON schema, export commands, card type specifications.

**Contains:**
- Default values (deck_name, theme, etc.)
- Fact verification fields
- Visual theme descriptions
- Batch tags convention
- **Complete JSON schema for all 6 card types**
- Image path requirements
- Person card fields (12 optional fields)
- Image occlusion coordinate system
- Export command syntax
- Model IDs for each card type

**When to read:** Any time you're generating cards or need JSON structure.

#### quality-fixes.md
**Purpose:** How to fix cards that fail quality checks.

**Contains:** Fix patterns for:
- Second-order thinking failures
- Interview test failures
- Natural language issues
- Specificity mismatches
- Non-atomic cards
- Retrieval test failures
- Complexity issues
- Structure problems
- Type check failures
- Pattern-matching problems

**When to read:** When applying quality checks or fixing user-provided cards.

#### choosing-card-type.md
**Purpose:** Decision tree for card type selection.

**Contains:**
- Visual decision tree
- Detailed guidance for factual, conceptual, procedural knowledge
- 3+ item rule for lists
- Image vs Image Occlusion guidance
- Cause-effect relationship handling

#### themes.py (SOURCE OF TRUTH FOR CSS)
**Purpose:** CSS definitions for all 4 themes.

**Contains:**
- Theme identifiers: minimal, rich, bold, ios
- Theme model ID offsets
- Complete CSS for each theme × each card type:
  - BASE (front-back, concept, cloze)
  - CONCEPT_INSTRUCTION
  - IMAGE
  - PERSON
  - IO (image occlusion)
- Helper functions: get_theme_model_id, get_*_css

**CRITICAL:** This is the source of truth for theme CSS. preview-template.jsx has a DUPLICATE copy that must stay in sync.

---

### Scripts

#### create_anki_package.py
**Purpose:** Generate .apkg files from JSON input.

**Usage:**
```bash
echo '<json_data>' | python3 /mnt/skills/user/anki-flashcards/scripts/create_anki_package.py /output/path.apkg
```

**Requires:** `pip install genanki --break-system-packages`

**Outputs:** JSON with statistics (deck_name, counts, total_notes, total_cards, media_files_included)

#### detect_occlusion_regions.py
**Purpose:** Automatically detect text labels and coordinates for image occlusion cards.

**CRITICAL:** This script exists because LLMs are notoriously bad at estimating coordinates. Research shows only ~2.5% accuracy for raw coordinate prediction. Use this script instead of asking Claude to estimate coordinates.

**Usage:**
```bash
# Basic OCR detection
python3 scripts/detect_occlusion_regions.py /path/to/image.jpg

# With grid overlay for unlabeled images
python3 scripts/detect_occlusion_regions.py /path/to/image.jpg --grid

# Generate preview with detected regions highlighted
python3 scripts/detect_occlusion_regions.py /path/to/image.jpg --preview

# JSON-only output for programmatic use
python3 scripts/detect_occlusion_regions.py /path/to/image.jpg --json
```

**Requires:** `pip install pytesseract pillow --break-system-packages`

**Outputs:**
- List of detected text labels with normalized coordinates (0-1)
- Optional: gridded image for manual selection
- Optional: preview image with bounding boxes

**Workflow for IO cards:**
1. Run detection script on user's image
2. Present detected labels to user for confirmation
3. User selects which labels should become occlusion regions
4. Use script-provided coordinates (not Claude-estimated) for card generation

---

### Artifacts

#### preview-template.jsx
**Purpose:** React preview component for reviewing cards before export.

**Size:** ~2300 lines (DO NOT read in full unless necessary)

**Contains:**
- Card rendering for all 6 types
- Tap-to-flip interaction
- Theme CSS (DUPLICATE of themes.py - must sync)
- Feedback collection (approve/edit/remove per card)
- Export feedback as JSON
- Placeholder: `__CARD_DATA_PLACEHOLDER__` for sed injection

**Usage:**
```bash
cp /mnt/skills/user/anki-flashcards/artifacts/preview-template.jsx /home/claude/preview.jsx
sed -i "s|__CARD_DATA_PLACEHOLDER__|<card_json>|" /home/claude/preview.jsx
present_files(['/home/claude/preview.jsx'])
```

#### onboarding.html
**Purpose:** User-facing guide (Notes vs Cards, setup checklists, alternatives)

---

### Developer Tools

#### dev-launch.sh
**Purpose:** Single command to enter developer mode.

**What it does:**
1. Copies portal.html → dev-portal.html
2. Copies changelog.html → dev-changelog.html
3. Packages skill → anki-flashcards.skill
4. Outputs files to /home/claude/

**Usage:** `bash /mnt/skills/user/anki-flashcards/developer/tools/dev-launch.sh`

**Then:** Present the three output files.

---

## Theme Designer Tool

The Theme Designer is a developer tool for rapid CSS iteration on card themes. It provides a full-viewport preview with side-by-side CSS editing.

### Features

- **Full-viewport layout** — Uses the entire screen, preview expands to fill available space
- **Side panel CSS editor** — 400px panel that slides in from the right (not a tiny modal)
- **Card selector** — Cycle through multiple sample cards of the same type with prev/next buttons
- **Live preview** — CSS changes apply immediately to the preview
- **Theme status badges** — Clear "Production" (green) vs "Working" (orange) indicators
- **Dark mode toggle** — Preview cards in light or dark mode
- **Export** — Copy-pasteable CSS formatted for themes.py

### Launching Theme Designer

```bash
bash /home/claude/anki-flashcards/developer/tools/theme-designer-launch.sh [working_themes_file]
# Then: present_files(['/home/claude/theme-designer.jsx'])
```

**Arguments:**
- `working_themes_file` (optional): Path to a JSON file with working theme definitions

### UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ TOOLBAR                                                          │
│ [Theme ▼] [Production] [Card Type ▼] [☀️/🌙] ... [Edit CSS] [Export] │
├─────────────────────────────────────────┬───────────────────────┤
│                                         │                       │
│         PREVIEW AREA                    │   CSS EDITOR PANEL    │
│                                         │   (when open)         │
│   ┌─────────────────────────────┐      │                       │
│   │                             │      │   Theme: minimal      │
│   │    Card iframe              │      │   Card type: Cloze    │
│   │    (full height)            │      │                       │
│   │                             │      │   ┌─────────────────┐ │
│   │                             │      │   │ CSS textarea    │ │
│   │    [Click to flip]          │      │   │                 │ │
│   └─────────────────────────────┘      │   └─────────────────┘ │
│                                         │                       │
│   [◀] Card 1/2: "What is..." [▶]       │                       │
│                                         │                       │
└─────────────────────────────────────────┴───────────────────────┘
```

### Workflow

1. **Launch:** Generate artifact with production themes (minimal, rich, bold, ios)
2. **Browse:** Select theme and card type from toolbar dropdowns
3. **Navigate:** Use prev/next buttons to cycle through sample cards of each type
4. **Preview:** Click card to flip between front/back, toggle dark mode
5. **Edit:** Click "Edit CSS" to open side panel for live CSS editing
6. **Iterate:** Changes apply immediately; "Unsaved" badge shows when you have edits
7. **Export:** Click "Export" to get copy-pasteable CSS formatted for themes.py

### Adding Working Themes

To inject experimental themes for comparison:

1. Create a JSON file with theme definitions:
```json
{
  "variant-1": {
    "base": "body { ... }",
    "conceptInstruction": ".concept-instruction { ... }",
    "image": ".prompt { ... }",
    "person": ".card { ... }"
  }
}
```

2. Pass the file to the launch script:
```bash
bash theme-designer-launch.sh /home/claude/working-themes.json
```

Working themes appear in the Theme dropdown under a "Working" group with orange status badges.

### Theme Data Structure

Each theme has four CSS sections:
- `base` — Core styles for front-back, concept, cloze cards
- `conceptInstruction` — Additional styles for concept cards (appended to base)
- `image` — Additional styles for image recognition cards (appended to base)
- `person` — Complete standalone styles for person cards

### Promoting a Theme to Production

When a working theme is ready:
1. User exports CSS from Theme Designer
2. Claude updates `scripts/themes.py` with new CSS
3. Claude updates matching section in `artifacts/preview-template.jsx`
4. Test both preview AND actual Anki import

---

## Development Conventions

### Session Close-Out Checklist

After every development session:

1. **Update changelog.html** if changes were made
2. **Update roadmap.html** if priorities changed or features completed
3. **Package the skill** using dev-launch.sh or package-skill.sh
4. **Present the .skill file** so user can update their installed skill

### CSS Theme Changes

**CRITICAL:** Theme CSS exists in TWO places that must stay in sync:
1. `scripts/themes.py` - Source of truth, used for .apkg generation
2. `artifacts/preview-template.jsx` - Duplicate, used for preview rendering

When updating themes:
1. Update themes.py first
2. Update matching section in preview-template.jsx
3. Test both preview AND actual Anki import

### Adding New Card Types

Requires changes in multiple files:
1. `scripts/create_anki_package.py` - Note model definition
2. `artifacts/preview-template.jsx` - Rendering logic
3. `references/apkg-export.md` - JSON schema documentation
4. `references/choosing-card-type.md` - Selection guidance
5. `SKILL.md` - Routing table
6. `assets/test-data/test-cards.json` - Test data

### Packaging for Distribution

```bash
cp -r /mnt/skills/user/anki-flashcards /home/claude/anki-flashcards
# Make modifications...
bash /home/claude/anki-flashcards/developer/tools/package-skill.sh /home/claude/anki-flashcards
# Present /home/claude/anki-flashcards.skill
```

---

## External Package Sync (anki-utils)

Some functionality has been extracted to the `anki-utils` PyPI package. The skill must stay synchronized with package updates.

### Current Synced Version

**Last synced: `0.2.1`** (first migration-aware version)

### How the Migration System Works

The package includes a CLI that reports what changed and what the skill needs to do:

```bash
# Check current version
anki-utils version --json
# → {"version": "0.2.1"}

# Get migrations since last sync
anki-utils migrations --since 0.2.1 --json
```

The migrations output includes:
- `has_updates`: boolean — whether there's anything new
- `entries`: array of changes, each with:
  - `version`, `date`, `changes` (informational)
  - `schema_changes` — any changes to JSON input format
  - `skill_instructions` — **specific steps to adapt the skill**

### Processing Updates

When `has_updates` is true:

1. Read each entry in order (oldest to newest)
2. Follow the `skill_instructions` for each
3. Update "Last synced" version above
4. If instructions require skill file changes, update and repackage

### What anki-utils Provides

| Command | Purpose | Replaces |
|---------|---------|----------|
| `export-apkg` | Create .apkg from JSON | `scripts/create_anki_package.py` |
| `themes` | Theme CSS definitions | `scripts/themes.py` |
| `asset` | JSX templates | `artifacts/preview-template.jsx`, `theme-designer.jsx` |
| `occlusion-detect` | OCR region detection | `scripts/detect_occlusion_regions.py` |
| `preprocess-test-data` | Base64 image conversion | `developer/tools/preprocess_test_data.py` |

### When to Check

- **Every skill invocation** — SKILL.md startup block runs the check automatically
- **Dev sessions** — Verify sync status before making changes
- **After unexpected errors** — Package API may have changed

### If Migrations Command Unavailable

If `anki-utils migrations` returns an error, the installed version is pre-0.2.1. The skill should:
1. Continue normally (core API is stable)
2. Note this in dev sessions so we can track when 0.2.1 is released
3. Once 0.2.1+ is available, the startup check will begin working

---

## Token Efficiency Notes

- SKILL.md is intentionally slim - real logic in workflow files
- Roadmap and changelog are separate files - only load when needed
- preview-template.jsx is large - avoid reading unless modifying preview
- Use sed injection pattern for preview rather than regenerating the whole file
- JSON intermediate format means Claude generates data once, reuses for preview + export

---

## Known Issues / TODOs

- Themes are too similar - need visual differentiation
- Theme CSS duplication is technical debt
- ~~Image cards don't render correctly in test preview (path resolution)~~ — Fixed v2.8 via base64 preprocessor
- Theme Designer v3.2 needs user review and bug fixes before marking complete
- Image Occlusion: OCR detection working, test data updated with accurate coordinates (v3.3)
