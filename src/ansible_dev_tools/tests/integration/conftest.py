"""Fixtures for integration tests."""

from __future__ import annotations

import contextlib
import os
import time

from typing import TYPE_CHECKING, Any

import pytest

from libtmux import exc
from libtmux.server import Server
from libtmux.test.constants import TEST_SESSION_PREFIX
from libtmux.test.random import get_test_session_name, namer


if TYPE_CHECKING:
    import pathlib

    from collections.abc import Generator

    from libtmux import Pane
    from libtmux.session import Session

    from ansible_dev_tools.tests.conftest import Infrastructure


@pytest.fixture
def session_params() -> dict[str, int]:
    """Set the tmux session parameters.

    Returns:
        dict: The tmux session parameters.
    """
    return {
        "x": 132,
        "y": 24,
    }


@pytest.fixture
def server(
    tmp_path: pathlib.Path,
) -> Generator[Server, None, None]:
    """Create a temporary tmux server.

    Args:
        tmp_path: Temporary path for config file.

    Yields:
        Server: A libtmux Server instance.
    """
    config_file = tmp_path / ".tmux.conf"
    config_file.write_text("set -g base-index 1\n", encoding="utf-8")

    srv = Server(socket_name=f"libtmux_test{next(namer)}")

    yield srv

    if srv.socket_name:
        with contextlib.suppress(exc.LibTmuxException, OSError):
            if srv.is_alive():
                srv.kill()


@pytest.fixture
def session(
    session_params: dict[str, Any],
    server: Server,
) -> Session:
    """Create a temporary tmux session.

    Args:
        session_params: Parameters for session creation.
        server: The tmux server.

    Returns:
        Session: A libtmux Session instance.
    """
    session_name = "tmuxp"

    if not server.has_session(session_name):
        server.new_session(session_name=session_name)

    test_session_name = get_test_session_name(server=server)

    _session = server.new_session(
        session_name=test_session_name,
        **session_params,
    )

    session_id = _session.session_id
    assert session_id is not None

    with contextlib.suppress(exc.LibTmuxException):
        server.switch_client(target_session=session_id)

    for s in server.sessions:
        old_name = s.session_name
        if (
            old_name is not None
            and old_name.startswith(TEST_SESSION_PREFIX)
            and old_name != test_session_name
        ):
            server.kill_session(old_name)

    return _session


class ContainerTmux:
    """A tmux session attached to the container."""

    def __init__(self, session: Session, infrastructure: Infrastructure) -> None:
        """Initialize an instance of ContainerTmux.

        Args:
            session: The tmux session.
            infrastructure: The testing infrastructure.
        """
        self.cmds: list[str] = []
        self.pane: Pane | None = session.active_pane
        self.infrastructure: Infrastructure = infrastructure
        self._shell_in_container()

    def _shell_in_container(self) -> None:
        """Open a shell in the container."""
        cmd = (
            f"{self.infrastructure.container_engine} exec -it"
            f" {self.infrastructure.container_name} /bin/zsh"
        )
        # 3s was not enough as we seen the arm64 runner timing out often
        self.send_and_wait(cmd, "workdir", 6)

    def send_and_wait(self, cmd: str, wait_for: str, timeout: float = 3.0) -> list[str]:
        """Send a command and wait for a response.

        Args:
            cmd: The command to send.
            wait_for: The string to wait for.
            timeout: The timeout.

        Returns:
            The stdout from the command.
        """
        self.cmds.append(cmd)
        if not self.pane:
            err = "No active pane found."
            pytest.fail(err)
        self.pane.send_keys(cmd)
        start_time = time.time()
        while True:
            stdout = self.pane.capture_pane()
            stdout_list = stdout if isinstance(stdout, list) else [stdout]
            if not wait_for:
                return stdout_list
            if any(wait_for in line for line in stdout):
                return stdout_list
            if time.time() > timeout + start_time:
                break
        error = (
            f"Timeout waiting for {timeout} seconds to find string '{wait_for}' in:\n"
            f" {os.linesep.join(stdout_list)}"
        )
        pytest.fail(error)

    def exit(self) -> None:
        """Exit the tmux session."""
        if any("ansible-navigator" in cmd for cmd in self.cmds):
            self.send_and_wait(cmd=":q", wait_for="workdir", timeout=6)
        self.send_and_wait(cmd="exit", wait_for="")


@pytest.fixture
def container_tmux(
    infrastructure: Infrastructure,
    session: Session,
) -> Generator[ContainerTmux, None, None]:
    """Create a tmux session attached to the container.

    Args:
        infrastructure: The testing infrastructure.
        session: The tmux session.

    Yields:
        ContainerTmux: A tmux session attached to the container.

    Returns:
        None.
    """
    _container_tmux = ContainerTmux(infrastructure=infrastructure, session=session)
    yield _container_tmux
    _container_tmux.exit()
