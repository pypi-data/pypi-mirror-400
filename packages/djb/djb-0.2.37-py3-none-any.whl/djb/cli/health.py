"""Health check commands for running lint, typecheck, and tests."""

from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, NamedTuple

import click

from djb.cli.context import CliContext, CliHealthContext, djb_pass_context
from djb.config import DjbConfig
from djb.config.validation import get_unrecognized_keys, suppress_unrecognized_key_warnings
from djb.cli.editable import (
    get_djb_source_path,
    is_djb_editable,
    is_djb_package_dir,
)
from djb.cli.docs_check import PathError, validate_paths, validate_toml_paths
from djb.cli.find_overlap import run_find_overlap
from djb.cli.health_barrels import check_all_barrels, fix_all_barrels
from djb.cli.utils.pyproject import has_pytest_cov, has_pytest_xdist
from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.core.logging import get_logger
from djb.cli.utils import TOOL_CHECK_TIMEOUT

logger = get_logger(__name__)


# Timeout for health check steps (in seconds)
# Used for lint, typecheck, and test steps - needs to be long enough for full test runs
HEALTH_STEP_TIMEOUT = 300  # 5 minutes


class HealthStep(NamedTuple):
    """A single health check step to execute."""

    label: str
    cmd: list[str]
    cwd: Path | None = None
    show_output: bool = False  # If True, show output even without -v flag (for test progress)


class ProjectContext(NamedTuple):
    """Context for which projects to run health checks on."""

    djb_path: Path | None  # Path to djb if we should check it
    host_path: Path | None  # Path to host project if we should check it
    inside_djb: bool  # True if running from inside djb directory


class StepFailure(NamedTuple):
    """A failed health check step with captured output."""

    label: str
    returncode: int
    stdout: str
    stderr: str


def _is_inside_djb_dir(path: Path) -> bool:
    """Check if the given path is inside the djb project directory."""
    return is_djb_package_dir(path)


def _get_run_scopes(scope_frontend: bool, scope_backend: bool) -> tuple[bool, bool]:
    """Determine which scopes to run based on flags.

    Args:
        scope_frontend: Whether --frontend flag was set
        scope_backend: Whether --backend flag was set

    Returns:
        Tuple of (run_backend, run_frontend). If neither flag is set, both are True.
    """
    neither_specified = not scope_frontend and not scope_backend
    run_frontend = scope_frontend or neither_specified
    run_backend = scope_backend or neither_specified
    return run_backend, run_frontend


def _get_project_context(config: DjbConfig) -> ProjectContext:
    """Determine which projects to run health checks on.

    Args:
        config: Current DjbConfig instance.

    Returns a ProjectContext with:
    - djb_path: Path to djb if we should check it (editable or inside djb)
    - host_path: Path to host project if we should check it
    - inside_djb: True if running from inside djb directory

    Logic:
    1. If running from inside djb directory: only check djb, skip host
    2. If djb is editable in host project: check djb first, then host
    3. Otherwise: just check the current project (host)
    """
    project_root = config.project_dir

    # Check if we're inside the djb directory
    if _is_inside_djb_dir(project_root):
        return ProjectContext(djb_path=project_root, host_path=None, inside_djb=True)

    # Check if djb is installed in editable mode
    if is_djb_editable(project_root):
        djb_source = get_djb_source_path(project_root)
        if djb_source:
            djb_path = (project_root / djb_source).resolve()
            return ProjectContext(djb_path=djb_path, host_path=project_root, inside_djb=False)

    # Default: just check the host project
    return ProjectContext(djb_path=None, host_path=project_root, inside_djb=False)


def _get_frontend_dir(project_root: Path) -> Path:
    """Get frontend directory path."""
    return project_root / "frontend"


def _get_host_display_name(host_path: Path, config: DjbConfig) -> str:
    """Get the display name for the host project.

    Uses the configured project name if the host path matches the config's project dir,
    otherwise falls back to directory name.

    Args:
        host_path: Path to the host project.
        config: Current DjbConfig instance.
    """
    # Use project_name from config if host_path matches config's project_dir
    if host_path == config.project_dir and config.project_name:
        return config.project_name
    return host_path.name


def _run_steps(
    runner: CmdRunner,
    steps: list[HealthStep],
    quiet: bool = False,
    verbose: bool = False,
) -> list[StepFailure]:
    """Run health check steps and return failures.

    Args:
        runner: CmdRunner instance for executing commands.
        steps: List of health check steps to run
        quiet: Suppress all output
        verbose: Stream output in real-time (shows failures inline)

    Returns:
        List of StepFailure for any failed steps
    """
    failures: list[StepFailure] = []

    for step in steps:
        # Show output if verbose flag or step requests it (e.g., tests)
        should_show = (verbose or step.show_output) and not quiet

        result = runner.run(
            step.cmd,
            cwd=step.cwd,
            label=step.label,
            quiet=quiet,
            show_output=should_show,
        )
        if result.returncode != 0:
            if not quiet:
                logger.fail(f"{step.label} failed (exit {result.returncode})")
                # Show error output if not already shown via show_output
                if not should_show:
                    if result.stdout:
                        logger.info(result.stdout.rstrip())
                    if result.stderr:
                        logger.info(result.stderr.rstrip())
            failures.append(
                StepFailure(step.label, result.returncode, result.stdout, result.stderr)
            )

    return failures


