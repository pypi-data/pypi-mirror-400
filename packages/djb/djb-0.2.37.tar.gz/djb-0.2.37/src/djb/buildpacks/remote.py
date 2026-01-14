"""Remote buildpack chain building via SSH."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from djb.buildpacks.base import BuildpackChain
from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.specs import parse

if TYPE_CHECKING:
    from djb.config import DjbConfig
    from djb.ssh import SSHClient


class RemoteBuildpackChain(BuildpackChain):
    """Buildpack chain builder for remote servers via SSH.

    Builds Docker images on a remote server using SSH, then pushes to
    the microk8s containerd registry.

    Usage:
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=ssh_client,
            pyproject_path=Path("pyproject.toml"),
        )
        final_image = chain.build(["python:3.14-slim", "gdal-slim-dynamic-v1"])
    """

    def __init__(
        self,
        registry: str,
        ssh: "SSHClient",
        pyproject_path: Path | None = None,
        djb_config: "DjbConfig | None" = None,
    ) -> None:
        """Initialize remote buildpack chain builder.

        Args:
            registry: Docker registry host (e.g., "localhost:32000")
            ssh: SSH client connected to the remote server
            pyproject_path: Path to pyproject.toml for dynamic version resolution
            djb_config: Optional DjbConfig for project-first Dockerfile resolution
        """
        super().__init__(registry, pyproject_path, djb_config)
        self.ssh = ssh

    def image_exists(self, image_tag: str) -> bool:
        """Check if an image exists in the remote registry.

        Uses microk8s ctr to check containerd registry.
        """
        returncode, _, _ = self.ssh.run(
            f"microk8s ctr image ls | grep -q '{image_tag}'",
            timeout=30,
        )
        return returncode == 0

    def _build_image(
        self,
        dockerfile_path: Path,
        cured_image_tag: str,
        composite_image: str | None,
        laminate_image: str | None = None,
        buildpack_version: str | None = None,
    ) -> str:
        """Build a Docker image on the remote server.

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
        remote_build_dir = "/tmp/djb-buildpack-build"

        # Create remote build directory
        self.ssh.run(f"mkdir -p {remote_build_dir}")

        # Read local Dockerfile and write to remote
        dockerfile_content = dockerfile_path.read_text()
        escaped_content = dockerfile_content.replace("'", "'\"'\"'")
        returncode, _, stderr = self.ssh.run(
            f"echo '{escaped_content}' > {remote_build_dir}/Dockerfile"
        )
        if returncode != 0:
            raise BuildpackError(f"Failed to write Dockerfile: {stderr}")

        # Build command with build args
        build_args = []
        if composite_image:
            build_args.append(f"--build-arg COMPOSITE_IMAGE={composite_image}")
        if laminate_image:
            build_args.append(f"--build-arg LAMINATE_IMAGE={laminate_image}")
            namespace = parse(laminate_image, validate_dockerfile=False).namespace
            build_args.append(f"--build-arg NAMESPACE={namespace}")
        if buildpack_version:
            build_args.append(f"--build-arg BUILDPACK_VERSION={buildpack_version}")

        build_args_str = " ".join(build_args)
        build_cmd = f"cd {remote_build_dir} && docker build {build_args_str} -t {cured_image_tag} ."

        timeout = self._estimate_build_timeout_seconds(dockerfile_path, laminate_image)
        returncode, _, stderr = self.ssh.run(build_cmd, timeout=timeout)
        if returncode != 0:
            raise BuildpackError(f"Failed to build {cured_image_tag}: {stderr}")

        # Import to containerd
        returncode, _, stderr = self.ssh.run(
            f"docker save {cured_image_tag} | microk8s ctr image import -",
            timeout=300,
        )
        if returncode != 0:
            raise BuildpackError(f"Failed to import {cured_image_tag}: {stderr}")

        # Push to registry
        returncode, _, stderr = self.ssh.run(
            f"microk8s ctr image push --plain-http {cured_image_tag}",
            timeout=300,
        )
        if returncode != 0:
            raise BuildpackError(f"Failed to push {cured_image_tag}: {stderr}")

        # Cleanup
        self.ssh.run(f"rm -rf {remote_build_dir}")

        return cured_image_tag
