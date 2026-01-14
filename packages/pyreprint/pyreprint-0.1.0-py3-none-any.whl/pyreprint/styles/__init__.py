"""Style system for pyreprint."""

from pyreprint.styles.builtins import (
    banner_style,
    box_style,
    divider_style,
    header_style,
    section_style,
)
from pyreprint.styles.loader import load_styles_from_file, load_styles_from_yaml
from pyreprint.styles.registry import (
    StyleRegistry,
    get_style,
    list_styles,
    register_style,
    registry,
)

__all__ = [
    # Registry
    "StyleRegistry",
    "registry",
    "register_style",
    "get_style",
    "list_styles",
    # Loader
    "load_styles_from_file",
    "load_styles_from_yaml",
    # Built-in styles
    "section_style",
    "header_style",
    "divider_style",
    "box_style",
    "banner_style",
]

