# PyRePrint

Enhanced `print()` with decorators, formatting, and style patterns.

## Installation

```bash
pip install pyreprint
```

## Quick Start

```python
from pyreprint import reprint

# Standard print behavior
reprint("Hello, World!")

# With decorators
reprint("Section Title", before="=", after="=", width=40)
# ========================================
# Section Title
# ========================================

# Using styles
reprint("Important!", style="banner", width=40)
# ****************************************
# *             Important!               *
# ****************************************
```

## Decorator Functions

```python
from pyreprint import line, header, box, banner

print(line("=", 40))        # ========================================
print(header("Title"))      # Title\n=====
print(box("Content"))       # +-------+\n| Content |\n+-------+
print(banner("WELCOME", width=40))
```

## Built-in Styles

```python
from pyreprint import reprint

reprint("Text", style="section")   # Lines above and below
reprint("Text", style="header")    # Underlined
reprint("Text", style="box")       # In a box
reprint("Text", style="banner")    # Centered banner
reprint("Text", style="success")   # [OK] Text
reprint("Text", style="warning")   # !! WARNING !! Text
reprint("Text", style="error")     # [ERROR] Text
```

## Custom Styles

```python
from pyreprint import register_style, reprint

@register_style("custom")
def custom_style(text, **kwargs):
    return f">>> {text} <<<"

reprint("Hello", style="custom")  # >>> Hello <<<
```

## Output Capture

```python
from pyreprint import capture_output

with capture_output() as captured:
    print("This is captured")

print(captured.stdout)  # "This is captured\n"
```

## Rich Integration

```python
from pyreprint import rprint, panel, rule

rprint("[bold red]Error:[/bold red] Something went wrong")
rule("Section")
panel("Important", title="Notice")
```

## Sklearn-style Repr

```python
from pyreprint import ReprMixin

class MyModel(ReprMixin):
    def __init__(self, alpha=1.0, max_iter=100):
        self.alpha = alpha
        self.max_iter = max_iter

model = MyModel(alpha=0.5)
print(model)  # MyModel(alpha=0.5, max_iter=100)
```

## Documentation

Full documentation: https://colinconwell.github.io/PyRePrint

## License

GPL-3.0-or-later
