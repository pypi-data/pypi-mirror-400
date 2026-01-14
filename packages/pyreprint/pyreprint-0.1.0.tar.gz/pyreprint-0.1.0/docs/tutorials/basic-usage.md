# Basic Usage Tutorial

This tutorial covers the fundamental usage patterns of PyRePrint.

## Getting Started

First, import the main function:

```python
from pyreprint import reprint
```

## Standard Printing

`reprint()` is fully compatible with Python's built-in `print()`:

```python
# Single value
reprint("Hello, World!")

# Multiple values
reprint("Name:", "PyRePrint", "Version:", "0.1.0")

# With separator
reprint("apple", "banana", "cherry", sep=", ")

# Without newline
reprint("Loading", end="")
reprint("...", end="")
reprint(" Done!")
```

## Adding Decorators

### Before and After

Add visual decorators before or after your content:

```python
# Line before
reprint("Title", before="=", width=40)
# Output:
# ========================================
# Title

# Line after
reprint("Title", after="-", width=40)
# Output:
# Title
# ----------------------------------------

# Both before and after
reprint("Section", before="=", after="=", width=40)
# Output:
# ========================================
# Section
# ========================================
```

### The Surround Shortcut

Use `surround` for the same decorator above and below:

```python
reprint("Centered Section", surround="*", width=40)
# Output:
# ****************************************
# Centered Section
# ****************************************
```

### Width Control

The `width` parameter controls decorator width:

```python
# Fixed width
reprint("Fixed", before="=", width=30)

# Auto-detect terminal width (default when width=0)
reprint("Full Width", before="=")
```

## Using Decorator Classes

For complex decorators, use the class instances:

```python
from pyreprint import Line, Header, Box, Banner

# Pass decorator objects directly
reprint("Content", before=Line("=", 50), after=Line("-", 50))

# Header with underline
from pyreprint import header
print(header("My Section", char="="))
# Output:
# My Section
# ==========

# Box around text
from pyreprint import box
print(box("Important Note"))
# Output:
# +----------------+
# | Important Note |
# +----------------+

# Full-width banner
from pyreprint import banner
print(banner("WELCOME", width=40))
# Output:
# ****************************************
# *              WELCOME                 *
# ****************************************
```

## Named Styles

Apply pre-defined formatting with the `style` parameter:

```python
# Section style
reprint("Major Section", style="section", width=40)
# Output:
# ========================================
# Major Section
# ========================================

# Header style
reprint("Subsection", style="header")
# Output:
# Subsection
# ==========

# Box style
reprint("Boxed Content", style="box")
# Output:
# +---------------+
# | Boxed Content |
# +---------------+

# Status styles
reprint("Operation complete", style="success")
# Output: [OK] Operation complete

reprint("Check this", style="warning")
# Output: !! WARNING !!
#         Check this

reprint("Failed", style="error")
# Output: [ERROR] Failed
```

## Combining Features

Features can be combined:

```python
# Style with custom width
reprint("Title", style="banner", width=50)

# Multiple values with decorators
reprint("Name:", user_name, before="=", width=40)
```

## Output to Files

Direct output to files:

```python
with open("output.txt", "w") as f:
    reprint("Logged message", file=f)
    reprint("With decorator", before="=", width=40, file=f)
```

## Practical Examples

### Script Header

```python
from pyreprint import reprint, banner

reprint(banner("DATA PROCESSING SCRIPT", width=60))
reprint("")
reprint("Configuration:", style="header")
reprint("  Input: data.csv")
reprint("  Output: results.json")
reprint("")
```

### Progress Sections

```python
from pyreprint import reprint

def process_step(name, func):
    reprint(f"Step: {name}", style="section", width=50)
    result = func()
    reprint(f"Completed: {name}", style="success")
    reprint("")
    return result
```

### Error Reporting

```python
from pyreprint import reprint

def report_error(message, details=None):
    reprint("ERROR", style="banner", width=40)
    reprint(message, style="error")
    if details:
        reprint(details, style="quote")
```

## Next Steps

- Learn about [Custom Styles](custom-styles.md)
- Explore [Jupyter Integration](jupyter-integration.md)
- See the [API Reference](../api/printer.md)

