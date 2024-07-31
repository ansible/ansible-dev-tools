"""Django server for the Ansible Devtools API."""

from __future__ import annotations

import os

from typing import TYPE_CHECKING

from django import setup
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.urls import path
from gunicorn.app.base import BaseApplication

from ansible_dev_tools.resources.server.creator import CreatorFrontendV1


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIHandler


urlpatterns = (
    path(route="v1/creator/playbook", view=CreatorFrontendV1().playbook),
    path(route="v1/creator/collection", view=CreatorFrontendV1().collection),
)


class AdtServerApp(BaseApplication):  # type: ignore[misc]
    """Custom application to integrate Gunicorn with the django WSGI app."""

    # pylint: disable=abstract-method
    def __init__(self: AdtServerApp, app: WSGIHandler, options: dict[str, str]) -> None:
        """Initialize the application.

        Args:
            app: The application to run with gunicorn.
            options: Configuration options for gunicorn.
        """
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self: AdtServerApp) -> None:
        """Load configuration for gunicorn."""
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self: AdtServerApp) -> WSGIHandler:
        """Load application.

        Returns:
            The application to run with gunicorn.
        """
        return self.application


class Server:
    """Ansible Devtools server implementation."""

    def __init__(self: Server, port: str, debug: bool) -> None:  # noqa: FBT001
        """Initialize an AdtServer object.

        Args:
            port: The port on which the server would run.
            debug: Enable or disable debug logging.
        """
        self.port: str = port
        self.debug: bool = debug

        settings.configure(
            SECRET_KEY=os.environ.get("SECRET_KEY", os.urandom(32)),
            ALLOWED_HOSTS=[
                "*",
            ],
            ROOT_URLCONF=__name__,
            MIDDLEWARE_CLASSES=(
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
            ),
        )
        setup()
        self.application = get_wsgi_application()

    def run(self: Server) -> None:
        """Start the server."""
        options = {"bind": f"0.0.0.0:{self.port}"}
        if self.debug:
            # set log level to debug and write access logs to stdout
            options.update({"loglevel": "debug", "accesslog": "-"})

        AdtServerApp(app=self.application, options=options).run()
