"""End-to-end tests for the complete export flow.

These tests verify the full journey from JSON input to valid .apkg file,
including database structure, media packaging, and content preservation.
"""

import json
import os
import sqlite3
import zipfile
from pathlib import Path

import pytest
from anki_utils.exporter import create_package


# Path to test data relative to repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_DATA_DIR = REPO_ROOT / "assets" / "test-data"
TEST_CARDS_JSON = TEST_DATA_DIR / "test-cards.json"


def load_test_cards() -> dict:
    """Load the comprehensive test cards JSON."""
    with TEST_CARDS_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_apkg(apkg_path: str, extract_dir: str) -> tuple[str, dict]:
    """Extract .apkg and return (collection_path, media_map).

    An .apkg file is a ZIP containing:
    - collection.anki21 or collection.anki2 (SQLite database)
    - media (JSON mapping of numeric keys to filenames)
    - Numbered media files (0, 1, 2, etc.)
    """
    with zipfile.ZipFile(apkg_path) as zf:
        zf.extractall(extract_dir)
        names = zf.namelist()

    # Find collection file
    collection_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
    collection_path = os.path.join(extract_dir, collection_name)

    # Load media manifest
    media_path = os.path.join(extract_dir, "media")
    if os.path.exists(media_path):
        with open(media_path, "r", encoding="utf-8") as f:
            media_map = json.load(f)
    else:
        media_map = {}

    return collection_path, media_map


class TestE2EAllCardTypes:
    """End-to-end tests for all 6 card types."""

    def test_e2e_export_all_card_types(self, temp_dir):
        """Export a deck with all 6 card types and verify it's valid."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "all_types.apkg")

        result = create_package(data, output_path, base_path=str(REPO_ROOT))

        # Verify file was created
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

        # Verify all card types were counted
        assert result["front_back_count"] >= 1
        assert result["concept_count"] >= 1
        assert result["cloze_count"] >= 1
        assert result["image_count"] >= 1
        assert result["person_count"] >= 1
        assert result["image_occlusion_count"] >= 1

        # Verify totals make sense
        total_notes = (
            result["front_back_count"] +
            result["concept_count"] +
            result["cloze_count"] +
            result["image_count"] +
            result["person_count"] +
            result["image_occlusion_count"]
        )
        assert result["total_notes"] == total_notes

        # Cards should be more than notes due to bidirectional concepts, cloze deletions, etc.
        assert result["total_cards"] >= result["total_notes"]

    def test_e2e_apkg_is_valid_zip(self, temp_dir):
        """The .apkg file should be a valid ZIP archive."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path, base_path=str(REPO_ROOT))

        # Verify it's a valid ZIP
        assert zipfile.is_zipfile(output_path)

        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()

            # Must contain collection database
            has_collection = "collection.anki21" in names or "collection.anki2" in names
            assert has_collection, f"Missing collection file. Found: {names}"

            # Must contain media manifest
            assert "media" in names, f"Missing media manifest. Found: {names}"


class TestE2EDatabaseStructure:
    """Verify the SQLite database structure inside the .apkg."""

    def test_e2e_database_has_notes_table(self, temp_dir):
        """The collection database should have a notes table with correct count."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "test.apkg")

        result = create_package(data, output_path, base_path=str(REPO_ROOT))
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            # Notes table should exist
            cursor = conn.execute("SELECT count(*) FROM notes")
            note_count = cursor.fetchone()[0]

            assert note_count == result["total_notes"], (
                f"Expected {result['total_notes']} notes, found {note_count}"
            )
        finally:
            conn.close()

    def test_e2e_database_has_cards_table(self, temp_dir):
        """The collection database should have a cards table."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "test.apkg")

        result = create_package(data, output_path, base_path=str(REPO_ROOT))
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            # Cards table should exist and have cards
            cursor = conn.execute("SELECT count(*) FROM cards")
            card_count = cursor.fetchone()[0]

            # Total cards accounts for multi-card notes (concept=2, cloze=N, person=N, IO=N)
            assert card_count == result["total_cards"], (
                f"Expected {result['total_cards']} cards, found {card_count}"
            )
        finally:
            conn.close()

    def test_e2e_database_notes_have_fields(self, temp_dir):
        """Each note should have non-empty fields."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path, base_path=str(REPO_ROOT))
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            cursor = conn.execute("SELECT flds FROM notes")
            notes = cursor.fetchall()

            # Each note should have some field content
            for i, (flds,) in enumerate(notes):
                # Fields are separated by \x1f (unit separator)
                fields = flds.split("\x1f")

                # At least one field should be non-empty
                non_empty = [f for f in fields if f.strip()]
                assert len(non_empty) > 0, f"Note {i} has no non-empty fields"
        finally:
            conn.close()


class TestE2EMediaPackaging:
    """Verify media files are correctly packaged."""

    def test_e2e_media_manifest_exists(self, temp_dir):
        """The media manifest should list all included media files."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "test.apkg")

        result = create_package(data, output_path, base_path=str(REPO_ROOT))
        collection_path, media_map = extract_apkg(output_path, temp_dir)

        # Should have media files for image and person cards
        assert len(media_map) == result["media_files_included"], (
            f"Expected {result['media_files_included']} media files, found {len(media_map)}"
        )

    def test_e2e_media_files_included_in_archive(self, temp_dir):
        """All media files listed in manifest should exist in the archive."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path, base_path=str(REPO_ROOT))

        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()
            media_manifest = json.loads(zf.read("media").decode("utf-8"))

            # Each key in the media manifest should have a corresponding file
            for key in media_manifest.keys():
                assert key in names, f"Media file {key} listed but not in archive"

    def test_e2e_media_files_have_correct_names(self, temp_dir):
        """Media manifest should map to recognizable filenames."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path, base_path=str(REPO_ROOT))
        collection_path, media_map = extract_apkg(output_path, temp_dir)

        # The test-cards.json includes these image files
        expected_filenames = {
            "statue-of-liberty.png",  # image card
            "sample-person.png",      # person card
            "heart-anatomy.jpg",      # image-occlusion (embedded as base64, but file still included)
        }

        actual_filenames = set(media_map.values())

        # All expected files should be present
        for expected in expected_filenames:
            assert expected in actual_filenames, (
                f"Expected media file {expected} not found. Found: {actual_filenames}"
            )


