"""Decorator patterns for enhancing print output."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Optional, Union


def _get_width(width: Optional[int] = None) -> int:
    """Get effective width, auto-detecting if needed."""
    if width is not None and width > 0:
        return width
    terminal_size = shutil.get_terminal_size(fallback=(80, 24))
    return terminal_size.columns


@dataclass
class Line:
    """A horizontal line decorator.

    Args:
        char: Character to repeat for the line.
        width: Width of the line (0 = auto-detect terminal width).

    Example:
        >>> line = Line('=', 40)
        >>> print(line)
        ========================================
    """

    char: str = "="
    width: int = 0

    def __str__(self) -> str:
        effective_width = _get_width(self.width)
        return self.char * effective_width

    def __repr__(self) -> str:
        return f"Line(char={self.char!r}, width={self.width})"


@dataclass
class Header:
    """A header with text and underline.

    Args:
        text: The header text.
        char: Character for the underline.
        width: Width of the underline (0 = match text length).
        above: Whether to include a line above the text.

    Example:
        >>> header = Header("My Section", char='=')
        >>> print(header)
        My Section
        ==========
    """

    text: str
    char: str = "="
    width: int = 0
    above: bool = False

    def __str__(self) -> str:
        effective_width = self.width if self.width > 0 else len(self.text)
        underline = self.char * effective_width
        if self.above:
            return f"{underline}\n{self.text}\n{underline}"
        return f"{self.text}\n{underline}"

    def __repr__(self) -> str:
        return f"Header(text={self.text!r}, char={self.char!r}, width={self.width})"


@dataclass
class Box:
    """A box around text content.

    Args:
        text: The text to box.
        char: Character for vertical borders.
        corner: Character for corners.
        horizontal: Character for horizontal borders.
        padding: Padding inside the box.
        width: Width of the box (0 = auto-fit to text).

    Example:
        >>> box = Box("Hello World")
        >>> print(box)
        +-------------+
        | Hello World |
        +-------------+
    """

    text: str
    char: str = "|"
    corner: str = "+"
    horizontal: str = "-"
    padding: int = 1
    width: int = 0

    def __str__(self) -> str:
        lines = self.text.split("\n")
        max_len = max(len(line) for line in lines)
        effective_width = self.width if self.width > 0 else max_len + (self.padding * 2)

        pad = " " * self.padding
        border = self.corner + self.horizontal * (effective_width + 2) + self.corner

        result = [border]
        for line in lines:
            padded = f"{pad}{line}{pad}".ljust(effective_width + 2)
            result.append(f"{self.char}{padded}{self.char}")
        result.append(border)

        return "\n".join(result)

    def __repr__(self) -> str:
        return f"Box(text={self.text!r}, char={self.char!r})"


@dataclass
class Banner:
    """A full-width banner with centered text.

    Args:
        text: The banner text.
        char: Character for the border.
        width: Width of the banner (0 = auto-detect terminal width).
        padding_lines: Number of empty lines above/below text.

    Example:
        >>> banner = Banner("WELCOME", char='*', width=30)
        >>> print(banner)
        ******************************
        *          WELCOME           *
        ******************************
    """

    text: str
    char: str = "*"
    width: int = 0
    padding_lines: int = 0

    def __str__(self) -> str:
        effective_width = _get_width(self.width)
        border = self.char * effective_width

        # Calculate inner width (without border chars)
        inner_width = effective_width - 2
        centered_text = self.text.center(inner_width)

        result = [border]
        for _ in range(self.padding_lines):
            result.append(f"{self.char}{' ' * inner_width}{self.char}")
        result.append(f"{self.char}{centered_text}{self.char}")
        for _ in range(self.padding_lines):
            result.append(f"{self.char}{' ' * inner_width}{self.char}")
        result.append(border)

        return "\n".join(result)

    def __repr__(self) -> str:
        return f"Banner(text={self.text!r}, char={self.char!r}, width={self.width})"


# Convenience functions


def line(char: str = "=", width: int = 0) -> str:
    """Create a horizontal line.

    Args:
        char: Character to repeat.
        width: Width of the line (0 = auto-detect terminal width).

    Returns:
        The line as a string.

    Example:
        >>> print(line('=', 40))
        ========================================
    """
    return str(Line(char=char, width=width))


def header(
    text: str,
    char: str = "=",
    width: int = 0,
    above: bool = False,
) -> str:
    """Create a header with underline.

    Args:
        text: The header text.
        char: Character for the underline.
        width: Width of the underline (0 = match text length).
        above: Whether to include a line above the text.

    Returns:
        The header as a string.

    Example:
        >>> print(header("My Section"))
        My Section
        ==========
    """
    return str(Header(text=text, char=char, width=width, above=above))


def box(
    text: str,
    char: str = "|",
    corner: str = "+",
    horizontal: str = "-",
    padding: int = 1,
    width: int = 0,
) -> str:
    """Create a box around text.

    Args:
        text: The text to box.
        char: Character for vertical borders.
        corner: Character for corners.
        horizontal: Character for horizontal borders.
        padding: Padding inside the box.
        width: Width of the box (0 = auto-fit to text).

    Returns:
        The boxed text as a string.

    Example:
        >>> print(box("Hello"))
        +-------+
        | Hello |
        +-------+
    """
    return str(
        Box(
            text=text,
            char=char,
            corner=corner,
            horizontal=horizontal,
            padding=padding,
            width=width,
        )
    )


def banner(
    text: str,
    char: str = "*",
    width: int = 0,
    padding_lines: int = 0,
) -> str:
    """Create a full-width banner with centered text.

    Args:
        text: The banner text.
        char: Character for the border.
        width: Width of the banner (0 = auto-detect terminal width).
        padding_lines: Number of empty lines above/below text.

    Returns:
        The banner as a string.

    Example:
        >>> print(banner("WELCOME", width=30))
        ******************************
        *          WELCOME           *
        ******************************
    """
    return str(Banner(text=text, char=char, width=width, padding_lines=padding_lines))


# Type alias for decorator arguments
DecoratorType = Union[str, Line, Header, Box, Banner, None]


def resolve_decorator(
    decorator: DecoratorType,
    width: Optional[int] = None,
) -> Optional[str]:
    """Resolve a decorator argument to a string.

    Args:
        decorator: The decorator specification (string, decorator object, or None).
        width: Optional width override.

    Returns:
        The resolved decorator string, or None.
    """
    if decorator is None:
        return None

    if isinstance(decorator, str):
        # Simple string like "=" becomes a line
        if len(decorator) == 1:
            return line(decorator, width=width or 0)
        return decorator

    if isinstance(decorator, (Line, Header, Box, Banner)):
        return str(decorator)

    return str(decorator)

