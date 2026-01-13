"""Tests for exporter module."""

import json
import os
import re
import sqlite3
import zipfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw
from anki_utils.exporter import (
    count_cloze_deletions,
    count_person_cards,
    convert_card_fields,
    create_package,
    create_image_occlusion_note,
    get_image_occlusion_model,
    validate_data,
    validate_card,
    ValidationError,
)


class TestCountClozeDeletions:
    """Tests for count_cloze_deletions function."""

    def test_single_cloze(self):
        """Test counting single cloze deletion."""
        text = "The {{c1::answer}} is here"
        assert count_cloze_deletions(text) == 1

    def test_multiple_same_number(self):
        """Test multiple clozes with same number counts as one."""
        text = "{{c1::First}} and {{c1::second}}"
        assert count_cloze_deletions(text) == 1

    def test_multiple_different_numbers(self):
        """Test multiple clozes with different numbers."""
        text = "{{c1::First}} and {{c2::second}} and {{c3::third}}"
        assert count_cloze_deletions(text) == 3

    def test_no_cloze(self):
        """Test text without cloze deletions."""
        text = "No cloze here"
        assert count_cloze_deletions(text) == 0

    def test_empty_string(self):
        """Test empty string."""
        assert count_cloze_deletions("") == 0

    def test_mixed_numbers(self):
        """Test non-sequential cloze numbers."""
        text = "{{c1::A}}, {{c3::B}}, {{c5::C}}"
        assert count_cloze_deletions(text) == 3

    def test_cloze_with_hint(self):
        """Test cloze with hint syntax."""
        text = "{{c1::answer::hint}}"
        assert count_cloze_deletions(text) == 1

    def test_double_digit_cloze_numbers(self):
        """Test double-digit cloze numbers."""
        text = "{{c10::tenth}} and {{c11::eleventh}}"
        assert count_cloze_deletions(text) == 2


class TestCountPersonCards:
    """Tests for count_person_cards function."""

    def test_empty_person(self):
        """Person with only name generates no cards."""
        card = {"full_name": "John Doe"}
        assert count_person_cards(card) == 0

    def test_person_with_photo(self):
        """Person with photo generates 1 card."""
        card = {"full_name": "John Doe", "photo_path": "/path/to/photo.jpg"}
        assert count_person_cards(card) == 1

    def test_person_with_multiple_fields(self):
        """Person with multiple fields generates multiple cards."""
        card = {
            "full_name": "John Doe",
            "photo_path": "/path/to/photo.jpg",
            "birthday": "March 15",
            "current_city": "NYC",
            "title": "Engineer",
        }
        assert count_person_cards(card) == 4

    def test_person_all_fields(self):
        """Person with all optional fields generates max cards."""
        card = {
            "full_name": "John Doe",
            "photo_path": "/path/to/photo.jpg",
            "current_city": "NYC",
            "title": "Engineer",
            "reports_to": "Jane",
            "direct_reports": "Tom, Jerry",
            "partner_name": "Mary",
            "hobbies": "Reading",
            "children_names": "Alice",
            "pet_names": "Rex",
            "phone_number": "555-1234",
            "birthday": "March 15",
            "company": "Acme Corp",
        }
        # 12 card-generating fields
        assert count_person_cards(card) == 12

    def test_empty_string_field_not_counted(self):
        """Empty string fields don't generate cards."""
        card = {
            "full_name": "John Doe",
            "birthday": "",
            "current_city": "NYC",
        }
        assert count_person_cards(card) == 1


