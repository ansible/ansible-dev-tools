"""Test the dev tools server for creator."""

from __future__ import annotations

import tarfile

from typing import TYPE_CHECKING

import pytest
import requests


if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("resource", ("playbook", "collection"))
def test_error_v2(server_url: str, resource: str) -> None:
    """Test the error response.

    Args:
        server_url: The server URL.
        resource: The resource to test.
    """
    response = requests.post(f"{server_url}/v2/creator/{resource}", timeout=10)
    assert response.status_code == requests.codes.get("bad_request")
    assert response.text == "Missing required request body"


def test_error_devfile_v2(server_url: str) -> None:
    """Test the error response when a request body is sent unexpectedly.

    Args:
        server_url: The server URL.

    Raises:
        AssertionError: If the test assertions fail (e.g., response status code or tar content).
    """
    # To simulate an error, we are sending the request with the get method as the api works with empty request body as well.
    response = requests.get(f"{server_url}/v2/creator/devfile", timeout=10)
    assert response.status_code == requests.codes.get("bad_request"), (
        f"Expected 400 but got {response.status_code}"
    )
    assert response.text == "Operation get not found for " + f"{server_url}/v2/creator/devfile"


def test_playbook_v2(server_url: str, tmp_path: Path) -> None:
    """Test the playbook creation.

    Args:
        server_url: The server URL.
        tmp_path: Pytest tmp_path fixture.
    """
    response = requests.post(
        f"{server_url}/v2/creator/playbook",
        json={
            "project": "ansible-project",
            "namespace": "ansible",
            "collection_name": "devops",
        },
        timeout=10,
    )
    assert response.status_code == requests.codes.get("created")
    assert response.headers["Content-Disposition"] == 'attachment; filename="ansible-devops.tar"'
    assert response.headers["Content-Type"] == "application/tar"
    dest_file = tmp_path / "ansible-devops.tar"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert (
            "./collections/ansible_collections/ansible/devops/roles/run/README.md"
            in file.getnames()
        )


def test_collection_v2(server_url: str, tmp_path: Path) -> None:
    """Test the collection creation.

    Args:
        server_url: The server URL.
        tmp_path: Pytest tmp_path fixture.
    """
    response = requests.post(
        f"{server_url}/v2/creator/collection",
        json={
            "collection": "namespace.name",
            "project": "collection",
        },
        timeout=10,
    )
    assert response.status_code == requests.codes.get("created")
    assert response.headers["Content-Disposition"] == 'attachment; filename="namespace.name.tar"'
    assert response.headers["Content-Type"] == "application/tar"
    dest_file = tmp_path / "namespace.name.tar"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert "./roles/run/tasks/main.yml" in file.getnames()


def test_devfile_v2(server_url: str, tmp_path: Path) -> None:
    """Test the devfile creation.

    Args:
        server_url: The server URL.
        tmp_path: Pytest tmp_path fixture.

    Raises:
        AssertionError: If the test assertions fail (e.g., response status code or tar content).
    """
    response = requests.post(
        f"{server_url}/v2/creator/devfile",
        json={},
        timeout=10,
    )
    assert response.status_code == requests.codes.get("created")
    assert response.headers["Content-Disposition"] == 'attachment; filename="devfile.tar"'
    assert response.headers["Content-Type"] == "application/tar"
    dest_file = tmp_path / "devfile.tar"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert "./devfile.yaml" in file.getnames()


def test_pattern_v2(server_url: str, tmp_path: Path) -> None:
    """Test the pattern creation.

    Args:
        server_url: The server URL.
        tmp_path: Pytest tmp_path fixture.
    """
    pattern_name = "foo"
    response = requests.post(
        f"{server_url}/v2/creator/pattern",
        json={
            "pattern_name": pattern_name,
        },
        timeout=10,
    )
    assert response.status_code == requests.codes.get("created")
    assert response.headers["Content-Disposition"] == f'attachment; filename="{pattern_name}.tar"'
    assert response.headers["Content-Type"] == "application/tar"
    dest_file = tmp_path / f"{pattern_name}.tar"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert "./extensions" in file.getnames()
