"""The Server Info API."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.urls import get_resolver

from ansible_dev_tools.server_utils import validate_request
from ansible_dev_tools.version_builder import version_builder


class GetMetadata:
    """The metadata, returns the available tools with their versions and available API endpoints."""

    def server_info(self, request: HttpRequest) -> JsonResponse:
        """Return server information including versions and available APIs.

        Args:
            request: HttpRequest Object
        Returns:
            JSON response containing tool versions and available API endpoints.
        """
        validate_request(request)
        versions = {}
        for line in version_builder().splitlines():
            tool, version = line.split(maxsplit=1)
            versions[tool] = version

        resolver = get_resolver()
        urlpatterns = resolver.url_patterns

        endpoints = [str(pattern.pattern) for pattern in urlpatterns]

        grouped_endpoints: dict[str, list[str]] = {}

        for endpoint in endpoints:
            parts = endpoint.split("/")
            key = parts[0]
            if key not in grouped_endpoints:
                grouped_endpoints[key] = []
            grouped_endpoints[key].append(f"/{endpoint}")

        return JsonResponse({"versions": versions, "apis": grouped_endpoints}, status=200)
