"""Configuration file loader for styles."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Union

from pyreprint.styles.registry import StyleFunction, registry


def _create_style_from_config(config: Dict[str, Any]) -> StyleFunction:
    """Create a style function from configuration dictionary.

    Args:
        config: Style configuration with keys like 'before', 'after', etc.

    Returns:
        A style function.
    """
    before_config = config.get("before", {})
    after_config = config.get("after", {})
    prefix = config.get("prefix", "")
    suffix = config.get("suffix", "")
    center = config.get("center", False)
    uppercase = config.get("uppercase", False)

    def style_func(text: str, width: int = 60, **kwargs: Any) -> str:
        result_parts = []

        # Before decorator
        if before_config:
            char = before_config.get("char", "=")
            line_width = before_config.get("width", width)
            result_parts.append(char * line_width)

        # Process text
        processed_text = text
        if uppercase:
            processed_text = processed_text.upper()
        if center:
            processed_text = processed_text.center(width)
        processed_text = f"{prefix}{processed_text}{suffix}"
        result_parts.append(processed_text)

        # After decorator
        if after_config:
            char = after_config.get("char", "=")
            line_width = after_config.get("width", width)
            result_parts.append(char * line_width)

        return "\n".join(result_parts)

    return style_func


def load_styles_from_yaml(yaml_content: str) -> Dict[str, StyleFunction]:
    """Load styles from YAML content.

    Args:
        yaml_content: YAML string containing style definitions.

    Returns:
        Dictionary of style name to style function.

    Example:
        >>> yaml_content = '''
        ... styles:
        ...   divider:
        ...     before:
        ...       char: "-"
        ...       width: 40
        ...     after:
        ...       char: "-"
        ...       width: 40
        ... '''
        >>> styles = load_styles_from_yaml(yaml_content)
    """
    import yaml

    data = yaml.safe_load(yaml_content)
    styles: Dict[str, StyleFunction] = {}

    if not data or "styles" not in data:
        return styles

    for name, config in data.get("styles", {}).items():
        styles[name] = _create_style_from_config(config)
        # Also register in global registry
        registry.register(name, styles[name])

    return styles


def load_styles_from_toml(toml_content: str) -> Dict[str, StyleFunction]:
    """Load styles from TOML content.

    Args:
        toml_content: TOML string containing style definitions.

    Returns:
        Dictionary of style name to style function.
    """
    if sys.version_info >= (3, 11):
        import tomllib

        data = tomllib.loads(toml_content)
    else:
        import tomli

        data = tomli.loads(toml_content)

    styles: Dict[str, StyleFunction] = {}

    if not data or "styles" not in data:
        return styles

    for name, config in data.get("styles", {}).items():
        styles[name] = _create_style_from_config(config)
        # Also register in global registry
        registry.register(name, styles[name])

    return styles


def load_styles_from_file(
    path: Union[str, Path],
    register: bool = True,
) -> Dict[str, StyleFunction]:
    """Load styles from a YAML or TOML configuration file.

    Args:
        path: Path to the configuration file.
        register: Whether to register styles in the global registry.

    Returns:
        Dictionary of style name to style function.

    Raises:
        ValueError: If file format is not supported.
        FileNotFoundError: If the file does not exist.

    Example:
        >>> styles = load_styles_from_file("my_styles.yaml")
        >>> # Now you can use: reprint("Hello", style="my_custom_style")
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Style configuration file not found: {path}")

    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        return load_styles_from_yaml(content)
    elif suffix == ".toml":
        return load_styles_from_toml(content)
    else:
        raise ValueError(f"Unsupported configuration file format: {suffix}")


def load_styles_from_dict(
    config: Dict[str, Dict[str, Any]],
    register: bool = True,
) -> Dict[str, StyleFunction]:
    """Load styles from a dictionary.

    Args:
        config: Dictionary of style name to style configuration.
        register: Whether to register styles in the global registry.

    Returns:
        Dictionary of style name to style function.

    Example:
        >>> config = {
        ...     "highlight": {
        ...         "prefix": ">>> ",
        ...         "suffix": " <<<",
        ...     }
        ... }
        >>> styles = load_styles_from_dict(config)
    """
    styles: Dict[str, StyleFunction] = {}

    for name, style_config in config.items():
        style_func = _create_style_from_config(style_config)
        styles[name] = style_func
        if register:
            registry.register(name, style_func)

    return styles

