"""Built-in style definitions for pyreprint."""

from __future__ import annotations

from typing import Any

from pyreprint.styles.registry import register_style


@register_style("section")
def section_style(text: str, width: int = 60, char: str = "=", **kwargs: Any) -> str:
    """Section style with lines above and below.

    Creates a section header with horizontal lines surrounding the text.

    Args:
        text: The text to style.
        width: Width of the lines.
        char: Character for the lines.

    Returns:
        Styled text.

    Example:
        >>> print(section_style("My Section"))
        ============================================================
        My Section
        ============================================================
    """
    line = char * width
    return f"{line}\n{text}\n{line}"


@register_style("header")
def header_style(text: str, width: int = 0, char: str = "=", **kwargs: Any) -> str:
    """Header style with underline.

    Creates a header with an underline matching the text length.

    Args:
        text: The text to style.
        width: Width of underline (0 = match text length).
        char: Character for the underline.

    Returns:
        Styled text.

    Example:
        >>> print(header_style("My Header"))
        My Header
        =========
    """
    line_width = width if width > 0 else len(text)
    line = char * line_width
    return f"{text}\n{line}"


@register_style("divider")
def divider_style(text: str, width: int = 60, char: str = "-", **kwargs: Any) -> str:
    """Divider style with subtle lines.

    Creates a softer divider using dashes.

    Args:
        text: The text to style.
        width: Width of the lines.
        char: Character for the lines.

    Returns:
        Styled text.

    Example:
        >>> print(divider_style("Section"))
        ------------------------------------------------------------
        Section
        ------------------------------------------------------------
    """
    line = char * width
    return f"{line}\n{text}\n{line}"


@register_style("box")
def box_style(
    text: str,
    width: int = 0,
    char: str = "|",
    corner: str = "+",
    horizontal: str = "-",
    padding: int = 1,
    **kwargs: Any,
) -> str:
    """Box style surrounding text.

    Creates a box around the text.

    Args:
        text: The text to style.
        width: Width of box (0 = auto-fit).
        char: Vertical border character.
        corner: Corner character.
        horizontal: Horizontal border character.
        padding: Padding inside box.

    Returns:
        Styled text.

    Example:
        >>> print(box_style("Hello"))
        +-------+
        | Hello |
        +-------+
    """
    lines = text.split("\n")
    max_len = max(len(line) for line in lines)
    effective_width = width if width > 0 else max_len + (padding * 2)

    pad = " " * padding
    border = corner + horizontal * (effective_width + 2) + corner

    result = [border]
    for line in lines:
        padded = f"{pad}{line}{pad}".ljust(effective_width + 2)
        result.append(f"{char}{padded}{char}")
    result.append(border)

    return "\n".join(result)


@register_style("banner")
def banner_style(
    text: str,
    width: int = 60,
    char: str = "*",
    padding_lines: int = 0,
    **kwargs: Any,
) -> str:
    """Banner style with centered text.

    Creates a full-width banner with centered text.

    Args:
        text: The text to style.
        width: Width of the banner.
        char: Border character.
        padding_lines: Empty lines above/below text.

    Returns:
        Styled text.

    Example:
        >>> print(banner_style("WELCOME", width=40))
        ****************************************
        *              WELCOME                 *
        ****************************************
    """
    border = char * width
    inner_width = width - 2
    centered_text = text.center(inner_width)

    result = [border]
    for _ in range(padding_lines):
        result.append(f"{char}{' ' * inner_width}{char}")
    result.append(f"{char}{centered_text}{char}")
    for _ in range(padding_lines):
        result.append(f"{char}{' ' * inner_width}{char}")
    result.append(border)

    return "\n".join(result)


@register_style("title")
def title_style(
    text: str,
    width: int = 60,
    char: str = "#",
    **kwargs: Any,
) -> str:
    """Title style with decorative borders.

    Creates a prominent title with thick borders.

    Args:
        text: The text to style.
        width: Width of the title.
        char: Border character.

    Returns:
        Styled text.

    Example:
        >>> print(title_style("Main Title"))
        ############################################################
        #                       Main Title                         #
        ############################################################
    """
    border = char * width
    inner_width = width - 2
    centered_text = text.center(inner_width)

    return f"{border}\n{char}{centered_text}{char}\n{border}"


