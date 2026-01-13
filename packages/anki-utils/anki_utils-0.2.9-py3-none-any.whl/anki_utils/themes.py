"""
CSS Theme Definitions for Anki Flashcards

This module defines 4 visual themes for card styling:
- minimal: Clean whitespace, system fonts, subtle colors (default)
- classic: Serif typography, warm cream backgrounds, scholarly/academic feel
- high-contrast: Strong colors, clear hierarchy, WCAG AA accessibility compliant
- calm: Muted pastels, soft shadows, relaxed feel for long study sessions

Each theme creates separate Anki model IDs so users can review
and compare styles before committing to one.

CSS Injection for Preview
-------------------------
The CSS in this file is the source of truth for all card themes. The
preview-template.jsx uses a placeholder (__THEMES_PLACEHOLDER__) that
gets replaced at runtime with output from `anki-utils themes --all-json`.

This injection approach means:
1. This file generates CSS for actual Anki .apkg files
2. preview-template.jsx receives CSS dynamically (no manual sync needed)
3. The get_theme_sections() function defines the structure injected into JSX

Contract with preview-template.jsx:
- get_theme_sections() must return: {base, conceptInstruction, image, person, io}
- The JSX's getCardCSS() function accesses these exact keys
- Tests in test_themes.py::TestPreviewTemplateContract verify this contract
"""

# Theme identifiers
THEMES = ['minimal', 'classic', 'high-contrast', 'calm']
DEFAULT_THEME = 'minimal'

# Model ID offsets for each theme (added to base model ID)
# This creates unique model IDs per theme
THEME_OFFSETS = {
    'minimal': 0,
    'classic': 100,
    'high-contrast': 200,
    'calm': 300,
}

# Theme display names for Anki
THEME_NAMES = {
    'minimal': '',           # Default, no suffix
    'classic': ' (Classic)',
    'high-contrast': ' (High Contrast)',
    'calm': ' (Calm)',
}


def get_theme_model_id(base_id: int, theme: str) -> int:
    """Get the model ID for a specific theme variant."""
    offset = THEME_OFFSETS.get(theme, 0)
    return base_id + offset


def get_theme_model_name(base_name: str, theme: str) -> str:
    """Get the model name for a specific theme variant."""
    suffix = THEME_NAMES.get(theme, '')
    return base_name + suffix


# =============================================================================
# MINIMAL THEME - Clean whitespace, system fonts, subtle colors
# =============================================================================

MINIMAL_BASE = '''html { overflow: scroll; overflow-x: hidden; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 18px;
    color: #333;
    background-color: #FFFFFF;
    margin: 0;
    padding: 20px;
    line-height: 1.5;
}

.card-header {
    font-size: 13px;
    color: #999;
    text-align: left;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
}

.card-header p { margin: 2px 0; }

.question {
    font-weight: 600;
    color: #222;
    font-size: 20px;
    text-align: center;
    margin-bottom: 20px;
}

.answer {
    font-size: 18px;
    color: #444;
    text-align: left;
    margin-bottom: 16px;
}

.extra-info {
    font-size: 15px;
    color: #666;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #eee;
}

li { margin-bottom: 0.75em; }

.cloze {
    font-weight: 600;
    color: #0066cc;
}

/* DARK MODE */
.night_mode body {
    background-color: #1a1a1a;
    color: #e0e0e0;
}
.night_mode .card-header { color: #777; border-bottom-color: #333; }
.night_mode .question { color: #f0f0f0; }
.night_mode .answer { color: #ccc; }
.night_mode .extra-info { color: #999; border-top-color: #333; }
.night_mode .cloze { color: #4da6ff; }
'''

MINIMAL_CONCEPT_INSTRUCTION = '''
.concept-instruction {
    font-size: 13px;
    color: #888;
    text-align: center;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.night_mode .concept-instruction { color: #666; }
'''

MINIMAL_IMAGE = '''
.prompt {
    font-weight: 600;
    color: #222;
    font-size: 18px;
    text-align: center;
    margin-bottom: 12px;
}

.image-container {
    text-align: center;
    margin: 12px 0;
}

.image-container img {
    max-height: 45vh;
    max-width: 100%;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 4px;
}

.answer {
    font-size: 20px;
    font-weight: 600;
    color: #222;
    text-align: center;
    margin: 16px 0;
    padding: 12px;
    background-color: #f5f5f5;
    border-radius: 6px;
}

.night_mode .prompt { color: #f0f0f0; }
.night_mode .answer { background-color: #2a2a2a; color: #f0f0f0; }
'''

