#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _replace_json_block(html: str, block_id: str, content: str) -> str:
    pattern = re.compile(
        rf'(<script type="application/json" id="{re.escape(block_id)}">)(.*?)(</script>)',
        re.DOTALL,
    )
    if not pattern.search(html):
        raise ValueError(f"Missing JSON block: {block_id}")
    return pattern.sub(lambda m: f"{m.group(1)}{content}{m.group(3)}", html, count=1)


def _preprocess_test_data(script_path: Path, json_path: Path, base_dir: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(script_path), str(json_path), str(base_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to preprocess test data.")
    return json.loads(result.stdout)


def main() -> int:
    repo_root = _repo_root()
    launcher_path = repo_root / "developer" / "test-launcher.html"
    preview_template_path = repo_root / "anki_utils" / "assets" / "preview-template.jsx"
    theme_template_path = repo_root / "anki_utils" / "assets" / "theme-designer.jsx"
    shared_preview_path = repo_root / "anki_utils" / "assets" / "shared-preview.jsx"
    pure_functions_path = repo_root / "anki_utils" / "assets" / "pure-functions.js"
    sample_cards_path = repo_root / "assets" / "test-data" / "test-cards.json"
    preprocess_script = repo_root / "developer" / "tools" / "preprocess_test_data.py"

    html = launcher_path.read_text(encoding="utf-8")
    preview_template = preview_template_path.read_text(encoding="utf-8")
    theme_template = theme_template_path.read_text(encoding="utf-8")
    shared_preview = shared_preview_path.read_text(encoding="utf-8")
    pure_functions = pure_functions_path.read_text(encoding="utf-8")

    sys.path.insert(0, str(repo_root))
    from anki_utils import themes  # pylint: disable=import-error

    production_themes = {
        name: themes.get_theme_sections(name) for name in themes.THEMES
    }
    sample_cards = _preprocess_test_data(
        preprocess_script, sample_cards_path, repo_root
    )

    html = _replace_json_block(
        html,
        "pure-functions-source",
        json.dumps(pure_functions, ensure_ascii=False),
    )
    html = _replace_json_block(
        html,
        "preview-template-source",
        json.dumps(preview_template, ensure_ascii=False),
    )
    html = _replace_json_block(
        html,
        "shared-preview-source",
        json.dumps(shared_preview, ensure_ascii=False),
    )
    html = _replace_json_block(
        html,
        "theme-template-source",
        json.dumps(theme_template, ensure_ascii=False),
    )
    html = _replace_json_block(
        html,
        "sample-cards-data",
        json.dumps(sample_cards, ensure_ascii=False, separators=(",", ":")),
    )
    html = _replace_json_block(
        html,
        "production-themes-data",
        json.dumps(production_themes, ensure_ascii=False, separators=(",", ":")),
    )
    html = _replace_json_block(
        html,
        "working-themes-data",
        json.dumps({}, ensure_ascii=False),
    )

    launcher_path.write_text(html, encoding="utf-8")
    print(f"Updated {launcher_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
