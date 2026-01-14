"""Style registry for pyreprint."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

# Type for style functions
StyleFunction = Callable[..., str]


class StyleRegistry:
    """Registry for named print styles.

    The StyleRegistry manages a collection of named style functions
    that can be applied to print output. Styles can be registered
    programmatically or loaded from configuration files.

    Example:
        >>> registry = StyleRegistry()
        >>> @registry.register("highlight")
        ... def highlight(text, **kwargs):
        ...     return f">>> {text} <<<"
        >>> styled = registry.apply("highlight", "Important")
        >>> print(styled)
        >>> Important <<<
    """

    def __init__(self) -> None:
        self._styles: Dict[str, StyleFunction] = {}

    def register(
        self,
        name: str,
        func: Optional[StyleFunction] = None,
    ) -> Callable[[StyleFunction], StyleFunction]:
        """Register a style function.

        Can be used as a decorator or called directly.

        Args:
            name: Name of the style.
            func: The style function (optional if used as decorator).

        Returns:
            The style function (for decorator usage).

        Example:
            As decorator:
            >>> @registry.register("section")
            ... def section_style(text, width=60, **kwargs):
            ...     line = "=" * width
            ...     return f"{line}\\n{text}\\n{line}"

            Direct registration:
            >>> registry.register("simple", lambda t, **k: f"[{t}]")
        """
        if func is not None:
            self._styles[name] = func
            return func

        def decorator(f: StyleFunction) -> StyleFunction:
            self._styles[name] = f
            return f

        return decorator

    def unregister(self, name: str) -> bool:
        """Remove a registered style.

        Args:
            name: Name of the style to remove.

        Returns:
            True if the style was removed, False if not found.
        """
        if name in self._styles:
            del self._styles[name]
            return True
        return False

    def get(self, name: str) -> Optional[StyleFunction]:
        """Get a style function by name.

        Args:
            name: Name of the style.

        Returns:
            The style function, or None if not found.
        """
        return self._styles.get(name)

    def apply(self, name: str, text: str, **kwargs: Any) -> str:
        """Apply a named style to text.

        Args:
            name: Name of the style.
            text: Text to style.
            **kwargs: Additional arguments for the style function.

        Returns:
            The styled text.

        Raises:
            KeyError: If the style is not found.
        """
        style_func = self._styles.get(name)
        if style_func is None:
            raise KeyError(f"Style '{name}' not found")
        return style_func(text, **kwargs)

    def list_styles(self) -> List[str]:
        """Get list of registered style names.

        Returns:
            List of style names.
        """
        return list(self._styles.keys())

    def has_style(self, name: str) -> bool:
        """Check if a style is registered.

        Args:
            name: Name of the style.

        Returns:
            True if the style exists.
        """
        return name in self._styles

    def clear(self) -> None:
        """Remove all registered styles."""
        self._styles.clear()

    def __contains__(self, name: str) -> bool:
        return name in self._styles

    def __len__(self) -> int:
        return len(self._styles)

    def __iter__(self):
        return iter(self._styles)


# Global registry instance
registry = StyleRegistry()


def register_style(
    name: str,
    func: Optional[StyleFunction] = None,
) -> Callable[[StyleFunction], StyleFunction]:
    """Register a style with the global registry.

    Can be used as a decorator or called directly.

    Args:
        name: Name of the style.
        func: The style function (optional if used as decorator).

    Returns:
        The style function (for decorator usage).

    Example:
        >>> @register_style("warning")
        ... def warning_style(text, **kwargs):
        ...     return f"[!] {text} [!]"
    """
    return registry.register(name, func)


def get_style(name: str) -> Optional[StyleFunction]:
    """Get a style function from the global registry.

    Args:
        name: Name of the style.

    Returns:
        The style function, or None if not found.
    """
    return registry.get(name)


def list_styles() -> List[str]:
    """List all registered styles in the global registry.

    Returns:
        List of style names.
    """
    return registry.list_styles()


def apply_style(name: str, text: str, **kwargs: Any) -> str:
    """Apply a named style from the global registry.

    Args:
        name: Name of the style.
        text: Text to style.
        **kwargs: Additional arguments for the style function.

    Returns:
        The styled text.

    Raises:
        KeyError: If the style is not found.
    """
    return registry.apply(name, text, **kwargs)

