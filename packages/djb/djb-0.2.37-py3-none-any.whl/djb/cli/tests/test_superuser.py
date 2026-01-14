"""Tests for djb sync-superuser CLI command."""

from __future__ import annotations

from unittest.mock import Mock

from djb.cli.djb import djb_cli


class TestSyncSuperuserCommand:
    """Tests for sync-superuser CLI command."""

    def test_help(self, cli_runner):
        """djb sync-superuser --help works."""
        result = cli_runner.invoke(djb_cli, ["sync-superuser", "--help"])
        assert result.exit_code == 0
        assert "Sync superuser from encrypted secrets" in result.output
        assert "--dry-run" in result.output
        assert "--app" in result.output
        # --mode is NOT a sync-superuser option (it's global)
        # The Options section should not list -m/--mode
        options_section = result.output.split("Options:")[1] if "Options:" in result.output else ""
        assert "-m, --mode" not in options_section

    def test_local_sync_default(self, cli_runner, djb_config, mock_cmd_runner):
        """djb sync-superuser runs local sync with default options."""
        result = cli_runner.invoke(djb_cli, ["sync-superuser"])

        assert result.exit_code == 0
        # Local sync uses run with show_output=True
        mock_cmd_runner.run.assert_called_once()
        call_args = mock_cmd_runner.run.call_args[0][0]
        call_kwargs = mock_cmd_runner.run.call_args[1]
        # Mode is always passed from config (defaults to development)
        assert call_args == [
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "development",
        ]
        assert call_kwargs["label"] == "Syncing superuser locally"
        assert call_kwargs.get("show_output") is True

    def test_local_sync_with_mode(self, cli_runner, mock_cmd_runner):
        """djb sync-superuser runs local sync with specific mode via --mode."""
        result = cli_runner.invoke(djb_cli, ["--mode", "staging", "sync-superuser"])

        assert result.exit_code == 0
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert call_args == [
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "staging",
        ]

    def test_local_sync_with_dry_run(self, cli_runner, djb_config, mock_cmd_runner):
        """djb sync-superuser --dry-run passes dry-run flag."""
        result = cli_runner.invoke(djb_cli, ["sync-superuser", "--dry-run"])

        assert result.exit_code == 0
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert call_args == [
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "development",
            "--dry-run",
        ]

    def test_local_sync_with_all_options(self, cli_runner, mock_cmd_runner):
        """djb sync-superuser combines all local options correctly."""
        result = cli_runner.invoke(djb_cli, ["--mode", "staging", "sync-superuser", "--dry-run"])

        assert result.exit_code == 0
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert call_args == [
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "staging",
            "--dry-run",
        ]

    def test_heroku_sync(self, cli_runner, djb_config, mock_cmd_runner):
        """djb sync-superuser --app syncs on Heroku with default mode."""
        result = cli_runner.invoke(djb_cli, ["sync-superuser", "--app", "myapp"])

        assert result.exit_code == 0
        mock_cmd_runner.run.assert_called_once()
        call_args = mock_cmd_runner.run.call_args[0][0]
        call_kwargs = mock_cmd_runner.run.call_args[1]
        # Mode is always passed from config (defaults to development)
        assert call_args == [
            "heroku",
            "run",
            "--no-notify",
            "--app",
            "myapp",
            "--",
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "development",
        ]
        assert call_kwargs["label"] == "Syncing superuser on Heroku (myapp)"

    def test_heroku_sync_with_mode(self, cli_runner, mock_cmd_runner):
        """djb sync-superuser --app syncs on Heroku with specific mode."""
        result = cli_runner.invoke(
            djb_cli, ["--mode", "production", "sync-superuser", "--app", "myapp"]
        )

        assert result.exit_code == 0
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert call_args == [
            "heroku",
            "run",
            "--no-notify",
            "--app",
            "myapp",
            "--",
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "production",
        ]

    def test_heroku_sync_with_dry_run(self, cli_runner, mock_cmd_runner):
        """djb sync-superuser --app --dry-run passes dry-run flag to Heroku."""
        result = cli_runner.invoke(djb_cli, ["sync-superuser", "--app", "myapp", "--dry-run"])

        assert result.exit_code == 0
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert "--dry-run" in call_args

    def test_heroku_sync_with_all_options(self, cli_runner, mock_cmd_runner):
        """djb sync-superuser --app combines all Heroku options correctly."""
        result = cli_runner.invoke(
            djb_cli, ["--mode", "production", "sync-superuser", "--app", "myapp", "--dry-run"]
        )

        assert result.exit_code == 0
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert call_args == [
            "heroku",
            "run",
            "--no-notify",
            "--app",
            "myapp",
            "--",
            "python",
            "manage.py",
            "sync_superuser",
            "--environment",
            "production",
            "--dry-run",
        ]

    def test_failure_returns_error(self, cli_runner, mock_cmd_runner):
        """djb sync-superuser raises ClickException on local command failure."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="")

        result = cli_runner.invoke(djb_cli, ["sync-superuser"])

        assert result.exit_code == 1
        assert "Failed to sync superuser" in result.output

    def test_heroku_failure_returns_error(self, cli_runner, mock_cmd_runner):
        """djb sync-superuser --app raises ClickException on Heroku command failure."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="")

        result = cli_runner.invoke(djb_cli, ["sync-superuser", "--app", "myapp"])

        assert result.exit_code == 1
        assert "Failed to sync superuser" in result.output
