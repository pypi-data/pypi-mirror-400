"""Tests for Anki import compatibility.

These tests verify that exported .apkg files:
1. Have valid ZIP structure
2. Contain valid SQLite database with correct schema
3. Have valid media manifest

Issue #80: https://github.com/Gilbetrar/anki-package/issues/80
"""

import json
import os
import sqlite3
import tempfile
import zipfile
from pathlib import Path

import pytest
from anki_utils.exporter import create_package


class TestZipStructure:
    """Tests verifying the ZIP archive structure of .apkg files."""

    def test_apkg_is_valid_zip(self, temp_dir, sample_front_back_card):
        """Exported .apkg file should be a valid ZIP archive."""
        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({"deck_name": "Test", "cards": [sample_front_back_card]}, output_path)

        assert zipfile.is_zipfile(output_path)

    def test_contains_collection_database(self, temp_dir, sample_front_back_card):
        """ZIP should contain collection.anki21 or collection.anki2."""
        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({"deck_name": "Test", "cards": [sample_front_back_card]}, output_path)

        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()
            has_collection = "collection.anki21" in names or "collection.anki2" in names
            assert has_collection, f"Expected collection database, got: {names}"

    def test_contains_media_manifest(self, temp_dir, sample_front_back_card):
        """ZIP should contain a media manifest file."""
        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({"deck_name": "Test", "cards": [sample_front_back_card]}, output_path)

        with zipfile.ZipFile(output_path) as zf:
            assert "media" in zf.namelist()

    def test_all_referenced_media_files_exist(self, temp_dir):
        """All media files referenced in manifest should exist in the archive."""
        # Create a test image
        import base64
        from io import BytesIO
        from PIL import Image

        img = Image.new('RGB', (100, 100), color='red')
        img_path = os.path.join(temp_dir, "test_image.png")
        img.save(img_path)

        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({
            "deck_name": "Test",
            "cards": [{
                "type": "image",
                "image_path": img_path,
                "prompt": "What is this?",
                "answer": "A red square"
            }]
        }, output_path)

        with zipfile.ZipFile(output_path) as zf:
            names = set(zf.namelist())
            media_manifest = json.loads(zf.read("media").decode("utf-8"))

            for index_str, filename in media_manifest.items():
                # In Anki .apkg files, media files are named by their index
                assert index_str in names, f"Media file {index_str} ({filename}) not in archive"

    def test_empty_deck_has_valid_structure(self, temp_dir):
        """Even empty decks should have valid ZIP structure."""
        output_path = os.path.join(temp_dir, "empty.apkg")
        create_package({"deck_name": "Empty", "cards": []}, output_path)

        assert zipfile.is_zipfile(output_path)
        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()
            has_collection = "collection.anki21" in names or "collection.anki2" in names
            assert has_collection
            assert "media" in names


