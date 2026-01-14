"""djb init - Main init command group."""

from __future__ import annotations

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.init.config import config
from djb.cli.init.db import db
from djb.cli.init.deps import deps
from djb.cli.init.docker import docker
from djb.cli.init.hooks import hooks
from djb.cli.init.project import project
from djb.cli.init.secrets import secrets
from djb.cli.init.shared import InitContext, show_success_message
from djb.core.logging import get_logger

logger = get_logger(__name__)


@click.group("init", invoke_without_command=True)
@click.option(
    "--skip-brew",
    is_flag=True,
    help="Skip installing system dependencies via Homebrew",
)
@click.option(
    "--skip-python",
    is_flag=True,
    help="Skip installing Python dependencies",
)
@click.option(
    "--skip-frontend",
    is_flag=True,
    help="Skip installing frontend dependencies",
)
@click.option(
    "--skip-db",
    is_flag=True,
    help="Skip database initialization",
)
@click.option(
    "--skip-migrations",
    is_flag=True,
    help="Skip running Django migrations",
)
@click.option(
    "--skip-seed",
    is_flag=True,
    help="Skip running the seed command",
)
@click.option(
    "--skip-secrets",
    is_flag=True,
    help="Skip secrets initialization",
)
@click.option(
    "--skip-hooks",
    is_flag=True,
    help="Skip installing git hooks",
)
@click.option(
    "--skip-docker",
    is_flag=True,
    help="Skip Docker setup",
)
@djb_pass_context
@click.pass_context
def init(
    ctx: click.Context,
    cli_ctx: CliContext,
    skip_brew: bool,
    skip_python: bool,
    skip_frontend: bool,
    skip_db: bool,
    skip_migrations: bool,
    skip_seed: bool,
    skip_secrets: bool,
    skip_hooks: bool,
    skip_docker: bool,
) -> None:
    """Initialize djb development environment.

    When run without a subcommand, executes all initialization steps.
    Use subcommands to run specific phases.

    \b
    Subcommands:
      config   - Configure project settings and identity
      project  - Update .gitignore and Django settings
      deps     - Install system and package dependencies
      db       - Initialize database and run migrations
      secrets  - Set up secrets management
      hooks    - Install git hooks
      docker   - Set up Docker (install, start, autostart)

    \b
    Examples:
      djb init                    # Full setup
      djb init --skip-brew        # Skip Homebrew
      djb init deps               # Only install dependencies
      djb init db --skip-seed     # Database without seeding
    """
    # Specialize context for init subcommands
    init_ctx = InitContext()
    init_ctx.__dict__.update(cli_ctx.__dict__)
    ctx.obj = init_ctx
    init_ctx.skip_brew = skip_brew
    init_ctx.skip_python = skip_python
    init_ctx.skip_frontend = skip_frontend
    init_ctx.skip_db = skip_db
    init_ctx.skip_migrations = skip_migrations
    init_ctx.skip_seed = skip_seed
    init_ctx.skip_secrets = skip_secrets
    init_ctx.skip_hooks = skip_hooks
    init_ctx.skip_docker = skip_docker

    # If no subcommand, run all
    if ctx.invoked_subcommand is None:
        _run_all(ctx)


def _run_all(ctx: click.Context) -> None:
    """Run all init subcommands in order."""
    logger.info("Initializing djb development environment")

    ctx.invoke(config)
    ctx.invoke(project)
    ctx.invoke(deps)
    ctx.invoke(docker)
    ctx.invoke(db)
    ctx.invoke(secrets)
    ctx.invoke(hooks)

    show_success_message()


# Register subcommands
init.add_command(config)
init.add_command(project)
init.add_command(deps)
init.add_command(docker)
init.add_command(db)
init.add_command(secrets)
init.add_command(hooks)
