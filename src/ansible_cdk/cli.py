"""CLI entrypoint."""
from argparse import Namespace

from .arg_parser import parse


class Cli:
    """The Cli class."""

    def __init__(self) -> None:
        """Initialize the CLI and parse CLI args."""
        self.args: Namespace

    def parse_args(self) -> None:
        """Parse the command line arguments."""
        self.args = parse()

    def run(self) -> None:
        """Run the cdk application."""
        print("Hi")


def main() -> None:
    """Entry point for ansible-creator CLI."""
    cli = Cli()
    cli.parse_args()
    cli.run()


if __name__ == "__main__":
    main()
