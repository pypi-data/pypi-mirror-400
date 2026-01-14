"""Integrations with external libraries."""

from pyreprint.integrations.pprint import pformat, pprint
from pyreprint.integrations.rich import RichPrinter, console, rprint

__all__ = [
    # Rich
    "RichPrinter",
    "console",
    "rprint",
    # PrettyPrint
    "pprint",
    "pformat",
]

