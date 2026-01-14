"""Unit tests for buildpack version resolvers.

Note: Tests requiring file I/O are in e2e/test_resolvers.py
"""

from __future__ import annotations

import pytest
from packaging.specifiers import SpecifierSet

from djb.buildpacks.metadata import has_version_resolver
from djb.buildpacks.resolvers import min_version_from_specifier


class TestMinVersionFromSpecifier:
    """Tests for min_version_from_specifier()."""

    def test_exact_version(self) -> None:
        """min_version_from_specifier() extracts exact version from ==."""
        specifier = SpecifierSet("==3.10.0")
        assert min_version_from_specifier(specifier) == "3.10.0"

    def test_minimum_version(self) -> None:
        """min_version_from_specifier() extracts minimum from >=."""
        specifier = SpecifierSet(">=3.9.0")
        assert min_version_from_specifier(specifier) == "3.9.0"

    def test_compatible_release(self) -> None:
        """min_version_from_specifier() extracts version from ~=."""
        specifier = SpecifierSet("~=3.10")
        assert min_version_from_specifier(specifier) == "3.10"

    def test_range_uses_minimum(self) -> None:
        """min_version_from_specifier() uses minimum bound from range."""
        specifier = SpecifierSet(">=3.9.0,<4.0")
        assert min_version_from_specifier(specifier) == "3.9.0"

    def test_complex_specifier(self) -> None:
        """min_version_from_specifier() handles complex specifiers."""
        specifier = SpecifierSet(">=3.10.0,<4.0,!=3.10.1")
        assert min_version_from_specifier(specifier) == "3.10.0"

    def test_empty_specifier_raises(self) -> None:
        """min_version_from_specifier() raises for empty specifier."""
        specifier = SpecifierSet("")
        with pytest.raises(ValueError, match="Could not extract version"):
            min_version_from_specifier(specifier)


class TestHasVersionResolver:
    """Tests for has_version_resolver()."""

    def test_registered_spec(self) -> None:
        """has_version_resolver() returns True for registered specs."""
        assert has_version_resolver("gdal-slim-dynamic-v1") is True

    def test_unregistered_spec(self) -> None:
        """has_version_resolver() returns False for unregistered specs."""
        assert has_version_resolver("unknown-dynamic-v1") is False

    def test_public_image(self) -> None:
        """has_version_resolver() returns False for public images."""
        assert has_version_resolver("python:3.14-slim") is False

    def test_static_buildpack(self) -> None:
        """has_version_resolver() returns False for static buildpacks."""
        assert has_version_resolver("test-buildpack-v1") is False
