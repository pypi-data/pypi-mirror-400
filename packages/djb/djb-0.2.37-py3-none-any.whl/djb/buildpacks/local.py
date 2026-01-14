"""Local buildpack chain building using Docker."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from djb.buildpacks.base import BuildpackChain
from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.specs import parse

if TYPE_CHECKING:
    from djb.config import DjbConfig
    from djb.core.cmd_runner import CmdRunner


class LocalBuildpackChain(BuildpackChain):
    """Buildpack chain builder for local Docker.

    Builds Docker images locally using the Docker daemon.
    Useful for local development with k3d or similar.

    Usage:
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=runner,
            pyproject_path=Path("pyproject.toml"),
        )
        final_image = chain.build(["python:3.14-slim", "gdal-slim-dynamic-v1"])
    """

    def __init__(
        self,
        registry: str,
        runner: "CmdRunner",
        pyproject_path: Path | None = None,
        djb_config: "DjbConfig | None" = None,
    ) -> None:
        """Initialize local buildpack chain builder.

        Args:
            registry: Docker registry host (e.g., "k3d-registry.localhost:5000")
            runner: Command runner for executing docker commands
            pyproject_path: Path to pyproject.toml for dynamic version resolution
            djb_config: Optional DjbConfig for project-first Dockerfile resolution
        """
        super().__init__(registry, pyproject_path, djb_config)
        self.runner = runner

    def image_exists(self, image_tag: str) -> bool:
        """Check if an image exists locally."""
        return self.runner.check(["docker", "image", "inspect", image_tag], timeout=10)

    def _build_image(
        self,
        dockerfile_path: Path,
        cured_image_tag: str,
        composite_image: str | None,
        laminate_image: str | None = None,
        buildpack_version: str | None = None,
    ) -> str:
        """Build a Docker image locally.

        Args:
            dockerfile_path: Path to the Dockerfile
            cured_image_tag: Tag for the built image (the new cured composite)
            composite_image: Existing composite to build on (COMPOSITE_IMAGE build arg)
            laminate_image: Layer being laminated in (LAMINATE_IMAGE build arg)
            buildpack_version: BUILDPACK_VERSION build arg value (for dynamic buildpacks)

        Returns:
            The cured_image_tag

        Raises:
            BuildpackError: If build fails
        """
        cmd = ["docker", "build"]

        if composite_image:
            cmd.extend(["--build-arg", f"COMPOSITE_IMAGE={composite_image}"])
        if laminate_image:
            cmd.extend(["--build-arg", f"LAMINATE_IMAGE={laminate_image}"])
            namespace = parse(laminate_image, validate_dockerfile=False).namespace
            cmd.extend(["--build-arg", f"NAMESPACE={namespace}"])
        if buildpack_version:
            cmd.extend(["--build-arg", f"BUILDPACK_VERSION={buildpack_version}"])

        cmd.extend(
            ["-f", str(dockerfile_path), "-t", cured_image_tag, str(self._get_build_context())]
        )

        success = self.runner.run(
            cmd,
            label=f"Building {cured_image_tag}",
            show_output=True,
            timeout=self._estimate_build_timeout_seconds(dockerfile_path, laminate_image),
        )

        if not success:
            raise BuildpackError(f"Failed to build {cured_image_tag}")

        return cured_image_tag