class TestE2EFieldContentPreservation:
    """Verify field content is preserved correctly through export."""

    def test_e2e_front_back_fields_preserved(self, temp_dir):
        """Front-back card fields should be preserved."""
        card = {
            "type": "front-back",
            "question": "Test question with **bold** text",
            "answer": "Test answer with *italic*",
            "extra_info": "Extra information here",
            "author": "Test Author",
            "source": "Test Source",
        }
        data = {"deck_name": "Field Test", "cards": [card]}
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            cursor = conn.execute("SELECT flds FROM notes")
            flds = cursor.fetchone()[0]
            fields = flds.split("\x1f")

            # Question should contain bold markup (converted to HTML)
            assert "<strong>bold</strong>" in fields[0]
            # Answer should contain italic markup
            assert "<em>italic</em>" in fields[1]
        finally:
            conn.close()

    def test_e2e_cloze_syntax_preserved(self, temp_dir):
        """Cloze deletion syntax should be preserved in export."""
        card = {
            "type": "cloze",
            "cloze_text": "The {{c1::first}} and {{c2::second}} items",
        }
        data = {"deck_name": "Cloze Test", "cards": [card]}
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            cursor = conn.execute("SELECT flds FROM notes")
            flds = cursor.fetchone()[0]

            # Cloze syntax should be preserved
            assert "{{c1::" in flds
            assert "{{c2::" in flds
        finally:
            conn.close()

    def test_e2e_unicode_preserved(self, temp_dir):
        """Unicode content should be preserved through export."""
        card = {
            "type": "front-back",
            "question": "カタカナ (Katakana) question",
            "answer": "القرآن الكريم - Arabic text",
        }
        data = {"deck_name": "Unicode Test", "cards": [card]}
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            cursor = conn.execute("SELECT flds FROM notes")
            flds = cursor.fetchone()[0]

            # Unicode should be preserved
            assert "カタカナ" in flds
            assert "القرآن" in flds
        finally:
            conn.close()


class TestE2ETags:
    """Verify tags are applied correctly."""

    def test_e2e_batch_tags_applied(self, temp_dir):
        """Batch tags should be applied to all notes."""
        card = {
            "type": "front-back",
            "question": "Q",
            "answer": "A",
        }
        data = {
            "deck_name": "Tag Test",
            "batch_tags": ["batch-tag-1", "batch-tag-2"],
            "cards": [card],
        }
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            cursor = conn.execute("SELECT tags FROM notes")
            tags = cursor.fetchone()[0]

            # Tags are stored space-separated in Anki
            assert "batch-tag-1" in tags
            assert "batch-tag-2" in tags
        finally:
            conn.close()

    def test_e2e_per_card_tags_applied(self, temp_dir):
        """Per-card tags should be merged with batch tags."""
        card = {
            "type": "front-back",
            "question": "Q",
            "answer": "A",
            "tags": ["card-specific-tag"],
        }
        data = {
            "deck_name": "Tag Test",
            "batch_tags": ["batch-tag"],
            "cards": [card],
        }
        output_path = os.path.join(temp_dir, "test.apkg")

        create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            cursor = conn.execute("SELECT tags FROM notes")
            tags = cursor.fetchone()[0]

            # Both batch and card-specific tags should be present
            assert "batch-tag" in tags
            assert "card-specific-tag" in tags
        finally:
            conn.close()


