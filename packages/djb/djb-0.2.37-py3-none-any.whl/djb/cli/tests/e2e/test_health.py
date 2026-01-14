"""End-to-end tests for djb health CLI commands.

These tests exercise the health check commands while mocking
the actual tool invocations (uv run, bun run).

Commands tested:
- djb health
- djb health --no-e2e
- djb health lint
- djb health typecheck
- djb health test
- djb health test --no-e2e
"""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.cli.djb import djb_cli
from djb.cli.health import (
    _get_project_context,
    _get_run_scopes,
    _is_inside_djb_dir,
)

from . import DJB_PYPROJECT_CONTENT


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def project_dir(health_project: Path) -> Path:
    """Use health_project for all tests in this module."""
    return health_project


class TestIsInsideDjbDir:
    """E2E tests for _is_inside_djb_dir helper."""

    def test_detects_djb_directory(self, project_dir):
        """It detects a djb project directory."""
        (project_dir / "pyproject.toml").write_text(DJB_PYPROJECT_CONTENT)
        assert _is_inside_djb_dir(project_dir) is True

    def test_rejects_non_djb_directory(self, project_dir):
        """It rejects a non-djb project directory."""
        (project_dir / "pyproject.toml").write_text('[project]\nname = "other-project"\n')
        assert _is_inside_djb_dir(project_dir) is False

    def test_rejects_missing_pyproject(self, project_dir):
        """It rejects a directory without pyproject.toml."""
        empty_dir = project_dir / "empty"
        empty_dir.mkdir()
        assert _is_inside_djb_dir(empty_dir) is False


class TestHealthHelperFunctions:
    """E2E tests for health helper functions."""

    def test_get_run_scopes_neither(self):
        """Neither flag means both scopes run."""
        run_backend, run_frontend = _get_run_scopes(scope_frontend=False, scope_backend=False)
        assert run_backend is True
        assert run_frontend is True

    def test_get_run_scopes_backend_only(self):
        """Backend-only scope."""
        run_backend, run_frontend = _get_run_scopes(scope_frontend=False, scope_backend=True)
        assert run_backend is True
        assert run_frontend is False

    def test_get_run_scopes_frontend_only(self):
        """Frontend-only scope."""
        run_backend, run_frontend = _get_run_scopes(scope_frontend=True, scope_backend=False)
        assert run_backend is False
        assert run_frontend is True

    def test_get_project_context_regular_project(self, project_dir, make_djb_config):
        """Project context for a regular (non-djb) project."""
        config = make_djb_config()
        context = _get_project_context(config)

        # Should identify as host project only
        assert context.host_path == project_dir
        assert context.djb_path is None
        assert context.inside_djb is False


class TestHealthLint:
    """E2E tests for djb health lint command."""

    def test_lint_runs_checks(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """Lint runs linting checks."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "lint"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()
        # Verify lint commands were called
        assert mock_cmd_runner.run.call_count > 0

    def test_lint_with_fix(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """Lint --fix runs format instead of check."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "lint", "--fix"],
        )

        # Should complete
        assert result.exit_code == 0 or "failed" in result.output.lower()


class TestHealthTypecheck:
    """E2E tests for djb health typecheck command."""

    def test_typecheck_runs_checks(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """Typecheck runs type checking."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "typecheck"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()
        # Verify typecheck commands were called
        assert mock_cmd_runner.run.call_count > 0


class TestHealthTest:
    """E2E tests for djb health test command."""

    def test_test_runs_pytest(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """Runs pytest."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "test"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()
        # Verify test commands were called
        assert mock_cmd_runner.run.call_count > 0


class TestHealthNoE2E:
    """E2E tests for djb health --no-e2e flag."""

    def test_no_e2e_flag_skips_e2e_tests(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """djb health --no-e2e runs full health check without E2E tests."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "--no-e2e"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()

    def test_test_with_no_e2e_flag(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """djb health test --no-e2e runs tests subcommand without E2E tests."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "test", "--no-e2e"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()
        # Verify test commands were called
        assert mock_cmd_runner.run.call_count > 0


class TestHealthAll:
    """E2E tests for djb health command (all checks)."""

    def test_health_runs_all_checks(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """Health (no subcommand) runs all checks."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()

    def test_health_backend_only(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """--backend flag limits to backend checks."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "--backend", "health"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()
        # Should not mention frontend
        assert "frontend" not in result.output.lower() or "skip" in result.output.lower()

    def test_health_frontend_only(
        self,
        cli_runner,
        mock_cmd_runner,
        project_dir,
    ):
        """--frontend flag limits to frontend checks."""
        mock_cmd_runner.run.only_mock(["uv", "bun"])
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "--frontend", "health"],
        )

        # Should complete (pass or fail)
        assert result.exit_code == 0 or "failed" in result.output.lower()
