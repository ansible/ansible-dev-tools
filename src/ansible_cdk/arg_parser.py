"""Parse the command line arguments."""
import argparse
from .version_builder import version_builder


def parse():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        description=("The ansible content development kit.",),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=version_builder(),
        help="Print ansible-creator version and exit.",
    )

    args = parser.parse_args()

    return args
