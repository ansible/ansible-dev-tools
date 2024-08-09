"""Test the server utilities.

Of interest for these tests may be the autouse fixture in the root
confest.py file. This fixture initializes and optionally returns
the Server instance configured with the Django settings.
"""

from __future__ import annotations

import json

from http import HTTPStatus

import pytest

from django.http import HttpRequest, HttpResponse
from django.test.client import RequestFactory
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult

from ansible_dev_tools.server_utils import validate_request, validate_response


@pytest.fixture(name="collection_request")
def fixture_collection_request() -> HttpRequest:
    """Return a request object.

    Returns:
        HttpRequest: A Django request object.
    """
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
    assert isinstance(result, RequestUnmarshalResult)
    assert result.errors == []
    assert result.body == json.loads(collection_request.body)


def test_validate_request_fail() -> None:
    """Test the validate_request function for failure."""
    rf = RequestFactory()
    request = rf.get("/hello/")
    result = validate_request(request)
    assert isinstance(result, HttpResponse)
    assert result.status_code == HTTPStatus.BAD_REQUEST.value


def test_validate_response_pass(collection_request: HttpRequest) -> None:
    """Test the validate_response function for success.

    Args:
        collection_request: A Django request object
    """
    response = HttpResponse()
    response["Content-Type"] = "application/tar+gzip"
    response.status_code = HTTPStatus.CREATED.value
    response.content = b"Hello, World!"
    result = validate_response(collection_request, response)
    assert result.status_code == HTTPStatus.CREATED.value


def test_validate_response_fail(collection_request: HttpRequest) -> None:
    """Test the validate_response function for failure.

    The response is missing data.

    Args:
        collection_request: A Django request object
    """
    response = HttpResponse()
    response["Content-Type"] = "application/tar+gzip"
    response.status_code = HTTPStatus.CREATED.value
    result = validate_response(collection_request, response)
    assert result.status_code == HTTPStatus.BAD_REQUEST.value
