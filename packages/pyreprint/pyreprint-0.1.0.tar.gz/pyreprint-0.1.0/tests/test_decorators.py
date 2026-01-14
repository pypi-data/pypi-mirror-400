"""Tests for decorator patterns."""

import pytest

from pyreprint import Banner, Box, Header, Line, banner, box, header, line


class TestLine:
    """Tests for Line decorator."""

    def test_basic_line(self):
        result = line("=", 10)
        assert result == "=" * 10

    def test_line_class(self):
        l = Line("*", 5)
        assert str(l) == "*****"

    def test_default_char(self):
        l = Line(width=10)
        assert str(l) == "=" * 10


class TestHeader:
    """Tests for Header decorator."""

    def test_basic_header(self):
        result = header("Test", char="=")
        assert "Test" in result
        assert "====" in result

    def test_header_with_above(self):
        result = header("Test", char="-", above=True)
        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "----"
        assert lines[1] == "Test"
        assert lines[2] == "----"

    def test_header_class(self):
        h = Header("Title", char="#")
        result = str(h)
        assert "Title" in result
        assert "#####" in result


class TestBox:
    """Tests for Box decorator."""

    def test_basic_box(self):
        result = box("Hi")
        assert "|" in result
        assert "+" in result
        assert "-" in result
        assert "Hi" in result

    def test_box_class(self):
        b = Box("Test")
        result = str(b)
        assert "Test" in result

    def test_multiline_box(self):
        result = box("Line1\nLine2")
        assert "Line1" in result
        assert "Line2" in result


class TestBanner:
    """Tests for Banner decorator."""

    def test_basic_banner(self):
        result = banner("TITLE", width=20)
        assert "*" * 20 in result
        assert "TITLE" in result

    def test_banner_custom_char(self):
        result = banner("TEST", char="#", width=20)
        assert "#" * 20 in result

    def test_banner_class(self):
        b = Banner("Hello", width=30)
        result = str(b)
        assert "Hello" in result
        assert len(result.split("\n")[0]) == 30

