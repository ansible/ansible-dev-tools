"""Test for the server module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    import pytest

    from ansible_dev_tools.subcommands.server import Server


def test_server_debug_options(monkeypatch: pytest.MonkeyPatch, adt_server: Server) -> None:
    """Test the server class with debug options.

    Args:
        monkeypatch: pytest fixture for patching.
        adt_server: The server instance.
    """
    called = False
    options = {}

    class MockAdtServerApp:
        """Mock AdtServerApp class."""

        def __init__(self, *_args: Any, **kwargs: Any) -> None:  # noqa: ANN401
            """Initialize the mock class.

            Args:
                *_args: The positional arguments.
                **kwargs: The keyword arguments.
            """
            nonlocal options
            options = kwargs["options"]

        def run(self) -> None:
            """Run the mock class."""
            nonlocal called
            called = True

    monkeypatch.setattr("ansible_dev_tools.subcommands.server.AdtServerApp", MockAdtServerApp)

    adt_server.run()
    assert options["loglevel"] == "debug"
    assert called
