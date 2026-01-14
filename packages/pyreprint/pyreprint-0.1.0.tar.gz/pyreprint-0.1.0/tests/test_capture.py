"""Tests for output capture utilities."""

import sys
import tempfile
from pathlib import Path

import pytest

from pyreprint import CapturedOutput, OutputBuffer, capture_output, redirect_to_file


class TestCaptureOutput:
    """Tests for capture_output context manager."""

    def test_capture_stdout(self):
        with capture_output() as captured:
            print("Hello")
        assert captured.stdout == "Hello\n"

    def test_capture_stderr(self):
        with capture_output() as captured:
            print("Error", file=sys.stderr)
        assert captured.stderr == "Error\n"

    def test_capture_both(self):
        with capture_output() as captured:
            print("stdout")
            print("stderr", file=sys.stderr)
        assert "stdout" in captured.stdout
        assert "stderr" in captured.stderr

    def test_capture_stdout_only(self):
        with capture_output(stderr=False) as captured:
            print("stdout")
        assert captured.stdout == "stdout\n"
        assert captured.stderr == ""

    def test_capture_stderr_only(self):
        with capture_output(stdout=False) as captured:
            print("test", file=sys.stderr)
        assert captured.stderr == "test\n"
        assert captured.stdout == ""

    def test_captured_output_combined(self):
        with capture_output() as captured:
            print("line1")
            print("line2")
        assert "line1" in captured.combined
        assert "line2" in captured.combined

    def test_captured_output_bool(self):
        with capture_output() as captured:
            pass
        assert not captured

        with capture_output() as captured:
            print("test")
        assert captured


class TestRedirectToFile:
    """Tests for redirect_to_file context manager."""

    def test_redirect_stdout(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            path = f.name

        with redirect_to_file(path):
            print("Hello file")

        content = Path(path).read_text()
        assert "Hello file" in content
        Path(path).unlink()

    def test_redirect_append(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            path = f.name

        with redirect_to_file(path, mode="w"):
            print("Line 1")

        with redirect_to_file(path, mode="a"):
            print("Line 2")

        content = Path(path).read_text()
        assert "Line 1" in content
        assert "Line 2" in content
        Path(path).unlink()


class TestOutputBuffer:
    """Tests for OutputBuffer class."""

    def test_buffer_capture(self):
        buffer = OutputBuffer()
        with buffer.capture():
            print("Line 1")
            print("Line 2")

        assert "Line 1" in buffer.get_output()
        assert "Line 2" in buffer.get_output()

    def test_buffer_replay(self, capsys):
        buffer = OutputBuffer()
        with buffer.capture():
            print("Test")

        buffer.replay()
        captured = capsys.readouterr()
        assert "Test" in captured.out

    def test_buffer_clear(self):
        buffer = OutputBuffer()
        with buffer.capture():
            print("Test")

        assert buffer.get_output()
        buffer.clear()
        assert not buffer.get_output()

    def test_buffer_bool(self):
        buffer = OutputBuffer()
        assert not buffer

        with buffer.capture():
            print("Test")
        assert buffer

