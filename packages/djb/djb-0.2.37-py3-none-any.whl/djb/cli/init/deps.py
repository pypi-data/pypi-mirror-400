"""djb init deps - Install system and package dependencies."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from djb.cli.context import djb_pass_context
from djb.cli.init.shared import InitContext
from djb.cli.utils import CmdRunner
from djb.cli.utils.pyproject import get_dependency_groups
from djb.core.logging import get_logger

logger = get_logger(__name__)


def install_brew_dependencies(runner: CmdRunner, *, skip: bool = False) -> None:
    """Install system dependencies via Homebrew.

    Args:
        runner: CmdRunner instance for executing commands.
        skip: If True, skip installation entirely.
    """
    is_brew_supported = sys.platform in ("darwin", "linux")

    if skip:
        logger.skip("System dependency installation")
        return

    if not is_brew_supported:
        logger.skip("Homebrew installation (not supported on this platform)")
        logger.info("Please install dependencies manually:")
        logger.info("  - SOPS: https://github.com/getsops/sops")
        logger.info("  - age: https://age-encryption.org/")
        logger.info("  - GnuPG: https://gnupg.org/")
        logger.info("  - PostgreSQL 17: https://www.postgresql.org/")
        logger.info("  - GDAL: https://gdal.org/")
        logger.info("  - Bun: https://bun.sh/")
        return

    logger.next("Checking system dependencies")

    if not runner.check(["which", "brew"]):
        logger.error("Homebrew not found. Please install from https://brew.sh/")
        raise click.ClickException("Homebrew is required for automatic dependency installation")

    # Check which tools need to be installed using 'which'
    # instead of 'brew list' (slow)
    tools_to_install: list[tuple[str, str, str]] = []  # (binary, brew_package, label)
    tools_present: list[str] = []

    checks = [
        ("sops", "sops", "sops"),
        ("age", "age", "age"),
        ("gpg", "gnupg", "gnupg"),
        ("psql", "postgresql@17", "postgresql@17"),
        ("gdalinfo", "gdal", "gdal"),
        ("bun", "oven-sh/bun/bun", "bun"),
        # Docker tools for K8s deployment
        ("docker", "docker", "docker"),
        ("docker-compose", "docker-compose", "docker-compose"),
        ("kubectl", "kubernetes-cli", "kubectl"),
    ]

    # Colima is only needed on macOS (Linux uses native Docker)
    if sys.platform == "darwin":
        checks.append(("colima", "colima", "colima"))

    for binary, brew_package, label in checks:
        if runner.check(["which", binary]):
            tools_present.append(label)
        else:
            tools_to_install.append((binary, brew_package, label))

    # Report what's already installed
    if tools_present:
        logger.info(f"Already installed: {', '.join(tools_present)}")

    # Install missing tools
    for binary, brew_package, label in tools_to_install:
        runner.run(
            ["brew", "install", brew_package],
            label=f"Installing {label}",
            done_msg=f"{label} installed",
        )

    logger.done("System dependencies ready")


def install_python_dependencies(
    runner: CmdRunner, project_root: Path, *, skip: bool = False
) -> None:
    """Install Python dependencies via uv.

    Automatically includes all dependency groups from pyproject.toml
    (except "dev" which is already included by default).

    Args:
        runner: CmdRunner instance for executing commands.
        project_root: Path to project root.
        skip: If True, skip installation entirely.
    """
    if skip:
        logger.skip("Python dependency installation")
        return

    # Build uv sync command
    cmd = ["uv", "sync", "--upgrade-package", "djb"]

    # Include all dependency groups (except "dev" which is default)
    # This ensures groups like "geo" (GDAL) are installed for local development
    pyproject_path = project_root / "pyproject.toml"
    groups = get_dependency_groups(pyproject_path)
    extra_groups = [g for g in groups if g != "dev"]
    for group in extra_groups:
        cmd.extend(["--group", group])
    if extra_groups:
        logger.info(f"Including dependency groups: {', '.join(extra_groups)}")

    runner.run(
        cmd,
        cwd=project_root,
        label="Installing Python dependencies (and upgrading djb to latest)",
        done_msg="Python dependencies installed",
    )


def install_frontend_dependencies(
    runner: CmdRunner, project_root: Path, *, skip: bool = False
) -> None:
    """Install frontend dependencies via bun.

    Args:
        runner: CmdRunner instance for executing commands.
        project_root: Path to project root.
        skip: If True, skip installation entirely.
    """
    if skip:
        logger.skip("Frontend dependency installation")
        return

    frontend_dir = project_root / "frontend"
    if frontend_dir.exists():
        runner.run(
            ["bun", "install"],
            cwd=frontend_dir,
            label="Installing frontend dependencies",
            done_msg="Frontend dependencies installed",
        )
    else:
        logger.skip(f"Frontend directory not found at {frontend_dir}")


@click.command("deps")
@click.option("--skip-brew", is_flag=True, help="Skip Homebrew dependencies")
@click.option("--skip-python", is_flag=True, help="Skip Python dependencies")
@click.option("--skip-frontend", is_flag=True, help="Skip frontend dependencies")
@djb_pass_context(InitContext)
@click.pass_context
def deps(
    ctx: click.Context,
    init_ctx: InitContext,
    skip_brew: bool,
    skip_python: bool,
    skip_frontend: bool,
) -> None:
    """Install system and package dependencies.

    Installs:
    - System dependencies via Homebrew (SOPS, age, PostgreSQL, GDAL, Bun)
    - Python dependencies via uv sync
    - Frontend dependencies via bun install
    """
    project_dir = init_ctx.config.project_dir
    skip_brew = init_ctx.skip_brew or skip_brew
    skip_python = init_ctx.skip_python or skip_python
    skip_frontend = init_ctx.skip_frontend or skip_frontend

    runner = init_ctx.runner
    install_brew_dependencies(runner, skip=skip_brew)
    install_python_dependencies(runner, project_dir, skip=skip_python)
    install_frontend_dependencies(runner, project_dir, skip=skip_frontend)
