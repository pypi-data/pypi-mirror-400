"""
djb run - Execute commands on remote server via SSH.

Provides a simple interface for running commands on the configured deployment server.
"""

from __future__ import annotations

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.core.logging import get_logger
from djb.ssh import SSHClient, SSHError

logger = get_logger(__name__)


@click.command("run")
@click.argument("command", nargs=-1, required=True)
@click.option(
    "--user",
    "-u",
    default="root",
    help="SSH user (default: root)",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=60,
    help="Command timeout in seconds (default: 60)",
)
@click.option(
    "--streaming/--no-streaming",
    default=True,
    help="Stream output in real-time (default: enabled)",
)
@djb_pass_context
def run(
    cli_ctx: CliContext,
    command: tuple[str, ...],
    user: str,
    timeout: int,
    streaming: bool,
) -> None:
    """Execute a command on the remote deployment server.

    The server is determined by the k8s.host configuration.

    Examples:

        djb run uptime

        djb run microk8s kubectl get pods

        djb run "cat /etc/hostname"

        djb run --user ubuntu whoami
    """
    config = cli_ctx.config

    # Get server IP from config
    server_ip = config.k8s.host
    if not server_ip:
        raise click.ClickException(
            "No server configured. Set k8s.host in config or run 'djb deploy k8s terraform'."
        )

    # Build host string
    host = f"{user}@{server_ip}"

    # Join command arguments into a single command string
    cmd_str = " ".join(command)

    logger.next(f"Connecting to {host}")

    try:
        ssh = SSHClient(
            host=host,
            cmd_runner=cli_ctx.runner,
            port=22,
        )
    except SSHError as e:
        raise click.ClickException(f"SSH connection failed: {e}")

    logger.next(f"Running: {cmd_str}")

    try:
        if streaming:
            returncode = ssh.run_streaming(cmd_str)
        else:
            returncode, stdout, stderr = ssh.run(cmd_str, timeout=timeout)
            if stdout:
                click.echo(stdout.rstrip())
            if stderr:
                click.echo(stderr.rstrip(), err=True)

        if returncode != 0:
            raise click.ClickException(f"Command exited with code {returncode}")

    except SSHError as e:
        raise click.ClickException(f"SSH error: {e}")
