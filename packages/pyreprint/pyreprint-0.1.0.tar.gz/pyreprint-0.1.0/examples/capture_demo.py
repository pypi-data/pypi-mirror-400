#!/usr/bin/env python
"""Output capture and redirection examples for PyRePrint."""

import sys
import tempfile
from pathlib import Path

from pyreprint import (
    CapturedOutput,
    OutputBuffer,
    OutputTee,
    capture_output,
    redirect_to_file,
    reprint,
)


def main():
    reprint("Output Capture Examples", style="banner", width=60)
    reprint("")

    # =========================================================================
    # Basic Capture
    # =========================================================================

    reprint("1. Basic Output Capture", style="header")

    with capture_output() as captured:
        print("This is captured stdout")
        print("Line 2 of stdout")

    reprint("Captured output:")
    reprint(captured.stdout, style="quote")
    reprint("")

    # =========================================================================
    # Capturing stderr
    # =========================================================================

    reprint("2. Capturing stderr", style="header")

    with capture_output(stdout=True, stderr=True) as captured:
        print("Standard output")
        print("Error message", file=sys.stderr)

    reprint("stdout:", style="info")
    reprint(captured.stdout.strip(), style="quote")
    reprint("stderr:", style="warning")
    reprint(captured.stderr.strip(), style="quote")
    reprint("")

    # =========================================================================
    # Selective Capture
    # =========================================================================

    reprint("3. Selective Capture", style="header")

    # Only capture stderr
    with capture_output(stdout=False, stderr=True) as captured:
        print("This goes to console")  # Not captured
        print("This is captured", file=sys.stderr)

    reprint(f"Captured stderr: {captured.stderr.strip()!r}")
    reprint("")

    # =========================================================================
    # Redirect to File
    # =========================================================================

    reprint("4. Redirect to File", style="header")

    # Create a temporary file for demo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name

    with redirect_to_file(temp_path):
        print("Line 1 written to file")
        print("Line 2 written to file")

    # Read and display the file contents
    content = Path(temp_path).read_text()
    reprint(f"File contents ({temp_path}):")
    reprint(content.strip(), style="quote")

    # Cleanup
    Path(temp_path).unlink()
    reprint("")

    # =========================================================================
    # Output Tee
    # =========================================================================

    reprint("5. Output Tee (Multiple Destinations)", style="header")

    # Create a temp file for tee demo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name

    with open(temp_path, 'w') as log_file:
        tee = OutputTee(log_file, include_stdout=True)
        with tee.activate():
            print("This goes to both console and file")
            print("So does this line")

    # Show what was written to file
    content = Path(temp_path).read_text()
    reprint("File also contains:")
    reprint(content.strip(), style="quote")

    # Cleanup
    Path(temp_path).unlink()
    reprint("")

    # =========================================================================
    # Output Buffer
    # =========================================================================

    reprint("6. Output Buffer (Conditional Display)", style="header")

    buffer = OutputBuffer()

    # Capture some output
    with buffer.capture():
        print("Processing step 1...")
        print("Processing step 2...")
        print("Processing complete!")

    # Decide whether to show it
    show_output = True  # Could be based on verbose flag

    if show_output:
        reprint("Showing buffered output:")
        buffer.replay()
    else:
        reprint("Output was suppressed")

    reprint("")

    # =========================================================================
    # Practical Example: Test Runner
    # =========================================================================

    reprint("7. Practical Example: Test Runner", style="header")

    def run_test(name, should_pass):
        """Simulate running a test."""
        with capture_output() as output:
            print(f"Running test: {name}")
            if should_pass:
                print("  All assertions passed")
                return True, output.stdout
            else:
                print("  AssertionError: values don't match")
                return False, output.stdout

    tests = [
        ("test_addition", True),
        ("test_subtraction", True),
        ("test_division", False),
        ("test_multiplication", True),
    ]

    passed = 0
    failed = 0
    failures = []

    for test_name, should_pass in tests:
        success, output = run_test(test_name, should_pass)
        if success:
            reprint(f"{test_name}", style="success")
            passed += 1
        else:
            reprint(f"{test_name}", style="error")
            failed += 1
            failures.append((test_name, output))

    reprint("")
    reprint(f"Results: {passed} passed, {failed} failed", style="section", width=40)

    if failures:
        reprint("")
        reprint("Failure Details:", style="warning")
        for name, output in failures:
            reprint(f"\n{name}:", style="header")
            print(output)

    reprint("")
    reprint("Examples Complete!", style="banner", width=60)


if __name__ == "__main__":
    main()

