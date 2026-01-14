"""Pretty print integration for pyreprint."""

from __future__ import annotations

import pprint as _pprint
import sys
from typing import Any, Optional, TextIO


def pprint(
    obj: Any,
    stream: Optional[TextIO] = None,
    indent: int = 1,
    width: int = 80,
    depth: Optional[int] = None,
    compact: bool = False,
    sort_dicts: bool = True,
) -> None:
    """Pretty print an object.

    Enhanced wrapper around the standard pprint module.

    Args:
        obj: Object to print.
        stream: Output stream (default: sys.stdout).
        indent: Indentation level for nested structures.
        width: Maximum line width.
        depth: Maximum depth to print (None for unlimited).
        compact: Use compact format for sequences.
        sort_dicts: Sort dictionary keys.

    Example:
        >>> pprint({"a": [1, 2, 3], "b": {"nested": "value"}})
        {'a': [1, 2, 3], 'b': {'nested': 'value'}}
    """
    _pprint.pprint(
        obj,
        stream=stream,
        indent=indent,
        width=width,
        depth=depth,
        compact=compact,
        sort_dicts=sort_dicts,
    )


def pformat(
    obj: Any,
    indent: int = 1,
    width: int = 80,
    depth: Optional[int] = None,
    compact: bool = False,
    sort_dicts: bool = True,
) -> str:
    """Format an object as a pretty-printed string.

    Args:
        obj: Object to format.
        indent: Indentation level for nested structures.
        width: Maximum line width.
        depth: Maximum depth to print (None for unlimited).
        compact: Use compact format for sequences.
        sort_dicts: Sort dictionary keys.

    Returns:
        Pretty-printed string representation.

    Example:
        >>> s = pformat({"key": "value"})
        >>> print(s)
        {'key': 'value'}
    """
    return _pprint.pformat(
        obj,
        indent=indent,
        width=width,
        depth=depth,
        compact=compact,
        sort_dicts=sort_dicts,
    )


class PrettyPrinter:
    """Configurable pretty printer.

    This class provides a reusable pretty printer with customizable settings.

    Args:
        indent: Indentation level for nested structures.
        width: Maximum line width.
        depth: Maximum depth to print (None for unlimited).
        compact: Use compact format for sequences.
        sort_dicts: Sort dictionary keys.
        stream: Default output stream.

    Example:
        >>> pp = PrettyPrinter(indent=2, width=60)
        >>> pp.pprint({"a": [1, 2, 3]})
    """

    def __init__(
        self,
        indent: int = 1,
        width: int = 80,
        depth: Optional[int] = None,
        compact: bool = False,
        sort_dicts: bool = True,
        stream: Optional[TextIO] = None,
    ) -> None:
        self.indent = indent
        self.width = width
        self.depth = depth
        self.compact = compact
        self.sort_dicts = sort_dicts
        self.stream = stream or sys.stdout
        self._pp = _pprint.PrettyPrinter(
            indent=indent,
            width=width,
            depth=depth,
            compact=compact,
            sort_dicts=sort_dicts,
            stream=self.stream,
        )

    def pprint(self, obj: Any) -> None:
        """Pretty print an object.

        Args:
            obj: Object to print.
        """
        self._pp.pprint(obj)

    def pformat(self, obj: Any) -> str:
        """Format an object as a pretty-printed string.

        Args:
            obj: Object to format.

        Returns:
            Pretty-printed string representation.
        """
        return self._pp.pformat(obj)

    def isreadable(self, obj: Any) -> bool:
        """Check if object repr is readable.

        Args:
            obj: Object to check.

        Returns:
            True if repr is readable Python code.
        """
        return self._pp.isreadable(obj)

    def isrecursive(self, obj: Any) -> bool:
        """Check if object has recursive reference.

        Args:
            obj: Object to check.

        Returns:
            True if object has recursive reference.
        """
        return self._pp.isrecursive(obj)

    def __call__(self, obj: Any) -> None:
        """Pretty print an object (shortcut for pprint).

        Args:
            obj: Object to print.
        """
        self.pprint(obj)

