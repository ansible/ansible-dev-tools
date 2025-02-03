"""Test suite for shell completion functionality.

This module provides pytest fixtures and tests to verify that ZSH shell
completions are active for various commands.
"""

from __future__ import annotations

import shutil
import subprocess

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture(scope="module")
def completion_checker() -> Callable[[str], tuple[bool, str]]:
    """Provide a function to test ZSH completion status for commands.

    Returns:
        A tuple of (is_active, details) indicating whether completions
        are active for that command.
    """

    def check(command: str) -> tuple[bool, str]:
        """Check if ZSH completions are active for a given command.

        Args:
            command: The command to test completions for.

        Returns:
            A tuple of (is_active, details) indicating whether completions
            are active for that command.

        Raises:
            FileNotFoundError: If ZSH is not found in the system's PATH.
        """
        zsh_path = shutil.which("zsh")
        if zsh_path is None:
            msg = "ZSH not found in $PATH"
            raise FileNotFoundError(msg)

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
        command: str,
        completion_checker: Callable[[str], tuple[bool, str]],  # pylint: disable=redefined-outer-name
    ) -> None:
        """Verify that command completions are properly configured and active.

        Args:
            command: The command to test completions for.
            completion_checker: Fixture that checks completion status

        """
        is_active, details = completion_checker(command)
        assert is_active, f"Completions for '{command}' are not active. Details:\n{details}"
