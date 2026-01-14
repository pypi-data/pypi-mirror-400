# Custom Styles Tutorial

Learn how to create and use custom styles in PyRePrint.

## Understanding Styles

Styles are functions that transform text into formatted output. They receive the text content and optional parameters, returning the styled string.

## Creating a Style

### Using the Decorator

The simplest way to create a style is with `@register_style`:

```python
from pyreprint import register_style, reprint

@register_style("emphasis")
def emphasis_style(text, **kwargs):
    return f"*** {text} ***"

# Use it
reprint("Important", style="emphasis")
# Output: *** Important ***
```

### Style Function Signature

Style functions should follow this pattern:

```python
def my_style(text: str, width: int = 60, **kwargs) -> str:
    # Transform text
    return transformed_text
```

- `text`: The content to style (required)
- `width`: Common parameter for width-based formatting
- `**kwargs`: Catch additional parameters for flexibility

## Practical Style Examples

### Bordered Section

```python
@register_style("bordered")
def bordered_style(text, width=60, char="#", **kwargs):
    border = char * width
    padding = char + " " * (width - 2) + char
    centered = text.center(width - 4)
    content = f"{char} {centered} {char}"
    return f"{border}\n{padding}\n{content}\n{padding}\n{border}"
```

### Code Block

```python
@register_style("code")
def code_style(text, language="", **kwargs):
    if language:
        return f"```{language}\n{text}\n```"
    return f"```\n{text}\n```"
```

### Timestamp

```python
from datetime import datetime

@register_style("timestamped")
def timestamped_style(text, **kwargs):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{now}] {text}"
```

### Multi-line Box

```python
@register_style("multibox")
def multibox_style(text, width=0, char="|", corner="+", horizontal="-", **kwargs):
    lines = text.split("\n")
    max_len = max(len(line) for line in lines)
    effective_width = width if width > 0 else max_len + 4

    border = corner + horizontal * (effective_width - 2) + corner
    result = [border]

    for line in lines:
        padded = line.center(effective_width - 4)
        result.append(f"{char} {padded} {char}")

    result.append(border)
    return "\n".join(result)
```

## Loading Styles from Files

### YAML Configuration

Create a `styles.yaml` file:

```yaml
styles:
  alert:
    before:
      char: "!"
      width: 40
    after:
      char: "!"
      width: 40
    prefix: "[ALERT] "

  quiet:
    prefix: "  "
    suffix: ""

  centered:
    center: true
    before:
      char: "-"
      width: 60
    after:
      char: "-"
      width: 60
```

Load and use:

```python
from pyreprint import load_styles_from_file, reprint

load_styles_from_file("styles.yaml")

reprint("System Alert", style="alert")
reprint("Quiet message", style="quiet")
reprint("Centered Text", style="centered")
```

### TOML Configuration

Create a `styles.toml` file:

```toml
[styles.notice]
prefix = "[*] "

[styles.divider]
before = { char = "~", width = 50 }
after = { char = "~", width = 50 }
```

Load it:

```python
from pyreprint import load_styles_from_file

load_styles_from_file("styles.toml")
```

### Dictionary Configuration

For programmatic configuration:

```python
from pyreprint import load_styles_from_dict

config = {
    "highlight": {
        "prefix": ">>> ",
        "suffix": " <<<",
    },
    "muted": {
        "prefix": "    ",
    }
}

load_styles_from_dict(config)
```

## Managing the Style Registry

### Listing Available Styles

```python
from pyreprint import list_styles

print("Available styles:")
for style in list_styles():
    print(f"  - {style}")
```

### Checking Style Existence

```python
from pyreprint import registry

if "custom" in registry:
    reprint("Text", style="custom")
else:
    reprint("Text")  # Fallback
```

### Removing Styles

```python
from pyreprint import registry

registry.unregister("temporary_style")
```

### Clearing All Styles

```python
from pyreprint import registry

registry.clear()
# Note: Built-in styles will be gone until you re-import
```

## Style Composition

Create styles that build on others:

```python
@register_style("urgent")
def urgent_style(text, **kwargs):
    from pyreprint.styles.builtins import banner_style
    return banner_style(f"URGENT: {text}", width=60, char="!")

@register_style("section_header")
def section_header_style(text, width=60, **kwargs):
    line = "=" * width
    return f"\n{line}\n{text.upper()}\n{line}\n"
```

## Best Practices

1. **Accept `**kwargs`**: Always include `**kwargs` for forward compatibility

2. **Document your styles**: Add docstrings explaining usage

3. **Handle edge cases**: Check for empty text, very long text, etc.

4. **Use sensible defaults**: Provide good default values for all parameters

5. **Organize styles**: Group related styles in separate files

```python
@register_style("robust")
def robust_style(text, width=60, fallback="(empty)", **kwargs):
    """A robust style that handles edge cases.

    Args:
        text: Content to style
        width: Output width
        fallback: Text to use if input is empty
    """
    if not text or not text.strip():
        text = fallback

    if len(text) > width - 4:
        text = text[:width - 7] + "..."

    return f"[ {text.center(width - 4)} ]"
```

## Next Steps

- Learn about [Jupyter Integration](jupyter-integration.md)
- See the [Styles API Reference](../api/styles.md)

