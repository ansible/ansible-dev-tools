"""Parse the command line arguments."""

from __future__ import annotations

import argparse

from .version_builder import version_builder


def parse() -> argparse.Namespace:
    """Parse the command line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="The ansible content development kit.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=version_builder(),
        help="Print the included tool versions and exit.",
    )

    subparsers = parser.add_subparsers(
        help="The subcommand to invoke.",
        title="Commands",
        dest="subcommand",
        required=True,
    )

    server_command_parser = subparsers.add_parser(
        "server",
        help="Start the Ansible Devtools server.",
        description=(
            "Starts the Ansible Devtools server on port 8000. Use --port to specify a custom port."
        ),
    )

    server_command_parser.add_argument(
        "--port",
        "-p",
        default="8000",
        help="Specify the port for the Ansible Devtools server.",
    )

    server_command_parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Run Ansible Devtools server with debug logging enabled.",
    )

    return parser.parse_args()
