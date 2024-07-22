"""Run tests against the container."""

import subprocess

from collections.abc import Callable
from pathlib import Path

import pytest

from ansible_navigator.utils.packaged_data import ImageEntry

from ansible_dev_tools.version_builder import PKGS

from ..conftest import Infrastructure  # noqa: TID252
from .conftest import ContainerTmux
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
        f" --mode stdout --pae false --lf {tmp_path}/navigator.log",
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


@pytest.mark.container()
def test_nav_collections(container_tmux: ContainerTmux, tmp_path: Path) -> None:
    """Test ansible-navigator collections.

    Args:
        container_tmux: A tmux session attached to the container.
        tmp_path: The temporary directory
    """
    cmd = f"ansible-navigator collections --lf {tmp_path}/navigator.log"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for=":help help", timeout=10)
    assert any("ansible.builtin" in line for line in stdout)
    assert any("ansible.posix" in line for line in stdout)
    cmd = ":0"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for=":help help")
    assert any("add_host" in line for line in stdout)


@pytest.mark.container()
def test_nav_images(container_tmux: ContainerTmux, tmp_path: Path) -> None:
    """Test ansible-navigator images.

    Args:
        container_tmux: A tmux session attached to the container.
        tmp_path: The temporary directory
    """
    cmd = f"ansible-navigator images --lf {tmp_path}/navigator.log"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for=":help help", timeout=10)
    nav_default = ImageEntry.DEFAULT_EE.get(app_name="ansible_navigator")
    assert any(nav_default in line for line in stdout)


def test_nav_playbook(container_tmux: ContainerTmux, tmp_path: Path) -> None:
    """Test ansible-navigator run using a creator created playbook.

    Args:
        container_tmux: A tmux session attached to the container.
        tmp_path: The temporary directory
    """
    cmd = f"ansible-creator init playbook test_ns.test_name {tmp_path}"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for="created", timeout=10)
    output = f"Note: ansible project created at {tmp_path}"
    assert any(output in line for line in stdout)
    cmd = f"cd {tmp_path} && ansible-navigator run site.yml"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for="Successful", timeout=10)
    assert stdout[-1].endswith("Successful")


def test_nav_collection(container_tmux: ContainerTmux, tmp_path: Path) -> None:
    """Test ansible-navigator run using a creator created collection.

    Args:
        container_tmux: A tmux session attached to the container.
        tmp_path: The temporary directory
    """
    namespace = "test_ns"
    name = "test_name"
    collection_path = tmp_path / "collections" / "ansible_collections" / namespace / name
    cmd = f"ansible-creator init collection test_ns.test_name {collection_path}"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for="created", timeout=10)
    output = f"Note: collection {namespace}.{name} created"
    assert any(output in line for line in stdout)
    cmd = (
        f"ANSIBLE_COLLECTIONS_PATH={tmp_path}/collections ansible-navigator collections --ee false"
    )
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for=":help help", timeout=10)
    assert any(f"{namespace}.{name}" in line for line in stdout)
