# cspell:ignore XDIST, sessionstart, sessionfinish
"""Global conftest.py for pytest.

The root package import below happens before the pytest workers are forked, so it
picked up by the initial coverage process for a source match.

Without it, coverage reports the following false positive error:

CoverageWarning: No data was collected. (no-data-collected)

This works in conjunction with the coverage source_pkg set to the package such that
a `coverage run --debug trace` shows the source package and file match.

<...>
Imported source package '<package>' as '/**/src/<package>/__init__.py'
<...>
Tracing '/**/src/<package>/__init__.py'
"""

import os
import shutil
import subprocess
import sys
import time

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
import requests

import ansible_dev_tools  # noqa: F401


@dataclass
class Infrastructure:
    """Structure for instance infrastructure.

    Attributes:
        session: The pytest session
        container_engine: The container engine
        container_name: The container name
        container: Container required
        image_name: The image name
        include_container: Include container tests
        only_container: Only container tests
        proc: The server process
        server: Server required
    """

    session: pytest.Session
    container_engine: str = ""
    container_name: str = ""
    container: bool = False
    image_name: str = ""
    include_container: bool = False
    only_container: bool = False
    proc: None | subprocess.Popen[bytes] = None
    server: bool = False

    def __post_init__(self) -> None:
        """Initialize the infrastructure.

        Raises:
            ValueError: If the container engine is not found.
            ValueError: If the container name is not set.
            ValueError: If both only_container and include_container are set.
        """
        self.container_engine = self.session.config.getoption("--container-engine")
        self.container_name = self.session.config.getoption("--container-name", "")
        self.image_name = self.session.config.getoption("--image-name", "")
        self.include_container = self.session.config.getoption("--include-container")
        self.only_container = self.session.config.getoption("--only-container")
        if self.only_container or self.include_container:
            if not self.container_name:
                err = "ADT_CONTAINER_NAME must be set for container tests"
                raise ValueError(err)
            if not self.container_engine:
                err = "No container engine found, required for container tests"
                raise ValueError(err)
        elif self.only_container and self.include_container:
            err = "Cannot use both --only-container and --include-container"
            raise ValueError(err)

        if self.only_container:
            self.container = True
            self.server = False
        elif self.include_container:
            self.container = True
            self.server = True
        else:
            self.container = False
            self.server = True


INFRASTRUCTURE: Infrastructure


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add options to pytest.

    Args:
        parser: The pytest parser.
    """
    parser.addoption(
        "--container-engine",
        action="store",
        default=os.environ.get(
            "ADT_CONTAINER_ENGINE",
            shutil.which("podman") or shutil.which("docker") or "",
        ),
        help="Container engine to use. (default=ADT_CONTAINER_ENGINE, podman, docker, '')",
    )
    parser.addoption(
        "--container-name",
        action="store",
        default=os.environ.get("ADT_CONTAINER_NAME", "adt-test-container"),
        help="Container name to use for the running container. (default=ADT_CONTAINER_NAME)",
    )
    parser.addoption(
        "--image-name",
        action="store",
        default=os.environ.get("ADT_IMAGE_NAME", ""),
        help="Container name to use. (default=ADT_IMAGE_NAME)",
    )
    parser.addoption(
        "--only-container",
        action="store_true",
        default=False,
        help="Only run container tests",
    )
    parser.addoption(
        "--include-container",
        action="store_true",
        default=False,
        help="Include container tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest.

    Args:
        config: The pytest configuration.
    """
    config.addinivalue_line("markers", "container: container tests")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Modify the collection of items.

    Args:
        config: The pytest configuration.
        items: The list of items.
    """
    if config.getoption("--only-container"):
        skip_container = pytest.mark.skip(reason="--only-container specified")
        for item in items:
            if "container" not in item.keywords:
                item.add_marker(skip_container)
    elif not config.getoption("--include-container"):
        skip_container = pytest.mark.skip(reason="need --include-container option to run")
        for item in items:
            if "container" in item.keywords:
                item.add_marker(skip_container)


@pytest.fixture(scope="session")
def dev_tools_server() -> str:
    """Run the server.

    Returns:
        str: The server URL.
    """
    return "http://localhost:8000"


def pytest_sessionstart(session: pytest.Session) -> None:
    """Start the server.

    Args:
        session: The pytest session.
    """
    assert session

    if os.environ.get("PYTEST_XDIST_WORKER"):
        return

    global INFRASTRUCTURE  # noqa: PLW0603

    INFRASTRUCTURE = Infrastructure(session)

    if INFRASTRUCTURE.container:
        _start_container()
    if INFRASTRUCTURE.server:
        _start_server()


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Stop the server.

    Args:
        session: The pytest session.
    """
    assert session
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return

    if INFRASTRUCTURE.container:
        _stop_container()
    if INFRASTRUCTURE.server:
        _stop_server()


def _start_container() -> None:
    """Start the container."""
    cmd = [
        INFRASTRUCTURE.container_engine,
        "run",
        "-d",
        "--rm",
        "--name",
        INFRASTRUCTURE.container_name,
        INFRASTRUCTURE.image_name,
        "sleep",
        "infinity",
    ]
    subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603


def _stop_container() -> None:
    """Stop the container."""
    cmd = [
        INFRASTRUCTURE.container_engine,
        "stop",
        INFRASTRUCTURE.container_name,
    ]
    subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603


def _exec_container(command: str) -> subprocess.CompletedProcess[str]:
    """Run the container.

    Args:
        command: The command to run

    Returns:
        subprocess.CompletedProcess: The completed process.
    """
    cmd = f"{INFRASTRUCTURE.container_engine} exec -it {INFRASTRUCTURE.container_name} {command}"
    return subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        shell=True,
    )


@pytest.fixture()
def exec_container() -> Callable[[str], subprocess.CompletedProcess[str]]:
    """Run the container.

    Returns:
        callable: The container executor.
    """
    return _exec_container


def _start_server() -> None:
    """Start the server.

    Raises:
        RuntimeError: If the server could not be started.
    """
    bin_path = Path(sys.executable).parent / "adt"
    INFRASTRUCTURE.proc = subprocess.Popen(  # noqa: S603
        [bin_path, "server", "-p", "8000"],
        env=os.environ,
    )
    tries = 0
    max_tries = 10
    while tries < max_tries:
        try:
            res = requests.get("http://localhost:8000", timeout=1)
            if res.status_code == requests.codes.get("not_found"):
                return
        except requests.exceptions.ConnectionError:  # noqa: PERF203
            tries += 1
            time.sleep(1)

    msg = "Could not start the server."
    raise RuntimeError(msg)


def _stop_server() -> None:
    """Stop the server.

    Raises:
        RuntimeError: If the server is not running.
    """
    if INFRASTRUCTURE.proc is None:
        msg = "The server is not running."
        raise RuntimeError(msg)
    INFRASTRUCTURE.proc.terminate()
    INFRASTRUCTURE.proc.wait()
    INFRASTRUCTURE.proc = None
