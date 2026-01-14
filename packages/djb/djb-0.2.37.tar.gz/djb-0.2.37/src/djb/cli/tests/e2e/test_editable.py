"""End-to-end tests for djb editable CLI command.

Commands tested:
- djb editable
- djb editable --status
- djb editable --uninstall
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from djb.cli.djb import djb_cli
from djb.cli.editable import (
    get_djb_version_specifier,
    is_djb_editable,
    is_djb_package_dir,
)


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


class TestEditableHelperFunctions:
    """E2E tests for editable helper functions."""

    def test_get_djb_version_specifier(self, host_project: Path):
        """Extracting djb version specifier from pyproject.toml."""
        specifier = get_djb_version_specifier(host_project)
        assert specifier == ">=0.2.0"

    def test_is_djb_package_dir_true(self, djb_package_dir: Path):
        """djb directory is correctly identified."""
        assert is_djb_package_dir(djb_package_dir) is True

    def test_is_djb_package_dir_false(self, host_project: Path):
        """Host project is not identified as djb."""
        assert is_djb_package_dir(host_project) is False

    def test_is_djb_editable_false_by_default(self, host_project: Path):
        """djb is not editable by default."""
        assert is_djb_editable(host_project) is False


class TestEditableDjb:
    """E2E tests for djb editable command."""

    def test_editable_status_shows_not_editable(
        self,
        cli_runner,
        host_project: Path,
    ):
        """status subcommand shows djb is not in editable mode."""
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(host_project), "editable", "status"],
        )

        # Should complete and show not editable
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "not" in result.output.lower() or "pypi" in result.output.lower()

    def test_editable_from_djb_dir_warns(
        self,
        cli_runner,
        djb_package_dir: Path,
    ):
        """Running from djb directory shows appropriate message."""
        # Special case: uses djb_package_dir instead of host_project
        env = {
            "DJB_PROJECT_DIR": str(djb_package_dir),
            "DJB_PROJECT_NAME": "djb",
        }

        with patch.dict(os.environ, env):
            result = cli_runner.invoke(
                djb_cli,
                ["editable", "status"],
            )

        # Should complete (may show special message for djb dir)
        assert "djb" in result.output.lower()
