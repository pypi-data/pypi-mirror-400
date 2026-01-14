#!/usr/bin/env python
"""Rich library integration examples for PyRePrint."""

from pyreprint import (
    RichPrinter,
    panel,
    pformat,
    pprint,
    reprint,
    rprint,
    rule,
)


def main():
    reprint("Rich Integration Examples", style="banner", width=60)
    reprint("")

    # =========================================================================
    # Basic Rich Printing
    # =========================================================================

    reprint("1. Basic Rich Printing", style="header")

    rprint("[bold]Bold text[/bold]")
    rprint("[italic]Italic text[/italic]")
    rprint("[underline]Underlined text[/underline]")
    rprint("[strike]Strikethrough text[/strike]")
    rprint("")

    # =========================================================================
    # Colors
    # =========================================================================

    reprint("2. Colors", style="header")

    rprint("[red]Red text[/red]")
    rprint("[green]Green text[/green]")
    rprint("[blue]Blue text[/blue]")
    rprint("[yellow]Yellow text[/yellow]")
    rprint("[magenta]Magenta text[/magenta]")
    rprint("[cyan]Cyan text[/cyan]")
    rprint("")

    # Combined styles
    rprint("[bold red]Bold red[/bold red]")
    rprint("[italic blue]Italic blue[/italic blue]")
    rprint("[bold underline green]Bold underline green[/bold underline green]")
    rprint("")

    # =========================================================================
    # Rules
    # =========================================================================

    reprint("3. Horizontal Rules", style="header")

    rule()
    rule("With Title")
    rule("Styled", style="bold blue")
    rprint("")

    # =========================================================================
    # Panels
    # =========================================================================

    reprint("4. Panels", style="header")

    panel("Simple panel content")
    rprint("")

    panel(
        "Panel with a title\nand multiple lines\nof content",
        title="Notice"
    )
    rprint("")

    panel(
        "[bold]Important:[/bold] This is a styled panel",
        title="Alert",
        border_style="red"
    )
    rprint("")

    # =========================================================================
    # RichPrinter Class
    # =========================================================================

    reprint("5. RichPrinter Class", style="header")

    printer = RichPrinter()

    printer.print("[bold cyan]Using RichPrinter instance[/bold cyan]")
    printer.rule("Section Divider")
    printer.header("Header Text")
    printer.section("Section Title")
    printer.panel("Panel via RichPrinter", title="Demo")
    rprint("")

    # Status messages
    printer.status("Information message", "info")
    printer.status("Success message", "success")
    printer.status("Warning message", "warning")
    printer.status("Error message", "error")
    rprint("")

    # =========================================================================
    # Tables
    # =========================================================================

    reprint("6. Tables", style="header")

    data = [
        ["Alice", 95, "A"],
        ["Bob", 82, "B"],
        ["Charlie", 78, "C+"],
        ["Diana", 91, "A-"],
    ]

    printer.table(
        data,
        headers=["Name", "Score", "Grade"],
        title="Student Grades"
    )
    rprint("")

    # =========================================================================
    # Pretty Printing
    # =========================================================================

    reprint("7. Pretty Printing", style="header")

    complex_data = {
        "name": "PyRePrint",
        "version": "0.1.0",
        "features": [
            "Enhanced print",
            "Decorators",
            "Styles",
            "Rich integration",
        ],
        "config": {
            "default_width": 60,
            "use_rich": True,
            "styles": {
                "section": {"before": "=", "after": "="},
                "header": {"after": "="},
            },
        },
    }

    rprint("[bold]pprint output:[/bold]")
    pprint(complex_data)
    rprint("")

    # pformat for string conversion
    formatted = pformat(complex_data)
    rprint(f"[bold]pformat returns string of length:[/bold] {len(formatted)}")
    rprint("")

    # =========================================================================
    # Combining with reprint
    # =========================================================================

    reprint("8. Combining Rich with reprint", style="header")

    # Use reprint with rich=True
    reprint(
        "[bold magenta]This uses reprint with Rich enabled[/bold magenta]",
        rich=True
    )

    # Decorators work with rich output
    reprint(
        "[green]Content with decorators[/green]",
        before="~",
        after="~",
        width=50,
        rich=True
    )
    rprint("")

    # =========================================================================
    # Practical Example: Report Generator
    # =========================================================================

    reprint("9. Practical Example: Report Generator", style="header")

    def generate_report(title, sections):
        """Generate a formatted report."""
        rprint(f"\n[bold blue]{'=' * 60}[/bold blue]")
        rprint(f"[bold blue]{title.center(60)}[/bold blue]")
        rprint(f"[bold blue]{'=' * 60}[/bold blue]\n")

        for section_title, content in sections.items():
            rule(section_title, style="cyan")

            if isinstance(content, dict):
                for key, value in content.items():
                    rprint(f"  [bold]{key}:[/bold] {value}")
            elif isinstance(content, list):
                for item in content:
                    rprint(f"  [dim]-[/dim] {item}")
            else:
                rprint(f"  {content}")

            rprint("")

    report_data = {
        "Summary": {
            "Status": "[green]Complete[/green]",
            "Duration": "2.3 seconds",
            "Items Processed": 1247,
        },
        "Key Findings": [
            "Performance improved by 15%",
            "No critical errors detected",
            "Memory usage within limits",
        ],
        "Recommendations": [
            "Continue monitoring",
            "Schedule next review",
            "Update documentation",
        ],
    }

    generate_report("System Analysis Report", report_data)

    reprint("Examples Complete!", style="banner", width=60)


if __name__ == "__main__":
    main()

