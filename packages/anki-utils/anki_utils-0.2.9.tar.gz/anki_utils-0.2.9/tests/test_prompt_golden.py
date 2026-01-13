"""Golden example tests for card structure validation.

These tests verify that the JSON -> card pipeline produces correct structure.
They are deterministic (no LLM variance) and focus on structural correctness,
not content quality.

Test cases are defined in tests/fixtures/golden_prompts.json.
"""

import json
import os
from pathlib import Path

import pytest

from anki_utils.exporter import (
    ValidationError,
    count_cloze_deletions,
    count_person_cards,
    create_package,
    validate_card,
    validate_data,
)


def load_golden_examples():
    """Load golden example test cases from JSON fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "golden_prompts.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["golden_examples"]


# Load examples at module level for parametrization
GOLDEN_EXAMPLES = load_golden_examples()


def get_example_ids():
    """Generate test IDs from example names."""
    return [ex["name"] for ex in GOLDEN_EXAMPLES]


class TestGoldenExampleValidation:
    """Tests that verify validation behavior matches golden examples."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("validation_passes", True)],
        ids=lambda ex: ex["name"],
    )
    def test_valid_examples_pass_validation(self, example):
        """Valid golden examples should pass validation without errors."""
        card = example["input_json"]

        # Should not raise
        validate_card(card, 0)

        # Full data validation should also pass
        data = {"cards": [card]}
        validate_data(data)

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if not ex["expected"].get("validation_passes", True)],
        ids=lambda ex: ex["name"],
    )
    def test_invalid_examples_fail_validation(self, example):
        """Invalid golden examples should fail with expected error message."""
        card = example["input_json"]
        expected_error = example["expected"].get("error_contains", "")

        with pytest.raises(ValidationError, match=expected_error):
            validate_card(card, 0)


class TestGoldenExampleCardType:
    """Tests that verify correct card type detection."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("card_type")],
        ids=lambda ex: ex["name"],
    )
    def test_card_type_matches_expected(self, example):
        """Card type should match the expected type from golden example."""
        card = example["input_json"]
        expected_type = example["expected"]["card_type"]

        actual_type = card.get("type", "").lower()
        assert actual_type == expected_type, (
            f"Expected card type '{expected_type}', got '{actual_type}'"
        )


class TestGoldenExampleRequiredFields:
    """Tests that verify required fields are present."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("required_fields_present")],
        ids=lambda ex: ex["name"],
    )
    def test_required_fields_present(self, example):
        """All required fields should be present in the card."""
        card = example["input_json"]
        required_fields = example["expected"]["required_fields_present"]

        missing_fields = []
        for field in required_fields:
            if field not in card or not card[field]:
                missing_fields.append(field)

        assert not missing_fields, (
            f"Missing required fields: {missing_fields}"
        )


class TestGoldenExampleOptionalFields:
    """Tests that verify optional fields are handled correctly."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("optional_fields_present")],
        ids=lambda ex: ex["name"],
    )
    def test_optional_fields_present(self, example):
        """Optional fields specified in expected should be present."""
        card = example["input_json"]
        optional_fields = example["expected"]["optional_fields_present"]

        missing_fields = []
        for field in optional_fields:
            if field not in card:
                missing_fields.append(field)

        assert not missing_fields, (
            f"Expected optional fields missing: {missing_fields}"
        )


class TestGoldenExampleCardCounts:
    """Tests that verify correct card count generation."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("cards_generated") is not None],
        ids=lambda ex: ex["name"],
    )
    def test_card_count_matches_expected(self, example, temp_dir):
        """Number of cards generated should match expected count."""
        card = example["input_json"]
        expected_cards = example["expected"]["cards_generated"]

        # Skip cards that won't pass validation (they're tested separately)
        if not example["expected"].get("validation_passes", True):
            pytest.skip("Skipping invalid card")

        # Skip image cards that need real files
        if card.get("type") == "image":
            pytest.skip("Image cards need real files for full export")

        # Calculate expected card count based on card type
        card_type = card.get("type", "").lower()

        if card_type == "front-back":
            calculated_cards = 1
        elif card_type == "concept":
            calculated_cards = 2  # Bidirectional
        elif card_type == "cloze":
            calculated_cards = count_cloze_deletions(card.get("cloze_text", ""))
        elif card_type == "person":
            calculated_cards = count_person_cards(card)
        elif card_type == "image":
            calculated_cards = 1
        elif card_type == "image-occlusion":
            calculated_cards = len(card.get("occlusions", []))
        else:
            calculated_cards = 0

        assert calculated_cards == expected_cards, (
            f"Expected {expected_cards} cards, calculated {calculated_cards}"
        )


class TestGoldenExampleClozeSyntax:
    """Tests that verify cloze syntax handling."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("cloze_count") is not None],
        ids=lambda ex: ex["name"],
    )
    def test_cloze_count_matches_expected(self, example):
        """Number of cloze deletions should match expected count."""
        card = example["input_json"]
        expected_count = example["expected"]["cloze_count"]

        cloze_text = card.get("cloze_text", "")
        actual_count = count_cloze_deletions(cloze_text)

        assert actual_count == expected_count, (
            f"Expected {expected_count} cloze deletions, got {actual_count}"
        )


class TestGoldenExampleTags:
    """Tests that verify tag handling."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("tags_applied")],
        ids=lambda ex: ex["name"],
    )
    def test_tags_applied_correctly(self, example, temp_dir):
        """Tags should be properly applied including batch tags."""
        card = example["input_json"]
        expected_tags = set(example["expected"]["tags_applied"])
        batch_tags = example.get("batch_tags", [])

        # Skip cards that won't pass validation
        if not example["expected"].get("validation_passes", True):
            pytest.skip("Skipping invalid card")

        # Skip image cards that need real files
        if card.get("type") == "image":
            pytest.skip("Image cards need real files for full export")

        # Get card tags and batch tags
        card_tags = set(card.get("tags", []))
        batch_tag_set = set(batch_tags)

        # Combined tags should match expected
        actual_tags = card_tags | batch_tag_set

        assert actual_tags == expected_tags, (
            f"Expected tags {expected_tags}, got {actual_tags}"
        )


