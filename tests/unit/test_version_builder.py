"""Tests for the version builder."""

import re

import pytest

from ansible_dev_tools.version_builder import PKGS, version_builder


def test_version_builder_success() -> None:
    """Test the version builder."""
    versions = version_builder()
    assert all(p in versions for p in PKGS)


def test_version_builder_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the version builder."""
    monkeypatch.setattr("ansible_dev_tools.version_builder.PKGS", ["__invalid__"])

    versions = version_builder()

    assert re.search(r"__invalid__\s+not installed", versions)
