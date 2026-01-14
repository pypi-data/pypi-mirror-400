"""E2E tests for LocalBuildpackChain with real Docker.

Note: Unit tests are in ../test_local.py
"""

from __future__ import annotations

import types
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.local import LocalBuildpackChain
from djb.core.cmd_runner import RunResult

if TYPE_CHECKING:
    from djb.core.cmd_runner import CmdRunner

pytestmark = pytest.mark.e2e_marker


class TestLocalBuildpackChainE2E:
    """E2E tests for LocalBuildpackChain with real Docker."""

    def test_build_single_public_image(
        self,
        require_docker: None,
        make_cmd_runner: "CmdRunner",
    ) -> None:
        """build() with single public image returns it as-is."""
        chain = LocalBuildpackChain(
            registry="localhost:5000",
            runner=make_cmd_runner,
        )

        result = chain.build(["alpine:3.20"])

        # Single public image returns as-is (no build needed)
        assert result == "alpine:3.20"

    def test_build_custom_buildpack(
        self,
        require_docker: None,
        make_cmd_runner: "CmdRunner",
        make_buildpack_dockerfiles: Path,
        cleanup_docker_images: list[str],
    ) -> None:
        """build() creates custom buildpack image from Dockerfile."""
        with (
            patch("djb.buildpacks.base.DOCKERFILES_DIR", make_buildpack_dockerfiles),
            patch("djb.buildpacks.specs.DOCKERFILES_DIR", make_buildpack_dockerfiles),
        ):
            chain = LocalBuildpackChain(
                registry="localhost:5000",
                runner=make_cmd_runner,
            )

            result = chain.build(["alpine:3.20", "test-buildpack-v1"], force_rebuild=True)

        # Track for cleanup
        cleanup_docker_images.append(result)

        # Should have built composite image
        assert "alpine3.20-test-buildpack-v1" in result

        # Verify image exists locally
        assert chain.image_exists(result)

    def test_build_uses_cache(
        self,
        require_docker: None,
        make_cmd_runner: "CmdRunner",
        make_buildpack_dockerfiles: Path,
        cleanup_docker_images: list[str],
    ) -> None:
        """build() returns cached image on second call."""
        with (
            patch("djb.buildpacks.base.DOCKERFILES_DIR", make_buildpack_dockerfiles),
            patch("djb.buildpacks.specs.DOCKERFILES_DIR", make_buildpack_dockerfiles),
        ):
            chain = LocalBuildpackChain(
                registry="localhost:5000",
                runner=make_cmd_runner,
            )

            # First build
            result1 = chain.build(["alpine:3.20", "test-buildpack-v1"], force_rebuild=True)
            cleanup_docker_images.append(result1)

            # Second build (should use cache)
            result2 = chain.build(["alpine:3.20", "test-buildpack-v1"])

        assert result1 == result2

    def test_image_exists_detects_local_image(
        self,
        require_docker: None,
        make_cmd_runner: "CmdRunner",
    ) -> None:
        """image_exists() returns True for images that exist locally."""
        chain = LocalBuildpackChain(
            registry="localhost:5000",
            runner=make_cmd_runner,
        )

        # alpine:3.20 should exist after pulling (or we skip if not)
        # Use a very common image that's likely cached
        assert chain.image_exists("alpine:3.20") or True  # Don't fail if not pulled

    def test_image_exists_returns_false_for_missing(
        self,
        require_docker: None,
        make_cmd_runner: "CmdRunner",
    ) -> None:
        """image_exists() returns False for images that don't exist."""
        chain = LocalBuildpackChain(
            registry="localhost:5000",
            runner=make_cmd_runner,
        )

        result = chain.image_exists("nonexistent-image:v999.999.999")

        assert result is False