class StepResult(NamedTuple):
    """Result of executing a health check step."""

    step: HealthStep
    failure: StepFailure | None
    duration: float  # seconds


def _run_step_worker(step: HealthStep, runner: CmdRunner) -> StepResult:
    """Execute a single step and return the result.

    This function is designed to be called from a thread pool.
    It always captures output (no streaming) to avoid interleaved output.
    """
    start = time.monotonic()
    try:
        result = runner.run(step.cmd, cwd=step.cwd, timeout=HEALTH_STEP_TIMEOUT)
        duration = time.monotonic() - start
        if result.returncode != 0:
            failure = StepFailure(step.label, result.returncode, result.stdout, result.stderr)
            return StepResult(step, failure, duration)
        return StepResult(step, None, duration)
    except CmdTimeout:
        duration = time.monotonic() - start
        failure = StepFailure(
            step.label,
            1,
            "",
            f"Command timed out after {HEALTH_STEP_TIMEOUT} seconds",
        )
        return StepResult(step, failure, duration)
    except Exception as e:
        duration = time.monotonic() - start
        failure = StepFailure(step.label, 1, "", str(e))
        return StepResult(step, failure, duration)


def _run_steps_parallel(
    steps: list[HealthStep], runner: CmdRunner, quiet: bool = False
) -> tuple[list[StepFailure], dict[str, float]]:
    """Run health check steps in parallel and return failures with timing.

    Args:
        steps: List of health check steps to run
        runner: CmdRunner instance for executing commands
        quiet: Suppress all output

    Returns:
        Tuple of (list of failures, dict of step label to duration in seconds)
    """
    failures: list[StepFailure] = []
    timings: dict[str, float] = {}

    if not steps:
        return failures, timings

    if not quiet:
        logger.info(f"Running {len(steps)} checks in parallel...")

    with ThreadPoolExecutor(max_workers=len(steps)) as executor:
        # Submit all steps
        future_to_step = {executor.submit(_run_step_worker, step, runner): step for step in steps}

        # Collect results as they complete
        for future in as_completed(future_to_step):
            result = future.result()
            timings[result.step.label] = result.duration

            if result.failure:
                if not quiet:
                    logger.fail(f"{result.step.label} failed ({result.duration:.1f}s)")
                    # Show error output immediately
                    if result.failure.stdout:
                        logger.info(result.failure.stdout.rstrip())
                    if result.failure.stderr:
                        logger.info(result.failure.stderr.rstrip())
                failures.append(result.failure)
            elif not quiet:
                logger.done(f"{result.step.label} ({result.duration:.1f}s)")

    return failures, timings


def _get_command_with_flag(
    flag: str, skip_if_present: list[str] | None = None, append: bool = False
) -> str:
    """Construct a command string with a flag added.

    Uses sys.argv to get the original command and adds the flag.
    Always uses 'djb' as the program name regardless of how it was invoked.

    Args:
        flag: The flag to add (e.g., "-v" or "--fix")
        skip_if_present: List of flags that, if already present, skip insertion
        append: If True, append at end (for subcommand flags like --fix).
                If False, insert after 'djb' (for global flags like -v).
    """
    args = sys.argv[:]

    # Replace full path with just 'djb'
    args[0] = "djb"

    # Skip if any of the specified flags are already present
    if skip_if_present and any(f in args for f in skip_if_present):
        return " ".join(args)

    if append:
        # Append at end (for subcommand flags like --fix)
        args.append(flag)
    else:
        # Insert after program name (for global flags like -v)
        if len(args) > 1:
            args.insert(1, flag)
        else:
            args.append(flag)

    return " ".join(args)


def _report_failures(
    failures: list[StepFailure],
    fix: bool = False,
) -> None:
    """Report failures and raise exception if any."""
    if failures:
        logger.info("")
        logger.fail("Health checks completed with failures:")
        for failure in failures:
            logger.fail(f"{failure.label} (exit {failure.returncode})")

        # Show tip for auto-fix if not already using --fix
        if not fix:
            logger.info("")
            fix_cmd = _get_command_with_flag("--fix", skip_if_present=["--fix"], append=True)
            logger.tip(f"re-run with --fix to attempt auto-fixes for lint issues: {fix_cmd}")

        raise click.ClickException("Health checks failed")

    logger.done("Health checks passed")


def _has_ruff(project_root: Path, runner: CmdRunner) -> bool:
    """Check if ruff is available in the project's environment."""
    try:
        result = runner.run(
            ["uv", "run", "ruff", "--version"],
            cwd=project_root,
            timeout=TOOL_CHECK_TIMEOUT,
        )
        return result.returncode == 0
    except CmdTimeout:
        return False


