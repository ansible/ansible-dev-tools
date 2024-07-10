"""Run tests against the container."""

import subprocess

from collections.abc import Callable

import pytest

from ansible_dev_tools.version_builder import PKGS


@pytest.mark.container()
def test_versions(exec_container: Callable[[str], subprocess.CompletedProcess[str]]) -> None:
    """Test the versions.

    Args:
        exec_container: The container executor.
    """
    versions = exec_container("adt --version")
    for pkg in PKGS:
        assert pkg in versions.stdout, f"{pkg} not found in version output"
