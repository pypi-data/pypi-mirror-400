"""Rich library integration for pyreprint."""

from __future__ import annotations

import sys
from typing import Any, Optional, TextIO

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text


class RichPrinter:
    """Rich-enabled printer with enhanced formatting.

    This class provides a printer that leverages Rich for colorful,
    formatted console output.

    Args:
        console: Rich Console instance to use.
        force_terminal: Force terminal output even if not a TTY.
        width: Console width (None for auto-detect).

    Example:
        >>> printer = RichPrinter()
        >>> printer.print("Hello, [bold]World[/bold]!")
        >>> printer.rule("Section")
        >>> printer.panel("Important message", title="Notice")
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        force_terminal: bool = False,
        width: Optional[int] = None,
    ) -> None:
        self.console = console or Console(
            force_terminal=force_terminal,
            width=width,
        )

    def print(
        self,
        *args: Any,
        sep: str = " ",
        end: str = "\n",
        markup: bool = True,
        highlight: bool = True,
        **kwargs: Any,
    ) -> None:
        """Print with Rich formatting.

        Args:
            *args: Values to print.
            sep: Separator between values.
            end: String to append at end.
            markup: Whether to parse Rich markup.
            highlight: Whether to highlight syntax.
            **kwargs: Additional arguments for Console.print.
        """
        message = sep.join(str(arg) for arg in args)
        self.console.print(message, end=end, markup=markup, highlight=highlight, **kwargs)

    def rule(
        self,
        title: str = "",
        char: str = "-",
        style: str = "rule.line",
        align: str = "center",
    ) -> None:
        """Print a horizontal rule.

        Args:
            title: Optional title in the rule.
            char: Character for the line (Rich may override).
            style: Rich style for the rule.
            align: Title alignment ('left', 'center', 'right').
        """
        if title:
            self.console.print(Rule(title=title, style=style, align=align))  # type: ignore
        else:
            self.console.print(Rule(style=style))

    def panel(
        self,
        content: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        border_style: str = "blue",
        expand: bool = True,
    ) -> None:
        """Print content in a panel.

        Args:
            content: The panel content.
            title: Optional panel title.
            subtitle: Optional panel subtitle.
            border_style: Style for the border.
            expand: Whether to expand to full width.
        """
        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style=border_style,
            expand=expand,
        )
        self.console.print(panel)

    def header(
        self,
        text: str,
        style: str = "bold",
        rule_style: str = "rule.line",
    ) -> None:
        """Print a header with underline.

        Args:
            text: Header text.
            style: Style for the text.
            rule_style: Style for the underline.
        """
        self.console.print(Text(text, style=style))
        self.console.print(Rule(style=rule_style))

    def section(
        self,
        text: str,
        style: str = "bold blue",
    ) -> None:
        """Print a section with rules above and below.

        Args:
            text: Section text.
            style: Style for the text.
        """
        self.console.print(Rule())
        self.console.print(Text(text, style=style), justify="center")
        self.console.print(Rule())

    def table(
        self,
        data: list,
        headers: Optional[list] = None,
        title: Optional[str] = None,
    ) -> None:
        """Print data as a table.

        Args:
            data: List of rows (each row is a list of values).
            headers: Optional list of column headers.
            title: Optional table title.
        """
        table = Table(title=title)

        if headers:
            for header in headers:
                table.add_column(str(header))
        elif data:
            for i in range(len(data[0])):
                table.add_column(f"Column {i + 1}")

        for row in data:
            table.add_row(*[str(cell) for cell in row])

        self.console.print(table)

    def status(
        self,
        message: str,
        status_type: str = "info",
    ) -> None:
        """Print a status message with appropriate styling.

        Args:
            message: The status message.
            status_type: Type of status ('info', 'success', 'warning', 'error').
        """
        styles = {
            "info": ("[blue][INFO][/blue]", "blue"),
            "success": ("[green][OK][/green]", "green"),
            "warning": ("[yellow][WARN][/yellow]", "yellow"),
            "error": ("[red][ERROR][/red]", "red"),
        }
        prefix, style = styles.get(status_type, styles["info"])
        self.console.print(f"{prefix} {message}")


# Global console instance
console = Console()


def rprint(
    *args: Any,
    sep: str = " ",
    end: str = "\n",
    file: Optional[TextIO] = None,
    markup: bool = True,
    highlight: bool = True,
    **kwargs: Any,
) -> None:
    """Rich-enabled print function.

    A drop-in replacement for print() that uses Rich for formatting.

    Args:
        *args: Values to print.
        sep: Separator between values.
        end: String to append at end.
        file: Output file (uses Rich console if None).
        markup: Whether to parse Rich markup.
        highlight: Whether to highlight syntax.
        **kwargs: Additional arguments for Console.print.

    Example:
        >>> rprint("[bold red]Error:[/bold red] Something went wrong")
        >>> rprint("Processing...", style="italic")
    """
    if file is not None and file != sys.stdout:
        # Use standard print for non-stdout files
        message = sep.join(str(arg) for arg in args)
        print(message, end=end, file=file)
    else:
        message = sep.join(str(arg) for arg in args)
        console.print(message, end=end, markup=markup, highlight=highlight, **kwargs)


def rule(title: str = "", style: str = "rule.line") -> None:
    """Print a horizontal rule.

    Args:
        title: Optional title in the rule.
        style: Rich style for the rule.
    """
    if title:
        console.print(Rule(title=title, style=style))
    else:
        console.print(Rule(style=style))


def panel(
    content: str,
    title: Optional[str] = None,
    border_style: str = "blue",
) -> None:
    """Print content in a panel.

    Args:
        content: The panel content.
        title: Optional panel title.
        border_style: Style for the border.
    """
    console.print(
        Panel(content, title=title, border_style=border_style)
    )

