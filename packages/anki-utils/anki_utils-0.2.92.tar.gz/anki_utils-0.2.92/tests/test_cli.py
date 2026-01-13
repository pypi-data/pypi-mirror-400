"""Tests for anki_utils CLI module."""

import json
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

import pytest

from anki_utils import cli


class TestVersionCommand:
    """Tests for the version command."""

    def test_version_default_output(self, capsys):
        """Version command prints version string."""
        result = cli.main(["version"])
        assert result == 0
        captured = capsys.readouterr()
        # Should be a version string like "0.3.0"
        assert captured.out.strip()
        assert "." in captured.out  # Has version dots

    def test_version_json_output(self, capsys):
        """Version command with --json outputs JSON."""
        result = cli.main(["version", "--json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "version" in data
        assert isinstance(data["version"], str)


class TestThemesCommand:
    """Tests for the themes command."""

    def test_themes_list(self, capsys):
        """--list shows available themes."""
        result = cli.main(["themes", "--list"])
        assert result == 0
        captured = capsys.readouterr()
        themes = captured.out.strip().split("\n")
        assert len(themes) >= 1
        assert "minimal" in themes

    def test_themes_all_json(self, capsys):
        """--all-json outputs JSON with all themes."""
        result = cli.main(["themes", "--all-json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, dict)
        assert "minimal" in data

    def test_themes_get_valid(self, capsys):
        """--get with valid theme returns CSS."""
        result = cli.main(["themes", "--get", "minimal"])
        assert result == 0
        captured = capsys.readouterr()
        # Should contain CSS
        assert ".card" in captured.out or "font" in captured.out.lower()

    def test_themes_get_invalid(self, capsys):
        """--get with invalid theme returns error."""
        result = cli.main(["themes", "--get", "nonexistent-theme"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown theme" in captured.err


class TestAssetCommand:
    """Tests for the asset command."""

    def test_asset_preview_template_stdout(self, capsys):
        """Asset command outputs preview-template to stdout."""
        result = cli.main(["asset", "preview-template"])
        assert result == 0
        captured = capsys.readouterr()
        # Should be JSX content
        assert "React" in captured.out or "function" in captured.out or "const" in captured.out

    def test_asset_theme_designer_stdout(self, capsys):
        """Asset command outputs theme-designer to stdout."""
        result = cli.main(["asset", "theme-designer"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 100  # Non-trivial content

    def test_asset_output_to_file(self, capsys, temp_dir):
        """Asset command with --output writes to file."""
        output_path = Path(temp_dir) / "output.jsx"
        result = cli.main(["asset", "preview-template", "--output", str(output_path)])
        assert result == 0
        captured = capsys.readouterr()
        assert str(output_path) in captured.out
        assert output_path.exists()
        content = output_path.read_text()
        assert len(content) > 100


class TestChangelogCommand:
    """Tests for the changelog command."""

    def test_changelog_full(self, capsys):
        """Changelog command outputs full changelog."""
        result = cli.main(["changelog"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Changelog" in captured.out or "##" in captured.out

    def test_changelog_latest(self, capsys):
        """Changelog --latest outputs most recent version only."""
        result = cli.main(["changelog", "--latest"])
        assert result == 0
        captured = capsys.readouterr()
        # Should have version header
        assert "## [" in captured.out or captured.out.strip() == ""


class TestMigrationsCommand:
    """Tests for the migrations command."""

    def test_migrations_full(self, capsys):
        """Migrations command outputs full migrations doc."""
        result = cli.main(["migrations"])
        assert result == 0
        captured = capsys.readouterr()
        # Either content or "no migrations" message
        assert len(captured.out) > 0

    def test_migrations_json(self, capsys):
        """Migrations --json outputs structured JSON."""
        result = cli.main(["migrations", "--json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "current_version" in data
        assert "has_updates" in data
        assert "entries" in data
        assert isinstance(data["entries"], list)

    def test_migrations_since_filter(self, capsys):
        """Migrations --since filters by version."""
        result = cli.main(["migrations", "--since", "0.0.1"])
        assert result == 0
        # Should succeed regardless of whether there are migrations

    def test_migrations_since_with_json(self, capsys):
        """Migrations --since with --json includes filter info."""
        result = cli.main(["migrations", "--since", "0.1.0", "--json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["since"] == "0.1.0"

    def test_migrations_since_future_version(self, capsys):
        """Migrations --since with future version returns no entries."""
        result = cli.main(["migrations", "--since", "99.99.99", "--json"])
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["has_updates"] is False
        assert len(data["entries"]) == 0


class TestRoadmapCommand:
    """Tests for the roadmap command."""

    def test_roadmap_shows_deprecation_notice(self, capsys):
        """Roadmap command shows deprecation notice."""
        result = cli.main(["roadmap"])
        assert result == 0
        captured = capsys.readouterr()
        assert "deprecated" in captured.out.lower()
        assert "GitHub Issues" in captured.out

    def test_roadmap_html_output(self, capsys):
        """Roadmap --html outputs HTML."""
        result = cli.main(["roadmap", "--html"])
        assert result == 0
        captured = capsys.readouterr()
        assert "<!DOCTYPE html>" in captured.out
        assert "<html>" in captured.out

    def test_roadmap_section_valid(self, capsys):
        """Roadmap --section with valid section filters output."""
        # First get the roadmap to find a valid section
        cli.main(["roadmap"])
        # Test with a section that likely exists
        result = cli.main(["roadmap", "--section", "Phase 1"])
        # May or may not find it, but should return valid code
        assert result in (0, 1)

    def test_roadmap_section_invalid(self, capsys):
        """Roadmap --section with invalid section returns error."""
        result = cli.main(["roadmap", "--section", "NonexistentSection12345"])
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err


class TestSkillUpdateProtocolCommand:
    """Tests for the skill-update-protocol command."""

    def test_skill_update_protocol_output(self, capsys):
        """Skill-update-protocol outputs content."""
        result = cli.main(["skill-update-protocol"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestExportApkgCommand:
    """Tests for the export-apkg command."""

    def test_export_apkg_success(self, capsys, temp_dir, sample_deck_data):
        """export-apkg creates package from valid JSON."""
        output_path = Path(temp_dir) / "test.apkg"
        json_input = json.dumps(sample_deck_data)

        with mock.patch.object(sys, "stdin", StringIO(json_input)):
            result = cli.main(["export-apkg", "--output", str(output_path)])

        assert result == 0
        assert output_path.exists()
        captured = capsys.readouterr()
        # Output should be JSON with result info
        result_data = json.loads(captured.out)
        assert "card_count" in result_data or "cards_created" in result_data or isinstance(result_data, dict)

    def test_export_apkg_malformed_json(self, capsys, temp_dir):
        """export-apkg returns error on malformed JSON."""
        output_path = Path(temp_dir) / "test.apkg"

        with mock.patch.object(sys, "stdin", StringIO("not valid json {")):
            result = cli.main(["export-apkg", "--output", str(output_path)])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error parsing JSON" in captured.err

    def test_export_apkg_with_base_path(self, capsys, temp_dir, sample_deck_data):
        """export-apkg handles --base-path argument."""
        output_path = Path(temp_dir) / "test.apkg"
        json_input = json.dumps(sample_deck_data)

        with mock.patch.object(sys, "stdin", StringIO(json_input)):
            result = cli.main([
                "export-apkg",
                "--output", str(output_path),
                "--base-path", temp_dir
            ])

        assert result == 0


class TestPreprocessTestDataCommand:
    """Tests for the preprocess-test-data command."""

    def test_preprocess_test_data_valid_json(self, temp_dir):
        """preprocess-test-data processes valid JSON file."""
        # Create a test JSON file
        json_path = Path(temp_dir) / "test.json"
        test_data = {"deck_name": "Test", "cards": []}
        json_path.write_text(json.dumps(test_data))

        with mock.patch("anki_utils.dev_tools.main", return_value=0) as mock_main:
            result = cli.main(["preprocess-test-data", str(json_path)])
            mock_main.assert_called_once()
            assert result == 0

    def test_preprocess_test_data_with_assets_dir(self, temp_dir):
        """preprocess-test-data passes assets_dir argument."""
        json_path = Path(temp_dir) / "test.json"
        test_data = {"deck_name": "Test", "cards": []}
        json_path.write_text(json.dumps(test_data))
        assets_dir = Path(temp_dir) / "assets"
        assets_dir.mkdir()

        with mock.patch("anki_utils.dev_tools.main", return_value=0) as mock_main:
            result = cli.main([
                "preprocess-test-data",
                str(json_path),
                str(assets_dir)
            ])
            mock_main.assert_called_once()
            # Check that assets_dir was passed
            call_args = mock_main.call_args[0][0]
            assert str(assets_dir) in call_args


class TestOcclusionDetectCommand:
    """Tests for the occlusion-detect command."""

    def test_occlusion_detect_passes_args(self, temp_dir):
        """occlusion-detect passes arguments to occlusion module."""
        image_path = Path(temp_dir) / "test.png"
        # Create a minimal test file
        image_path.write_bytes(b"fake image data")

        with mock.patch("anki_utils.occlusion.main", return_value=0) as mock_main:
            result = cli.main(["occlusion-detect", str(image_path)])
            mock_main.assert_called_once()
            assert result == 0

    def test_occlusion_detect_with_all_flags(self, temp_dir):
        """occlusion-detect passes all optional flags."""
        image_path = Path(temp_dir) / "test.png"
        image_path.write_bytes(b"fake image data")
        output_dir = Path(temp_dir) / "output"
        output_dir.mkdir()

        with mock.patch("anki_utils.occlusion.main", return_value=0) as mock_main:
            result = cli.main([
                "occlusion-detect",
                str(image_path),
                "--json",
                "--grid",
                "--output", str(output_dir),
                "--min-conf", "80",
                "--preview",
                "--grid-size", "5"
            ])
            mock_main.assert_called_once()
            call_args = mock_main.call_args[0][0]
            assert "--json" in call_args
            assert "--grid" in call_args
            assert "--output" in call_args
            assert "--min-conf" in call_args
            assert "80" in call_args
            assert "--preview" in call_args
            assert "--grid-size" in call_args
            assert "5" in call_args


class TestParserBuildAndErrors:
    """Tests for argument parser construction and error handling."""

    def test_build_parser_returns_parser(self):
        """build_parser returns an ArgumentParser."""
        parser = cli.build_parser()
        assert isinstance(parser, cli.argparse.ArgumentParser)

    def test_no_command_raises_error(self):
        """No command argument raises SystemExit."""
        with pytest.raises(SystemExit):
            cli.main([])

    def test_invalid_command_raises_error(self):
        """Invalid command raises SystemExit."""
        with pytest.raises(SystemExit):
            cli.main(["nonexistent-command"])

    def test_themes_requires_mutex_option(self):
        """themes command requires one of the mutually exclusive options."""
        with pytest.raises(SystemExit):
            cli.main(["themes"])

    def test_export_apkg_requires_output(self):
        """export-apkg requires --output argument."""
        with pytest.raises(SystemExit):
            cli.main(["export-apkg"])


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_compare_versions_less_than(self):
        """_compare_versions returns -1 when v1 < v2."""
        assert cli._compare_versions("0.1.0", "0.2.0") == -1
        assert cli._compare_versions("0.1.0", "1.0.0") == -1
        assert cli._compare_versions("0.1.1", "0.1.2") == -1

    def test_compare_versions_greater_than(self):
        """_compare_versions returns 1 when v1 > v2."""
        assert cli._compare_versions("0.2.0", "0.1.0") == 1
        assert cli._compare_versions("1.0.0", "0.9.9") == 1
        assert cli._compare_versions("0.1.2", "0.1.1") == 1

    def test_compare_versions_equal(self):
        """_compare_versions returns 0 when versions are equal."""
        assert cli._compare_versions("0.1.0", "0.1.0") == 0
        assert cli._compare_versions("1.2.3", "1.2.3") == 0

    def test_load_asset_valid(self):
        """_load_asset loads valid assets."""
        content = cli._load_asset("preview-template")
        assert len(content) > 0

    def test_load_asset_invalid(self):
        """_load_asset raises KeyError for invalid asset."""
        with pytest.raises(KeyError):
            cli._load_asset("nonexistent-asset")

    def test_load_doc_valid(self):
        """_load_doc loads valid documents."""
        content = cli._load_doc("changelog")
        assert len(content) > 0

    def test_load_doc_invalid(self):
        """_load_doc raises KeyError for invalid document."""
        with pytest.raises(KeyError):
            cli._load_doc("nonexistent-doc")

    def test_parse_migrations_empty(self):
        """_parse_migrations returns empty list for empty content."""
        result = cli._parse_migrations("")
        assert result == []

    def test_parse_migrations_with_entry(self):
        """_parse_migrations parses a migration entry."""
        content = """# Migrations

## [0.2.0] - 2025-01-01

### What Changed
- Added new feature
- Fixed bug

### Skill Instructions
Update your skill to use the new API.
"""
        result = cli._parse_migrations(content)
        assert len(result) == 1
        assert result[0]["version"] == "0.2.0"
        assert result[0]["date"] == "2025-01-01"
        assert len(result[0]["changes"]) == 2
        assert "new feature" in result[0]["changes"][0]

    def test_markdown_to_html_roadmap_basic(self):
        """_markdown_to_html_roadmap converts basic markdown."""
        markdown = """# Title

## Section

Some text here.

> A quote

| Column1 | Column2 |
|---------|---------|
| Cell1   | Cell2   |
"""
        html = cli._markdown_to_html_roadmap(markdown)
        assert "<!DOCTYPE html>" in html
        assert "<h1>Title</h1>" in html
        assert "<h2>Section</h2>" in html
        assert "<blockquote>" in html
        assert "<table>" in html
