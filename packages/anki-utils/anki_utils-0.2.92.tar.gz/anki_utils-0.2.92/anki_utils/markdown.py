"""
Markdown to HTML conversion for Anki cards.

This module handles converting markdown-style formatting to HTML
that renders correctly in Anki's card templates.
"""

from typing import Optional

import re


def markdown_to_html(text: Optional[str]) -> str:
    """
    Convert markdown-style formatting to HTML for Anki cards.

    Handles:
    - **bold** and __bold__ → <strong>bold</strong>
    - *italic* and _italic_ → <em>italic</em>
    - `code` → <code>code</code>
    - ```code blocks``` → <pre><code>code</code></pre>
    - Bullet lists (-, *, •) → <ul><li>...</li></ul>
    - Numbered lists (1., 2.) → <ol><li>...</li></ol>
    - Line breaks → <br>
    - Paragraphs (double newline) → <p>...</p>
    - [text](url) → <a href="url">text</a>
    - Cloze syntax {{c1::...}} is preserved
    """
    if not text or not isinstance(text, str):
        return text or ''

    # Preserve cloze deletions by temporarily replacing them
    cloze_placeholders = {}
    cloze_pattern = r'\{\{c\d+::.*?\}\}'

    def save_cloze(match):
        placeholder = f"CLOZEPLACEHOLDER{len(cloze_placeholders)}ENDCLOZE"
        cloze_placeholders[placeholder] = match.group(0)
        return placeholder

    text = re.sub(cloze_pattern, save_cloze, text)

    # Handle code blocks first (before other processing)
    def convert_code_block(match):
        code = match.group(1).strip()
        # Escape HTML in code blocks
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code>{code}</code></pre>'

    text = re.sub(r'```(?:\w+)?\n?(.*?)```', convert_code_block, text, flags=re.DOTALL)

    # Handle inline code (preserve content, escape HTML)
    def convert_inline_code(match):
        code = match.group(1)
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<code>{code}</code>'

    text = re.sub(r'`([^`]+)`', convert_inline_code, text)

    # Convert links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # Convert bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Convert italic (*text* or _text_) - be careful not to match inside words
    text = re.sub(r'(?<!\w)\*(?!\*)(.+?)(?<!\*)\*(?!\w)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_(?!_)(.+?)(?<!_)_(?!\w)', r'<em>\1</em>', text)

    # Process lists and paragraphs by splitting into lines
    lines = text.split('\n')
    result_lines = []
    in_ul = False
    in_ol = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for bullet list item
        bullet_match = re.match(r'^[-*•]\s+(.+)$', stripped)
        # Check for numbered list item
        numbered_match = re.match(r'^(\d+)[.)]\s+(.+)$', stripped)

        if bullet_match:
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            if not in_ul:
                result_lines.append('<ul>')
                in_ul = True
            result_lines.append(f'<li>{bullet_match.group(1)}</li>')
        elif numbered_match:
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if not in_ol:
                result_lines.append('<ol>')
                in_ol = True
            result_lines.append(f'<li>{numbered_match.group(2)}</li>')
        else:
            # Close any open lists
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False

            # Add the line (non-list content)
            if stripped:
                result_lines.append(stripped)
            elif result_lines and result_lines[-1] not in ('</ul>', '</ol>', '<br>'):
                # Empty line between content becomes a break
                result_lines.append('<br>')

    # Close any remaining open lists
    if in_ul:
        result_lines.append('</ul>')
    if in_ol:
        result_lines.append('</ol>')

    # Join lines with <br> for single newlines within non-list content
    # But avoid double breaks
    html = ''
    for i, line in enumerate(result_lines):
        if line.startswith('<ul>') or line.startswith('<ol>') or line.startswith('</ul>') or line.startswith('</ol>') or line.startswith('<li>') or line.startswith('<pre>'):
            html += line
        elif line == '<br>':
            html += '<br>'
        else:
            if html and not html.endswith('>'):
                html += '<br>'
            html += line

    # Clean up multiple consecutive <br> tags
    html = re.sub(r'(<br>\s*){2,}', '<br><br>', html)

    # Restore cloze deletions
    for placeholder, cloze in cloze_placeholders.items():
        html = html.replace(placeholder, cloze)

    return html


def convert_card_fields(card_data: dict) -> dict:
    """
    Convert all text fields in a card from markdown to HTML.
    Returns a new dict with converted fields.
    """
    converted = card_data.copy()

    # Fields that should be converted (all text content fields)
    text_fields = [
        'question', 'answer',           # front-back
        'concept', 'definition',        # concept
        'cloze_text',                   # cloze
        'prompt',                       # image
        'example', 'extra_info',        # shared optional fields
        # Person fields (most are simple text, but convert just in case)
        'hobbies', 'children_names', 'pet_names', 'direct_reports',
    ]

    for field in text_fields:
        if field in converted and converted[field]:
            converted[field] = markdown_to_html(converted[field])

    return converted
