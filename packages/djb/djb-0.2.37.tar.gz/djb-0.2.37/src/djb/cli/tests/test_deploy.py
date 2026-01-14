"""Tests for djb deploy CLI commands."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from djb.cli.heroku.heroku import (
    HerokuDeployConfig,
    _deploy_heroku_impl,
    _get_app_or_fail,
    _resolve_heroku_app,
    _run_heroku_migrations,
)
from djb.types import Mode
from djb.cli.djb import djb_cli
from djb.cli.tests import FAKE_PROJECT_DIR
from djb.config import DjbConfig
from djb.secrets import SopsError


def _mock_path_exists_all():
    """Create a Path.exists mock that returns True for all deploy-related directories."""
    original_exists = Path.exists

    def mock_exists(self):
        path_str = str(self)
        if ".git" in path_str or path_str.endswith("frontend") or path_str.endswith("secrets"):
            return True
        return original_exists(self)

    return mock_exists


def _deploy_mock_side_effect(cmd, *args, **kwargs):
    """Default side_effect for deploy tests - returns appropriate responses for each command."""
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    if "branch --show-current" in cmd_str:
        return Mock(returncode=0, stdout="main\n", stderr="")
    elif "rev-list --count" in cmd_str:
        return Mock(returncode=0, stdout="0\n", stderr="")
    elif "fetch heroku" in cmd_str:
        return Mock(returncode=0, stdout="", stderr="")
    else:
        return Mock(returncode=0, stdout="", stderr="")


@pytest.fixture
def mock_deploy_context(monkeypatch, mock_cmd_runner):
    """Mock Path.cwd for deploy tests, using mock_cmd_runner for commands.

    Yields mock_cmd_runner for configuring in tests.
    Default setup: run returns success with "main" branch.
    Uses environment variables instead of real config files.
    """
    # Mock config via environment variables instead of creating files
    monkeypatch.setenv("DJB_NAME", "Test User")
    monkeypatch.setenv("DJB_EMAIL", "test@example.com")

    with (
        patch("djb.cli.heroku.heroku.Path.cwd", return_value=FAKE_PROJECT_DIR),
        patch.object(Path, "exists", _mock_path_exists_all()),
        patch.object(Path, "is_dir", _mock_path_exists_all()),
    ):
        mock_cmd_runner.run.side_effect = _deploy_mock_side_effect
        yield mock_cmd_runner


def make_revert_side_effect(
    *,
    rev_parse_stdout: str = "abc1234567890\n",
    cat_file_stdout: str = "commit\n",
    cat_file_returncode: int = 0,
    log_stdout: str = "abc1234 Some commit\n",
) -> Callable:
    """Factory for creating revert command side_effect functions.

    Args:
        rev_parse_stdout: Output for git rev-parse command
        cat_file_stdout: Output for git cat-file command
        cat_file_returncode: Return code for git cat-file (1 for invalid hash)
        log_stdout: Output for git log command

    Note: When using patch.object(CmdRunner, "run"), the mock receives (cmd, ...)
    without the self argument, since MagicMock doesn't implement descriptor protocol.
    """

    def side_effect(cmd, *args, **kwargs):
        if cmd == ["heroku", "auth:whoami"]:
            return Mock(returncode=0, stdout="", stderr="")
        if "rev-parse" in cmd:
            return Mock(returncode=0, stdout=rev_parse_stdout, stderr="")
        if "cat-file" in cmd:
            return Mock(returncode=cat_file_returncode, stdout=cat_file_stdout, stderr="")
        if "log" in cmd:
            return Mock(returncode=0, stdout=log_stdout, stderr="")
        return Mock(returncode=0, stdout="", stderr="")

    return side_effect


class TestDeployHerokuCommand:
    """Tests for deploy heroku CLI command."""

    def test_help(self, cli_runner):
        """djb deploy heroku --help works."""
        result = cli_runner.invoke(djb_cli, ["deploy", "heroku", "--help"])
        assert result.exit_code == 0
        assert "Deploy to Heroku" in result.output
        assert "deploys the application to Heroku" in result.output
        assert "--app" in result.output
        assert "--local-build" in result.output
        assert "--skip-migrate" in result.output
        assert "--skip-secrets" in result.output
        # Verify subcommands are listed
        assert "setup" in result.output
        assert "revert" in result.output

    def test_local_build_option(self, cli_runner, mock_deploy_context):
        """djb deploy heroku --local-build runs frontend build locally."""
        # Frontend dir existence is mocked by mock_deploy_context
        result = cli_runner.invoke(
            djb_cli, ["-y", "deploy", "heroku", "--app", "testapp", "--local-build"]
        )

        assert result.exit_code == 0
        # Verify bun build was called
        cmd_calls = [call.args[0] for call in mock_deploy_context.run.call_args_list]
        assert ["bun", "run", "build"] in cmd_calls

    def test_skip_migrate_option(self, cli_runner, mock_deploy_context):
        """djb deploy heroku --skip-migrate skips database migrations."""
        result = cli_runner.invoke(
            djb_cli, ["-y", "deploy", "heroku", "--app", "testapp", "--skip-migrate"]
        )

        assert "Database migrations" in result.output  # logger.skip() format

    def test_skip_secrets_option(self, cli_runner, mock_deploy_context):
        """djb deploy heroku --skip-secrets skips secrets sync."""
        result = cli_runner.invoke(
            djb_cli, ["-y", "deploy", "heroku", "--app", "testapp", "--skip-secrets"]
        )

        assert "Secrets sync" in result.output  # logger.skip() format

    def test_requires_git_repository(self, cli_runner, mock_cmd_runner, djb_config):
        """djb deploy heroku requires a git repository."""
        # Mock .git to NOT exist by patching the Path class methods
        original_exists = Path.exists
        original_is_dir = Path.is_dir

        def mock_exists(self):
            if ".git" in str(self):
                return False
            return original_exists(self)

        def mock_is_dir(self):
            if ".git" in str(self):
                return False
            return original_is_dir(self)

        with (
            patch("djb.cli.heroku.heroku.Path.cwd", return_value=FAKE_PROJECT_DIR),
            patch.object(Path, "exists", mock_exists),
            patch.object(Path, "is_dir", mock_is_dir),
        ):
            mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")

            result = cli_runner.invoke(
                djb_cli,
                ["-y", "deploy", "heroku", "--app", "testapp"],
            )

        assert result.exit_code == 1
        assert "Not in a git repository" in result.output

    def test_mode_guard_warns_when_not_production(
        self, cli_runner, mock_project_with_git_repo, mock_deploy_context
    ):
        """Mode guard displays warning message when deploying in non-production mode."""
        # Deploy with default mode (development) and confirm the prompt
        result = cli_runner.invoke(djb_cli, ["deploy", "heroku", "--app", "testapp"], input="y\n")

        assert "Deploying to Heroku with mode=development" in result.output
        assert "Set production mode: djb --mode production deploy heroku" in result.output

    def test_mode_guard_can_cancel_deployment(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner
    ):
        """Mode guard allows user to cancel deployment via 'n' input."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")

            # Deploy with default mode (development) and decline the prompt
            result = cli_runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp"], input="n\n"
            )

        assert result.exit_code == 1
        assert "Deployment cancelled" in result.output

    def test_mode_guard_yes_flag_skips_confirmation(
        self, cli_runner, mock_project_with_git_repo, mock_deploy_context
    ):
        """djb -y deploy heroku skips mode confirmation prompt."""
        # Deploy with -y flag should not prompt for mode confirmation
        result = cli_runner.invoke(djb_cli, ["-y", "deploy", "heroku", "--app", "testapp"])

        # Should show warning but not prompt
        assert "Deploying to Heroku with mode=development" in result.output
        # Should proceed without user input
        assert "Continue with deployment?" not in result.output

    def test_mode_guard_no_warning_when_production(self, cli_runner, mock_deploy_context):
        """djb deploy heroku shows no mode warning when mode is production."""
        # Mode is set via --mode flag, no need for config file
        # Use -y to skip other prompts (uncommitted changes, etc.)
        result = cli_runner.invoke(
            djb_cli, ["--mode", "production", "-y", "deploy", "heroku", "--app", "testapp"]
        )

        # Should not show mode warning (the mode guard should not trigger)
        assert "Deploying to Heroku with mode=" not in result.output


