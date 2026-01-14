"""
djb docker - Docker build commands for local development.

Provides commands for building Docker images locally, including the
buildpack chain required for the application Dockerfile.

Commands:
    djb docker build     - Build the buildpack chain
    djb docker build -f  - Force rebuild all images

The buildpack chain is composed of public images (glued together)
and custom buildpacks (built from Dockerfiles in djb).
"""

from __future__ import annotations

import click

from djb.buildpacks import BuildpackError, LocalBuildpackChain
from djb.cli.context import CliContext, djb_pass_context
from djb.core.logging import get_logger

logger = get_logger(__name__)


@click.group("docker")
def docker() -> None:
    """Docker build commands for local development.

    Build the buildpack chain and application images locally
    for use with Skaffold or direct Docker workflows.
    """


@docker.command("build")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force rebuild all images even if they exist.",
)
@click.option(
    "--registry",
    default=None,
    help="Registry address (default: from cluster provider or localhost:5000).",
)
@djb_pass_context
def build(cli_ctx: CliContext, force: bool, registry: str | None) -> str:
    """Build the buildpack chain for local development.

    Builds each layer of the buildpack chain:
    - Public images (with :) are used as-is or merged via Dockerfile.glue
    - Custom buildpacks (without :) are built from their Dockerfiles

    Returns the final composite image tag for use in the application Dockerfile.

    \b
    Examples:
        djb docker build           # Build buildpack chain
        djb docker build --force   # Rebuild all layers
    """
    buildpacks = cli_ctx.config.k8s.backend.buildpacks

    if not buildpacks:
        raise click.ClickException(
            "No buildpacks configured.\n" "Add buildpacks to .djb/project.toml under [k8s.backend]"
        )

    # Default registry for local development
    if registry is None:
        registry = "localhost:5000"

    logger.next("Building buildpack chain")
    logger.info(f"Buildpacks: {' -> '.join(buildpacks)}")

    try:
        chain = LocalBuildpackChain(
            registry=registry,
            runner=cli_ctx.runner,
            pyproject_path=cli_ctx.config.project_dir / "pyproject.toml",
            djb_config=cli_ctx.config,
        )
        final_image = chain.build(buildpacks, force_rebuild=force)
        logger.done(f"Buildpack chain ready: {final_image}")
        return final_image

    except BuildpackError as e:
        raise click.ClickException(str(e))


def build_buildpacks_for_registry(
    cli_ctx: CliContext,
    registry: str,
    force: bool = False,
) -> str:
    """Build the buildpack chain for a specific registry.

    Utility function for use by other commands (e.g., local dev).

    Args:
        cli_ctx: CLI context with config and runner
        registry: Registry address to tag images for
        force: Force rebuild all layers

    Returns:
        Final composite image tag
    """
    buildpacks = cli_ctx.config.k8s.backend.buildpacks

    if not buildpacks:
        raise BuildpackError(
            "No buildpacks configured. " "Add buildpacks to .djb/project.toml under [k8s.backend]"
        )

    chain = LocalBuildpackChain(
        registry=registry,
        runner=cli_ctx.runner,
        pyproject_path=cli_ctx.config.project_dir / "pyproject.toml",
        djb_config=cli_ctx.config,
    )
    return chain.build(buildpacks, force_rebuild=force)