MINIMAL_PERSON = '''
.card {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 18px;
    text-align: center;
    color: #333;
    background-color: white;
    padding: 20px;
}

.card img {
    max-width: 280px;
    max-height: 280px;
    width: auto;
    height: auto;
    object-fit: contain;
    margin: 12px auto;
    display: block;
    border-radius: 8px;
}

hr {
    border: none;
    border-top: 1px solid #eee;
    margin: 16px 0;
}

.night_mode .card { background-color: #1a1a1a; color: #e0e0e0; }
.night_mode hr { border-top-color: #333; }
'''

MINIMAL_IO = '''
.io-header {
    font-size: 18px;
    font-weight: 600;
    color: #222;
    text-align: center;
    margin-bottom: 12px;
}

.io-container {
    position: relative;
    display: inline-block;
    width: 100%;
    max-width: 100%;
    text-align: center;
}

.io-container img {
    max-width: 100%;
    max-height: 55vh;
    display: block;
    margin: 0 auto;
}

.io-svg-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.io-mask { fill: #d0d0d0; stroke: #a0a0a0; stroke-width: 1; }
.io-mask-active { fill: #e85555; stroke: #cc3333; stroke-width: 1; }
.io-revealed { fill: transparent; stroke: #4CAF50; stroke-width: 1; stroke-dasharray: 3,2; }

.io-answer { display: none; }

.io-cloze-data { display: none; }

.io-back-extra {
    font-size: 15px;
    color: #666;
    margin-top: 12px;
    text-align: center;
}

.cloze { font-weight: 600; color: #2e7d32; }

.night_mode .io-header { color: #f0f0f0; }
.night_mode .io-mask { fill: #4a4a4a; stroke: #666666; }
.night_mode .io-mask-active { fill: #cc4444; stroke: #aa2222; }
.night_mode .io-revealed { stroke: #66bb6a; stroke-width: 1; }
.night_mode .io-back-extra { color: #999; }
.night_mode .cloze { color: #66bb6a; }
'''


# =============================================================================
# CLASSIC THEME - Elegant serif typography, warm cream backgrounds, scholarly feel
# =============================================================================

CLASSIC_BASE = '''html { overflow: scroll; overflow-x: hidden; }

body {
    font-family: Georgia, 'Times New Roman', 'Palatino Linotype', serif;
    font-size: 18px;
    color: #2d2318;
    background-color: #faf8f3;
    margin: 0;
    padding: 24px;
    line-height: 1.7;
}

.card-header {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 12px;
    color: #8b7355;
    text-align: left;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e8e0d4;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.card-header p { margin: 3px 0; }

.question {
    font-weight: normal;
    font-style: italic;
    color: #1a1410;
    font-size: 24px;
    text-align: center;
    margin-bottom: 28px;
    line-height: 1.5;
}

.answer {
    font-size: 18px;
    color: #3d3328;
    text-align: left;
    margin-bottom: 20px;
}

.extra-info {
    font-size: 15px;
    color: #6b5d4d;
    font-style: italic;
    margin-top: 20px;
    padding: 16px 20px;
    background-color: #f5f0e8;
    border-left: 3px solid #c9b99a;
    border-radius: 0 6px 6px 0;
}

li { margin-bottom: 0.9em; }

.cloze {
    font-weight: bold;
    color: #8b4513;
    background-color: #fdf5e6;
    padding: 2px 8px;
    border-radius: 4px;
}

/* DARK MODE */
.night_mode body {
    background-color: #1c1a17;
    color: #d8d2c8;
}
.night_mode .card-header { color: #8b7355; border-bottom-color: #3a352d; }
.night_mode .question { color: #f0ece4; }
.night_mode .answer { color: #c8c0b4; }
.night_mode .extra-info { color: #a89880; background-color: #2a2620; border-left-color: #5c5040; }
.night_mode .cloze { color: #daa520; background-color: #3a3020; }
'''

CLASSIC_CONCEPT_INSTRUCTION = '''
.concept-instruction {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 11px;
    color: #8b7355;
    text-align: center;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.night_mode .concept-instruction { color: #7a6545; }
'''

