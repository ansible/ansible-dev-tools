"""Fixtures for integration tests."""

from __future__ import annotations

import time

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from collections.abc import Generator

    from libtmux import Pane, Session

    from tests.conftest import Infrastructure


@pytest.fixture()
def session_params() -> dict[str, int]:
    """Set the tmux session parameters.

    Returns:
        dict: The tmux session parameters.
    """
    return {
        "x": 132,
        "y": 24,
    }


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
        self.send_and_wait(cmd, "workdir", 3)

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
        timeout = time.time() + timeout
        while True:
            stdout = self.pane.capture_pane()
            if not wait_for:
                return stdout if isinstance(stdout, list) else [stdout]
            if any(wait_for in line for line in stdout):
                return stdout if isinstance(stdout, list) else [stdout]
            if time.time() > timeout:
                break
        error = f"Timeout waiting for {wait_for} in {stdout}"
        pytest.fail(error)

    def exit(self) -> None:
        """Exit the tmux session."""
        if any("ansible-navigator" in cmd for cmd in self.cmds):
            self.send_and_wait(cmd=":q", wait_for="workdir")
        self.send_and_wait(cmd="exit", wait_for="")


@pytest.fixture()
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
