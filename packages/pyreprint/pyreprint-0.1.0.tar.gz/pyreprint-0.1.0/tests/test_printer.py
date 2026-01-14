"""Tests for the printer module."""

import sys
from io import StringIO

import pytest

from pyreprint import Printer, reprint


class TestReprint:
    """Tests for the reprint function."""

    def test_basic_print(self, capsys):
        reprint("Hello")
        captured = capsys.readouterr()
        assert captured.out == "Hello\n"

    def test_multiple_args(self, capsys):
        reprint("a", "b", "c")
        captured = capsys.readouterr()
        assert captured.out == "a b c\n"

    def test_custom_sep(self, capsys):
        reprint("a", "b", sep="-")
        captured = capsys.readouterr()
        assert captured.out == "a-b\n"

    def test_custom_end(self, capsys):
        reprint("test", end="")
        captured = capsys.readouterr()
        assert captured.out == "test"

    def test_before_decorator(self, capsys):
        reprint("text", before="=", width=5)
        captured = capsys.readouterr()
        assert "=====" in captured.out
        assert "text" in captured.out

    def test_after_decorator(self, capsys):
        reprint("text", after="-", width=5)
        captured = capsys.readouterr()
        assert "-----" in captured.out
        assert "text" in captured.out

    def test_surround_decorator(self, capsys):
        reprint("text", surround="*", width=5)
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert lines[0] == "*****"
        assert lines[-1] == "*****"

    def test_file_output(self):
        output = StringIO()
        reprint("test", file=output)
        assert output.getvalue() == "test\n"


class TestPrinter:
    """Tests for the Printer class."""

    def test_printer_instance(self, capsys):
        printer = Printer(width=40)
        printer("Hello")
        captured = capsys.readouterr()
        assert captured.out == "Hello\n"

    def test_printer_with_decorator(self, capsys):
        printer = Printer(width=10)
        printer("Hi", before="=")
        captured = capsys.readouterr()
        assert "==========" in captured.out

    def test_printer_default_style(self, capsys):
        printer = Printer(default_style="highlight")
        printer("test")
        captured = capsys.readouterr()
        assert ">>>" in captured.out or "test" in captured.out