CLASSIC_IMAGE = '''
.prompt {
    font-style: italic;
    color: #1a1410;
    font-size: 20px;
    text-align: center;
    margin-bottom: 16px;
}

.image-container {
    text-align: center;
    margin: 20px 0;
}

.image-container img {
    max-height: 45vh;
    max-width: 100%;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(45, 35, 24, 0.15);
    border: 1px solid #e8e0d4;
}

.answer {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 20px;
    font-weight: 600;
    color: #2d2318;
    text-align: center;
    margin: 24px 0;
    padding: 16px 24px;
    background: linear-gradient(135deg, #faf8f3, #f5f0e8);
    border-radius: 8px;
    border: 1px solid #e8e0d4;
    box-shadow: 0 2px 6px rgba(45, 35, 24, 0.08);
}

.night_mode .prompt { color: #f0ece4; }
.night_mode .image-container img { box-shadow: 0 4px 12px rgba(0,0,0,0.4); border-color: #3a352d; }
.night_mode .answer { background: linear-gradient(135deg, #2a2620, #252218); color: #f0ece4; border-color: #3a352d; }
'''

CLASSIC_PERSON = '''
.card {
    font-family: Georgia, serif;
    font-size: 18px;
    text-align: center;
    color: #2d2318;
    background-color: #faf8f3;
    padding: 24px;
}

.card img {
    max-width: 260px;
    max-height: 260px;
    width: auto;
    height: auto;
    object-fit: contain;
    margin: 20px auto;
    display: block;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(45, 35, 24, 0.18);
    border: 1px solid #e8e0d4;
}

hr {
    border: none;
    border-top: 1px solid #e8e0d4;
    margin: 24px 60px;
}

.night_mode .card { background-color: #1c1a17; color: #d8d2c8; }
.night_mode .card img { box-shadow: 0 4px 16px rgba(0,0,0,0.5); border-color: #3a352d; }
.night_mode hr { border-top-color: #3a352d; }
'''

CLASSIC_IO = '''
.io-header {
    font-style: italic;
    font-size: 22px;
    color: #1a1410;
    text-align: center;
    margin-bottom: 20px;
}

.io-container {
    position: relative;
    display: inline-block;
    width: 100%;
    max-width: 100%;
    text-align: center;
}

.io-container img {
    max-width: 100%;
    max-height: 55vh;
    display: block;
    margin: 0 auto;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(45, 35, 24, 0.15);
    border: 1px solid #e8e0d4;
}

.io-svg-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.io-mask { fill: #d4c4a8; stroke: #b8a888; stroke-width: 2; }
.io-mask-active { fill: #c9a86c; stroke: #a88c50; stroke-width: 2; }
.io-revealed { fill: transparent; stroke: #6b8e23; stroke-width: 2; stroke-dasharray: 6,4; }

.io-answer {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 20px;
    font-weight: 600;
    color: #2d2318;
    text-align: center;
    margin: 20px 0;
    padding: 14px 24px;
    background: linear-gradient(135deg, #e8f5e9, #dcedc8);
    border-radius: 8px;
    border: 1px solid #c5e1a5;
    box-shadow: 0 2px 6px rgba(45, 35, 24, 0.08);
}

.io-cloze-data { display: none; }

.io-back-extra {
    font-size: 15px;
    color: #6b5d4d;
    font-style: italic;
    margin-top: 20px;
    text-align: center;
}

.cloze { font-weight: bold; color: #556b2f; }

.night_mode .io-header { color: #f0ece4; }
.night_mode .io-container img { box-shadow: 0 4px 12px rgba(0,0,0,0.4); border-color: #3a352d; }
.night_mode .io-mask { fill: #4a4030; stroke: #5a5040; }
.night_mode .io-mask-active { fill: #5a4830; stroke: #6a5840; }
.night_mode .io-revealed { stroke: #9acd32; }
.night_mode .io-answer { background: linear-gradient(135deg, #2a3a2a, #253525); color: #e0e0e0; border-color: #3a4a3a; }
.night_mode .io-back-extra { color: #a89880; }
.night_mode .cloze { color: #9acd32; }
'''


# =============================================================================
# HIGH CONTRAST THEME - Bold colors, strong borders, WCAG AA accessibility
# =============================================================================

