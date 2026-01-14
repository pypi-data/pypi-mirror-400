"""
djb deploy seed CLI - Run seed command across platforms.

This command runs the host project's seed command to populate the database.
It works across all deployment platforms:
- Local development
- Heroku
- Kubernetes

The command is idempotent if the seed command itself is idempotent.
"""

from __future__ import annotations

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.seed import run_seed_command
from djb.core.logging import get_logger
from djb.k8s import K8sManifestGenerator, MigrationCtx
from djb.ssh import SSHClient
from djb.types import Platform

logger = get_logger(__name__)


@click.command("seed")
@click.option(
    "--app",
    default=None,
    help="Heroku app name (for Heroku platform)",
)
@click.option(
    "--host",
    default=None,
    help="SSH host for K8s deployment (e.g., user@host:port)",
)
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
@djb_pass_context
def deploy_seed(
    cli_ctx: CliContext, app: str | None, host: str | None, extra_args: tuple[str, ...]
) -> None:
    """Run the host project's seed command.

    Executes the configured seed command to populate the database with
    initial data. Any additional arguments are passed to the seed command.

    The platform is auto-detected from configuration, or can be overridden
    with --app (Heroku) or --host (K8s).

    \b
    Examples:
      djb deploy seed                        # Auto-detect platform
      djb deploy seed --app myapp            # Run on Heroku
      djb deploy seed --host root@host       # Run on K8s
      djb deploy seed -- --truncate          # Pass args to seed command
    """
    config = cli_ctx.config

    if not config.seed_command:
        raise click.ClickException(
            "No seed_command configured.\n\n"
            "Configure a seed command with:\n"
            "  djb config seed_command myapp.cli.seed:seed"
        )

    # Build the seed command - invoke the configured seed command directly
    # Parse the module:attr format (e.g., "beachresort25.cli.seed:seed")
    seed_command = config.seed_command
    module_path, attr_name = seed_command.split(":")

    # Build a Python command that imports and runs the seed function
    # This bypasses the djb CLI which requires config files
    # Quote the entire Python code to prevent shell interpretation of semicolons
    python_code = (
        f"import django; django.setup(); "
        f"from {module_path} import {attr_name}; "
        f"{attr_name}.main(standalone_mode=False)"
    )
    # The full command that will be passed to the shell
    seed_cmd = [f'python -c "{python_code}"']
    if extra_args:
        # Extra args not supported in this mode
        logger.warning("Extra arguments not supported for K8s seed")

    # Determine platform
    if app:
        _run_on_heroku(cli_ctx, app, seed_cmd)
    elif host:
        _run_on_k8s(cli_ctx, host, seed_cmd)
    elif config.platform == Platform.K8S:
        raise click.ClickException("K8s host not specified. Use --host option.")
    else:
        _run_locally(cli_ctx, seed_cmd)


def _run_locally(cli_ctx: CliContext, cmd: list[str]) -> None:
    """Run seed locally."""
    logger.next("Running seed locally")
    # For local, use the seed command directly
    if not run_seed_command(cli_ctx.config):
        raise click.ClickException("Seed failed")
    logger.done("Seed complete")


def _run_on_heroku(cli_ctx: CliContext, app: str, seed_cmd: list[str]) -> None:
    """Run seed on Heroku."""
    cmd = [
        "heroku",
        "run",
        "--no-notify",
        "--app",
        app,
        "--",
        *seed_cmd,
    ]
    cli_ctx.runner.run(
        cmd,
        label=f"Running seed on Heroku ({app})",
        show_output=True,
        fail_msg=click.ClickException("Seed failed on Heroku"),
        done_msg="Seed complete",
    )


def _run_on_k8s(cli_ctx: CliContext, ssh_host: str, seed_cmd: list[str]) -> None:
    """Run seed on K8s as a Job."""
    config = cli_ctx.config
    project_name = config.project_name
    runner = cli_ctx.runner

    logger.next("Running seed on K8s")

    # Parse SSH host
    user, host, port = _parse_ssh_host(ssh_host)

    # Get the current image from the deployment
    ssh = SSHClient(host=f"{user}@{host}", cmd_runner=runner, port=port)
    returncode, stdout, _ = ssh.run(
        f"microk8s kubectl get deployment {project_name} -n {project_name} "
        f"-o jsonpath='{{.spec.template.spec.containers[0].image}}'"
    )
    if returncode != 0 or not stdout.strip():
        raise click.ClickException("Could not get current deployment image")
    image_tag = stdout.strip()

    # Build environment variables
    env_vars: dict[str, str] = {}
    if domains := ",".join(config.domain_names_list):
        env_vars["DJB_DOMAINS"] = domains
    env_vars["DJB_INTERNAL_HOST"] = project_name

    # Create a job manifest using the migration template
    job_name = f"{project_name}-seed"
    command = " ".join(seed_cmd)

    migration_ctx = MigrationCtx(
        image=image_tag,
        command=command,
        has_secrets=True,  # Seed may need secrets
        env_vars=env_vars,
    )

    generator = K8sManifestGenerator()
    job_manifest = generator.render("migration-job.yaml.j2", config, migration_ctx)

    # Replace the job name in the manifest
    job_manifest = job_manifest.replace(
        f"{project_name}-migrate-{image_tag.split(':')[-1][:8]}", job_name
    )

    # Delete any existing job
    ssh.run(f"microk8s kubectl delete job {job_name} -n {project_name} --ignore-not-found")

    # Apply the job
    escaped_manifest = job_manifest.replace("'", "'\"'\"'")
    returncode, _, stderr = ssh.run(
        f"echo '{escaped_manifest}' | microk8s kubectl apply -f -",
    )
    if returncode != 0:
        raise click.ClickException(f"Failed to create seed job: {stderr}")

    # Wait for job to complete (seed can take a while)
    returncode, _, stderr = ssh.run(
        f"microk8s kubectl wait --for=condition=complete job/{job_name} "
        f"-n {project_name} --timeout=600s",
        timeout=630,
    )

    if returncode != 0:
        # Get job logs for debugging
        ssh.run(f"microk8s kubectl logs job/{job_name} -n {project_name}")
        raise click.ClickException(f"Seed failed: {stderr}")

    logger.done("Seed complete")


def _parse_ssh_host(ssh_host: str) -> tuple[str, str, int]:
    """Parse SSH host string into user, host, port."""
    # Format: user@host:port or user@host or host
    user = "root"
    port = 22

    if "@" in ssh_host:
        user, ssh_host = ssh_host.split("@", 1)

    if ":" in ssh_host:
        host, port_str = ssh_host.rsplit(":", 1)
        port = int(port_str)
    else:
        host = ssh_host

    return user, host, port
