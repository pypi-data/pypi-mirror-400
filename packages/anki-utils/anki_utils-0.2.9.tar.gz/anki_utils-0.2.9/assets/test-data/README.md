# Test Cards Documentation

Test cards for validating theme rendering, card generation, and edge case handling.

## Card Types Covered

| Card Type | Count | Purpose |
|-----------|-------|---------|
| front-back | 6 | Basic Q&A format |
| concept | 3 | Term/definition pairs |
| cloze | 4 | Fill-in-the-blank |
| image | 1 | Image-based recognition |
| person | 1 | Contact/person cards |
| image-occlusion | 1 | Diagram label masking |

## Edge Case Test Cards

Cards tagged with `edge-case` exercise specific rendering challenges:

### Long Text (tag: `long-text`)
- **Card**: Machine Learning Definition
- **Tests**: Text overflow, paragraph spacing, bullet list rendering, lengthy content layout

### Code Blocks (tag: `code-block`)
- **Card**: Fibonacci Function (cloze)
- **Tests**: Syntax highlighting, monospace fonts, code block background, cloze deletions inside code

### Complex Markdown (tag: `complex-markdown`)
- **Card**: TCP vs UDP Comparison
- **Tests**: Headers (h2, h3), nested lists, markdown tables, mixed formatting

### Unicode - Japanese (tag: `unicode`, `japanese`)
- **Card**: Katakana Explanation
- **Tests**: CJK character rendering, mixed Japanese/English text, emoji support

### RTL Script - Arabic (tag: `rtl`, `arabic`)
- **Card**: القرآن الكريم (Quran) concept
- **Tests**: Right-to-left text direction, Arabic script rendering, mixed RTL/LTR content

### Special Characters (tag: `special-characters`)
- **Card**: Escape Sequences (cloze)
- **Tests**: Backslash handling, escape sequences in inline code, special character display

### Math Symbols (tag: `math`)
- **Card**: Set Notation Symbols
- **Tests**: Mathematical Unicode symbols (∈, ∅, ∀, ∃, ℕ, ℤ, ℝ), tables with symbols, subscripts

## Running Tests

```bash
# Validate JSON syntax
python -c "import json; json.load(open('assets/test-data/test-cards.json'))"

# Generate test deck
anki-utils export-apkg assets/test-data/test-cards.json -o test-deck.apkg

# Run full test suite
pytest -v
```

## Image Occlusion Notes

- Sample diagram: `assets/test-data/heart-anatomy.jpg` (used by image-occlusion test data).
- Expected export behavior: IO notes embed SVG masks in the image field, cloze labels in the text field, and occlusion JSON in the data field.
- Manual Anki check: import the generated .apkg and confirm masks align to the heart chambers on front, with labels revealed on back.

## Adding New Test Cards

1. Add the card to `test-cards.json`
2. Tag with `edge-case` plus specific tags (e.g., `unicode`, `code-block`)
3. Update this README with what the card tests
4. Run validation to ensure JSON is valid