def _build_backend_lint_steps(
    project_root: Path, fix: bool, prefix: str, scope: str, runner: CmdRunner
) -> list[HealthStep]:
    """Build backend lint steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    steps = []

    if fix:
        steps.append(
            HealthStep(
                f"{label_prefix}{scope} format (black)", ["uv", "run", "black", "."], project_root
            )
        )
        if _has_ruff(project_root, runner):
            steps.append(
                HealthStep(
                    f"{label_prefix}{scope} lint fix (ruff check --fix)",
                    ["uv", "run", "ruff", "check", "--fix", "."],
                    project_root,
                )
            )
    else:
        steps.append(
            HealthStep(
                f"{label_prefix}{scope} lint (black --check)",
                ["uv", "run", "black", "--check", "."],
                project_root,
            )
        )
        if _has_ruff(project_root, runner):
            steps.append(
                HealthStep(
                    f"{label_prefix}{scope} lint (ruff check)",
                    ["uv", "run", "ruff", "check", "."],
                    project_root,
                )
            )

    return steps


def _build_backend_typecheck_steps(project_root: Path, prefix: str, scope: str) -> list[HealthStep]:
    """Build backend typecheck steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    return [
        HealthStep(
            f"{label_prefix}{scope} typecheck (pyright)", ["uv", "run", "pyright"], project_root
        )
    ]


def _build_backend_test_steps(
    project_root: Path,
    prefix: str,
    scope: str,
    runner: CmdRunner,
    cov: bool = False,
    parallel: bool = True,
    e2e: bool = True,
    verbose: bool = False,
) -> list[HealthStep]:
    """Build backend test steps for a project."""
    label_prefix = f"{prefix} " if prefix else ""
    cmd = ["uv", "run", "pytest"]
    label_parts = []

    # Add verbose flag to show test names as they run
    if verbose:
        cmd.append("-v")

    if parallel:
        if has_pytest_xdist(runner, project_root):
            cmd.extend(["-n", "auto", "--dist", "worksteal"])
        else:
            logger.warning(
                f"pytest-xdist not installed in {project_root.name}, "
                "running tests sequentially. Run: uv add --dev pytest-xdist"
            )

    if not e2e:
        cmd.append("--no-e2e")
        label_parts.append("no E2E")

    if cov:
        if has_pytest_cov(runner, project_root):
            cmd.extend(["--cov", "--cov-report=term-missing"])
            label_parts.append("coverage")
        else:
            logger.notice(
                f"pytest-cov not installed in {project_root.name}, "
                "skipping coverage. Run: uv add --dev pytest-cov"
            )

    label_suffix = f" ({', '.join(label_parts)})" if label_parts else ""
    return [
        HealthStep(
            f"{label_prefix}{scope} tests (pytest{label_suffix})",
            cmd,
            project_root,
            show_output=True,  # Show test progress in real-time
        )
    ]


def _build_frontend_lint_steps(frontend_dir: Path, fix: bool, prefix: str = "") -> list[HealthStep]:
    """Build frontend lint steps for a project."""
    if not frontend_dir.exists():
        return []
    label_prefix = f"{prefix} " if prefix else ""
    if fix:
        return [
            HealthStep(
                f"{label_prefix}Frontend lint (bun lint --fix)",
                ["bun", "run", "lint", "--fix"],
                frontend_dir,
            )
        ]
    return [
        HealthStep(f"{label_prefix}Frontend lint (bun lint)", ["bun", "run", "lint"], frontend_dir)
    ]


def _build_frontend_typecheck_steps(frontend_dir: Path, prefix: str = "") -> list[HealthStep]:
    """Build frontend typecheck steps for a project."""
    if not frontend_dir.exists():
        return []
    label_prefix = f"{prefix} " if prefix else ""
    return [
        HealthStep(f"{label_prefix}Frontend typecheck (tsc)", ["bun", "run", "tsc"], frontend_dir)
    ]


def _build_frontend_test_steps(frontend_dir: Path, prefix: str = "") -> list[HealthStep]:
    """Build frontend test steps for a project."""
    if not frontend_dir.exists():
        return []
    label_prefix = f"{prefix} " if prefix else ""
    return [
        HealthStep(
            f"{label_prefix}Frontend tests (bun test)",
            ["bun", "test"],
            frontend_dir,
            show_output=True,  # Show test progress in real-time
        )
    ]


# Type alias for step builder callbacks used by _run_for_projects
StepBuilder = Callable[[Path, str, bool, CmdRunner], list[HealthStep]]


def _run_for_projects(
    health_ctx: CliHealthContext,
    build_steps: StepBuilder,
    section_name: str,
    fix: bool = False,
) -> None:
    """Run a health subcommand across djb and host projects.

    This helper extracts the common pattern shared by lint, typecheck, and test
    subcommands. Each subcommand follows the same structure:
    1. Check for djb (editable) and run steps if present
    2. Check for host project and run steps if present
    3. Report failures

    Args:
        health_ctx: CLI health context with verbose/quiet flags and config.
        build_steps: Callback that takes (path, prefix, is_djb) and returns steps.
            - path: Project root path
            - prefix: Label prefix like "[djb]" or "[host_name]"
            - is_djb: True if building steps for djb, False for host project
        section_name: Name for logging sections (e.g., "lint", "typecheck").
        fix: Whether --fix flag is enabled (for _report_failures tip).
    """
    # Suppress load-time warnings for entire run (tests may load config)
    with suppress_unrecognized_key_warnings():
        _run_for_projects_impl(health_ctx, build_steps, section_name, fix)


