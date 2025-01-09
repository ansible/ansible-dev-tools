"""Test suite for shell completion functionality.

This module provides pytest fixtures and tests to verify that ZSH shell
completions are active for various commands.
"""

from __future__ import annotations

import subprocess

from pathlib import Path
from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture(scope="module")
def zsh_path() -> Path:
    """Locate the ZSH executable.

    Returns:
        Path to ZSH executable.

    Raises:
        FileNotFoundError: If ZSH is not found in standard locations.
    """
    path = next(
        (Path(p) for p in ["/usr/bin/zsh", "/bin/zsh"] if Path(p).exists()),
        None,
    )
    if not path:
        msg = "ZSH not found in standard locations"
        raise FileNotFoundError(msg)
    return path


@pytest.fixture(scope="module")
def completion_checker(zsh_path: Path) -> Callable[[str], tuple[bool, str]]:
    """Provide a function to test ZSH completion status for commands.

    Args:
        zsh_path: Path to the ZSH executable.

    Returns:
        A callable that takes a command name and returns a tuple of
        (is_active: bool, details: str) indicating whether completions
        are active for that command.
    """

    def check(command: str) -> tuple[bool, str]:
        """Test if ZSH completions are active for a command.

        Args:
            command: The name of the command to check completions for.

        Returns:
            A tuple of (is_active, details) where is_active is a boolean
            indicating if completions are working, and details is a string
            containing the test output or error message.

        Raises:
            subprocess.TimeoutExpired: If the command times out.
            OSError: If an OS-level error occurs.
        """
        # Construct the test command
        test_command = (
            "source ~/.zshrc && "
            f"type _{command} &>/dev/null && "
            'echo "COMPLETIONS_ACTIVE=true" || '
            'echo "COMPLETIONS_ACTIVE=false"'
        )

        try:
            result = subprocess.run(  # noqa: S603
                [zsh_path, "-c", test_command],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,  # Prevent hanging
            )
            is_active = "COMPLETIONS_ACTIVE=true" in result.stdout
            return is_active, result.stdout.strip()

        except subprocess.TimeoutExpired:
            return False, "Command timed out after 5 seconds"
        except OSError as e:
            return False, f"OS error occurred: {e!s}"

    return check


class TestShellCompletions:
    """Test suite for shell completion functionality."""

    @pytest.mark.parametrize(
        "command",
        (
            "molecule_completion",
            # Add more commands here as needed
        ),
    )
    def test_command_completions(
        self,
        completion_checker: Callable[[str], tuple[bool, str]],
        command: str,
    ) -> None:
        """Verify that command completions are properly configured and active.

        Args:
            completion_checker: Fixture providing the completion testing function.
            command: The command to test completions for.
        """
        is_active, details = completion_checker(command)
        assert is_active, f"Completions for '{command}' are not active. Details:\n{details}"
