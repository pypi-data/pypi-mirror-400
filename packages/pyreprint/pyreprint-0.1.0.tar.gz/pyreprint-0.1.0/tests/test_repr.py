"""Tests for repr formatting."""

import pytest

from pyreprint import ReprMixin, format_repr, html_repr


class TestFormatRepr:
    """Tests for format_repr function."""

    def test_basic_format(self):
        class Simple:
            def __init__(self, a=1, b=2):
                self.a = a
                self.b = b

        obj = Simple()
        result = format_repr(obj)
        assert "Simple" in result
        assert "a=1" in result
        assert "b=2" in result

    def test_format_with_params(self):
        class Test:
            pass

        obj = Test()
        result = format_repr(obj, params={"x": 10, "y": "hello"})
        assert "x=10" in result
        assert "y='hello'" in result

    def test_compact_mode(self):
        class Short:
            def __init__(self, x=1):
                self.x = x

        obj = Short()
        result = format_repr(obj, compact=True)
        assert "\n" not in result

    def test_long_values_truncated(self):
        class WithLongValue:
            def __init__(self, data=""):
                self.data = data

        obj = WithLongValue(data="x" * 100)
        result = format_repr(obj)
        assert "..." in result


class TestReprMixin:
    """Tests for ReprMixin class."""

    def test_repr(self):
        class Model(ReprMixin):
            def __init__(self, alpha=1.0, beta=2.0):
                self.alpha = alpha
                self.beta = beta

        model = Model(alpha=0.5)
        result = repr(model)
        assert "Model" in result
        assert "alpha=0.5" in result

    def test_get_params(self):
        class Estimator(ReprMixin):
            def __init__(self, n=10, m=20):
                self.n = n
                self.m = m

        est = Estimator(n=5)
        params = est.get_params()
        assert params["n"] == 5
        assert params["m"] == 20

    def test_set_params(self):
        class Configurable(ReprMixin):
            def __init__(self, value=0):
                self.value = value

        obj = Configurable()
        obj.set_params(value=42)
        assert obj.value == 42

    def test_repr_html(self):
        class HtmlTest(ReprMixin):
            def __init__(self, x=1):
                self.x = x

        obj = HtmlTest()
        html = obj._repr_html_()
        assert "<" in html
        assert "HtmlTest" in html


class TestHtmlRepr:
    """Tests for html_repr function."""

    def test_basic_html(self):
        class Test:
            def __init__(self, a=1):
                self.a = a

        obj = Test()
        html = html_repr(obj)
        assert "<" in html
        assert "Test" in html

    def test_different_styles(self):
        class Test:
            def __init__(self, x=1):
                self.x = x

        obj = Test()

        for style in ["sklearn", "dark", "minimal"]:
            html = html_repr(obj, style=style)
            assert "Test" in html

    def test_collapsible(self):
        class Test:
            def __init__(self, a=1):
                self.a = a

        obj = Test()
        html = html_repr(obj, collapsible=True)
        assert "<details" in html

