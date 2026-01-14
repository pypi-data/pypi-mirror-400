"""
Stash/restore editable djb configuration.

Provides a clean way to temporarily remove editable djb configuration for
operations that need to push/commit clean files (like deploy and publish),
then restore the editable state afterward.

Uses `djb editable-djb` commands under the hood, which delegate pyproject.toml
manipulation to uv.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from djb.core.cmd_runner import CmdRunner
from djb.core.logging import get_logger
from djb.cli.editable import (
    install_editable_djb,
    is_djb_editable,
    uninstall_editable_djb,
)

logger = get_logger(__name__)


def bust_uv_cache(runner: CmdRunner) -> None:
    """Clear uv's cache for djb to ensure fresh resolution."""
    runner.run(["uv", "cache", "clean", "djb"])


def regenerate_uv_lock(runner: CmdRunner, repo_root: Path, quiet: bool = False) -> bool:
    """Regenerate uv.lock with the current pyproject.toml.

    Returns True on success, False on failure.
    If quiet=False (default), prints stderr on failure to help diagnose issues.
    """
    result = runner.run(["uv", "lock", "--refresh"], cwd=repo_root)
    if result.returncode != 0 and not quiet:
        if result.stderr:
            logger.fail(f"uv lock error: {result.stderr.strip()}")
        if result.stdout:
            logger.info(f"uv lock output: {result.stdout.strip()}")
    return result.returncode == 0


@contextmanager
def stashed_editable(runner: CmdRunner, repo_root: Path, quiet: bool = False):
    """Context manager to temporarily remove editable djb configuration.

    Uses `djb editable-djb --uninstall` to remove and `djb editable-djb` to
    restore.

    Usage:
        with stashed_editable(runner, repo_root) as was_editable:
            # pyproject.toml no longer has editable config
            # do git operations here
            pass
        # editable config is restored

    Args:
        runner: CmdRunner instance for executing commands.
        repo_root: Project root directory.
        quiet: If True, suppress output messages.

    Yields:
        bool: True if djb was in editable mode before stashing, False otherwise.

    If an exception occurs, the original state is still restored.
    """
    was_editable = is_djb_editable(repo_root)

    if was_editable:
        if not quiet:
            logger.info("Temporarily removing editable djb configuration...")
        uninstall_editable_djb(runner, repo_root, quiet=True)

    try:
        yield was_editable
    finally:
        if was_editable:
            if not quiet:
                logger.info("Restoring editable djb configuration...")
            install_editable_djb(runner, repo_root, quiet=True)


def restore_editable(runner: CmdRunner, repo_root: Path, quiet: bool = False) -> bool:
    """Re-enable editable mode for local development.

    Used by publish after committing the version bump. This installs djb
    in editable mode using `uv add --editable`, which handles all the
    TOML manipulation correctly.

    Args:
        runner: CmdRunner instance for executing commands.
        repo_root: Path to the project root
        quiet: If True, suppress output messages

    Returns:
        True on success, False on failure
    """
    return install_editable_djb(runner, repo_root, quiet=quiet)
