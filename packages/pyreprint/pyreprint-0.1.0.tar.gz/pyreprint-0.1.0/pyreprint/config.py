"""Global configuration for pyreprint."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Config:
    """Global configuration settings for pyreprint."""

    # Default width for decorators (0 = auto-detect terminal width)
    default_width: int = 0

    # Default character for line decorators
    default_char: str = "="

    # Whether to use rich by default when available
    use_rich: bool = True

    # Whether to enable markup parsing in rich output
    rich_markup: bool = True

    # Default style to apply (None = no default style)
    default_style: Optional[str] = None

    # Custom style configurations loaded from files
    loaded_styles: Dict[str, Any] = field(default_factory=dict)

    def get_width(self, width: Optional[int] = None) -> int:
        """Get the effective width, with auto-detection if needed."""
        if width is not None and width > 0:
            return width
        if self.default_width > 0:
            return self.default_width
        # Auto-detect terminal width
        terminal_size = shutil.get_terminal_size(fallback=(80, 24))
        return terminal_size.columns

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.default_width = 0
        self.default_char = "="
        self.use_rich = True
        self.rich_markup = True
        self.default_style = None
        self.loaded_styles.clear()


# Global configuration instance
config = Config()


def configure(**kwargs: Any) -> None:
    """Update global configuration settings.

    Args:
        **kwargs: Configuration options to update.
            - default_width: Default width for decorators
            - default_char: Default character for line decorators
            - use_rich: Whether to use rich by default
            - rich_markup: Whether to enable markup parsing
            - default_style: Default style name to apply
    """
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration option: {key}")


def get_config() -> Config:
    """Get the global configuration instance."""
    return config

