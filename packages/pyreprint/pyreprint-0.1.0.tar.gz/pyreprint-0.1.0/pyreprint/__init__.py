"""PyRePrint - Enhanced print() with decorators, formatting, and style patterns.

PyRePrint provides an enhanced print function with support for:
- Decorators (lines, boxes, headers, banners)
- Named styles that can be applied via a `style` parameter
- Output capture and redirection
- Rich library integration
- Scikit-learn style __repr__ formatting

Basic Usage:
    >>> from pyreprint import reprint
    >>> reprint("Hello, World!")
    Hello, World!

    >>> reprint("Section", before="=", after="=", width=40)
    ========================================
    Section
    ========================================

    >>> reprint("Important!", style="banner", width=40)
    ****************************************
    *             Important!               *
    ****************************************

Using Decorators:
    >>> from pyreprint import line, header, box, banner
    >>> print(line("=", 40))
    ========================================
    >>> print(header("My Section"))
    My Section
    ==========

Capturing Output:
    >>> from pyreprint import capture_output
    >>> with capture_output() as captured:
    ...     print("Hello")
    >>> print(captured.stdout)
    Hello

Using Styles:
    >>> from pyreprint import register_style, reprint
    >>> @register_style("custom")
    ... def my_style(text, **kwargs):
    ...     return f">>> {text} <<<"
    >>> reprint("Hello", style="custom")
    >>> Hello <<<

Rich Integration:
    >>> from pyreprint import rprint
    >>> rprint("[bold red]Error:[/bold red] Something went wrong")
"""

from pyreprint._version import __version__

# Configuration
from pyreprint.config import (
    Config,
    config,
    configure,
    get_config,
)

# Capture utilities
from pyreprint.core.capture import (
    CapturedOutput,
    OutputBuffer,
    OutputTee,
    capture_output,
    redirect_to_file,
)

# Decorators
from pyreprint.core.decorators import (
    Banner,
    Box,
    Header,
    Line,
    banner,
    box,
    header,
    line,
)

# Core functionality
from pyreprint.core.printer import (
    Printer,
    install_print,
    reprint,
    uninstall_print,
)
from pyreprint.formatting.html import (
    HTMLFormatter,
    display_html,
    html_repr,
)

# Formatting
from pyreprint.formatting.repr import (
    ReprConfig,
    ReprMixin,
    format_repr,
)
from pyreprint.integrations.pprint import (
    PrettyPrinter,
    pformat,
    pprint,
)

# Integrations
from pyreprint.integrations.rich import (
    RichPrinter,
    console,
    panel,
    rprint,
    rule,
)
from pyreprint.styles import builtins as _builtins  # noqa: F401
from pyreprint.styles.loader import (
    load_styles_from_dict,
    load_styles_from_file,
    load_styles_from_yaml,
)

# Style system
from pyreprint.styles.registry import (
    StyleRegistry,
    apply_style,
    get_style,
    list_styles,
    register_style,
    registry,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "reprint",
    "Printer",
    "install_print",
    "uninstall_print",
    # Decorators
    "Line",
    "Header",
    "Box",
    "Banner",
    "line",
    "header",
    "box",
    "banner",
    # Capture
    "capture_output",
    "redirect_to_file",
    "CapturedOutput",
    "OutputTee",
    "OutputBuffer",
    # Styles
    "StyleRegistry",
    "registry",
    "register_style",
    "get_style",
    "list_styles",
    "apply_style",
    "load_styles_from_file",
    "load_styles_from_yaml",
    "load_styles_from_dict",
    # Formatting
    "ReprMixin",
    "ReprConfig",
    "format_repr",
    "HTMLFormatter",
    "html_repr",
    "display_html",
    # Rich integration
    "RichPrinter",
    "console",
    "rprint",
    "rule",
    "panel",
    # PrettyPrint
    "PrettyPrinter",
    "pprint",
    "pformat",
    # Configuration
    "Config",
    "config",
    "configure",
    "get_config",
]

