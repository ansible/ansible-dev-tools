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
from __future__ import annotations

import errno
import os
import pty
import select
import shutil
import subprocess
import sys
import time
import warnings

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import requests

import ansible_dev_tools  # noqa: F401

from ansible_dev_tools.subcommands.server import Server


if TYPE_CHECKING:
    from collections.abc import Callable


FIXTURES_DIR = Path(__file__).parent / "fixtures"


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
        navigator_ee: The image to use with ansible navigator
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
    navigator_ee: str = ""

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
        default=os.environ.get(
            "ADT_IMAGE_NAME",
            "ghcr.io/ansible/community-ansible-dev-tools:latest",
        ),
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
def server_url() -> str:
    """Run the server.

    Returns:
        str: The server URL.
    """
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def server_in_container_url() -> str:
    """Run the server.

    Returns:
        str: The server URL.
    """
    return "http://localhost:8001"


def pytest_sessionstart(session: pytest.Session) -> None:
    """Start the server.

    Args:
        session: The pytest session.
    """
    if session.config.option.collectonly:
        return

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
    if session.config.option.collectonly:
        return
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return

    if INFRASTRUCTURE.container:
        _stop_container()
    if INFRASTRUCTURE.server:
        _stop_server()


BASE_CMD = """{container_engine} run -d --rm
 --cap-add=SYS_ADMIN
 --cap-add=SYS_RESOURCE
 --device "/dev/fuse"
 -e NO_COLOR=1
 --hostname=ansible-dev-container
 --name={container_name}
 -p 8001:8001
 --security-opt "apparmor=unconfined"
 --security-opt "label=disable"
 --security-opt "seccomp=unconfined"
 -v $PWD:/workdir
"""

PODMAN_CMD = """ --user=root
 --userns=host
"""

DOCKER_CMD = """ --user=root
"""

END = """ {image_name}
 adt server --port 8001
 """


def _start_container() -> None:
    """Start the container.

    The default image for navigator is pulled ahead of time.
    It is determined by the container image name. If the image name
    starts with localhost, the default ee for navigator is pulled.
    If the image name contains a /, that is used, otherwise the default
    ee for navigator is pulled.

    Raises:
        ValueError: If the container engine is not podman or docker.
    """
    cmd = (
        f"{INFRASTRUCTURE.container_engine} kill {INFRASTRUCTURE.container_name};"
        f"{INFRASTRUCTURE.container_engine} rm {INFRASTRUCTURE.container_name}"
    )
    subprocess.run(cmd, check=False, capture_output=True, shell=True, text=True)

    auth_file = "$XDG_RUNTIME_DIR/containers/auth.json"
    auth_mount = ""
    if "XDG_RUNTIME_DIR" in os.environ and Path(os.path.expandvars(auth_file)).exists():
        auth_mount = f" -v {auth_file}:/run/containers/0/auth.json"

    if "podman" in INFRASTRUCTURE.container_engine:
        cmd = BASE_CMD + PODMAN_CMD + auth_mount + END
        warnings.warn("Podman auth mount added: " + auth_mount, stacklevel=0)
    elif "docker" in INFRASTRUCTURE.container_engine:
        cmd = BASE_CMD + DOCKER_CMD + END
    else:
        err = f"Container engine {INFRASTRUCTURE.container_engine} not found."
        raise ValueError(err)

    cmd = cmd.replace("\n", " ").format(
        container_engine=INFRASTRUCTURE.container_engine,
        container_name=INFRASTRUCTURE.container_name,
        image_name=INFRASTRUCTURE.image_name,
    )
    try:
        subprocess.run(cmd, check=True, capture_output=True, shell=True, text=True)
    except subprocess.CalledProcessError as exc:
        err = (
            f"Failed to start container:\n"
            f"cmd: {cmd}\n"
            f"stdout: {exc.stdout}\n"
            f"stderr: {exc.stderr}"
        )
        pytest.fail(err)

    # image is local, can't be pulled, use default
    if INFRASTRUCTURE.image_name.startswith("localhost"):
        nav_ee = get_nav_default_ee_in_container()
        warning = f"localhost in image name, pulling default {nav_ee} for navigator"
    # dots and slashes in image name, use it
    elif "/" in INFRASTRUCTURE.image_name and "." in INFRASTRUCTURE.image_name:
        nav_ee = INFRASTRUCTURE.image_name
        warning = f"/ and . in image name, pulling {nav_ee} for navigator"
    # otherwise, use default
    else:
        nav_ee = get_nav_default_ee_in_container()
        warning = f"localhost / . not in image name, pulling default {nav_ee} for navigator"
    warnings.warn(warning, stacklevel=0)
    INFRASTRUCTURE.navigator_ee = nav_ee
    _proc = _exec_container(command=f"podman pull {nav_ee}")


