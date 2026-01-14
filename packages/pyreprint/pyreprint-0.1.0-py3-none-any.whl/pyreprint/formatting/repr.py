"""Scikit-learn style __repr__ formatting."""

from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional, Type


def _get_param_names(cls: Type[Any]) -> List[str]:
    """Get parameter names from class __init__ signature.

    Args:
        cls: The class to inspect.

    Returns:
        List of parameter names.
    """
    init = getattr(cls, "__init__", None)
    if init is None:
        return []

    try:
        sig = inspect.signature(init)
        return [
            p.name
            for p in sig.parameters.values()
            if p.name != "self" and p.kind != inspect.Parameter.VAR_KEYWORD
        ]
    except (ValueError, TypeError):
        return []


def _format_value(value: Any, max_len: int = 40) -> str:
    """Format a value for display in repr.

    Args:
        value: The value to format.
        max_len: Maximum length before truncation.

    Returns:
        Formatted string representation.
    """
    if isinstance(value, str):
        if len(value) > max_len:
            return repr(value[: max_len - 3] + "...")
        return repr(value)
    elif isinstance(value, (list, tuple)):
        if len(value) > 5:
            return f"{type(value).__name__}[{len(value)} items]"
        return repr(value)
    elif isinstance(value, dict):
        if len(value) > 5:
            return f"dict[{len(value)} items]"
        return repr(value)
    else:
        s = repr(value)
        if len(s) > max_len:
            return s[: max_len - 3] + "..."
        return s


def format_repr(
    obj: Any,
    params: Optional[Dict[str, Any]] = None,
    max_line_length: int = 80,
    compact: bool = True,
) -> str:
    """Format an object's repr in scikit-learn style.

    Args:
        obj: The object to format.
        params: Dictionary of parameter names to values.
                If None, attempts to extract from object.
        max_line_length: Maximum line length before wrapping.
        compact: Whether to use compact single-line format when possible.

    Returns:
        Formatted repr string.

    Example:
        >>> class MyClass:
        ...     def __init__(self, a=1, b="hello"):
        ...         self.a = a
        ...         self.b = b
        >>> obj = MyClass(a=42, b="world")
        >>> print(format_repr(obj))
        MyClass(a=42, b='world')
    """
    class_name = obj.__class__.__name__

    # Get parameters
    if params is None:
        param_names = _get_param_names(obj.__class__)
        params = {}
        for name in param_names:
            if hasattr(obj, name):
                params[name] = getattr(obj, name)
            elif hasattr(obj, f"_{name}"):
                params[name] = getattr(obj, f"_{name}")

    if not params:
        return f"{class_name}()"

    # Format parameter strings
    param_strs = [f"{k}={_format_value(v)}" for k, v in params.items()]

    # Try compact format first
    compact_repr = f"{class_name}({', '.join(param_strs)})"
    if compact and len(compact_repr) <= max_line_length:
        return compact_repr

    # Multi-line format
    indent = " " * (len(class_name) + 1)
    lines = [f"{class_name}({param_strs[0]},"]
    for param_str in param_strs[1:-1]:
        lines.append(f"{indent}{param_str},")
    if len(param_strs) > 1:
        lines.append(f"{indent}{param_strs[-1]})")
    else:
        lines[-1] = lines[-1].rstrip(",") + ")"

    return "\n".join(lines)


class ReprMixin:
    """Mixin providing scikit-learn style __repr__ and _repr_html_.

    This mixin automatically generates a formatted __repr__ based on
    the class's __init__ parameters. It also provides _repr_html_ for
    rich display in Jupyter notebooks.

    To use, simply inherit from this mixin:

    Example:
        >>> class MyEstimator(ReprMixin):
        ...     def __init__(self, alpha=1.0, max_iter=100):
        ...         self.alpha = alpha
        ...         self.max_iter = max_iter
        >>> est = MyEstimator(alpha=0.5)
        >>> print(est)
        MyEstimator(alpha=0.5, max_iter=100)

    Attributes:
        _repr_max_line_length: Maximum line length for repr.
        _repr_compact: Whether to use compact format when possible.
        _repr_html_style: CSS style for HTML repr.
    """

    _repr_max_line_length: int = 80
    _repr_compact: bool = True
    _repr_html_style: str = "sklearn"

    def __repr__(self) -> str:
        """Return a formatted string representation."""
        return format_repr(
            self,
            max_line_length=self._repr_max_line_length,
            compact=self._repr_compact,
        )

    def _repr_html_(self) -> str:
        """Return HTML representation for Jupyter notebooks."""
        from pyreprint.formatting.html import html_repr

        return html_repr(
            self,
            style=self._repr_html_style,
        )

    def _get_param_names(self) -> List[str]:
        """Get parameter names for this instance."""
        return _get_param_names(self.__class__)

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """Get parameters for this instance (sklearn-compatible).

        Args:
            deep: Whether to return nested object params.

        Returns:
            Dictionary of parameter names to values.
        """
        params = {}
        for name in self._get_param_names():
            value = getattr(self, name, None)
            params[name] = value

            if deep and hasattr(value, "get_params"):
                nested = value.get_params(deep=True)
                for key, val in nested.items():
                    params[f"{name}__{key}"] = val

        return params

    def set_params(self, **params: Any) -> "ReprMixin":
        """Set parameters for this instance (sklearn-compatible).

        Args:
            **params: Parameters to set.

        Returns:
            self
        """
        for key, value in params.items():
            if "__" in key:
                # Nested parameter
                parts = key.split("__", 1)
                nested_obj = getattr(self, parts[0])
                nested_obj.set_params(**{parts[1]: value})
            else:
                setattr(self, key, value)
        return self


class ReprConfig:
    """Configuration for repr formatting.

    This class allows customizing the default repr behavior.

    Attributes:
        max_line_length: Maximum line length before wrapping.
        compact: Whether to use compact format when possible.
        show_types: Whether to show type annotations.
        max_value_length: Maximum length for value representations.
    """

    def __init__(
        self,
        max_line_length: int = 80,
        compact: bool = True,
        show_types: bool = False,
        max_value_length: int = 40,
    ) -> None:
        self.max_line_length = max_line_length
        self.compact = compact
        self.show_types = show_types
        self.max_value_length = max_value_length


# Default configuration
default_repr_config = ReprConfig()

