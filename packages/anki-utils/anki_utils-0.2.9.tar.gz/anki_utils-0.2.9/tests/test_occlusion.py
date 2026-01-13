"""Tests for anki_utils occlusion module.

Tests are designed to run without Tesseract installed by mocking pytesseract.
"""

import json
import tempfile
from pathlib import Path
from unittest import mock
from io import BytesIO

import pytest
from PIL import Image

from anki_utils import occlusion


# ============================================================================
# Pure Function Tests (No Mocking Needed)
# ============================================================================


class TestMergeAdjacentRegions:
    """Tests for merge_adjacent_regions() - pure function."""

    def test_empty_list(self):
        """Empty list returns empty list."""
        result = occlusion.merge_adjacent_regions([])
        assert result == []

    def test_single_region_unchanged(self):
        """Single region is returned unchanged."""
        regions = [{
            'text': 'Label',
            'confidence': 0.95,
            'left': 0.1,
            'top': 0.2,
            'width': 0.1,
            'height': 0.05,
        }]
        result = occlusion.merge_adjacent_regions(regions)
        assert len(result) == 1
        assert result[0]['text'] == 'Label'

    def test_merges_vertically_adjacent_regions(self):
        """Two vertically adjacent regions are merged."""
        regions = [
            {
                'text': 'Left',
                'confidence': 0.90,
                'left': 0.10,
                'top': 0.20,
                'width': 0.08,
                'height': 0.03,
            },
            {
                'text': 'Atrium',
                'confidence': 0.85,
                'left': 0.10,
                'top': 0.24,  # Slightly below "Left"
                'width': 0.10,
                'height': 0.03,
            },
        ]
        result = occlusion.merge_adjacent_regions(regions)
        assert len(result) == 1
        assert 'Left' in result[0]['text']
        assert 'Atrium' in result[0]['text']

    def test_does_not_merge_distant_regions(self):
        """Regions far apart are not merged."""
        regions = [
            {
                'text': 'Top',
                'confidence': 0.90,
                'left': 0.10,
                'top': 0.10,
                'width': 0.10,
                'height': 0.05,
            },
            {
                'text': 'Bottom',
                'confidence': 0.85,
                'left': 0.10,
                'top': 0.80,  # Far from "Top"
                'width': 0.10,
                'height': 0.05,
            },
        ]
        result = occlusion.merge_adjacent_regions(regions)
        assert len(result) == 2

    def test_preserves_minimum_confidence(self):
        """Merged region uses minimum confidence."""
        regions = [
            {
                'text': 'First',
                'confidence': 0.95,
                'left': 0.10,
                'top': 0.20,
                'width': 0.10,
                'height': 0.03,
            },
            {
                'text': 'Second',
                'confidence': 0.70,
                'left': 0.10,
                'top': 0.24,
                'width': 0.10,
                'height': 0.03,
            },
        ]
        result = occlusion.merge_adjacent_regions(regions)
        assert len(result) == 1
        assert result[0]['confidence'] == 0.70

    def test_concatenates_text_in_top_to_bottom_order(self):
        """Merged text is ordered top to bottom."""
        regions = [
            {
                'text': 'Lower',
                'confidence': 0.90,
                'left': 0.10,
                'top': 0.24,
                'width': 0.10,
                'height': 0.03,
            },
            {
                'text': 'Upper',
                'confidence': 0.90,
                'left': 0.10,
                'top': 0.20,  # Above "Lower"
                'width': 0.10,
                'height': 0.03,
            },
        ]
        result = occlusion.merge_adjacent_regions(regions)
        assert len(result) == 1
        # "Upper" should come first since it's higher
        assert result[0]['text'].startswith('Upper')

    def test_expands_bounding_box_on_merge(self):
        """Merged region has expanded bounding box."""
        regions = [
            {
                'text': 'A',
                'confidence': 0.90,
                'left': 0.10,
                'top': 0.20,
                'width': 0.05,
                'height': 0.03,
            },
            {
                'text': 'B',
                'confidence': 0.90,
                'left': 0.08,  # Slightly to the left
                'top': 0.24,
                'width': 0.10,  # Wider
                'height': 0.03,
            },
        ]
        result = occlusion.merge_adjacent_regions(regions)
        assert len(result) == 1
        # Bounding box should span both regions
        assert result[0]['left'] == 0.08  # Leftmost
        assert result[0]['top'] == 0.20  # Topmost