def get_nav_default_ee_in_container() -> str:
    """Get the default ee for navigator in the container.

    Returns:
        str: The default ee for navigator in the container.
    """
    cmd = (
        'python -c "from ansible_navigator.utils.packaged_data import ImageEntry;'
        'print(ImageEntry.DEFAULT_EE.get(app_name=\\"ansible_navigator\\"))"'
    )

    proc = _exec_container(cmd)
    return proc.stdout.strip()


@pytest.fixture(name="nav_default_ee")
def nav_default_ee() -> str:
    """Get the default ee for navigator in the container.

    Returns:
        str: The default ee for navigator in the container.
    """
    return get_nav_default_ee_in_container()


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
    cmd = (
        f"{INFRASTRUCTURE.container_engine} exec -t"
        f" {INFRASTRUCTURE.container_name} bash -c '{command}'"
    )
    return subprocess.run(
        cmd,
        check=False,
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


@pytest.fixture()
def test_fixture_dir(request: pytest.FixtureRequest) -> Path:
    """Provide the fixture directory for a given test.

    Args:
        request: The pytest fixture request.

    Returns:
        Path: The test fixture directory.
    """
    return FIXTURES_DIR / request.path.relative_to(Path(__file__).parent).with_suffix("")


@pytest.fixture()
def test_fixture_dir_container(request: pytest.FixtureRequest) -> Path:
    """Provide the fixture directory for a given test within the container.

    Args:
        request: The pytest fixture request.

    Returns:
        Path: The test fixture directory within the container.
    """
    return Path("/workdir/tests/fixtures") / request.path.relative_to(
        Path(__file__).parent,
    ).with_suffix("")


@pytest.fixture()
def infrastructure() -> Infrastructure:
    """Provide the infrastructure.

    Returns:
        Infrastructure: The infrastructure.
    """
    return INFRASTRUCTURE


def _cmd_in_tty(  # noqa: C901
    cmd: str,
    bytes_input: bytes | None = None,
    cwd: Path | None = None,
) -> tuple[str, str, int]:
    """Capture the output of cmd using a tty.

    Based on Andy Hayden's gist:
    https://gist.github.com/hayd/4f46a68fc697ba8888a7b517a414583e

    Args:
        cmd: The command to run
        bytes_input: Some bytes to input
        cwd: The working directory

    Raises:
        OSError: If the command fails
    Returns:
        stdout, stderr, and the exit code
    """
    m_stdout, s_stdout = pty.openpty()  # provide tty to enable line-buffering
    m_stderr, s_stderr = pty.openpty()
    m_stdin, s_stdin = pty.openpty()

    with subprocess.Popen(
        cmd,
        bufsize=1,
        cwd=cwd,
        shell=True,
        stdin=s_stdin,
        stdout=s_stdout,
        stderr=s_stderr,
        close_fds=True,
    ) as proc:
        for file_d in [s_stdout, s_stderr, s_stdin]:
            os.close(file_d)
        if bytes_input:
            os.write(m_stdin, bytes_input)

        timeout = 0.04
        readable = [m_stdout, m_stderr]
        result = {m_stdout: b"", m_stderr: b""}
        try:
            while readable:
                ready, _, _ = select.select(readable, [], [], timeout)
                for file_d in ready:
                    try:
                        data = os.read(file_d, 512)
                    except OSError as exc:  # noqa: PERF203
                        if exc.errno != errno.EIO:
                            raise
                        # EIO means EOF on some systems
                        readable.remove(file_d)
                    else:
                        if not data:  # EOF
                            readable.remove(file_d)
                        result[file_d] += data

        finally:
            for file_d in [m_stdout, m_stderr, m_stdin]:
                os.close(file_d)
            if proc.poll() is None:
                proc.kill()
            proc.wait()

    return result[m_stdout].decode("utf-8"), result[m_stderr].decode("utf-8"), proc.returncode


@pytest.fixture()
def cmd_in_tty() -> Callable[..., tuple[str, str, int]]:
    """Provide the cmd in tty function as a fixture.

    Returns:
        The cmd in tty function
    """
    return _cmd_in_tty


@pytest.fixture(scope="session", autouse=True)
def adt_server() -> Server:
    """Configure the server and it's settings.

    This prevents the django settings from getting initialized multiple times.

    Returns:
        Server: The server instance
    """
    return Server(port="8000", debug=True)
