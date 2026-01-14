"""HTML formatting for Jupyter notebook display."""

from __future__ import annotations

import html
from typing import Any, Dict, Optional

# CSS styles for different themes
STYLES = {
    "sklearn": """
        <style>
        .pyreprint-repr {
            font-family: 'SF Mono', 'Menlo', 'Monaco', 'Consolas', monospace;
            font-size: 13px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 8px 0;
            display: inline-block;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .pyreprint-repr .class-name {
            color: #0d6efd;
            font-weight: 600;
        }
        .pyreprint-repr .param-name {
            color: #6f42c1;
        }
        .pyreprint-repr .param-value {
            color: #198754;
        }
        .pyreprint-repr .param-value.string {
            color: #d63384;
        }
        .pyreprint-repr .param-value.number {
            color: #fd7e14;
        }
        .pyreprint-repr .punctuation {
            color: #495057;
        }
        </style>
    """,
    "dark": """
        <style>
        .pyreprint-repr {
            font-family: 'SF Mono', 'Menlo', 'Monaco', 'Consolas', monospace;
            font-size: 13px;
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 8px 0;
            display: inline-block;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            color: #d4d4d4;
        }
        .pyreprint-repr .class-name {
            color: #569cd6;
            font-weight: 600;
        }
        .pyreprint-repr .param-name {
            color: #9cdcfe;
        }
        .pyreprint-repr .param-value {
            color: #b5cea8;
        }
        .pyreprint-repr .param-value.string {
            color: #ce9178;
        }
        .pyreprint-repr .param-value.number {
            color: #b5cea8;
        }
        .pyreprint-repr .punctuation {
            color: #808080;
        }
        </style>
    """,
    "minimal": """
        <style>
        .pyreprint-repr {
            font-family: monospace;
            font-size: 13px;
            padding: 8px;
            display: inline-block;
        }
        .pyreprint-repr .class-name {
            font-weight: bold;
        }
        </style>
    """,
}


def _get_value_class(value: Any) -> str:
    """Get CSS class for a value based on its type."""
    if isinstance(value, str):
        return "string"
    elif isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, bool):
        return "bool"
    return ""


def _format_html_value(value: Any, max_len: int = 40) -> str:
    """Format a value for HTML display.

    Args:
        value: The value to format.
        max_len: Maximum length before truncation.

    Returns:
        HTML-escaped string representation.
    """
    if isinstance(value, str):
        if len(value) > max_len:
            display = value[: max_len - 3] + "..."
        else:
            display = value
        return f"'{html.escape(display)}'"
    elif isinstance(value, (list, tuple)):
        if len(value) > 5:
            return f"{type(value).__name__}[{len(value)} items]"
        return html.escape(repr(value))
    elif isinstance(value, dict):
        if len(value) > 5:
            return f"dict[{len(value)} items]"
        return html.escape(repr(value))
    else:
        s = repr(value)
        if len(s) > max_len:
            s = s[: max_len - 3] + "..."
        return html.escape(s)


def html_repr(
    obj: Any,
    style: str = "sklearn",
    params: Optional[Dict[str, Any]] = None,
    collapsible: bool = False,
) -> str:
    """Generate HTML representation of an object.

    Args:
        obj: The object to format.
        style: Style theme ('sklearn', 'dark', 'minimal').
        params: Dictionary of parameter names to values.
                If None, attempts to extract from object.
        collapsible: Whether to make the repr collapsible.

    Returns:
        HTML string representation.

    Example:
        >>> class MyClass:
        ...     def __init__(self, a=1):
        ...         self.a = a
        >>> obj = MyClass()
        >>> html = html_repr(obj)
    """
    class_name = obj.__class__.__name__

    # Get parameters
    if params is None:
        from pyreprint.formatting.repr import _get_param_names

        param_names = _get_param_names(obj.__class__)
        params = {}
        for name in param_names:
            if hasattr(obj, name):
                params[name] = getattr(obj, name)
            elif hasattr(obj, f"_{name}"):
                params[name] = getattr(obj, f"_{name}")

    # Get CSS
    css = STYLES.get(style, STYLES["sklearn"])

    # Build HTML
    parts = []
    parts.append(css)

    if collapsible:
        parts.append('<details class="pyreprint-repr">')
        summary = f'<span class="class-name">{html.escape(class_name)}</span>(...)'
        parts.append(f"<summary>{summary}</summary>")
        parts.append('<div style="padding-left: 20px; margin-top: 8px;">')

        for name, value in params.items():
            value_class = _get_value_class(value)
            value_str = _format_html_value(value)
            parts.append(
                f'<div><span class="param-name">{html.escape(name)}</span>'
                f'<span class="punctuation">=</span>'
                f'<span class="param-value {value_class}">{value_str}</span></div>'
            )

        parts.append("</div>")
        parts.append("</details>")
    else:
        parts.append('<span class="pyreprint-repr">')
        parts.append(f'<span class="class-name">{html.escape(class_name)}</span>')
        parts.append('<span class="punctuation">(</span>')

        param_parts = []
        for name, value in params.items():
            value_class = _get_value_class(value)
            value_str = _format_html_value(value)
            param_parts.append(
                f'<span class="param-name">{html.escape(name)}</span>'
                f'<span class="punctuation">=</span>'
                f'<span class="param-value {value_class}">{value_str}</span>'
            )

        parts.append('<span class="punctuation">, </span>'.join(param_parts))
        parts.append('<span class="punctuation">)</span>')
        parts.append("</span>")

    return "".join(parts)


class HTMLFormatter:
    """Configurable HTML formatter for objects.

    This class provides a reusable formatter with customizable settings.

    Args:
        style: Style theme ('sklearn', 'dark', 'minimal').
        collapsible: Whether to make repr collapsible by default.
        max_value_length: Maximum length for value representations.

    Example:
        >>> formatter = HTMLFormatter(style='dark', collapsible=True)
        >>> html = formatter.format(my_object)
    """

    def __init__(
        self,
        style: str = "sklearn",
        collapsible: bool = False,
        max_value_length: int = 40,
    ) -> None:
        self.style = style
        self.collapsible = collapsible
        self.max_value_length = max_value_length

    def format(
        self,
        obj: Any,
        params: Optional[Dict[str, Any]] = None,
        collapsible: Optional[bool] = None,
    ) -> str:
        """Format an object as HTML.

        Args:
            obj: The object to format.
            params: Optional parameter dictionary override.
            collapsible: Override default collapsible setting.

        Returns:
            HTML string representation.
        """
        use_collapsible = collapsible if collapsible is not None else self.collapsible
        return html_repr(
            obj,
            style=self.style,
            params=params,
            collapsible=use_collapsible,
        )

    def __call__(self, obj: Any, **kwargs: Any) -> str:
        """Format an object (shortcut for format method)."""
        return self.format(obj, **kwargs)


def display_html(obj: Any, **kwargs: Any) -> None:
    """Display an object's HTML repr in Jupyter.

    Args:
        obj: The object to display.
        **kwargs: Arguments passed to html_repr.
    """
    try:
        from IPython.display import HTML, display

        html_str = html_repr(obj, **kwargs)
        display(HTML(html_str))
    except ImportError:
        # Not in Jupyter, fall back to print
        print(repr(obj))

