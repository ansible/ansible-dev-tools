"""Some tests for the CLI module."""

from __future__ import annotations

from typing import Any

import pytest

from ansible_dev_tools.cli import main
from ansible_dev_tools.version_builder import PKGS


def test_version(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test collecting versions.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        capsys: Pytest capsys fixture.
    """
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
    """Test the server subcommand fails if server dependencies are missing.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        capsys: Pytest capsys fixture.
    """
    monkeypatch.setattr("sys.argv", ["adt", "server"])

    class MockServer:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:  # noqa: ANN401
            """Initialize the MockServer.

            Args:
                *_args: Positional arguments.
                **_kwargs: Keyword arguments.

            Raises:
                ImportError: Always raises ImportError.
            """
            raise ImportError

    monkeypatch.setattr("ansible_dev_tools.subcommands.server.Server", MockServer)

    with pytest.raises(SystemExit):
        main()

    captured = capsys.readouterr()
    assert "Error: Missing server dependencies" in captured.err
