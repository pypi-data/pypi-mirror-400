"""djb init config - Configure project settings and sync git identity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from djb.cli.context import djb_pass_context
from djb.cli.init.shared import InitContext
from djb.config import DjbConfig
from djb.types import Mode
from djb.config.acquisition import acquire_all_fields
from djb.config.storage.io import LocalConfigIO
from djb.config.storage.io.external import GitConfigIO
from djb.core.logging import get_logger

logger = get_logger(__name__)


def validate_project(project_root: Path) -> None:
    """Validate we're in a Python project with pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        raise click.ClickException(
            f"No pyproject.toml found in {project_root}. "
            "Run 'djb init' from your project root directory."
        )


def configure_all_fields(project_dir: Path, config: DjbConfig) -> dict[str, Any]:
    """Configure all config fields using the acquisition generator.

    Field order is determined by declaration order in DjbConfig.
    Acquirable fields are those with an acquire() method and prompt_text.

    Project config values are saved to the bare/production section (no mode prefix)
    because init sets up the project's base configuration, not mode-specific overrides.

    Args:
        project_dir: Project root directory.
        config: Current DjbConfig instance.

    Returns:
        Dict of configured field values.
    """
    # Create a production-mode config for saving project values
    # This ensures values are written to the bare section (e.g., [tool.djb])
    # rather than a mode-specific section (e.g., [tool.djb.development])
    # Uses augment() to preserve CLI overrides from parent command
    override_config = DjbConfig(mode=Mode.PRODUCTION)
    save_config = config.augment(override_config)

    configured: dict[str, Any] = {}
    copied_from_git: list[str] = []

    logger.next("Configuring project settings")

    for field_name, result in acquire_all_fields(save_config):
        configured[field_name] = result.value

        # Track git config sources for summary message
        if result.source_name == "git config":
            copied_from_git.append(field_name)

    # Summary message for git config copies
    if copied_from_git:
        logger.info(f"Copied {' and '.join(copied_from_git)} from git config")

    # Log config file location
    config_path = LocalConfigIO(config).resolve_path()
    if any(f in configured for f in ("name", "email")):
        logger.info(f"Config saved to: {config_path}")

    return configured


def sync_identity_to_git(config: DjbConfig) -> None:
    """Sync name/email from djb config to git global config if needed.

    If name/email are in djb config but not from git config, sync them
    so users don't have to configure git separately.

    Args:
        config: Current DjbConfig instance.
    """
    for field_name in ("name", "email"):
        value = getattr(config, field_name, None)

        # Only sync if we have a value from djb config (not from git)
        if value and config.is_explicit(field_name):
            git_key = "user.name" if field_name == "name" else "user.email"
            git_io = GitConfigIO(git_key, config)
            # Only sync if git config doesn't already have this value
            current_git_value, _ = git_io.get(field_name)
            if current_git_value != value:
                git_io.set(field_name, value)


@click.command("config")
@djb_pass_context(InitContext)
@click.pass_context
def config(ctx: click.Context, init_ctx: InitContext) -> None:
    """Configure project settings and sync git identity.

    Validates pyproject.toml exists, prompts for name/email if needed,
    and syncs identity to git global config.
    """
    djb_config = init_ctx.config
    project_dir = djb_config.project_dir

    validate_project(project_dir)

    logger.info("Configuring project settings")

    # Configure all fields using the acquisition generator
    configured = configure_all_fields(project_dir, djb_config)
    sync_identity_to_git(djb_config)

    # Store results in context for other subcommands
    init_ctx.configured_values = configured
    init_ctx.user_name = configured.get("name")
    init_ctx.user_email = configured.get("email")
    init_ctx.project_name = configured.get("project_name", djb_config.project_name)
