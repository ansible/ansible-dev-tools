"""Build version text."""

from __future__ import annotations

import importlib.metadata


PKGS = [
    "ansible-builder",
    "ansible-core",
    "ansible-creator",
    "ansible-dev-environment",
    "ansible-dev-tools",
    "ansible-lint",
    "ansible-navigator",
    "ansible-sign",
    "molecule",
    "pytest-ansible",
    "tox-ansible",
]


def version_builder() -> str:
    """Build a string of formatted versions.

    Returns:
        The versions string
    """
    lines = []
    for pkg in sorted(PKGS):
        try:
            version = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            version = "not installed"
        lines.append(f"{pkg: <40} {version}")

    return "\n".join(lines)
