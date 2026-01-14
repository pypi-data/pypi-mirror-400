"""
djb deploy k8s buildpack - Manage buildpack base images.

Provides commands for building and managing buildpack images
that form the base layers for fast application deployments.

Buildpacks are chained Docker images:
    python:3.14-slim -> oven/bun:latest -> postgres:17-bookworm -> gdal-slim-dynamic-v1

The colon (`:`) is the discriminator:
- With `:` -> Public image (used as-is if first, glued otherwise)
- Without `:` -> Custom buildpack (must have Dockerfile.{spec})

Each buildpack builds FROM the previous one. The final image becomes
the base for the application layer, enabling fast deploys.
"""

from __future__ import annotations

import click

from djb.buildpacks import (
    DOCKERFILES_DIR,
    BuildpackError,
    RemoteBuildpackChain,
    parse,
)
from djb.cli.context import CliK8sContext, djb_pass_context
from djb.core.logging import get_logger
from djb.ssh import SSHClient, SSHError

logger = get_logger(__name__)


@click.group()
def buildpack():
    """Manage buildpack base images.

    Buildpacks are pre-built Docker images that contain heavy dependencies
    like Python, GDAL, and build tools. By pre-building these layers,
    application deployments become much faster (seconds instead of minutes).

    \b
    Examples:
      djb deploy k8s buildpack list           # List available buildpacks
      djb deploy k8s buildpack build          # Build configured buildpacks
      djb deploy k8s buildpack build --force  # Rebuild all buildpacks
    """
    pass


@buildpack.command("list")
@djb_pass_context
def buildpack_list(cli_ctx: CliK8sContext):
    """List configured buildpacks in the chain.

    Shows the buildpack chain from .djb/project.toml and available
    custom buildpack Dockerfiles.
    """
    config = cli_ctx.config
    if config is None:
        raise click.ClickException("No djb configuration found")

    buildpacks_list = config.k8s.backend.buildpacks

    if not buildpacks_list:
        logger.info("No buildpacks configured in .djb/project.toml")
        logger.info('Add buildpacks with: [k8s.backend] buildpacks = ["python:3.14-slim"]')
        return

    logger.info("Configured buildpack chain:")
    for i, spec_str in enumerate(buildpacks_list):
        spec = parse(spec_str, validate_dockerfile=False)
        if spec.is_public:
            if i == 0:
                logger.info(f"  {i + 1}. {spec_str} (public, base image)")
            else:
                logger.info(f"  {i + 1}. {spec_str} (public, glued)")
        else:
            dockerfile = DOCKERFILES_DIR / f"Dockerfile.{spec_str}"
            if dockerfile.exists():
                logger.info(f"  {i + 1}. {spec_str} (custom, {dockerfile.name})")
            else:
                logger.info(f"  {i + 1}. {spec_str} (custom, MISSING: {dockerfile.name})")

    logger.note()
    logger.info("Available custom buildpack Dockerfiles:")
    dockerfiles = sorted(DOCKERFILES_DIR.glob("Dockerfile.*"))
    for dockerfile in dockerfiles:
        if dockerfile.name == "Dockerfile.glue":
            continue  # Skip the glue Dockerfile
        spec_name = dockerfile.name.replace("Dockerfile.", "")
        logger.info(f"  - {spec_name}")


@buildpack.command("build")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Rebuild all buildpacks even if they exist.",
)
@djb_pass_context
@click.pass_context
def buildpack_build(ctx: click.Context, cli_ctx: CliK8sContext, force: bool):
    """Build the configured buildpack chain on the remote server.

    Builds each buildpack in the chain configured in .djb/project.toml.
    Each buildpack builds FROM the previous one in the chain.

    Skips buildpacks that already exist in the registry unless --force is used.

    \b
    Configuration in .djb/project.toml:
      [k8s.backend]
      buildpacks = ["python:3.14-slim", "oven/bun:latest", "gdal-slim-dynamic-v1"]
    """
    k8s_ctx = ctx.find_object(CliK8sContext)
    if k8s_ctx is None:
        raise click.ClickException("k8s context not available")

    config = cli_ctx.config
    if config is None:
        raise click.ClickException("No djb configuration found")

    buildpacks_list = config.k8s.backend.buildpacks

    if not buildpacks_list:
        logger.info("No buildpacks configured in .djb/project.toml")
        logger.info('Add buildpacks with: [k8s.backend] buildpacks = ["python:3.14-slim"]')
        return

    # Default registry for remote builds
    registry = "localhost:32000"

    # Get host from k8s context or config
    host = k8s_ctx.host
    if host is None:
        # Try to get from k8s config
        if config.k8s.host:
            host = f"root@{config.k8s.host}"
        else:
            raise click.ClickException("No host specified. Use --host or configure a server first.")

    logger.info(f"Building buildpack chain on {host}")
    logger.info(f"Buildpacks: {' -> '.join(buildpacks_list)}")
    logger.info(f"Registry: {registry}")

    # Create SSH client
    try:
        ssh = SSHClient(
            host=host,
            cmd_runner=cli_ctx.runner,
            port=k8s_ctx.port,
            key_path=k8s_ctx.ssh_key,
        )
    except SSHError as e:
        raise click.ClickException(f"SSH connection failed: {e}")

    try:
        chain = RemoteBuildpackChain(
            registry=registry,
            ssh=ssh,
            pyproject_path=config.project_dir / "pyproject.toml",
            djb_config=config,
        )
        final_image = chain.build(buildpacks_list, force_rebuild=force)
        logger.note()
        logger.done("Buildpack chain complete!")
        logger.info(f"Final image: {final_image}")
        logger.note()
    except BuildpackError as e:
        raise click.ClickException(str(e))
