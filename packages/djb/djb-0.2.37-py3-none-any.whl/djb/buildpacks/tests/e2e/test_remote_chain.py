"""E2E tests for RemoteBuildpackChain.

Note: Unit tests are in ../test_remote.py
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.remote import RemoteBuildpackChain

pytestmark = pytest.mark.e2e_marker


class TestRemoteBuildpackChainBuildImage:
    """Tests for RemoteBuildpackChain._build_image()."""

    def test_build_image_creates_remote_dir(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() creates remote build directory."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="localhost:32000/test:latest",
            composite_image="python:3.14-slim",
        )

        # First call should create directory
        first_call = mock_ssh.run.call_args_list[0]
        assert "mkdir -p" in first_call[0][0]

    def test_build_image_passes_composite_image_arg(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() passes COMPOSITE_IMAGE build arg."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="localhost:32000/test:latest",
            composite_image="python:3.14-slim",
        )

        # Find the build command
        build_call = next(c for c in mock_ssh.run.call_args_list if "docker build" in str(c))
        assert "--build-arg COMPOSITE_IMAGE=python:3.14-slim" in build_call[0][0]

    def test_build_image_passes_laminate_image_and_namespace(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() passes LAMINATE_IMAGE and NAMESPACE args."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.glue"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="localhost:32000/test:latest",
            composite_image="localhost:32000/base:latest",
            laminate_image="oven/bun:latest",
        )

        # Find the build command
        build_call = next(c for c in mock_ssh.run.call_args_list if "docker build" in str(c))
        cmd = build_call[0][0]
        assert "--build-arg LAMINATE_IMAGE=oven/bun:latest" in cmd
        assert "--build-arg NAMESPACE=bun" in cmd

    def test_build_image_passes_buildpack_version(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() passes BUILDPACK_VERSION for dynamic buildpacks."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.gdal-slim-dynamic-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="localhost:32000/test:latest",
            composite_image="python:3.14-slim",
            buildpack_version="3.10.0",
        )

        # Find the build command
        build_call = next(c for c in mock_ssh.run.call_args_list if "docker build" in str(c))
        assert "--build-arg BUILDPACK_VERSION=3.10.0" in build_call[0][0]

    def test_build_image_imports_to_containerd(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() imports built image to containerd."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="localhost:32000/test:latest",
            composite_image="python:3.14-slim",
        )

        # Find the import command
        import_call = next(c for c in mock_ssh.run.call_args_list if "ctr image import" in str(c))
        assert "docker save" in import_call[0][0]
        assert "microk8s ctr image import" in import_call[0][0]

    def test_build_image_pushes_to_registry(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() pushes image to registry."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="localhost:32000/test:latest",
            composite_image="python:3.14-slim",
        )

        # Find the push command
        push_call = next(c for c in mock_ssh.run.call_args_list if "ctr image push" in str(c))
        assert "--plain-http" in push_call[0][0]
        assert "localhost:32000/test:latest" in push_call[0][0]

    def test_build_image_raises_on_build_failure(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() raises BuildpackError on build failure."""

        def run_side_effect(cmd: str, **kwargs: object) -> tuple[int, str, str]:
            if "docker build" in cmd:
                return (1, "", "Build failed: out of memory")
            return (0, "", "")

        mock_ssh.run.side_effect = run_side_effect
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        with pytest.raises(BuildpackError, match="Failed to build"):
            chain._build_image(
                dockerfile_path=dockerfile,
                cured_image_tag="localhost:32000/test:latest",
                composite_image="python:3.14-slim",
            )

    def test_build_image_cleans_up(
        self, mock_ssh: MagicMock, make_buildpack_dockerfiles: Path
    ) -> None:
        """_build_image() cleans up remote build directory."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        dockerfile = make_buildpack_dockerfiles / "Dockerfile.test-buildpack-v1"
        chain._build_image(
            dockerfile_path=dockerfile,
            cured_image_tag="localhost:32000/test:latest",
            composite_image="python:3.14-slim",
        )

        # Last call should be cleanup
        last_call = mock_ssh.run.call_args_list[-1]
        assert "rm -rf" in last_call[0][0]


class TestRemoteBuildpackChainBuild:
    """Tests for RemoteBuildpackChain.build() with pyproject.toml.

    These tests require real file I/O (pyproject.toml) but use mock SSH.
    """

    def test_build_returns_cached_image(
        self, mock_ssh: MagicMock, make_pyproject_with_gdal: Path
    ) -> None:
        """build() returns existing image without rebuilding."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
            pyproject_path=make_pyproject_with_gdal,
        )

        result = chain.build(["python:3.14-slim"])

        assert result == "localhost:32000/python3.14-slim:latest"
        # Only called once to check if image exists
        assert mock_ssh.run.call_count == 1

    def test_build_first_public_image_not_built(
        self, mock_ssh: MagicMock, make_pyproject_with_gdal: Path
    ) -> None:
        """build() uses first public image as-is without building."""
        mock_ssh.run.return_value = (1, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
            pyproject_path=make_pyproject_with_gdal,
        )

        result = chain.build(["python:3.14-slim"])

        # Should return the public image directly
        assert result == "python:3.14-slim"
