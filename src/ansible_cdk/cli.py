"""CLI entrypoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .arg_parser import parse


if TYPE_CHECKING:
    from argparse import Namespace


class Cli:
    """The Cli class."""

    def __init__(self: Cli) -> None:
        """Initialize the CLI and parse CLI args."""
        self.args: Namespace

    def parse_args(self: Cli) -> None:
        """Parse the command line arguments."""
        self.args = parse()


def main() -> None:
    """Entry point for ansible-creator CLI."""
    cli = Cli()
    cli.parse_args()


if __name__ == "__main__":
    main()
