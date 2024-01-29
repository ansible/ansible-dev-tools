#!python3
"""Script that tests rule markdown documentation."""
from __future__ import annotations

import re
import subprocess

from pathlib import Path


if __name__ == "__main__":
    result = subprocess.run(
        "adt --version",  # noqa: S607
        shell=True,  # noqa: S602
        check=True,
        capture_output=True,
        text=True,
    )

    file = Path("README.md")
    with file.open(encoding="utf-8", mode="r+") as fh:
        content = fh.read()
        content = re.sub(
            "<!-- START -->(.*?)<!-- END -->",
            f"<!-- START -->\n\n```\n$ adt --version\n{result.stdout}```\n\n<!-- END -->",
            content,
            flags=re.DOTALL,
        )
        fh.seek(0)
        fh.write(content)
        fh.truncate()
