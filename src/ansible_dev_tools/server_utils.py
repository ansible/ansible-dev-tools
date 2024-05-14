"""Utility functions requiring server dependencies."""

from importlib import resources as importlib_resources

import yaml

from django.http import FileResponse, HttpRequest, HttpResponse
from openapi_core import OpenAPI
from openapi_core.contrib.django import DjangoOpenAPIRequest, DjangoOpenAPIResponse
from openapi_core.exceptions import OpenAPIError
from openapi_core.unmarshalling.request.datatypes import RequestUnmarshalResult


OPENAPI = OpenAPI.from_dict(
    yaml.safe_load(
        (
            importlib_resources.files("ansible_dev_tools.resources.server.data")
            / "openapi.yaml"
        ).read_text(),
    ),
)


def validate_request(request: HttpRequest) -> RequestUnmarshalResult | HttpResponse:
    """
    Validate the request against the OpenAPI schema.

    Args:
        request: HttpRequest object.

    Returns:
        The request body or the error HTTP response is validation fails.
    """
    try:
        openapi_request = DjangoOpenAPIRequest(request)
        OPENAPI.validate_request(openapi_request)
    except OpenAPIError as exc:
        return HttpResponse(str(exc), status=400)
    return OPENAPI.unmarshal_request(openapi_request)


def validate_response(
    request: HttpRequest,
    response: FileResponse | HttpResponse,
) -> FileResponse | HttpResponse:
    """
    Validate the response against the OpenAPI schema.

    Args:
        request: HttpRequest object.
        response: HttpResponse object.

    Returns:
        HttpResponse: The response object.
    """
    try:
        OPENAPI.validate_response(
            request=DjangoOpenAPIRequest(request),
            response=DjangoOpenAPIResponse(response),
        )
    except OpenAPIError as exc:
        return HttpResponse(str(exc), status=400)
    return response
