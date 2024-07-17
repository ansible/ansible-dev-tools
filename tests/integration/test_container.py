"""Run tests against the container."""

import subprocess

from collections.abc import Callable
from pathlib import Path

import pytest

from ansible_dev_tools.version_builder import PKGS

from ..conftest import Infrastructure  # noqa: TID252
from .test_server_creator import test_collection_v1 as tst_collection_v1
from .test_server_creator import test_error as tst_error
from .test_server_creator import test_playbook_v1 as tst_playbook_v1


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
        f"ansible-navigator run {playbook}"
        f" --mode stdout --pp never --pae false --lf {tmp_path}/navigator.log",
    )
    assert "Success" in result.stdout
    assert "ok=1" in result.stdout


@pytest.mark.container()
def test_navigator_simple(
    cmd_in_tty: Callable[[str], tuple[str, str, int]],
    infrastructure: Infrastructure,
    test_fixture_dir: Path,
    tmp_path: Path,
) -> None:
    """Test ansible-navigator run using the container as an ee.

    Use the container engine specified in the infrastructure fixture
    but pass only the executable name to the --ce option.

    Args:
        cmd_in_tty: The command in tty executor.
        infrastructure: The testing infrastructure
        test_fixture_dir: The test fixture directory.
        tmp_path: The temporary directory.
    """
    playbook = test_fixture_dir / "site.yml"
    cmd = (
        f" ansible-navigator run {playbook}"
        f" --mode stdout --pp never --pae false --lf {tmp_path}/navigator.log"
        f" --ce {infrastructure.container_engine.split('/')[-1]}"
        f" --eei {infrastructure.image_name}"
    )
    stdout, stderr, return_code = cmd_in_tty(cmd)
    assert not stderr
    assert return_code == 0
    assert "Success" in stdout
    assert "ok=1" in stdout


@pytest.mark.container()
def test_error_container(server_in_container_url: str) -> None:
    """Test the error response.

    Args:
        server_in_container_url: The dev tools server.
    """
    tst_error(server_url=server_in_container_url)


@pytest.mark.container()
def test_collection_v1_container(server_in_container_url: str, tmp_path: Path) -> None:
    """Test the collection creation.

    Args:
        server_in_container_url: The dev tools server.
        tmp_path: The temporary directory.
    """
    tst_collection_v1(server_url=server_in_container_url, tmp_path=tmp_path)


@pytest.mark.container()
def test_playbook_v1_container(server_in_container_url: str, tmp_path: Path) -> None:
    """Test the playbook creation.

    Args:
        server_in_container_url: The dev tools server.
        tmp_path: The temporary directory.
    """
    tst_playbook_v1(server_url=server_in_container_url, tmp_path=tmp_path)
