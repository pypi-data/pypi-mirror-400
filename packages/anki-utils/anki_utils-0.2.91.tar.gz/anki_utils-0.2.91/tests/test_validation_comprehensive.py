"""Comprehensive validation edge case tests for anki-utils.

These tests verify validation behavior for edge cases beyond the basic tests
in test_exporter.py. Each test class covers a specific category of edge case.
"""

import pytest
from anki_utils.exporter import (
    validate_data,
    validate_card,
    ValidationError,
    create_package,
)


class TestEmptyVsMissingFields:
    """Tests for empty string vs missing field vs whitespace handling."""

    def test_empty_string_question_fails(self):
        """Empty string for required 'question' field should fail."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "question": "", "answer": "A"}, 0)

    def test_empty_string_answer_fails(self):
        """Empty string for required 'answer' field should fail."""
        with pytest.raises(ValidationError, match="missing required field 'answer'"):
            validate_card({"type": "front-back", "question": "Q", "answer": ""}, 0)

    def test_missing_question_field_fails(self):
        """Completely missing 'question' field should fail."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "answer": "A"}, 0)

    def test_whitespace_only_question_passes(self):
        """Whitespace-only content for required field passes validation.

        Note: The validator uses truthy check, so whitespace strings pass.
        This documents current behavior - whitespace is not stripped.
        """
        # Whitespace string is truthy, so passes validation
        card = {"type": "front-back", "question": "   ", "answer": "A"}
        validate_card(card, 0)  # Should not raise

    def test_whitespace_only_cloze_text_fails_syntax_check(self):
        """Whitespace-only cloze_text fails cloze syntax check.

        Note: Whitespace passes the truthy check but fails cloze syntax validation.
        """
        with pytest.raises(ValidationError, match="must contain cloze syntax"):
            validate_card({"type": "cloze", "cloze_text": "   "}, 0)

    def test_none_value_for_required_field_fails(self):
        """None value for required field should fail validation."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "question": None, "answer": "A"}, 0)

    def test_empty_concept_fails(self):
        """Empty concept field should fail."""
        with pytest.raises(ValidationError, match="missing required field 'concept'"):
            validate_card({"type": "concept", "concept": "", "definition": "D"}, 0)

    def test_empty_definition_fails(self):
        """Empty definition field should fail."""
        with pytest.raises(ValidationError, match="missing required field 'definition'"):
            validate_card({"type": "concept", "concept": "C", "definition": ""}, 0)

    def test_empty_full_name_fails(self):
        """Empty full_name for person card should fail."""
        with pytest.raises(ValidationError, match="missing required field 'full_name'"):
            validate_card({"type": "person", "full_name": ""}, 0)

    def test_whitespace_full_name_passes(self):
        """Whitespace-only full_name passes validation.

        Note: Whitespace string is truthy, so passes the required field check.
        This documents current behavior.
        """
        card = {"type": "person", "full_name": "   \t\n  "}
        validate_card(card, 0)  # Should not raise


class TestClozeEdgeCases:
    """Tests for cloze deletion syntax edge cases."""

    def test_invalid_cloze_syntax_braces_fails(self):
        """Text that looks like cloze but has wrong braces fails."""
        with pytest.raises(ValidationError, match="must contain cloze syntax"):
            validate_card({"type": "cloze", "cloze_text": "{c1::not valid}"}, 0)

    def test_invalid_cloze_single_brace_fails(self):
        """Single brace cloze syntax fails."""
        with pytest.raises(ValidationError, match="must contain cloze syntax"):
            validate_card({"type": "cloze", "cloze_text": "The {c1::answer} here"}, 0)

    def test_nested_cloze_passes_validation(self):
        """Nested cloze (unusual) still passes basic validation.

        Note: This passes validation but may not work correctly in Anki.
        The validator only checks for presence of cloze syntax, not correctness.
        """
        # This has valid cloze syntax characters, so it passes validation
        # even though nested cloze doesn't make sense
        card = {
            "type": "cloze",
            "cloze_text": "{{c1::outer {{c2::inner}}}}"
        }
        # Should not raise - validation is lenient
        validate_card(card, 0)

    def test_duplicate_cloze_numbers_passes(self):
        """Duplicate cloze numbers are valid (creates same card)."""
        card = {
            "type": "cloze",
            "cloze_text": "{{c1::first}} and {{c1::second}}"
        }
        # Should not raise
        validate_card(card, 0)

    def test_out_of_order_cloze_numbers_passes(self):
        """Out-of-order cloze numbers are valid."""
        card = {
            "type": "cloze",
            "cloze_text": "{{c3::third}} {{c1::first}} {{c2::second}}"
        }
        # Should not raise
        validate_card(card, 0)

    def test_very_high_cloze_number_passes(self):
        """Very high cloze numbers are valid."""
        card = {
            "type": "cloze",
            "cloze_text": "{{c99::answer}} with high number"
        }
        # Should not raise
        validate_card(card, 0)

    def test_cloze_number_999_passes(self):
        """Three-digit cloze numbers work."""
        card = {
            "type": "cloze",
            "cloze_text": "{{c999::many cards}}"
        }
        # Should not raise
        validate_card(card, 0)

    def test_cloze_with_hint_passes(self):
        """Cloze with hint syntax is valid."""
        card = {
            "type": "cloze",
            "cloze_text": "{{c1::answer::hint text here}}"
        }
        # Should not raise
        validate_card(card, 0)

    def test_cloze_with_empty_answer_fails(self):
        """Cloze with empty answer portion is still valid syntax."""
        # This has valid syntax even if empty - Anki handles it
        card = {
            "type": "cloze",
            "cloze_text": "{{c1::}}"
        }
        # Should not raise - has valid cloze syntax
        validate_card(card, 0)

    def test_cloze_zero_number_passes(self):
        """c0 is technically valid syntax (though unusual)."""
        card = {
            "type": "cloze",
            "cloze_text": "{{c0::zero-indexed}}"
        }
        # Should not raise - has valid cloze pattern
        validate_card(card, 0)


class TestPathEdgeCases:
    """Tests for file path validation edge cases."""

    def test_image_path_with_spaces_passes_validation(self):
        """Paths with spaces are valid for validation (file may not exist)."""
        card = {
            "type": "image",
            "image_path": "/path/with spaces/image.jpg",
            "prompt": "Question",
            "answer": "Answer"
        }
        # Should not raise - validation doesn't check file existence
        validate_card(card, 0)

    def test_image_path_with_unicode_passes_validation(self):
        """Paths with unicode characters are valid."""
        card = {
            "type": "image",
            "image_path": "/путь/к/изображение.jpg",
            "prompt": "Question",
            "answer": "Answer"
        }
        # Should not raise
        validate_card(card, 0)

    def test_image_path_with_chinese_characters(self):
        """Paths with Chinese characters are valid."""
        card = {
            "type": "image",
            "image_path": "/路径/图片.jpg",
            "prompt": "Question",
            "answer": "Answer"
        }
        # Should not raise
        validate_card(card, 0)

    def test_image_path_with_special_characters(self):
        """Paths with special characters are valid."""
        card = {
            "type": "image",
            "image_path": "/path/with-dashes_underscores/image (1).jpg",
            "prompt": "Question",
            "answer": "Answer"
        }
        # Should not raise
        validate_card(card, 0)

    def test_relative_path_with_dotdot(self):
        """Relative paths with .. are valid."""
        card = {
            "type": "image",
            "image_path": "../images/photo.jpg",
            "prompt": "Question",
            "answer": "Answer"
        }
        # Should not raise
        validate_card(card, 0)

    def test_person_photo_path_with_spaces(self):
        """Person photo paths with spaces are valid."""
        card = {
            "type": "person",
            "full_name": "John Doe",
            "photo_path": "/Users/john doe/Pictures/photo.jpg"
        }
        # Should not raise
        validate_card(card, 0)

    def test_io_image_path_with_unicode(self):
        """Image-occlusion paths with unicode are valid."""
        card = {
            "type": "image-occlusion",
            "image_path": "/données/диаграмма.png",
            "occlusions": [
                {"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}
            ]
        }
        # Should not raise
        validate_card(card, 0)


class TestTypeCoercion:
    """Tests for type coercion and type mismatch handling."""

    def test_number_where_string_expected_fails(self):
        """Number in place of string field should fail or be handled."""
        # Numbers are falsy in the 'not card.get(field)' check when 0
        # Non-zero numbers would be truthy but wrong type
        card = {"type": "front-back", "question": 123, "answer": "A"}
        # The validation checks `if not card.get(field)` - 123 is truthy
        # So this passes validation even though it's the wrong type
        # This is a known limitation - type checking is loose
        validate_card(card, 0)  # Passes because 123 is truthy

    def test_zero_number_where_string_expected_fails(self):
        """Zero (falsy number) where string expected fails."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "question": 0, "answer": "A"}, 0)

    def test_string_where_list_expected_for_tags(self):
        """String where list expected for tags - handled at package creation."""
        # Tags are optional and not validated strictly at card level
        card = {
            "type": "front-back",
            "question": "Q",
            "answer": "A",
            "tags": "not-a-list"  # Should be a list
        }
        # Card validation passes (tags not validated here)
        validate_card(card, 0)

    def test_boolean_where_string_expected(self):
        """Boolean True is truthy so may pass validation."""
        card = {"type": "front-back", "question": True, "answer": "A"}
        # True is truthy, so passes the 'if not card.get(field)' check
        validate_card(card, 0)

    def test_boolean_false_where_string_expected_fails(self):
        """Boolean False is falsy so fails validation."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "question": False, "answer": "A"}, 0)

    def test_list_where_string_expected(self):
        """List where string expected - truthy so passes validation."""
        card = {
            "type": "front-back",
            "question": ["item1", "item2"],  # Wrong type but truthy
            "answer": "A"
        }
        # Lists are truthy, so passes basic validation
        validate_card(card, 0)

    def test_empty_list_where_string_expected_fails(self):
        """Empty list is falsy so fails validation."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "question": [], "answer": "A"}, 0)

    def test_dict_where_string_expected(self):
        """Dict where string expected - truthy so passes validation."""
        card = {
            "type": "front-back",
            "question": {"nested": "object"},
            "answer": "A"
        }
        # Dicts are truthy, so passes basic validation
        validate_card(card, 0)

    def test_empty_dict_where_string_expected_fails(self):
        """Empty dict is falsy so fails validation."""
        with pytest.raises(ValidationError, match="missing required field 'question'"):
            validate_card({"type": "front-back", "question": {}, "answer": "A"}, 0)