class TestDeployHerokuRevertCommand:
    """Tests for deploy heroku revert CLI command."""

    def test_help(self, cli_runner):
        """djb deploy heroku revert --help works."""
        result = cli_runner.invoke(djb_cli, ["deploy", "heroku", "revert", "--help"])
        assert result.exit_code == 0
        assert "Revert to a previous deployment" in result.output
        assert "--skip-migrate" in result.output

    def test_revert_to_previous_commit(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner, djb_config
    ):
        """djb deploy heroku revert defaults to previous commit (HEAD~1)."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            mock_cmd_runner.run.side_effect = make_revert_side_effect(
                log_stdout="abc1234 Previous commit\n"
            )

            result = cli_runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp", "revert"], input="y\n"
            )

        assert "No git hash provided, using previous commit" in result.output

    def test_revert_to_specific_commit(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner, djb_config
    ):
        """Revert CLI shows correct output message when given specific commit hash."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            mock_cmd_runner.run.side_effect = make_revert_side_effect(
                log_stdout="def5678 Specific commit\n"
            )

            result = cli_runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp", "revert", "def5678"], input="y\n"
            )

        assert "Reverting to: def5678" in result.output

    def test_revert_invalid_hash(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner, djb_config
    ):
        """djb deploy heroku revert with invalid hash shows error."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            mock_cmd_runner.run.side_effect = make_revert_side_effect()
            # runner.check() is used for git cat-file validation, return False for invalid hash
            mock_cmd_runner.check.return_value = False

            result = cli_runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp", "revert", "invalid"]
            )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_revert_cancelled(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner, djb_config
    ):
        """djb deploy heroku revert can be cancelled at confirmation."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            mock_cmd_runner.run.side_effect = make_revert_side_effect()

            result = cli_runner.invoke(
                djb_cli, ["deploy", "heroku", "--app", "testapp", "revert"], input="n\n"
            )

        assert result.exit_code == 1
        assert "Revert cancelled" in result.output

    def test_revert_skip_migrate(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner, djb_config
    ):
        """djb deploy heroku revert --skip-migrate skips migrations."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            mock_cmd_runner.run.side_effect = make_revert_side_effect()

            result = cli_runner.invoke(
                djb_cli,
                ["deploy", "heroku", "--app", "testapp", "revert", "--skip-migrate"],
                input="y\n",
            )

        assert "Database migrations" in result.output  # logger.skip() format


class TestDeployHerokuSeedCommand:
    """Tests for deploy heroku seed CLI command."""

    def test_help_unconfigured(self, cli_runner, djb_config):
        """deploy heroku seed --help shows configuration instructions when no seed_command is configured."""
        # djb_config fixture has seed_command=None by default
        # Don't pass --project-dir since djb_config patches get_djb_config
        result = cli_runner.invoke(
            djb_cli,
            ["deploy", "heroku", "seed", "--help"],
        )

        assert result.exit_code == 0
        assert "Run the host project's seed command on Heroku" in result.output
        assert "WARNING: This modifies the production database on Heroku!" in result.output
        assert "No seed_command is currently configured" in result.output
        assert "djb config seed_command" in result.output

    def test_help_configured(self, cli_runner, make_djb_config):
        """Help shows djb options plus host command help when seed_command is configured."""

        # Create a mock host command with help text
        @click.command()
        @click.option("--truncate", is_flag=True, help="Clear database before seeding")
        def mock_seed(truncate):
            """A test seed command for the database."""

        config = make_djb_config(DjbConfig(seed_command="myapp.cli:seed"))
        with (
            patch("djb.cli.djb.get_djb_config", return_value=config),
            patch("djb.cli.heroku.heroku.load_seed_command") as mock_load,
        ):
            mock_load.return_value = mock_seed

            result = cli_runner.invoke(
                djb_cli,
                ["deploy", "heroku", "seed", "--help"],
            )

        assert result.exit_code == 0
        # Check djb command's own help is shown
        assert "Run seed command on Heroku" in result.output
        assert "--here-be-dragons" in result.output
        assert "--app" in result.output
        # Check host command help is appended
        assert "Configured seed command: myapp.cli:seed" in result.output
        assert "--- Host command help ---" in result.output
        assert "A test seed command for the database" in result.output

    def test_requires_here_be_dragons(self, cli_runner):
        """djb deploy heroku seed requires --here-be-dragons."""
        result = cli_runner.invoke(djb_cli, ["deploy", "heroku", "--app", "testapp", "seed"])
        assert result.exit_code != 0
        assert "Missing option '--here-be-dragons'" in result.output

    def test_builds_correct_heroku_command(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner
    ):
        """djb deploy heroku seed builds correct heroku run command."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            result = cli_runner.invoke(
                djb_cli,
                ["deploy", "heroku", "--app", "testapp", "seed", "--here-be-dragons"],
            )

        assert result.exit_code == 0
        # Verify the heroku run command was called correctly
        # Find the run call that has "heroku run" (uses show_output=True)
        heroku_run_calls = [
            call for call in mock_cmd_runner.run.call_args_list if "heroku" in str(call)
        ]
        assert len(heroku_run_calls) > 0
        call_args = heroku_run_calls[-1][0][0]  # Get the last heroku call's cmd
        assert call_args == [
            "heroku",
            "run",
            "--no-notify",
            "--app",
            "testapp",
            "--",
            "djb",
            "seed",
        ]

    def test_extra_args_passed_to_seed(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner
    ):
        """Extra args (like --truncate) are passed through to djb seed."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            result = cli_runner.invoke(
                djb_cli,
                [
                    "deploy",
                    "heroku",
                    "--app",
                    "testapp",
                    "seed",
                    "--here-be-dragons",
                    "--",
                    "--truncate",
                ],
            )

        assert result.exit_code == 0
        # Find the heroku run call
        heroku_run_calls = [
            call for call in mock_cmd_runner.run.call_args_list if "heroku" in str(call)
        ]
        call_args = heroku_run_calls[-1][0][0]
        assert call_args == [
            "heroku",
            "run",
            "--no-notify",
            "--app",
            "testapp",
            "--",
            "djb",
            "seed",
            "--truncate",
        ]

    def test_inherits_app_from_parent(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner
    ):
        """djb deploy heroku seed inherits app from parent command."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            result = cli_runner.invoke(
                djb_cli,
                ["deploy", "heroku", "--app", "parentapp", "seed", "--here-be-dragons"],
            )

        assert result.exit_code == 0
        # Find the heroku run call
        heroku_run_calls = [
            call for call in mock_cmd_runner.run.call_args_list if "heroku" in str(call)
        ]
        call_args = heroku_run_calls[-1][0][0]
        assert "parentapp" in call_args

    def test_heroku_command_failure(self, cli_runner, mock_project_with_git_repo, mock_cmd_runner):
        """djb deploy heroku seed reports heroku run failure."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="")
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):
            result = cli_runner.invoke(
                djb_cli,
                ["deploy", "heroku", "--app", "testapp", "seed", "--here-be-dragons"],
            )

        assert result.exit_code == 1
        assert "Seed failed on 'testapp'" in result.output


class TestDeployGroup:
    """Tests for deploy command group."""

    def test_deploy_help(self, cli_runner):
        """djb deploy --help shows subcommands."""
        result = cli_runner.invoke(djb_cli, ["deploy", "--help"])
        assert result.exit_code == 0
        assert "heroku" in result.output
        # revert is a subcommand of heroku, not a direct command of deploy
        # Check that it's in the Commands section (the subcommands list)
        commands_section = (
            result.output.split("Commands:")[1] if "Commands:" in result.output else ""
        )
        assert "  revert" not in commands_section


_NO_CONFIG = object()  # sentinel for "no config object"


class TestGetAppOrFail:
    """Unit tests for _get_app_or_fail helper function.

    This function resolves the Heroku app name from explicit --app value
    or falls back to config.project_name.
    """

    @pytest.mark.parametrize(
        "app,config_project_name,expected",
        [
            pytest.param("myapp", None, "myapp", id="explicit_app_no_config"),
            pytest.param(
                "explicit-app", "from-config", "explicit-app", id="explicit_takes_precedence"
            ),
            pytest.param(None, "from-config", "from-config", id="falls_back_to_config"),
        ],
    )
    def test_returns_app_name(self, app, config_project_name, expected):
        """_get_app_or_fail returns correct app name."""
        config = None
        if config_project_name is not None:
            config = MagicMock(spec=DjbConfig)
            config.project_name = config_project_name

        with patch("djb.cli.heroku.heroku.logger"):
            result = _get_app_or_fail(app, config)

        assert result == expected

    @pytest.mark.parametrize(
        "config_project_name",
        [
            pytest.param(_NO_CONFIG, id="no_config"),
            pytest.param(None, id="project_name_is_none"),
            pytest.param("", id="project_name_is_empty"),
        ],
    )
    def test_raises_when_no_app_resolvable(self, config_project_name):
        """_get_app_or_fail raises ClickException when no app can be determined."""
        if config_project_name is _NO_CONFIG:
            config = None
        else:
            config = MagicMock(spec=DjbConfig)
            config.project_name = config_project_name

        with pytest.raises(click.ClickException) as excinfo:
            _get_app_or_fail(None, config)

        assert "No app name provided" in str(excinfo.value)

    def test_logs_info_when_using_config(self):
        """_get_app_or_fail logs info message when using config.project_name."""
        mock_config = MagicMock(spec=DjbConfig)
        mock_config.project_name = "test-project"

        with patch("djb.cli.heroku.heroku.logger") as mock_logger:
            _get_app_or_fail(None, mock_config)

        mock_logger.info.assert_called_once()
        assert "test-project" in mock_logger.info.call_args[0][0]


class TestRunHerokuMigrations:
    """Direct unit tests for _run_heroku_migrations helper function.

    This function runs Django migrations on Heroku via `heroku run`.
    """

    def test_runs_heroku_migrate_command(self, mock_cmd_runner):
        """_run_heroku_migrations executes correct heroku run command."""
        with patch("djb.cli.heroku.heroku.logger"):
            _run_heroku_migrations(mock_cmd_runner, "myapp", skip=False)

        mock_cmd_runner.run.assert_called_once()
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
            "migrate",
        ]

    def test_uses_correct_label_and_show_output(self, mock_cmd_runner):
        """_run_heroku_migrations sets label and show_output=True."""
        with patch("djb.cli.heroku.heroku.logger"):
            _run_heroku_migrations(mock_cmd_runner, "myapp", skip=False)

        _, kwargs = mock_cmd_runner.run.call_args
        assert kwargs["label"] == "Running database migrations on Heroku"
        assert kwargs.get("show_output") is True

    def test_raises_on_migration_failure(self, mock_cmd_runner):
        """_run_heroku_migrations raises ClickException when migrations fail."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="")

        with patch("djb.cli.heroku.heroku.logger"):
            with pytest.raises(click.ClickException) as excinfo:
                _run_heroku_migrations(mock_cmd_runner, "myapp", skip=False)

        assert "Migrations failed on Heroku" in str(excinfo.value)

    def test_skips_migrations_when_skip_is_true(self, mock_cmd_runner):
        """_run_heroku_migrations skips migrations when skip=True."""
        with patch("djb.cli.heroku.heroku.logger") as mock_logger:
            _run_heroku_migrations(mock_cmd_runner, "myapp", skip=True)

        # run should not be called for migrations
        # Note: mock starts with a default call, so check no "migrate" in calls
        migrate_calls = [
            call for call in mock_cmd_runner.run.call_args_list if "migrate" in str(call)
        ]
        assert len(migrate_calls) == 0
        # logger.skip should be called
        mock_logger.skip.assert_called_once_with("Database migrations")

    def test_passes_done_msg_to_runner(self, mock_cmd_runner):
        """_run_heroku_migrations passes done_msg to runner for logging."""
        with patch("djb.cli.heroku.heroku.logger"):
            _run_heroku_migrations(mock_cmd_runner, "myapp", skip=False)

        _, kwargs = mock_cmd_runner.run.call_args
        assert kwargs.get("done_msg") == "Migrations complete"

    def test_uses_app_name_in_command(self, mock_cmd_runner):
        """_run_heroku_migrations includes the app name in the command."""
        with patch("djb.cli.heroku.heroku.logger"):
            _run_heroku_migrations(mock_cmd_runner, "different-app", skip=False)

        call_args = mock_cmd_runner.run.call_args[0][0]
        assert "--app" in call_args
        app_index = call_args.index("--app")
        assert call_args[app_index + 1] == "different-app"