HIGH_CONTRAST_BASE = '''html { overflow: scroll; overflow-x: hidden; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-size: 20px;
    color: #000000;
    background-color: #ffffff;
    margin: 0;
    padding: 24px;
    line-height: 1.6;
}

.card-header {
    font-size: 14px;
    font-weight: 700;
    color: #333333;
    text-align: left;
    margin-bottom: 20px;
    padding: 12px 16px;
    background-color: #f0f0f0;
    border-radius: 8px;
    border: 2px solid #cccccc;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.card-header p { margin: 4px 0; }

.question {
    font-weight: 800;
    color: #000000;
    font-size: 26px;
    text-align: center;
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 4px solid #0056b3;
}

.answer {
    font-size: 20px;
    font-weight: 500;
    color: #1a1a1a;
    text-align: left;
    margin-bottom: 20px;
}

.extra-info {
    font-size: 18px;
    color: #1a1a1a;
    margin-top: 20px;
    padding: 16px;
    background-color: #fff3cd;
    border-radius: 8px;
    border: 3px solid #e6c200;
}

li { margin-bottom: 1em; }

.cloze {
    font-weight: 800;
    color: #ffffff;
    background-color: #0056b3;
    padding: 4px 10px;
    border-radius: 6px;
}

/* DARK MODE - High contrast maintained */
.night_mode body {
    background-color: #000000;
    color: #ffffff;
}
.night_mode .card-header { color: #ffffff; background-color: #1a1a1a; border-color: #666666; }
.night_mode .question { color: #ffffff; border-bottom-color: #4da6ff; }
.night_mode .answer { color: #f0f0f0; }
.night_mode .extra-info { color: #000000; background-color: #ffe066; border-color: #ffcc00; }
.night_mode .cloze { color: #000000; background-color: #4da6ff; }
'''

HIGH_CONTRAST_CONCEPT_INSTRUCTION = '''
.concept-instruction {
    font-size: 14px;
    font-weight: 800;
    color: #0056b3;
    text-align: center;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.night_mode .concept-instruction { color: #4da6ff; }
'''

HIGH_CONTRAST_IMAGE = '''
.prompt {
    font-weight: 800;
    color: #000000;
    font-size: 22px;
    text-align: center;
    margin-bottom: 16px;
}

.image-container {
    text-align: center;
    margin: 16px 0;
}

.image-container img {
    max-height: 45vh;
    max-width: 100%;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 8px;
    border: 4px solid #0056b3;
}

.answer {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    text-align: center;
    margin: 20px 0;
    padding: 18px 24px;
    background-color: #0056b3;
    border-radius: 10px;
}

.night_mode .prompt { color: #ffffff; }
.night_mode .image-container img { border-color: #4da6ff; }
.night_mode .answer { background-color: #004494; }
'''

HIGH_CONTRAST_PERSON = '''
.card {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 20px;
    text-align: center;
    color: #000000;
    background-color: #ffffff;
    padding: 24px;
}

.card img {
    max-width: 280px;
    max-height: 280px;
    width: auto;
    height: auto;
    object-fit: contain;
    margin: 16px auto;
    display: block;
    border-radius: 12px;
    border: 4px solid #0056b3;
}

hr {
    border: none;
    height: 4px;
    background: linear-gradient(90deg, transparent, #0056b3, transparent);
    margin: 24px 0;
}

.night_mode .card { background-color: #000000; color: #ffffff; }
.night_mode .card img { border-color: #4da6ff; }
.night_mode hr { background: linear-gradient(90deg, transparent, #4da6ff, transparent); }
'''

HIGH_CONTRAST_IO = '''
.io-header {
    font-size: 24px;
    font-weight: 800;
    color: #000000;
    text-align: center;
    margin-bottom: 16px;
}

.io-container {
    position: relative;
    display: inline-block;
    width: 100%;
    max-width: 100%;
    text-align: center;
}

.io-container img {
    max-width: 100%;
    max-height: 55vh;
    display: block;
    margin: 0 auto;
    border-radius: 8px;
    border: 4px solid #0056b3;
}

.io-svg-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.io-mask { fill: #ff6600; stroke: #cc5200; stroke-width: 4; }
.io-mask-active { fill: #ff3300; stroke: #cc2900; stroke-width: 4; }
.io-revealed { fill: transparent; stroke: #00aa44; stroke-width: 4; stroke-dasharray: 8,4; }

.io-answer {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    text-align: center;
    margin: 16px 0;
    padding: 16px 24px;
    background-color: #00aa44;
    border-radius: 10px;
}

.io-cloze-data { display: none; }

.io-back-extra {
    font-size: 18px;
    color: #1a1a1a;
    font-weight: 600;
    margin-top: 16px;
    text-align: center;
}

.cloze { font-weight: 800; color: #00aa44; }

.night_mode .io-header { color: #ffffff; }
.night_mode .io-container img { border-color: #4da6ff; }
.night_mode .io-mask { fill: #cc5200; stroke: #993d00; }
.night_mode .io-mask-active { fill: #cc2900; stroke: #991f00; }
.night_mode .io-revealed { stroke: #00ff66; }
.night_mode .io-answer { background-color: #008833; }
.night_mode .io-back-extra { color: #e0e0e0; }
.night_mode .cloze { color: #00ff66; }
'''


