"""Shared fixtures for anki-utils tests."""

import pytest
import tempfile
import os


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_front_back_card():
    """Sample front-back card data."""
    return {
        "type": "front-back",
        "question": "What is the capital of France?",
        "answer": "Paris",
        "example": "Paris is known for the Eiffel Tower.",
        "extra_info": "Population: ~2.1 million",
        "author": "Test Author",
        "source": "Geography 101",
        "tags": ["geography", "europe"]
    }


@pytest.fixture
def sample_concept_card():
    """Sample concept card data."""
    return {
        "type": "concept",
        "concept": "Photosynthesis",
        "definition": "The process by which plants convert sunlight into energy.",
        "example": "Plants use chlorophyll to capture light.",
        "extra_info": "Occurs primarily in leaves.",
        "author": "Test Author",
        "source": "Biology 101",
        "tags": ["biology", "plants"]
    }


@pytest.fixture
def sample_cloze_card():
    """Sample cloze card data."""
    return {
        "type": "cloze",
        "cloze_text": "The {{c1::mitochondria}} is the {{c2::powerhouse}} of the cell.",
        "example": "Found in most eukaryotic cells.",
        "extra_info": "Produces ATP through cellular respiration.",
        "author": "Test Author",
        "source": "Biology 101",
        "tags": ["biology", "cells"]
    }


@pytest.fixture
def sample_person_card():
    """Sample person card data."""
    return {
        "type": "person",
        "full_name": "Jane Doe",
        "birthday": "March 15",
        "current_city": "San Francisco",
        "phone_number": "555-123-4567",
        "partner_name": "John Doe",
        "hobbies": "Reading, hiking",
        "title": "Software Engineer",
        "company": "Tech Corp",
        "tags": ["work", "contacts"]
    }


@pytest.fixture
def sample_image_occlusion_card():
    """Sample image-occlusion card data with base64 fallback for testing."""
    import base64
    from io import BytesIO
    from PIL import Image

    # Create a 100x100 test image so tests work without real files
    img = Image.new('RGB', (100, 100), color='gray')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    b64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return {
        "type": "image-occlusion",
        "image_path": "/path/to/diagram.jpg",  # Fake path (won't exist)
        "image_data": f"data:image/png;base64,{b64_data}",  # Fallback for tests
        "header": "Label the parts",
        "back_extra": "Extra context",
        "occlusion_mode": "hide_all_guess_one",
        "occlusions": [
            {
                "cloze_num": 1,
                "label": "Part A",
                "shape": "rect",
                "left": 0.1,
                "top": 0.2,
                "width": 0.15,
                "height": 0.1,
                "fill": "#ffeba2"
            },
            {
                "cloze_num": 2,
                "label": "Part B",
                "shape": "ellipse",
                "left": 0.5,
                "top": 0.6,
                "width": 0.2,
                "height": 0.15
            }
        ],
        "tags": ["anatomy"]
    }


@pytest.fixture
def sample_deck_data(sample_front_back_card, sample_cloze_card):
    """Sample deck with multiple card types."""
    return {
        "deck_name": "Test Deck",
        "theme": "minimal",
        "batch_tags": ["test-batch"],
        "cards": [sample_front_back_card, sample_cloze_card]
    }


@pytest.fixture
def sample_image_occlusion_card_with_base64():
    """Sample image-occlusion card using base64 image_data instead of image_path.

    This is a tiny 2x2 red PNG encoded as base64.
    """
    # Minimal valid 2x2 red PNG (created programmatically)
    # This is a real PNG that can be decoded by PIL
    import base64
    from io import BytesIO
    from PIL import Image

    # Create a small test image
    img = Image.new('RGB', (100, 75), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    png_bytes = buffer.getvalue()
    b64_data = base64.b64encode(png_bytes).decode('utf-8')

    return {
        "type": "image-occlusion",
        "image_data": f"data:image/png;base64,{b64_data}",
        "header": "Label the parts",
        "back_extra": "Extra context",
        "occlusion_mode": "hide_all_guess_one",
        "occlusions": [
            {
                "cloze_num": 1,
                "label": "Part A",
                "shape": "rect",
                "left": 0.1,
                "top": 0.2,
                "width": 0.15,
                "height": 0.1,
            }
        ],
        "tags": ["base64-test"]
    }
