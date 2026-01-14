"""
djb deploy heroku CLI - Heroku deployment commands.

Provides commands for deploying Django applications to Heroku:
- `djb deploy heroku` - Deploy to Heroku
- `djb deploy heroku setup` - Configure Heroku app
- `djb deploy heroku revert` - Revert to previous deployment
- `djb deploy heroku seed` - Seed production database

Deployment Workflow
-------------------
The `djb deploy heroku` command orchestrates a complete deployment:

1. **Secrets Sync**: Decrypts secrets (based on current mode) and sets them as Heroku config vars
2. **Editable Stash**: Temporarily removes editable djb config (restored after)
3. **Git Push**: Force-pushes the current branch to Heroku's main
4. **Migrations**: Runs Django migrations on the Heroku dyno
5. **Tagging**: Tags the commit for deployment tracking (deploy-<hash>)

Why Force Push
--------------
Heroku requires pushing to its `main` branch. Using --force ensures the
deployment succeeds even if the branch histories have diverged (common
after reverts or rebases). The deployment is tagged, so rollback is easy.

Editable Mode Handling
----------------------
If djb is installed in editable mode during development, the pyproject.toml
contains a local path reference that won't work on Heroku. The stashed_editable
context manager temporarily removes this configuration during git push,
then restores it after deployment completes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import click

from djb.core.cmd_runner import CmdError, CmdRunner

from djb.cli.context import CliContext, CliHerokuContext, djb_pass_context
from djb.cli.domain import domain_sync
from djb.cli.editable_stash import stashed_editable
from djb.cli.seed import load_seed_command
from djb.cli.utils import flatten_dict
from djb.config import DjbConfig
from djb.core.logging import get_logger
from djb.secrets import (
    ProtectedFileError,
    SecretsManager,
    SopsError,
    find_placeholder_secrets,
    get_default_key_path,
    get_default_secrets_dir,
)
from djb.types import Mode

logger = get_logger(__name__)


# Maximum length for Heroku config var values displayed/logged
# (truncation threshold for readability, not a Heroku API limit)
HEROKU_CONFIG_VAR_MAX_LENGTH: Final[int] = 500


@dataclass
class HerokuDeployConfig:
    """Configuration for Heroku deployment implementation.

    Groups parameters passed to _deploy_heroku_impl().
    This is an implementation detail dataclass, not a Click context.
    """

    # Target
    app: str
    mode: Mode
    domains: list[str]

    # Behavior flags
    local_build: bool
    skip_migrate: bool
    skip_secrets: bool
    yes: bool

    # Paths
    repo_root: Path
    frontend_dir: Path
    secrets_dir: Path
    key_path: Path


def _get_app_or_fail(app: str | None, config: DjbConfig | None) -> str:
    """Resolve Heroku app name from explicit value or config.

    Args:
        app: Explicit app name (if provided via --app flag)
        config: DjbConfig object with project_name (or None)

    Returns:
        Resolved app name

    Raises:
        click.ClickException: If no app name can be determined
    """
    if app is not None:
        return app

    if config is not None and config.project_name:
        logger.info(f"Using project name as Heroku app: {config.project_name}")
        return config.project_name

    raise click.ClickException(
        "No app name provided. Either use --app or ensure project name is set "
        "(via --project-name, DJB_PROJECT_NAME env var, or pyproject.toml)."
    )


# Heroku-managed config vars that should not be overwritten during deploy
HEROKU_MANAGED_KEYS = frozenset(
    {
        "DATABASE_URL",  # Managed by Heroku Postgres addon
        "DB_CREDENTIALS_USERNAME",
        "DB_CREDENTIALS_PASSWORD",
        "DB_CREDENTIALS_DATABASE",
        "DB_CREDENTIALS_HOST",
        "DB_CREDENTIALS_PORT",
    }
)


def _run_heroku_migrations(runner: CmdRunner, app: str, *, skip: bool = False) -> None:
    """Run Django migrations on Heroku with streaming output.

    Args:
        runner: CmdRunner instance for executing commands.
        app: Heroku app name.
        skip: If True, skip migrations and log skip message.

    Raises:
        click.ClickException: If migrations fail.
    """
    if skip:
        logger.skip("Database migrations")
        return

    cmd = ["heroku", "run", "--no-notify", "--app", app, "--", "python", "manage.py", "migrate"]
    runner.run(
        cmd,
        label="Running database migrations on Heroku",
        show_output=True,
        fail_msg=click.ClickException("Migrations failed on Heroku"),
        done_msg="Migrations complete",
    )


def _resolve_heroku_app(ctx: click.Context, param: click.Parameter, value: str | None) -> str:
    """Click callback to resolve Heroku app name from --app flag or config.

    If --app is provided, use that value. Otherwise, fall back to project_name
    from config (pyproject.toml, DJB_PROJECT_NAME env var, or --project-name).

    This callback is used by the --app option so subcommands don't need to
    manually call resolution logic.

    Args:
        ctx: Click context (provides access to config via ctx.obj)
        param: The --app parameter being processed
        value: Value provided via --app flag (or None)

    Returns:
        Resolved app name

    Raises:
        click.BadParameter: If no app name can be determined
    """
    if value is not None:
        return value

    # Try to get from config
    cli_ctx = ctx.find_object(CliContext)
    if cli_ctx and cli_ctx.config and cli_ctx.config.project_name:
        logger.info(f"Using project name as Heroku app: {cli_ctx.config.project_name}")
        return cli_ctx.config.project_name

    raise click.BadParameter(
        "No app name provided. Either use --app or ensure project name is set "
        "(via --project-name, DJB_PROJECT_NAME env var, or pyproject.toml).",
        ctx=ctx,
        param=param,
    )


def _ensure_heroku_domains_configured(ctx: click.Context) -> None:
    """Configure custom domains on Heroku and optionally Cloudflare DNS.

    Only runs if:
    - cloudflare.auto_dns is enabled
    - There are custom domains (non-herokuapp.com) configured

    Args:
        ctx: Click context (used to invoke domain sync command)
    """
    config = ctx.obj.config
    # Filter out herokuapp.com domains (Heroku manages those)
    custom_domains = [
        d for d in config.heroku.domain_names.keys() if not d.endswith(".herokuapp.com")
    ]

    if not custom_domains:
        return

    if not config.cloudflare.auto_dns:
        logger.info("Cloudflare auto_dns disabled, skipping domain configuration")
        return

    logger.next("Configuring custom domains")
    ctx.invoke(domain_sync, dry_run=False)


@click.group("heroku", invoke_without_command=True)
@click.option(
    "--app",
    default=None,
    callback=_resolve_heroku_app,
    help="Heroku app name (default: project_name). Use when app name differs from project.",
)
@click.option(
    "--local-build",
    is_flag=True,
    help="Build frontend locally before push (default: let Heroku buildpack build).",
)
@click.option(
    "--skip-migrate",
    is_flag=True,
    help="Skip running database migrations on Heroku.",
)
@click.option(
    "--skip-secrets",
    is_flag=True,
    help="Skip syncing secrets to Heroku config vars.",
)
@click.option(
    "--frontend-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Frontend directory containing package.json (default: ./frontend)",
)
@click.option(
    "--secrets-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Secrets directory (default: ./secrets)",
)
@click.option(
    "--key-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to age key file (default: ~/.age/keys.txt)",
)
@djb_pass_context
@click.pass_context
def heroku(
    ctx: click.Context,
    cli_ctx: CliContext,
    app: str,
    local_build: bool,
    skip_migrate: bool,
    skip_secrets: bool,
    frontend_dir: Path | None,
    secrets_dir: Path | None,
    key_path: Path | None,
):
    """Deploy to Heroku or manage Heroku configuration.

    When invoked without a subcommand, deploys the application to Heroku.

    \b
    Deployment workflow:
    * Checks mode (warns and prompts if not production)
    * Syncs secrets to Heroku config vars (loads secrets matching current mode)
    * Pushes code to Heroku (buildpacks handle frontend and collectstatic)
    * Runs database migrations
    * Tags the deployment for tracking

    If djb is in editable mode, the config is temporarily stashed during deploy.

    \b
    Examples:
      djb deploy heroku                    # Deploy to Heroku
      djb --mode production deploy heroku  # Deploy in production mode
      djb deploy heroku --app myapp        # Explicit app name
      djb -y deploy heroku                 # Skip confirmation prompts
      djb deploy heroku setup              # Configure Heroku app
      djb deploy heroku revert             # Revert to previous deployment
      djb deploy heroku seed --here-be-dragons  # Seed production database
    """
    # Specialize context for heroku subcommands
    heroku_ctx = CliHerokuContext(app=app, **cli_ctx.__dict__)
    ctx.obj = heroku_ctx

    # Only run deployment if no subcommand was invoked
    if ctx.invoked_subcommand is not None:
        return

    # Deployment guard: warn if not in production mode
    config = heroku_ctx.config
    repo_root = config.project_dir
    current_mode = config.mode
    if current_mode != Mode.PRODUCTION:
        logger.warning(f"Deploying to Heroku with mode={current_mode}")
        logger.info("Heroku deployments typically use mode=production.")
        logger.tip("Set production mode: djb --mode production deploy heroku")
        if not heroku_ctx.yes and not click.confirm("Continue with deployment?", default=False):
            raise click.ClickException("Deployment cancelled")

    if frontend_dir is None:
        frontend_dir = repo_root / "frontend"
    if secrets_dir is None:
        secrets_dir = get_default_secrets_dir(repo_root)
    if key_path is None:
        key_path = get_default_key_path(repo_root)
    assert frontend_dir is not None

    # Create runner from context
    runner = heroku_ctx.runner

    # Temporarily remove editable djb config if present (restores automatically on exit)
    # Use quiet=True since we print our own messages here
    with stashed_editable(runner, repo_root, quiet=True) as was_editable:
        if was_editable:
            logger.info("Stashed editable djb configuration for deploy...")

        deploy_config = HerokuDeployConfig(
            app=app,
            mode=current_mode,
            domains=list(config.heroku.domain_names.keys()),
            local_build=local_build,
            skip_migrate=skip_migrate,
            skip_secrets=skip_secrets,
            yes=heroku_ctx.yes,
            repo_root=repo_root,
            frontend_dir=frontend_dir,
            secrets_dir=secrets_dir,
            key_path=key_path,
        )
        _deploy_heroku_impl(runner, deploy_config)

        # Configure custom domains on Heroku and optionally Cloudflare DNS
        _ensure_heroku_domains_configured(ctx)

        if was_editable:
            logger.info("Restoring editable djb configuration...")


def _deploy_heroku_impl(runner: CmdRunner, config: HerokuDeployConfig):
    """Internal implementation of Heroku deployment."""
    # Check if logged into Heroku
    try:
        runner.run(
            ["heroku", "auth:whoami"],
            label="Checking Heroku auth",
            fail_msg=CmdError("Heroku auth check failed"),
        )
    except CmdError:
        raise click.ClickException("Not logged into Heroku. Run 'heroku login' first.")

    # Verify we're in a git repository
    if not (config.repo_root / ".git").exists():
        raise click.ClickException("Not in a git repository")

    # Sync secrets to Heroku config vars
    # Use the current mode to determine which secrets to load
    if not config.skip_secrets:
        logger.next(f"Syncing {config.mode.value} secrets to Heroku")
        try:
            # SecretsManager handles GPG-protected keys automatically
            manager = SecretsManager(
                runner,
                config.repo_root,
                secrets_dir=config.secrets_dir,
            )
            secrets = manager.load_secrets(config.mode)

            # Sync secrets to Heroku if we loaded them
            if secrets is not None:
                # Check for placeholder secrets that need to be changed
                placeholders = find_placeholder_secrets(secrets)
                if placeholders:
                    logger.warning(f"Found {len(placeholders)} secret(s) with placeholder values:")
                    for key in placeholders:
                        logger.info(f"   * {key}")
                    logger.note()
                    logger.warning(
                        "These secrets contain values like 'CHANGE-ME' that must be updated."
                    )
                    logger.info(f"Run 'djb secrets edit' to set real values.")
                    logger.note()
                    if not config.yes and not click.confirm(
                        "Continue deployment with placeholder secrets?", default=False
                    ):
                        raise click.ClickException("Deployment cancelled - update secrets first")

                flat_secrets = flatten_dict(secrets)

                # Collect config vars to set, filtering out managed/large values
                config_vars: list[str] = []
                for key_name, value in flat_secrets.items():
                    # Skip Heroku-managed database config vars
                    if key_name in HEROKU_MANAGED_KEYS:
                        logger.skip(f"{key_name} (managed by Heroku)")
                        continue

                    # Skip if it's a complex value
                    if len(value) > HEROKU_CONFIG_VAR_MAX_LENGTH:
                        logger.skip(f"{key_name} (value too large)")
                        continue

                    config_vars.append(f"{key_name}={value}")

                # Set all config vars in a single Heroku call
                if config_vars:
                    result = runner.run(
                        ["heroku", "config:set", *config_vars, "--app", config.app],
                    )
                    if result.returncode != 0:
                        raise CmdError(f"heroku config:set failed: {result.stderr}")

                logger.done(f"Synced {len(config_vars)} secrets to Heroku config")
        except (
            FileNotFoundError,
            SopsError,
            ProtectedFileError,
            CmdError,
        ) as e:
            logger.warning(f"Failed to sync secrets: {e}")
            if not config.yes and not click.confirm(
                "Continue deployment without secrets?", default=False
            ):
                raise click.ClickException("Deployment cancelled")
    else:
        logger.skip("Secrets sync")

    # Set DJB_DOMAINS for ALLOWED_HOSTS in Django settings
    if config.domains:
        domains_str = ",".join(config.domains)
        runner.run(
            ["heroku", "config:set", f"DJB_DOMAINS={domains_str}", "--app", config.app],
            label="Setting DJB_DOMAINS",
            done_msg=f"DJB_DOMAINS={domains_str}",
        )
    else:
        logger.warning("No domains configured. Set domains in .djb/project.toml [heroku] section")

    # Check for uncommitted changes
    result = runner.run(["git", "status", "--porcelain"], cwd=config.repo_root)
    if result.stdout.strip():
        logger.warning("You have uncommitted changes:")
        logger.info(result.stdout)
        if not config.yes and not click.confirm("Continue with deployment?", default=False):
            raise click.ClickException("Deployment cancelled")

    # Optionally build frontend locally (default: let Heroku bun buildpack handle it)
    if config.local_build:
        if config.frontend_dir.exists():
            runner.run(
                ["bun", "run", "build"],
                cwd=config.frontend_dir,
                label="Building frontend assets locally",
                done_msg="Frontend build complete",
            )

            # Also run collectstatic locally if doing local build
            runner.run(
                ["python", "manage.py", "collectstatic", "--noinput", "--clear"],
                cwd=config.repo_root,
                label="Collecting Django static files",
                done_msg="Static files collected",
            )
        else:
            logger.warning(f"Frontend directory not found at {config.frontend_dir}, skipping build")

    # Get current git commit hash for tracking
    result = runner.run(["git", "rev-parse", "HEAD"], cwd=config.repo_root)
    commit_hash = result.stdout.strip()[:7]

    # Check current branch
    result = runner.run(["git", "branch", "--show-current"], cwd=config.repo_root)
    current_branch = result.stdout.strip()

    logger.info(f"Deploying from branch '{current_branch}' (commit {commit_hash})...")

    # Check if force-push would overwrite commits on Heroku
    # Fetch the latest refs from Heroku first
    runner.run(["git", "fetch", "heroku"], cwd=config.repo_root)

    # Check if Heroku remote has commits not in local branch
    result = runner.run(
        ["git", "rev-list", "--count", f"HEAD..heroku/main"],
        cwd=config.repo_root,
    )
    remote_ahead_count = int(result.stdout.strip()) if result.returncode == 0 else 0

    if remote_ahead_count > 0:
        logger.warning(f"Force-push will overwrite {remote_ahead_count} commit(s) on Heroku")

        # Show the commits that will be lost
        result = runner.run(
            ["git", "log", "--oneline", f"HEAD..heroku/main"],
            cwd=config.repo_root,
        )
        if result.stdout.strip():
            logger.info("Commits that will be overwritten:")
            for line in result.stdout.strip().split("\n"):
                logger.info(f"   {line}")

        if not config.yes:
            logger.note()
            if not click.confirm(
                "Continue with force-push? (This will overwrite remote commits)", default=False
            ):
                raise click.ClickException("Deployment cancelled - use 'git pull' to merge first")

    # Push to Heroku - stream output in real-time while capturing for analysis
    result = runner.run(
        ["git", "push", "heroku", f"{current_branch}:main", "--force"],
        cwd=config.repo_root,
        label=f"Pushing to Heroku ({config.app})",
        show_output=True,
    )

    # Check if anything was actually pushed
    # Git outputs "Everything up-to-date" to stderr when nothing to push
    captured_output = result.stdout + result.stderr
    already_deployed = "Everything up-to-date" in captured_output

    if result.returncode != 0 and not already_deployed:
        logger.fail("Git push failed")
        raise click.ClickException("Failed to push to Heroku")

    if already_deployed:
        logger.warning(f"Nothing to deploy - commit {commit_hash} is already deployed on Heroku")
        return  # Exit early, no need to run migrations or tag

    logger.done("Code pushed to Heroku")

    _run_heroku_migrations(runner, config.app, skip=config.skip_migrate)

    # Tag the deployment
    tag_name = f"deploy-{commit_hash}"
    runner.run(["git", "tag", "-f", tag_name], cwd=config.repo_root)
    runner.run(["git", "push", "--tags", "--force"], cwd=config.repo_root)

    logger.done(f"Deployment successful! (commit: {commit_hash})")
    logger.info(f"App URL: https://{config.app}.herokuapp.com/")
    logger.tip(f"Logs: heroku logs --tail --app {config.app}")


@heroku.command("revert")
@click.argument("git_hash", required=False)
@click.option(
    "--skip-migrate",
    is_flag=True,
    help="Skip running database migrations on Heroku.",
)
@djb_pass_context(CliHerokuContext)
@click.pass_context
def revert(
    ctx: click.Context, heroku_ctx: CliHerokuContext, git_hash: str | None, skip_migrate: bool
):
    """Revert to a previous deployment.

    Pushes a previous git commit to Heroku, effectively rolling back
    your deployment. By default reverts to the previous commit (HEAD~1).

    Confirms before executing the revert. Tags the revert for tracking.

    \b
    Examples:
      djb deploy heroku revert               # Revert to previous commit
      djb deploy heroku revert abc123        # Revert to specific commit
      djb deploy heroku revert --skip-migrate  # Revert without migrations
    """
    config = heroku_ctx.config
    repo_root = config.project_dir
    app = heroku_ctx.app

    # Create runner from context
    runner = heroku_ctx.runner

    # Check if logged into Heroku
    try:
        runner.run(
            ["heroku", "auth:whoami"],
            label="Checking Heroku auth",
            fail_msg=CmdError("Heroku auth check failed"),
        )
    except CmdError:
        raise click.ClickException("Not logged into Heroku. Run 'heroku login' first.")

    # Verify we're in a git repository
    if not (repo_root / ".git").exists():
        raise click.ClickException("Not in a git repository")

    # If no git hash provided, use the previous commit
    if git_hash is None:
        result = runner.run(["git", "rev-parse", "HEAD~1"], cwd=repo_root)
        if result.returncode != 0:
            raise click.ClickException("Could not determine previous commit")
        assert result.stdout is not None  # For type checker: runner.run always captures output
        git_hash = result.stdout.strip()
        logger.info(f"No git hash provided, using previous commit: {git_hash[:7]}")

    # Verify the git hash exists
    if not runner.check(["git", "cat-file", "-t", git_hash], cwd=repo_root):
        raise click.ClickException(f"Git hash '{git_hash}' not found in repository")

    # Get full commit info
    result = runner.run(["git", "log", "-1", "--oneline", git_hash], cwd=repo_root)
    commit_info = result.stdout.strip()

    logger.info(f"Reverting to: {commit_info}")
    if not click.confirm("Continue with revert?", default=False):
        raise click.ClickException("Revert cancelled")

    # Push the specified commit to Heroku
    runner.run(
        ["git", "push", "heroku", f"{git_hash}:main", "--force"],
        label=f"Pushing commit {git_hash[:7]} to Heroku ({app})",
        done_msg="Code pushed to Heroku",
    )

    _run_heroku_migrations(runner, app, skip=skip_migrate)

    # Tag the revert
    short_hash = git_hash[:7]
    tag_name = f"revert-to-{short_hash}"
    runner.run(["git", "tag", "-f", tag_name], cwd=repo_root)
    runner.run(["git", "push", "--tags", "--force"], cwd=repo_root)

    logger.done(f"Revert successful! (commit: {short_hash})")
    logger.info(f"App URL: https://{app}.herokuapp.com/")
    logger.tip(f"Logs: heroku logs --tail --app {app}")


# Buildpacks required for djb projects (order matters!)
DJB_BUILDPACKS = [
    "https://github.com/heroku/heroku-geo-buildpack.git",  # GDAL for GeoDjango
    "https://github.com/jakeg/heroku-buildpack-bun",  # Bun for frontend
    "heroku/python",  # Python/Django
]


@heroku.command("setup")
@click.option(
    "--skip-buildpacks",
    is_flag=True,
    help="Skip configuring buildpacks.",
)
@click.option(
    "--skip-postgres",
    is_flag=True,
    help="Skip adding Heroku Postgres addon.",
)
@click.option(
    "--skip-remote",
    is_flag=True,
    help="Skip adding heroku git remote.",
)
@click.option(
    "--postgres-plan",
    default="essential-0",
    help="Heroku Postgres plan (default: essential-0, ~$5/month).",
)
@djb_pass_context(CliHerokuContext)
def setup(
    heroku_ctx: CliHerokuContext,
    skip_buildpacks: bool,
    skip_postgres: bool,
    skip_remote: bool,
    postgres_plan: str,
):
    """Configure Heroku app for djb deployment.

    Sets up an existing Heroku app with the required buildpacks,
    config vars, and addons for a Django + Bun + GeoDjango project.

    This command is idempotent. It will skip configuration that's already in
    place.

    \b
    Configuration applied:
    * Buildpacks (in order):
      1. heroku-geo-buildpack (GDAL for GeoDjango)
      2. heroku-buildpack-bun (Bun for frontend)
      3. heroku/python (Python/Django)
    * Config vars: DEBUG=False, DJB_MODE=production
    * Git remote: heroku -> https://git.heroku.com/<app>.git
    * Addon: heroku-postgresql (optional)

    \b
    Examples:
      djb deploy heroku --app myapp setup   # Setup specific app
      djb deploy heroku setup               # Use project_name from djb config
      djb deploy heroku setup --skip-postgres  # Skip database addon
      djb -y deploy heroku setup            # Auto-confirm all prompts
    """
    config = heroku_ctx.config
    repo_root = config.project_dir
    app = heroku_ctx.app

    # Create runner from context
    runner = heroku_ctx.runner

    logger.info(f"Setting up Heroku app: {app}")

    # Check if logged into Heroku
    try:
        runner.run(
            ["heroku", "auth:whoami"],
            label="Checking Heroku auth",
            fail_msg=CmdError("Heroku auth check failed"),
        )
    except CmdError:
        raise click.ClickException("Not logged into Heroku. Run 'heroku login' first.")

    # Verify the app exists
    result = runner.run(
        ["heroku", "apps:info", "--app", app],
        label=f"Verifying app '{app}' exists",
    )
    if result.returncode != 0:
        raise click.ClickException(
            f"App '{app}' not found. Create it first with: heroku create {app}"
        )
    logger.done(f"App '{app}' found")

    # Configure buildpacks
    if not skip_buildpacks:
        logger.next("Configuring buildpacks")

        # Get current buildpacks
        result = runner.run(
            ["heroku", "buildpacks", "--app", app],
        )
        current_buildpacks = result.stdout.strip()

        # Check if buildpacks are already configured correctly
        all_present = all(bp in current_buildpacks for bp in DJB_BUILDPACKS)
        if all_present:
            logger.done("Buildpacks already configured correctly")
        else:
            # Clear and set buildpacks in order
            logger.info("Setting buildpacks (order matters for Heroku):")
            for i, buildpack in enumerate(DJB_BUILDPACKS, 1):
                logger.info(f"  {i}. {buildpack}")

            if not heroku_ctx.yes and not click.confirm(
                "Apply this buildpack configuration?", default=True
            ):
                logger.skip("Buildpack configuration")
            else:
                # Clear existing buildpacks
                runner.run(
                    ["heroku", "buildpacks:clear", "--app", app],
                )

                # Add buildpacks in order
                for buildpack in DJB_BUILDPACKS:
                    runner.run(
                        ["heroku", "buildpacks:add", buildpack, "--app", app],
                    )

                logger.done("Buildpacks configured")
    else:
        logger.skip("Buildpack configuration")

    # Set config vars: DEBUG=False, DJB_MODE=production
    logger.next("Setting config vars")

    # Check current values
    result = runner.run(
        ["heroku", "config:get", "DEBUG", "--app", app],
    )
    current_debug = result.stdout.strip()

    result = runner.run(
        ["heroku", "config:get", "DJB_MODE", "--app", app],
    )
    current_djb_mode = result.stdout.strip()

    # Collect vars that need to be set
    vars_to_set: list[str] = []
    if current_debug != "False":
        vars_to_set.append("DEBUG=False")
    if current_djb_mode != "production":
        vars_to_set.append("DJB_MODE=production")

    if vars_to_set:
        runner.run(
            ["heroku", "config:set", *vars_to_set, "--app", app],
        )
        logger.done(f"Set: {', '.join(vars_to_set)}")
    else:
        logger.done("DEBUG=False, DJB_MODE=production already set")

    # Add Heroku Postgres addon
    if not skip_postgres:
        logger.next("Checking Heroku Postgres addon")

        result = runner.run(
            ["heroku", "addons", "--app", app],
        )
        has_postgres = "heroku-postgresql" in result.stdout

        if has_postgres:
            logger.done("Heroku Postgres already attached")
        else:
            logger.info(f"Heroku Postgres not found. Plan: {postgres_plan}")
            if not heroku_ctx.yes and not click.confirm(
                f"Add heroku-postgresql:{postgres_plan} addon?", default=True
            ):
                logger.skip("Postgres addon")
            else:
                runner.run(
                    ["heroku", "addons:create", f"heroku-postgresql:{postgres_plan}", "--app", app],
                    label="Adding Heroku Postgres",
                    done_msg=f"Heroku Postgres ({postgres_plan}) added",
                )
    else:
        logger.skip("Postgres addon")

    # Set up git remote
    if not skip_remote:
        logger.next("Configuring git remote")

        # Check if heroku remote exists
        result = runner.run(
            ["git", "remote", "get-url", "heroku"],
            cwd=repo_root,
        )

        expected_url = f"https://git.heroku.com/{app}.git"

        if result.returncode == 0:
            current_url = result.stdout.strip()
            if current_url == expected_url:
                logger.done(f"Git remote 'heroku' already configured")
            else:
                # Update existing remote
                runner.run(
                    ["git", "remote", "set-url", "heroku", expected_url],
                    cwd=repo_root,
                )
                logger.done(f"Updated git remote 'heroku' -> {expected_url}")
        else:
            # Add new remote
            runner.run(
                ["git", "remote", "add", "heroku", expected_url],
                cwd=repo_root,
            )
            logger.done(f"Added git remote 'heroku' -> {expected_url}")
    else:
        logger.skip("Git remote configuration")

    logger.note()
    logger.done("Heroku setup complete!")
    logger.note()
    logger.info("Next steps:")
    logger.info("  1. Configure secrets: djb secrets edit production")
    logger.info(f"  2. Deploy: djb deploy heroku")
    logger.tip(f"View app config: heroku config --app {app}")


# Help text shown when no seed_command is configured (for heroku seed)
_HEROKU_SEED_UNCONFIGURED_HELP = """\
Run the host project's seed command on Heroku.

