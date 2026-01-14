"""E2E tests for buildpack version resolvers.

Tests that require reading pyproject.toml from disk.
"""

from collections.abc import Callable
from pathlib import Path

import pytest

from djb.buildpacks.metadata import resolve_version
from djb.buildpacks.resolvers import resolve_gdal_version


class TestResolveVersion:
    """Tests for resolve_version()."""

    def test_resolves_gdal(self, make_pyproject_with_gdal: Path) -> None:
        """resolve_version() resolves GDAL version from pyproject.toml."""
        version = resolve_version("gdal-slim-dynamic-v1", make_pyproject_with_gdal)
        assert version == "3.10.0"

    def test_unregistered_spec_raises(self, make_pyproject_with_gdal: Path) -> None:
        """resolve_version() raises KeyError for unregistered specs."""
        with pytest.raises(KeyError):
            resolve_version("unknown-dynamic-v1", make_pyproject_with_gdal)


class TestResolveGdalVersion:
    """Tests for resolve_gdal_version() with real pyproject.toml."""

    def test_exact_version(self, make_pyproject_with_gdal: Path) -> None:
        """resolve_gdal_version() extracts exact GDAL version."""
        version = resolve_gdal_version(make_pyproject_with_gdal)
        assert version == "3.10.0"

    def test_version_range(self, make_pyproject_with_gdal_range: Path) -> None:
        """resolve_gdal_version() extracts minimum from range."""
        version = resolve_gdal_version(make_pyproject_with_gdal_range)
        assert version == "3.9.0"

    def test_missing_gdal_raises(self, make_pyproject: Callable[..., Path]) -> None:
        """resolve_gdal_version() raises when gdal not in dependencies."""
        pyproject = make_pyproject()
        with pytest.raises(ValueError, match="gdal dependency not found"):
            resolve_gdal_version(pyproject)
