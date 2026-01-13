#!/bin/bash
# theme-designer-launch.sh
# Generates a theme designer artifact with current themes and sample data
#
# Usage: 
#   bash theme-designer-launch.sh [working_themes_json_file] [injected_css_file]
#
# Arguments:
#   working_themes_json_file - Optional path to a JSON file with working theme definitions
#                              If not provided, no working themes are added
#   injected_css_file - Optional path to a CSS file to inject into previews
#
# Output:
#   Creates /home/claude/theme-designer.jsx ready for presentation

set -e

# Determine repo root (local dev or installed skill)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if git -C "$SCRIPT_DIR" rev-parse --show-toplevel >/dev/null 2>&1; then
    SKILL_DIR="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
elif [ -d "/home/claude/anki-flashcards" ]; then
    SKILL_DIR="/home/claude/anki-flashcards"
elif [ -d "/mnt/skills/user/anki-flashcards" ]; then
    SKILL_DIR="/mnt/skills/user/anki-flashcards"
else
    echo "❌ Unable to locate skill directory." >&2
    exit 1
fi

WORKING_THEMES_FILE="${1:-}"
INJECTED_CSS_FILE="${2:-}"

echo "🎨 Generating Theme Designer artifact..."
echo "Using skill directory: $SKILL_DIR"

python3 << PYTHON_SCRIPT
import importlib
import importlib.util
import importlib.resources
import sys
import os
import json

# Configuration
skill_dir = "$SKILL_DIR"
working_themes_file = "$WORKING_THEMES_FILE"
injected_css_file = "$INJECTED_CSS_FILE"
default_output_dir = "/home/claude"
output_dir = default_output_dir if os.path.isdir(default_output_dir) else os.path.expanduser("~")
output_file = os.path.join(output_dir, "theme-designer.jsx")

# Add scripts directory to path
scripts_dir = os.path.join(skill_dir, "scripts")
sys.path.insert(0, scripts_dir)
sys.path.insert(0, skill_dir)

# Import theme definitions
def import_themes_module():
    for module_name in ("anki_utils.themes", "themes"):
        if importlib.util.find_spec(module_name):
            return importlib.import_module(module_name), module_name
    raise ImportError("Unable to import theme definitions from anki_utils.themes or themes.")

themes_module, themes_source = import_themes_module()
print(f"Using theme definitions from {themes_source}")

# Build production themes dict
if hasattr(themes_module, "CLASSIC_BASE"):
    production_themes = {
        "minimal": {
            "base": themes_module.MINIMAL_BASE,
            "conceptInstruction": themes_module.MINIMAL_CONCEPT_INSTRUCTION,
            "image": themes_module.MINIMAL_IMAGE,
            "person": themes_module.MINIMAL_PERSON,
            "io": themes_module.MINIMAL_IO,
        },
        "classic": {
            "base": themes_module.CLASSIC_BASE,
            "conceptInstruction": themes_module.CLASSIC_CONCEPT_INSTRUCTION,
            "image": themes_module.CLASSIC_IMAGE,
            "person": themes_module.CLASSIC_PERSON,
            "io": themes_module.CLASSIC_IO,
        },
        "high-contrast": {
            "base": themes_module.HIGH_CONTRAST_BASE,
            "conceptInstruction": themes_module.HIGH_CONTRAST_CONCEPT_INSTRUCTION,
            "image": themes_module.HIGH_CONTRAST_IMAGE,
            "person": themes_module.HIGH_CONTRAST_PERSON,
            "io": themes_module.HIGH_CONTRAST_IO,
        },
        "calm": {
            "base": themes_module.CALM_BASE,
            "conceptInstruction": themes_module.CALM_CONCEPT_INSTRUCTION,
            "image": themes_module.CALM_IMAGE,
            "person": themes_module.CALM_PERSON,
            "io": themes_module.CALM_IO,
        },
    }