class TestResolveHerokuApp:
    """Direct unit tests for _resolve_heroku_app Click callback.

    This callback resolves the Heroku app name from --app flag or config.project_name.
    """

    def test_returns_explicit_value_when_provided(self):
        """_resolve_heroku_app returns explicit --app value unchanged."""
        mock_ctx = MagicMock()
        mock_param = MagicMock()

        result = _resolve_heroku_app(mock_ctx, mock_param, "explicit-app")

        assert result == "explicit-app"

    def test_uses_config_project_name_when_no_value(self, mock_cli_ctx):
        """_resolve_heroku_app uses config.project_name when --app not provided."""
        mock_ctx = MagicMock()
        mock_cli_ctx.config = MagicMock(spec=DjbConfig)
        mock_cli_ctx.config.project_name = "from-context"
        mock_ctx.find_object.return_value = mock_cli_ctx
        mock_param = MagicMock()

        with patch("djb.cli.heroku.heroku.logger"):
            result = _resolve_heroku_app(mock_ctx, mock_param, None)

        assert result == "from-context"

    def test_raises_bad_parameter_when_no_app_available(self):
        """_resolve_heroku_app raises BadParameter when no app can be determined."""
        mock_ctx = MagicMock()
        mock_ctx.find_object.return_value = None
        mock_param = MagicMock()

        with pytest.raises(click.BadParameter) as excinfo:
            _resolve_heroku_app(mock_ctx, mock_param, None)

        assert "No app name provided" in str(excinfo.value)

    def test_raises_when_cli_context_has_no_config(self, mock_cli_ctx):
        """_resolve_heroku_app raises BadParameter when CLI context has no config."""
        mock_ctx = MagicMock()
        mock_cli_ctx.config = None  # testing error case
        mock_ctx.find_object.return_value = mock_cli_ctx
        mock_param = MagicMock()

        with pytest.raises(click.BadParameter) as excinfo:
            _resolve_heroku_app(mock_ctx, mock_param, None)

        assert "No app name provided" in str(excinfo.value)

    def test_raises_when_config_has_no_project_name(self, mock_cli_ctx):
        """_resolve_heroku_app raises BadParameter when config has no project_name."""
        mock_ctx = MagicMock()
        mock_cli_ctx.config = MagicMock(spec=DjbConfig)
        mock_cli_ctx.config.project_name = None
        mock_ctx.find_object.return_value = mock_cli_ctx
        mock_param = MagicMock()

        with pytest.raises(click.BadParameter) as excinfo:
            _resolve_heroku_app(mock_ctx, mock_param, None)

        assert "No app name provided" in str(excinfo.value)

    def test_logs_info_when_using_config(self, mock_cli_ctx):
        """_resolve_heroku_app logs info message when using config.project_name."""
        mock_ctx = MagicMock()
        mock_cli_ctx.config = MagicMock(spec=DjbConfig)
        mock_cli_ctx.config.project_name = "test-project"
        mock_ctx.find_object.return_value = mock_cli_ctx
        mock_param = MagicMock()

        with patch("djb.cli.heroku.heroku.logger") as mock_logger:
            _resolve_heroku_app(mock_ctx, mock_param, None)

        mock_logger.info.assert_called_once()
        assert "test-project" in mock_logger.info.call_args[0][0]