def _run_for_projects_impl(
    health_ctx: CliHealthContext,
    build_steps: StepBuilder,
    section_name: str,
    fix: bool = False,
) -> None:
    """Implementation of _run_for_projects."""
    verbose = health_ctx.verbose
    quiet = health_ctx.quiet
    config = health_ctx.config
    project_ctx = _get_project_context(config)
    runner = health_ctx.runner
    all_failures: list[StepFailure] = []

    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if prefix and not quiet:
            logger.section(f"Running {section_name} for djb (editable)")
        steps = build_steps(project_ctx.djb_path, prefix, True, runner)
        all_failures.extend(_run_steps(runner, steps, quiet, verbose))

    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path, config)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if prefix and not quiet:
            logger.section(f"Running {section_name} for {host_name}")
        steps = build_steps(project_ctx.host_path, prefix, False, runner)
        all_failures.extend(_run_steps(runner, steps, quiet, verbose))

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    _report_failures(all_failures, fix=fix)


@click.group(invoke_without_command=True)
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to auto-fix lint/format issues.",
)
@click.option(
    "--cov",
    is_flag=True,
    help="Enable code coverage reporting for tests.",
)
@click.option(
    "--parallel/--no-parallel",
    default=True,
    help="Run health checks in parallel (default: enabled).",
)
@click.option(
    "--e2e/--no-e2e",
    default=True,
    help="Include E2E tests (default: enabled).",
)
@djb_pass_context
@click.pass_context
def health(
    ctx: click.Context, cli_ctx: CliContext, fix: bool, cov: bool, parallel: bool, e2e: bool
):
    """Run health checks: lint, typecheck, and tests.

    \b
    When run without a subcommand, executes all checks:
      * Linting (black for backend, bun lint for frontend)
      * Type checking (pyright for backend, tsc for frontend)
      * Tests (pytest for backend, bun test for frontend)

    E2E tests are included by default. Use --no-e2e to skip them.

    \b
    Subcommands:
      lint       Run linting only
      typecheck  Run type checking only
      test       Run tests only

    \b
    Examples:
      djb health                    # Run all checks (parallel)
      djb health --no-e2e           # Run all checks without E2E tests
      djb health --no-parallel      # Run checks sequentially
      djb --backend health          # Backend checks only
      djb --frontend health         # Frontend checks only
      djb health lint --fix         # Run linting with auto-fix
      djb health typecheck          # Type checking only
      djb health test               # Tests only (includes E2E)
      djb health test --no-e2e      # Tests without E2E
      djb health test --cov         # Tests with coverage
      djb -v health                 # Show error details on failure
    """
    # Specialize context for health subcommands
    health_ctx = CliHealthContext()
    health_ctx.__dict__.update(cli_ctx.__dict__)
    health_ctx.fix = fix
    health_ctx.cov = cov
    health_ctx.parallel = parallel
    health_ctx.e2e = e2e
    ctx.obj = health_ctx

    # If no subcommand, run all checks
    if ctx.invoked_subcommand is None:
        _run_all_checks(health_ctx)


class ProjectCheckResult(NamedTuple):
    """Result of running health checks on a single project."""

    failures: list[StepFailure]
    config_errors: list[str]
    docs_errors: list[PathError]