class TestGoldenExampleTheme:
    """Tests that verify theme handling."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("theme_applied")],
        ids=lambda ex: ex["name"],
    )
    def test_theme_applied_correctly(self, example, temp_dir):
        """Theme should be applied to generated package."""
        card = example["input_json"]
        expected_theme = example["expected"]["theme_applied"]
        theme = example.get("theme", "minimal")

        output_path = os.path.join(temp_dir, "test_theme.apkg")
        data = {
            "deck_name": "Theme Test",
            "theme": theme,
            "cards": [card],
        }

        result = create_package(data, output_path)

        assert result["theme"] == expected_theme, (
            f"Expected theme '{expected_theme}', got '{result['theme']}'"
        )


class TestGoldenExampleExportIntegration:
    """Integration tests that verify full export pipeline."""

    @pytest.mark.parametrize(
        "example",
        [
            ex for ex in GOLDEN_EXAMPLES
            if ex["expected"].get("validation_passes", True)
            and ex["expected"].get("card_type") not in ["image", "image-occlusion"]
        ],
        ids=lambda ex: ex["name"],
    )
    def test_valid_example_exports_successfully(self, example, temp_dir):
        """Valid golden examples should export to .apkg without errors."""
        card = example["input_json"]
        batch_tags = example.get("batch_tags", [])
        theme = example.get("theme", "minimal")

        output_path = os.path.join(temp_dir, f"{example['name']}.apkg")
        data = {
            "deck_name": f"Golden Test: {example['name']}",
            "theme": theme,
            "batch_tags": batch_tags,
            "cards": [card],
        }

        result = create_package(data, output_path)

        # File should exist
        assert os.path.exists(output_path), "Package file was not created"

        # Should have correct note count
        card_type = card.get("type", "").lower()
        if card_type in ["front-back", "concept", "cloze", "person"]:
            assert result["total_notes"] == 1, f"Expected 1 note, got {result['total_notes']}"

        # Card count should match expected
        expected_cards = example["expected"].get("cards_generated")
        if expected_cards is not None:
            assert result["total_cards"] == expected_cards, (
                f"Expected {expected_cards} cards, got {result['total_cards']}"
            )


class TestGoldenExampleMarkdown:
    """Tests that verify markdown handling."""

    @pytest.mark.parametrize(
        "example",
        [ex for ex in GOLDEN_EXAMPLES if ex["expected"].get("contains_markdown")],
        ids=lambda ex: ex["name"],
    )
    def test_markdown_fields_detected(self, example):
        """Cards with markdown should be identified correctly."""
        card = example["input_json"]

        # Check if any text field contains markdown syntax
        markdown_indicators = ["**", "*", "`", "```", "#", "- ", "1. ", "[", "!["]

        has_markdown = False
        text_fields = ["question", "answer", "definition", "concept", "cloze_text", "example", "extra_info"]

        for field in text_fields:
            value = card.get(field, "")
            if isinstance(value, str):
                for indicator in markdown_indicators:
                    if indicator in value:
                        has_markdown = True
                        break
            if has_markdown:
                break

        assert has_markdown, "Expected markdown content but none found"


class TestGoldenExampleCompleteness:
    """Tests to ensure golden examples cover all card types and scenarios."""

    def test_all_card_types_have_examples(self):
        """Every supported card type should have at least one golden example."""
        required_types = {"front-back", "concept", "cloze", "person", "image"}

        covered_types = set()
        for example in GOLDEN_EXAMPLES:
            if example["expected"].get("card_type"):
                covered_types.add(example["expected"]["card_type"])

        missing_types = required_types - covered_types
        assert not missing_types, f"Missing golden examples for card types: {missing_types}"

    def test_minimum_example_count(self):
        """Should have at least 10 golden examples as per issue requirements."""
        assert len(GOLDEN_EXAMPLES) >= 10, (
            f"Expected at least 10 golden examples, got {len(GOLDEN_EXAMPLES)}"
        )

    def test_has_valid_and_invalid_examples(self):
        """Should have both valid and invalid examples for validation testing."""
        valid_count = sum(
            1 for ex in GOLDEN_EXAMPLES
            if ex["expected"].get("validation_passes", True)
        )
        invalid_count = sum(
            1 for ex in GOLDEN_EXAMPLES
            if not ex["expected"].get("validation_passes", True)
        )

        assert valid_count > 0, "No valid examples found"
        assert invalid_count > 0, "No invalid examples found (for error testing)"

    def test_examples_have_descriptions(self):
        """Every golden example should have a description for clarity."""
        missing_descriptions = []
        for example in GOLDEN_EXAMPLES:
            if not example.get("description"):
                missing_descriptions.append(example["name"])

        assert not missing_descriptions, (
            f"Examples missing descriptions: {missing_descriptions}"
        )
