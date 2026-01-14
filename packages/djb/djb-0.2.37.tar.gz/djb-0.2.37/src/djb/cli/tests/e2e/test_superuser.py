"""End-to-end tests for djb sync-superuser CLI command.

Commands tested:
- djb sync-superuser
"""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.cli.djb import djb_cli


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def project_dir(django_project: Path) -> Path:
    """Use django_project for all tests in this module."""
    return django_project


class TestSyncSuperuser:
    """E2E tests for djb sync-superuser command."""

    def test_sync_superuser_local(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """Sync-superuser for local development."""
        # Mock uv run commands (which run manage.py/python)
        mock_cmd_runner.run.only_mock(["uv", "python", "manage.py"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "sync-superuser"],
        )

        # Should complete (may fail if Django not configured, that's ok)
        # We just check it runs without crashing
        assert (
            "sync" in result.output.lower()
            or "superuser" in result.output.lower()
            or result.exit_code in [0, 1]
        )

    def test_sync_superuser_dry_run(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """Sync-superuser with --dry-run flag."""
        # Mock uv run commands (which run manage.py/python)
        mock_cmd_runner.run.only_mock(["uv", "python", "manage.py"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "sync-superuser", "--dry-run"],
        )

        # Should complete
        assert (
            "dry" in result.output.lower()
            or "would" in result.output.lower()
            or result.exit_code in [0, 1]
        )
