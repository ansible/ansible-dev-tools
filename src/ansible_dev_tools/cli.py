"""CLI entrypoint."""

from __future__ import annotations

import sys

from importlib import import_module
from typing import TYPE_CHECKING

from ansible_dev_tools.arg_parser import parse
from ansible_dev_tools.utils import Colors


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

    def _run_subcommand(self: Cli, subcommand: str) -> None:
        """Run the subcommand.

        Args:
            subcommand: The subcommand to run.
        """
        subcommand_module = f"ansible_dev_tools.subcommands.{subcommand}"
        subcommand_cls_name = f"{subcommand}".capitalize()
        subcommand_cls = getattr(import_module(subcommand_module), subcommand_cls_name)
        subcommand_cls(**self.args).run()

    def run(self: Cli) -> None:
        """Dispatch work to correct subcommand class."""
        subcommand = self.args.pop("subcommand")
        if subcommand == "server":
            try:
                self._run_subcommand(subcommand)
            except ImportError as exc:
                print(f"{Colors.RED}{exc}{Colors.END}", file=sys.stderr)  # noqa: T201
                err = (
                    "Error: Missing server dependencies. Please install the server dependencies."
                    " `pip install ansible-dev-tools[server]`"
                )
                print(f"{Colors.RED}{err}{Colors.END}", file=sys.stderr)  # noqa: T201
                sys.exit(1)
        else:
            self._run_subcommand(subcommand)


def main() -> None:
    """Entry point for ansible-creator CLI."""
    cli = Cli()
    cli.parse_args()
    cli.run()


if __name__ == "__main__":
    main()