class TestSqliteSchema:
    """Tests verifying the SQLite database schema is valid for Anki."""

    @pytest.fixture
    def db_from_apkg(self, temp_dir, sample_front_back_card):
        """Create an .apkg and extract the SQLite database."""
        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({"deck_name": "Test", "cards": [sample_front_back_card]}, output_path)

        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()
            collection_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            db_bytes = zf.read(collection_name)

        db_path = os.path.join(temp_dir, "collection.db")
        with open(db_path, "wb") as f:
            f.write(db_bytes)

        conn = sqlite3.connect(db_path)
        yield conn
        conn.close()

    def test_database_is_valid_sqlite(self, db_from_apkg):
        """Extracted database should be valid SQLite."""
        # If we got here, connection succeeded - database is valid
        cursor = db_from_apkg.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        assert version  # Version string exists

    def test_has_notes_table(self, db_from_apkg):
        """Database should have a notes table."""
        cursor = db_from_apkg.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='notes'"
        )
        assert cursor.fetchone() is not None

    def test_has_cards_table(self, db_from_apkg):
        """Database should have a cards table."""
        cursor = db_from_apkg.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cards'"
        )
        assert cursor.fetchone() is not None

    def test_has_col_table(self, db_from_apkg):
        """Database should have a col (collection) table."""
        cursor = db_from_apkg.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='col'"
        )
        assert cursor.fetchone() is not None

    def test_notes_table_has_required_columns(self, db_from_apkg):
        """Notes table should have required columns."""
        cursor = db_from_apkg.execute("PRAGMA table_info(notes)")
        columns = {row[1] for row in cursor.fetchall()}

        required = {"id", "guid", "mid", "mod", "usn", "tags", "flds", "sfld", "csum", "flags", "data"}
        missing = required - columns
        assert not missing, f"Notes table missing columns: {missing}"

    def test_cards_table_has_required_columns(self, db_from_apkg):
        """Cards table should have required columns."""
        cursor = db_from_apkg.execute("PRAGMA table_info(cards)")
        columns = {row[1] for row in cursor.fetchall()}

        required = {"id", "nid", "did", "ord", "mod", "usn", "type", "queue", "due", "ivl", "factor", "reps", "lapses", "left", "odue", "odid", "flags", "data"}
        missing = required - columns
        assert not missing, f"Cards table missing columns: {missing}"

    def test_col_table_has_models_column(self, db_from_apkg):
        """Col table should have models column with valid JSON."""
        cursor = db_from_apkg.execute("PRAGMA table_info(col)")
        columns = {row[1] for row in cursor.fetchall()}
        assert "models" in columns

    def test_models_are_valid_json(self, db_from_apkg):
        """Model definitions in col table should be valid JSON."""
        cursor = db_from_apkg.execute("SELECT models FROM col")
        models_json = cursor.fetchone()[0]

        # Should be valid JSON
        models = json.loads(models_json)
        assert isinstance(models, dict)

    def test_decks_are_valid_json(self, db_from_apkg):
        """Deck definitions in col table should be valid JSON."""
        cursor = db_from_apkg.execute("SELECT decks FROM col")
        decks_json = cursor.fetchone()[0]

        decks = json.loads(decks_json)
        assert isinstance(decks, dict)

    def test_note_has_valid_model_reference(self, db_from_apkg):
        """Each note's mid should reference a valid model."""
        cursor = db_from_apkg.execute("SELECT models FROM col")
        models = json.loads(cursor.fetchone()[0])
        valid_model_ids = {int(k) for k in models.keys()}

        cursor = db_from_apkg.execute("SELECT mid FROM notes")
        for row in cursor.fetchall():
            mid = row[0]
            assert mid in valid_model_ids, f"Note references unknown model {mid}"

    def test_card_references_valid_note(self, db_from_apkg):
        """Each card's nid should reference a valid note."""
        cursor = db_from_apkg.execute("SELECT id FROM notes")
        valid_note_ids = {row[0] for row in cursor.fetchall()}

        cursor = db_from_apkg.execute("SELECT nid FROM cards")
        for row in cursor.fetchall():
            nid = row[0]
            assert nid in valid_note_ids, f"Card references unknown note {nid}"


class TestMediaManifest:
    """Tests verifying the media manifest is valid."""

    def test_media_manifest_is_valid_json(self, temp_dir, sample_front_back_card):
        """Media manifest should be valid JSON."""
        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({"deck_name": "Test", "cards": [sample_front_back_card]}, output_path)

        with zipfile.ZipFile(output_path) as zf:
            media_bytes = zf.read("media")
            media = json.loads(media_bytes.decode("utf-8"))
            assert isinstance(media, dict)

    def test_media_manifest_keys_are_numeric_strings(self, temp_dir):
        """Media manifest keys should be numeric strings."""
        from PIL import Image

        img = Image.new('RGB', (100, 100), color='blue')
        img_path = os.path.join(temp_dir, "test_img.png")
        img.save(img_path)

        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({
            "deck_name": "Test",
            "cards": [{
                "type": "image",
                "image_path": img_path,
                "prompt": "What is this?",
                "answer": "Blue"
            }]
        }, output_path)

        with zipfile.ZipFile(output_path) as zf:
            media = json.loads(zf.read("media").decode("utf-8"))

            for key in media.keys():
                assert key.isdigit(), f"Media key '{key}' is not a numeric string"

    def test_media_manifest_values_are_filenames(self, temp_dir):
        """Media manifest values should be filename strings."""
        from PIL import Image

        img = Image.new('RGB', (100, 100), color='green')
        img_path = os.path.join(temp_dir, "my_image.png")
        img.save(img_path)

        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({
            "deck_name": "Test",
            "cards": [{
                "type": "image",
                "image_path": img_path,
                "prompt": "What is this?",
                "answer": "Green"
            }]
        }, output_path)

        with zipfile.ZipFile(output_path) as zf:
            media = json.loads(zf.read("media").decode("utf-8"))

            for key, filename in media.items():
                assert isinstance(filename, str), f"Media value for key {key} is not a string"
                assert len(filename) > 0, f"Media filename for key {key} is empty"

    def test_media_manifest_empty_for_no_media(self, temp_dir, sample_front_back_card):
        """Media manifest should be empty dict when no media files."""
        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({"deck_name": "Test", "cards": [sample_front_back_card]}, output_path)

        with zipfile.ZipFile(output_path) as zf:
            media = json.loads(zf.read("media").decode("utf-8"))
            assert media == {}

    def test_media_indices_sequential(self, temp_dir):
        """Media file indices should be sequential starting from 0."""
        from PIL import Image

        # Create multiple images
        img_paths = []
        for i, color in enumerate(['red', 'green', 'blue']):
            img = Image.new('RGB', (50, 50), color=color)
            path = os.path.join(temp_dir, f"img_{i}.png")
            img.save(path)
            img_paths.append(path)

        output_path = os.path.join(temp_dir, "test.apkg")
        create_package({
            "deck_name": "Test",
            "cards": [
                {"type": "image", "image_path": path, "prompt": "Color?", "answer": f"Color {i}"}
                for i, path in enumerate(img_paths)
            ]
        }, output_path)

        with zipfile.ZipFile(output_path) as zf:
            media = json.loads(zf.read("media").decode("utf-8"))

            indices = sorted(int(k) for k in media.keys())
            expected = list(range(len(indices)))
            assert indices == expected, f"Media indices not sequential: {indices}"