def _mock_path_exists_no_frontend():
    """Create a Path.exists mock that returns False for frontend directory."""
    original_exists = Path.exists

    def mock_exists(self):
        path_str = str(self)
        if path_str.endswith("frontend"):
            return False
        if ".git" in path_str:
            return True
        return original_exists(self)

    return mock_exists


class TestLocalBuildMissingFrontendDir:
    """Test --local-build behavior when frontend directory doesn't exist."""

    def test_local_build_warns_when_frontend_dir_missing(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner
    ):
        """djb deploy heroku --local-build logs warning when frontend_dir doesn't exist."""
        mock_cmd_runner.run.side_effect = _deploy_mock_side_effect
        with (
            patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo),
            patch.object(Path, "exists", _mock_path_exists_no_frontend()),
            patch.object(Path, "is_dir", _mock_path_exists_no_frontend()),
        ):
            result = cli_runner.invoke(
                djb_cli, ["-y", "deploy", "heroku", "--app", "testapp", "--local-build"]
            )

        # Should log warning about missing frontend directory
        assert "Frontend directory not found" in result.output
        # Should NOT show "Building frontend assets locally" since we skipped
        # (the warning replaces the build step)
        assert result.exit_code == 0

    def test_local_build_skips_frontend_build_commands(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner
    ):
        """djb deploy heroku --local-build skips bun build when frontend_dir missing."""
        mock_cmd_runner.run.side_effect = _deploy_mock_side_effect
        with (
            patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo),
            patch.object(Path, "exists", _mock_path_exists_no_frontend()),
            patch.object(Path, "is_dir", _mock_path_exists_no_frontend()),
        ):

            cli_runner.invoke(
                djb_cli, ["-y", "deploy", "heroku", "--app", "testapp", "--local-build"]
            )

        # Check that "bun run build" was not called
        bun_calls = [call for call in mock_cmd_runner.run.call_args_list if "bun" in str(call)]
        assert len(bun_calls) == 0, "bun build should not be called when frontend_dir missing"

        # Check that collectstatic was not called either (it's only called after bun build)
        collectstatic_calls = [
            call for call in mock_cmd_runner.run.call_args_list if "collectstatic" in str(call)
        ]
        assert (
            len(collectstatic_calls) == 0
        ), "collectstatic should not be called when frontend_dir missing"