def _run_project_checks(
    health_ctx: CliHealthContext,
    project_root: Path,
    prefix: str,
    scope: str,
) -> ProjectCheckResult:
    """Run all health checks for a single project.

    Runs checks in order: docs -> lint/typecheck -> tests.
    All checks for this project complete before returning.
    """
    # Extract config fields from context
    fix = health_ctx.fix
    cov = health_ctx.cov
    parallel = health_ctx.parallel
    e2e = health_ctx.e2e
    verbose = health_ctx.verbose
    quiet = health_ctx.quiet
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)
    runner = health_ctx.runner

    failures: list[StepFailure] = []
    docs_errors: list[PathError] = []
    frontend_dir = _get_frontend_dir(project_root)

    # 1. Config validation (fast, Python-native)
    config_errors: list[str] = []
    if run_backend:
        # Create config for this project (may differ from health_ctx.config.project_dir
        # when validating editable djb)
        # Suppress warnings during load - _validate_project_config reports them as errors
        with suppress_unrecognized_key_warnings():
            project_config = health_ctx.config.augment(
                DjbConfig(project_dir=project_root),
            )
        config_errors = _validate_project_config(prefix, project_config)

    # 2. Docs validation (fast, Python-native)
    if run_backend:
        project_docs_errors = _validate_project_docs(project_root, quiet)
        if project_docs_errors and not quiet:
            logger.fail("Documentation path validation failed:")
            for error in project_docs_errors:
                logger.fail(
                    f"  {error.source_file}:{error.line_number}: " f"path not found: {error.path}"
                )
        elif not quiet:
            logger.done(f"{prefix} Docs validated" if prefix else "Docs validated")
        docs_errors.extend(project_docs_errors)

    # 3. Collect lint/typecheck steps (fast steps)
    fast_steps: list[HealthStep] = []
    if run_backend:
        fast_steps.extend(
            _build_backend_lint_steps(project_root, fix, prefix, scope=scope, runner=runner)
        )
        fast_steps.extend(_build_backend_typecheck_steps(project_root, prefix, scope=scope))
    if run_frontend:
        fast_steps.extend(_build_frontend_lint_steps(frontend_dir, fix, prefix))
        fast_steps.extend(_build_frontend_typecheck_steps(frontend_dir, prefix))

    # 3. Collect test steps
    test_steps: list[HealthStep] = []
    if run_backend:
        test_steps.extend(
            _build_backend_test_steps(
                project_root,
                prefix,
                scope=scope,
                runner=runner,
                cov=cov,
                parallel=parallel,
                e2e=e2e,
                verbose=verbose,
            )
        )
    if run_frontend:
        test_steps.extend(_build_frontend_test_steps(frontend_dir, prefix))

    # 4. Execute steps
    if parallel and len(fast_steps) > 1:
        # Run lint/typecheck in parallel
        step_failures, _ = _run_steps_parallel(fast_steps, runner, quiet)
        failures.extend(step_failures)
    else:
        failures.extend(_run_steps(runner, fast_steps, quiet, verbose))

    # Run tests sequentially with streaming
    failures.extend(_run_steps(runner, test_steps, quiet, verbose=True))

    return ProjectCheckResult(failures, config_errors, docs_errors)


def _run_all_checks(health_ctx: CliHealthContext) -> None:
    """Run all health checks."""
    # Suppress load-time warnings for entire health check run (tests may load config)
    with suppress_unrecognized_key_warnings():
        _run_all_checks_impl(health_ctx)


def _run_all_checks_impl(health_ctx: CliHealthContext) -> None:
    """Run all health checks (implementation)."""
    quiet = health_ctx.quiet
    config = health_ctx.config

    project_ctx = _get_project_context(config)
    total_start = time.monotonic()
    all_failures: list[StepFailure] = []
    all_config_errors: list[str] = []
    all_docs_errors: list[PathError] = []

    # Run checks for djb first (if editable)
    if project_ctx.djb_path:
        if project_ctx.host_path and not quiet:
            logger.section("Running health checks for djb (editable)")

        result = _run_project_checks(
            health_ctx,
            project_root=project_ctx.djb_path,
            prefix="[djb]" if project_ctx.host_path else "",
            scope="Python",
        )
        all_failures.extend(result.failures)
        all_config_errors.extend(result.config_errors)
        all_docs_errors.extend(result.docs_errors)

    # Run checks for host project
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path, config)
        if project_ctx.djb_path and not quiet:
            logger.section(f"Running health checks for {host_name}")

        result = _run_project_checks(
            health_ctx,
            project_root=project_ctx.host_path,
            prefix=f"[{host_name}]" if project_ctx.djb_path else "",
            scope="Backend",
        )
        all_failures.extend(result.failures)
        all_config_errors.extend(result.config_errors)
        all_docs_errors.extend(result.docs_errors)

    # Show skip message if inside djb
    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    # Report timing
    total_duration = time.monotonic() - total_start
    if not quiet:
        logger.info("")
        logger.info(f"Completed in {total_duration:.1f}s")

    # Include config errors in failure count
    if all_config_errors:
        config_output = "\n".join(all_config_errors)
        all_failures.append(StepFailure("Config validation", 1, config_output, ""))

    # Include docs errors in failure count
    if all_docs_errors:
        docs_output = "\n".join(
            f"{e.source_file}:{e.line_number}: {e.path}" for e in all_docs_errors
        )
        all_failures.append(StepFailure("Docs validation", 1, docs_output, ""))

    _report_failures(all_failures, health_ctx.fix)


@health.command()
@click.option("--fix", is_flag=True, help="Attempt to auto-fix lint issues.")
@djb_pass_context(CliHealthContext)
def lint(health_ctx: CliHealthContext, fix: bool):
    """Run linting checks.

    Backend: black (--check unless --fix)
    Frontend: bun run lint
    """
    fix = fix or health_ctx.fix
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)

    def build_steps(path: Path, prefix: str, is_djb: bool, runner: CmdRunner) -> list[HealthStep]:
        steps: list[HealthStep] = []
        frontend_dir = _get_frontend_dir(path)
        scope = "Python" if is_djb else "Backend"
        if run_backend:
            steps.extend(_build_backend_lint_steps(path, fix, prefix, scope=scope, runner=runner))
        if run_frontend:
            steps.extend(_build_frontend_lint_steps(frontend_dir, fix, prefix))
        return steps

    _run_for_projects(health_ctx, build_steps, "lint", fix=fix)


