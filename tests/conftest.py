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
import subprocess
import sys
import time

from pathlib import Path

import pytest
import requests

import ansible_dev_tools  # noqa: F401


PROC: None | subprocess.Popen[bytes] = None


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

    Raises:
        RuntimeError: If the server could not be started.
    """
    assert session
    bin_path = Path(sys.executable).parent / "adt"

    if os.environ.get("PYTEST_XDIST_WORKER"):
        return

    global PROC  # noqa: PLW0603
    PROC = subprocess.Popen(
        [bin_path, "server", "-p", "8000"],  # noqa: S603
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


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Stop the server.

    Args:
        session: The pytest session.

    Raises:
        RuntimeError: If the server could not be stopped.
    """
    assert session
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return

    global PROC  # noqa: PLW0603
    if PROC is None:
        msg = "The server is not running."
        raise RuntimeError(msg)
    PROC.terminate()
    PROC.wait()
    PROC = None
