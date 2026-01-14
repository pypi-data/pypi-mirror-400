"""djb init db - Initialize database and run migrations."""

from __future__ import annotations

from pathlib import Path

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.db import init_database
from djb.cli.init.shared import InitContext
from djb.cli.seed import run_seed_command
from djb.cli.utils import CmdRunner
from djb.config import DjbConfig
from djb.core.logging import get_logger

logger = get_logger(__name__)


def init_db(cli_ctx: CliContext, *, skip: bool = False) -> bool:
    """Initialize the development database.

    Args:
        cli_ctx: CLI context with runner and config.
        skip: If True, skip database initialization entirely.

    Returns:
        True if database was initialized or skipped, False if failed.
    """
    if skip:
        logger.skip("Database initialization")
        return True

    logger.next("Initializing development database")
    if not init_database(cli_ctx, start_service=True, quiet=False):
        logger.warning("Database initialization failed - you can run 'djb db init' later")
        return False
    return True


def run_migrations(runner: CmdRunner, project_root: Path, *, skip: bool = False) -> bool:
    """Run Django migrations.

    Args:
        runner: CmdRunner instance for executing commands.
        project_root: Path to project root.
        skip: If True, skip migrations entirely.

    Returns:
        True if migrations succeeded or skipped, False if failed.
    """
    if skip:
        logger.skip("Django migrations")
        return True

    logger.next("Running Django migrations")
    result = runner.run(
        ["uv", "run", "python", "manage.py", "migrate"],
        cwd=project_root,
        label="Running migrations",
        done_msg="Migrations complete",
    )
    if result.returncode != 0:
        logger.warning("Migrations failed - you can run 'python manage.py migrate' later")
        return False
    return True


def run_seed(config: DjbConfig, *, skip: bool = False) -> bool:
    """Run the host project's seed command if configured.

    Args:
        config: Current DjbConfig instance.
        skip: If True, skip seeding entirely.

    Returns:
        True if seed succeeded, skipped, or not configured, False if failed.
    """
    if skip:
        logger.skip("Database seeding")
        return True

    if not config.seed_command:
        logger.skip("No seed_command configured")
        return True

    logger.next("Seeding database")
    if not run_seed_command(config):
        logger.warning("Seed failed - you can run 'djb seed' later")
        return False
    # Seed command prints its own done message
    return True


@click.command("db")
@click.option("--skip-db", is_flag=True, help="Skip database initialization")
@click.option("--skip-migrations", is_flag=True, help="Skip Django migrations")
@click.option("--skip-seed", is_flag=True, help="Skip database seeding")
@djb_pass_context(InitContext)
@click.pass_context
def db(
    ctx: click.Context,
    init_ctx: InitContext,
    skip_db: bool,
    skip_migrations: bool,
    skip_seed: bool,
) -> None:
    """Initialize database and run migrations.

    Initializes PostgreSQL database, runs Django migrations,
    and optionally seeds the database.
    """
    djb_config = init_ctx.config
    project_dir = djb_config.project_dir
    skip_db = init_ctx.skip_db or skip_db
    skip_migrations = init_ctx.skip_migrations or skip_migrations
    skip_seed = init_ctx.skip_seed or skip_seed

    runner = init_ctx.runner
    init_db(init_ctx, skip=skip_db)
    run_migrations(runner, project_dir, skip=skip_migrations)
    run_seed(djb_config, skip=skip_seed)
