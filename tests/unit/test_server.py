"""Test for the server module."""

from typing import Any

import pytest

from ansible_dev_tools.subcommands.server import Server


def test_server_debug_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the server class with debug options.

    Args:
        monkeypatch: pytest fixture for patching.
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

    server = Server(port="8080", debug=True)
    server.run()
    assert options["loglevel"] == "debug"
    assert called
