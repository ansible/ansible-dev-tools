"""Some tests for the CLI module."""

import sys

import pytest

from ansible_dev_tools.cli import main
from ansible_dev_tools.version_builder import PKGS


def test_version(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test collecting versions."""
    monkeypatch.setattr("sys.argv", ["adt", "--version"])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    for pkg in PKGS:
        assert pkg in captured.out, f"{pkg} not found in version output"


def test_server_fail_no_deps(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test the server subcommand fails if server dependencies are missing."""
    monkeypatch.setattr("sys.argv", ["adt", "server"])
    monkeypatch.setitem(sys.modules, "django", None)

    with pytest.raises(SystemExit):
        main()

    captured = capsys.readouterr()
    assert "Error: Missing server dependencies" in captured.err
