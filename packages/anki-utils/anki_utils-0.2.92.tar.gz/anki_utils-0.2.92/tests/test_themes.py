"""Tests for theme system."""

import pytest
from anki_utils.themes import (
    THEMES,
    DEFAULT_THEME,
    THEME_OFFSETS,
    THEME_NAMES,
    get_theme_model_id,
    get_theme_model_name,
    get_front_back_css,
    get_concept_css,
    get_cloze_css,
    get_image_css,
    get_person_css,
    get_image_occlusion_css,
    get_theme_sections,
)


class TestThemeConstants:
    """Test theme constant definitions."""

    def test_themes_list_has_four_themes(self):
        """Verify all expected themes are defined."""
        assert len(THEMES) == 4
        assert "minimal" in THEMES
        assert "classic" in THEMES
        assert "high-contrast" in THEMES
        assert "calm" in THEMES

    def test_default_theme_is_minimal(self):
        """Verify default theme is minimal."""
        assert DEFAULT_THEME == "minimal"

    def test_theme_offsets_defined(self):
        """Verify each theme has an offset."""
        for theme in THEMES:
            assert theme in THEME_OFFSETS

    def test_theme_offsets_are_unique(self):
        """Verify theme offsets don't collide."""
        offsets = list(THEME_OFFSETS.values())
        assert len(offsets) == len(set(offsets))


class TestGetThemeModelId:
    """Tests for get_theme_model_id function."""

    def test_minimal_theme_no_offset(self):
        """Minimal theme should have no offset."""
        base_id = 1000000
        result = get_theme_model_id(base_id, "minimal")
        assert result == base_id

    def test_classic_theme_adds_offset(self):
        """Classic theme should add 100 offset."""
        base_id = 1000000
        result = get_theme_model_id(base_id, "classic")
        assert result == base_id + 100

    def test_high_contrast_theme_adds_offset(self):
        """High-contrast theme should add 200 offset."""
        base_id = 1000000
        result = get_theme_model_id(base_id, "high-contrast")
        assert result == base_id + 200

    def test_calm_theme_adds_offset(self):
        """Calm theme should add 300 offset."""
        base_id = 1000000
        result = get_theme_model_id(base_id, "calm")
        assert result == base_id + 300

    def test_unknown_theme_no_offset(self):
        """Unknown theme should default to no offset."""
        base_id = 1000000
        result = get_theme_model_id(base_id, "unknown")
        assert result == base_id


class TestGetThemeModelName:
    """Tests for get_theme_model_name function."""

    def test_minimal_theme_no_suffix(self):
        """Minimal theme should have no suffix."""
        result = get_theme_model_name("Base Name", "minimal")
        assert result == "Base Name"

    def test_classic_theme_adds_suffix(self):
        """Classic theme should add (Classic) suffix."""
        result = get_theme_model_name("Base Name", "classic")
        assert result == "Base Name (Classic)"

    def test_high_contrast_theme_adds_suffix(self):
        """High-contrast theme should add (High Contrast) suffix."""
        result = get_theme_model_name("Base Name", "high-contrast")
        assert result == "Base Name (High Contrast)"

    def test_calm_theme_adds_suffix(self):
        """Calm theme should add (Calm) suffix."""
        result = get_theme_model_name("Base Name", "calm")
        assert result == "Base Name (Calm)"


class TestCssGetters:
    """Tests for CSS getter functions."""

    @pytest.mark.parametrize("theme", THEMES)
    def test_get_front_back_css_returns_string(self, theme):
        """All themes return non-empty CSS for front-back."""
        result = get_front_back_css(theme)
        assert isinstance(result, str)
        assert len(result) > 100  # Should be substantial CSS

    @pytest.mark.parametrize("theme", THEMES)
    def test_get_concept_css_returns_string(self, theme):
        """All themes return non-empty CSS for concept."""
        result = get_concept_css(theme)
        assert isinstance(result, str)
        assert len(result) > 100
        # Concept should include instruction styling
        assert "concept-instruction" in result

    @pytest.mark.parametrize("theme", THEMES)
    def test_get_cloze_css_returns_string(self, theme):
        """All themes return non-empty CSS for cloze."""
        result = get_cloze_css(theme)
        assert isinstance(result, str)
        assert len(result) > 100
        # Cloze should have cloze styling
        assert ".cloze" in result

    @pytest.mark.parametrize("theme", THEMES)
    def test_get_image_css_returns_string(self, theme):
        """All themes return non-empty CSS for image."""
        result = get_image_css(theme)
        assert isinstance(result, str)
        assert len(result) > 100
        # Image should have image-container styling
        assert "image-container" in result

    @pytest.mark.parametrize("theme", THEMES)
    def test_get_person_css_returns_string(self, theme):
        """All themes return non-empty CSS for person."""
        result = get_person_css(theme)
        assert isinstance(result, str)
        assert len(result) > 50

    @pytest.mark.parametrize("theme", THEMES)
    def test_get_image_occlusion_css_returns_string(self, theme):
        """All themes return non-empty CSS for image occlusion."""
        result = get_image_occlusion_css(theme)
        assert isinstance(result, str)
        assert len(result) > 100
        # IO should have io-specific classes
        assert "io-container" in result

    @pytest.mark.parametrize("theme", THEMES)
    def test_css_includes_dark_mode(self, theme):
        """All themes should include dark mode styles."""
        result = get_front_back_css(theme)
        assert "night_mode" in result


