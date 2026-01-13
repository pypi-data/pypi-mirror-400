#!/usr/bin/env python3
"""
Bundle artifacts for Claude's artifact runtime.

This script inlines shared components into preview-template.jsx and theme-designer.jsx,
producing self-contained bundled versions that work in Claude's isolated artifact environment.

Inlined components:
- shared-preview.jsx: SharedCardPreview component
- pure-functions.js: Pure utility functions (getCardCSS, escapeHtml, etc.)

The source files use placeholders that get replaced with inlined code:
- const SharedCardPreview = window.SharedCardPreview;
- const { ... } = window.PureFunctions;

Output files are written to anki_utils/assets/bundled/
"""
from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _extract_shared_component(shared_preview_content: str) -> str:
    """
    Extract the SharedCardPreview component from shared-preview.jsx.

    Removes the window.SharedCardPreview export line since the bundled version
    will have the component defined inline.
    """
    # Remove the window export line
    content = re.sub(
        r"^\s*window\.SharedCardPreview\s*=\s*SharedCardPreview;\s*$",
        "",
        shared_preview_content,
        flags=re.MULTILINE,
    )
    # Remove the "Export for consumption" comment if present
    content = re.sub(
        r"^\s*//\s*Export for consumption.*$",
        "",
        content,
        flags=re.MULTILINE,
    )
    return content.strip()


def _extract_pure_functions(pure_functions_content: str) -> str:
    """
    Extract pure functions from pure-functions.js for inlining.

    Removes:
    - ES module export statement (export { ... })
    - window.PureFunctions assignment (browser global export)
    - Related comments and section headers
    """
    content = pure_functions_content

    # Remove the entire EXPORTS section (everything from the header to end of file)
    # This includes: section header, ES module exports, comments, and window assignment
    content = re.sub(
        r"// =+\n// EXPORTS\n// =+\n[\s\S]*$",
        "",
        content,
    )

    return content.strip()


def _bundle_shared_component(source_content: str, shared_component: str) -> str:
    """
    Replace the SharedCardPreview placeholder with the inlined component.

    The placeholder is: const SharedCardPreview = window.SharedCardPreview;
    We replace it with the actual component definition.
    """
    # Pattern matches the line that reads from window.SharedCardPreview
    pattern = r"^\s*const\s+SharedCardPreview\s*=\s*window\.SharedCardPreview;\s*$"

    if not re.search(pattern, source_content, re.MULTILINE):
        raise ValueError(
            "Could not find 'const SharedCardPreview = window.SharedCardPreview;' "
            "placeholder in source file"
        )

    # Replace with the inlined component
    replacement = f"""// =============================================================================
// SHARED CARD PREVIEW COMPONENT (Inlined by bundle-artifacts.py)
// Source: anki_utils/assets/shared-preview.jsx
// =============================================================================
{shared_component}
// =============================================================================
// END SHARED CARD PREVIEW COMPONENT
// ============================================================================="""

    return re.sub(pattern, replacement, source_content, count=1, flags=re.MULTILINE)


def _bundle_pure_functions(source_content: str, pure_functions: str) -> str:
    """
    Replace the PureFunctions placeholder with inlined functions.

    The placeholder is: const { ... } = window.PureFunctions;
    We replace it with the actual function definitions.
    """
    # Pattern matches the destructuring from window.PureFunctions
    # This is a multi-line pattern that captures the entire block
    pattern = r"^\s*const\s*\{\s*[\s\S]*?\}\s*=\s*window\.PureFunctions;\s*$"

    match = re.search(pattern, source_content, re.MULTILINE)
    if not match:
        raise ValueError(
            "Could not find 'const { ... } = window.PureFunctions;' "
            "placeholder in source file"
        )

    # Build the replacement (can't use re.sub because pure_functions contains \d, etc.)
    replacement = f"""// =============================================================================
// PURE FUNCTIONS (Inlined by bundle-artifacts.py)
// Source: anki_utils/assets/pure-functions.js
// =============================================================================
{pure_functions}
// =============================================================================
// END PURE FUNCTIONS
// ============================================================================="""

    # Replace using string slicing to avoid regex escaping issues
    return source_content[: match.start()] + replacement + source_content[match.end() :]


def main() -> int:
    repo_root = _repo_root()

    # Source paths
    shared_preview_path = repo_root / "anki_utils" / "assets" / "shared-preview.jsx"
    pure_functions_path = repo_root / "anki_utils" / "assets" / "pure-functions.js"
    preview_template_path = repo_root / "anki_utils" / "assets" / "preview-template.jsx"
    theme_designer_path = repo_root / "anki_utils" / "assets" / "theme-designer.jsx"

    # Output directory
    bundled_dir = repo_root / "anki_utils" / "assets" / "bundled"
    bundled_dir.mkdir(exist_ok=True)

    # Read source files
    shared_preview = shared_preview_path.read_text(encoding="utf-8")
    pure_functions = pure_functions_path.read_text(encoding="utf-8")
    preview_template = preview_template_path.read_text(encoding="utf-8")
    theme_designer = theme_designer_path.read_text(encoding="utf-8")

    # Extract components (without export statements)
    shared_component = _extract_shared_component(shared_preview)
    pure_funcs = _extract_pure_functions(pure_functions)

    # Bundle preview-template.jsx (needs both pure functions and shared component)
    bundled_preview = preview_template
    bundled_preview = _bundle_pure_functions(bundled_preview, pure_funcs)
    bundled_preview = _bundle_shared_component(bundled_preview, shared_component)

    # Bundle theme-designer.jsx (only needs shared component)
    bundled_theme = _bundle_shared_component(theme_designer, shared_component)

    # Write bundled files
    bundled_preview_path = bundled_dir / "preview-template.jsx"
    bundled_theme_path = bundled_dir / "theme-designer.jsx"

    bundled_preview_path.write_text(bundled_preview, encoding="utf-8")
    bundled_theme_path.write_text(bundled_theme, encoding="utf-8")

    print(f"Bundled: {bundled_preview_path}")
    print(f"Bundled: {bundled_theme_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
