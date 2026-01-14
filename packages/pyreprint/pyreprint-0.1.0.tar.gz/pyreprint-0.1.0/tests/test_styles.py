"""Tests for the style system."""

import pytest

from pyreprint import (
    StyleRegistry,
    get_style,
    list_styles,
    register_style,
    registry,
)


class TestStyleRegistry:
    """Tests for StyleRegistry class."""

    def test_register_and_get(self):
        reg = StyleRegistry()

        @reg.register("test")
        def test_style(text, **kwargs):
            return f"[{text}]"

        assert reg.has_style("test")
        assert reg.get("test") is not None

    def test_apply_style(self):
        reg = StyleRegistry()
        reg.register("wrap", lambda t, **k: f"({t})")

        result = reg.apply("wrap", "hello")
        assert result == "(hello)"

    def test_unregister(self):
        reg = StyleRegistry()
        reg.register("temp", lambda t, **k: t)
        assert reg.has_style("temp")

        reg.unregister("temp")
        assert not reg.has_style("temp")

    def test_list_styles(self):
        reg = StyleRegistry()
        reg.register("a", lambda t, **k: t)
        reg.register("b", lambda t, **k: t)

        styles = reg.list_styles()
        assert "a" in styles
        assert "b" in styles

    def test_clear(self):
        reg = StyleRegistry()
        reg.register("test", lambda t, **k: t)
        assert len(reg) > 0

        reg.clear()
        assert len(reg) == 0


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def test_builtin_styles_exist(self):
        styles = list_styles()
        assert "section" in styles
        assert "header" in styles
        assert "box" in styles
        assert "banner" in styles

    def test_get_builtin_style(self):
        section = get_style("section")
        assert section is not None
        assert callable(section)

    def test_apply_builtin_style(self):
        section = get_style("section")
        result = section("Test", width=20)
        assert "Test" in result
        assert "=" * 20 in result

    def test_register_custom_style(self):
        @register_style("custom_test")
        def custom(text, **kwargs):
            return f"!{text}!"

        assert get_style("custom_test") is not None
        result = get_style("custom_test")("hi")
        assert result == "!hi!"

        # Cleanup
        registry.unregister("custom_test")

