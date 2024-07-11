"""Run tests against the container."""

import subprocess

from collections.abc import Callable
from pathlib import Path

import pytest

from ansible_dev_tools.version_builder import PKGS

from ..conftest import Infrastructure  # noqa: TID252


@pytest.mark.container()
def test_versions(exec_container: Callable[[str], subprocess.CompletedProcess[str]]) -> None:
    """Test the versions.

    Args:
        exec_container: The container executor.
    """
    versions = exec_container("adt --version")
    for pkg in PKGS:
        assert pkg in versions.stdout, f"{pkg} not found in version output"


@pytest.mark.container()
def test_podman(exec_container: Callable[[str], subprocess.CompletedProcess[str]]) -> None:
    """Test podman from within the container.

    Args:
        exec_container: The container executor.
    """
    result = exec_container("podman run hello")
    assert result.returncode == 0, "podman command failed"


@pytest.mark.container()
def test_navigator_simple_c_in_c(
    exec_container: Callable[[str], subprocess.CompletedProcess[str]],
    test_fixture_dir_container: Path,
    tmp_path: Path,
) -> None:
    """Test ansible-navigator run against a simple playbook within the container.

    Args:
        exec_container: The container executor.
        test_fixture_dir_container: The test fixture directory.
        tmp_path: The temporary directory.
    """
    playbook = test_fixture_dir_container / "site.yml"
    result = exec_container(
        f" ansible-navigator run {playbook}"
        f" --mode stdout --pp never --pae false --lf {tmp_path}/navigator.log",
    )
    assert "Success" in result.stdout
    assert "ok=1" in result.stdout


@pytest.mark.container()
def test_navigator_simple(
    infrastructure: Infrastructure,
    test_fixture_dir: Path,
    tmp_path: Path,
) -> None:
    """Test ansible-navigator run using the container as an ee.

    Args:
        infrastructure: The testing infrastructure
        test_fixture_dir: The test fixture directory.
        tmp_path: The temporary directory.
    """
    playbook = test_fixture_dir / "site.yml"
    cmd = (
        f" ansible-navigator run {playbook}"
        f" --mode stdout --pp never --pae false --lf {tmp_path}/navigator.log"
        f" --ce {infrastructure.container_engine}"
        f" --eei {infrastructure.image_name}"
    )
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    assert "Success" in result.stdout
    assert "ok=1" in result.stdout
