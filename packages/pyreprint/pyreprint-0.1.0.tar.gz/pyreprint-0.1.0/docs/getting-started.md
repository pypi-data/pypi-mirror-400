# Getting Started

This guide covers the essentials of using PyRePrint.

## Installation

Install PyRePrint using pip:

```bash
pip install pyreprint
```

For development, clone the repository and install with dev dependencies:

```bash
git clone https://github.com/colinconwell/PyRePrint.git
cd PyRePrint
pip install -e ".[dev]"
```

## Basic Usage

### The `reprint` Function

The main function in PyRePrint is `reprint()`, which works exactly like Python's built-in `print()` but with additional parameters:

```python
from pyreprint import reprint

# Works just like print()
reprint("Hello, World!")
reprint("Multiple", "values", sep=", ")
```

### Adding Decorators

Use the `before`, `after`, or `surround` parameters to add decorators:

```python
# Add a line before the text
reprint("Title", before="=", width=40)

# Add a line after the text
reprint("Title", after="-", width=40)

# Add lines both before and after
reprint("Section", surround="=", width=40)
```

### Using Named Styles

Apply pre-defined styles with the `style` parameter:

```python
reprint("Header", style="header")
reprint("Boxed Content", style="box")
reprint("Important", style="banner", width=50)
reprint("Notice", style="warning")
```

Built-in styles include:

- `section` - Lines above and below
- `header` - Text with underline
- `divider` - Softer divider style
- `box` - Text in a box
- `banner` - Full-width centered text
- `title` - Prominent title format
- `quote` - Blockquote style
- `highlight` - Attention markers
- `warning`, `error`, `success`, `info` - Status messages

## Decorator Classes

For more control, use the decorator classes directly:

### Line

```python
from pyreprint import Line, line

# Using the class
my_line = Line(char="=", width=60)
print(my_line)

# Using the convenience function
print(line("=", 60))
```

### Header

```python
from pyreprint import Header, header

# With underline only
print(header("My Section", char="="))

# With line above and below
print(header("My Section", char="=", above=True))
```

### Box

```python
from pyreprint import Box, box

# Basic box
print(box("Hello World"))

# Custom box characters
print(box("Content", char="|", corner="+", horizontal="-"))
```

### Banner

```python
from pyreprint import Banner, banner

# Full-width banner
print(banner("WELCOME"))

# Fixed-width banner with padding
print(banner("TITLE", width=40, padding_lines=1))
```

## Capturing Output

Use `capture_output()` to capture stdout and stderr:

```python
from pyreprint import capture_output
import sys

with capture_output() as captured:
    print("Standard output")
    print("Error output", file=sys.stderr)

print(f"stdout: {captured.stdout}")
print(f"stderr: {captured.stderr}")
```

### Redirecting to File

```python
from pyreprint import redirect_to_file

with redirect_to_file("output.txt"):
    print("This goes to the file")
```

### Output Tee

Write to multiple destinations:

```python
from pyreprint import OutputTee

with open("log.txt", "w") as f:
    tee = OutputTee(f, include_stdout=True)
    with tee.activate():
        print("Goes to both console and file")
```

## Custom Styles

### Registering Styles

Define custom styles using the `@register_style` decorator:

```python
from pyreprint import register_style, reprint

@register_style("custom")
def my_custom_style(text, width=60, **kwargs):
    border = "#" * width
    centered = text.center(width - 4)
    return f"{border}\n# {centered} #\n{border}"

reprint("Custom Style!", style="custom")
```

### Loading Styles from Files

Load styles from YAML or TOML files:

```python
from pyreprint import load_styles_from_file

# styles.yaml:
# styles:
#   mydivider:
#     before:
#       char: "-"
#       width: 40
#     after:
#       char: "-"
#       width: 40

load_styles_from_file("styles.yaml")
reprint("Text", style="mydivider")
```

## Rich Integration

PyRePrint includes Rich library integration:

```python
from pyreprint import rprint, rule, panel

# Rich-formatted print
rprint("[bold blue]Title[/bold blue]")
rprint("[italic]Emphasized text[/italic]")

# Horizontal rule
rule("Section")

# Panel
panel("Important content", title="Notice")
```

## Replacing Built-in Print

Optionally replace the built-in print:

```python
from pyreprint import install_print, uninstall_print

# Replace built-in print
original = install_print()

# Now print() uses reprint
print("Hello", before="=")

# Restore original
uninstall_print(original)
```

## Next Steps

- Explore the [API Reference](api/printer.md) for complete documentation
- Check out [Tutorials](tutorials/basic-usage.md) for more examples
- Learn about [Custom Styles](tutorials/custom-styles.md)

