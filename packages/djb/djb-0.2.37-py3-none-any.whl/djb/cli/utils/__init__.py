"""
djb.cli.utils - Utility functions for djb CLI.

Command runner (re-exported from djb.core.cmd_runner):
    CmdRunner - Class for running shell commands (construct with CliContext)
        runner.run() - Run a shell command with optional error handling
            - show_output=True streams output to terminal
            - interactive=True uses PTY for commands needing terminal (GPG, editors)
            - fail_msg=Exception raises on failure
        runner.check() - Check if a command succeeds
        runner.exec() - Replace current process with command
    RunResult - Dataclass containing returncode, stdout, stderr
    CmdError - Exception raised when command fails
    CmdTimeout - Exception raised when command times out

Pyproject utilities:
    load_pyproject - Load and parse a pyproject.toml file
    collect_all_dependencies - Collect dependencies from regular + optional deps
    find_dependency - Find a dependency by name, returns parsed Requirement
    find_dependency_string - Find a dependency by name, returns raw string
    has_dependency - Check if a package is a dependency

Other utilities:
    flatten_dict - Flatten a nested dictionary into a flat dict with uppercase keys

Constants:
    TOOL_CHECK_TIMEOUT - Timeout (seconds) for tool availability checks
"""

from __future__ import annotations

from .flatten import flatten_dict
from .pyproject import (
    collect_all_dependencies,
    find_pyproject_dependency,
    find_dependency_string,
    has_dependency,
    load_pyproject,
)
from .run import (
    CmdError,
    CmdRunner,
    CmdTimeout,
    RunResult,
)

# Timeout for tool availability checks (in seconds)
# Used by subprocess calls that check if a tool (pytest-cov, ruff, etc.) is installed
TOOL_CHECK_TIMEOUT = 10

__all__ = [
    "CmdError",
    "CmdRunner",
    "CmdTimeout",
    "RunResult",
    "TOOL_CHECK_TIMEOUT",
    "collect_all_dependencies",
    "find_pyproject_dependency",
    "find_dependency_string",
    "flatten_dict",
    "has_dependency",
    "load_pyproject",
]
