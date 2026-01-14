"""Core printer functionality for pyreprint."""

from __future__ import annotations

import sys
from typing import Any, Callable, Optional, TextIO

from pyreprint.core.decorators import DecoratorType, resolve_decorator


class Printer:
    """Enhanced printer with decorator and style support.

    The Printer class provides a configurable print function with
    support for decorators (lines before/after), styles, and rich
    integration.

    Args:
        width: Default width for decorators (0 = auto-detect).
        use_rich: Whether to use rich for output.
        default_style: Default style to apply to all prints.

    Example:
        >>> printer = Printer(width=60)
        >>> printer("Hello", before="=", after="=")
        ============================================================
        Hello
        ============================================================
    """

    def __init__(
        self,
        width: int = 0,
        use_rich: bool = False,
        default_style: Optional[str] = None,
    ) -> None:
        self.width = width
        self.use_rich = use_rich
        self.default_style = default_style

    def __call__(
        self,
        *args: Any,
        sep: str = " ",
        end: str = "\n",
        file: Optional[TextIO] = None,
        flush: bool = False,
        before: DecoratorType = None,
        after: DecoratorType = None,
        surround: DecoratorType = None,
        style: Optional[str] = None,
        width: Optional[int] = None,
        rich: Optional[bool] = None,
        markup: bool = True,
        **kwargs: Any,
    ) -> None:
        """Print with optional decorators and styling.

        Args:
            *args: Values to print (same as built-in print).
            sep: Separator between values.
            end: String to append at end.
            file: Output file (default: sys.stdout).
            flush: Whether to flush output.
            before: Decorator to print before the content.
            after: Decorator to print after the content.
            surround: Decorator for both before and after.
            style: Named style to apply.
            width: Width for decorators.
            rich: Whether to use rich for this print.
            markup: Whether to parse rich markup.
            **kwargs: Additional arguments for style functions.
        """
        output_file = file or sys.stdout
        effective_width = width or self.width

        # Handle surround shortcut
        if surround is not None:
            before = before or surround
            after = after or surround

        # Apply style if specified
        effective_style = style or self.default_style
        if effective_style:
            self._apply_style(
                *args,
                sep=sep,
                end=end,
                file=output_file,
                flush=flush,
                style=effective_style,
                width=effective_width,
                **kwargs,
            )
            return

        # Determine if we should use rich
        use_rich_output = rich if rich is not None else self.use_rich

        # Print with decorators
        if use_rich_output:
            self._rich_print(
                *args,
                sep=sep,
                end=end,
                file=output_file,
                flush=flush,
                before=before,
                after=after,
                width=effective_width,
                markup=markup,
            )
        else:
            self._standard_print(
                *args,
                sep=sep,
                end=end,
                file=output_file,
                flush=flush,
                before=before,
                after=after,
                width=effective_width,
            )

    def _standard_print(
        self,
        *args: Any,
        sep: str,
        end: str,
        file: TextIO,
        flush: bool,
        before: DecoratorType,
        after: DecoratorType,
        width: int,
    ) -> None:
        """Print using standard print function."""
        # Print before decorator
        before_str = resolve_decorator(before, width=width)
        if before_str:
            print(before_str, file=file)

        # Print main content
        print(*args, sep=sep, end=end, file=file, flush=flush)

        # Print after decorator
        after_str = resolve_decorator(after, width=width)
        if after_str:
            print(after_str, file=file, flush=flush)

    def _rich_print(
        self,
        *args: Any,
        sep: str,
        end: str,
        file: TextIO,
        flush: bool,
        before: DecoratorType,
        after: DecoratorType,
        width: int,
        markup: bool,
    ) -> None:
        """Print using rich console."""
        try:
            from rich.console import Console

            console = Console(file=file, force_terminal=True)

            # Print before decorator
            before_str = resolve_decorator(before, width=width)
            if before_str:
                console.print(before_str, markup=markup)

            # Print main content
            message = sep.join(str(arg) for arg in args)
            console.print(message, end=end, markup=markup)

            # Print after decorator
            after_str = resolve_decorator(after, width=width)
            if after_str:
                console.print(after_str, markup=markup)

            if flush:
                file.flush()

        except ImportError:
            # Fallback to standard print if rich not available
            self._standard_print(
                *args,
                sep=sep,
                end=end,
                file=file,
                flush=flush,
                before=before,
                after=after,
                width=width,
            )

    def _apply_style(
        self,
        *args: Any,
        sep: str,
        end: str,
        file: TextIO,
        flush: bool,
        style: str,
        width: int,
        **kwargs: Any,
    ) -> None:
        """Apply a named style to the output."""
        # Import here to avoid circular imports
        from pyreprint.styles.registry import get_style

        style_func = get_style(style)
        if style_func is None:
            # Style not found, print with warning
            print(f"[Warning: Style '{style}' not found]", file=file)
            print(*args, sep=sep, end=end, file=file, flush=flush)
            return

        # Build content string
        content = sep.join(str(arg) for arg in args)

        # Apply style function
        styled_output = style_func(content, width=width, **kwargs)
        print(styled_output, end=end, file=file, flush=flush)

    def line(
        self,
        char: str = "=",
        width: Optional[int] = None,
        file: Optional[TextIO] = None,
    ) -> None:
        """Print a horizontal line.

        Args:
            char: Character for the line.
            width: Width of the line (0 = auto).
            file: Output file.
        """
        from pyreprint.core.decorators import line

        effective_width = width or self.width
        print(line(char, effective_width), file=file or sys.stdout)

    def header(
        self,
        text: str,
        char: str = "=",
        width: Optional[int] = None,
        above: bool = False,
        file: Optional[TextIO] = None,
    ) -> None:
        """Print a header with underline.

        Args:
            text: Header text.
            char: Underline character.
            width: Width of underline (0 = match text).
            above: Whether to include line above.
            file: Output file.
        """
        from pyreprint.core.decorators import header

        effective_width = width or self.width
        print(header(text, char, effective_width, above), file=file or sys.stdout)

    def box(
        self,
        text: str,
        char: str = "|",
        corner: str = "+",
        file: Optional[TextIO] = None,
    ) -> None:
        """Print text in a box.

        Args:
            text: Text to box.
            char: Vertical border character.
            corner: Corner character.
            file: Output file.
        """
        from pyreprint.core.decorators import box

        print(box(text, char, corner), file=file or sys.stdout)

    def banner(
        self,
        text: str,
        char: str = "*",
        width: Optional[int] = None,
        file: Optional[TextIO] = None,
    ) -> None:
        """Print a full-width banner.

        Args:
            text: Banner text.
            char: Border character.
            width: Width of banner (0 = auto).
            file: Output file.
        """
        from pyreprint.core.decorators import banner

        effective_width = width or self.width
        print(banner(text, char, effective_width), file=file or sys.stdout)