def make_run_cmd_side_effect(
    *,
    auth_returncode: int = 0,
    git_status_stdout: str = "",
    branch_stdout: str = "main\n",
    commit_stdout: str = "abc1234\n",
) -> Callable:
    """Factory for creating run_cmd side_effect functions for _deploy_heroku_impl tests.

    Args:
        auth_returncode: Return code for heroku auth:whoami (0 = logged in)
        git_status_stdout: Output for git status --porcelain (empty = no uncommitted changes)
        branch_stdout: Output for git branch --show-current
        commit_stdout: Output for git rev-parse HEAD
    """

    def side_effect(cmd, *args, **kwargs):
        # Handle fail_msg for auth check
        if cmd == ["heroku", "auth:whoami"]:
            if auth_returncode != 0:
                fail_msg = kwargs.get("fail_msg")
                if isinstance(fail_msg, Exception):
                    raise fail_msg
            return Mock(returncode=auth_returncode, stdout="user@example.com\n", stderr="")
        if cmd == ["git", "status", "--porcelain"]:
            return Mock(returncode=0, stdout=git_status_stdout, stderr="")
        if cmd == ["git", "branch", "--show-current"]:
            return Mock(returncode=0, stdout=branch_stdout, stderr="")
        if cmd == ["git", "rev-parse", "HEAD"]:
            return Mock(returncode=0, stdout=commit_stdout, stderr="")
        if cmd == ["git", "fetch", "heroku"]:
            return Mock(returncode=0, stdout="", stderr="")
        if len(cmd) >= 3 and cmd[0] == "git" and cmd[1] == "rev-list" and "--count" in cmd:
            return Mock(returncode=0, stdout="0\n", stderr="")
        # Default: success
        return Mock(returncode=0, stdout="", stderr="")

    return side_effect


def _mock_path_exists(git_exists: bool = True, key_exists: bool = True):
    """Create a Path.exists mock that returns appropriate values for deploy tests.

    Args:
        git_exists: Whether .git directory exists.
        key_exists: Whether keys.txt file exists.

    Returns True for .git, secrets, frontend directories based on git_exists.
    """
    original_exists = Path.exists

    def mock_exists(self):
        path_str = str(self)
        if ".git" in path_str:
            return git_exists
        if path_str.endswith("secrets") or path_str.endswith("frontend"):
            return True
        # For key files in FAKE_PROJECT_DIR
        if "keys.txt" in path_str and "/fake/" in path_str:
            return key_exists
        return original_exists(self)

    return mock_exists


@pytest.fixture
def deploy_impl_mocks(mock_cmd_runner):
    """Mock all external dependencies for _deploy_heroku_impl tests.

    Mocks directory existence for:
    - .git directory
    - secrets/ directory
    - frontend/ directory

    Patches:
    - mock_cmd_runner.run (for all commands: git push, migrations, git commands, heroku config:set)
    - SecretsManager (handles secrets loading and GPG-protected keys)
    - click.confirm
    - logger
    - Path.exists (for directory checks)

    Yields a dict with all mocks for configuration in tests.
    """
    # Create a mock SecretsManager instance
    mock_secrets_manager_instance = Mock()
    mock_secrets_manager_instance.load_secrets.return_value = {}

    with (
        patch("djb.cli.heroku.heroku.SecretsManager") as mock_secrets_manager_class,
        patch("djb.cli.heroku.heroku.click.confirm") as mock_confirm,
        patch("djb.cli.heroku.heroku.logger") as mock_logger,
        patch.object(Path, "exists", _mock_path_exists(git_exists=True)),
        patch.object(Path, "is_dir", _mock_path_exists(git_exists=True)),
    ):
        # Default setup
        mock_cmd_runner.run.side_effect = make_run_cmd_side_effect()
        mock_secrets_manager_class.return_value = mock_secrets_manager_instance
        mock_confirm.return_value = True

        yield {
            "run": mock_cmd_runner.run,
            "secrets_manager_class": mock_secrets_manager_class,
            "secrets_manager": mock_secrets_manager_instance,
            "confirm": mock_confirm,
            "logger": mock_logger,
            "project_dir": FAKE_PROJECT_DIR,
            "runner": mock_cmd_runner,
        }


