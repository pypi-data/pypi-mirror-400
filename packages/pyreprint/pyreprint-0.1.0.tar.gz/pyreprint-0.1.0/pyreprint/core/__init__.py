"""Core functionality for pyreprint."""

from pyreprint.core.capture import (
    CapturedOutput,
    OutputTee,
    capture_output,
    redirect_to_file,
)
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
from pyreprint.core.printer import Printer, reprint

__all__ = [
    # Printer
    "Printer",
    "reprint",
    # Decorators
    "Line",
    "Box",
    "Header",
    "Banner",
    "line",
    "box",
    "header",
    "banner",
    # Capture
    "capture_output",
    "redirect_to_file",
    "CapturedOutput",
    "OutputTee",
]

