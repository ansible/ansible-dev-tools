"""A runpy entry point for ansible-dev-tools.

This makes it possible to invoke CLI
via :command:`python3 -m ansible_dev_tools`.
"""

from __future__ import annotations

from .cli import main


if __name__ == "__main__":
    main()