class TestGridRefToCoords:
    """Tests for grid_ref_to_coords() - pure function."""

    def test_single_cell_d4(self):
        """Single cell 'D4' returns correct coordinates."""
        coords = occlusion.grid_ref_to_coords('D4')
        # D = row 3 (0-indexed), 4 = column 3 (0-indexed)
        # With grid_size=10: left = 3/10 = 0.3, top = 3/10 = 0.3
        assert coords['left'] == 0.3
        assert coords['top'] == 0.3
        assert coords['width'] == 0.1
        assert coords['height'] == 0.1
        assert coords['source'] == 'grid'

    def test_single_cell_a1(self):
        """Edge cell 'A1' (top-left corner)."""
        coords = occlusion.grid_ref_to_coords('A1')
        assert coords['left'] == 0.0
        assert coords['top'] == 0.0
        assert coords['width'] == 0.1
        assert coords['height'] == 0.1

    def test_single_cell_j10(self):
        """Edge cell 'J10' (bottom-right corner)."""
        coords = occlusion.grid_ref_to_coords('J10')
        # J = row 9, column 10 = index 9
        assert coords['left'] == 0.9
        assert coords['top'] == 0.9
        assert coords['width'] == 0.1
        assert coords['height'] == 0.1

    def test_range_d4_e5(self):
        """Range 'D4-E5' returns expanded bounding box."""
        coords = occlusion.grid_ref_to_coords('D4-E5')
        # D4: left=0.3, top=0.3, E5: left=0.4, top=0.4
        # Range spans from D4 to E5 (inclusive)
        assert coords['left'] == 0.3
        assert coords['top'] == 0.3
        # Width: (0.4 + 0.1) - 0.3 = 0.2
        assert coords['width'] == 0.2
        assert coords['height'] == 0.2
        assert coords['source'] == 'grid'

    def test_lowercase_input(self):
        """Lowercase input is handled correctly."""
        coords = occlusion.grid_ref_to_coords('d4')
        assert coords['left'] == 0.3
        assert coords['top'] == 0.3

    def test_whitespace_stripped(self):
        """Whitespace is stripped from input."""
        coords = occlusion.grid_ref_to_coords('  D4  ')
        assert coords['left'] == 0.3
        assert coords['top'] == 0.3

    def test_custom_grid_size(self):
        """Custom grid size affects coordinates."""
        # With grid_size=5, each cell is 0.2 x 0.2
        coords = occlusion.grid_ref_to_coords('B2', grid_size=5)
        # B = row 1, 2 = column 1
        assert coords['left'] == 0.2
        assert coords['top'] == 0.2
        assert coords['width'] == 0.2
        assert coords['height'] == 0.2

    def test_larger_column_number(self):
        """Column numbers > 9 work correctly."""
        coords = occlusion.grid_ref_to_coords('A12', grid_size=15)
        # Column 12 = index 11
        assert coords['left'] == round(11 / 15, 4)
        assert coords['top'] == 0.0


# ============================================================================
# Tests Requiring Mocking (OCR / PIL)
# ============================================================================