class TestDeployHerokuImpl:
    """Direct unit tests for _deploy_heroku_impl function.

    This function contains ~180 lines of core deployment logic that was
    previously only tested via CLI integration tests. These tests verify:
    - Auth checking (heroku auth:whoami)
    - Git repo verification (.git directory check)
    - Secrets sync orchestration (protected/unprotected key decision tree)
    - Config var filtering (HEROKU_MANAGED_KEYS and >500 char filtering)
    - Uncommitted changes check (warning + confirmation)
    """

    def _call_deploy_impl(self, mocks, **kwargs):
        """Helper to call _deploy_heroku_impl with default values."""
        defaults = {
            "app": "testapp",
            "mode": Mode.PRODUCTION,
            "domains": ["test.example.com"],
            "local_build": False,
            "skip_migrate": True,  # Skip migrations by default for faster tests
            "skip_secrets": False,
            "yes": True,  # Auto-confirm by default
            "repo_root": mocks["project_dir"],
            "frontend_dir": mocks["project_dir"] / "frontend",
            "secrets_dir": mocks["project_dir"] / "secrets",
            "key_path": mocks["project_dir"] / "keys.txt",
        }
        defaults.update(kwargs)
        config = HerokuDeployConfig(**defaults)
        return _deploy_heroku_impl(mocks["runner"], config)

    def test_auth_failure_raises_click_exception(self, deploy_impl_mocks):
        """_deploy_heroku_impl raises ClickException on Heroku auth failure."""
        mocks = deploy_impl_mocks
        mocks["run"].side_effect = make_run_cmd_side_effect(auth_returncode=1)

        with pytest.raises(click.ClickException) as excinfo:
            self._call_deploy_impl(mocks)

        assert "Not logged into Heroku" in str(excinfo.value)

    def test_missing_git_repo_raises_click_exception(self, deploy_impl_mocks):
        """_deploy_heroku_impl raises ClickException when .git directory is missing."""
        mocks = deploy_impl_mocks

        # Override the Path.exists mock to return False for .git
        with (
            patch.object(Path, "exists", _mock_path_exists(git_exists=False)),
            patch.object(Path, "is_dir", _mock_path_exists(git_exists=False)),
            pytest.raises(click.ClickException) as excinfo,
        ):
            self._call_deploy_impl(mocks)

        assert "Not in a git repository" in str(excinfo.value)

    def test_skip_secrets_logs_skip_message(self, deploy_impl_mocks):
        """_deploy_heroku_impl logs skip message when skip_secrets=True."""
        mocks = deploy_impl_mocks

        self._call_deploy_impl(mocks, skip_secrets=True)

        mocks["logger"].skip.assert_any_call("Secrets sync")

    def test_secrets_synced_via_heroku_config_set(self, deploy_impl_mocks):
        """_deploy_heroku_impl syncs secrets to Heroku via heroku config:set."""
        mocks = deploy_impl_mocks
        # Key path existence is mocked, SecretsManager is mocked
        key_path = mocks["project_dir"] / "keys.txt"

        mocks["secrets_manager"].load_secrets.return_value = {
            "SECRET_KEY": "mysecretkey",
            "API_TOKEN": "mytoken",
        }

        self._call_deploy_impl(mocks, key_path=key_path)

        # Verify subprocess.run was called with heroku config:set for secrets
        config_set_calls = [
            call for call in mocks["run"].call_args_list if "config:set" in str(call)
        ]
        # Find the call that sets secrets (not DJB_DOMAINS)
        secrets_calls = [call for call in config_set_calls if "SECRET_KEY" in str(call)]
        assert len(secrets_calls) >= 1
        call_args = secrets_calls[0][0][0]
        assert "heroku" in call_args
        assert "config:set" in call_args
        assert "SECRET_KEY=mysecretkey" in call_args
        assert "API_TOKEN=mytoken" in call_args

    def test_secrets_manager_is_used(self, deploy_impl_mocks):
        """_deploy_heroku_impl uses SecretsManager to load secrets."""
        mocks = deploy_impl_mocks
        mocks["secrets_manager"].load_secrets.return_value = {"SECRET": "value"}

        self._call_deploy_impl(mocks)

        # Verify SecretsManager was instantiated with correct args
        mocks["secrets_manager_class"].assert_called_once()
        # Verify load_secrets was called
        mocks["secrets_manager"].load_secrets.assert_called_once()

    def test_heroku_managed_keys_are_filtered(self, deploy_impl_mocks):
        """_deploy_heroku_impl filters HEROKU_MANAGED_KEYS from config vars."""
        mocks = deploy_impl_mocks
        # Key path existence is mocked, SecretsManager is mocked
        key_path = mocks["project_dir"] / "keys.txt"

        mocks["secrets_manager"].load_secrets.return_value = {
            "DATABASE_URL": "postgres://...",
            "SECRET_KEY": "mysecret",
        }

        self._call_deploy_impl(mocks, key_path=key_path)

        # Verify DATABASE_URL was skipped
        skip_calls = [str(call) for call in mocks["logger"].skip.call_args_list]
        assert any("DATABASE_URL (managed by Heroku)" in call for call in skip_calls)

        # Verify SECRET_KEY was set (not filtered)
        config_set_calls = [
            call for call in mocks["run"].call_args_list if "config:set" in str(call)
        ]
        if config_set_calls:
            call_args = config_set_calls[0][0][0]
            assert "SECRET_KEY=mysecret" in call_args
            assert "DATABASE_URL" not in str(call_args)

    def test_large_values_are_filtered(self, deploy_impl_mocks):
        """_deploy_heroku_impl filters values > 500 chars from config vars."""
        mocks = deploy_impl_mocks
        # Key path existence is mocked, SecretsManager is mocked
        key_path = mocks["project_dir"] / "keys.txt"

        large_value = "x" * 501
        mocks["secrets_manager"].load_secrets.return_value = {
            "LARGE_KEY": large_value,
            "SMALL_KEY": "small",
        }

        self._call_deploy_impl(mocks, key_path=key_path)

        # Verify LARGE_KEY was skipped
        skip_calls = [str(call) for call in mocks["logger"].skip.call_args_list]
        assert any("LARGE_KEY (value too large)" in call for call in skip_calls)

        # Verify SMALL_KEY was set
        config_set_calls = [
            call for call in mocks["run"].call_args_list if "config:set" in str(call)
        ]
        if config_set_calls:
            call_args = config_set_calls[0][0][0]
            assert "SMALL_KEY=small" in call_args
            assert "LARGE_KEY" not in str(call_args)

    def test_uncommitted_changes_prompts_confirmation(self, deploy_impl_mocks):
        """_deploy_heroku_impl prompts for confirmation when uncommitted changes exist."""
        mocks = deploy_impl_mocks
        mocks["run"].side_effect = make_run_cmd_side_effect(
            git_status_stdout="M modified_file.py\n"
        )
        mocks["confirm"].return_value = True

        self._call_deploy_impl(mocks, yes=False, skip_secrets=True)

        # Verify warning was logged
        warning_calls = [str(call) for call in mocks["logger"].warning.call_args_list]
        assert any("uncommitted changes" in call for call in warning_calls)

        # Verify confirm was called
        confirm_calls = [str(call) for call in mocks["confirm"].call_args_list]
        assert any("Continue with deployment?" in call for call in confirm_calls)

    def test_uncommitted_changes_can_cancel_deployment(self, deploy_impl_mocks):
        """_deploy_heroku_impl cancels deployment when user declines uncommitted changes confirmation."""
        mocks = deploy_impl_mocks
        mocks["run"].side_effect = make_run_cmd_side_effect(
            git_status_stdout="M modified_file.py\n"
        )
        mocks["confirm"].return_value = False

        with pytest.raises(click.ClickException) as excinfo:
            self._call_deploy_impl(mocks, yes=False, skip_secrets=True)

        assert "Deployment cancelled" in str(excinfo.value)

    def test_placeholder_secrets_prompts_confirmation(self, deploy_impl_mocks):
        """_deploy_heroku_impl prompts for confirmation when placeholder secrets exist."""
        mocks = deploy_impl_mocks
        # Key path existence is mocked, SecretsManager is mocked
        key_path = mocks["project_dir"] / "keys.txt"

        mocks["secrets_manager"].load_secrets.return_value = {
            "SECRET_KEY": "CHANGE-ME-secret-key",
        }
        mocks["confirm"].return_value = True

        self._call_deploy_impl(mocks, yes=False, key_path=key_path)

        # Verify warning was logged
        warning_calls = [str(call) for call in mocks["logger"].warning.call_args_list]
        assert any("placeholder values" in call for call in warning_calls)

    def test_yes_flag_skips_uncommitted_confirmation(self, deploy_impl_mocks):
        """_deploy_heroku_impl skips uncommitted changes confirmation when yes=True."""
        mocks = deploy_impl_mocks
        mocks["run"].side_effect = make_run_cmd_side_effect(
            git_status_stdout="M modified_file.py\n"
        )

        self._call_deploy_impl(mocks, yes=True, skip_secrets=True)

        # confirm should not have been called for uncommitted changes
        confirm_calls = [str(call) for call in mocks["confirm"].call_args_list]
        # Since yes=True, no confirmation should be needed
        uncommitted_confirm = [c for c in confirm_calls if "Continue with deployment?" in c]
        assert len(uncommitted_confirm) == 0

    def test_missing_key_warns_and_skips_secrets(self, deploy_impl_mocks):
        """_deploy_heroku_impl warns and skips secrets sync when age key is missing."""
        mocks = deploy_impl_mocks

        # Make SecretsManager raise FileNotFoundError (simulating missing key)
        mocks["secrets_manager"].load_secrets.side_effect = SopsError("Age key not found")

        self._call_deploy_impl(mocks)

        # Verify warning was logged
        warning_calls = [str(call) for call in mocks["logger"].warning.call_args_list]
        assert any("Age key not found" in call for call in warning_calls)

    def test_nested_secrets_are_flattened(self, deploy_impl_mocks):
        """_deploy_heroku_impl flattens nested secret dicts correctly."""
        mocks = deploy_impl_mocks
        # Key path existence is mocked, SecretsManager is mocked
        key_path = mocks["project_dir"] / "keys.txt"

        mocks["secrets_manager"].load_secrets.return_value = {
            "AWS": {
                "ACCESS_KEY_ID": "AKIAEXAMPLE",
                "SECRET_ACCESS_KEY": "secret",
            }
        }

        self._call_deploy_impl(mocks, key_path=key_path)

        # Verify flattened keys were set
        config_set_calls = [
            call for call in mocks["run"].call_args_list if "config:set" in str(call)
        ]
        if config_set_calls:
            call_args = config_set_calls[0][0][0]
            assert "AWS_ACCESS_KEY_ID=AKIAEXAMPLE" in call_args
            assert "AWS_SECRET_ACCESS_KEY=secret" in call_args

    def test_detached_head_uses_empty_branch_in_push(self, deploy_impl_mocks):
        """Detached HEAD state (empty branch) is passed to git push.

        Documents current behavior: when git branch --show-current returns empty
        (detached HEAD), the push uses :main refspec. This test verifies behavior
        and documents that an empty branch may cause issues.
        """
        mocks = deploy_impl_mocks
        mocks["run"].side_effect = make_run_cmd_side_effect(
            branch_stdout=""  # Empty = detached HEAD
        )

        self._call_deploy_impl(mocks, skip_secrets=True)

        # Find the heroku push call (not the tags push)
        heroku_push_calls = [
            call
            for call in mocks["run"].call_args_list
            if "push" in str(call) and "heroku" in str(call)
        ]
        assert len(heroku_push_calls) == 1
        # In detached HEAD, the push command will be: git push heroku :main --force
        # This documents the current behavior (empty branch before the colon)
        push_cmd = heroku_push_calls[0][0][0]
        assert ":main" in push_cmd