@health.command()
@djb_pass_context(CliHealthContext)
def typecheck(health_ctx: CliHealthContext):
    """Run type checking.

    Backend: pyright
    Frontend: bun run tsc
    """
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)

    def build_steps(path: Path, prefix: str, is_djb: bool, runner: CmdRunner) -> list[HealthStep]:
        del runner  # Unused but required by StepBuilder signature
        steps: list[HealthStep] = []
        frontend_dir = _get_frontend_dir(path)
        scope = "Python" if is_djb else "Backend"
        if run_backend:
            steps.extend(_build_backend_typecheck_steps(path, prefix, scope=scope))
        if run_frontend:
            steps.extend(_build_frontend_typecheck_steps(frontend_dir, prefix))
        return steps

    _run_for_projects(health_ctx, build_steps, "typecheck")


@health.group(invoke_without_command=True)
@click.option("--cov/--no-cov", default=False, help="Enable/disable code coverage reporting.")
@click.option(
    "--e2e/--no-e2e", default=None, help="Include/exclude E2E tests (inherits from parent)."
)
@djb_pass_context(CliHealthContext)
@click.pass_context
def test(ctx: click.Context, health_ctx: CliHealthContext, cov: bool, e2e: bool | None):
    """Run tests.

    Backend: pytest (includes E2E tests by default)
    Frontend: bun test

    Use --cov to enable code coverage reporting.
    Use --no-e2e to skip E2E tests.

    Subcommands:
        overlap    Find tests with overlapping coverage
    """
    # If a subcommand was invoked, don't run the default behavior
    if ctx.invoked_subcommand is not None:
        return
    # Combine local flags with parent flags from health group
    cov = cov or health_ctx.cov
    e2e = e2e if e2e is not None else health_ctx.e2e
    run_backend, run_frontend = _get_run_scopes(health_ctx.scope_frontend, health_ctx.scope_backend)

    def build_steps(path: Path, prefix: str, is_djb: bool, runner: CmdRunner) -> list[HealthStep]:
        steps: list[HealthStep] = []
        frontend_dir = _get_frontend_dir(path)
        scope = "Python" if is_djb else "Backend"
        if run_backend:
            steps.extend(
                _build_backend_test_steps(
                    path,
                    prefix,
                    scope=scope,
                    runner=runner,
                    cov=cov,
                    parallel=health_ctx.parallel,
                    e2e=e2e,
                    verbose=health_ctx.verbose,
                )
            )
        if run_frontend:
            steps.extend(_build_frontend_test_steps(frontend_dir, prefix))
        return steps

    _run_for_projects(health_ctx, build_steps, "tests")


@test.command("overlap")
@click.option(
    "--min-similarity",
    type=float,
    default=0.95,
    help="Minimum Jaccard similarity to report (0-1, default: 0.95)",
)
@click.option(
    "--show-pairs",
    is_flag=True,
    help="Show all overlapping test pairs instead of parametrization groups.",
)
@click.option(
    "-p",
    "--package",
    "packages",
    multiple=True,
    help="Package(s) to analyze (can be specified multiple times). Defaults to 'src'.",
)
@djb_pass_context(CliHealthContext)
def overlap(
    health_ctx: CliHealthContext, min_similarity: float, show_pairs: bool, packages: tuple[str, ...]
):
    """Find tests with overlapping coverage for potential consolidation.

    Collects per-test coverage data and identifies tests in the same class
    that cover the same code paths. These are candidates for consolidation
    using @pytest.mark.parametrize.

    Examples:
        djb health test overlap
        djb health test overlap -p src/djb/cli -p src/djb/core
        djb health test overlap --min-similarity 0.90
    """
    project_ctx = _get_project_context(health_ctx.config)
    project_root = project_ctx.djb_path or project_ctx.host_path

    if not project_root:
        raise click.ClickException("No project directory found")

    runner = health_ctx.runner
    run_find_overlap(project_root, runner, min_similarity, show_pairs, list(packages) or None)


def _find_markdown_files(project_root: Path) -> list[Path]:
    """Find markdown files to validate in a project.

    Returns markdown files in:
    - Project root directory (AGENTS.md, README.md, etc.)
    - docs/ directory recursively (docs/**/*.md)

    Excludes:
    - docs/plans/ - plan files contain speculative/proposed paths
    - docs/todo/ - auto-generated agent reports with code snippets

    Follows symlinks to avoid duplicates (e.g., CLAUDE.md -> AGENTS.md).
    """
    markdown_files: list[Path] = []
    seen_targets: set[Path] = set()

    # Root-level markdown files
    for md_file in project_root.glob("*.md"):
        target = md_file.resolve()
        if target in seen_targets:
            continue
        seen_targets.add(target)
        markdown_files.append(md_file)

    # Nested docs directory
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        for md_file in docs_dir.rglob("*.md"):
            # Skip excluded directories
            parts = md_file.parts
            # Skip plan files - they contain speculative/proposed paths
            if "plans" in parts:
                continue
            # Skip auto-generated agent reports with code snippets
            if "todo" in parts:
                continue
            target = md_file.resolve()
            if target in seen_targets:
                continue
            seen_targets.add(target)
            markdown_files.append(md_file)

    return sorted(markdown_files)


