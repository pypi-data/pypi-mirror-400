"""Output capture and redirection utilities."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import IO, Iterator, List, Optional, TextIO, Union


@dataclass
class CapturedOutput:
    """Container for captured stdout and stderr output.

    Attributes:
        stdout: Captured stdout content.
        stderr: Captured stderr content.
    """

    stdout: str = ""
    stderr: str = ""

    def __str__(self) -> str:
        """Return combined output."""
        if self.stderr:
            return f"{self.stdout}\n--- stderr ---\n{self.stderr}"
        return self.stdout

    def __bool__(self) -> bool:
        """Return True if any output was captured."""
        return bool(self.stdout or self.stderr)

    @property
    def combined(self) -> str:
        """Get combined stdout and stderr."""
        return self.stdout + self.stderr

    def print_stdout(self) -> None:
        """Print captured stdout to current stdout."""
        if self.stdout:
            print(self.stdout, end="")

    def print_stderr(self) -> None:
        """Print captured stderr to current stderr."""
        if self.stderr:
            print(self.stderr, end="", file=sys.stderr)


@contextmanager
def capture_output(
    stdout: bool = True,
    stderr: bool = True,
) -> Iterator[CapturedOutput]:
    """Context manager to capture stdout and/or stderr.

    Args:
        stdout: Whether to capture stdout.
        stderr: Whether to capture stderr.

    Yields:
        CapturedOutput object containing captured content.

    Example:
        >>> with capture_output() as captured:
        ...     print("Hello")
        ...     print("Error", file=sys.stderr)
        >>> print(captured.stdout)
        Hello
        >>> print(captured.stderr)
        Error
    """
    result = CapturedOutput()
    stdout_capture = StringIO() if stdout else None
    stderr_capture = StringIO() if stderr else None

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        if stdout_capture:
            sys.stdout = stdout_capture
        if stderr_capture:
            sys.stderr = stderr_capture

        yield result

    finally:
        if stdout_capture:
            result.stdout = stdout_capture.getvalue()
            sys.stdout = old_stdout
            stdout_capture.close()
        if stderr_capture:
            result.stderr = stderr_capture.getvalue()
            sys.stderr = old_stderr
            stderr_capture.close()


@contextmanager
def redirect_to_file(
    path: Union[str, Path],
    mode: str = "w",
    stdout: bool = True,
    stderr: bool = False,
    encoding: str = "utf-8",
) -> Iterator[IO[str]]:
    """Context manager to redirect output to a file.

    Args:
        path: Path to the output file.
        mode: File open mode ('w' for write, 'a' for append).
        stdout: Whether to redirect stdout.
        stderr: Whether to redirect stderr.
        encoding: File encoding.

    Yields:
        The opened file object.

    Example:
        >>> with redirect_to_file("output.txt") as f:
        ...     print("This goes to the file")
    """
    path = Path(path)
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    with open(path, mode, encoding=encoding) as f:
        try:
            if stdout:
                sys.stdout = f
            if stderr:
                sys.stderr = f
            yield f
        finally:
            if stdout:
                sys.stdout = old_stdout
            if stderr:
                sys.stderr = old_stderr


class OutputTee:
    """Write to multiple destinations simultaneously.

    This class allows output to be sent to multiple file-like objects
    at once, similar to the Unix 'tee' command.

    Args:
        *destinations: File-like objects to write to.
        include_stdout: Whether to include sys.stdout as a destination.

    Example:
        >>> with open("log.txt", "w") as f:
        ...     tee = OutputTee(f, include_stdout=True)
        ...     old_stdout = sys.stdout
        ...     sys.stdout = tee
        ...     print("This goes to both console and file")
        ...     sys.stdout = old_stdout
    """

    def __init__(
        self,
        *destinations: TextIO,
        include_stdout: bool = True,
    ) -> None:
        self._destinations: List[TextIO] = list(destinations)
        self._include_stdout = include_stdout
        self._original_stdout: Optional[TextIO] = None

    def write(self, text: str) -> int:
        """Write to all destinations."""
        bytes_written = 0
        for dest in self._destinations:
            result = dest.write(text)
            if result is not None:
                bytes_written = max(bytes_written, result)

        if self._include_stdout and self._original_stdout:
            result = self._original_stdout.write(text)
            if result is not None:
                bytes_written = max(bytes_written, result)

        return bytes_written

    def flush(self) -> None:
        """Flush all destinations."""
        for dest in self._destinations:
            dest.flush()
        if self._include_stdout and self._original_stdout:
            self._original_stdout.flush()

    def add_destination(self, dest: TextIO) -> None:
        """Add a new destination."""
        self._destinations.append(dest)

    def remove_destination(self, dest: TextIO) -> None:
        """Remove a destination."""
        if dest in self._destinations:
            self._destinations.remove(dest)

    @contextmanager
    def activate(self) -> Iterator["OutputTee"]:
        """Context manager to activate the tee for stdout.

        Example:
            >>> tee = OutputTee(open("log.txt", "w"))
            >>> with tee.activate():
            ...     print("Goes to console and file")
        """
        self._original_stdout = sys.stdout
        sys.stdout = self  # type: ignore[assignment]
        try:
            yield self
        finally:
            sys.stdout = self._original_stdout
            self._original_stdout = None


@dataclass
class OutputBuffer:
    """A buffer that collects output and can replay it later.

    This is useful for capturing output and then deciding whether
    to display it based on some condition.

    Example:
        >>> buffer = OutputBuffer()
        >>> with buffer.capture():
        ...     print("Line 1")
        ...     print("Line 2")
        >>> if some_condition:
        ...     buffer.replay()
    """

    _lines: List[str] = field(default_factory=list)
    _capturing: bool = False

    def write(self, text: str) -> int:
        """Write to the buffer."""
        if self._capturing:
            self._lines.append(text)
        return len(text)

    def flush(self) -> None:
        """Flush (no-op for buffer)."""
        pass

    @contextmanager
    def capture(self) -> Iterator["OutputBuffer"]:
        """Context manager to capture stdout to this buffer."""
        old_stdout = sys.stdout
        self._capturing = True
        sys.stdout = self  # type: ignore[assignment]
        try:
            yield self
        finally:
            sys.stdout = old_stdout
            self._capturing = False

    def replay(self, file: Optional[TextIO] = None) -> None:
        """Replay captured output to stdout or specified file."""
        target = file or sys.stdout
        for line in self._lines:
            target.write(line)
        target.flush()

    def get_output(self) -> str:
        """Get all captured output as a string."""
        return "".join(self._lines)

    def clear(self) -> None:
        """Clear the buffer."""
        self._lines.clear()

    def __str__(self) -> str:
        return self.get_output()

    def __bool__(self) -> bool:
        return bool(self._lines)

