"""Tests for BuildpackChain base class."""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.buildpacks.base import BuildpackChain
from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.metadata import (
    DEFAULT_CUSTOM_BUILD_TIMEOUT_SECONDS,
    PUBLIC_IMAGE_BUILD_TIMEOUT_SECONDS,
    get_build_timeout,
)

# Note: TestBuildpackChainBuildDynamicVersion moved to e2e/test_base_chain.py


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


class TestBuildpackSpecFromDockerfile:
    """Tests for BuildpackChain._buildpack_spec_from_dockerfile()."""

    def test_returns_none_for_glue_dockerfile(self) -> None:
        """_buildpack_spec_from_dockerfile() returns None for Dockerfile.glue."""
        result = BuildpackChain._buildpack_spec_from_dockerfile(Path("/path/to/Dockerfile.glue"))
        assert result is None

    def test_extracts_spec_from_dockerfile_name(self) -> None:
        """_buildpack_spec_from_dockerfile() extracts spec from Dockerfile.{spec}."""
        result = BuildpackChain._buildpack_spec_from_dockerfile(
            Path("/path/to/Dockerfile.gdal-slim-dynamic-v1")
        )
        assert result == "gdal-slim-dynamic-v1"

    def test_extracts_spec_with_dots(self) -> None:
        """_buildpack_spec_from_dockerfile() handles specs with dots in name."""
        result = BuildpackChain._buildpack_spec_from_dockerfile(
            Path("/path/to/Dockerfile.some-pack-1.0-v1")
        )
        assert result == "some-pack-1.0-v1"

    def test_returns_none_for_plain_dockerfile(self) -> None:
        """_buildpack_spec_from_dockerfile() returns None for plain Dockerfile."""
        result = BuildpackChain._buildpack_spec_from_dockerfile(Path("/path/to/Dockerfile"))
        assert result is None

    def test_returns_none_for_other_files(self) -> None:
        """_buildpack_spec_from_dockerfile() returns None for non-Dockerfile files."""
        result = BuildpackChain._buildpack_spec_from_dockerfile(Path("/path/to/requirements.txt"))
        assert result is None


class TestEstimateBuildTimeout:
    """Tests for BuildpackChain._estimate_build_timeout_seconds()."""

    def test_glue_image_uses_public_timeout(self) -> None:
        """_estimate_build_timeout_seconds() returns PUBLIC timeout for glue builds."""
        chain = ConcreteBuildpackChain(registry="localhost:32000")
        dockerfile = Path("/path/to/Dockerfile.glue")

        timeout = chain._estimate_build_timeout_seconds(dockerfile, glue_image="oven/bun:latest")

        assert timeout == PUBLIC_IMAGE_BUILD_TIMEOUT_SECONDS

    def test_gdal_uses_registered_timeout(self) -> None:
        """_estimate_build_timeout_seconds() returns registered timeout for known specs."""
        chain = ConcreteBuildpackChain(registry="localhost:32000")
        dockerfile = Path("/path/to/Dockerfile.gdal-slim-dynamic-v1")

        timeout = chain._estimate_build_timeout_seconds(dockerfile, glue_image=None)

        # Should match the timeout from metadata registry
        assert timeout == get_build_timeout("gdal-slim-dynamic-v1")
        assert timeout == 1800  # 30 minutes for GDAL

    def test_unknown_uses_default_timeout(self) -> None:
        """_estimate_build_timeout_seconds() returns DEFAULT timeout for unknown specs."""
        chain = ConcreteBuildpackChain(registry="localhost:32000")
        dockerfile = Path("/path/to/Dockerfile.unknown-buildpack-v1")

        timeout = chain._estimate_build_timeout_seconds(dockerfile, glue_image=None)

        assert timeout == DEFAULT_CUSTOM_BUILD_TIMEOUT_SECONDS

    def test_plain_dockerfile_uses_default(self) -> None:
        """_estimate_build_timeout_seconds() returns DEFAULT for plain Dockerfile."""
        chain = ConcreteBuildpackChain(registry="localhost:32000")
        dockerfile = Path("/path/to/Dockerfile")

        timeout = chain._estimate_build_timeout_seconds(dockerfile, glue_image=None)

        assert timeout == DEFAULT_CUSTOM_BUILD_TIMEOUT_SECONDS


class TestBuildpackChainBuild:
    """Tests for BuildpackChain.build() method."""

    def test_build_empty_buildpacks_raises(self) -> None:
        """build() raises BuildpackError for empty buildpack list."""
        chain = ConcreteBuildpackChain(registry="localhost:32000")

        with pytest.raises(BuildpackError, match="No buildpacks specified"):
            chain.build([])

    def test_build_returns_cached_when_exists(self) -> None:
        """build() returns existing image without rebuilding."""
        chain = ConcreteBuildpackChain(
            registry="localhost:32000",
            image_exists_result=True,
        )

        result = chain.build(["python:3.14-slim"])

        assert result == "localhost:32000/python3.14-slim:latest"

    def test_build_single_public_returns_raw(self) -> None:
        """build() returns public image as-is when it's first in chain."""
        chain = ConcreteBuildpackChain(
            registry="localhost:32000",
            image_exists_result=False,
        )

        result = chain.build(["python:3.14-slim"])

        # Single public image returns as-is (no build needed)
        assert result == "python:3.14-slim"