class TestE2ECardCounts:
    """Verify card counts match expectations for multi-card note types."""

    def test_e2e_concept_generates_two_cards(self, temp_dir):
        """Concept notes should generate exactly 2 cards (bidirectional)."""
        card = {
            "type": "concept",
            "concept": "Test Concept",
            "definition": "Test definition",
        }
        data = {"deck_name": "Count Test", "cards": [card]}
        output_path = os.path.join(temp_dir, "test.apkg")

        result = create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            note_count = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
            card_count = conn.execute("SELECT count(*) FROM cards").fetchone()[0]

            assert note_count == 1
            assert card_count == 2
            assert result["total_cards"] == 2
        finally:
            conn.close()

    def test_e2e_cloze_generates_correct_card_count(self, temp_dir):
        """Cloze notes should generate one card per deletion."""
        card = {
            "type": "cloze",
            "cloze_text": "{{c1::A}}, {{c2::B}}, {{c3::C}}",
        }
        data = {"deck_name": "Count Test", "cards": [card]}
        output_path = os.path.join(temp_dir, "test.apkg")

        result = create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            note_count = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
            card_count = conn.execute("SELECT count(*) FROM cards").fetchone()[0]

            assert note_count == 1
            assert card_count == 3  # One per cloze deletion
            assert result["total_cards"] == 3
        finally:
            conn.close()

    def test_e2e_person_generates_variable_card_count(self, temp_dir):
        """Person notes should generate one card per filled optional field."""
        card = {
            "type": "person",
            "full_name": "Jane Doe",
            "birthday": "March 15",      # 1 card
            "current_city": "NYC",       # 1 card
            "title": "Engineer",         # 1 card
        }
        data = {"deck_name": "Count Test", "cards": [card]}
        output_path = os.path.join(temp_dir, "test.apkg")

        result = create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            note_count = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
            card_count = conn.execute("SELECT count(*) FROM cards").fetchone()[0]

            assert note_count == 1
            assert card_count == 3  # One per filled field
        finally:
            conn.close()

    def test_e2e_image_occlusion_generates_correct_card_count(self, temp_dir):
        """Image-occlusion notes should generate one card per occlusion region."""
        import base64
        from io import BytesIO
        from PIL import Image

        # Create test image
        img = Image.new("RGB", (100, 100), color="gray")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        b64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

        card = {
            "type": "image-occlusion",
            "image_data": f"data:image/png;base64,{b64_data}",
            "occlusions": [
                {"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1},
                {"cloze_num": 2, "label": "B", "left": 0.3, "top": 0.1, "width": 0.1, "height": 0.1},
                {"cloze_num": 3, "label": "C", "left": 0.5, "top": 0.1, "width": 0.1, "height": 0.1},
                {"cloze_num": 4, "label": "D", "left": 0.7, "top": 0.1, "width": 0.1, "height": 0.1},
            ],
        }
        data = {"deck_name": "Count Test", "cards": [card]}
        output_path = os.path.join(temp_dir, "test.apkg")

        result = create_package(data, output_path)
        collection_path, _ = extract_apkg(output_path, temp_dir)

        conn = sqlite3.connect(collection_path)
        try:
            note_count = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
            card_count = conn.execute("SELECT count(*) FROM cards").fetchone()[0]

            assert note_count == 1
            assert card_count == 4  # One per occlusion region
            assert result["total_cards"] == 4
        finally:
            conn.close()


class TestE2EThemeSupport:
    """Verify theme selection works in E2E export."""

    @pytest.mark.parametrize("theme", ["minimal", "classic", "high-contrast", "calm"])
    def test_e2e_export_with_all_themes(self, temp_dir, theme):
        """Export should work with all supported themes."""
        card = {
            "type": "front-back",
            "question": "Q",
            "answer": "A",
        }
        data = {
            "deck_name": "Theme Test",
            "theme": theme,
            "cards": [card],
        }
        output_path = os.path.join(temp_dir, f"theme_{theme}.apkg")

        result = create_package(data, output_path)

        assert os.path.exists(output_path)
        assert result["theme"] == theme


class TestE2EFullTestDeck:
    """Integration test using the complete test-cards.json file."""

    def test_e2e_full_deck_export(self, temp_dir):
        """Export the full test deck and verify comprehensive success."""
        data = load_test_cards()
        output_path = os.path.join(temp_dir, "full_test.apkg")

        result = create_package(data, output_path, base_path=str(REPO_ROOT))
        collection_path, media_map = extract_apkg(output_path, temp_dir)

        # Verify the result matches expected structure
        assert result["deck_name"] == "Anki Skill Test Deck"
        assert result["theme"] == "minimal"

        # Verify database integrity
        conn = sqlite3.connect(collection_path)
        try:
            note_count = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
            card_count = conn.execute("SELECT count(*) FROM cards").fetchone()[0]

            assert note_count == result["total_notes"]
            assert card_count == result["total_cards"]

            # Verify we have the expected note types
            assert result["front_back_count"] >= 6  # Several front-back cards in test data
            assert result["concept_count"] >= 2     # Several concept cards
            assert result["cloze_count"] >= 4       # Several cloze cards
            assert result["image_count"] >= 1       # At least one image card
            assert result["person_count"] >= 1      # At least one person card
            assert result["image_occlusion_count"] >= 1  # At least one IO card

            # Verify batch tags applied
            cursor = conn.execute("SELECT tags FROM notes")
            all_tags = " ".join([row[0] for row in cursor.fetchall()])
            assert "test-data" in all_tags
            assert "skill-validation" in all_tags
        finally:
            conn.close()

        # Verify media files
        assert len(media_map) >= 3  # At least statue, person photo, heart anatomy
