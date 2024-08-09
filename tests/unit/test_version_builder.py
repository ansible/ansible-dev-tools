"""Tests for the version builder."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from ansible_dev_tools.version_builder import PKGS, version_builder


if TYPE_CHECKING:
    import pytest


def test_version_builder_success() -> None:
    """Test the version builder."""
    versions = version_builder()
    assert all(p in versions for p in PKGS)


def test_version_builder_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the version builder."""
    monkeypatch.setattr("ansible_dev_tools.version_builder.PKGS", ["__invalid__"])

    versions = version_builder()

    assert re.search(r"__invalid__\s+not installed", versions)