@register_style("quote")
def quote_style(text: str, prefix: str = "> ", **kwargs: Any) -> str:
    """Quote style with prefix on each line.

    Adds a prefix to each line, like a blockquote.

    Args:
        text: The text to style.
        prefix: Prefix for each line.

    Returns:
        Styled text.

    Example:
        >>> print(quote_style("Line 1\\nLine 2"))
        > Line 1
        > Line 2
    """
    lines = text.split("\n")
    return "\n".join(f"{prefix}{line}" for line in lines)


@register_style("bullet")
def bullet_style(text: str, bullet: str = "- ", indent: int = 2, **kwargs: Any) -> str:
    """Bullet list style.

    Formats text as a bullet point.

    Args:
        text: The text to style.
        bullet: Bullet character.
        indent: Indentation for continuation lines.

    Returns:
        Styled text.

    Example:
        >>> print(bullet_style("Item text"))
        - Item text
    """
    lines = text.split("\n")
    if not lines:
        return ""

    result = [f"{bullet}{lines[0]}"]
    indent_str = " " * (len(bullet) + indent - len(bullet))
    for line in lines[1:]:
        result.append(f"{indent_str}{line}")

    return "\n".join(result)


@register_style("numbered")
def numbered_style(
    text: str,
    number: int = 1,
    separator: str = ". ",
    **kwargs: Any,
) -> str:
    """Numbered item style.

    Formats text as a numbered item.

    Args:
        text: The text to style.
        number: The item number.
        separator: Separator after number.

    Returns:
        Styled text.

    Example:
        >>> print(numbered_style("First item", number=1))
        1. First item
    """
    return f"{number}{separator}{text}"


@register_style("highlight")
def highlight_style(
    text: str,
    prefix: str = ">>> ",
    suffix: str = " <<<",
    **kwargs: Any,
) -> str:
    """Highlight style with prefix and suffix.

    Draws attention to text with markers.

    Args:
        text: The text to style.
        prefix: Prefix marker.
        suffix: Suffix marker.

    Returns:
        Styled text.

    Example:
        >>> print(highlight_style("Important"))
        >>> Important <<<
    """
    return f"{prefix}{text}{suffix}"


@register_style("warning")
def warning_style(text: str, width: int = 60, **kwargs: Any) -> str:
    """Warning style with attention-grabbing format.

    Creates a warning message format.

    Args:
        text: The warning text.
        width: Width of the warning box.

    Returns:
        Styled text.

    Example:
        >>> print(warning_style("Check this!"))
        !! WARNING !!
        Check this!
    """
    return f"!! WARNING !!\n{text}"


@register_style("error")
def error_style(text: str, width: int = 60, **kwargs: Any) -> str:
    """Error style with prominent format.

    Creates an error message format.

    Args:
        text: The error text.
        width: Width of the error box.

    Returns:
        Styled text.

    Example:
        >>> print(error_style("Something failed"))
        [ERROR] Something failed
    """
    return f"[ERROR] {text}"


@register_style("success")
def success_style(text: str, width: int = 60, **kwargs: Any) -> str:
    """Success style with positive format.

    Creates a success message format.

    Args:
        text: The success text.
        width: Width of the success box.

    Returns:
        Styled text.

    Example:
        >>> print(success_style("Operation complete"))
        [OK] Operation complete
    """
    return f"[OK] {text}"


@register_style("info")
def info_style(text: str, width: int = 60, **kwargs: Any) -> str:
    """Info style with informational format.

    Creates an info message format.

    Args:
        text: The info text.
        width: Width of the info box.

    Returns:
        Styled text.

    Example:
        >>> print(info_style("FYI"))
        [INFO] FYI
    """
    return f"[INFO] {text}"

