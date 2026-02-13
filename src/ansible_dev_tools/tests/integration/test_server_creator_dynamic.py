"""Test the dynamic creator API endpoints."""

from __future__ import annotations

import json
import tarfile

from typing import TYPE_CHECKING

import requests


if TYPE_CHECKING:
    from pathlib import Path


# --- Capabilities tests ---


def test_capabilities(server_url: str) -> None:
    """Test that the capabilities endpoint returns the command tree.

    Args:
        server_url: The server URL.
    """
    response = requests.get(f"{server_url}/v2/creator/capabilities", timeout=10)
    assert response.status_code == requests.codes.get("ok")
    data = response.json()
    assert data["name"] == "ansible-creator"
    assert "subcommands" in data
    assert "init" in data["subcommands"]
    assert "add" in data["subcommands"]
    # Verify init has expected project types
    init_cmd = data["subcommands"]["init"]
    assert "subcommands" in init_cmd
    assert "collection" in init_cmd["subcommands"]
    assert "playbook" in init_cmd["subcommands"]
    assert "execution_env" in init_cmd["subcommands"]


def test_capabilities_wrong_method(server_url: str) -> None:
    """Test that POST to capabilities returns 400.

    Args:
        server_url: The server URL.
    """
    response = requests.post(f"{server_url}/v2/creator/capabilities", timeout=10)
    assert response.status_code == requests.codes.get("bad_request")


# --- Schema tests ---


def test_schema_init_collection(server_url: str) -> None:
    """Test schema endpoint for init collection command.

    Args:
        server_url: The server URL.
    """
    response = requests.get(
        f"{server_url}/v2/creator/schema",
        params=[("command_path", "init"), ("command_path", "collection")],
        timeout=10,
    )
    assert response.status_code == requests.codes.get("ok")
    data = response.json()
    assert data["name"] == "collection"
    assert "parameters" in data
    assert "collection" in data["parameters"]["properties"]


def test_schema_add_resource_devfile(server_url: str) -> None:
    """Test schema endpoint for add resource devfile command.

    Args:
        server_url: The server URL.
    """
    response = requests.get(
        f"{server_url}/v2/creator/schema",
        params=[
            ("command_path", "add"),
            ("command_path", "resource"),
            ("command_path", "devfile"),
        ],
        timeout=10,
    )
    assert response.status_code == requests.codes.get("ok")
    data = response.json()
    assert data["name"] == "devfile"


def test_schema_invalid_path(server_url: str) -> None:
    """Test schema endpoint with an invalid command path.

    Args:
        server_url: The server URL.
    """
    response = requests.get(
        f"{server_url}/v2/creator/schema",
        params=[("command_path", "init"), ("command_path", "nonexistent")],
        timeout=10,
    )
    assert response.status_code == requests.codes.get("bad_request")
    data = response.json()
    assert "error" in data


def test_schema_missing_param(server_url: str) -> None:
    """Test schema endpoint without command_path parameter.

    Args:
        server_url: The server URL.
    """
    response = requests.get(f"{server_url}/v2/creator/schema", timeout=10)
    assert response.status_code == requests.codes.get("bad_request")
    assert "command_path" in response.text


def test_schema_wrong_method(server_url: str) -> None:
    """Test that POST to schema returns 400.

    Args:
        server_url: The server URL.
    """
    response = requests.post(f"{server_url}/v2/creator/schema", timeout=10)
    assert response.status_code == requests.codes.get("bad_request")


# --- Scaffold tests ---


def test_scaffold_init_ee(server_url: str, tmp_path: Path) -> None:
    """Test scaffolding an execution environment project.

    Args:
        server_url: The server URL.
        tmp_path: Pytest tmp_path fixture.
    """
    response = requests.post(
        f"{server_url}/v2/creator/scaffold",
        json={"command_path": ["init", "execution_env"]},
        timeout=10,
    )
    assert response.status_code == requests.codes.get("created")
    assert response.headers["Content-Type"] == "application/tar"
    assert "X-Creator-Message" in response.headers
    dest_file = tmp_path / "ee.tar"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert "./execution-environment.yml" in file.getnames()


def test_scaffold_add_devfile(server_url: str, tmp_path: Path) -> None:
    """Test scaffolding a devfile resource.

    Args:
        server_url: The server URL.
        tmp_path: Pytest tmp_path fixture.
    """
    response = requests.post(
        f"{server_url}/v2/creator/scaffold",
        json={"command_path": ["add", "resource", "devfile"]},
        timeout=10,
    )
    assert response.status_code == requests.codes.get("created")
    assert response.headers["Content-Type"] == "application/tar"
    dest_file = tmp_path / "devfile.tar"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert "./devfile.yaml" in file.getnames()


def test_scaffold_init_collection(server_url: str, tmp_path: Path) -> None:
    """Test scaffolding a collection project with params.

    Args:
        server_url: The server URL.
        tmp_path: Pytest tmp_path fixture.
    """
    response = requests.post(
        f"{server_url}/v2/creator/scaffold",
        json={
            "command_path": ["init", "collection"],
            "params": {"collection": "namespace.name"},
        },
        timeout=10,
    )
    assert response.status_code == requests.codes.get("created")
    assert response.headers["Content-Type"] == "application/tar"
    # Check logs header is present and valid JSON
    logs_header = response.headers.get("X-Creator-Logs", "[]")
    logs = json.loads(logs_header)
    assert isinstance(logs, list)
    dest_file = tmp_path / "collection.tar"
    with dest_file.open(mode="wb") as tar_file:
        tar_file.write(response.content)
    with tarfile.open(dest_file) as file:
        assert "./galaxy.yml" in file.getnames()


def test_scaffold_invalid_command(server_url: str) -> None:
    """Test scaffold with an invalid command path returns error JSON.

    Args:
        server_url: The server URL.
    """
    response = requests.post(
        f"{server_url}/v2/creator/scaffold",
        json={"command_path": ["init", "nonexistent"]},
        timeout=10,
    )
    assert response.status_code == requests.codes.get("bad_request")
    data = response.json()
    assert data["status"] == "error"
    assert "logs" in data


def test_scaffold_missing_command_path(server_url: str) -> None:
    """Test scaffold without command_path returns 400.

    The OpenAPI schema requires ``command_path``, so the request is
    rejected at the validation layer before reaching the handler.

    Args:
        server_url: The server URL.
    """
    response = requests.post(
        f"{server_url}/v2/creator/scaffold",
        json={},
        timeout=10,
    )
    assert response.status_code == requests.codes.get("bad_request")


def test_scaffold_wrong_method(server_url: str) -> None:
    """Test that GET to scaffold returns 400.

    Args:
        server_url: The server URL.
    """
    response = requests.get(f"{server_url}/v2/creator/scaffold", timeout=10)
    assert response.status_code == requests.codes.get("bad_request")