class TestConvertCardFields:
    """Tests for convert_card_fields function."""

    def test_converts_question_field(self):
        """Question field should be converted."""
        card = {"question": "**Bold question**"}
        result = convert_card_fields(card)
        assert "<strong>Bold question</strong>" in result["question"]

    def test_converts_answer_field(self):
        """Answer field should be converted."""
        card = {"answer": "The answer is *italic*"}
        result = convert_card_fields(card)
        assert "<em>italic</em>" in result["answer"]

    def test_preserves_non_text_fields(self):
        """Non-text fields should be preserved as-is."""
        card = {"type": "front-back", "tags": ["tag1", "tag2"]}
        result = convert_card_fields(card)
        assert result["type"] == "front-back"
        assert result["tags"] == ["tag1", "tag2"]

    def test_handles_missing_fields(self):
        """Missing fields should not cause errors."""
        card = {"question": "Just a question"}
        result = convert_card_fields(card)
        assert "answer" not in result

    def test_converts_cloze_text(self):
        """Cloze text should be converted but preserve cloze syntax."""
        card = {"cloze_text": "**Bold** with {{c1::cloze}}"}
        result = convert_card_fields(card)
        assert "<strong>Bold</strong>" in result["cloze_text"]
        assert "{{c1::cloze}}" in result["cloze_text"]


