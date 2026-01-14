"""Pytest-xdist detection utilities."""

from __future__ import annotations

from pathlib import Path

from djb.cli.utils import TOOL_CHECK_TIMEOUT
from djb.core.cmd_runner import CmdRunner


def has_pytest_xdist(runner: CmdRunner, project_root: Path) -> bool:
    """Check if pytest-xdist is available in the project's environment.

    Args:
        runner: CmdRunner instance for executing commands.
        project_root: Root directory of the project.

    Returns:
        True if pytest-xdist is available, False otherwise.
    """
    return runner.check(
        ["uv", "run", "python", "-c", "import xdist"],
        cwd=project_root,
        timeout=TOOL_CHECK_TIMEOUT,
    )