def _find_toml_files(project_root: Path) -> list[Path]:
    """Find TOML files to validate in docs/todo/.

    Excludes lock files (*.lock).
    """
    todo_dir = project_root / "docs" / "todo"
    if not todo_dir.exists():
        return []

    toml_files = []
    for toml_file in todo_dir.glob("*.toml"):
        # Skip lock files
        if toml_file.suffix == ".lock" or toml_file.name.endswith(".toml.lock"):
            continue
        toml_files.append(toml_file)

    return sorted(toml_files)


def _validate_project_config(prefix: str, config: DjbConfig) -> list[str]:
    """Validate config files for unrecognized keys.

    Args:
        prefix: Prefix for output (e.g., "[djb]")
        config: Config to validate (with project_dir set to the project being checked).
            Caller should wrap config creation with suppress_unrecognized_key_warnings() since this
            function reports unrecognized keys as structured errors.

    Returns:
        List of error messages for unrecognized keys
    """
    errors: list[str] = []
    quiet = config.quiet

    unrecognized = get_unrecognized_keys(config, type(config))

    if not unrecognized:
        if not quiet:
            msg = "Config validated"
            if prefix:
                msg = f"{prefix} {msg}"
            logger.done(msg)
        return []

    # Collect and report errors
    for file_label, keys in unrecognized.items():
        for key in keys:
            error_msg = f"{file_label}: {key}"
            errors.append(error_msg)
            if not quiet:
                msg = f"Unrecognized config key '{key}' in {file_label}"
                if prefix:
                    msg = f"{prefix} {msg}"
                logger.fail(msg)

    return errors


def _validate_project_docs(project_root: Path, quiet: bool = False) -> list[PathError]:
    """Validate all documentation files in a project.

    Validates:
    - Markdown files (*.md in root and docs/**/*)
    - TOML task files (docs/todo/*.toml)

    Args:
        project_root: Root directory of the project
        quiet: Suppress output

    Returns:
        List of PathError for paths that don't exist
    """
    all_errors: list[PathError] = []

    # Validate markdown files
    markdown_files = _find_markdown_files(project_root)
    for md_file in markdown_files:
        errors = validate_paths(project_root, md_file)
        all_errors.extend(errors)

    # Validate TOML files
    toml_files = _find_toml_files(project_root)
    for toml_file in toml_files:
        errors = validate_toml_paths(project_root, toml_file)
        all_errors.extend(errors)

    if not markdown_files and not toml_files and not quiet:
        logger.notice(f"No documentation files found in {project_root}")

    return all_errors


@health.command()
@djb_pass_context(CliHealthContext)
def docs(health_ctx: CliHealthContext):
    """Validate documentation path references.

    Checks that file paths referenced in documentation files exist.
    This prevents stale references after refactoring.

    Validates:
    - Markdown files (*.md in root and docs/**/*)
      - Markdown links: [text](path)
      - Inline code paths: `path/to/file.py`
    - TOML task files (docs/todo/*.toml)
      - File references: files = ["path:line"]
    """
    quiet = health_ctx.quiet
    config = health_ctx.config
    project_ctx = _get_project_context(config)
    all_errors: list[PathError] = []

    if project_ctx.djb_path:
        if project_ctx.host_path and not quiet:
            logger.section("Validating docs for djb (editable)")
        errors = _validate_project_docs(project_ctx.djb_path, quiet)
        if errors and not quiet:
            logger.fail("Documentation path validation failed:")
            for error in errors:
                logger.fail(
                    f"  {error.source_file}:{error.line_number}: " f"path not found: {error.path}"
                )
        elif not quiet:
            logger.done("Documentation paths validated")
        all_errors.extend(errors)

    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path, config)
        if project_ctx.djb_path and not quiet:
            logger.section(f"Validating docs for {host_name}")
        errors = _validate_project_docs(project_ctx.host_path, quiet)
        if errors and not quiet:
            logger.fail("Documentation path validation failed:")
            for error in errors:
                logger.fail(
                    f"  {error.source_file}:{error.line_number}: " f"path not found: {error.path}"
                )
        elif not quiet:
            logger.done("Documentation paths validated")
        all_errors.extend(errors)

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    if all_errors:
        raise click.ClickException("Documentation validation failed")


