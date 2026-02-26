"""Dynamic, schema-driven creator API endpoints."""

from __future__ import annotations

import json
import shutil

from typing import TYPE_CHECKING, Any

from ansible_creator.api import V1
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse

from ansible_dev_tools.resources.server.creator_v2 import create_tar_file
from ansible_dev_tools.server_utils import validate_request, validate_response


if TYPE_CHECKING:
    from pathlib import Path


class CreatorDynamic:
    """Dynamic creator endpoints driven by ansible-creator's V1 API.

    Provides discovery, schema inspection, and generic scaffolding
    without hardcoding individual project types.
    """

    def _response_from_tar(self, tar_file: Path) -> FileResponse:
        """Create a FileResponse from a tar file.

        Args:
            tar_file: The tar file path.

        Returns:
            The file response.
        """
        fs = FileSystemStorage(str(tar_file.parent))
        response = FileResponse(
            fs.open(tar_file.name, "rb"),
            content_type="application/tar",
            status=201,
        )
        response["Content-Disposition"] = f'attachment; filename="{tar_file.name}"'
        return response

    def capabilities(self, request: HttpRequest) -> JsonResponse | HttpResponse:
        """Return the full ansible-creator capability tree.

        Args:
            request: HttpRequest object.

        Returns:
            JSON response with the capability schema.
        """
        result = validate_request(request)
        if isinstance(result, HttpResponse):
            return result
        api = V1()
        return JsonResponse(api.schema(), status=200)

    def schema(self, request: HttpRequest) -> JsonResponse | HttpResponse:
        """Return the parameter schema for a specific command path.

        The command path is provided via repeated ``command_path`` query
        parameters, e.g. ``?command_path=init&command_path=collection``.

        Args:
            request: HttpRequest object.

        Returns:
            JSON response with the command schema, or 400 on error.
        """
        result = validate_request(request)
        if isinstance(result, HttpResponse):
            return result
        path_segments = request.GET.getlist("command_path")
        if not path_segments:  # pragma: no cover
            return HttpResponse(
                "Missing required query parameter: command_path",
                status=400,
            )
        try:
            api = V1()
            schema_result = api.schema_for(*path_segments)
        except KeyError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        return JsonResponse(schema_result, status=200)

    def scaffold(self, request: HttpRequest) -> FileResponse | HttpResponse:
        """Scaffold an ansible-creator project dynamically.

        Accepts a JSON body with ``command_path`` (list of strings) and
        optional ``params`` (dict). Delegates to ``V1().run()`` and returns
        the scaffolded content as a tar archive.

        On success, logs are included in ``X-Creator-Logs`` and
        ``X-Creator-Message`` response headers.

        On error, returns a JSON body with ``status``, ``message``,
        and ``logs``.

        Args:
            request: HttpRequest object.

        Returns:
            Tar file response on success, or JSON/HTTP error response.
        """
        result = validate_request(request)
        if isinstance(result, HttpResponse):
            return result

        body: dict[str, Any] = result.body  # type: ignore[assignment]
        command_path: list[str] = body.get("command_path", [])
        params: dict[str, Any] = body.get("params", {})

        if not command_path:  # pragma: no cover
            return JsonResponse(
                {"status": "error", "message": "Missing command_path", "logs": []},
                status=400,
            )

        api = V1()
        creator_result = api.run(*command_path, **params)

        if creator_result.status == "error":
            # Clean up the temp directory on error
            if creator_result.path:  # pragma: no cover
                shutil.rmtree(creator_result.path, ignore_errors=True)
            return JsonResponse(
                {
                    "status": "error",
                    "message": creator_result.message,
                    "logs": creator_result.logs,
                },
                status=400,
            )

        if creator_result.path is None:  # pragma: no cover
            return JsonResponse(
                {
                    "status": "error",
                    "message": "No output path",
                    "logs": creator_result.logs,
                },
                status=400,
            )

        try:
            tar_name = f"{'_'.join(command_path)}.tar"
            tar_file = creator_result.path.parent / tar_name
            create_tar_file(creator_result.path, tar_file)
            response = self._response_from_tar(tar_file)
            response["X-Creator-Logs"] = json.dumps(creator_result.logs)
            response["X-Creator-Message"] = creator_result.message
        finally:
            shutil.rmtree(creator_result.path, ignore_errors=True)

        return validate_response(
            request=request,
            response=response,
        )
