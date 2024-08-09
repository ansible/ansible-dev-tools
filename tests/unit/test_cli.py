"""Test the cli module."""

from __future__ import annotations

import pytest

from ansible_dev_tools.cli import Cli


def test_cli_subcommand_missing() -> None:
    """Test the cli class with a missing subcommand.

    This is really only necessary until a second subcommand is added.

    Argparse should protect us from this.
    """
    cli = Cli()
    cli.args = {"subcommand": "missing"}
    with pytest.raises(ImportError):
        cli.run()