class TestCreatePackage:
    """Tests for create_package function."""

    def test_creates_apkg_file(self, temp_dir, sample_front_back_card):
        """create_package should create an .apkg file."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Test Deck",
            "cards": [sample_front_back_card],
        }
        result = create_package(data, output_path)

        assert os.path.exists(output_path)
        assert result["deck_name"] == "Test Deck"

    def test_returns_correct_counts(self, temp_dir, sample_front_back_card):
        """create_package should return accurate card counts."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Test Deck",
            "cards": [sample_front_back_card],
        }
        result = create_package(data, output_path)

        assert result["front_back_count"] == 1
        assert result["total_notes"] == 1
        assert result["total_cards"] == 1

    def test_cloze_counts_cards_correctly(self, temp_dir, sample_cloze_card):
        """Cloze cards should count based on deletions."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Test Deck",
            "cards": [sample_cloze_card],
        }
        result = create_package(data, output_path)

        assert result["cloze_count"] == 1
        assert result["total_notes"] == 1
        # The sample cloze has 2 deletions (c1 and c2)
        assert result["total_cards"] == 2

    def test_concept_counts_two_cards(self, temp_dir, sample_concept_card):
        """Concept cards generate 2 cards (bidirectional)."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Test Deck",
            "cards": [sample_concept_card],
        }
        result = create_package(data, output_path)

        assert result["concept_count"] == 1
        assert result["total_cards"] == 2

    def test_mixed_card_types(self, temp_dir, sample_deck_data):
        """Multiple card types should be counted correctly."""
        output_path = os.path.join(temp_dir, "test.apkg")
        result = create_package(sample_deck_data, output_path)

        assert result["front_back_count"] == 1
        assert result["cloze_count"] == 1
        assert result["total_notes"] == 2

    def test_applies_batch_tags(self, temp_dir, sample_front_back_card):
        """Batch tags should be applied to all cards."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Test Deck",
            "batch_tags": ["batch-tag"],
            "cards": [sample_front_back_card],
        }
        # We can't easily verify tags in the output, but this should not error
        result = create_package(data, output_path)
        assert os.path.exists(output_path)

    def test_uses_default_theme(self, temp_dir, sample_front_back_card):
        """Default theme should be used when not specified."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Test Deck",
            "cards": [sample_front_back_card],
        }
        result = create_package(data, output_path)
        assert result["theme"] == "minimal"

    def test_uses_specified_theme(self, temp_dir, sample_front_back_card):
        """Specified theme should be used."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Test Deck",
            "theme": "high-contrast",
            "cards": [sample_front_back_card],
        }
        result = create_package(data, output_path)
        assert result["theme"] == "high-contrast"

    def test_empty_deck(self, temp_dir):
        """Empty deck should create valid package."""
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {
            "deck_name": "Empty Deck",
            "cards": [],
        }
        result = create_package(data, output_path)
        assert os.path.exists(output_path)
        assert result["total_notes"] == 0

    def test_resolves_relative_media_paths_with_base_path(self, temp_dir):
        """Relative image paths should resolve against base_path."""
        output_path = os.path.join(temp_dir, "test.apkg")
        media_dir = os.path.join(temp_dir, "assets")
        os.makedirs(media_dir, exist_ok=True)
        image_path = os.path.join(media_dir, "example.png")
        with open(image_path, "wb") as image_file:
            image_file.write(b"")

        data = {
            "deck_name": "Media Test",
            "cards": [
                {
                    "type": "image",
                    "image_path": os.path.join("assets", "example.png"),
                    "prompt": "Test image",
                    "answer": "Example",
                }
            ],
        }

        result = create_package(data, output_path, base_path=temp_dir)

        assert os.path.exists(output_path)
        assert result["media_files_included"] == 1


class TestValidation:
    """Tests for input validation."""

    def test_valid_data_passes(self, sample_front_back_card):
        """Valid data should pass validation."""
        data = {"cards": [sample_front_back_card]}
        # Should not raise
        validate_data(data)

    def test_data_must_be_dict(self):
        """Input must be a dictionary."""
        with pytest.raises(ValidationError, match="must be a dictionary"):
            validate_data("not a dict")

    def test_cards_must_be_list(self):
        """Cards must be a list."""
        with pytest.raises(ValidationError, match="must be an array"):
            validate_data({"cards": "not a list"})

    def test_batch_tags_must_be_list(self):
        """Batch tags must be a list."""
        with pytest.raises(ValidationError, match="must be an array"):
            validate_data({"cards": [], "batch_tags": "not a list"})

    def test_card_must_be_dict(self):
        """Each card must be a dictionary."""
        with pytest.raises(ValidationError, match="must be a dictionary"):
            validate_data({"cards": ["not a dict"]})

    def test_card_requires_type(self):
        """Card must have a type field."""
        with pytest.raises(ValidationError, match="missing required 'type' field"):
            validate_card({"question": "Q", "answer": "A"}, 0)

    def test_card_type_must_be_valid(self):
        """Card type must be one of the valid types."""
        with pytest.raises(ValidationError, match="invalid type"):
            validate_card({"type": "invalid-type"}, 0)

    def test_front_back_requires_question_and_answer(self):
        """Front-back card requires question and answer."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "answer": "A"}, 0)

        with pytest.raises(ValidationError, match="missing required field 'answer'"):
            validate_card({"type": "front-back", "question": "Q"}, 0)

    def test_concept_requires_concept_and_definition(self):
        """Concept card requires concept and definition."""
        with pytest.raises(ValidationError, match="missing required field 'concept'"):
            validate_card({"type": "concept", "definition": "D"}, 0)

    def test_cloze_requires_cloze_text(self):
        """Cloze card requires cloze_text."""
        with pytest.raises(ValidationError, match="missing required field 'cloze_text'"):
            validate_card({"type": "cloze"}, 0)

    def test_cloze_requires_cloze_syntax(self):
        """Cloze text must contain cloze syntax."""
        with pytest.raises(ValidationError, match="must contain cloze syntax"):
            validate_card({"type": "cloze", "cloze_text": "no cloze here"}, 0)

    def test_person_requires_full_name(self):
        """Person card requires full_name."""
        with pytest.raises(ValidationError, match="missing required field 'full_name'"):
            validate_card({"type": "person"}, 0)

    def test_image_occlusion_requires_occlusions(self):
        """Image-occlusion requires occlusions field."""
        # Empty list is treated as missing (falsy)
        with pytest.raises(ValidationError, match="missing required field 'occlusions'"):
            validate_card({
                "type": "image-occlusion",
                "image_path": "/path/to/image.jpg",
                "occlusions": []
            }, 0)

        # Missing field entirely
        with pytest.raises(ValidationError, match="missing required field 'occlusions'"):
            validate_card({
                "type": "image-occlusion",
                "image_path": "/path/to/image.jpg",
            }, 0)

    def test_image_occlusion_accepts_image_data_as_alternative(self):
        """Image-occlusion accepts image_data instead of image_path."""
        # Should not raise - image_data is valid alternative
        validate_card({
            "type": "image-occlusion",
            "image_data": "data:image/png;base64,iVBORw0KGgo=",
            "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
        }, 0)

    def test_image_occlusion_requires_image_path_or_image_data(self):
        """Image-occlusion requires either image_path or image_data."""
        with pytest.raises(ValidationError, match="requires either 'image_path' or 'image_data'"):
            validate_card({
                "type": "image-occlusion",
                "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
            }, 0)

    def test_image_occlusion_accepts_both_image_path_and_image_data(self):
        """Image-occlusion can have both image_path and image_data (path preferred)."""
        # Should not raise - having both is fine
        validate_card({
            "type": "image-occlusion",
            "image_path": "/path/to/image.jpg",
            "image_data": "data:image/png;base64,iVBORw0KGgo=",
            "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
        }, 0)

    def test_create_package_validates_input(self, temp_dir):
        """create_package should raise ValidationError for invalid input."""
        output_path = os.path.join(temp_dir, "test.apkg")
        with pytest.raises(ValidationError):
            create_package({"cards": [{"type": "invalid"}]}, output_path)