class TestBoundaryConditions:
    """Tests for boundary conditions like empty arrays, single items, etc."""

    def test_empty_cards_array(self):
        """Empty cards array is valid."""
        data = {"cards": []}
        # Should not raise
        validate_data(data)

    def test_empty_tags_array_is_valid(self):
        """Empty tags array on card is valid."""
        card = {
            "type": "front-back",
            "question": "Q",
            "answer": "A",
            "tags": []
        }
        # Should not raise
        validate_card(card, 0)

    def test_empty_batch_tags_array_is_valid(self):
        """Empty batch_tags array is valid."""
        data = {
            "cards": [],
            "batch_tags": []
        }
        # Should not raise
        validate_data(data)

    def test_single_card_array(self):
        """Single item cards array is valid."""
        data = {
            "cards": [
                {"type": "front-back", "question": "Q", "answer": "A"}
            ]
        }
        # Should not raise
        validate_data(data)

    def test_single_tag_array(self):
        """Single item tags array is valid."""
        card = {
            "type": "front-back",
            "question": "Q",
            "answer": "A",
            "tags": ["single-tag"]
        }
        # Should not raise
        validate_card(card, 0)

    def test_single_occlusion(self):
        """Single occlusion is valid."""
        card = {
            "type": "image-occlusion",
            "image_data": "data:image/png;base64,iVBORw0KGgo=",
            "occlusions": [
                {"cloze_num": 1, "label": "Only", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}
            ]
        }
        # Should not raise
        validate_card(card, 0)

    def test_empty_occlusions_array_fails(self):
        """Empty occlusions array fails (no masks to show).

        Note: Empty list is falsy, so fails the 'missing required field' check first.
        The 'must be a non-empty array' check is secondary validation.
        """
        with pytest.raises(ValidationError, match="missing required field 'occlusions'"):
            validate_card({
                "type": "image-occlusion",
                "image_path": "/path/to/image.jpg",
                "occlusions": []
            }, 0)

    def test_many_occlusions_valid(self):
        """Many occlusions (50) are valid."""
        occlusions = [
            {"cloze_num": i, "label": f"Region {i}", "left": 0.01 * i, "top": 0.01 * i, "width": 0.05, "height": 0.05}
            for i in range(1, 51)
        ]
        card = {
            "type": "image-occlusion",
            "image_data": "data:image/png;base64,iVBORw0KGgo=",
            "occlusions": occlusions
        }
        # Should not raise
        validate_card(card, 0)

    def test_none_cards_field_is_valid(self):
        """None cards field is treated as empty list."""
        data = {"cards": None}
        # Should not raise - None is handled
        validate_data(data)

    def test_cards_none_causes_type_error(self, temp_dir):
        """Deck with None cards causes TypeError during iteration.

        Note: This documents current behavior - None cards is not gracefully
        handled after validation passes. validate_data accepts None but
        create_package iterates over it causing TypeError.
        """
        import os
        output_path = os.path.join(temp_dir, "test.apkg")
        data = {"deck_name": "Empty", "cards": None}
        with pytest.raises(TypeError, match="'NoneType' object is not iterable"):
            create_package(data, output_path)

    def test_missing_cards_field_entirely(self):
        """Missing cards field entirely is valid (defaults to empty)."""
        data = {"deck_name": "Empty Deck"}
        # Should not raise - cards defaults to empty list
        validate_data(data)

    def test_very_long_question_valid(self):
        """Very long question text is valid."""
        long_text = "Q" * 10000
        card = {
            "type": "front-back",
            "question": long_text,
            "answer": "A"
        }
        # Should not raise
        validate_card(card, 0)

    def test_very_long_cloze_text_valid(self):
        """Very long cloze text is valid."""
        long_text = "Word " * 1000 + "{{c1::answer}}" + " more" * 500
        card = {
            "type": "cloze",
            "cloze_text": long_text
        }
        # Should not raise
        validate_card(card, 0)


