"""Test the server utilities."""

import json

from http import HTTPStatus

import pytest

from django.http import HttpRequest, HttpResponse
from django.test.client import RequestFactory

from ansible_dev_tools.server_utils import validate_request, validate_response
from ansible_dev_tools.subcommands.server import Server


@pytest.fixture(name="collection_request")
def fixture_collection_request() -> HttpRequest:
    """Return a request object.

    Returns:
        HttpRequest: A Django request object.
    """
    Server(port="8000", debug=True)
    rf = RequestFactory()
    data = {"project": "collection", "collection": "namespace.name"}
    return rf.post(
        path="/v1/creator/collection",
        data=data,
        content_type="application/json",
    )


def test_validate_request_pass(collection_request: HttpRequest) -> None:
    """Test the validate_request function for success.

    Instantiate the Server to set the django settings.

    Args:
        collection_request: A Django request object
    """
    result = validate_request(collection_request)
    assert result.errors == []
    assert result.body == json.loads(collection_request.body)


def test_validate_request_fail() -> None:
    """Test the validate_request function for failure."""
    Server(port="8000", debug=True)
    rf = RequestFactory()
    request = rf.get("/hello/")
    result = validate_request(request)
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_validate_response_pass(collection_request: HttpRequest) -> None:
    """Test the validate_response function for success.

    Args:
        collection_request: A Django request object
    """
    response = HttpResponse()
    response["Content-Type"] = "application/tar+gzip"
    response.status_code = HTTPStatus.CREATED
    response.content = b"Hello, World!"
    result = validate_response(collection_request, response)
    assert result.status_code == HTTPStatus.CREATED


def test_validate_response_fail(collection_request: HttpRequest) -> None:
    """Test the validate_response function for failure.

    The response is missing data.

    Args:
        collection_request: A Django request object
    """
    response = HttpResponse()
    response["Content-Type"] = "application/tar+gzip"
    response.status_code = HTTPStatus.CREATED
    result = validate_response(collection_request, response)
    assert result.status_code == HTTPStatus.BAD_REQUEST