# Default printer instance
_default_printer = Printer()


def reprint(
    *args: Any,
    sep: str = " ",
    end: str = "\n",
    file: Optional[TextIO] = None,
    flush: bool = False,
    before: DecoratorType = None,
    after: DecoratorType = None,
    surround: DecoratorType = None,
    style: Optional[str] = None,
    width: Optional[int] = None,
    rich: Optional[bool] = None,
    markup: bool = True,
    **kwargs: Any,
) -> None:
    """Enhanced print function with decorator and style support.

    This is the main function of pyreprint, providing a drop-in
    replacement for the built-in print() with additional features.

    Args:
        *args: Values to print (same as built-in print).
        sep: Separator between values.
        end: String to append at end.
        file: Output file (default: sys.stdout).
        flush: Whether to flush output.
        before: Decorator to print before the content.
        after: Decorator to print after the content.
        surround: Decorator for both before and after.
        style: Named style to apply.
        width: Width for decorators (0 = auto).
        rich: Whether to use rich for this print.
        markup: Whether to parse rich markup.
        **kwargs: Additional arguments for style functions.

    Examples:
        Basic usage:
        >>> reprint("Hello, World!")
        Hello, World!

        With decorators:
        >>> reprint("Section", before="=", after="=", width=40)
        ========================================
        Section
        ========================================

        With style:
        >>> reprint("Important!", style="banner")
        ****************************************
        *             Important!               *
        ****************************************
    """
    _default_printer(
        *args,
        sep=sep,
        end=end,
        file=file,
        flush=flush,
        before=before,
        after=after,
        surround=surround,
        style=style,
        width=width,
        rich=rich,
        markup=markup,
        **kwargs,
    )


def install_print() -> Callable[..., None]:
    """Replace the built-in print with reprint.

    Returns:
        The original print function (for restoration if needed).

    Example:
        >>> original_print = install_print()
        >>> print("Now uses reprint!")  # Uses reprint
        >>> import builtins
        >>> builtins.print = original_print  # Restore
    """
    import builtins

    original = builtins.print
    builtins.print = reprint  # type: ignore[assignment]
    return original


def uninstall_print(original: Optional[Callable[..., None]] = None) -> None:
    """Restore the built-in print function.

    Args:
        original: The original print function to restore.
                  If None, restores the standard print.
    """
    import builtins

    if original is not None:
        builtins.print = original
    else:
        # Get the original from the builtins module itself
        import _io

        builtins.print = _io.TextIOWrapper.write  # type: ignore[assignment]

