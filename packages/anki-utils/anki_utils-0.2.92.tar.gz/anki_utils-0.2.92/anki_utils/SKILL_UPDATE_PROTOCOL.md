# Skill Update Protocol

> This document is for the Claude skill that consumes `anki-utils`.
> It describes how to check for updates and validate that everything works.

## When to Check for Updates

Check for package updates:
1. At the start of any card creation session
2. When encountering unexpected errors
3. When the user mentions updating or new features

## Update Check Procedure

```python
import subprocess
import json

# 1. Get current package version
result = subprocess.run(['anki-utils', 'version', '--json'], capture_output=True, text=True)
current_version = json.loads(result.stdout)['version']

# 2. Compare with your stored version
if current_version != stored_version:
    # 3. Get migration instructions
    result = subprocess.run(
        ['anki-utils', 'migrations', '--since', stored_version, '--json'],
        capture_output=True, text=True
    )
    migrations = json.loads(result.stdout)

    # 4. Follow each migration's skill_instructions
    for entry in migrations.get('entries', []):
        # Read and apply entry['skill_instructions']
        pass

    # 5. Run validation tests (see below)
    # 6. Update stored_version = current_version
```

## Validation Test Suite

After any update, run these tests to confirm everything works. Each test should complete without errors.

### Test 1: Basic Card Types

Create a test package with one of each card type:

```python
import subprocess
import json
import tempfile
import os

test_data = {
    "deck_name": "Validation Test",
    "theme": "minimal",
    "cards": [
        {
            "type": "front-back",
            "question": "What is 2 + 2?",
            "answer": "4"
        },
        {
            "type": "concept",
            "concept": "Photosynthesis",
            "definition": "Process by which plants convert light to energy"
        },
        {
            "type": "cloze",
            "cloze_text": "The capital of France is {{c1::Paris}}"
        }
    ]
}

# Write to temp file and run export
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(test_data, f)
    input_path = f.name

output_path = tempfile.mktemp(suffix='.apkg')

result = subprocess.run(
    ['anki-utils', 'export-apkg', '--input', input_path, '--output', output_path],
    capture_output=True, text=True
)

# Verify success
assert result.returncode == 0, f"Export failed: {result.stderr}"
assert os.path.exists(output_path), "Output file not created"
assert os.path.getsize(output_path) > 0, "Output file is empty"

# Clean up
os.unlink(input_path)
os.unlink(output_path)

print("✓ Test 1 passed: Basic card types")
```

### Test 2: All Themes

Verify each theme produces valid output:

```python
themes = ['minimal', 'rich', 'bold', 'ios']

for theme in themes:
    test_data = {
        "deck_name": f"Theme Test - {theme}",
        "theme": theme,
        "cards": [
            {"type": "front-back", "question": "Test Q", "answer": "Test A"}
        ]
    }

    # Export and verify (same pattern as Test 1)
    # ...

print("✓ Test 2 passed: All themes")
```

### Test 3: Preview Template Injection

Verify the preview template works with theme injection:

```python
import subprocess

# Get theme CSS
themes_result = subprocess.run(
    ['anki-utils', 'themes', '--all-json'],
    capture_output=True, text=True
)
assert themes_result.returncode == 0, "Failed to get themes"

themes_json = themes_result.stdout

# Get preview template
template_result = subprocess.run(
    ['anki-utils', 'asset', 'preview-template.jsx'],
    capture_output=True, text=True
)
assert template_result.returncode == 0, "Failed to get preview template"

template = template_result.stdout

# Verify placeholder exists
assert '__THEMES_PLACEHOLDER__' in template, "Theme placeholder missing from template"

# Inject themes
injected = template.replace('__THEMES_PLACEHOLDER__', themes_json)

# Verify injection worked
assert '__THEMES_PLACEHOLDER__' not in injected, "Theme placeholder not replaced"
assert '"minimal"' in injected, "Theme data not injected correctly"

print("✓ Test 3 passed: Preview template injection")
```

### Test 4: Image Occlusion (if supported)

```python
test_data = {
    "deck_name": "IO Validation",
    "cards": [
        {
            "type": "image-occlusion",
            "image_path": "/path/to/test/image.png",  # Use actual test image
            "header": "Label the diagram",
            "occlusions": [
                {
                    "cloze_num": 1,
                    "label": "Part A",
                    "shape": "rect",
                    "left": 0.1,
                    "top": 0.1,
                    "width": 0.2,
                    "height": 0.2
                }
            ]
        }
    ]
}

# Export and verify
# ...

print("✓ Test 4 passed: Image occlusion")
```

### Test 5: Person Cards

```python
test_data = {
    "deck_name": "Person Validation",
    "cards": [
        {
            "type": "person",
            "full_name": "Ada Lovelace",
            "title": "Mathematician",
            "company": "None",
            "birthday": "December 10"
        }
    ]
}

# Export and verify
# ...

print("✓ Test 5 passed: Person cards")
```

## Validation Summary

After running all tests, output a summary:

```
=== anki-utils Validation Complete ===
Version: X.Y.Z
Tests passed: 5/5

✓ Basic card types (front-back, concept, cloze)
✓ All themes (minimal, rich, bold, ios)
✓ Preview template injection
✓ Image occlusion cards
✓ Person cards

Ready for production use.
```

## If Validation Fails

1. Note the specific test that failed
2. Check MIGRATIONS.md for any missed instructions
3. Report the error to the user with:
   - Which test failed
   - The error message
   - Current package version
4. Suggest running `pip install --upgrade anki-utils`

## Preview Template Launch

When launching the card preview:

```python
import subprocess

# 1. Get theme CSS
themes_json = subprocess.check_output(['anki-utils', 'themes', '--all-json']).decode()

# 2. Get template
template = subprocess.check_output(['anki-utils', 'asset', 'preview-template.jsx']).decode()

# 3. Inject themes
template = template.replace('__THEMES_PLACEHOLDER__', themes_json)

# 4. Inject card data
template = template.replace('__CARD_DATA_PLACEHOLDER__', card_data_json)

# 5. Render as artifact
```

## Version History

For version-specific changes and instructions, query:
```bash
anki-utils migrations --json
```

This is the source of truth for what changed in each version and what the skill needs to do.