WARNING: This modifies the production database on Heroku!

No seed_command is currently configured. To use this command, first
register your project's seed command:

  djb config seed_command myapp.cli.seed:seed

Then run with --here-be-dragons to confirm:

  djb deploy heroku seed --here-be-dragons

Any additional arguments after -- are passed to the host seed command:

  djb deploy heroku seed --here-be-dragons -- --truncate
"""


class DynamicHelpHerokuSeedCommand(click.Command):
    """A Click command that shows dynamic help based on seed_command configuration."""

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Format help, showing djb options plus host command help if configured."""
        # Get seed_command from config (set up by djb_cli in ctx.obj)
        cli_ctx = ctx.find_object(CliContext)
        seed_command_path = cli_ctx.config.seed_command if cli_ctx else None
        host_command = load_seed_command(seed_command_path) if seed_command_path else None

        if host_command is None:
            # No seed command configured - show configuration instructions
            formatter.write(_HEROKU_SEED_UNCONFIGURED_HELP)
        else:
            # Show djb command's own help first (usage, description, options)
            super().format_help(ctx, formatter)

            # Then append the host command's help
            formatter.write("\n")
            formatter.write(f"Configured seed command: {seed_command_path}\n\n")
            formatter.write("--- Host command help ---\n\n")

            # Get help from host command
            with click.Context(host_command) as host_ctx:
                host_command.format_help(host_ctx, formatter)


