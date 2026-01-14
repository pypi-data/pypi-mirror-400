"""End-to-end tests for djb deploy CLI commands.

These tests exercise the deploy commands while mocking Heroku CLI
to avoid side effects.

Commands tested:
- djb deploy heroku
# - djb deploy heroku revert
- djb deploy heroku setup
"""

from __future__ import annotations

import os
import subprocess  # noqa: TID251 - invokes git directly to test editable djb stashing
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from djb.cli.djb import djb_cli
from djb.cli.utils import CmdRunner


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def project_dir(deploy_project: Path) -> Path:
    """Use deploy_project for all tests in this module."""
    return deploy_project


@pytest.fixture
def mock_heroku_success():
    """Mock Heroku CLI via CmdRunner.run.

    Mocks heroku commands and git push to heroku, but preserves
    real CmdRunner execution for git and other commands.
    """
    original_run = CmdRunner.run

    def run_side_effect(runner_self, cmd, *args, **kwargs):
        cmd_list = cmd if isinstance(cmd, list) else [cmd]
        cmd_str = " ".join(cmd_list)

        # Check for git commands first (they may contain "heroku" in ref names)
        if cmd_list[0] == "git" and "heroku" in cmd_str:
            # Mock git commands that reference heroku remote
            if "push" in cmd_str:
                return Mock(returncode=0, stdout="", stderr="Everything up-to-date")
            elif "fetch" in cmd_str:
                return Mock(returncode=0, stdout="", stderr="")
            elif "rev-list" in cmd_str:
                return Mock(returncode=0, stdout="0\n", stderr="")
            elif "log" in cmd_str:
                return Mock(returncode=0, stdout="", stderr="")
            else:
                return Mock(returncode=0, stdout="", stderr="")
        elif "heroku" in cmd_str:
            # Mock various Heroku commands
            if "auth:whoami" in cmd_str:
                return Mock(returncode=0, stdout="test@example.com\n", stderr="")
            elif "apps:info" in cmd_str:
                return Mock(returncode=0, stdout="=== myproject\nDynos: 0\n", stderr="")
            elif "config:set" in cmd_str:
                return Mock(returncode=0, stdout="", stderr="")
            elif "config:get" in cmd_str:
                return Mock(returncode=0, stdout="False\n", stderr="")
            elif "buildpacks" in cmd_str and "--app" in cmd_str:
                return Mock(returncode=0, stdout="heroku/python\n", stderr="")
            elif "buildpacks:clear" in cmd_str:
                return Mock(returncode=0, stdout="", stderr="")
            elif "buildpacks:add" in cmd_str:
                return Mock(returncode=0, stdout="", stderr="")
            elif "addons" in cmd_str:
                return Mock(
                    returncode=0, stdout="heroku-postgresql (postgresql-solid-12345)\n", stderr=""
                )
            elif "run" in cmd_str:
                return Mock(returncode=0, stdout="", stderr="")
            else:
                return Mock(returncode=0, stdout="", stderr="")
        else:
            # Run real CmdRunner for non-Heroku commands
            return original_run(runner_self, cmd, *args, **kwargs)

    return run_side_effect


class TestDeployHerokuSetup:
    """E2E tests for djb deploy heroku setup command."""

    def test_setup_configures_app(
        self,
        cli_runner,
        project_dir,
        mock_heroku_success,
    ):
        """Setup configures buildpacks, config vars, and remote."""
        with patch.object(CmdRunner, "run", mock_heroku_success):
            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "-y",
                    "deploy",
                    "heroku",
                    "--app",
                    "myproject",
                    "setup",
                ],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "setup complete" in result.output.lower()

    def test_setup_with_skip_flags(
        self,
        cli_runner,
        project_dir,
        mock_heroku_success,
    ):
        """Setup respects skip flags."""
        with patch.object(CmdRunner, "run", mock_heroku_success):
            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "-y",
                    "deploy",
                    "heroku",
                    "--app",
                    "myproject",
                    "setup",
                    "--skip-buildpacks",
                    "--skip-postgres",
                    "--skip-remote",
                ],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should complete setup (skipping doesn't mean no output about those sections)
        assert "setup complete" in result.output.lower()


class TestDeployHeroku:
    """E2E tests for djb deploy heroku command."""

    def test_deploy_requires_production_mode_warning(
        self,
        cli_runner,
        project_dir,
        mock_heroku_success,
    ):
        """Deploy warns when not in production mode."""
        with patch.object(CmdRunner, "run", mock_heroku_success):
            # Without -y, it should prompt about non-production mode
            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "deploy",
                    "heroku",
                    "--app",
                    "myproject",
                    "--skip-secrets",
                ],
                input="n\n",  # Decline the prompt
            )

        # Should warn about mode
        assert "mode" in result.output.lower()

    def test_deploy_with_skip_options(
        self,
        cli_runner,
        project_dir,
        mock_heroku_success,
    ):
        """Deploy works with skip options."""
        # Change to project directory so git commands work
        old_cwd = os.getcwd()
        try:
            os.chdir(project_dir)
            with patch.object(CmdRunner, "run", mock_heroku_success):
                result = cli_runner.invoke(
                    djb_cli,
                    [
                        "--project-dir",
                        str(project_dir),
                        "--mode",
                        "production",
                        "-y",
                        "deploy",
                        "heroku",
                        "--app",
                        "myproject",
                        "--skip-secrets",
                        "--skip-migrate",
                    ],
                )
        finally:
            os.chdir(old_cwd)

        # Should succeed or show "up-to-date" message
        output_lower = result.output.lower()
        assert (
            result.exit_code == 0 or "up-to-date" in output_lower
        ), f"Command failed: {result.output}"


