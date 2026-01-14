"""
djb sync-superuser CLI - Sync Django superuser from encrypted secrets.
"""

from __future__ import annotations

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.core.logging import get_logger

logger = get_logger(__name__)


@click.command("sync-superuser")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "--app",
    default=None,
    help="Heroku app name (runs on Heroku instead of locally)",
)
@djb_pass_context
def sync_superuser(cli_ctx: CliContext, dry_run: bool, app: str | None):
    """Sync superuser from encrypted secrets.

    Creates or updates the Django superuser based on credentials stored
    in the encrypted secrets file. Requires the Django project to have
    a `sync_superuser` management command.

    The environment is determined by the current mode (from djb --mode or DJB_MODE).

    \b
    Examples:
      djb sync-superuser                        # Sync locally (development mode)
      djb --mode staging sync-superuser         # Sync using staging secrets
      djb sync-superuser --app myapp            # Sync on Heroku
      djb sync-superuser --dry-run              # Preview changes
    """
    config = cli_ctx.config
    project_dir = config.project_dir
    mode = config.mode.value

    if app:
        # Run on Heroku - use --no-notify and -- separator for proper arg passing
        cmd = [
            "heroku",
            "run",
            "--no-notify",
            "--app",
            app,
            "--",
            "python",
            "manage.py",
            "sync_superuser",
        ]
        if mode:
            cmd.extend(["--environment", mode])
        if dry_run:
            cmd.append("--dry-run")
        cli_ctx.runner.run(
            cmd,
            label=f"Syncing superuser on Heroku ({app})",
            show_output=True,
            fail_msg=click.ClickException("Failed to sync superuser"),
        )
    else:
        # Run locally with streaming output
        cmd = ["python", "manage.py", "sync_superuser"]
        if mode:
            cmd.extend(["--environment", mode])
        if dry_run:
            cmd.append("--dry-run")
        cli_ctx.runner.run(
            cmd,
            cwd=project_dir,
            label="Syncing superuser locally",
            show_output=True,
            fail_msg=click.ClickException("Failed to sync superuser"),
        )