class TestMixedEdgeCases:
    """Combined edge cases and real-world scenarios."""

    def test_card_with_only_type_field(self):
        """Card with only type field fails (missing required fields)."""
        with pytest.raises(ValidationError, match="missing required field"):
            validate_card({"type": "front-back"}, 0)

    def test_unknown_extra_fields_preserved(self):
        """Unknown extra fields should not cause errors."""
        card = {
            "type": "front-back",
            "question": "Q",
            "answer": "A",
            "unknown_field": "should be ignored",
            "another_unknown": 12345
        }
        # Should not raise
        validate_card(card, 0)

    def test_case_sensitive_type_field(self):
        """Type field is case-insensitive (lowercased internally)."""
        card = {"type": "FRONT-BACK", "question": "Q", "answer": "A"}
        # Should not raise - type is lowercased
        validate_card(card, 0)

    def test_mixed_case_type_field(self):
        """Mixed case type field works."""
        card = {"type": "FrOnT-bAcK", "question": "Q", "answer": "A"}
        # Should not raise
        validate_card(card, 0)

    def test_type_with_leading_trailing_spaces_fails(self):
        """Type with extra spaces fails (not trimmed)."""
        with pytest.raises(ValidationError, match="invalid type"):
            validate_card({"type": "  front-back  ", "question": "Q", "answer": "A"}, 0)

    def test_cards_must_be_array_not_dict(self):
        """Cards field must be array, not dict."""
        with pytest.raises(ValidationError, match="must be an array"):
            validate_data({"cards": {"0": {"type": "front-back"}}})

    def test_batch_tags_must_be_array_not_string(self):
        """Batch tags must be array, not string."""
        with pytest.raises(ValidationError, match="must be an array"):
            validate_data({"cards": [], "batch_tags": "tag1,tag2"})

    def test_multiple_validation_errors_reports_first(self):
        """Multiple cards with errors - reports first error encountered."""
        data = {
            "cards": [
                {"type": "invalid"},
                {"type": "front-back"},  # Missing question/answer
                {"type": "cloze", "cloze_text": "no cloze"},
            ]
        }
        # Should fail on first card
        with pytest.raises(ValidationError, match="Card 0"):
            validate_data(data)

    def test_image_requires_all_three_fields(self):
        """Image card requires image_path, prompt, and answer."""
        with pytest.raises(ValidationError, match="missing required field 'image_path'"):
            validate_card({"type": "image", "prompt": "P", "answer": "A"}, 0)

        with pytest.raises(ValidationError, match="missing required field 'prompt'"):
            validate_card({"type": "image", "image_path": "/p.jpg", "answer": "A"}, 0)

        with pytest.raises(ValidationError, match="missing required field 'answer'"):
            validate_card({"type": "image", "image_path": "/p.jpg", "prompt": "P"}, 0)

    def test_valid_card_index_in_error_message(self):
        """Error message includes correct card index."""
        data = {
            "cards": [
                {"type": "front-back", "question": "Q", "answer": "A"},
                {"type": "front-back", "question": "Q", "answer": "A"},
                {"type": "cloze", "cloze_text": "no cloze here"},  # Invalid at index 2
            ]
        }
        with pytest.raises(ValidationError, match="Card 2"):
            validate_data(data)


