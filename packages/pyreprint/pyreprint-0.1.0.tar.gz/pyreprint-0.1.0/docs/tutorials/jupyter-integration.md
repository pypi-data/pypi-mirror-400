# Jupyter Integration Tutorial

PyRePrint provides special features for Jupyter notebooks, including HTML formatting and rich output display.

## ReprMixin for Custom Classes

The `ReprMixin` class automatically provides scikit-learn style `__repr__` and `_repr_html_` methods:

```python
from pyreprint import ReprMixin

class MyModel(ReprMixin):
    def __init__(self, alpha=1.0, max_iter=100, verbose=False):
        self.alpha = alpha
        self.max_iter = max_iter
        self.verbose = verbose

model = MyModel(alpha=0.5)
```

In a Jupyter cell:

```python
model  # Displays nicely formatted HTML
```

In terminal:

```python
print(model)
# Output: MyModel(alpha=0.5, max_iter=100, verbose=False)
```

## Customizing ReprMixin

Configure the mixin behavior:

```python
class MyEstimator(ReprMixin):
    _repr_max_line_length = 100  # Wider output
    _repr_compact = True         # Prefer single-line
    _repr_html_style = "dark"    # Dark theme for HTML

    def __init__(self, param1=1, param2="value"):
        self.param1 = param1
        self.param2 = param2
```

## HTML Styles

Three built-in styles are available:

### sklearn (default)

Light theme with colored syntax highlighting:

```python
from pyreprint import HTMLFormatter

formatter = HTMLFormatter(style="sklearn")
```

### dark

Dark theme suitable for dark notebook themes:

```python
formatter = HTMLFormatter(style="dark")
```

### minimal

Plain, unstyled output:

```python
formatter = HTMLFormatter(style="minimal")
```

## Direct HTML Formatting

Use `html_repr` for one-off formatting:

```python
from pyreprint import html_repr
from IPython.display import HTML, display

class Config:
    def __init__(self, debug=False, port=8080):
        self.debug = debug
        self.port = port

config = Config(debug=True)
html = html_repr(config, style="sklearn")
display(HTML(html))
```

## Collapsible Output

For objects with many parameters, use collapsible display:

```python
from pyreprint import html_repr
from IPython.display import HTML, display

html = html_repr(large_object, collapsible=True)
display(HTML(html))
```

This creates a collapsible `<details>` element.

## Using display_html

The convenience function `display_html` combines formatting and display:

```python
from pyreprint import display_html

class Pipeline(ReprMixin):
    def __init__(self, steps=None, memory=None, verbose=False):
        self.steps = steps or []
        self.memory = memory
        self.verbose = verbose

pipeline = Pipeline(steps=["preprocess", "model", "postprocess"])
display_html(pipeline, style="dark", collapsible=True)
```

## Output Capture in Notebooks

Capture cell output for later use:

```python
from pyreprint import capture_output

with capture_output() as captured:
    print("Processing data...")
    # ... complex output ...
    print("Done!")

# Store for later
log = captured.stdout

# Or replay
captured.print_stdout()
```

## Rich Output in Notebooks

Rich formatting works in Jupyter with proper terminal emulation:

```python
from pyreprint import rprint, panel, rule

rprint("[bold blue]Analysis Results[/bold blue]")
rule("Summary")
panel("Key findings here", title="Findings")
```

## Pretty Printing Data Structures

Use `pprint` for complex data:

```python
from pyreprint import pprint

data = {
    "users": [
        {"name": "Alice", "scores": [95, 87, 92]},
        {"name": "Bob", "scores": [78, 82, 80]},
    ],
    "metadata": {"version": 2, "format": "json"}
}

pprint(data)
```

## Complete Notebook Example

```python
# Cell 1: Imports
from pyreprint import (
    reprint, ReprMixin, display_html,
    capture_output, rprint, panel
)

# Cell 2: Define model class
class Classifier(ReprMixin):
    _repr_html_style = "sklearn"

    def __init__(self, n_estimators=100, max_depth=None, random_state=42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

# Cell 3: Create and display
clf = Classifier(n_estimators=200, max_depth=10)
clf  # Rich HTML display

# Cell 4: Training with captured output
with capture_output() as log:
    for i in range(3):
        print(f"Epoch {i+1}: loss=0.{9-i}")

print("Training log:")
print(log.stdout)

# Cell 5: Results
rprint("[bold green]Training Complete![/bold green]")
panel(
    f"Model: {clf.__class__.__name__}\n"
    f"Parameters: {clf.get_params()}",
    title="Summary"
)
```

## Tips for Notebooks

1. **Use ReprMixin** for all custom classes that will be displayed

2. **Choose appropriate styles** based on notebook theme

3. **Capture verbose output** to keep notebooks clean

4. **Use collapsible display** for objects with many parameters

5. **Combine with Rich** for colorful, formatted output

## Next Steps

- See the [Repr API Reference](../api/repr.md)
- Explore [Rich Integration](../api/rich.md)
- Check the [Example Notebooks](../../examples/notebooks/)