class TestImageOcclusionExport:
    """Tests for image-occlusion card export functionality."""

    def test_io_note_generates_svg_structure(self, sample_image_occlusion_card):
        """IO card generates correct SVG with masks."""
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(sample_image_occlusion_card, model)

        fields = note.fields
        image_svg_field = fields[0]

        assert '<svg class="io-svg"' in image_svg_field
        assert 'viewBox="0 0 100 100"' in image_svg_field
        assert 'data-occlusion-mode="hide_all_guess_one"' in image_svg_field

    def test_io_note_generates_rect_mask(self, sample_image_occlusion_card):
        """IO card generates rect mask for rect shapes."""
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(sample_image_occlusion_card, model)

        image_svg = note.fields[0]
        assert '<rect class="io-mask" data-cloze="1"' in image_svg
        assert 'x="10.0000"' in image_svg
        assert 'y="20.0000"' in image_svg

    def test_io_note_generates_ellipse_mask(self, sample_image_occlusion_card):
        """IO card generates ellipse mask for ellipse shapes."""
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(sample_image_occlusion_card, model)

        image_svg = note.fields[0]
        assert '<ellipse class="io-mask" data-cloze="2"' in image_svg
        assert 'cx="60.0000"' in image_svg
        assert 'cy="67.5000"' in image_svg

    def test_io_note_generates_cloze_text(self, sample_image_occlusion_card):
        """IO card generates cloze text from occlusion labels."""
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(sample_image_occlusion_card, model)

        cloze_field = note.fields[1]
        assert '{{c1::Part A}}' in cloze_field
        assert '{{c2::Part B}}' in cloze_field

    def test_io_note_includes_fill_color(self, sample_image_occlusion_card):
        """IO mask with fill color includes style attribute."""
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(sample_image_occlusion_card, model)

        image_svg = note.fields[0]
        assert 'style="fill: #ffeba2;"' in image_svg

    def test_io_card_multiple_occlusions_all_exported(self):
        """IO card with multiple occlusions exports all masks."""
        import base64
        from io import BytesIO
        from PIL import Image as PILImage

        # Create test image
        img = PILImage.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        b64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        card = {
            "type": "image-occlusion",
            "image_data": f"data:image/png;base64,{b64_data}",
            "occlusions": [
                {"cloze_num": 1, "label": "A", "shape": "rect", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1},
                {"cloze_num": 2, "label": "B", "shape": "rect", "left": 0.3, "top": 0.3, "width": 0.1, "height": 0.1},
                {"cloze_num": 3, "label": "C", "shape": "rect", "left": 0.5, "top": 0.5, "width": 0.1, "height": 0.1},
            ]
        }
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(card, model)

        image_svg = note.fields[0]
        assert image_svg.count('class="io-mask"') == 3
        assert 'data-cloze="1"' in image_svg
        assert 'data-cloze="2"' in image_svg
        assert 'data-cloze="3"' in image_svg

    @pytest.mark.parametrize("theme", ["minimal", "classic", "high-contrast", "calm"])
    def test_io_card_works_with_all_themes(self, sample_image_occlusion_card, theme):
        """IO card exports correctly with all 4 themes."""
        model = get_image_occlusion_model(theme)
        note = create_image_occlusion_note(sample_image_occlusion_card, model)

        assert note is not None
        assert '<svg class="io-svg"' in note.fields[0]
        assert '{{c1::Part A}}' in note.fields[1]

    def test_io_export_creates_apkg(self, temp_dir, sample_image_occlusion_card):
        """IO card exports to .apkg successfully."""
        output_path = os.path.join(temp_dir, "io_test.apkg")
        data = {
            "deck_name": "IO Test Deck",
            "cards": [sample_image_occlusion_card]
        }
        result = create_package(data, output_path)

        assert os.path.exists(output_path)
        assert result['image_occlusion_count'] == 1
        assert result['total_cards'] >= 2

    def test_io_note_with_image_data(self, sample_image_occlusion_card_with_base64):
        """IO card works with base64 image_data instead of image_path."""
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(sample_image_occlusion_card_with_base64, model)

        image_svg = note.fields[0]
        # Should contain the base64 data URL in the SVG
        assert 'data:image/png;base64,' in image_svg
        assert '<svg class="io-svg"' in image_svg
        assert '{{c1::Part A}}' in note.fields[1]

    def test_io_note_extracts_dimensions_from_base64(self, sample_image_occlusion_card_with_base64):
        """IO card extracts correct dimensions from base64 image_data."""
        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(sample_image_occlusion_card_with_base64, model)

        image_svg = note.fields[0]
        # The fixture creates a 100x75 image, so aspect ratio should be 75%
        # viewBox width is always 100, height should be 75
        assert 'viewBox="0 0 100 75"' in image_svg

    def test_io_note_uses_explicit_dimensions(self):
        """IO card uses explicit image_width/image_height when provided."""
        import base64
        from io import BytesIO
        from PIL import Image as PILImage

        # Create a 50x50 image but provide different explicit dimensions
        img = PILImage.new('RGB', (50, 50), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        b64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        card = {
            "type": "image-occlusion",
            "image_data": f"data:image/png;base64,{b64_data}",
            "image_width": 200,  # Override: pretend it's 200x100
            "image_height": 100,
            "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
        }

        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(card, model)

        image_svg = note.fields[0]
        # With 200x100, aspect ratio is 50%, so viewBox height should be 50
        assert 'viewBox="0 0 100 50"' in image_svg

    def test_io_note_fails_without_image_source(self):
        """IO card raises ValidationError when neither image_path nor image_data available."""
        card = {
            "type": "image-occlusion",
            "image_path": "/nonexistent/path/to/image.jpg",  # File doesn't exist
            # No image_data fallback
            "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
        }

        model = get_image_occlusion_model('minimal')
        with pytest.raises(ValidationError, match="could not load image"):
            create_image_occlusion_note(card, model)

    def test_io_note_prefers_file_over_base64(self, temp_dir):
        """IO card prefers reading from image_path over using image_data."""
        import base64
        from io import BytesIO
        from PIL import Image as PILImage

        # Create actual file with a green image
        green_img = PILImage.new('RGB', (80, 60), color='green')
        file_path = os.path.join(temp_dir, 'test_image.png')
        green_img.save(file_path, format='PNG')

        # Create base64 of a red image (different content)
        red_img = PILImage.new('RGB', (40, 30), color='red')
        buffer = BytesIO()
        red_img.save(buffer, format='PNG')
        red_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        card = {
            "type": "image-occlusion",
            "image_path": file_path,  # Points to green image
            "image_data": f"data:image/png;base64,{red_b64}",  # Contains red image
            "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
        }

        model = get_image_occlusion_model('minimal')
        note = create_image_occlusion_note(card, model)

        image_svg = note.fields[0]
        # Should use dimensions from file (80x60), not from base64 (40x30)
        # 80x60 = 75% aspect ratio, so viewBox height should be 75
        assert 'viewBox="0 0 100 75"' in image_svg

    def test_io_export_with_base64_creates_apkg(self, temp_dir, sample_image_occlusion_card_with_base64):
        """IO card with base64 image_data exports to .apkg successfully."""
        output_path = os.path.join(temp_dir, "io_base64_test.apkg")
        data = {
            "deck_name": "IO Base64 Test Deck",
            "cards": [sample_image_occlusion_card_with_base64]
        }
        result = create_package(data, output_path)

        assert os.path.exists(output_path)
        assert result['image_occlusion_count'] == 1
        assert result['total_cards'] >= 1


class TestImageOcclusionEndToEnd:
    """End-to-end checks for IO export artifacts and media packaging."""

    def test_io_export_packages_media_and_svg(self, temp_dir):
        """IO export writes SVG masks, cloze text, and media into the .apkg."""
        repo_root = Path(__file__).resolve().parents[1]
        image_rel_path = Path("assets/test-data/heart-anatomy.jpg")
        image_abs_path = repo_root / image_rel_path

        assert image_abs_path.exists()

        card = {
            "type": "image-occlusion",
            "image_path": str(image_rel_path),
            "header": "Label the four chambers of the heart",
            "back_extra": "Verify occlusion masking and labels.",
            "occlusion_mode": "hide_all_guess_one",
            "occlusions": [
                {
                    "cloze_num": 1,
                    "label": "Right Atrium",
                    "shape": "rect",
                    "left": 0.175,
                    "top": 0.2878,
                    "width": 0.0672,
                    "height": 0.0566,
                },
                {
                    "cloze_num": 2,
                    "label": "Left Atrium",
                    "shape": "rect",
                    "left": 0.7523,
                    "top": 0.2867,
                    "width": 0.068,
                    "height": 0.0577,
                },
            ],
            "tags": ["image-occlusion-test"],
        }

        output_path = os.path.join(temp_dir, "io-e2e.apkg")
        result = create_package(
            {"deck_name": "IO E2E Test", "cards": [card]},
            output_path,
            base_path=str(repo_root),
        )

        assert os.path.exists(output_path)
        assert result["image_occlusion_count"] == 1
        assert result["media_files_included"] == 1

        with zipfile.ZipFile(output_path) as package:
            names = package.namelist()
            collection_name = "collection.anki21" if "collection.anki21" in names else "collection.anki2"
            assert collection_name in names
            assert "media" in names

            media_map = json.loads(package.read("media").decode("utf-8"))
            assert image_abs_path.name in media_map.values()

            collection_bytes = package.read(collection_name)

        db_path = os.path.join(temp_dir, collection_name)
        with open(db_path, "wb") as db_file:
            db_file.write(collection_bytes)

        conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute("select flds from notes").fetchall()
        finally:
            conn.close()

        assert rows
        note_fields = rows[0][0].split("\x1f")
        assert len(note_fields) >= 3

        image_svg = note_fields[0]
        cloze_text = note_fields[1]
        occlusion_payload = json.loads(note_fields[2])

        assert '<svg class="io-svg"' in image_svg
        assert 'data:image/jpeg;base64,' in image_svg
        assert 'data-occlusion-mode="hide_all_guess_one"' in image_svg
        assert 'class="io-mask"' in image_svg
        assert 'data-cloze="1"' in image_svg
        assert 'data-cloze="2"' in image_svg
        assert "{{c1::Right Atrium}}" in cloze_text
        assert "{{c2::Left Atrium}}" in cloze_text
        assert occlusion_payload["mode"] == "hide_all_guess_one"
        assert occlusion_payload["regions"][0]["shape"] == "rect"
        assert occlusion_payload["regions"][0]["label"] == "Right Atrium"


def _load_test_io_card() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    test_cards_path = repo_root / "assets/test-data/test-cards.json"
    with test_cards_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    for card in payload.get("cards", []):
        if card.get("type") == "image-occlusion":
            return card
    raise AssertionError("Missing image-occlusion card in test data")


def _label_boxes_for_heart_diagram() -> dict[str, dict[str, float]]:
    return {
        "Right Atrium": {"left": 0.175, "top": 0.2878, "width": 0.0672, "height": 0.0566},
        "Left Atrium": {"left": 0.7523, "top": 0.2867, "width": 0.068, "height": 0.0577},
        "Right Ventricle": {"left": 0.168, "top": 0.6456, "width": 0.0883, "height": 0.0566},
        "Left Ventricle": {"left": 0.7461, "top": 0.6444, "width": 0.0875, "height": 0.0578},
    }


def _coverage_ratio(outer: dict, inner: dict) -> float:
    outer_left = outer["left"]
    outer_top = outer["top"]
    outer_right = outer_left + outer["width"]
    outer_bottom = outer_top + outer["height"]

    inner_left = inner["left"]
    inner_top = inner["top"]
    inner_right = inner_left + inner["width"]
    inner_bottom = inner_top + inner["height"]

    intersect_left = max(outer_left, inner_left)
    intersect_top = max(outer_top, inner_top)
    intersect_right = min(outer_right, inner_right)
    intersect_bottom = min(outer_bottom, inner_bottom)

    if intersect_right <= intersect_left or intersect_bottom <= intersect_top:
        return 0.0

    intersect_area = (intersect_right - intersect_left) * (intersect_bottom - intersect_top)
    inner_area = (inner_right - inner_left) * (inner_bottom - inner_top)
    if inner_area <= 0:
        return 0.0
    return intersect_area / inner_area


def _resolve_io_card_path(card: dict) -> tuple[Path, dict]:
    repo_root = Path(__file__).resolve().parents[1]
    card_copy = dict(card)
    image_path = Path(card_copy["image_path"])
    if not image_path.is_absolute():
        image_path = repo_root / image_path
    card_copy["image_path"] = str(image_path)
    return image_path, card_copy


def _tesseract_available() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except Exception:
        return False
    return True


class TestImageOcclusionAlignment:
    def test_io_heart_occlusions_cover_label_boxes(self):
        card = _load_test_io_card()
        _, resolved_card = _resolve_io_card_path(card)
        occlusions = resolved_card["occlusions"]
        labels = _label_boxes_for_heart_diagram()

        for label, expected_box in labels.items():
            best_coverage = max(
                _coverage_ratio(occ, expected_box) for occ in occlusions
            )
            assert best_coverage >= 0.9, f"{label} coverage too low ({best_coverage:.2f})"

    def test_io_svg_viewbox_matches_image_aspect_ratio(self):
        card = _load_test_io_card()
        image_path, resolved_card = _resolve_io_card_path(card)
        model = get_image_occlusion_model("minimal")
        note = create_image_occlusion_note(resolved_card, model)

        with Image.open(image_path) as img:
            width, height = img.size
        expected_height = 100.0 * (height / width)

        match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', note.fields[0])
        assert match is not None
        viewbox_width = float(match.group(1))
        viewbox_height = float(match.group(2))

        assert abs(viewbox_width - 100.0) < 0.01
        assert abs(viewbox_height - expected_height) < 0.05

    def test_io_heart_masks_hide_label_text(self):
        if not _tesseract_available():
            pytest.skip("tesseract not available")

        import pytesseract

        card = _load_test_io_card()
        image_path, resolved_card = _resolve_io_card_path(card)

        with Image.open(image_path).convert("RGB") as img:
            draw = ImageDraw.Draw(img)
            for occ in resolved_card["occlusions"]:
                left = occ["left"] * img.width
                top = occ["top"] * img.height
                width = occ["width"] * img.width
                height = occ["height"] * img.height
                bbox = [left, top, left + width, top + height]
                if occ.get("shape") == "ellipse":
                    draw.ellipse(bbox, fill=(0, 0, 0))
                else:
                    draw.rectangle(bbox, fill=(0, 0, 0))

            ocr = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        labels = {"right", "left", "atrium", "ventricle"}
        found = set()
        for text, conf in zip(ocr["text"], ocr["conf"]):
            try:
                conf_value = float(conf)
            except ValueError:
                continue
            if conf_value < 50:
                continue
            token = text.strip().lower()
            if token in labels:
                found.add(token)

        assert not found, f"Visible label text detected: {sorted(found)}"
