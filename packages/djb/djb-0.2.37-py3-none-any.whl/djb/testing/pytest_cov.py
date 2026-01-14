"""Pytest-cov detection utilities."""

from __future__ import annotations

from pathlib import Path

from djb.cli.utils import TOOL_CHECK_TIMEOUT
from djb.core.cmd_runner import CmdRunner


def has_pytest_cov(runner: CmdRunner, project_root: Path) -> bool:
    """Check if pytest-cov is available in the project's environment.

    Args:
        runner: CmdRunner instance for executing commands.
        project_root: Root directory of the project.

    Returns:
        True if pytest-cov is available, False otherwise.
    """
    return runner.check(
        ["uv", "run", "python", "-c", "import pytest_cov"],
        cwd=project_root,
        timeout=TOOL_CHECK_TIMEOUT,
    )
