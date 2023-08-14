"""Basic smoke tests."""

from ansible_cdk.version_builder import PKGS
import pytest
import subprocess
import sys


@pytest.mark.parametrize("package", PKGS)
def test_version(package: str) -> None:
    """Placeholder."""
    command = f"{sys.executable} -m ansible_cdk --version"
    proc = subprocess.run(
        args=command,
        shell=True,
        text=True,
        check=True,
        capture_output=True,
    )
    assert proc.returncode == 0
    assert package in proc.stdout
