"""Tests for Jupyter notebooks using nbval.

This module provides notebook testing via pytest-nbval.

To run notebook tests:
    pytest --nbval-lax examples/notebooks/tutorial.ipynb

The --nbval-lax flag allows outputs to differ from saved outputs,
only checking that cells execute without errors.

For strict output matching:
    pytest --nbval examples/notebooks/tutorial.ipynb
"""

from pathlib import Path

import pytest


NOTEBOOK_DIR = Path(__file__).parent.parent / "examples" / "notebooks"


def test_notebooks_directory_exists():
    """Verify notebook directory exists."""
    assert NOTEBOOK_DIR.exists(), f"Notebook directory not found: {NOTEBOOK_DIR}"


def test_tutorial_notebook_exists():
    """Verify tutorial notebook exists."""
    tutorial = NOTEBOOK_DIR / "tutorial.ipynb"
    assert tutorial.exists(), f"Tutorial notebook not found: {tutorial}"


def test_notebooks_are_valid_json():
    """Verify all notebooks are valid JSON files."""
    import json

    notebooks = list(NOTEBOOK_DIR.glob("*.ipynb"))
    assert len(notebooks) > 0, "No notebooks found"

    for notebook in notebooks:
        with open(notebook, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                assert "cells" in data, f"No cells in {notebook.name}"
                assert "nbformat" in data, f"No nbformat in {notebook.name}"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {notebook.name}: {e}")


def test_notebook_has_code_cells():
    """Verify tutorial notebook has code cells."""
    import json

    tutorial = NOTEBOOK_DIR / "tutorial.ipynb"
    with open(tutorial, "r", encoding="utf-8") as f:
        data = json.load(f)

    code_cells = [c for c in data["cells"] if c.get("cell_type") == "code"]
    assert len(code_cells) > 0, "No code cells found in tutorial notebook"


# The following tests use nbval for actual notebook execution
# They are marked with pytest.mark.nbval to be run with --nbval flag

@pytest.fixture
def notebook_path():
    """Return path to tutorial notebook."""
    return NOTEBOOK_DIR / "tutorial.ipynb"


def test_notebook_imports_work():
    """Test that the imports from the notebook work."""
    # This tests the actual import without running the notebook
    from pyreprint import (
        reprint,
        line,
        header,
        box,
        banner,
        capture_output,
        register_style,
        ReprMixin,
        rprint,
        panel,
        rule,
    )

    # Quick sanity check
    assert callable(reprint)
    assert callable(line)
    assert callable(header)
    assert callable(box)
    assert callable(banner)
    assert callable(capture_output)
    assert callable(register_style)
    assert callable(rprint)
    assert callable(panel)
    assert callable(rule)
