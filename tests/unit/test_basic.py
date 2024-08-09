"""Some basic tests."""

from __future__ import annotations

import runpy

import pytest


def test_main() -> None:
    """Test the main entry point.

    Gives an error message due to missing subcommand.
    """
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("ansible_dev_tools.__main__", run_name="__main__")
    expected_error_code = 2
    assert exc.value.code == expected_error_code


def test_cli_main() -> None:
    """Test the main entry point.

    Gives an error message due to missing subcommand.
    """
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("ansible_dev_tools.cli", run_name="__main__")
    expected_error_code = 2
    assert exc.value.code == expected_error_code