class TestLocalBuildOption:
    """Tests for --local-build option behavior (failure and edge cases)."""

    def _call_deploy_impl(self, mocks, **kwargs):
        """Helper to call _deploy_heroku_impl with default values."""
        defaults = {
            "app": "testapp",
            "mode": Mode.PRODUCTION,
            "domains": ["test.example.com"],
            "local_build": True,  # Default to True for this test class
            "skip_migrate": True,
            "skip_secrets": True,  # Skip secrets to simplify tests
            "yes": True,
            "repo_root": mocks["project_dir"],
            "frontend_dir": mocks["project_dir"] / "frontend",
            "secrets_dir": mocks["project_dir"] / "secrets",
            "key_path": mocks["project_dir"] / "keys.txt",
        }
        defaults.update(kwargs)
        config = HerokuDeployConfig(**defaults)
        return _deploy_heroku_impl(mocks["runner"], config)

    def test_bun_build_failure_raises_exception(self, deploy_impl_mocks):
        """_deploy_heroku_impl raises ClickException on bun run build failure."""
        mocks = deploy_impl_mocks

        def run_cmd_side_effect(cmd, *args, **kwargs):
            if cmd == ["bun", "run", "build"]:
                raise click.ClickException("Command failed: bun run build")
            return make_run_cmd_side_effect()(cmd, *args, **kwargs)

        mocks["run"].side_effect = run_cmd_side_effect

        with pytest.raises(click.ClickException) as excinfo:
            self._call_deploy_impl(mocks)

        assert "bun run build" in str(excinfo.value)

    def test_collectstatic_failure_raises_exception(self, deploy_impl_mocks):
        """_deploy_heroku_impl raises ClickException on collectstatic failure."""
        mocks = deploy_impl_mocks

        def run_cmd_side_effect(cmd, *args, **kwargs):
            if cmd == ["bun", "run", "build"]:
                return Mock(returncode=0, stdout="", stderr="")
            if "collectstatic" in cmd:
                raise click.ClickException("Command failed: collectstatic")
            return make_run_cmd_side_effect()(cmd, *args, **kwargs)

        mocks["run"].side_effect = run_cmd_side_effect

        with pytest.raises(click.ClickException) as excinfo:
            self._call_deploy_impl(mocks)

        assert "collectstatic" in str(excinfo.value)

    def test_bun_failure_skips_collectstatic(self, deploy_impl_mocks):
        """_deploy_heroku_impl skips collectstatic when bun build fails."""
        mocks = deploy_impl_mocks
        commands_called = []

        def run_cmd_side_effect(cmd, *args, **kwargs):
            commands_called.append(cmd)
            if cmd == ["bun", "run", "build"]:
                raise click.ClickException("Build failed")
            return make_run_cmd_side_effect()(cmd, *args, **kwargs)

        mocks["run"].side_effect = run_cmd_side_effect

        with pytest.raises(click.ClickException):
            self._call_deploy_impl(mocks)

        # Verify bun was called
        assert ["bun", "run", "build"] in commands_called
        # Verify collectstatic was NOT called
        collectstatic_calls = [c for c in commands_called if "collectstatic" in str(c)]
        assert len(collectstatic_calls) == 0

    def test_runs_bun_build_and_collectstatic_in_sequence(self, deploy_impl_mocks):
        """_deploy_heroku_impl runs bun build and collectstatic in sequence."""
        mocks = deploy_impl_mocks
        commands_called = []

        def run_cmd_side_effect(cmd, *args, **kwargs):
            commands_called.append(cmd)
            return make_run_cmd_side_effect()(cmd, *args, **kwargs)

        mocks["run"].side_effect = run_cmd_side_effect

        self._call_deploy_impl(mocks)

        # Find indices of the build commands
        bun_index = None
        collectstatic_index = None
        for i, cmd in enumerate(commands_called):
            if cmd == ["bun", "run", "build"]:
                bun_index = i
            if "collectstatic" in str(cmd):
                collectstatic_index = i

        assert bun_index is not None, "bun run build was not called"
        assert collectstatic_index is not None, "collectstatic was not called"
        assert bun_index < collectstatic_index, "bun build should run before collectstatic"

    def test_correct_working_directories_for_build_commands(self, deploy_impl_mocks):
        """_deploy_heroku_impl uses correct working directories for build commands."""
        mocks = deploy_impl_mocks
        frontend_dir = mocks["project_dir"] / "frontend"
        repo_root = mocks["project_dir"]

        self._call_deploy_impl(mocks)

        # Check bun run build was called with frontend_dir
        bun_calls = [
            call for call in mocks["run"].call_args_list if call[0][0] == ["bun", "run", "build"]
        ]
        assert len(bun_calls) == 1
        assert bun_calls[0][1].get("cwd") == frontend_dir

        # Check collectstatic was called with repo_root
        collectstatic_calls = [
            call for call in mocks["run"].call_args_list if "collectstatic" in str(call[0][0])
        ]
        assert len(collectstatic_calls) == 1
        assert collectstatic_calls[0][1].get("cwd") == repo_root

    def test_local_build_false_skips_build_commands(self, deploy_impl_mocks):
        """_deploy_heroku_impl skips all build commands when local_build=False."""
        mocks = deploy_impl_mocks

        self._call_deploy_impl(mocks, local_build=False)

        # Verify bun build was not called
        bun_calls = [
            call for call in mocks["run"].call_args_list if call[0][0] == ["bun", "run", "build"]
        ]
        assert len(bun_calls) == 0

        # Verify collectstatic was not called
        collectstatic_calls = [
            call for call in mocks["run"].call_args_list if "collectstatic" in str(call[0][0])
        ]
        assert len(collectstatic_calls) == 0


