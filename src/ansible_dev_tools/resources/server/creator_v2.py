"""The creator frontend and backend APIs."""

from __future__ import annotations

import tarfile
import tempfile

from pathlib import Path

from ansible_creator._version import version as creator_version
from ansible_creator.config import Config
from ansible_creator.output import Output
from ansible_creator.subcommands.init import Init
from ansible_creator.subcommands.add import Add
from ansible_creator.utils import TermFeatures
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpRequest, HttpResponse

from ansible_dev_tools.server_utils import validate_request, validate_response


def create_tar_file(init_path: Path, tar_file: Path) -> None:
    """Create a tar file from the given directory.

    Args:
        init_path: The directory path to create the tar file from.
        tar_file: The output tar file path.
    """
    with tarfile.open(tar_file, "w") as tar:
        tar.add(str(init_path), arcname=".")


class CreatorFrontendV2:
    """The creator frontend, handles requests from users."""

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

    def playbook(
        self,
        request: HttpRequest,
    ) -> FileResponse | HttpResponse:
        """Create a new playbook project.

        Args:
            request: HttpRequest object.

        Returns:
            File or error response.
        """
        result = validate_request(request)
        if isinstance(result, HttpResponse):
            return result
        with tempfile.TemporaryDirectory() as tmp_dir:
            # result.body here is a dict, it appear the type hint is wrong
            tar_file = CreatorBackend(Path(tmp_dir)).playbook(
                **result.body,  # type: ignore[arg-type]
            )
            response = self._response_from_tar(tar_file)

        return validate_response(
            request=request,
            response=response,
        )

    def collection(
        self,
        request: HttpRequest,
    ) -> FileResponse | HttpResponse:
        """Create a new collection project.

        Args:
            request: HttpRequest object.

        Returns:
            File or error response.
        """
        result = validate_request(request)
        if isinstance(result, HttpResponse):
            return result
        with tempfile.TemporaryDirectory() as tmp_dir:
            # result.body here is a dict, it appear the type hint is wrong
            tar_file = CreatorBackend(Path(tmp_dir)).collection(
                **result.body,  # type: ignore[arg-type]
            )
            response = self._response_from_tar(tar_file)

        return validate_response(
            request=request,
            response=response,
        )
   
    def devfile(
        self,
        request: HttpRequest,
    ) -> FileResponse | HttpResponse:
        """Add a devfile.

        Args:
            request: HttpRequest object.

        Returns:
            File or error response.
        """
        result = validate_request(request)
        if isinstance(result, HttpResponse):
            return result
        with tempfile.TemporaryDirectory() as tmp_dir:
            tar_file = CreatorBackend(Path(tmp_dir)).devfile(
                **result.body,  # type: ignore[arg-type]
            )
            response = self._response_from_tar(tar_file)

        return validate_response(
            request=request,
            response=response,
        )




class CreatorOutput(Output):
    """The creator output."""

    def __init__(self, log_file: str) -> None:
        """Initialize the creator output.

        Convenience class to consistently define output with a changing temporary directory.

        Args:
            log_file: The log file path.
        """
        super().__init__(
            log_file=log_file,
            log_level="DEBUG",
            log_append="false",
            term_features=TermFeatures(color=False, links=False),
            verbosity=1,
        )


class CreatorBackend:
    """The creator wrapper, handles interaction with the python creator project."""

    def __init__(self, tmp_dir: Path) -> None:
        """Initialize the creator.

        Args:
            tmp_dir: The temporary directory.
        """
        self.tmp_dir = tmp_dir

    def collection(self, collection: str, project: str) -> Path:
        """Scaffold a collection.

        Args:
            collection: The collection name.
            project: The project type.

        Returns:
            The tar file path.
        """
        init_path = self.tmp_dir / collection
        config = Config(
            creator_version=creator_version,
            init_path=str(init_path),
            output=CreatorOutput(log_file=str(self.tmp_dir / "creator.log")),
            collection=collection,
            subcommand="init",
            project=project,
        )
        Init(config).run()
        tar_file = self.tmp_dir / f"{collection}.tar"
        create_tar_file(init_path, tar_file)
        return tar_file

    def playbook(
        self,
        project: str,
        namespace: str,
        collection_name: str,
    ) -> Path:
        """Scaffold a playbook project.

        Args:
            project: The project type.
            namespace: The collection namespace.
            collection_name: The collection name.

        Returns:
            The tar file path.
        """
        init_path = self.tmp_dir / f"{namespace}-{collection_name}"
        config = Config(
            creator_version=creator_version,
            init_path=str(init_path),
            output=CreatorOutput(log_file=str(self.tmp_dir / "creator.log")),
            project=project,
            namespace=namespace,
            collection_name=collection_name,
            subcommand="init",
        )
        Init(config).run()
        tar_file = self.tmp_dir / f"{namespace}-{collection_name}.tar"
        create_tar_file(init_path, tar_file)
        return tar_file


    def devfile(self, project: str, collection: str) -> Path:
        """Scaffold a devfile.

        Args:
            project: The project type.
            devfile_name: The name of the devfile.
            config_params: Configuration parameters for devfile creation.

        Returns:
            The tar file path.
        """
        # Path where the devfile will be added in the collection
        add_path= self.tmp_dir / collection

        config = Config(
            resource_type="devfile",
            project=project,
            creator_version=creator_version,
            add_path=str(add_path),
            output=CreatorOutput(log_file=str(self.tmp_dir / "creator.log")),
            collection=collection,
            subcommand="add",
        )
        Add(config).run()
        tar_file = self.tmp_dir / "devfile.tar"
        create_tar_file(add_path, tar_file)
        return tar_file
