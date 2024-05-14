"""Test the dev tools server for creator."""

import tarfile

from pathlib import Path

import requests


def test_error(dev_tools_server: str) -> None:
    """Test the error response."""
    response = requests.post(f"{dev_tools_server}/v1/creator/playbook", timeout=1)
    assert response.status_code == requests.codes.get("bad_request")
    assert response.text == "Missing required request body"


def test_playbook_v1(dev_tools_server: str, tmp_path: Path) -> None:
    """Test the playbook creation."""
    response = requests.post(
        f"{dev_tools_server}/v1/creator/playbook",
        json={
            "project": "ansible-project",
            "scm_org": "ansible",
            "scm_project": "devops",
        },
        timeout=1,
    )
    assert response.status_code == requests.codes.get("created")
    assert (
        response.headers["Content-Disposition"]
        == 'attachment; filename="ansible-devops.tar.gz"'
    )
    assert response.headers["Content-Type"] == "application/tar+gzip"
    dest_file = tmp_path / "ansible-devops.tar.gz"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert (
            "./collections/ansible_collections/ansible/devops/roles/run/README.md"
            in file.getnames()
        )


def test_collection_v1(dev_tools_server: str, tmp_path: Path) -> None:
    """Test the collection creation."""
    response = requests.post(
        f"{dev_tools_server}/v1/creator/collection",
        json={
            "collection": "namespace.name",
            "project": "collection",
        },
        timeout=1,
    )
    assert response.status_code == requests.codes.get("created")
    assert (
        response.headers["Content-Disposition"]
        == 'attachment; filename="namespace.name.tar.gz"'
    )
    assert response.headers["Content-Type"] == "application/tar+gzip"
    dest_file = tmp_path / "namespace.name.tar.gz"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert "./roles/run/tasks/main.yml" in file.getnames()
