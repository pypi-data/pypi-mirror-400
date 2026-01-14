"""CLI context for passing global options to subcommands."""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar, overload

import click

from djb.config.storage import LocalConfigIO, ProjectConfigType
from djb.config.storage.base import ConfigStore

from djb.core.cmd_runner import CmdRunner
from djb.machine_state import SearchStrategy

if TYPE_CHECKING:
    from djb.config import DjbConfig

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T", bound="CliContext")


@dataclass
class CliContext:
    """Context object passed through click's ctx.obj.

    This dataclass holds global CLI options that any subcommand can access.
    Use ctx.ensure_object(CliContext) in the main CLI group and access
    values via ctx.obj.<field_name> in subcommands.

    Subcommand groups can specialize the context by:
    1. Saving the parent context: `parent_ctx = ctx.obj`
    2. Creating their specialized context: `ctx.obj = CliHealthContext()`
    3. Copying parent fields: `ctx.obj.__dict__.update(parent_ctx.__dict__)`
    4. Setting specialized fields: `ctx.obj.fix = fix`

    Example:
        @pass_context
        def my_command(cli_ctx: CliContext):
            project_dir = cli_ctx.config.project_dir
    """

    # Global options (set by djb_cli)
    verbose: bool = False
    quiet: bool = False
    yes: bool = False

    # Config is set by djb_cli before any subcommand runs.
    # Typed as DjbConfig for IDE support; default None for dataclass machinery.
    config: "DjbConfig" = field(default=None)  # type: ignore[assignment]

    # Scope options (useful for multiple commands)
    scope_frontend: bool = False
    scope_backend: bool = False

    # Internal invocation tracking - set by invoke_subcommand() helper
    _invoked_by: str | None = field(default=None, repr=False)

    # Machine state options
    search_strategy: SearchStrategy = SearchStrategy.AUTO

    @cached_property
    def runner(self) -> CmdRunner:
        """Lazily create a CmdRunner with the context's verbosity setting."""
        return CmdRunner(verbose=self.verbose)


@dataclass
class CliHealthContext(CliContext):
    """Specialized context for `djb health` command group.

    Inherits all global options from CliContext and adds health-specific options.
    """

    fix: bool = False
    cov: bool = False
    parallel: bool = True
    e2e: bool = True  # Include E2E tests by default


@dataclass(kw_only=True)
class CliHerokuContext(CliContext):
    """Specialized context for `djb deploy heroku` command group.

    Inherits all global options from CliContext and adds heroku-specific options.
    """

    # App is resolved by _resolve_heroku_app callback (from --app or config.project_name)
    app: str


@dataclass
class CliConfigContext(CliContext):
    """Specialized context for `djb config` command group.

    Inherits all global options from CliContext and adds config-specific options
    for controlling which config file to write to.
    """

    target_project: bool = False
    target_local: bool = False

    @property
    def target_store(self) -> type[ConfigStore] | None:
        """Get the target store class from flags, or None if not specified.

        Returns a class, not an instance. Caller should instantiate with ctx.

        Raises:
            click.ClickException: If both --project and --local are specified.
        """
        if self.target_project and self.target_local:
            raise click.ClickException("Cannot specify both --project and --local")
        if self.target_project:
            return ProjectConfigType
        if self.target_local:
            return LocalConfigIO
        return None


@dataclass
class CliK8sContext(CliContext):
    """Specialized context for `djb deploy k8s` command group.

    Extends CliContext with K8s-specific fields like SSH host configuration
    and deployment behavior flags.
    """

    # SSH target
    host: str | None = None
    port: int = 22
    ssh_key: Path | None = None

    # Behavior flags
    skip_build: bool = False
    skip_migrate: bool = False
    skip_secrets: bool = False


@overload
def djb_pass_context() -> Callable[[Callable[..., R]], Callable[..., R]]: ...


@overload
def djb_pass_context(ctx_type: type[T]) -> Callable[[Callable[..., R]], Callable[..., R]]: ...


@overload
def djb_pass_context(ctx_type: Callable[..., R]) -> Callable[..., R]: ...


def djb_pass_context(
    ctx_type: type[T] | Callable[..., R] | None = None,
) -> Callable[[Callable[..., R]], Callable[..., R]] | Callable[..., R]:
    """Decorator that passes a context object as the first argument to a command.

    Can be used with or without parentheses:

        @click.command()
        @pass_context  # Uses CliContext (default)
        def my_command(cli_ctx: CliContext):
            project_dir = cli_ctx.config.project_dir

        @health.command()
        @pass_context(CliHealthContext)  # Uses CliHealthContext
        def lint(health_ctx: CliHealthContext):
            fix = health_ctx.fix

    Args:
        ctx_type: The context class to expect (default: CliContext).
            When used without parentheses, this is the decorated function.
    """
    # Handle @pass_context without parentheses (ctx_type is the function)
    if ctx_type is not None and callable(ctx_type) and not isinstance(ctx_type, type):
        f = ctx_type
        return _make_context_wrapper(f, CliContext)

    # Handle @pass_context() or @pass_context(SomeContextClass)
    actual_type: type[CliContext] = ctx_type if isinstance(ctx_type, type) else CliContext

    def decorator(f: Callable[..., R]) -> Callable[..., R]:
        return _make_context_wrapper(f, actual_type)

    return decorator


def _make_context_wrapper(f: Callable[..., R], ctx_type: type[T]) -> Callable[..., R]:
    """Create a wrapper that passes the context to the function."""

    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        ctx = click.get_current_context()
        cli_ctx = ctx.obj
        assert isinstance(cli_ctx, ctx_type), f"Expected {ctx_type.__name__} at ctx.obj"
        return f(cli_ctx, *args, **kwargs)

    return wrapper


def invoke_subcommand(ctx: click.Context, cmd: click.Command, **kwargs: object) -> None:
    """Invoke a Click command as an internal subcommand.

    Use this instead of ctx.invoke() when you want the invoked command
    to know it was called programmatically (not from CLI).

    The invoked command can check is_invoked_standalone() to determine
    whether to show "Next steps" messages or other CLI-only output.

    Example:
        # In deploy_k8s command:
        invoke_subcommand(ctx, terraform, host=host, port=port)

        # In terraform command:
        if is_invoked_standalone(ctx):
            logger.info("Next steps: ...")

    Args:
        ctx: The Click context
        cmd: The Click command to invoke
        **kwargs: Arguments to pass to the command
    """
    cli_ctx = ctx.obj
    if isinstance(cli_ctx, CliContext):
        cli_ctx._invoked_by = ctx.info_name
    ctx.invoke(cmd, **kwargs)


def is_invoked_standalone(ctx: click.Context) -> bool:
    """Check if the current command was invoked from CLI (not programmatically).

    Returns True if the command was invoked directly from the CLI.
    Returns False if the command was invoked via invoke_subcommand().

    Example:
        @click.command()
        @click.pass_context
        def my_command(ctx):
            if is_invoked_standalone(ctx):
                logger.info("Next steps: ...")

    Args:
        ctx: The Click context

    Returns:
        True if standalone CLI invocation, False if programmatic
    """
    cli_ctx = ctx.obj
    if isinstance(cli_ctx, CliContext):
        return cli_ctx._invoked_by is None
    return True  # Default to standalone if context is not CliContext
