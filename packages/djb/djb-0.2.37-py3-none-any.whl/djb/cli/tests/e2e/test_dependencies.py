"""End-to-end tests for djb dependencies CLI command.

Commands tested:
- djb --backend dependencies
- djb --frontend dependencies
- djb dependencies --bump
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner
import pytest

from djb.cli.djb import djb_cli
from djb.cli.utils import CmdRunner


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def project_dir(deps_project: Path) -> Path:
    """Use deps_project for all tests in this module."""
    return deps_project


class TestDependencies:
    """E2E tests for djb dependencies command."""

    def test_dependencies_requires_scope(
        self,
        cli_runner: CliRunner,
        project_dir: Path,
    ):
        """E2E: dependencies command fails with helpful error when no scope flag provided."""
        result = cli_runner.invoke(djb_cli, ["--project-dir", str(project_dir), "dependencies"])

        # Should fail with helpful error
        assert result.exit_code != 0
        assert "backend" in result.output.lower() or "frontend" in result.output.lower()

    def test_dependencies_backend(
        self,
        cli_runner: CliRunner,
        project_dir: Path,
    ):
        """E2E: --backend flag runs uv lock and uv sync for Python deps."""

        def mock_run(cmd, *args, **kwargs):
            return Mock(returncode=0, stdout="", stderr="")

        with patch.object(CmdRunner, "run", side_effect=mock_run):
            result = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(project_dir), "--backend", "dependencies"],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "backend" in result.output.lower() or "python" in result.output.lower()

    def test_dependencies_frontend(
        self,
        cli_runner: CliRunner,
        project_dir: Path,
    ):
        """E2E: --frontend flag runs bun refresh-deps for JavaScript deps."""

        def mock_run(cmd, *args, **kwargs):
            return Mock(returncode=0, stdout="", stderr="")

        with patch.object(CmdRunner, "run", side_effect=mock_run):
            result = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(project_dir), "--frontend", "dependencies"],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "frontend" in result.output.lower()

    def test_dependencies_bump(
        self,
        cli_runner: CliRunner,
        project_dir: Path,
    ):
        """Dependency bump with --bump flag."""

        def mock_run(cmd, *args, **kwargs):
            return Mock(returncode=0, stdout="", stderr="")

        with patch.object(CmdRunner, "run", side_effect=mock_run):
            result = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(project_dir), "--backend", "dependencies", "--bump"],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should mention bump
        assert "bump=yes" in result.output.lower()
