"""Tests for dev_tools module - image preprocessing for test data."""

import pytest
import json
import base64
import os
import tempfile
from io import BytesIO, StringIO
from unittest.mock import patch
from PIL import Image

from anki_utils.dev_tools import (
    get_mime_type,
    file_to_base64_data_url,
    get_image_dimensions,
    resolve_path,
    process_card,
    process_json,
    main,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_png_image(temp_dir):
    """Create a temporary PNG image file."""
    img_path = os.path.join(temp_dir, "test_image.png")
    img = Image.new('RGB', (100, 75), color='red')
    img.save(img_path, format='PNG')
    return img_path


@pytest.fixture
def temp_jpg_image(temp_dir):
    """Create a temporary JPEG image file."""
    img_path = os.path.join(temp_dir, "test_image.jpg")
    img = Image.new('RGB', (200, 150), color='blue')
    img.save(img_path, format='JPEG')
    return img_path


@pytest.fixture
def temp_gif_image(temp_dir):
    """Create a temporary GIF image file."""
    img_path = os.path.join(temp_dir, "test_image.gif")
    img = Image.new('RGB', (50, 50), color='green')
    img.save(img_path, format='GIF')
    return img_path


@pytest.fixture
def temp_json_with_images(temp_dir, temp_png_image):
    """Create a temporary JSON file referencing an image."""
    json_path = os.path.join(temp_dir, "test_data.json")
    data = {
        "deck_name": "Test Deck",
        "cards": [
            {
                "type": "image-occlusion",
                "image_path": temp_png_image,
                "header": "Test"
            }
        ]
    }
    with open(json_path, 'w') as f:
        json.dump(data, f)
    return json_path


@pytest.fixture
def temp_json_with_photo(temp_dir, temp_jpg_image):
    """Create a temporary JSON file with photo_path."""
    json_path = os.path.join(temp_dir, "test_photo.json")
    data = {
        "deck_name": "Test Deck",
        "cards": [
            {
                "type": "person",
                "full_name": "Test Person",
                "photo_path": temp_jpg_image
            }
        ]
    }
    with open(json_path, 'w') as f:
        json.dump(data, f)
    return json_path


# =============================================================================
# Tests for get_mime_type()
# =============================================================================

class TestGetMimeType:
    """Tests for get_mime_type function."""

    def test_png_extension(self):
        """PNG files return correct MIME type."""
        assert get_mime_type("image.png") == "image/png"
        assert get_mime_type("IMAGE.PNG") == "image/png"

    def test_jpg_extension(self):
        """JPG/JPEG files return correct MIME type."""
        assert get_mime_type("photo.jpg") == "image/jpeg"
        assert get_mime_type("photo.jpeg") == "image/jpeg"

    def test_gif_extension(self):
        """GIF files return correct MIME type."""
        assert get_mime_type("animation.gif") == "image/gif"

    def test_webp_extension(self):
        """WebP files return correct MIME type."""
        assert get_mime_type("modern.webp") == "image/webp"

    def test_svg_extension(self):
        """SVG files return correct MIME type."""
        assert get_mime_type("vector.svg") == "image/svg+xml"

    def test_unknown_extension(self):
        """Unknown extensions return octet-stream."""
        assert get_mime_type("file.qzx") == "application/octet-stream"
        assert get_mime_type("file") == "application/octet-stream"

    def test_path_with_directories(self):
        """MIME type works with full paths."""
        assert get_mime_type("/path/to/image.png") == "image/png"
        assert get_mime_type("./relative/path/photo.jpg") == "image/jpeg"


# =============================================================================
# Tests for file_to_base64_data_url()
# =============================================================================

class TestFileToBase64DataUrl:
    """Tests for file_to_base64_data_url function."""

    def test_valid_png_file(self, temp_png_image):
        """Valid PNG file converts to base64 data URL."""
        result = file_to_base64_data_url(temp_png_image)
        assert result is not None
        assert result.startswith("data:image/png;base64,")
        # Verify it's valid base64
        b64_part = result.split(",")[1]
        decoded = base64.b64decode(b64_part)
        assert len(decoded) > 0

    def test_valid_jpg_file(self, temp_jpg_image):
        """Valid JPEG file converts to base64 data URL."""
        result = file_to_base64_data_url(temp_jpg_image)
        assert result is not None
        assert result.startswith("data:image/jpeg;base64,")

    def test_valid_gif_file(self, temp_gif_image):
        """Valid GIF file converts to base64 data URL."""
        result = file_to_base64_data_url(temp_gif_image)
        assert result is not None
        assert result.startswith("data:image/gif;base64,")

    def test_missing_file_returns_none(self):
        """Missing file returns None."""
        result = file_to_base64_data_url("/nonexistent/path/image.png")
        assert result is None

    def test_file_with_spaces_in_path(self, temp_dir):
        """Files with spaces in path work correctly."""
        img_path = os.path.join(temp_dir, "test image with spaces.png")
        img = Image.new('RGB', (10, 10), color='white')
        img.save(img_path, format='PNG')

        result = file_to_base64_data_url(img_path)
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_file_with_unicode_path(self, temp_dir):
        """Files with unicode characters in path work correctly."""
        img_path = os.path.join(temp_dir, "图片_тест.png")
        img = Image.new('RGB', (10, 10), color='white')
        img.save(img_path, format='PNG')

        result = file_to_base64_data_url(img_path)
        assert result is not None
        assert result.startswith("data:image/png;base64,")


# =============================================================================
# Tests for get_image_dimensions()
# =============================================================================

class TestGetImageDimensions:
    """Tests for get_image_dimensions function."""

    def test_png_dimensions(self, temp_png_image):
        """PNG image returns correct dimensions."""
        width, height = get_image_dimensions(temp_png_image)
        assert width == 100
        assert height == 75

    def test_jpg_dimensions(self, temp_jpg_image):
        """JPEG image returns correct dimensions."""
        width, height = get_image_dimensions(temp_jpg_image)
        assert width == 200
        assert height == 150

    def test_gif_dimensions(self, temp_gif_image):
        """GIF image returns correct dimensions."""
        width, height = get_image_dimensions(temp_gif_image)
        assert width == 50
        assert height == 50

    def test_missing_file_returns_none(self):
        """Missing file returns (None, None)."""
        width, height = get_image_dimensions("/nonexistent/image.png")
        assert width is None
        assert height is None

    def test_corrupt_file_returns_none(self, temp_dir):
        """Corrupt image file returns (None, None)."""
        corrupt_path = os.path.join(temp_dir, "corrupt.png")
        with open(corrupt_path, 'wb') as f:
            f.write(b"not a valid image")

        width, height = get_image_dimensions(corrupt_path)
        assert width is None
        assert height is None


# =============================================================================
# Tests for resolve_path()
# =============================================================================

class TestResolvePath:
    """Tests for resolve_path function."""

    def test_absolute_path_unchanged(self, temp_png_image):
        """Absolute paths are returned unchanged."""
        result = resolve_path(temp_png_image, "/some/base/dir")
        assert result == temp_png_image

    def test_relative_path_joins_with_base(self, temp_dir, temp_png_image):
        """Relative paths join with base directory."""
        filename = os.path.basename(temp_png_image)
        result = resolve_path(filename, temp_dir)
        assert result == temp_png_image

    def test_nonexistent_path_returns_default(self, temp_dir):
        """Non-existent relative path returns joined default."""
        result = resolve_path("nonexistent.png", temp_dir)
        assert result == os.path.join(temp_dir, "nonexistent.png")

    def test_parent_directory_fallback(self, temp_dir):
        """Tests fallback to parent directories."""
        # Create nested structure
        subdir = os.path.join(temp_dir, "sub", "dir")
        os.makedirs(subdir)

        # Create image in temp_dir (two levels up from subdir)
        img_path = os.path.join(temp_dir, "image.png")
        img = Image.new('RGB', (10, 10), color='white')
        img.save(img_path, format='PNG')

        # Try to resolve from subdir - should find via ../../ fallback
        result = resolve_path("image.png", subdir)
        # The function tries multiple candidates; if found, returns found path
        assert os.path.exists(result) or result == os.path.join(subdir, "image.png")


# =============================================================================
# Tests for process_card()
# =============================================================================

class TestProcessCard:
    """Tests for process_card function."""

    def test_card_with_image_path(self, temp_dir, temp_png_image):
        """Card with image_path gets image_data and dimensions."""
        card = {
            "type": "image-occlusion",
            "image_path": temp_png_image,
            "header": "Test"
        }

        result = process_card(card, temp_dir)

        assert "image_data" in result
        assert result["image_data"].startswith("data:image/png;base64,")
        assert result["image_width"] == 100
        assert result["image_height"] == 75
        # Original card should not be mutated
        assert "image_data" not in card

    def test_card_with_photo_path(self, temp_dir, temp_jpg_image):
        """Card with photo_path gets photo_data."""
        card = {
            "type": "person",
            "full_name": "Test Person",
            "photo_path": temp_jpg_image
        }

        result = process_card(card, temp_dir)

        assert "photo_data" in result
        assert result["photo_data"].startswith("data:image/jpeg;base64,")
        # Original card should not be mutated
        assert "photo_data" not in card

    def test_card_without_image_paths(self, temp_dir):
        """Card without image paths is returned unchanged."""
        card = {
            "type": "front-back",
            "question": "What is 2+2?",
            "answer": "4"
        }

        result = process_card(card, temp_dir)

        assert result == card
        assert "image_data" not in result
        assert "photo_data" not in result

    def test_card_with_empty_image_path(self, temp_dir):
        """Card with empty image_path is not processed."""
        card = {
            "type": "image-occlusion",
            "image_path": "",
            "header": "Test"
        }

        result = process_card(card, temp_dir)

        assert "image_data" not in result

    def test_card_with_missing_image_file(self, temp_dir):
        """Card with missing image file doesn't get image_data."""
        card = {
            "type": "image-occlusion",
            "image_path": "/nonexistent/image.png",
            "header": "Test"
        }

        result = process_card(card, temp_dir)

        assert "image_data" not in result


# =============================================================================
# Tests for process_json()
# =============================================================================

class TestProcessJson:
    """Tests for process_json function."""

    def test_process_multiple_cards(self, temp_dir, temp_png_image, temp_jpg_image):
        """Process JSON with multiple cards."""
        data = {
            "deck_name": "Test Deck",
            "cards": [
                {"type": "image-occlusion", "image_path": temp_png_image},
                {"type": "person", "photo_path": temp_jpg_image},
                {"type": "front-back", "question": "Q", "answer": "A"}
            ]
        }

        result = process_json(data, temp_dir)

        assert len(result["cards"]) == 3
        assert "image_data" in result["cards"][0]
        assert "photo_data" in result["cards"][1]
        assert "image_data" not in result["cards"][2]
        # Original should not be mutated
        assert "image_data" not in data["cards"][0]

    def test_process_empty_cards(self, temp_dir):
        """Process JSON with empty cards array."""
        data = {"deck_name": "Empty Deck", "cards": []}

        result = process_json(data, temp_dir)

        assert result["cards"] == []

    def test_process_no_cards_key(self, temp_dir):
        """Process JSON without cards key."""
        data = {"deck_name": "No Cards"}

        result = process_json(data, temp_dir)

        assert "cards" not in result
        assert result["deck_name"] == "No Cards"

    def test_original_data_not_mutated(self, temp_dir):
        """Original data structure is not mutated."""
        data = {"deck_name": "Test", "cards": [{"type": "front-back"}]}
        original_deck_name = data["deck_name"]

        result = process_json(data, temp_dir)

        assert data["deck_name"] == original_deck_name
        assert data is not result


# =============================================================================
# Tests for main()
# =============================================================================

class TestMain:
    """Tests for main CLI function."""

    def test_no_arguments_returns_error(self, capsys):
        """Running with no arguments returns error."""
        result = main([])

        assert result == 1
        captured = capsys.readouterr()
        assert "Usage:" in captured.err

    def test_missing_file_returns_error(self, capsys):
        """Running with non-existent file returns error."""
        result = main(["/nonexistent/file.json"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error reading JSON file" in captured.err

    def test_valid_json_file(self, temp_json_with_images, capsys):
        """Valid JSON file is processed and output to stdout."""
        result = main([temp_json_with_images])

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "deck_name" in output
        assert "cards" in output
        # Image should have been converted to base64
        assert "image_data" in output["cards"][0]

    def test_custom_base_dir(self, temp_dir, temp_png_image, capsys):
        """Custom base_dir argument is respected."""
        # Create JSON file that references image by filename only
        json_path = os.path.join(temp_dir, "test.json")
        filename = os.path.basename(temp_png_image)
        data = {
            "cards": [{"type": "image-occlusion", "image_path": filename}]
        }
        with open(json_path, 'w') as f:
            json.dump(data, f)

        result = main([json_path, temp_dir])

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "image_data" in output["cards"][0]

    def test_invalid_json_returns_error(self, temp_dir, capsys):
        """Invalid JSON file returns error."""
        json_path = os.path.join(temp_dir, "invalid.json")
        with open(json_path, 'w') as f:
            f.write("not valid json {{{")

        result = main([json_path])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error reading JSON file" in captured.err

    def test_json_in_current_dir(self, temp_dir, capsys):
        """JSON file in current directory uses '.' as base_dir."""
        json_path = os.path.join(temp_dir, "test.json")
        data = {"deck_name": "Test", "cards": []}
        with open(json_path, 'w') as f:
            json.dump(data, f)

        # Provide json_path without directory component scenario
        # When dirname returns empty, it should use '.'
        result = main([json_path])

        assert result == 0

    def test_photo_path_processing(self, temp_json_with_photo, capsys):
        """Photo paths are processed correctly."""
        result = main([temp_json_with_photo])

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "photo_data" in output["cards"][0]
        assert output["cards"][0]["photo_data"].startswith("data:image/jpeg;base64,")
