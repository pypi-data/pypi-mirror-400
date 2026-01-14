"""
djb CLI - Main command-line interface.

Provides subcommands for secrets management, deployment, and development.

Subcommands are lazily loaded to speed up startup. Heavy dependencies like
django, yaml, jinja2, and hcloud are only imported when the specific
subcommand is invoked.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import click

from djb._version import __version__
from djb.cli.context import CliContext
from djb.cli.lazy import LazyGroup
from djb.core.logging import Colors, get_logger, setup_logging
from djb.config import DjbConfig, get_djb_config
from djb.config.fields.machine_state import MachineStateConfig
from djb.machine_state import SearchStrategy
from djb.types import Mode, Platform

logger = get_logger(__name__)


def print_banner(config: DjbConfig) -> None:
    """Print the djb banner showing current mode and platform.

    Mode colors:
    - development: green
    - staging: cyan
    - production: red

    Platform colors:
    - heroku: purple
    - k8s: blue
    """
    mode_colors = {
        Mode.DEVELOPMENT: Colors.GREEN,
        Mode.STAGING: Colors.CYAN,
        Mode.PRODUCTION: Colors.RED,
    }
    platform_colors = {
        Platform.HEROKU: Colors.PURPLE,
        Platform.K8S: Colors.BLUE,
    }

    mode_color = mode_colors.get(config.mode, "")
    mode_str = f"{mode_color}{config.mode}{Colors.RESET}"
    platform_color = platform_colors.get(config.platform, "")
    platform_str = f"{platform_color}{config.platform}{Colors.RESET}"

    logger.info(f"[djb] mode: {mode_str} | platform: {platform_str}")


@click.group(cls=LazyGroup, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="djb")
@click.option(
    "--log-level",
    type=click.Choice(["error", "warning", "info", "note", "debug"], case_sensitive=False),
    default=None,
    envvar="DJB_LOG_LEVEL",
    show_envvar=True,
    help="Set logging verbosity level (default: from config or 'info')",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed output (e.g., error messages on failure)",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress non-essential output",
)
@click.option(
    "--frontend",
    "scope_frontend",
    is_flag=True,
    help="Limit scope to frontend tasks only",
)
@click.option(
    "--backend",
    "scope_backend",
    is_flag=True,
    help="Limit scope to backend tasks only",
)
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    envvar="DJB_PROJECT_DIR",
    show_envvar=True,
    help="Project root directory (default: auto-detect).",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["development", "staging", "production"], case_sensitive=False),
    default=None,
    envvar="DJB_MODE",
    show_envvar=True,
    help="Deployment mode (persists to config when set).",
)
@click.option(
    "--platform",
    "-p",
    type=click.Choice(["heroku", "k8s"], case_sensitive=False),
    default=None,
    envvar="DJB_PLATFORM",
    show_envvar=True,
    help="Deployment platform (persists to config when set).",
)
@click.option(
    "--config-class",
    default=None,
    envvar="DJB_CONFIG_CLASS",
    show_envvar=True,
    help="Config class (module.path.ClassName) for extending DjbConfig.",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Auto-confirm prompts.",
)
@click.option(
    "--machine-state-search-strategy",
    "search_strategy",
    type=click.Choice([s.value for s in SearchStrategy], case_sensitive=False),
    default=None,
    envvar="DJB_MACHINE_STATE_SEARCH_STRATEGY",
    show_envvar=True,
    help="Algorithm for multi-step commands (init, deploy, etc.): auto, linear, or binary.",
)
@click.pass_context
def djb_cli(
    ctx: click.Context,
    log_level: str | None,
    verbose: bool,
    quiet: bool,
    scope_frontend: bool,
    scope_backend: bool,
    project_dir: Path | None,
    mode: str | None,
    platform: str | None,
    config_class: str | None,
    yes: bool,
    search_strategy: str | None,
):
    """djb - Django + Bun deployment platform"""
    # Get config with CLI overrides using augment() pattern
    try:
        config = get_djb_config()
    except ValueError as e:
        raise click.ClickException(str(e))

    if project_dir is not None:
        config = config.augment(DjbConfig(project_dir=project_dir))
    if mode is not None:
        config = config.augment(DjbConfig(mode=Mode(mode)))
    if platform is not None:
        config = config.augment(DjbConfig(platform=Platform(platform)))
    if log_level is not None:
        config = config.augment(DjbConfig(log_level=log_level))
    if verbose:
        config = config.augment(DjbConfig(verbose=verbose))
    if quiet:
        config = config.augment(DjbConfig(quiet=quiet))
    if yes:
        config = config.augment(DjbConfig(yes=yes))
    if config_class is not None:
        config = config.augment(DjbConfig(config_class=config_class))
    if search_strategy is not None:
        config = config.augment(
            DjbConfig(
                machine_state=MachineStateConfig(search_strategy=SearchStrategy(search_strategy))
            )
        )

    # Set up logging using resolved config value (CLI > ENV > local > project > default)
    setup_logging(config.log_level)

    # Persist mode/platform if explicitly set via CLI
    if mode is not None:
        config.set("mode", str(config.mode))
    if platform is not None:
        config.set("platform", str(config.platform))

    # Store in context for subcommands
    ctx.ensure_object(CliContext)
    if not isinstance(ctx.obj, CliContext):
        raise click.ClickException("Internal error: context object is not CliContext")
    ctx.obj.verbose = verbose
    ctx.obj.quiet = quiet
    ctx.obj.yes = yes
    ctx.obj.scope_frontend = scope_frontend
    ctx.obj.scope_backend = scope_backend
    ctx.obj.config = config

    # Set search strategy from config (already resolved CLI > ENV > config)
    ctx.obj.search_strategy = config.machine_state.search_strategy

    # Print banner (unless nested invocation, quiet mode, or pipe-friendly command)
    # Commands that output data for piping should not print the banner
    pipe_friendly_commands = {"secrets export-key"}
    command_path = " ".join(
        arg for arg in sys.argv[1:] if not arg.startswith("-") and not arg.startswith("--")
    )
    is_pipe_friendly = any(command_path.startswith(cmd) for cmd in pipe_friendly_commands)

    # DJB_NESTED is used to supress the djb cli banner for nested cli invocations.
    if not os.environ.get("DJB_NESTED") and not quiet and not is_pipe_friendly:
        print_banner(config)

    # Handle bare invocation (no subcommand)
    if ctx.invoked_subcommand is None:
        if mode is not None or platform is not None:
            # Mode/platform was set, config saved, banner printed - just exit
            return
        # No subcommand and no config change - show help
        logger.info(ctx.get_help())
        return

    # Validate required config fields (skip for init command which sets them up)
    if ctx.invoked_subcommand != "init":
        missing = []
        if config.project_dir is None:
            missing.append("project_dir")
        if config.project_name is None:
            missing.append("project_name")
        if config.name is None:
            missing.append("name")
        if config.email is None:
            missing.append("email")
        if missing:
            raise click.ClickException(
                f"Missing required config: {', '.join(missing)}. "
                f"Run 'djb init' from your project directory to set up configuration."
            )


# Register subcommands with lazy loading
# Commands are only imported when invoked, speeding up startup
LAZY_COMMANDS = {
    "config": "djb.cli.config_cmd:config_group",
    "db": "djb.cli.db:db",
    "dependencies": "djb.cli.dependencies:dependencies",
    "deploy": "djb.cli.deploy:deploy",
    "docker": "djb.cli.docker:docker",
    "domain": "djb.cli.domain:domain",
    "editable": "djb.cli.editable:editable_djb",
    "health": "djb.cli.health:health",
    "heroku": "djb.cli.heroku:heroku",
    "index": "djb.cli.index:index",
    "init": "djb.cli.init.init:init",
    "k8s": "djb.cli.k8s:k8s",
    "publish": "djb.cli.publish:publish",
    "run": "djb.cli.run:run",
    "secrets": "djb.cli.secrets:secrets",
    "seed": "djb.cli.seed:seed",
    "sync-superuser": "djb.cli.superuser:sync_superuser",
}

for name, import_path in LAZY_COMMANDS.items():
    djb_cli.add_lazy_command(import_path, name)


@djb_cli.command("help")
@click.pass_context
def help_cmd(ctx: click.Context) -> None:
    """Show this help message."""
    # Get the parent (djb_cli) context and print its help
    if ctx.parent is not None:
        logger.info(ctx.parent.get_help())


def main():
    """Entry point for djb CLI."""
    djb_cli()


if __name__ == "__main__":
    main()
