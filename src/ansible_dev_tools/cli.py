"""CLI entrypoint."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from ansible_dev_tools.arg_parser import parse


if TYPE_CHECKING:
    from typing import Any


class Cli:
    """The Cli class."""

    def __init__(self: Cli) -> None:
        """Initialize the CLI and parse CLI args."""
        self.args: dict[str, Any]

    def parse_args(self: Cli) -> None:
        """Parse the command line arguments."""
        self.args = vars(parse())

    def run(self: Cli) -> None:
        """Dispatch work to correct subcommand class."""
        subcommand = self.args.pop("subcommand")
        subcommand_module = f"ansible_dev_tools.subcommands.{subcommand}"
        subcommand_cls = f"{subcommand}".capitalize()
        # TO-DO: wrap this with a try-except
        subcommand = getattr(import_module(subcommand_module), subcommand_cls)
        subcommand(**self.args).run()


def main() -> None:
    """Entry point for ansible-creator CLI."""
    cli = Cli()
    cli.parse_args()
    cli.run()


if __name__ == "__main__":
    main()