else:
    production_themes = {
        "minimal": {
            "base": themes_module.MINIMAL_BASE,
            "conceptInstruction": themes_module.MINIMAL_CONCEPT_INSTRUCTION,
            "image": themes_module.MINIMAL_IMAGE,
            "person": themes_module.MINIMAL_PERSON,
            "io": getattr(themes_module, "MINIMAL_IO", ""),
        },
        "rich": {
            "base": themes_module.RICH_BASE,
            "conceptInstruction": themes_module.RICH_CONCEPT_INSTRUCTION,
            "image": themes_module.RICH_IMAGE,
            "person": themes_module.RICH_PERSON,
            "io": getattr(themes_module, "RICH_IO", ""),
        },
        "bold": {
            "base": themes_module.BOLD_BASE,
            "conceptInstruction": themes_module.BOLD_CONCEPT_INSTRUCTION,
            "image": themes_module.BOLD_IMAGE,
            "person": themes_module.BOLD_PERSON,
            "io": getattr(themes_module, "BOLD_IO", ""),
        },
        "ios": {
            "base": themes_module.IOS_BASE,
            "conceptInstruction": themes_module.IOS_CONCEPT_INSTRUCTION,
            "image": themes_module.IOS_IMAGE,
            "person": themes_module.IOS_PERSON,
            "io": getattr(themes_module, "IOS_IO", ""),
        },
    }

missing_io = [key for key, theme in production_themes.items() if not theme.get("io")]
if missing_io:
    print(f"Warning: Missing IO styles for theme(s): {', '.join(missing_io)}")

# Load working themes from file if provided
working_themes = {}
if working_themes_file and os.path.exists(working_themes_file):
    with open(working_themes_file, 'r') as f:
        working_themes = json.load(f)
    print(f"Loaded {len(working_themes)} working theme(s) from {working_themes_file}")

# Load injected CSS if provided
injected_css = ""
if injected_css_file and os.path.exists(injected_css_file):
    with open(injected_css_file, "r") as f:
        injected_css = f.read()
    print(f"Loaded injected CSS from {injected_css_file}")

# Load and preprocess sample cards (convert image paths to base64 for iframe compatibility)
import subprocess
preprocess_script = os.path.join(skill_dir, "developer", "tools", "preprocess_test_data.py")

def first_existing_path(label, candidates):
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(f"Unable to locate {label}. Tried: {candidates}")

def load_theme_designer_template():
    if themes_source == "anki_utils.themes":
        try:
            return importlib.resources.files("anki_utils").joinpath(
                "assets", "theme-designer.jsx"
            ).read_text(encoding="utf-8")
        except Exception as exc:
            print(f"Warning: unable to load theme designer asset from anki_utils: {exc}")
    template_file = first_existing_path(
        "theme designer template",
        [
            os.path.join(skill_dir, "anki_utils", "assets", "theme-designer.jsx"),
            os.path.join(skill_dir, "assets", "theme-designer.jsx"),
            os.path.join(skill_dir, "artifacts", "theme-designer.jsx"),
        ],
    )
    with open(template_file, "r") as f:
        return f.read()

sample_cards_file = first_existing_path(
    "sample cards",
    [
        os.path.join(skill_dir, "assets", "test-data", "test-cards.json"),
        os.path.join(skill_dir, "anki_utils", "assets", "test-data", "test-cards.json"),
    ],
)
test_data_dir = os.path.dirname(sample_cards_file)

result = subprocess.run(
    ["python3", preprocess_script, sample_cards_file, test_data_dir],
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print(f"Error preprocessing test data: {result.stderr}", file=sys.stderr)
    sys.exit(1)

sample_cards = json.loads(result.stdout)

def count_base64_embeds(value):
    if isinstance(value, dict):
        return sum(count_base64_embeds(item) for item in value.values())
    if isinstance(value, list):
        return sum(count_base64_embeds(item) for item in value)
    if isinstance(value, str):
        return value.count("data:image/")
    return 0

embed_count = count_base64_embeds(sample_cards)
print(f"Embedded {embed_count} base64 image(s) in sample cards.")

# Read template
content = load_theme_designer_template()

# Replace placeholders with JSON
content = content.replace('__PRODUCTION_THEMES_PLACEHOLDER__', json.dumps(production_themes))
content = content.replace('__WORKING_THEMES_PLACEHOLDER__', json.dumps(working_themes))
content = content.replace('__SAMPLE_CARDS_PLACEHOLDER__', json.dumps(sample_cards))
content = content.replace('__INJECTED_CSS_PLACEHOLDER__', json.dumps(injected_css))

# Write output
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w') as f:
    f.write(content)

print(f"✅ Theme Designer ready: {output_file}")
print()
print("Present the file to the developer:")
print(f"  present_files(['{output_file}'])")
PYTHON_SCRIPT