class TestCardTypeCompatibility:
    """Tests verifying all card types produce valid .apkg files."""

    @pytest.mark.parametrize("card_fixture", [
        "sample_front_back_card",
        "sample_concept_card",
        "sample_cloze_card",
        "sample_person_card",
        "sample_image_occlusion_card",
    ])
    def test_card_type_produces_valid_apkg(self, temp_dir, card_fixture, request):
        """Each card type should produce a valid .apkg file."""
        card = request.getfixturevalue(card_fixture)
        output_path = os.path.join(temp_dir, f"{card_fixture}.apkg")

        create_package({"deck_name": "Test", "cards": [card]}, output_path)

        # Verify ZIP structure
        assert zipfile.is_zipfile(output_path)

        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()

            # Has collection database
            has_db = "collection.anki21" in names or "collection.anki2" in names
            assert has_db

            # Has media manifest
            assert "media" in names

            # Media manifest is valid JSON
            media = json.loads(zf.read("media").decode("utf-8"))
            assert isinstance(media, dict)

            # Extract and validate SQLite
            db_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            db_bytes = zf.read(db_name)

        db_path = os.path.join(temp_dir, "test.db")
        with open(db_path, "wb") as f:
            f.write(db_bytes)

        conn = sqlite3.connect(db_path)
        try:
            # Should have at least one note
            count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            assert count >= 1

            # Models should be valid JSON
            models_json = conn.execute("SELECT models FROM col").fetchone()[0]
            json.loads(models_json)
        finally:
            conn.close()


class TestAllThemesCompatibility:
    """Tests verifying all themes produce valid .apkg files."""

    @pytest.mark.parametrize("theme", ["minimal", "classic", "high-contrast", "calm"])
    def test_theme_produces_valid_apkg(self, temp_dir, sample_front_back_card, theme):
        """Each theme should produce a valid .apkg file."""
        output_path = os.path.join(temp_dir, f"theme_{theme}.apkg")

        create_package({
            "deck_name": "Test",
            "theme": theme,
            "cards": [sample_front_back_card]
        }, output_path)

        assert zipfile.is_zipfile(output_path)

        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()
            has_db = "collection.anki21" in names or "collection.anki2" in names
            assert has_db

            db_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            db_bytes = zf.read(db_name)

        # Verify SQLite is valid
        db_path = os.path.join(temp_dir, "test.db")
        with open(db_path, "wb") as f:
            f.write(db_bytes)

        conn = sqlite3.connect(db_path)
        try:
            models = json.loads(conn.execute("SELECT models FROM col").fetchone()[0])
            # Should have at least one model
            assert len(models) >= 1
        finally:
            conn.close()


class TestMixedContentCompatibility:
    """Tests verifying mixed card types in a single deck."""

    def test_mixed_deck_produces_valid_apkg(
        self, temp_dir,
        sample_front_back_card, sample_concept_card,
        sample_cloze_card, sample_person_card,
        sample_image_occlusion_card
    ):
        """Deck with multiple card types should produce valid .apkg."""
        output_path = os.path.join(temp_dir, "mixed.apkg")

        create_package({
            "deck_name": "Mixed Deck",
            "cards": [
                sample_front_back_card,
                sample_concept_card,
                sample_cloze_card,
                sample_person_card,
                sample_image_occlusion_card,
            ]
        }, output_path)

        assert zipfile.is_zipfile(output_path)

        with zipfile.ZipFile(output_path) as zf:
            names = zf.namelist()
            db_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            db_bytes = zf.read(db_name)

        db_path = os.path.join(temp_dir, "test.db")
        with open(db_path, "wb") as f:
            f.write(db_bytes)

        conn = sqlite3.connect(db_path)
        try:
            # Should have 5 notes (one per card type)
            note_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            assert note_count == 5

            # Should have multiple models
            models = json.loads(conn.execute("SELECT models FROM col").fetchone()[0])
            assert len(models) >= 4  # Different models for different card types

            # All notes should reference valid models
            valid_mids = {int(k) for k in models.keys()}
            cursor = conn.execute("SELECT mid FROM notes")
            for (mid,) in cursor.fetchall():
                assert mid in valid_mids
        finally:
            conn.close()
