"""Shared utilities and context for djb init subcommands."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any

import click

from djb.cli.context import CliContext
from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class InitContext(CliContext):
    """Specialized context for djb init command group.

    Holds state that flows between subcommands when running the full init.
    """

    # From config phase
    configured_values: dict[str, Any] = field(default_factory=dict)
    user_name: str | None = None
    user_email: str | None = None
    project_name: str | None = None

    # From project phase
    gitignore_updated: bool = False

    # Skip flags (set by main init command, read by subcommands)
    skip_brew: bool = False
    skip_python: bool = False
    skip_frontend: bool = False
    skip_db: bool = False
    skip_migrations: bool = False
    skip_seed: bool = False
    skip_secrets: bool = False
    skip_hooks: bool = False
    skip_docker: bool = False


def get_clipboard_command() -> str:
    """Get the appropriate clipboard command for the current platform.

    Returns:
        'clip.exe' on WSL2, 'pbcopy' on macOS, 'xclip' on Linux.
    """
    # Check for WSL2 first
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                return "clip.exe"
    except (FileNotFoundError, PermissionError):
        pass

    # macOS
    if sys.platform == "darwin":
        return "pbcopy"

    # Linux fallback
    return "xclip"


def get_clipboard_read_command() -> list[str]:
    """Get the appropriate clipboard read command for the current platform.

    Returns:
        Command as list of strings for subprocess:
        - ['powershell.exe', '-command', 'Get-Clipboard'] on WSL2
        - ['pbpaste'] on macOS
        - ['xclip', '-selection', 'clipboard', '-o'] on Linux
    """
    # Check for WSL2 first
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                return ["powershell.exe", "-command", "Get-Clipboard"]
    except (FileNotFoundError, PermissionError):
        pass

    # macOS
    if sys.platform == "darwin":
        return ["pbpaste"]

    # Linux fallback
    return ["xclip", "-selection", "clipboard", "-o"]


def read_clipboard(runner: CmdRunner) -> str:
    """Read content from the system clipboard.

    Args:
        runner: CmdRunner instance for executing commands.

    Returns:
        Clipboard content as string (trailing newline stripped).

    Raises:
        click.ClickException: If clipboard cannot be read or tool is not installed.
    """
    cmd = get_clipboard_read_command()
    try:
        result = runner.run(cmd, timeout=5)
        if result.returncode != 0:
            raise click.ClickException(f"Failed to read clipboard: {result.stderr.strip()}")
        return result.stdout.removesuffix("\n")
    except CmdTimeout:
        raise click.ClickException("Clipboard read timed out")


def show_success_message() -> None:
    """Show final success message with next steps."""
    logger.done("djb initialization complete!")
    logger.note()
    logger.info("To start developing, run in separate terminals:")
    logger.info("  1. python manage.py runserver")
    logger.info("  2. cd frontend && bun run dev")
    logger.note()
    clip_cmd = get_clipboard_command()
    logger.tip(f"Back up your private secrets Age key: djb secrets export-key | {clip_cmd}")
    logger.tip(
        "Push your commit, then ask a teammate to run: djb secrets rotate\n"
        "         (This gives you access to staging/production secrets)"
    )