@health.command()
@click.option("--fix", is_flag=True, help="Auto-fix barrel listings in markdown files.")
@djb_pass_context(CliHealthContext)
def barrels(health_ctx: CliHealthContext, fix: bool):
    """Validate barrel export listings in markdown documentation.

    Checks that barrel export listings in markdown files match the actual
    exports in the source files they reference.

    \b
    Barrel format detected:
        **Label** [`path/to/file`]: `export1`, `export2`, ...

    \b
    Supported source files:
        - Python: reads __all__ from barrel files
        - TypeScript: reads export { } statements

    Use --fix to automatically update markdown files with correct exports.
    """
    quiet = health_ctx.quiet
    config = health_ctx.config
    project_ctx = _get_project_context(config)
    has_discrepancies = False

    def _run_barrels_check(project_root: Path, prefix: str) -> bool:
        """Run barrel check for a project. Returns True if discrepancies found."""
        results = check_all_barrels(project_root)

        if not results:
            if not quiet:
                logger.notice(
                    f"{prefix}No barrel listings found" if prefix else "No barrel listings found"
                )
            return False

        total_listings = sum(len(listings) for listings, _ in results.values())
        total_discrepancies = sum(len(discrepancies) for _, discrepancies in results.values())

        if not quiet:
            msg = f"Found {total_listings} barrel listing(s) in {len(results)} file(s)"
            if prefix:
                msg = f"{prefix} {msg}"
            logger.info(msg)

        if total_discrepancies == 0:
            if not quiet:
                logger.done(
                    f"{prefix}All barrel listings in sync"
                    if prefix
                    else "All barrel listings in sync"
                )
            return False

        # Report discrepancies
        if not quiet:
            for md_path, (listings, discrepancies) in results.items():
                if not discrepancies:
                    continue
                relative_path = md_path.relative_to(project_root)
                for d in discrepancies:
                    if d.missing:
                        logger.fail(f"  {relative_path}: {d.label} missing: {', '.join(d.missing)}")
                    if d.extra:
                        logger.fail(f"  {relative_path}: {d.label} extra: {', '.join(d.extra)}")

        return True

    def _run_barrels_fix(project_root: Path, prefix: str) -> int:
        """Fix barrel listings for a project. Returns number of listings fixed."""
        results = fix_all_barrels(project_root)
        total_fixed = sum(results.values())

        if total_fixed > 0 and not quiet:
            for md_path, count in results.items():
                relative_path = md_path.relative_to(project_root)
                msg = f"Updated {relative_path} ({count} listing(s) fixed)"
                if prefix:
                    msg = f"{prefix} {msg}"
                logger.done(msg)

        return total_fixed

    # Run for djb if present
    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if project_ctx.host_path and not quiet:
            logger.section("Checking barrels for djb (editable)")

        if fix:
            _run_barrels_fix(project_ctx.djb_path, prefix)
        else:
            if _run_barrels_check(project_ctx.djb_path, prefix):
                has_discrepancies = True

    # Run for host project if present
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path, config)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if project_ctx.djb_path and not quiet:
            logger.section(f"Checking barrels for {host_name}")

        if fix:
            _run_barrels_fix(project_ctx.host_path, prefix)
        else:
            if _run_barrels_check(project_ctx.host_path, prefix):
                has_discrepancies = True

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    if has_discrepancies and not fix:
        if not quiet:
            fix_cmd = _get_command_with_flag("--fix", skip_if_present=["--fix"], append=True)
            logger.tip(f"Run with --fix to update: {fix_cmd}")
        raise click.ClickException("Barrel listings out of sync")


@health.command("config")
@djb_pass_context(CliHealthContext)
def config_check(health_ctx: CliHealthContext):
    """Validate configuration files.

    Checks for unrecognized keys in config files that may indicate
    typos or outdated configuration.

    \b
    Validates:
    - .djb/project.toml
    - .djb/local.toml
    - pyproject.toml[tool.djb]
    """
    quiet = health_ctx.quiet
    config = health_ctx.config
    project_ctx = _get_project_context(config)
    has_errors = False

    def _check_config(project_root: "Path", prefix: str) -> bool:
        """Check config for a project. Returns True if errors found."""
        # Load a fresh config for this project to check (suppress warnings during load)
        # Uses augment() to preserve CLI overrides from parent command
        with suppress_unrecognized_key_warnings():
            override_config = DjbConfig(project_dir=project_root)
            check_config = config.augment(override_config)

        unrecognized = get_unrecognized_keys(check_config, type(check_config))

        if not unrecognized:
            if not quiet:
                msg = "Configuration valid"
                if prefix:
                    msg = f"{prefix} {msg}"
                logger.done(msg)
            return False

        # Report errors
        if not quiet:
            for file_label, keys in unrecognized.items():
                for key in keys:
                    msg = f"Unrecognized config key '{key}' in {file_label}"
                    if prefix:
                        msg = f"{prefix} {msg}"
                    logger.fail(msg)

        return True

    # Run for djb if present
    if project_ctx.djb_path:
        prefix = "[djb]" if project_ctx.host_path else ""
        if project_ctx.host_path and not quiet:
            logger.section("Checking config for djb (editable)")

        if _check_config(project_ctx.djb_path, prefix):
            has_errors = True

    # Run for host project if present
    if project_ctx.host_path:
        host_name = _get_host_display_name(project_ctx.host_path, config)
        prefix = f"[{host_name}]" if project_ctx.djb_path else ""
        if project_ctx.djb_path and not quiet:
            logger.section(f"Checking config for {host_name}")

        if _check_config(project_ctx.host_path, prefix):
            has_errors = True

    if project_ctx.inside_djb and project_ctx.host_path is None and not quiet:
        logger.notice("Running from djb directory, skipping host project checks.")

    if has_errors:
        raise click.ClickException("Configuration validation failed")