@heroku.command(
    "seed",
    cls=DynamicHelpHerokuSeedCommand,
    context_settings={"allow_extra_args": True, "allow_interspersed_args": False},
)
@click.option(
    "--here-be-dragons",
    is_flag=True,
    required=True,
    help="Required safety flag to confirm you want to seed the production database.",
)
@djb_pass_context(CliHerokuContext)
@click.pass_context
def heroku_seed(
    ctx: click.Context,
    heroku_ctx: CliHerokuContext,
    here_be_dragons: bool,  # noqa: ARG001 - required flag, value not used
) -> None:
    """Run seed command on Heroku.

    WARNING: This modifies the production database on Heroku!

    Executes `djb seed` on a Heroku dyno. Requires --here-be-dragons
    flag as a safety measure. Additional arguments are passed through
    to the host project's seed command.

    \b
    Examples:
      djb deploy heroku seed --here-be-dragons
      djb deploy heroku --app myapp seed --here-be-dragons
      djb deploy heroku seed --here-be-dragons -- --truncate
    """
    app = heroku_ctx.app

    # Create runner from context
    runner = heroku_ctx.runner

    # Build command: heroku run --app APP -- djb seed [extra_args...]
    cmd = ["heroku", "run", "--no-notify", "--app", app, "--", "djb", "seed"]
    # Pass through any extra args to djb seed (e.g., --truncate)
    cmd.extend(ctx.args)

    # Run with streaming output
    runner.run(
        cmd,
        label=f"Running seed on Heroku app '{app}'",
        show_output=True,
        fail_msg=click.ClickException(f"Seed failed on '{app}'"),
        done_msg=f"Seed completed on '{app}'",
    )