class TestGetThemeSections:
    """Tests for get_theme_sections function."""

    @pytest.mark.parametrize("theme", THEMES)
    def test_returns_all_sections(self, theme):
        """All themes should return all expected sections."""
        result = get_theme_sections(theme)
        assert "base" in result
        assert "conceptInstruction" in result
        assert "image" in result
        assert "person" in result
        assert "io" in result

    @pytest.mark.parametrize("theme", THEMES)
    def test_sections_are_strings(self, theme):
        """All sections should be strings."""
        result = get_theme_sections(theme)
        for key, value in result.items():
            assert isinstance(value, str), f"{key} should be a string"


class TestPreviewTemplateContract:
    """
    Tests that verify the contract between themes.py and preview-template.jsx.

    The preview-template.jsx uses THEME_CSS injected via `anki-utils themes --all-json`.
    The JSX's getCardCSS() function expects specific keys in each theme object.
    These tests ensure any changes to themes.py structure don't break the preview.

    See: anki_utils/assets/preview-template.jsx, getCardCSS function (lines 37-51)
    """

    # These are the exact keys that preview-template.jsx's getCardCSS() accesses
    EXPECTED_SECTION_KEYS = {"base", "conceptInstruction", "image", "person", "io"}

    @pytest.mark.parametrize("theme", THEMES)
    def test_theme_sections_match_preview_contract(self, theme):
        """
        Verify get_theme_sections() returns exactly the keys preview-template.jsx expects.

        If this test fails, preview-template.jsx's getCardCSS() will break because
        it accesses these specific keys: t.base, t.conceptInstruction, t.image, t.person, t.io
        """
        result = get_theme_sections(theme)
        actual_keys = set(result.keys())

        assert actual_keys == self.EXPECTED_SECTION_KEYS, (
            f"Theme '{theme}' sections don't match preview-template.jsx contract.\n"
            f"Expected keys: {self.EXPECTED_SECTION_KEYS}\n"
            f"Actual keys: {actual_keys}\n"
            f"Missing: {self.EXPECTED_SECTION_KEYS - actual_keys}\n"
            f"Extra: {actual_keys - self.EXPECTED_SECTION_KEYS}"
        )

    def test_all_themes_have_consistent_structure(self):
        """Verify all themes have identical key structure."""
        structures = {}
        for theme in THEMES:
            structures[theme] = set(get_theme_sections(theme).keys())

        first_theme = THEMES[0]
        first_structure = structures[first_theme]

        for theme in THEMES[1:]:
            assert structures[theme] == first_structure, (
                f"Theme '{theme}' has different structure than '{first_theme}'.\n"
                f"{first_theme}: {first_structure}\n"
                f"{theme}: {structures[theme]}"
            )

    @pytest.mark.parametrize("theme", THEMES)
    def test_sections_contain_css_selectors(self, theme):
        """Verify each section contains valid CSS (has selectors)."""
        sections = get_theme_sections(theme)

        # Base should have body styles
        assert "body" in sections["base"], f"{theme} base missing body selector"

        # conceptInstruction should have the .concept-instruction class
        assert ".concept-instruction" in sections["conceptInstruction"], (
            f"{theme} conceptInstruction missing .concept-instruction selector"
        )

        # image should have image-related selectors
        assert ".image-container" in sections["image"], (
            f"{theme} image missing .image-container selector"
        )

        # person should have .card selector
        assert ".card" in sections["person"], (
            f"{theme} person missing .card selector"
        )

        # io should have image occlusion selectors
        assert ".io-container" in sections["io"], (
            f"{theme} io missing .io-container selector"
        )

    def test_cli_themes_output_matches_get_theme_sections(self):
        """
        Verify `anki-utils themes --all-json` output matches get_theme_sections().

        This ensures the CLI command (used to inject CSS into preview-template.jsx)
        produces the same structure as the Python API.
        """
        import json
        import subprocess

        # Get CLI output
        result = subprocess.run(
            ["anki-utils", "themes", "--all-json"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        cli_output = json.loads(result.stdout)

        # Compare with Python API for each theme
        for theme in THEMES:
            python_sections = get_theme_sections(theme)
            cli_sections = cli_output.get(theme, {})

            # Keys should match
            assert set(python_sections.keys()) == set(cli_sections.keys()), (
                f"Theme '{theme}' CLI output keys don't match Python API"
            )

            # Values should match (exact CSS content)
            for key in python_sections:
                assert python_sections[key] == cli_sections[key], (
                    f"Theme '{theme}' section '{key}' differs between CLI and Python API"
                )