# =============================================================================
# CALM THEME - Muted pastels, soft shadows, relaxed feel for long study sessions
# =============================================================================

CALM_BASE = '''html { overflow: scroll; overflow-x: hidden; }

body {
    font-family: 'Avenir Next', 'Segoe UI', -apple-system, sans-serif;
    font-size: 17px;
    color: #4a5568;
    background-color: #f7f8fc;
    margin: 0;
    padding: 20px;
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
}

.card-header {
    font-size: 13px;
    color: #a0aec0;
    text-align: left;
    margin-bottom: 14px;
}

.card-header p { margin: 2px 0; }

.question {
    font-weight: 500;
    color: #2d3748;
    font-size: 19px;
    text-align: center;
    margin-bottom: 18px;
    padding: 18px 20px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.answer {
    font-size: 17px;
    color: #4a5568;
    text-align: left;
    margin-bottom: 14px;
    padding: 18px 20px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.extra-info {
    font-size: 15px;
    color: #a0aec0;
    margin-top: 14px;
    padding: 14px 18px;
    background-color: #edf2f7;
    border-radius: 10px;
}

li { margin-bottom: 0.6em; }

.cloze {
    font-weight: 600;
    color: #667eea;
}

/* DARK MODE */
.night_mode body {
    background-color: #1a202c;
    color: #e2e8f0;
}
.night_mode .card-header { color: #718096; }
.night_mode .question { color: #f7fafc; background-color: #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.night_mode .answer { color: #e2e8f0; background-color: #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.night_mode .extra-info { color: #a0aec0; background-color: #2d3748; }
.night_mode .cloze { color: #a3bffa; }
'''

CALM_CONCEPT_INSTRUCTION = '''
.concept-instruction {
    font-size: 12px;
    color: #a0aec0;
    text-align: center;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 500;
}
.night_mode .concept-instruction { color: #718096; }
'''

CALM_IMAGE = '''
.prompt {
    font-weight: 500;
    color: #2d3748;
    font-size: 17px;
    text-align: center;
    margin-bottom: 14px;
    padding: 14px 18px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.image-container {
    text-align: center;
    margin: 14px 0;
}

.image-container img {
    max-height: 45vh;
    max-width: 100%;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.answer {
    font-size: 19px;
    font-weight: 500;
    color: #2d3748;
    text-align: center;
    margin: 14px 0;
    padding: 18px 20px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.night_mode .prompt { color: #f7fafc; background-color: #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.night_mode .answer { color: #f7fafc; background-color: #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
'''

CALM_PERSON = '''
.card {
    font-family: 'Avenir Next', 'Segoe UI', -apple-system, sans-serif;
    font-size: 17px;
    text-align: center;
    color: #4a5568;
    background-color: #f7f8fc;
    padding: 20px;
    line-height: 1.65;
}

.card img {
    max-width: 260px;
    max-height: 260px;
    width: auto;
    height: auto;
    object-fit: contain;
    margin: 14px auto;
    display: block;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #cbd5e0, transparent);
    margin: 18px 0;
}

.night_mode .card { background-color: #1a202c; color: #e2e8f0; }
.night_mode hr { background: linear-gradient(90deg, transparent, #4a5568, transparent); }
'''

CALM_IO = '''
.io-header {
    font-size: 17px;
    font-weight: 500;
    color: #2d3748;
    text-align: center;
    margin-bottom: 14px;
    padding: 14px 18px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.io-container {
    position: relative;
    display: inline-block;
    width: 100%;
    max-width: 100%;
    text-align: center;
}

.io-container img {
    max-width: 100%;
    max-height: 55vh;
    display: block;
    margin: 0 auto;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.io-svg-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.io-mask { fill: #b794f4; stroke: #9f7aea; stroke-width: 2; }
.io-mask-active { fill: #9f7aea; stroke: #805ad5; stroke-width: 2; }
.io-revealed { fill: transparent; stroke: #68d391; stroke-width: 2; stroke-dasharray: 4,2; }

.io-answer {
    font-size: 19px;
    font-weight: 500;
    color: #2d3748;
    text-align: center;
    margin: 14px 0;
    padding: 18px 20px;
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.io-cloze-data { display: none; }

.io-back-extra {
    font-size: 15px;
    color: #a0aec0;
    margin-top: 14px;
    text-align: center;
}

.cloze { font-weight: 600; color: #667eea; }

.night_mode .io-header { color: #f7fafc; background-color: #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.night_mode .io-mask { fill: #9f7aea; stroke: #805ad5; }
.night_mode .io-mask-active { fill: #805ad5; stroke: #6b46c1; }
.night_mode .io-revealed { stroke: #68d391; }
.night_mode .io-answer { color: #f7fafc; background-color: #2d3748; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
.night_mode .io-back-extra { color: #a0aec0; }
.night_mode .cloze { color: #a3bffa; }
'''


