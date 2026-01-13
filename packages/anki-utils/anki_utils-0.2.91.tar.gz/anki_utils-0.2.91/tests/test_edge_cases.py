"""Tests for edge case test data validation and export."""

import json
import os
import sqlite3
import zipfile
from pathlib import Path

import pytest
from anki_utils.exporter import create_package, validate_data, ValidationError


# Path to edge cases test data
EDGE_CASES_PATH = Path(__file__).resolve().parents[1] / "assets/test-data/test-cards-edge-cases.json"
GOLDEN_APKG_PATH = Path(__file__).resolve().parents[1] / "assets/test-data/test-cards-edge-cases.apkg"


@pytest.fixture
def edge_cases_data():
    """Load the edge cases test data."""
    with open(EDGE_CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def edge_cases_cards(edge_cases_data):
    """Get just the cards array from edge cases data."""
    return edge_cases_data.get("cards", [])


class TestEdgeCasesValidation:
    """Tests that all edge case cards pass validation."""

    def test_edge_cases_file_exists(self):
        """Edge cases test data file should exist."""
        assert EDGE_CASES_PATH.exists(), f"Missing edge cases file: {EDGE_CASES_PATH}"

    def test_golden_apkg_exists(self):
        """Golden .apkg snapshot should exist for regression testing."""
        assert GOLDEN_APKG_PATH.exists(), f"Missing golden .apkg: {GOLDEN_APKG_PATH}"

    def test_all_edge_cases_pass_validation(self, edge_cases_data):
        """All edge case cards should pass validation."""
        # Should not raise ValidationError
        validate_data(edge_cases_data)

    def test_edge_cases_have_expected_card_count(self, edge_cases_cards):
        """Edge cases should have expected number of cards."""
        # Should have at least 20 cards covering various edge cases
        assert len(edge_cases_cards) >= 20, f"Expected at least 20 edge case cards, got {len(edge_cases_cards)}"

    def test_all_card_types_represented(self, edge_cases_cards):
        """Edge cases should include all card types."""
        card_types = {card.get("type") for card in edge_cases_cards}
        expected_types = {"front-back", "concept", "cloze", "person", "image-occlusion"}
        missing = expected_types - card_types
        assert not missing, f"Missing card types in edge cases: {missing}"


class TestFormattingEdgeCases:
    """Tests for markdown/formatting edge cases."""

    def test_bullet_list_card_exists(self, edge_cases_cards):
        """Should have a card with bullet lists."""
        bullet_cards = [c for c in edge_cases_cards if "bullet-list" in c.get("tags", [])]
        assert bullet_cards, "Missing bullet list edge case card"
        # Verify it contains list markers
        answer = bullet_cards[0].get("answer", "")
        assert "-" in answer or "*" in answer, "Bullet list card should contain list markers"

    def test_numbered_list_card_exists(self, edge_cases_cards):
        """Should have a card with numbered lists."""
        numbered_cards = [c for c in edge_cases_cards if "numbered-list" in c.get("tags", [])]
        assert numbered_cards, "Missing numbered list edge case card"
        answer = numbered_cards[0].get("answer", "")
        assert "1." in answer or "1)" in answer, "Numbered list card should contain numbered items"

    def test_nested_list_card_exists(self, edge_cases_cards):
        """Should have a card with nested lists."""
        nested_cards = [c for c in edge_cases_cards if "nested-list" in c.get("tags", [])]
        assert nested_cards, "Missing nested list edge case card"

    def test_bold_italic_card_exists(self, edge_cases_cards):
        """Should have a card with bold and italic formatting."""
        format_cards = [c for c in edge_cases_cards if "bold-italic" in c.get("tags", [])]
        assert format_cards, "Missing bold/italic edge case card"
        answer = format_cards[0].get("answer", "")
        assert "**" in answer or "__" in answer, "Should contain bold markers"
        assert "*" in answer or "_" in answer, "Should contain italic markers"

    def test_code_block_card_exists(self, edge_cases_cards):
        """Should have a card with code blocks."""
        code_cards = [c for c in edge_cases_cards if "code-block" in c.get("tags", [])]
        assert code_cards, "Missing code block edge case card"
        answer = code_cards[0].get("answer", "")
        assert "```" in answer, "Code block card should contain fenced code block"

    def test_links_card_exists(self, edge_cases_cards):
        """Should have a card with links."""
        link_cards = [c for c in edge_cases_cards if "links" in c.get("tags", [])]
        assert link_cards, "Missing links edge case card"
        answer = link_cards[0].get("answer", "")
        assert "](http" in answer or "](https" in answer, "Links card should contain markdown links"

    def test_mixed_formatting_card_exists(self, edge_cases_cards):
        """Should have a card with mixed formatting."""
        mixed_cards = [c for c in edge_cases_cards if "mixed-formatting" in c.get("tags", [])]
        assert mixed_cards, "Missing mixed formatting edge case card"


class TestUnicodeEdgeCases:
    """Tests for Unicode edge cases."""

    def test_emoji_card_exists(self, edge_cases_cards):
        """Should have a card with emoji content."""
        emoji_cards = [c for c in edge_cases_cards if "emoji" in c.get("tags", [])]
        assert emoji_cards, "Missing emoji edge case card"

    def test_cjk_card_exists(self, edge_cases_cards):
        """Should have a card with CJK characters."""
        cjk_cards = [c for c in edge_cases_cards if "cjk" in c.get("tags", []) or "japanese" in c.get("tags", [])]
        assert cjk_cards, "Missing CJK edge case card"

    def test_rtl_card_exists(self, edge_cases_cards):
        """Should have a card with RTL text."""
        rtl_cards = [c for c in edge_cases_cards if "rtl" in c.get("tags", []) or "arabic" in c.get("tags", [])]
        assert rtl_cards, "Missing RTL edge case card"

    def test_special_chars_card_exists(self, edge_cases_cards):
        """Should have a card testing HTML escaping characters."""
        special_cards = [c for c in edge_cases_cards if "html-escaping" in c.get("tags", []) or "special-chars" in c.get("tags", [])]
        assert special_cards, "Missing special characters edge case card"


class TestMinimalValidCards:
    """Tests for minimal valid cards."""

    def test_minimal_front_back_exists(self, edge_cases_cards):
        """Should have a minimal front-back card."""
        minimal_fb = [c for c in edge_cases_cards
                      if c.get("type") == "front-back" and "minimal" in c.get("tags", [])]
        assert minimal_fb, "Missing minimal front-back card"

    def test_minimal_concept_exists(self, edge_cases_cards):
        """Should have a minimal concept card."""
        minimal_concept = [c for c in edge_cases_cards
                          if c.get("type") == "concept" and "minimal" in c.get("tags", [])]
        assert minimal_concept, "Missing minimal concept card"

    def test_minimal_cloze_exists(self, edge_cases_cards):
        """Should have a minimal cloze card."""
        minimal_cloze = [c for c in edge_cases_cards
                        if c.get("type") == "cloze" and "minimal" in c.get("tags", [])]
        assert minimal_cloze, "Missing minimal cloze card"

    def test_minimal_person_exists(self, edge_cases_cards):
        """Should have a minimal person card."""
        minimal_person = [c for c in edge_cases_cards
                         if c.get("type") == "person" and "minimal" in c.get("tags", [])]
        assert minimal_person, "Missing minimal person card"


class TestCardTypeSpecifics:
    """Tests for card type specific edge cases."""

    def test_person_with_all_fields_exists(self, edge_cases_cards):
        """Should have a person card with all 12 optional fields populated."""
        all_fields_person = [c for c in edge_cases_cards
                            if c.get("type") == "person" and "all-fields" in c.get("tags", [])]
        assert all_fields_person, "Missing person card with all fields"

        person = all_fields_person[0]
        # Check all 12 optional fields + required full_name
        expected_fields = [
            "full_name", "photo_path", "birthday", "current_city", "phone_number",
            "partner_name", "children_names", "pet_names", "hobbies",
            "title", "reports_to", "direct_reports", "company"
        ]
        for field in expected_fields:
            assert field in person, f"Person card missing field: {field}"

    def test_image_occlusion_many_regions_exists(self, edge_cases_cards):
        """Should have an image-occlusion card with 5+ regions."""
        io_cards = [c for c in edge_cases_cards
                   if c.get("type") == "image-occlusion" and "many-regions" in c.get("tags", [])]
        assert io_cards, "Missing image-occlusion card with many regions"

        io_card = io_cards[0]
        occlusions = io_card.get("occlusions", [])
        assert len(occlusions) >= 5, f"Expected 5+ occlusion regions, got {len(occlusions)}"

    def test_cloze_with_hints_exists(self, edge_cases_cards):
        """Should have a cloze card with hint syntax."""
        hint_cloze = [c for c in edge_cases_cards
                     if c.get("type") == "cloze" and "hints" in c.get("tags", [])]
        assert hint_cloze, "Missing cloze card with hints"

        cloze_text = hint_cloze[0].get("cloze_text", "")
        assert "::" in cloze_text and "hint" in cloze_text.lower(), "Cloze should contain hint syntax"

    def test_cloze_with_same_number_exists(self, edge_cases_cards):
        """Should have a cloze card with same cloze number used multiple times."""
        same_num_cloze = [c for c in edge_cases_cards
                         if c.get("type") == "cloze" and "same-number" in c.get("tags", [])]
        assert same_num_cloze, "Missing cloze card with same-number duplicates"

    def test_cloze_with_mixed_numbers_exists(self, edge_cases_cards):
        """Should have a cloze card with non-sequential cloze numbers."""
        mixed_cloze = [c for c in edge_cases_cards
                      if c.get("type") == "cloze" and "mixed-numbers" in c.get("tags", [])]
        assert mixed_cloze, "Missing cloze card with mixed numbers"


class TestEdgeCasesExport:
    """Tests for exporting edge cases to .apkg."""

    def test_edge_cases_export_succeeds(self, temp_dir, edge_cases_data):
        """All edge cases should export to .apkg successfully."""
        output_path = os.path.join(temp_dir, "edge-cases-test.apkg")
        repo_root = Path(__file__).resolve().parents[1]

        result = create_package(edge_cases_data, output_path, base_path=str(repo_root))

        assert os.path.exists(output_path)
        assert result["total_notes"] >= 20

    def test_edge_cases_export_card_counts(self, temp_dir, edge_cases_data):
        """Edge cases export should have expected card type counts."""
        output_path = os.path.join(temp_dir, "edge-cases-counts.apkg")
        repo_root = Path(__file__).resolve().parents[1]

        result = create_package(edge_cases_data, output_path, base_path=str(repo_root))

        # Should have cards of each type
        assert result["front_back_count"] >= 10, "Should have multiple front-back cards"
        assert result["concept_count"] >= 1, "Should have at least 1 concept card"
        assert result["cloze_count"] >= 3, "Should have multiple cloze cards"
        assert result["person_count"] >= 2, "Should have at least 2 person cards"
        assert result["image_occlusion_count"] >= 1, "Should have at least 1 image-occlusion card"

    def test_edge_cases_export_includes_media(self, temp_dir, edge_cases_data):
        """Edge cases export should include media files."""
        output_path = os.path.join(temp_dir, "edge-cases-media.apkg")
        repo_root = Path(__file__).resolve().parents[1]

        result = create_package(edge_cases_data, output_path, base_path=str(repo_root))

        # Person and image-occlusion cards reference media files
        assert result["media_files_included"] >= 1, "Should include media files"

    def test_golden_apkg_is_valid_zip(self):
        """Golden .apkg should be a valid ZIP file."""
        assert zipfile.is_zipfile(GOLDEN_APKG_PATH), "Golden .apkg is not a valid ZIP"

        with zipfile.ZipFile(GOLDEN_APKG_PATH) as zf:
            names = zf.namelist()
            # Should contain Anki collection database
            has_collection = "collection.anki21" in names or "collection.anki2" in names
            assert has_collection, "Golden .apkg missing collection database"
            assert "media" in names, "Golden .apkg missing media manifest"

    def test_golden_apkg_has_expected_notes(self):
        """Golden .apkg should contain expected number of notes."""
        import tempfile

        with zipfile.ZipFile(GOLDEN_APKG_PATH) as zf:
            names = zf.namelist()
            collection_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            collection_bytes = zf.read(collection_name)

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp.write(collection_bytes)
            tmp_path = tmp.name

        try:
            conn = sqlite3.connect(tmp_path)
            note_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            conn.close()
        finally:
            os.unlink(tmp_path)

        # Should have at least 20 notes
        assert note_count >= 20, f"Golden .apkg has only {note_count} notes, expected 20+"


class TestMarkdownConversionInEdgeCases:
    """Tests that markdown formatting survives conversion."""

    def test_bullet_list_converts_to_html(self, edge_cases_cards):
        """Bullet lists should convert to HTML ul/li elements."""
        from anki_utils.exporter import convert_card_fields

        bullet_cards = [c for c in edge_cases_cards if "bullet-list" in c.get("tags", [])]
        assert bullet_cards

        converted = convert_card_fields(bullet_cards[0])
        answer = converted.get("answer", "")

        assert "<ul>" in answer or "<li>" in answer, "Bullet list should convert to HTML list"

    def test_numbered_list_converts_to_html(self, edge_cases_cards):
        """Numbered lists should convert to HTML ol elements."""
        from anki_utils.exporter import convert_card_fields

        numbered_cards = [c for c in edge_cases_cards if "numbered-list" in c.get("tags", [])]
        assert numbered_cards

        converted = convert_card_fields(numbered_cards[0])
        answer = converted.get("answer", "")

        assert "<ol>" in answer or "<li>" in answer, "Numbered list should convert to HTML list"

    def test_code_block_converts_to_html(self, edge_cases_cards):
        """Code blocks should convert to HTML pre/code elements."""
        from anki_utils.exporter import convert_card_fields

        code_cards = [c for c in edge_cases_cards if "code-block" in c.get("tags", [])]
        assert code_cards

        converted = convert_card_fields(code_cards[0])
        answer = converted.get("answer", "")

        assert "<pre>" in answer or "<code>" in answer, "Code block should convert to HTML code element"

    def test_bold_converts_to_html(self, edge_cases_cards):
        """Bold text should convert to HTML strong element."""
        from anki_utils.exporter import convert_card_fields

        format_cards = [c for c in edge_cases_cards if "bold-italic" in c.get("tags", [])]
        assert format_cards

        converted = convert_card_fields(format_cards[0])
        answer = converted.get("answer", "")

        assert "<strong>" in answer or "<b>" in answer, "Bold should convert to HTML"

    def test_italic_converts_to_html(self, edge_cases_cards):
        """Italic text should convert to HTML em element."""
        from anki_utils.exporter import convert_card_fields

        format_cards = [c for c in edge_cases_cards if "bold-italic" in c.get("tags", [])]
        assert format_cards

        converted = convert_card_fields(format_cards[0])
        answer = converted.get("answer", "")

        assert "<em>" in answer or "<i>" in answer, "Italic should convert to HTML"

    def test_links_convert_to_html(self, edge_cases_cards):
        """Links should convert to HTML anchor elements."""
        from anki_utils.exporter import convert_card_fields

        link_cards = [c for c in edge_cases_cards if "links" in c.get("tags", [])]
        assert link_cards

        converted = convert_card_fields(link_cards[0])
        answer = converted.get("answer", "")

        assert "<a href=" in answer, "Links should convert to HTML anchors"
