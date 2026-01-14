"""djb init hooks - Install git hooks."""

from __future__ import annotations

from pathlib import Path

import click

from djb.cli.context import djb_pass_context
from djb.cli.editable import install_pre_commit_hook
from djb.cli.init.shared import InitContext
from djb.core.logging import get_logger

logger = get_logger(__name__)


def install_git_hooks(project_root: Path, *, skip: bool = False) -> None:
    """Install git hooks for the project.

    Installs:
    - pre-commit hook to prevent committing pyproject.toml with editable djb

    Args:
        project_root: Path to project root.
        skip: If True, skip hook installation entirely.
    """
    if skip:
        logger.skip("Git hooks installation")
        return

    logger.next("Installing git hooks")

    git_dir = project_root / ".git"
    if not git_dir.exists():
        logger.skip("Not a git repository, skipping hooks")
        return

    # Use the pre-commit hook from djb.cli.editable
    if install_pre_commit_hook(project_root, quiet=True):
        logger.done("Git hooks installed (pre-commit: editable djb check)")
    else:
        logger.warning("Could not install git hooks")


@click.command("hooks")
@click.option("--skip-hooks", is_flag=True, help="Skip git hooks installation")
@djb_pass_context(InitContext)
@click.pass_context
def hooks(ctx: click.Context, init_ctx: InitContext, skip_hooks: bool) -> None:
    """Install git hooks.

    Installs pre-commit hook to prevent committing pyproject.toml
    with editable djb reference.
    """
    project_dir = init_ctx.config.project_dir
    skip_hooks = init_ctx.skip_hooks or skip_hooks

    install_git_hooks(project_dir, skip=skip_hooks)