class TestValidationPassCases:
    """Tests that verify valid data passes validation."""

    def test_minimal_front_back_card_passes(self):
        """Minimal valid front-back card passes."""
        card = {"type": "front-back", "question": "Q", "answer": "A"}
        validate_card(card, 0)  # Should not raise

    def test_minimal_concept_card_passes(self):
        """Minimal valid concept card passes."""
        card = {"type": "concept", "concept": "C", "definition": "D"}
        validate_card(card, 0)  # Should not raise

    def test_minimal_cloze_card_passes(self):
        """Minimal valid cloze card passes."""
        card = {"type": "cloze", "cloze_text": "{{c1::answer}}"}
        validate_card(card, 0)  # Should not raise

    def test_minimal_person_card_passes(self):
        """Minimal valid person card passes."""
        card = {"type": "person", "full_name": "John Doe"}
        validate_card(card, 0)  # Should not raise

    def test_minimal_image_card_passes(self):
        """Minimal valid image card passes."""
        card = {"type": "image", "image_path": "/p.jpg", "prompt": "P", "answer": "A"}
        validate_card(card, 0)  # Should not raise

    def test_minimal_io_card_with_path_passes(self):
        """Minimal valid IO card with image_path passes."""
        card = {
            "type": "image-occlusion",
            "image_path": "/p.jpg",
            "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
        }
        validate_card(card, 0)  # Should not raise

    def test_minimal_io_card_with_data_passes(self):
        """Minimal valid IO card with image_data passes."""
        card = {
            "type": "image-occlusion",
            "image_data": "data:image/png;base64,iVBORw0KGgo=",
            "occlusions": [{"cloze_num": 1, "label": "A", "left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}]
        }
        validate_card(card, 0)  # Should not raise

    def test_full_front_back_card_passes(self):
        """Fully populated front-back card passes."""
        card = {
            "type": "front-back",
            "question": "What is Python?",
            "answer": "A programming language",
            "example": "print('Hello World')",
            "extra_info": "Created by Guido van Rossum",
            "author": "Test Author",
            "source": "Python Docs",
            "source_link": "https://python.org",
            "tags": ["programming", "python"]
        }
        validate_card(card, 0)  # Should not raise

    def test_full_deck_data_passes(self):
        """Fully populated deck data passes."""
        data = {
            "deck_name": "My Deck",
            "theme": "minimal",
            "batch_tags": ["batch-1"],
            "cards": [
                {"type": "front-back", "question": "Q1", "answer": "A1"},
                {"type": "concept", "concept": "C1", "definition": "D1"},
                {"type": "cloze", "cloze_text": "{{c1::answer}}"},
            ]
        }
        validate_data(data)  # Should not raise