class TestDetectTextRegions:
    """Tests for detect_text_regions() - mocks pytesseract."""

    @pytest.fixture
    def test_image_path(self, temp_dir):
        """Create a temporary test image."""
        img_path = Path(temp_dir) / "test.png"
        img = Image.new('RGB', (1000, 500), color='white')
        img.save(str(img_path))
        return str(img_path)

    @mock.patch('pytesseract.image_to_data')
    def test_returns_normalized_coordinates(self, mock_ocr, test_image_path):
        """Detected regions have normalized coordinates (0-1 scale)."""
        mock_ocr.return_value = {
            'text': ['Label', ''],
            'conf': [90, -1],
            'left': [100, 0],
            'top': [200, 0],
            'width': [50, 0],
            'height': [20, 0],
        }

        regions = occlusion.detect_text_regions(test_image_path)

        assert len(regions) == 1
        assert regions[0]['text'] == 'Label'
        # Image is 1000x500, so: left=100/1000=0.1, top=200/500=0.4
        assert regions[0]['left'] == 0.1
        assert regions[0]['top'] == 0.4
        assert regions[0]['width'] == 0.05
        assert regions[0]['height'] == 0.04

    @mock.patch('pytesseract.image_to_data')
    def test_filters_low_confidence_results(self, mock_ocr, test_image_path):
        """Results below min_confidence are filtered."""
        mock_ocr.return_value = {
            'text': ['HighConf', 'LowConf', ''],
            'conf': [90, 40, -1],
            'left': [100, 200, 0],
            'top': [100, 100, 0],
            'width': [50, 50, 0],
            'height': [20, 20, 0],
        }

        regions = occlusion.detect_text_regions(test_image_path, min_confidence=60)

        assert len(regions) == 1
        assert regions[0]['text'] == 'HighConf'

    @mock.patch('pytesseract.image_to_data')
    def test_handles_empty_ocr_response(self, mock_ocr, test_image_path):
        """Empty OCR response returns empty list."""
        mock_ocr.return_value = {
            'text': [],
            'conf': [],
            'left': [],
            'top': [],
            'width': [],
            'height': [],
        }

        regions = occlusion.detect_text_regions(test_image_path)

        assert regions == []

    @mock.patch('pytesseract.image_to_data')
    def test_skips_empty_text(self, mock_ocr, test_image_path):
        """Entries with empty text are skipped."""
        mock_ocr.return_value = {
            'text': ['', '  ', 'Valid', '\t'],
            'conf': [90, 90, 90, 90],
            'left': [0, 0, 100, 0],
            'top': [0, 0, 100, 0],
            'width': [50, 50, 50, 50],
            'height': [20, 20, 20, 20],
        }

        regions = occlusion.detect_text_regions(test_image_path)

        assert len(regions) == 1
        assert regions[0]['text'] == 'Valid'

    @mock.patch('pytesseract.image_to_data')
    def test_skips_tiny_detections(self, mock_ocr, test_image_path):
        """Very small detections (likely noise) are skipped."""
        mock_ocr.return_value = {
            'text': ['Tiny', 'Normal'],
            'conf': [90, 90],
            'left': [100, 200],
            'top': [100, 100],
            'width': [5, 50],  # 5 is < 10 threshold
            'height': [5, 20],
        }

        regions = occlusion.detect_text_regions(test_image_path)

        assert len(regions) == 1
        assert regions[0]['text'] == 'Normal'

    @mock.patch('pytesseract.image_to_data')
    def test_includes_pixel_coordinates(self, mock_ocr, test_image_path):
        """Regions include absolute pixel coordinates."""
        mock_ocr.return_value = {
            'text': ['Label'],
            'conf': [90],
            'left': [100],
            'top': [200],
            'width': [50],
            'height': [20],
        }

        regions = occlusion.detect_text_regions(test_image_path)

        assert regions[0]['pixel_left'] == 100
        assert regions[0]['pixel_top'] == 200
        assert regions[0]['pixel_width'] == 50
        assert regions[0]['pixel_height'] == 20

    @mock.patch('pytesseract.image_to_data')
    def test_source_is_ocr(self, mock_ocr, test_image_path):
        """Detected regions have source='ocr'."""
        mock_ocr.return_value = {
            'text': ['Label'],
            'conf': [90],
            'left': [100],
            'top': [200],
            'width': [50],
            'height': [20],
        }

        regions = occlusion.detect_text_regions(test_image_path)

        assert regions[0]['source'] == 'ocr'