# =============================================================================
# THEME CSS GETTERS
# =============================================================================

def get_front_back_css(theme: str = 'minimal') -> str:
    """Get CSS for Front-Back cards."""
    if theme == 'classic':
        return CLASSIC_BASE
    elif theme == 'high-contrast':
        return HIGH_CONTRAST_BASE
    elif theme == 'calm':
        return CALM_BASE
    return MINIMAL_BASE


def get_concept_css(theme: str = 'minimal') -> str:
    """Get CSS for Concept (Bidirectional) cards."""
    if theme == 'classic':
        return CLASSIC_BASE + CLASSIC_CONCEPT_INSTRUCTION
    elif theme == 'high-contrast':
        return HIGH_CONTRAST_BASE + HIGH_CONTRAST_CONCEPT_INSTRUCTION
    elif theme == 'calm':
        return CALM_BASE + CALM_CONCEPT_INSTRUCTION
    return MINIMAL_BASE + MINIMAL_CONCEPT_INSTRUCTION


def get_cloze_css(theme: str = 'minimal') -> str:
    """Get CSS for Cloze cards."""
    if theme == 'classic':
        return CLASSIC_BASE
    elif theme == 'high-contrast':
        return HIGH_CONTRAST_BASE
    elif theme == 'calm':
        return CALM_BASE
    return MINIMAL_BASE


def get_image_css(theme: str = 'minimal') -> str:
    """Get CSS for Image Recognition cards."""
    base = get_front_back_css(theme)
    if theme == 'classic':
        return base + CLASSIC_IMAGE
    elif theme == 'high-contrast':
        return base + HIGH_CONTRAST_IMAGE
    elif theme == 'calm':
        return base + CALM_IMAGE
    return base + MINIMAL_IMAGE


def get_person_css(theme: str = 'minimal') -> str:
    """Get CSS for Person cards."""
    if theme == 'classic':
        return CLASSIC_PERSON
    elif theme == 'high-contrast':
        return HIGH_CONTRAST_PERSON
    elif theme == 'calm':
        return CALM_PERSON
    return MINIMAL_PERSON


def get_image_occlusion_css(theme: str = 'minimal') -> str:
    """Get CSS for Image Occlusion cards."""
    base = 'html { overflow: scroll; overflow-x: hidden; }\n'
    if theme == 'classic':
        return CLASSIC_BASE + CLASSIC_IO
    elif theme == 'high-contrast':
        return HIGH_CONTRAST_BASE + HIGH_CONTRAST_IO
    elif theme == 'calm':
        return CALM_BASE + CALM_IO
    return MINIMAL_BASE + MINIMAL_IO


def get_theme_sections(theme: str = 'minimal') -> dict:
    """Get the base and per-card CSS sections for a theme."""
    if theme == 'classic':
        return {
            "base": CLASSIC_BASE,
            "conceptInstruction": CLASSIC_CONCEPT_INSTRUCTION,
            "image": CLASSIC_IMAGE,
            "person": CLASSIC_PERSON,
            "io": CLASSIC_IO,
        }
    if theme == 'high-contrast':
        return {
            "base": HIGH_CONTRAST_BASE,
            "conceptInstruction": HIGH_CONTRAST_CONCEPT_INSTRUCTION,
            "image": HIGH_CONTRAST_IMAGE,
            "person": HIGH_CONTRAST_PERSON,
            "io": HIGH_CONTRAST_IO,
        }
    if theme == 'calm':
        return {
            "base": CALM_BASE,
            "conceptInstruction": CALM_CONCEPT_INSTRUCTION,
            "image": CALM_IMAGE,
            "person": CALM_PERSON,
            "io": CALM_IO,
        }
    return {
        "base": MINIMAL_BASE,
        "conceptInstruction": MINIMAL_CONCEPT_INSTRUCTION,
        "image": MINIMAL_IMAGE,
        "person": MINIMAL_PERSON,
        "io": MINIMAL_IO,
    }
