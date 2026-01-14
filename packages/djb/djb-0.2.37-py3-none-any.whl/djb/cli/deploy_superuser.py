"""
djb deploy superuser CLI - Sync Django superuser across platforms.

This command creates or updates the Django superuser based on credentials
stored in encrypted secrets. It works across all deployment platforms:
- Local development
- Heroku
- Kubernetes

The command is idempotent - it can be run multiple times safely.
"""

from __future__ import annotations

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.core.logging import get_logger
from djb.k8s import K8sManifestGenerator, MigrationCtx
from djb.ssh import SSHClient
from djb.types import Platform

logger = get_logger(__name__)


@click.command("superuser")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
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
@djb_pass_context
def deploy_superuser(cli_ctx: CliContext, dry_run: bool, app: str | None, host: str | None) -> None:
    """Sync superuser from encrypted secrets.

    Creates or updates the Django superuser based on credentials stored
    in the encrypted secrets file. This command is idempotent and can be
    run as part of deployment.

    The platform is auto-detected from configuration, or can be overridden
    with --app (Heroku) or --host (K8s).

    \b
    Examples:
      djb deploy superuser                    # Auto-detect platform
      djb deploy superuser --app myapp        # Run on Heroku
      djb deploy superuser --host root@host   # Run on K8s
      djb deploy superuser --dry-run          # Preview changes
    """
    config = cli_ctx.config
    mode = config.mode.value

    # Build the base command
    mgmt_cmd = ["python", "manage.py", "sync_superuser"]
    if mode:
        mgmt_cmd.extend(["--environment", mode])
    if dry_run:
        mgmt_cmd.append("--dry-run")

    # Determine platform
    if app:
        _run_on_heroku(cli_ctx, app, mgmt_cmd)
    elif host:
        _run_on_k8s(cli_ctx, host, mgmt_cmd)
    elif config.platform == Platform.K8S:
        raise click.ClickException("K8s host not specified. Use --host option.")
    else:
        _run_locally(cli_ctx, mgmt_cmd)


def _run_locally(cli_ctx: CliContext, cmd: list[str]) -> None:
    """Run sync_superuser locally."""
    cli_ctx.runner.run(
        cmd,
        cwd=cli_ctx.config.project_dir,
        label="Syncing superuser locally",
        show_output=True,
        fail_msg=click.ClickException("Failed to sync superuser"),
        done_msg="Superuser synced",
    )


def _run_on_heroku(cli_ctx: CliContext, app: str, mgmt_cmd: list[str]) -> None:
    """Run sync_superuser on Heroku."""
    cmd = [
        "heroku",
        "run",
        "--no-notify",
        "--app",
        app,
        "--",
        *mgmt_cmd,
    ]
    cli_ctx.runner.run(
        cmd,
        label=f"Syncing superuser on Heroku ({app})",
        show_output=True,
        fail_msg=click.ClickException("Failed to sync superuser on Heroku"),
        done_msg="Superuser synced",
    )


def _run_on_k8s(cli_ctx: CliContext, ssh_host: str, mgmt_cmd: list[str]) -> None:
    """Run sync_superuser on K8s as a Job."""
    config = cli_ctx.config
    project_name = config.project_name
    runner = cli_ctx.runner

    logger.next("Syncing superuser on K8s")

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
    job_name = f"{project_name}-superuser"
    command = " ".join(mgmt_cmd)

    migration_ctx = MigrationCtx(
        image=image_tag,
        command=command,
        has_secrets=True,  # Superuser needs secrets for credentials
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
        raise click.ClickException(f"Failed to create superuser job: {stderr}")

    # Wait for job to complete
    returncode, _, stderr = ssh.run(
        f"microk8s kubectl wait --for=condition=complete job/{job_name} "
        f"-n {project_name} --timeout=120s",
        timeout=150,
    )

    if returncode != 0:
        # Get job logs for debugging
        ssh.run(f"microk8s kubectl logs job/{job_name} -n {project_name}")
        raise click.ClickException(f"Superuser sync failed: {stderr}")

    logger.done("Superuser synced")


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
