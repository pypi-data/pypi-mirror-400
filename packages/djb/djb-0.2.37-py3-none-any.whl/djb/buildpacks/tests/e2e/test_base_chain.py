"""E2E tests for BuildpackChain.build() with dynamic version resolution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from djb.buildpacks.base import BuildpackChain
from djb.buildpacks.constants import BuildpackError

pytestmark = pytest.mark.e2e_marker


class ConcreteBuildpackChain(BuildpackChain):
    """Concrete implementation for testing the ABC."""

    def __init__(
        self,
        registry: str,
        pyproject_path: Path | None = None,
        image_exists_result: bool = False,
    ) -> None:
        super().__init__(registry, pyproject_path)
        self._image_exists_result = image_exists_result

    def image_exists(self, image_tag: str) -> bool:
        return self._image_exists_result

    def _build_image(
        self,
        dockerfile_path: Path,
        cured_image_tag: str,
        composite_image: str | None,
        laminate_image: str | None = None,
        buildpack_version: str | None = None,
    ) -> str:
        return cured_image_tag


class TestBuildpackChainBuildDynamicVersion:
    """Tests for BuildpackChain.build() with dynamic version resolution."""

    def test_build_resolves_dynamic_version(
        self, make_pyproject_with_gdal: Path, make_buildpack_dockerfiles: Path
    ) -> None:
        """build() resolves version for dynamic buildpacks."""
        chain = ConcreteBuildpackChain(
            registry="localhost:32000",
            pyproject_path=make_pyproject_with_gdal,
            image_exists_result=False,
        )

        with patch("djb.buildpacks.specs.DOCKERFILES_DIR", make_buildpack_dockerfiles):
            result = chain.build(["python:3.14-slim", "gdal-slim-dynamic-v1"])

        # Should include resolved version in name
        assert "gdal3.10.0" in result

    def test_build_without_pyproject_raises_for_dynamic(
        self, make_buildpack_dockerfiles: Path
    ) -> None:
        """build() raises when dynamic buildpack used without pyproject_path."""
        chain = ConcreteBuildpackChain(
            registry="localhost:32000",
            pyproject_path=None,
            image_exists_result=False,
        )

        with patch("djb.buildpacks.specs.DOCKERFILES_DIR", make_buildpack_dockerfiles):
            with pytest.raises(BuildpackError, match="requires pyproject_path"):
                chain.build(["python:3.14-slim", "gdal-slim-dynamic-v1"])
