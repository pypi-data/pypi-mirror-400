# Changelog

> Query via CLI: `anki-utils changelog`

All notable changes to the anki-utils package.

## [Unreleased]

### Changed
- Preview tool: Cards are now auto-approved when flipped from front to back
- Preview tool: Tapping again (or pressing Space) advances to next card instead of flipping back
- Preview tool: Updated onboarding instructions and keyboard hints to reflect new flow

### Fixed
- Preview tool: Summary screen cards are now clickable to return to review mode (Issue #107)
- Theme designer: Removed rounded corners from card preview wrapper for accurate Anki card rendering (cards should have sharp corners)
- Preview tool: Removed excess padding around the app container for tighter layout
- Preview tool: Keyboard shortcut hints now hidden on mobile devices (768px and below) where they don't work

---

## [0.2.9] - 2026-01-04

### Added
- GitHub Action (`version-docs.yml`) that automatically versions CHANGELOG.md and MIGRATIONS.md on release - converts `[Unreleased]` sections to proper version numbers
- `anki-utils export-apkg --base-path` to resolve relative media paths when bundling images.
- Preview tool: Keyboard shortcuts for desktop review (Space=flip, A=approve, E=edit, X=remove, arrows=navigate)
- Preview tool: Keyboard hints bar showing available shortcuts
- Image occlusion cards now accept `image_data` (base64 data URL) as an alternative to `image_path`
- Optional `image_width` and `image_height` fields for explicit dimension control
- Dimensions are automatically extracted from base64 data if not explicitly provided
- Build step (`bundle-artifacts.py`) that produces self-contained bundled artifacts for Claude runtime

### Changed
- Preview tool: Action buttons (approve/edit/remove) are now immediately active without requiring a card flip first
- Preview tool: Progress bar now uses continuous fill with "X of Y" counter (scales to 50+ cards)
- Preview tool: Export button now shows "✓ Copied!" confirmation with green highlight for 2 seconds

### Fixed
- Image occlusion exports now embed base64 image data in SVGs so Anki renders the base image.
- Image occlusion cards now fail loudly with a clear error when neither `image_path` nor `image_data` is usable, instead of silently falling back to a broken filename reference.
- **Preview template white screen fix** (Issue #71): Preview and theme designer artifacts now bundle `SharedCardPreview` inline, so they work in Claude's isolated artifact runtime without the white screen crash.

---

## [0.2.2] - 2025-01-01

### Changed
- **Theme Redesign**: Renamed and redesigned 3 of 4 visual themes for better differentiation
  - `rich` → `classic`: Serif typography (Georgia), warm cream (#faf8f3) backgrounds, scholarly academic feel
  - `bold` → `high-contrast`: WCAG AA compliant, 20px base text, strong borders, accessibility-focused
  - `ios` → `calm`: Muted pastels (#f7f8fc background), soft shadows, relaxed feel for long study sessions
  - `minimal`: Unchanged (clean, system fonts, subtle colors)
- All themes support light and dark mode with consistent styling across 6 card types

### Breaking Changes
- Theme identifiers changed: `rich`→`classic`, `bold`→`high-contrast`, `ios`→`calm`
- Users requesting old theme names will fall back to `minimal` with a warning

---

## [0.2.3] - 2025-01-01

### Added
- Image Occlusion exporter now embeds the image inside an SVG with pre-rendered masks for export parity with preview

### Changed
- Image Occlusion model now uses `ImageSVG` field instead of `Image`
- Theme designer launch script now supports local development and skill environments
- Theme designer now imports themes from `anki_utils` with legacy fallbacks and includes IO theme styles
- Theme designer preprocesses sample cards to base64 images and reports embedded image counts

---

## [0.2.1] - 2025-01-01

### Added
- `anki-utils migrations` CLI command for querying migration instructions
- `anki-utils version` CLI command to check current package version
- `anki-utils roadmap --html` flag for styled HTML output
- `MIGRATIONS.md` file with structured agent-to-agent update protocol

### Agent Integration
- Migration system allows consuming agents to track and apply updates
- JSON output format for programmatic parsing (`--json` flag)
- Version filtering with `--since` flag to get only new migrations
- Skill instructions included in each migration entry

---

## [0.2.0] - 2025-01-01

### Added
- `anki-utils roadmap` CLI command to view development roadmap
- `anki-utils changelog` CLI command to view version history
- `docs/VISION.md` - End-state description for agent context
- `docs/ARCHITECTURE.md` - Technical documentation of code structure
- `docs/AGENT_GUIDE.md` - Working conventions for autonomous development
- `archive/` directory for legacy reference files

### Changed
- Restructured repository for agent-driven development
- Moved ROADMAP.md and CHANGELOG.md into package for distribution
- Archived `scripts/` directory (was duplicating `anki_utils/`)
- Archived `workflows/` and `references/` (Claude skill files)

### Fixed
- Documentation now reflects actual package structure (was referencing old scripts/)

---

## [0.1.1] - 2024-12

### Added
- OCR-based region detection for image occlusion cards (`occlusion.py`)
- Tesseract integration for automatic text label detection
- Multi-line label merging for complex diagrams
- Grid overlay generation for unlabeled images
- Preview image generation with bounding boxes
- Image occlusion CSS improvements for minimal theme

### Changed
- Preview now embeds images inside SVG for better mask alignment
- `preprocess_test_data.py` extracts image dimensions via PIL
- Rectangular masks only (cleaner appearance)

### Fixed
- Image occlusion coordinate system documentation
- Theme CSS sync between themes.py and preview-template.jsx

---

## [0.1.0] - 2024-11

### Added
- Initial PyPI release as `anki-utils`
- Core card types: Front-Back, Concept, Cloze, Image, Person, Image Occlusion
- Four themes: minimal, rich, bold, ios
- CLI interface with subcommands
- Preview template (React/JSX)
- Theme designer tool
- genanki integration for .apkg generation

### Infrastructure
- setuptools-scm for version management
- GitHub Actions for PyPI publishing
