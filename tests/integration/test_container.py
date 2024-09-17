"""Run tests against the container."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ansible_dev_tools.version_builder import PKGS

from .test_server_creator import test_collection_v1 as tst_collection_v1
from .test_server_creator import test_error as tst_error
from .test_server_creator import test_playbook_v1 as tst_playbook_v1


if TYPE_CHECKING:
    import subprocess

    from collections.abc import Callable
    from pathlib import Path

    from tests.conftest import Infrastructure

    from .conftest import ContainerTmux


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
def test_container_in_container(
    exec_container: Callable[[str], subprocess.CompletedProcess[str]],
) -> None:
    """Test podman container-in-container functionality for plugin copy.

    Args:
        exec_container: The container executor.
    """
    podman_run_container = exec_container(
        "podman run -i --rm -d -e ANSIBLE_DEV_TOOLS_CONTAINER=1 --user=root"
        " -e ANSIBLE_FORCE_COLOR=0 --name ghcr_io_ansible_community_ansible_dev_tools_latest"
        " ghcr.io/ansible/community-ansible-dev-tools:latest bash",
    )
    assert podman_run_container.returncode == 0

    test_path_access = exec_container(
        "podman exec ghcr_io_ansible_community_ansible_dev_tools_latest"
        " ls /usr/local/lib/python3.12/site-packages/ansible/plugins/",
    )
    assert "OCI permission denied" not in test_path_access.stdout
    assert test_path_access.returncode == 0


@pytest.mark.container()
@pytest.mark.parametrize("app", ("nano", "tar", "vi"))
def test_app(exec_container: Callable[[str], subprocess.CompletedProcess[str]], app: str) -> None:
    """Test the presence of an app in the container.

    Args:
        exec_container: The container executor.
        app: The app to test.
    """
    result = exec_container(f"{app} --version")
    assert result.returncode == 0, f"{app} command failed"


@pytest.mark.container()
def test_user_shell(exec_container: Callable[[str], subprocess.CompletedProcess[str]]) -> None:
    """Test the user shell.

    Args:
        exec_container: The container executor.
    """
    result = exec_container("cat /etc/passwd | grep root | grep zsh")
    assert result.returncode == 0, "zsh not found in /etc/passwd"


@pytest.mark.container()
def test_navigator_simple_c_in_c(
    exec_container: Callable[[str], subprocess.CompletedProcess[str]],
    test_fixture_dir_container: Path,
    tmp_path: Path,
    infrastructure: Infrastructure,
) -> None:
    """Test ansible-navigator run against a simple playbook within the container.

    Args:
        exec_container: The container executor.
        test_fixture_dir_container: The test fixture directory.
        tmp_path: The temporary directory.
        infrastructure: The testing infrastructure.
    """
    playbook = test_fixture_dir_container / "site.yml"
    result = exec_container(
        f"ansible-navigator run {playbook}"
        f" --mode stdout --pae false --lf {tmp_path}/navigator.log"
        f" --eei {infrastructure.navigator_ee} --pp never",
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
        f" --mode stdout --pae false --lf {tmp_path}/navigator.log"
        f" --ce {infrastructure.container_engine.split('/')[-1]}"
        f" --pp never --eei {infrastructure.image_name}"
    )
    stdout, stderr, return_code = cmd_in_tty(cmd)
    assert not stderr
    assert return_code == 0
    assert "Success" in stdout
    assert "ok=1" in stdout


@pytest.mark.container()
@pytest.mark.parametrize("resource", ("playbook", "collection"))
def test_error_container(server_in_container_url: str, resource: str) -> None:
    """Test the error response.

    Args:
        server_in_container_url: The dev tools server.
        resource: The resource to test.
    """
    tst_error(server_url=server_in_container_url, resource=resource)


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
def test_nav_collections(
    container_tmux: ContainerTmux,
    tmp_path: Path,
    infrastructure: Infrastructure,
) -> None:
    """Test ansible-navigator collections.

    Args:
        container_tmux: A tmux session attached to the container.
        tmp_path: The temporary directory
        infrastructure: The testing infrastructure
    """
    cmd = (
        f"ansible-navigator collections --lf {tmp_path}/navigator.log"
        f" --pp never --eei {infrastructure.navigator_ee}"
    )
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for=":help help", timeout=10)
    assert any("ansible.builtin" in line for line in stdout)
    assert any("ansible.posix" in line for line in stdout)
    cmd = ":0"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for=":help help")
    assert any("add_host" in line for line in stdout)


@pytest.mark.container()
def test_nav_images(
    container_tmux: ContainerTmux,
    tmp_path: Path,
    infrastructure: Infrastructure,
) -> None:
    """Test ansible-navigator images.

    Args:
        container_tmux: A tmux session attached to the container.
        tmp_path: The temporary directory
        infrastructure: The testing infrastructure
    """
    cmd = (
        f"ansible-navigator images --lf {tmp_path}/nav.log"
        f" --pp never --eei {infrastructure.navigator_ee}"
    )
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for=":help help", timeout=10)
    image = infrastructure.navigator_ee.split(":")[0].split("/")[-1]
    assert any(image in line for line in stdout)


@pytest.mark.container()
def test_nav_playbook(
    container_tmux: ContainerTmux,
    tmp_path: Path,
    infrastructure: Infrastructure,
) -> None:
    """Test ansible-navigator run using a creator created playbook.

    Args:
        container_tmux: A tmux session attached to the container.
        tmp_path: The temporary directory
        infrastructure: The testing infrastructure
    """
    cmd = f"ansible-creator init playbook test_ns.test_name {tmp_path}"
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for="created", timeout=10)
    output = "Note: ansible project created"
    assert any(output in line for line in stdout)
    cmd = (
        f"cd {tmp_path} &&"
        f" ansible-navigator run site.yml"
        f" --pp never --eei {infrastructure.navigator_ee}"
    )
    stdout = container_tmux.send_and_wait(cmd=cmd, wait_for="Successful", timeout=10)
    assert stdout[-1].endswith("Successful")


@pytest.mark.container()
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
