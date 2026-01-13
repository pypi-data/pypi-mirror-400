"""Utility helpers for Anki assets."""

from importlib.metadata import PackageNotFoundError, version

from .themes import (
    DEFAULT_THEME,
    THEMES,
    get_cloze_css,
    get_concept_css,
    get_front_back_css,
    get_image_css,
    get_image_occlusion_css,
    get_person_css,
    get_theme_sections,
)

__all__ = [
    "__version__",
    "DEFAULT_THEME",
    "THEMES",
    "create_package",
    "get_cloze_css",
    "get_concept_css",
    "get_front_back_css",
    "get_image_css",
    "get_image_occlusion_css",
    "get_person_css",
    "get_theme_sections",
]

try:
    __version__ = version("anki-utils")
except PackageNotFoundError:
    __version__ = "0.0.0"


def __getattr__(name: str):
    if name == "create_package":
        from .exporter import create_package

        return create_package
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