class TestDeployHerokuRevert:
    """E2E tests for djb deploy heroku revert command."""

    def test_revert_prompts_for_confirmation(
        self,
        cli_runner,
        project_dir,
        mock_heroku_success,
    ):
        """Revert prompts for confirmation."""
        # Change to project directory so git commands work
        old_cwd = os.getcwd()
        try:
            os.chdir(project_dir)
            with patch.object(CmdRunner, "run", mock_heroku_success):
                result = cli_runner.invoke(
                    djb_cli,
                    [
                        "--project-dir",
                        str(project_dir),
                        "deploy",
                        "heroku",
                        "--app",
                        "myproject",
                        "revert",
                    ],
                    input="n\n",  # Decline the prompt
                )
        finally:
            os.chdir(old_cwd)

        # Should prompt for confirmation and show we're reverting
        # (the confirmation prompt or cancellation message should appear)
        output_lower = result.output.lower()
        assert "revert" in output_lower or "previous" in output_lower or "continue" in output_lower

    def test_revert_to_specific_commit(
        self,
        cli_runner,
        project_dir,
        mock_heroku_success,
    ):
        """E2E: revert command accepts specific commit hash argument."""

        # Get the first commit hash
        commit_result = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "HEAD~1"],
            capture_output=True,
            text=True,
        )
        first_commit = commit_result.stdout.strip()[:7]

        # Change to project directory so git commands work
        old_cwd = os.getcwd()
        try:
            os.chdir(project_dir)
            with patch.object(CmdRunner, "run", mock_heroku_success):
                result = cli_runner.invoke(
                    djb_cli,
                    [
                        "--project-dir",
                        str(project_dir),
                        "deploy",
                        "heroku",
                        "--app",
                        "myproject",
                        "revert",
                        first_commit,
                    ],
                    input="y\n",  # Confirm the revert
                )
        finally:
            os.chdir(old_cwd)

        # Should show the commit being reverted to or confirm the revert
        output_lower = result.output.lower()
        assert (
            first_commit in result.output or "revert" in output_lower or "continue" in output_lower
        )


class TestDerivedProjectName:
    """E2E tests for project_name derivation from directory name."""

    def test_deploy_uses_derived_project_name_when_not_configured(
        self, cli_runner, project_dir, monkeypatch
    ):
        """Deploy heroku: project_name defaults to directory name when unconfigured."""
        # Create minimal project without project_name config
        derived_dir = project_dir / "my-derived-name"
        derived_dir.mkdir()
        (derived_dir / "pyproject.toml").write_text("[project]\ndependencies = []\n")

        monkeypatch.chdir(derived_dir)
        monkeypatch.delenv("DJB_PROJECT_NAME", raising=False)

        result = cli_runner.invoke(djb_cli, ["deploy", "heroku"])
        # Should proceed (fail for other reasons like missing git)
        # but NOT fail due to missing project_name
        assert "Missing required config: project_name" not in result.output

    def test_revert_uses_derived_project_name_when_not_configured(
        self, cli_runner, project_dir, monkeypatch
    ):
        """Deploy heroku revert: project_name defaults to directory name when unconfigured."""
        derived_dir = project_dir / "my-derived-name"
        derived_dir.mkdir()
        (derived_dir / "pyproject.toml").write_text("[project]\ndependencies = []\n")

        monkeypatch.chdir(derived_dir)
        monkeypatch.delenv("DJB_PROJECT_NAME", raising=False)

        result = cli_runner.invoke(djb_cli, ["deploy", "heroku", "revert"])
        assert "Missing required config: project_name" not in result.output


class TestEditableDjbStashing:
    """E2E tests for editable djb stashing during deploy."""

    def test_editable_djb_is_stashed_and_restored(
        self, cli_runner, make_project_with_editable_djb_repo, mock_heroku_success
    ):
        """Editable djb is temporarily stashed for deploy."""
        editable_project = make_project_with_editable_djb_repo(
            user_email="test@example.com", user_name="Test User"
        )

        # Add heroku remote (like deploy_project fixture)
        subprocess.run(
            [
                "git",
                "-C",
                str(editable_project),
                "remote",
                "add",
                "heroku",
                "https://git.heroku.com/testapp.git",
            ],
            capture_output=True,
        )

        with patch.object(CmdRunner, "run", mock_heroku_success):
            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(editable_project),
                    "-y",
                    "deploy",
                    "heroku",
                    "--app",
                    "testapp",
                ],
            )

        assert "Stashed editable djb configuration for deploy" in result.output
        assert "Restoring editable djb configuration" in result.output
