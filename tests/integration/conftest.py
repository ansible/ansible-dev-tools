"""Fixtures for the tests."""

import subprocess
import sys
import time

from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def dev_tools_server() -> Generator[str, None, None]:
    """Run the server."""
    bin_path = Path(sys.executable).parent / "adt"
    with subprocess.Popen(
        [bin_path, "server", "-p", "8000", "--debug"],  # noqa: S603
    ) as proc:
        time.sleep(1)  # allow the server to start
        yield "http://localhost:8000"
        proc.terminate()
