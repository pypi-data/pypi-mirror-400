"""djb init secrets - Set up secrets management."""

from __future__ import annotations

from pathlib import Path

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.init.shared import InitContext
from djb.cli.secrets import _ensure_prerequisites as ensure_secrets_prerequisites
from djb.cli.utils import CmdRunner
from djb.core.logging import get_logger
from djb.secrets import init_gpg_agent_config, init_or_upgrade_secrets

logger = get_logger(__name__)


def auto_commit_secrets(runner: CmdRunner, project_root: Path, user_email: str | None) -> None:
    """Auto-commit secrets config to git if modified."""
    secrets_dir = project_root / "secrets"
    git_dir = project_root / ".git"

    if not git_dir.exists() or not user_email:
        return

    sops_config = secrets_dir / ".sops.yaml"
    files_to_commit = []

    if sops_config.exists():
        result = runner.run(
            ["git", "status", "--porcelain", str(sops_config)],
            cwd=project_root,
        )
        if result.stdout.strip():
            files_to_commit.append(str(sops_config.relative_to(project_root)))

    if files_to_commit:
        logger.next("Committing public key to git")
        logger.info(f"Files: {', '.join(files_to_commit)}")

        for file in files_to_commit:
            runner.run(["git", "add", file], cwd=project_root)

        commit_msg = f"Add public key for {user_email}"
        result = runner.run(
            ["git", "commit", "-m", commit_msg],
            cwd=project_root,
            fail_msg="Could not commit public key",
        )
        if result.returncode == 0:
            if result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    logger.info(f"  {line}")
            logger.done("Public key committed")


def init_secrets(
    cli_ctx: CliContext,
    project_root: Path,
    user_email: str | None,
    user_name: str | None,
    project_name: str,
    *,
    skip: bool = False,
) -> None:
    """Initialize secrets management.

    Args:
        cli_ctx: CLI context with runner and config.
        project_root: Path to project root.
        user_email: User email for secrets.
        user_name: User name for secrets.
        project_name: Project name for secrets.
        skip: If True, skip secrets initialization entirely.
    """
    if skip:
        logger.skip("Secrets initialization")
        return

    logger.next("Initializing secrets management")

    runner = cli_ctx.runner
    if not ensure_secrets_prerequisites(cli_ctx, quiet=True):
        raise click.ClickException("Cannot initialize secrets without SOPS and age")

    if init_gpg_agent_config(runner):
        logger.done("Created GPG agent config with passphrase caching")

    status = init_or_upgrade_secrets(
        cli_ctx, project_root, email=user_email, name=user_name, project_name=project_name
    )

    if status.initialized:
        logger.done(f"Created secrets: {', '.join(status.initialized)}")
    if status.upgraded:
        logger.done(f"Upgraded secrets: {', '.join(status.upgraded)}")
    if status.up_to_date and not status.initialized and not status.upgraded:
        logger.info("Secrets already up to date")

    # Auto-commit .sops.yaml if this is a git repo and the file was modified
    auto_commit_secrets(runner, project_root, user_email)


@click.command("secrets")
@click.option("--skip-secrets", is_flag=True, help="Skip secrets initialization")
@djb_pass_context(InitContext)
@click.pass_context
def secrets(ctx: click.Context, init_ctx: InitContext, skip_secrets: bool) -> None:
    """Set up secrets management.

    Initializes SOPS/age encryption for secrets and configures GPG agent
    for passphrase caching.
    """
    djb_config = init_ctx.config
    project_dir = djb_config.project_dir
    user_email = init_ctx.user_email
    user_name = init_ctx.user_name
    project_name = init_ctx.project_name or djb_config.project_name
    skip_secrets = init_ctx.skip_secrets or skip_secrets

    init_secrets(
        init_ctx,
        project_dir,
        user_email,
        user_name,
        project_name,
        skip=skip_secrets,
    )
