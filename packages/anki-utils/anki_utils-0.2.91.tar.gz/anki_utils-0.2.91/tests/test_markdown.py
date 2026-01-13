"""Tests for markdown_to_html conversion."""

import pytest
from anki_utils.markdown import markdown_to_html


class TestMarkdownToHtml:
    """Tests for the markdown_to_html function."""

    # Basic formatting tests
    def test_bold_double_asterisk(self):
        """Test **bold** conversion."""
        result = markdown_to_html("This is **bold** text")
        assert "<strong>bold</strong>" in result

    def test_bold_double_underscore(self):
        """Test __bold__ conversion."""
        result = markdown_to_html("This is __bold__ text")
        assert "<strong>bold</strong>" in result

    def test_italic_single_asterisk(self):
        """Test *italic* conversion."""
        result = markdown_to_html("This is *italic* text")
        assert "<em>italic</em>" in result

    def test_italic_single_underscore(self):
        """Test _italic_ conversion."""
        result = markdown_to_html("This is _italic_ text")
        assert "<em>italic</em>" in result

    def test_inline_code(self):
        """Test `code` conversion."""
        result = markdown_to_html("Use the `print()` function")
        assert "<code>print()</code>" in result

    def test_inline_code_escapes_html(self):
        """Test that HTML in inline code is escaped."""
        result = markdown_to_html("Use `<div>` tags")
        assert "&lt;div&gt;" in result
        assert "<div>" not in result

    # Code block tests
    def test_code_block(self):
        """Test triple backtick code block conversion."""
        text = "```\nprint('hello')\n```"
        result = markdown_to_html(text)
        assert "<pre><code>" in result
        assert "</code></pre>" in result

    def test_code_block_with_language(self):
        """Test code block with language specifier."""
        text = "```python\nprint('hello')\n```"
        result = markdown_to_html(text)
        assert "<pre><code>" in result

    def test_code_block_escapes_html(self):
        """Test that HTML in code blocks is escaped."""
        text = "```\n<script>alert('xss')</script>\n```"
        result = markdown_to_html(text)
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    # Link tests
    def test_link_conversion(self):
        """Test [text](url) link conversion."""
        result = markdown_to_html("Visit [Google](https://google.com)")
        assert '<a href="https://google.com">Google</a>' in result

    # List tests
    def test_bullet_list_dash(self):
        """Test bullet list with dash."""
        text = "- Item 1\n- Item 2"
        result = markdown_to_html(text)
        assert "<ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "</ul>" in result

    def test_bullet_list_asterisk(self):
        """Test bullet list with asterisk."""
        text = "* Item 1\n* Item 2"
        result = markdown_to_html(text)
        assert "<ul>" in result
        assert "<li>" in result

    def test_numbered_list(self):
        """Test numbered list conversion."""
        text = "1. First\n2. Second"
        result = markdown_to_html(text)
        assert "<ol>" in result
        assert "<li>First</li>" in result
        assert "<li>Second</li>" in result
        assert "</ol>" in result

    # Cloze preservation tests
    def test_cloze_single_preserved(self):
        """Test that single cloze deletion is preserved."""
        text = "The {{c1::answer}} is here"
        result = markdown_to_html(text)
        assert "{{c1::answer}}" in result

    def test_cloze_multiple_preserved(self):
        """Test that multiple cloze deletions are preserved."""
        text = "{{c1::First}} and {{c2::second}}"
        result = markdown_to_html(text)
        assert "{{c1::First}}" in result
        assert "{{c2::second}}" in result

    def test_cloze_with_formatting(self):
        """Test cloze with surrounding formatting."""
        text = "The **{{c1::bold answer}}** is correct"
        result = markdown_to_html(text)
        assert "{{c1::bold answer}}" in result

    # Edge cases
    def test_empty_string(self):
        """Test empty string input."""
        result = markdown_to_html("")
        assert result == ""

    def test_none_input(self):
        """Test None input."""
        result = markdown_to_html(None)
        assert result == ""

    def test_plain_text(self):
        """Test plain text without formatting."""
        text = "Just plain text"
        result = markdown_to_html(text)
        assert "Just plain text" in result

    def test_mixed_formatting(self):
        """Test multiple formatting types together."""
        text = "**Bold** and *italic* with `code`"
        result = markdown_to_html(text)
        assert "<strong>Bold</strong>" in result
        assert "<em>italic</em>" in result
        assert "<code>code</code>" in result

    def test_consecutive_line_breaks(self):
        """Test that consecutive breaks are handled."""
        text = "Line 1\n\n\nLine 2"
        result = markdown_to_html(text)
        # Should not have more than double breaks
        assert "<br><br><br>" not in result
