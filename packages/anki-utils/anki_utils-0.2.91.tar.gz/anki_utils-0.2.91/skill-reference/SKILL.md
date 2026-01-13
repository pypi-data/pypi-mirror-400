---
name: anki-flashcards
description: "Create high-quality Anki flashcards optimized for spaced repetition. Use when users want to make flashcards, create Anki cards, memorize something, turn notes into spaced repetition cards, export to Anki, or create .apkg files. Supports six card types: Front-Back, Bidirectional Concept, Cloze Deletion, Image Recognition, Image Occlusion, and Person cards. Outputs to downloadable .apkg packages or Obsidian format."
---

# Anki Flashcards

## Startup (Run Every Time)

```bash
# 1. Ensure anki-utils is available
pip install anki-utils --break-system-packages -q

# 2. Check for package updates
anki-utils migrations --since 0.2.3 --json 2>/dev/null || echo '{"has_updates": false, "error": "migrations command not available"}'
```

**If `has_updates` is true:** Read [developer/claude-guide.md](developer/claude-guide.md#external-package-sync-anki-utils) for migration instructions before proceeding.

**If migrations command unavailable:** Package is pre-0.2.1; continue normally but note this in any dev session.

---

## Quick Commands

| Trigger | Action |
|---------|--------|
| "dev", "developer", "developer mode", "work on this skill" | Run `bash /mnt/skills/user/anki-flashcards/developer/tools/dev-launch.sh` then present the files it outputs — **Do this first when user wants to develop/improve the skill** |
| "debug", "test preview", "test the skill" | Run [Debug Preview](#debug-preview) |
| "theme designer", "work on themes", "iterate on themes" | Run `bash /home/claude/anki-flashcards/developer/tools/theme-designer-launch.sh` then present `/home/claude/theme-designer.jsx` |
| "/anki-help", "how do I use this" | Present `artifacts/onboarding.html` |

**Developer Mode:** When a user indicates they want to work on, improve, or develop this skill (not just use it), run the dev-launch script and present all three output files: `dev-portal.html`, `dev-changelog.html`, and `anki-flashcards.skill`. This gives the developer immediate access to documentation and the exportable skill bundle.

### Debug Preview
```bash
# Get template from package
anki-utils asset preview-template --output /home/claude/preview.jsx

# Preprocess test data (converts image paths to base64 for iframe compatibility)
TEST_DATA=$(anki-utils preprocess-test-data \
    /mnt/skills/user/anki-flashcards/assets/test-data/test-cards.json \
    /mnt/skills/user/anki-flashcards/assets/test-data)

# Get theme CSS as JSON
THEMES_JSON=$(anki-utils themes --all-json)

# Inject both placeholders using Python (safer for large strings)
python3 -c "
import subprocess
with open('/home/claude/preview.jsx', 'r') as f: content = f.read()
content = content.replace('__THEMES_PLACEHOLDER__', '''$THEMES_JSON''')
content = content.replace('__CARD_DATA_PLACEHOLDER__', '''$TEST_DATA''')
with open('/home/claude/preview.jsx', 'w') as f: f.write(content)
"
```
Present `/home/claude/preview.jsx`. **Done.**

---

## Intent Detection

Detect user intent and route to the appropriate workflow:

| User Intent | Signals | Route To |
|-------------|---------|----------|
| **Quick cards** | Vocab terms, acronyms, pre-formatted Q&A, person photo/details, image recognition, "make a card for X" | [workflows/quick-cards.md](workflows/quick-cards.md) |
| **Document extraction** | Uploads PDF/doc, "turn this into cards", "extract from this" | [workflows/document-extraction.md](workflows/document-extraction.md) |
| **Batch import** | Has structured data (CSV, JSON, list), "convert these" | [workflows/batch-import.md](workflows/batch-import.md) |
| **Review cycle** | "preview", "let me review", returns feedback JSON | [workflows/review-cycle.md](workflows/review-cycle.md) |
| **Image occlusion** | Diagram + "label this", anatomy image, wants to occlude regions | [references/image-occlusion.md](references/image-occlusion.md) |

If intent is unclear, **ask one clarifying question** then proceed with best guess.

---

## Core Principle

Flashcards work through **retrieval practice**: recalling knowledge strengthens memory. Cards must be focused (one concept), precise (unambiguous), and effortful (requires genuine recall).

---

## Card Types Reference

| Type | Use For | Output |
|------|---------|--------|
| **Front-Back** | Questions, procedures, cause-effect | 1 card |
| **Bidirectional Concept** | Vocabulary, terminology | 2 cards |
| **Cloze Deletion** | Lists of 3+ items, sequences | 1 card per cloze |
| **Image Recognition** | Visual ID: landmarks, art, species | 1 card |
| **Image Occlusion** | Labeling diagrams, anatomy, maps | 1 card per region |
| **Person** | Names, faces, contact details | 1 card per field |

**Format detection:**
- Ends with "?" → Front-Back
- Single term/definition → Bidirectional Concept
- 3+ item list → Cloze
- Image + "what is this" → Image Recognition
- Diagram + "label" → Image Occlusion
- Person details → Person

---

## Quality Checklist (Apply Before Export)

Every card must pass:

1. **Atomic** - One concept only
2. **Interview-proof** - No "but why?" follow-up possible
3. **Self-contained** - Answer needs no external context
4. **Right type** - Card type matches knowledge type (see table)
5. **Complexity handled** - 3+ items use Cloze, not Q→A

**→ Detailed guidance:** [references/quality-fixes.md](references/quality-fixes.md)

---

## Default Output

Always generate `.apkg` file unless user requests Obsidian format.

**→ Export instructions:** [references/apkg-export.md](references/apkg-export.md)

---

## Onboarding

First-time users (no `anki-flashcards-onboarded` memory):
1. Present `artifacts/onboarding.html`
2. Create memory: `anki-flashcards-onboarded: true`
3. Continue with task

Returning users: Occasionally mention "/anki-help" is available.