class TestBranchNameEdgeCases:
    """Test branch names with special characters are handled correctly."""

    def _call_deploy_impl(self, mocks, **kwargs):
        """Helper to call _deploy_heroku_impl with default values."""
        defaults = {
            "app": "testapp",
            "mode": Mode.PRODUCTION,
            "domains": ["test.example.com"],
            "local_build": False,
            "skip_migrate": True,
            "skip_secrets": True,
            "yes": True,
            "repo_root": mocks["project_dir"],
            "frontend_dir": mocks["project_dir"] / "frontend",
            "secrets_dir": mocks["project_dir"] / "secrets",
            "key_path": mocks["project_dir"] / "keys.txt",
        }
        defaults.update(kwargs)
        config = HerokuDeployConfig(**defaults)
        return _deploy_heroku_impl(mocks["runner"], config)

    @pytest.mark.parametrize(
        "branch_name",
        [
            "feature/user-auth",
            "feature/api/v2",
            "fix-authentication-bug",
            "feature_new_auth",
        ],
        ids=["slash", "multiple_slashes", "hyphen", "underscore"],
    )
    def test_branch_with_special_characters(self, deploy_impl_mocks, branch_name):
        """_deploy_heroku_impl handles branch names with special characters correctly."""
        mocks = deploy_impl_mocks
        mocks["run"].side_effect = make_run_cmd_side_effect(branch_stdout=f"{branch_name}\n")

        self._call_deploy_impl(mocks)

        # Find the heroku push call (not the tags push)
        heroku_push_calls = [
            call
            for call in mocks["run"].call_args_list
            if "push" in str(call) and "heroku" in str(call)
        ]
        assert len(heroku_push_calls) == 1
        push_cmd = heroku_push_calls[0][0][0]
        assert f"{branch_name}:main" in push_cmd


class TestRevertEdgeCases:
    """Test edge cases for the revert command."""

    def test_revert_first_commit_fails_gracefully(
        self, cli_runner, mock_project_with_git_repo, mock_cmd_runner, djb_config
    ):
        """djb deploy heroku revert fails when no previous commit exists."""
        with patch("djb.cli.heroku.heroku.Path.cwd", return_value=mock_project_with_git_repo):

            def side_effect(cmd, *args, **kwargs):
                if cmd == ["heroku", "auth:whoami"]:
                    return Mock(returncode=0, stdout="", stderr="")
                # Simulate first commit - HEAD~1 doesn't exist
                if "rev-parse" in cmd and "HEAD~1" in cmd:
                    return Mock(returncode=128, stdout="", stderr="fatal: HEAD~1")
                return Mock(returncode=0, stdout="", stderr="")

            mock_cmd_runner.run.side_effect = side_effect

            result = cli_runner.invoke(djb_cli, ["deploy", "heroku", "--app", "testapp", "revert"])

        assert result.exit_code == 1
        assert "Could not determine previous commit" in result.output