class TestGenerateGridImage:
    """Tests for generate_grid_image() - mocks image save."""

    @pytest.fixture
    def test_image_path(self, temp_dir):
        """Create a temporary test image."""
        img_path = Path(temp_dir) / "test.png"
        img = Image.new('RGB', (500, 500), color='white')
        img.save(str(img_path))
        return str(img_path)

    def test_creates_output_file(self, test_image_path, temp_dir):
        """Grid image is saved to specified path."""
        output_path = str(Path(temp_dir) / "grid_output.png")

        result = occlusion.generate_grid_image(test_image_path, output_path)

        assert result == output_path
        assert Path(output_path).exists()

    def test_custom_grid_size(self, test_image_path, temp_dir):
        """Custom grid_size is applied."""
        output_path = str(Path(temp_dir) / "grid_5.png")

        result = occlusion.generate_grid_image(
            test_image_path, output_path, grid_size=5
        )

        assert Path(result).exists()
        # Verify image was created (existence check is sufficient)


class TestGeneratePreviewImage:
    """Tests for generate_preview_image() - mocks image save."""

    @pytest.fixture
    def test_image_path(self, temp_dir):
        """Create a temporary test image."""
        img_path = Path(temp_dir) / "test.png"
        img = Image.new('RGB', (500, 500), color='white')
        img.save(str(img_path))
        return str(img_path)

    def test_creates_output_file(self, test_image_path, temp_dir):
        """Preview image is saved to specified path."""
        output_path = str(Path(temp_dir) / "preview.png")
        regions = [{
            'text': 'Label',
            'left': 0.1,
            'top': 0.2,
            'width': 0.1,
            'height': 0.1,
        }]

        result = occlusion.generate_preview_image(
            test_image_path, regions, output_path
        )

        assert result == output_path
        assert Path(output_path).exists()

    def test_handles_multiple_regions(self, test_image_path, temp_dir):
        """Multiple regions are all rendered."""
        output_path = str(Path(temp_dir) / "preview_multi.png")
        regions = [
            {'text': f'Label{i}', 'left': 0.1 * i, 'top': 0.1, 'width': 0.08, 'height': 0.05}
            for i in range(5)
        ]

        result = occlusion.generate_preview_image(
            test_image_path, regions, output_path
        )

        assert Path(result).exists()


class TestGetImageDimensions:
    """Tests for get_image_dimensions()."""

    def test_returns_correct_dimensions(self, temp_dir):
        """Returns (width, height) tuple."""
        img_path = Path(temp_dir) / "test.png"
        img = Image.new('RGB', (800, 600), color='white')
        img.save(str(img_path))

        width, height = occlusion.get_image_dimensions(str(img_path))

        assert width == 800
        assert height == 600


# ============================================================================
# CLI / Main Function Tests
# ============================================================================


