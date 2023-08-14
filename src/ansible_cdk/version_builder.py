"""Build version text."""
import importlib.metadata


PKGS = [
    "ansible-cdk",
    "ansible-core",
    "ansible-builder",
    # "ansible-creator",
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
    for pkg in PKGS:
        version = importlib.metadata.version(pkg)
        lines.append(f"{pkg: <40} {version}")

    return "\n".join(lines)
