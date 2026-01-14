# PyRePrint

Enhanced `print()` with decorators, formatting, and style patterns.

PyRePrint provides a drop-in replacement for Python's built-in `print()` function with powerful features for formatting terminal and notebook output.

## Installation

```bash
pip install pyreprint
```

## Quick Start

### Basic Usage

```python
from pyreprint import reprint

# Standard print behavior
reprint("Hello, World!")

# With decorators
reprint("Section Title", before="=", after="=", width=40)
```

Output:

```
========================================
Section Title
========================================
```

### Using Styles

```python
from pyreprint import reprint

reprint("Important Message", style="banner", width=40)
```

Output:

```
****************************************
*          Important Message           *
****************************************
```

### Decorator Functions

```python
from pyreprint import line, header, box, banner

print(line("=", 40))
print(header("My Header"))
print(box("Content in a box"))
print(banner("WELCOME", width=40))
```

### Output Capture

```python
from pyreprint import capture_output

with capture_output() as captured:
    print("This is captured")

print(f"Captured: {captured.stdout}")
```

### Rich Integration

```python
from pyreprint import rprint

rprint("[bold red]Error:[/bold red] Something went wrong")
rprint("[green]Success![/green] Operation completed")
```

## Key Concepts

### Decorators

Decorators are visual elements that can be added before or after your print output:

- **Line**: A horizontal line of repeated characters
- **Header**: Text with an underline
- **Box**: Text surrounded by a border
- **Banner**: Full-width centered text with borders

### Styles

Styles are named formatting presets that can be applied with a single parameter:

```python
reprint("Message", style="section")    # Lines above and below
reprint("Message", style="warning")    # Warning format
reprint("Message", style="box")        # Boxed output
```

### Custom Styles

Define your own styles using the `@register_style` decorator:

```python
from pyreprint import register_style, reprint

@register_style("highlight")
def my_highlight(text, **kwargs):
    return f">>> {text} <<<"

reprint("Important", style="highlight")
# Output: >>> Important <<<
```

## Next Steps

- [Getting Started Guide](getting-started.md) - Detailed introduction
- [API Reference](api/printer.md) - Complete API documentation
- [Tutorials](tutorials/basic-usage.md) - Step-by-step guides