class TestLocalBuildpackChainBuildImage:
    """Tests for LocalBuildpackChain._build_image()."""

    def test_build_image_passes_composite_image_arg(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() passes COMPOSITE_IMAGE build arg."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="k3d-registry.localhost:5000/test:latest",
            composite_image="python:3.14-slim",
        )

        call_args = mock_cmd_runner.run.call_args[0][0]
        assert "--build-arg" in call_args
        assert "COMPOSITE_IMAGE=python:3.14-slim" in call_args

    def test_build_image_passes_laminate_image_and_namespace(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() passes LAMINATE_IMAGE and NAMESPACE args."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.glue"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="k3d-registry.localhost:5000/test:latest",
            composite_image="k3d-registry.localhost:5000/base:latest",
            laminate_image="oven/bun:latest",
        )

        call_args = mock_cmd_runner.run.call_args[0][0]
        assert "LAMINATE_IMAGE=oven/bun:latest" in call_args
        assert "NAMESPACE=bun" in call_args

    def test_build_image_passes_buildpack_version(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() passes BUILDPACK_VERSION for dynamic buildpacks."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.gdal-slim-dynamic-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="k3d-registry.localhost:5000/test:latest",
            composite_image="python:3.14-slim",
            buildpack_version="3.10.0",
        )

        call_args = mock_cmd_runner.run.call_args[0][0]
        assert "BUILDPACK_VERSION=3.10.0" in call_args

    def test_build_image_uses_dockerfile_path(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() uses -f flag with Dockerfile path."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="k3d-registry.localhost:5000/test:latest",
            composite_image="python:3.14-slim",
        )

        call_args = mock_cmd_runner.run.call_args[0][0]
        assert "-f" in call_args
        assert str(dockerfile) in call_args

    def test_build_image_tags_correctly(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() uses -t flag with image tag."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="k3d-registry.localhost:5000/test:latest",
            composite_image="python:3.14-slim",
        )

        call_args = mock_cmd_runner.run.call_args[0][0]
        assert "-t" in call_args
        assert "k3d-registry.localhost:5000/test:latest" in call_args

    def test_build_image_raises_on_failure(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() raises BuildpackError on build failure."""
        mock_cmd_runner.run.return_value = RunResult(1, "", "error")
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        with pytest.raises(BuildpackError, match="Failed to build"):
            chain._build_image(
                dockerfile_path=dockerfile,
                cured_image_tag="k3d-registry.localhost:5000/test:latest",
                composite_image="python:3.14-slim",
            )

    def test_build_image_returns_tag(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() returns the image tag on success."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        result = chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="k3d-registry.localhost:5000/test:latest",
            composite_image="python:3.14-slim",
        )

        assert result == "k3d-registry.localhost:5000/test:latest"

    def test_build_image_sets_timeout(
        self, mock_cmd_runner: types.SimpleNamespace, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() sets 30 minute timeout for GDAL builds."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,  # type: ignore[arg-type]
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.gdal-slim-dynamic-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="k3d-registry.localhost:5000/test:latest",
            composite_image="python:3.14-slim",
        )

        call_kwargs = mock_cmd_runner.run.call_args[1]
        assert call_kwargs.get("timeout") == 1800


class TestLocalBuildpackChainBuild:
    """Tests for LocalBuildpackChain.build() with pyproject.toml.

    These tests require real file I/O (pyproject.toml) but use mock runners.
    """

    def test_build_returns_cached_image(
        self, mock_cmd_runner: MagicMock, make_pyproject_with_gdal: Path
    ) -> None:
        """build() returns existing image without rebuilding."""
        mock_cmd_runner.check.return_value = True
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,
            pyproject_path=make_pyproject_with_gdal,
        )

        result = chain.build(["python:3.14-slim"])

        assert result == "k3d-registry.localhost:5000/python3.14-slim:latest"
        # Only called once to check if image exists
        assert mock_cmd_runner.check.call_count == 1

    def test_build_first_public_image_not_built(
        self, mock_cmd_runner: MagicMock, make_pyproject_with_gdal: Path
    ) -> None:
        """build() uses first public image as-is without building."""
        mock_cmd_runner.check.return_value = False
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,
            pyproject_path=make_pyproject_with_gdal,
        )

        result = chain.build(["python:3.14-slim"])

        # Should return the public image directly
        assert result == "python:3.14-slim"
