"""Test the dev tools server for metadata."""

from __future__ import annotations

import requests


def test_metadata(server_url: str) -> None:
    """Test the server info endpoint.

    Args:
        server_url: The server URL.
    """
    endpoint = f"{server_url}/metadata"

    response = requests.get(endpoint, timeout=10)

    expected_response_code = 200
    assert response.status_code == expected_response_code, (
        f"Expected status code 200 but got {response.status_code}"
    )

    assert response.headers["Content-Type"] == "application/json"

    data = response.json()

    assert "versions" in data, "Response is missing 'versions' key"
    assert "apis" in data, "Response is missing 'apis' key"

    assert len(data["versions"]) > 0, "Versions should contain at least one package"

    assert len(data["apis"]) > 0, "APIs should contain at least one endpoint"
