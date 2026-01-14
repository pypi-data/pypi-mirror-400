#!/usr/bin/env python
"""Custom styles examples for PyRePrint."""

from datetime import datetime

from pyreprint import (
    list_styles,
    load_styles_from_dict,
    register_style,
    reprint,
)


# =============================================================================
# Defining Custom Styles
# =============================================================================

@register_style("timestamp")
def timestamp_style(text, **kwargs):
    """Add timestamp to messages."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{now}] {text}"


@register_style("debug")
def debug_style(text, level="DEBUG", **kwargs):
    """Debug message format."""
    return f"[{level}] {text}"


@register_style("code_block")
def code_block_style(text, language="", **kwargs):
    """Format as a code block."""
    header = f"```{language}" if language else "```"
    return f"{header}\n{text}\n```"


@register_style("fancy_box")
def fancy_box_style(text, width=50, **kwargs):
    """A fancy double-lined box."""
    lines = text.split("\n")
    max_len = max(len(line) for line in lines)
    effective_width = max(width, max_len + 4)

    top = "+" + "=" * (effective_width - 2) + "+"
    bottom = "+" + "=" * (effective_width - 2) + "+"
    empty = "|" + " " * (effective_width - 2) + "|"

    result = [top, empty]
    for line in lines:
        padded = line.center(effective_width - 4)
        result.append(f"| {padded} |")
    result.extend([empty, bottom])

    return "\n".join(result)


@register_style("rainbow")
def rainbow_style(text, **kwargs):
    """Apply visual markers to text."""
    markers = ["*", "-", "*"]
    decorated = f"{markers[0]} {text} {markers[2]}"
    line = "-" * len(decorated)
    return f"{line}\n{decorated}\n{line}"


@register_style("step")
def step_style(text, number=1, total=None, **kwargs):
    """Format as a step in a process."""
    if total:
        prefix = f"[Step {number}/{total}]"
    else:
        prefix = f"[Step {number}]"
    return f"{prefix} {text}"


def main():
    reprint("Custom Styles Examples", style="banner", width=60)
    reprint("")

    # =========================================================================
    # Using Custom Styles
    # =========================================================================

    reprint("1. Decorator-Defined Styles", style="header")

    reprint("Application started", style="timestamp")
    reprint("Variable x = 42", style="debug")
    reprint("Something important", style="debug", level="INFO")
    reprint("")

    reprint("print('Hello')", style="code_block", language="python")
    reprint("")

    reprint("Special Announcement", style="fancy_box", width=40)
    reprint("")

    reprint("Featured Content", style="rainbow")
    reprint("")

    reprint("Initialize database", style="step", number=1, total=3)
    reprint("Load configuration", style="step", number=2, total=3)
    reprint("Start server", style="step", number=3, total=3)
    reprint("")

    # =========================================================================
    # Loading Styles from Dictionary
    # =========================================================================

    reprint("2. Dictionary-Defined Styles", style="header")

    # Define styles programmatically
    style_config = {
        "arrow": {
            "prefix": ">>> ",
            "suffix": "",
        },
        "bracket": {
            "prefix": "[ ",
            "suffix": " ]",
        },
        "underline": {
            "after": {"char": "_", "width": 30},
        },
    }

    load_styles_from_dict(style_config)

    reprint("Arrow prefix", style="arrow")
    reprint("Bracketed text", style="bracket")
    reprint("Underlined text", style="underline")
    reprint("")

    # =========================================================================
    # Listing Available Styles
    # =========================================================================

    reprint("3. Available Styles", style="header")

    styles = list_styles()
    reprint(f"Total registered styles: {len(styles)}")
    reprint("")

    # Group styles for display
    builtin = ["section", "header", "divider", "box", "banner", "title",
               "quote", "bullet", "numbered", "highlight",
               "warning", "error", "success", "info"]
    custom = [s for s in styles if s not in builtin]

    reprint("Built-in styles:", style="info")
    for style in sorted(builtin):
        if style in styles:
            print(f"  - {style}")

    reprint("")
    reprint("Custom styles:", style="info")
    for style in sorted(custom):
        print(f"  - {style}")
    reprint("")

    # =========================================================================
    # Practical Example: Logger
    # =========================================================================

    reprint("4. Practical Example: Simple Logger", style="header")

    @register_style("log_info")
    def log_info(text, **kwargs):
        ts = datetime.now().strftime("%H:%M:%S")
        return f"{ts} [INFO]  {text}"

    @register_style("log_warn")
    def log_warn(text, **kwargs):
        ts = datetime.now().strftime("%H:%M:%S")
        return f"{ts} [WARN]  {text}"

    @register_style("log_error")
    def log_error(text, **kwargs):
        ts = datetime.now().strftime("%H:%M:%S")
        return f"{ts} [ERROR] {text}"

    reprint("Application starting", style="log_info")
    reprint("Configuration file not found, using defaults", style="log_warn")
    reprint("Ready to accept connections", style="log_info")
    reprint("Connection timeout", style="log_error")
    reprint("")

    reprint("Examples Complete!", style="banner", width=60)


if __name__ == "__main__":
    main()

