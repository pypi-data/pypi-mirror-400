#!/usr/bin/env python
"""Basic usage examples for PyRePrint."""

from pyreprint import (
    Banner,
    Box,
    Header,
    Line,
    banner,
    box,
    header,
    line,
    reprint,
)


def main():
    # =========================================================================
    # Basic Printing
    # =========================================================================

    reprint("PyRePrint Basic Usage Examples", style="banner", width=60)
    reprint("")

    # Standard print behavior
    reprint("1. Standard Printing", style="header")
    reprint("Hello, World!")
    reprint("Multiple", "values", "joined", sep=" | ")
    reprint("")

    # =========================================================================
    # Using Decorators
    # =========================================================================

    reprint("2. Using Decorators", style="header")

    # Before and after
    reprint("With line before", before="=", width=40)
    reprint("")

    reprint("With line after", after="-", width=40)
    reprint("")

    # Surround shortcut
    reprint("Surrounded by lines", surround="*", width=40)
    reprint("")

    # =========================================================================
    # Decorator Classes
    # =========================================================================

    reprint("3. Decorator Classes", style="header")

    # Line
    print(Line("=", 50))
    print("Using Line class directly")
    print(Line("-", 50))
    reprint("")

    # Header
    print(Header("Section Title", char="="))
    reprint("")

    # Box
    print(Box("Content inside a box"))
    reprint("")

    # Banner
    print(Banner("ANNOUNCEMENT", char="#", width=50))
    reprint("")

    # =========================================================================
    # Convenience Functions
    # =========================================================================

    reprint("4. Convenience Functions", style="header")

    print(line("~", 40))
    print(header("My Header"))
    print(box("Boxed text\nwith multiple lines"))
    print(banner("CENTERED", width=40))
    reprint("")

    # =========================================================================
    # Built-in Styles
    # =========================================================================

    reprint("5. Built-in Styles", style="header")

    reprint("Section style", style="section", width=40)
    reprint("")

    reprint("Divider style", style="divider", width=40)
    reprint("")

    reprint("Box style", style="box")
    reprint("")

    reprint("Title style", style="title", width=40)
    reprint("")

    reprint("Quote style\nMultiple lines", style="quote")
    reprint("")

    # Status styles
    reprint("Operation successful", style="success")
    reprint("Check this carefully", style="warning")
    reprint("Something went wrong", style="error")
    reprint("For your information", style="info")
    reprint("")

    # =========================================================================
    # Combining Features
    # =========================================================================

    reprint("6. Combining Features", style="header")

    # Multiple values with style
    name, version = "PyRePrint", "0.1.0"
    reprint(f"Package: {name} v{version}", style="highlight")
    reprint("")

    # Nested decorators
    reprint("Important Section", style="banner", width=50)
    reprint("  This is the section content.")
    reprint("  It can have multiple lines.")
    reprint(line("-", 50))
    reprint("")

    # =========================================================================
    # End
    # =========================================================================

    reprint("Examples Complete!", style="banner", width=60)


if __name__ == "__main__":
    main()