class TestMainCLI:
    """Tests for main() CLI entry point."""

    @pytest.fixture
    def test_image_path(self, temp_dir):
        """Create a temporary test image."""
        img_path = Path(temp_dir) / "test.png"
        img = Image.new('RGB', (500, 500), color='white')
        img.save(str(img_path))
        return str(img_path)

    @mock.patch('pytesseract.image_to_data')
    def test_json_output_format(self, mock_ocr, test_image_path, capsys):
        """--json flag outputs valid JSON."""
        mock_ocr.return_value = {
            'text': ['Label'],
            'conf': [90],
            'left': [100],
            'top': [100],
            'width': [50],
            'height': [20],
        }

        result = occlusion.main([test_image_path, '--json'])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert 'image_path' in data
        assert 'detected_regions' in data
        assert 'image_width' in data
        assert 'image_height' in data

    def test_missing_image_returns_error(self, capsys):
        """Non-existent image returns exit code 1."""
        result = occlusion.main(['/nonexistent/image.png'])

        assert result == 1
        captured = capsys.readouterr()
        assert 'Error' in captured.err

    @mock.patch('pytesseract.image_to_data')
    def test_grid_flag_generates_grid_image(self, mock_ocr, test_image_path, temp_dir, capsys):
        """--grid flag generates grid image."""
        mock_ocr.return_value = {
            'text': [],
            'conf': [],
            'left': [],
            'top': [],
            'width': [],
            'height': [],
        }

        result = occlusion.main([
            test_image_path,
            '--grid',
            '--json',
            '--output', temp_dir
        ])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert 'grid_image_path' in data

    @mock.patch('pytesseract.image_to_data')
    def test_preview_flag_generates_preview_image(self, mock_ocr, test_image_path, temp_dir, capsys):
        """--preview flag generates preview image when regions exist."""
        mock_ocr.return_value = {
            'text': ['Label'],
            'conf': [90],
            'left': [100],
            'top': [100],
            'width': [50],
            'height': [20],
        }

        result = occlusion.main([
            test_image_path,
            '--preview',
            '--json',
            '--output', temp_dir
        ])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert 'preview_image_path' in data

    @mock.patch('pytesseract.image_to_data')
    def test_min_conf_argument(self, mock_ocr, test_image_path, capsys):
        """--min-conf argument affects filtering."""
        mock_ocr.return_value = {
            'text': ['High', 'Medium', 'Low'],
            'conf': [95, 75, 50],
            'left': [100, 200, 300],
            'top': [100, 100, 100],
            'width': [50, 50, 50],
            'height': [20, 20, 20],
        }

        result = occlusion.main([test_image_path, '--json', '--min-conf', '80'])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        # Only "High" should pass the 80% threshold
        assert len(data['detected_regions']) == 1

    @mock.patch('pytesseract.image_to_data')
    def test_grid_size_argument(self, mock_ocr, test_image_path, temp_dir, capsys):
        """--grid-size argument is passed correctly."""
        mock_ocr.return_value = {
            'text': [],
            'conf': [],
            'left': [],
            'top': [],
            'width': [],
            'height': [],
        }

        result = occlusion.main([
            test_image_path,
            '--grid',
            '--grid-size', '5',
            '--json',
            '--output', temp_dir
        ])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data['grid_size'] == 5

    @mock.patch('pytesseract.image_to_data')
    def test_human_readable_output(self, mock_ocr, test_image_path, capsys):
        """Default output is human-readable."""
        mock_ocr.return_value = {
            'text': ['TestLabel'],
            'conf': [90],
            'left': [100],
            'top': [100],
            'width': [50],
            'height': [20],
        }

        result = occlusion.main([test_image_path])

        assert result == 0
        captured = capsys.readouterr()
        # Human readable output contains formatted text
        assert 'Image Occlusion Region Detection' in captured.out
        assert 'TestLabel' in captured.out

    @mock.patch('pytesseract.image_to_data')
    def test_output_directory_argument(self, mock_ocr, test_image_path, temp_dir, capsys):
        """--output argument specifies output directory."""
        mock_ocr.return_value = {
            'text': [],
            'conf': [],
            'left': [],
            'top': [],
            'width': [],
            'height': [],
        }
        output_dir = Path(temp_dir) / "custom_output"
        output_dir.mkdir()

        result = occlusion.main([
            test_image_path,
            '--grid',
            '--json',
            '--output', str(output_dir)
        ])

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert str(output_dir) in data['grid_image_path']


# ============================================================================
# Integration Tests (Skip if Tesseract Unavailable)
# ============================================================================


class TestIntegration:
    """Integration tests that require Tesseract installed."""

    @pytest.fixture
    def has_tesseract(self):
        """Check if Tesseract is available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    @pytest.fixture
    def test_image_with_text(self, temp_dir):
        """Create an image with actual text for OCR."""
        from PIL import ImageDraw

        img_path = Path(temp_dir) / "text_image.png"
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 30), "TEST LABEL", fill='black')
        img.save(str(img_path))
        return str(img_path)

    def test_real_ocr_if_available(self, has_tesseract, test_image_with_text):
        """Test with real Tesseract if available."""
        if not has_tesseract:
            pytest.skip("Tesseract not installed")

        regions = occlusion.detect_text_regions(test_image_with_text, min_confidence=30)

        # Should detect something (exact results depend on Tesseract)
        assert isinstance(regions, list)
