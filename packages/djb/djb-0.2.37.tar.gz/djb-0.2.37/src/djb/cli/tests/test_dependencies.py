"""Tests for djb dependencies command.

All tests use FAKE_PROJECT_DIR and mock_cmd_runner fixture. No real file I/O is performed.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from djb.cli.djb import djb_cli
from djb.cli.tests import FAKE_PROJECT_DIR


class TestDjbDependencies:
    """Tests for djb dependencies command."""

    def test_dependencies_help(self, cli_runner):
        """djb dependencies --help works."""
        result = cli_runner.invoke(djb_cli, ["dependencies", "--help"])
        assert result.exit_code == 0
        assert "Refresh dependencies" in result.output
        assert "--bump" in result.output

    def test_dependencies_requires_scope(self, cli_runner):
        """djb dependencies without scope shows 'Specify --frontend and/or --backend' error."""
        result = cli_runner.invoke(djb_cli, ["dependencies"])
        assert result.exit_code == 1
        assert "Specify --frontend and/or --backend" in result.output


class TestBackendDependencies:
    """Tests for backend dependency refresh (--backend)."""

    def test_backend_runs_uv_lock_and_sync(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --backend dependencies runs uv lock --upgrade followed by uv sync."""
        result = cli_runner.invoke(djb_cli, ["--backend", "dependencies"])

        assert result.exit_code == 0
        assert mock_cmd_runner.run.call_count == 2

        # First call: uv lock --upgrade
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert first_call.args[0] == ["uv", "lock", "--upgrade"]
        assert first_call.kwargs["cwd"] == FAKE_PROJECT_DIR
        assert first_call.kwargs["label"] == "uv lock"

        # Second call: uv sync
        second_call = mock_cmd_runner.run.call_args_list[1]
        assert second_call.args[0] == ["uv", "sync"]
        assert second_call.kwargs["cwd"] == FAKE_PROJECT_DIR
        assert second_call.kwargs["label"] == "uv sync"

    def test_backend_with_bump_adds_latest_flag(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --backend dependencies --bump adds --latest to uv lock."""
        result = cli_runner.invoke(djb_cli, ["--backend", "dependencies", "--bump"])

        assert result.exit_code == 0
        assert mock_cmd_runner.run.call_count == 2

        # First call should have --latest
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert first_call.args[0] == ["uv", "lock", "--upgrade", "--latest"]

    def test_backend_uv_lock_failure_raises_error(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --backend dependencies raises ClickException on uv lock failure."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="error output")

        result = cli_runner.invoke(djb_cli, ["--backend", "dependencies"])

        assert result.exit_code == 1
        assert "uv lock failed" in result.output

    def test_backend_uv_sync_failure_raises_error(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --backend dependencies raises ClickException on uv sync failure."""
        # First call succeeds (uv lock), second call fails (uv sync)
        mock_cmd_runner.run.side_effect_values.extend(
            [
                Mock(returncode=0, stdout="", stderr=""),
                Mock(returncode=1, stdout="", stderr="sync error"),
            ]
        )

        result = cli_runner.invoke(djb_cli, ["--backend", "dependencies"])

        assert result.exit_code == 1
        assert "uv sync failed" in result.output


class TestFrontendDependencies:
    """Tests for frontend dependency refresh (--frontend)."""

    def test_frontend_runs_bun_refresh_deps(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --frontend dependencies runs bun run refresh-deps in frontend directory."""
        result = cli_runner.invoke(djb_cli, ["--frontend", "dependencies"])

        assert result.exit_code == 0
        assert mock_cmd_runner.run.call_count == 1

        call = mock_cmd_runner.run.call_args_list[0]
        assert call.args[0] == ["bun", "run", "refresh-deps"]
        assert call.kwargs["cwd"] == FAKE_PROJECT_DIR / "frontend"
        assert call.kwargs["label"] == "frontend refresh-deps"

    def test_frontend_with_bump_adds_bump_flag(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --frontend dependencies --bump adds --bump to bun run refresh-deps."""
        result = cli_runner.invoke(djb_cli, ["--frontend", "dependencies", "--bump"])

        assert result.exit_code == 0

        call = mock_cmd_runner.run.call_args_list[0]
        assert call.args[0] == ["bun", "run", "refresh-deps", "--bump"]

    def test_frontend_failure_raises_error(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --frontend dependencies raises ClickException on refresh-deps failure."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="bun error")

        result = cli_runner.invoke(djb_cli, ["--frontend", "dependencies"])

        assert result.exit_code == 1
        assert "frontend refresh-deps failed" in result.output


class TestDependenciesProgressMessages:
    """Tests for progress messages in both backend and frontend dependency refresh."""

    @pytest.mark.parametrize(
        "scope_flag,expected_message",
        [
            ("--backend", "Refreshing Python deps with uv"),
            ("--frontend", "Refreshing frontend deps with Bun"),
        ],
        ids=["backend", "frontend"],
    )
    def test_shows_progress_message(
        self, cli_runner, djb_config, mock_cmd_runner, scope_flag, expected_message
    ):
        """djb dependencies shows informative progress messages for each scope."""
        result = cli_runner.invoke(djb_cli, [scope_flag, "dependencies"])

        assert result.exit_code == 0
        assert expected_message in result.output
        assert "bump=no" in result.output

    @pytest.mark.parametrize(
        "scope_flag",
        ["--backend", "--frontend"],
        ids=["backend", "frontend"],
    )
    def test_with_bump_shows_bump_status(self, cli_runner, djb_config, mock_cmd_runner, scope_flag):
        """djb dependencies --bump shows bump=yes in progress message."""
        result = cli_runner.invoke(djb_cli, [scope_flag, "dependencies", "--bump"])

        assert result.exit_code == 0
        assert "bump=yes" in result.output


class TestBothScopes:
    """Tests for running both backend and frontend dependencies."""

    def test_both_scopes_runs_all_commands(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --backend --frontend dependencies runs all dependency commands."""
        result = cli_runner.invoke(djb_cli, ["--backend", "--frontend", "dependencies"])

        assert result.exit_code == 0
        # Backend: uv lock + uv sync, Frontend: bun run refresh-deps
        assert mock_cmd_runner.run.call_count == 3

        # Verify backend commands
        assert mock_cmd_runner.run.call_args_list[0].args[0] == [
            "uv",
            "lock",
            "--upgrade",
        ]
        assert mock_cmd_runner.run.call_args_list[1].args[0] == ["uv", "sync"]

        # Verify frontend command
        assert mock_cmd_runner.run.call_args_list[2].args[0] == [
            "bun",
            "run",
            "refresh-deps",
        ]
        assert mock_cmd_runner.run.call_args_list[2].kwargs["cwd"] == FAKE_PROJECT_DIR / "frontend"

    def test_both_scopes_with_bump(self, cli_runner, djb_config, mock_cmd_runner):
        """djb dependencies --bump applies to both backend and frontend."""
        result = cli_runner.invoke(djb_cli, ["--backend", "--frontend", "dependencies", "--bump"])

        assert result.exit_code == 0

        # Backend should have --latest
        assert mock_cmd_runner.run.call_args_list[0].args[0] == [
            "uv",
            "lock",
            "--upgrade",
            "--latest",
        ]

        # Frontend should have --bump
        assert mock_cmd_runner.run.call_args_list[2].args[0] == [
            "bun",
            "run",
            "refresh-deps",
            "--bump",
        ]

    def test_backend_failure_stops_before_frontend(self, cli_runner, djb_config, mock_cmd_runner):
        """djb --backend --frontend dependencies stops before frontend on backend failure."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="uv lock error")

        result = cli_runner.invoke(djb_cli, ["--backend", "--frontend", "dependencies"])

        assert result.exit_code == 1
        # Only uv lock should have been called before failure
        assert mock_cmd_runner.run.call_count == 1
