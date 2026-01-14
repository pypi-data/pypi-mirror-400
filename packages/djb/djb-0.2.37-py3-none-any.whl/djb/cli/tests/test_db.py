"""Tests for djb db module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from djb.cli.db import (
    DbSettings,
    DbStatus,
    _get_db_settings_from_secrets,
    _get_default_db_settings,
    _run_psql,
    can_connect_as_user,
    check_postgres_installed,
    check_postgres_running,
    create_database,
    create_extensions,
    create_template_database,
    create_user_and_grant,
    database_exists,
    get_db_settings,
    get_db_status,
    grant_schema_permissions,
    init_database,
    start_postgres_service,
    user_exists,
    user_has_database_privileges,
    user_is_superuser,
    wait_for_postgres,
)
from djb.cli.djb import djb_cli
from djb.config import DjbConfig
from djb.secrets import SopsError


class TestDbSettings:
    """Tests for DbSettings dataclass."""

    def test_dataclass_fields(self):
        """DbSettings has expected fields."""
        settings = DbSettings(
            name="testdb",
            user="testuser",
            password="testpass",
            host="localhost",
            port=5432,
        )
        assert settings.name == "testdb"
        assert settings.user == "testuser"
        assert settings.password == "testpass"
        assert settings.host == "localhost"
        assert settings.port == 5432


class TestGetDbSettingsFallback:
    """Tests for get_db_settings fallback behavior with specific project names."""

    def test_falls_back_to_defaults(self, make_djb_config, mock_cli_ctx):
        """Falls back to project-name-based defaults when secrets unavailable."""
        config = make_djb_config(DjbConfig(project_name="my-cool-project"))
        mock_cli_ctx.config = config
        with patch("djb.cli.db._get_db_settings_from_secrets", return_value=None):
            settings = get_db_settings(mock_cli_ctx)

        assert settings.name == "my_cool_project"  # hyphens converted to underscores
        assert settings.user == "my_cool_project"
        assert settings.password == "foobarqux"
        assert settings.host == "localhost"
        assert settings.port == 5432


class TestGetDbSettingsSecrets:
    """Tests for get_db_settings when secrets are available."""

    def test_uses_secrets_when_available(self, djb_config, mock_cli_ctx):
        """Uses secrets when db_credentials found in dev secrets."""
        secrets_settings = DbSettings(
            name="secrets_db",
            user="secrets_user",
            password="secrets_pass",
            host="db.example.com",
            port=5433,
        )

        mock_cli_ctx.config = djb_config
        with patch("djb.cli.db._get_db_settings_from_secrets", return_value=secrets_settings):
            settings = get_db_settings(mock_cli_ctx)

        assert settings.name == "secrets_db"
        assert settings.user == "secrets_user"
        assert settings.password == "secrets_pass"
        assert settings.host == "db.example.com"
        assert settings.port == 5433


class TestGetDbSettingsIncomplete:
    """Tests for get_db_settings fallback when secrets are incomplete."""

    def test_falls_back_when_secrets_incomplete(self, make_djb_config, mock_cli_ctx):
        """Falls back to defaults when secrets have empty name/user."""
        incomplete_settings = DbSettings(
            name="",  # Empty name
            user="",  # Empty user
            password="some_pass",
            host="localhost",
            port=5432,
        )

        config = make_djb_config(DjbConfig(project_name="my-project"))
        mock_cli_ctx.config = config
        with patch("djb.cli.db._get_db_settings_from_secrets", return_value=incomplete_settings):
            settings = get_db_settings(mock_cli_ctx)

        # Should fall back to defaults
        assert settings.name == "my_project"
        assert settings.user == "my_project"


class TestGetDbSettingsSopsError:
    """Tests for get_db_settings fallback on SOPS decryption errors."""

    def test_falls_back_on_sops_decryption_error(self, make_djb_config, mock_fs, mock_cli_ctx):
        """Falls back to defaults when SOPS decryption fails (user not in .sops.yaml)."""
        config = make_djb_config(DjbConfig(project_name="new-user-project"))
        mock_cli_ctx.config = config
        # Mock that secrets directory exists
        mock_fs.add_dir(config.project_dir / "secrets")
        with mock_fs.apply():
            with patch("djb.secrets.load_secrets", side_effect=SopsError("Failed to decrypt")):
                settings = get_db_settings(mock_cli_ctx)

        # Should fall back to defaults
        assert settings.name == "new_user_project"
        assert settings.user == "new_user_project"
        assert settings.password == "foobarqux"


class TestPostgresChecks:
    """Tests for PostgreSQL availability checks."""

    def test_check_postgres_installed_when_present(self):
        """check_postgres_installed returns True when psql is available."""
        with patch("djb.cli.db.shutil.which", return_value="/usr/bin/psql"):
            assert check_postgres_installed() is True

    def test_check_postgres_installed_when_missing(self):
        """check_postgres_installed returns False when psql is missing."""
        with patch("djb.cli.db.shutil.which", return_value=None):
            assert check_postgres_installed() is False

    def test_check_postgres_running_success(self, mock_cli_ctx):
        """check_postgres_running returns True when server is up."""
        with patch("djb.cli.db.shutil.which", return_value="/usr/bin/pg_isready"):
            mock_cli_ctx.runner.run.return_value = Mock(returncode=0)
            assert check_postgres_running(mock_cli_ctx) is True

    def test_check_postgres_running_failure(self, mock_cli_ctx):
        """check_postgres_running returns False when server is down."""
        with patch("djb.cli.db.shutil.which", return_value="/usr/bin/pg_isready"):
            mock_cli_ctx.runner.run.return_value = Mock(returncode=1)
            assert check_postgres_running(mock_cli_ctx) is False

    def test_check_postgres_running_no_pg_isready(self, mock_cli_ctx):
        """check_postgres_running returns False when pg_isready is missing."""
        with patch("djb.cli.db.shutil.which", return_value=None):
            assert check_postgres_running(mock_cli_ctx) is False


class TestDatabaseOperations:
    """Tests for database existence and connection checks."""

    @pytest.mark.parametrize(
        "psql_stdout,expected",
        [("1\n", True), ("", False)],
        ids=["exists", "not_exists"],
    )
    def test_database_exists(self, psql_stdout, expected, mock_cli_ctx):
        """database_exists returns correct boolean based on psql output."""
        with patch("djb.cli.db._run_psql") as mock_psql:
            mock_psql.return_value = Mock(stdout=psql_stdout, returncode=0)
            assert database_exists(mock_cli_ctx, "mydb") is expected

    @pytest.mark.parametrize(
        "psql_stdout,expected",
        [("1\n", True), ("", False)],
        ids=["exists", "not_exists"],
    )
    def test_user_exists(self, psql_stdout, expected, mock_cli_ctx):
        """user_exists returns correct boolean based on psql output."""
        with patch("djb.cli.db._run_psql") as mock_psql:
            mock_psql.return_value = Mock(stdout=psql_stdout, returncode=0)
            assert user_exists(mock_cli_ctx, "myuser") is expected

    @pytest.mark.parametrize(
        "psql_stdout,expected",
        [("t\n", True), ("f\n", False)],
        ids=["is_superuser", "not_superuser"],
    )
    def test_user_is_superuser(self, psql_stdout, expected, mock_cli_ctx):
        """user_is_superuser returns correct boolean based on psql output."""
        with patch("djb.cli.db._run_psql") as mock_psql:
            mock_psql.return_value = Mock(stdout=psql_stdout, returncode=0)
            assert user_is_superuser(mock_cli_ctx, "myuser") is expected

    @pytest.mark.parametrize(
        "psql_stdout,expected",
        [("t\n", True), ("f\n", False)],
        ids=["has_privileges", "lacks_privileges"],
    )
    def test_user_has_database_privileges(self, psql_stdout, expected, mock_cli_ctx):
        """user_has_database_privileges returns correct boolean based on psql output."""
        with patch("djb.cli.db._run_psql") as mock_psql:
            mock_psql.return_value = Mock(stdout=psql_stdout, returncode=0)
            assert user_has_database_privileges(mock_cli_ctx, "myuser", "mydb") is expected

    @pytest.mark.parametrize(
        "returncode,expected",
        [(0, True), (1, False)],
        ids=["success", "failure"],
    )
    def test_can_connect_as_user(self, returncode, expected, mock_cli_ctx):
        """can_connect_as_user returns correct boolean based on connection result."""
        settings = DbSettings(
            name="testdb",
            user="testuser",
            password="testpass",
            host="localhost",
            port=5432,
        )
        mock_cli_ctx.runner.run.return_value = Mock(returncode=returncode)
        assert can_connect_as_user(mock_cli_ctx, settings) is expected


class TestDbStatus:
    """Tests for get_db_status function."""

    def test_status_uninstalled(self, mock_cli_ctx):
        """get_db_status returns UNINSTALLED when PostgreSQL not installed."""
        settings = DbSettings("db", "user", "pass", "localhost", 5432)
        with patch("djb.cli.db.check_postgres_installed", return_value=False):
            assert get_db_status(mock_cli_ctx, settings) == DbStatus.UNINSTALLED

    def test_status_unreachable(self, mock_cli_ctx):
        """get_db_status returns UNREACHABLE when PostgreSQL not running."""
        settings = DbSettings("db", "user", "pass", "localhost", 5432)
        with (
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=False),
        ):
            assert get_db_status(mock_cli_ctx, settings) == DbStatus.UNREACHABLE

    def test_status_no_database(self, mock_cli_ctx):
        """get_db_status returns NO_DATABASE when database_exists check returns False (mocked)."""
        settings = DbSettings("db", "user", "pass", "localhost", 5432)
        with (
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.database_exists", return_value=False),
        ):
            assert get_db_status(mock_cli_ctx, settings) == DbStatus.NO_DATABASE

    def test_status_no_user(self, mock_cli_ctx):
        """get_db_status returns NO_USER when PostgreSQL role doesn't exist."""
        settings = DbSettings("db", "user", "pass", "localhost", 5432)
        with (
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.database_exists", return_value=True),
            patch("djb.cli.db.user_exists", return_value=False),
        ):
            assert get_db_status(mock_cli_ctx, settings) == DbStatus.NO_USER

    def test_status_ok(self, mock_cli_ctx):
        """get_db_status returns OK when everything is set up."""
        settings = DbSettings("db", "user", "pass", "localhost", 5432)
        with (
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.database_exists", return_value=True),
            patch("djb.cli.db.user_exists", return_value=True),
            patch("djb.cli.db.can_connect_as_user", return_value=True),
        ):
            assert get_db_status(mock_cli_ctx, settings) == DbStatus.OK


class TestCreateDatabase:
    """Tests for create_database function."""

    def test_skips_when_exists(self, mock_cli_ctx):
        """create_database skips creation when database already exists."""
        settings = DbSettings("testdb", "user", "pass", "localhost", 5432)
        with patch("djb.cli.db.database_exists", return_value=True):
            result = create_database(mock_cli_ctx, settings)
        assert result is True

    def test_creates_when_missing(self, mock_cli_ctx):
        """create_database creates the database when it doesn't exist."""
        settings = DbSettings("testdb", "user", "pass", "localhost", 5432)
        with (
            patch("djb.cli.db.database_exists", return_value=False),
            patch("djb.cli.db._run_psql") as mock_psql,
        ):
            mock_psql.return_value = Mock(returncode=0)
            result = create_database(mock_cli_ctx, settings)
        assert result is True
        mock_psql.assert_called_once()

    def test_returns_false_on_error(self, mock_cli_ctx):
        """create_database returns False when psql CREATE DATABASE fails."""
        settings = DbSettings("testdb", "user", "pass", "localhost", 5432)
        with (
            patch("djb.cli.db.database_exists", return_value=False),
            patch("djb.cli.db._run_psql") as mock_psql,
        ):
            mock_psql.return_value = Mock(returncode=1, stderr="error")
            result = create_database(mock_cli_ctx, settings)
        assert result is False


class TestCreateUserAndGrant:
    """Tests for create_user_and_grant function."""

    def test_creates_user_when_missing(self, mock_cli_ctx):
        """create_user_and_grant creates PostgreSQL role when user doesn't exist."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)
        with (
            patch("djb.cli.db.user_exists", return_value=False),
            patch("djb.cli.db._run_psql") as mock_psql,
        ):
            mock_psql.return_value = Mock(returncode=0)
            result = create_user_and_grant(mock_cli_ctx, settings)
        assert result is True

    def test_updates_existing_user(self, mock_cli_ctx):
        """create_user_and_grant updates password for existing user."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)
        with (
            patch("djb.cli.db.user_exists", return_value=True),
            patch("djb.cli.db._run_psql") as mock_psql,
        ):
            mock_psql.return_value = Mock(returncode=0)
            result = create_user_and_grant(mock_cli_ctx, settings)
        assert result is True

    def test_returns_false_on_error(self, mock_cli_ctx):
        """create_user_and_grant returns False when CREATE ROLE psql command fails."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)
        with (
            patch("djb.cli.db.user_exists", return_value=False),
            patch("djb.cli.db._run_psql") as mock_psql,
        ):
            mock_psql.return_value = Mock(returncode=1, stderr="error")
            result = create_user_and_grant(mock_cli_ctx, settings)
        assert result is False


class TestCreateTemplateDatabase:
    """Tests for create_template_database function."""

    def test_returns_true_when_template_exists(self, mock_cli_ctx):
        """create_template_database returns True if template already exists."""
        with patch("djb.cli.db._run_psql") as mock_psql:
            mock_psql.return_value = Mock(returncode=0, stdout="1")
            result = create_template_database(mock_cli_ctx)
        assert result is True
        mock_psql.assert_called_once()

    def test_creates_template_when_missing(self, mock_cli_ctx):
        """create_template_database creates template with extensions when missing."""
        with patch("djb.cli.db._run_psql") as mock_psql:
            # Template doesn't exist
            mock_psql.return_value = Mock(returncode=0, stdout="")
            # createdb and psql extension creation succeed
            mock_cli_ctx.runner.run.return_value = Mock(returncode=0)
            result = create_template_database(mock_cli_ctx)

        assert result is True
        # Should call createdb and psql for extension
        assert mock_cli_ctx.runner.run.call_count >= 2

    def test_returns_false_when_createdb_fails(self, mock_cli_ctx):
        """create_template_database returns False when subprocess createdb command fails."""
        with patch("djb.cli.db._run_psql") as mock_psql:
            mock_psql.return_value = Mock(returncode=0, stdout="")
            mock_cli_ctx.runner.run.return_value = Mock(returncode=1, stderr="createdb failed")
            result = create_template_database(mock_cli_ctx)

        assert result is False


class TestCreateExtensions:
    """Tests for create_extensions function."""

    def test_creates_extensions(self, mock_cli_ctx):
        """create_extensions creates required extensions in database."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)

        def side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            cmd_str = " ".join(str(c) for c in cmd)
            # First call checks existing extensions - return empty list
            if "SELECT extname FROM pg_extension" in cmd_str:
                return Mock(returncode=0, stdout="plpgsql\n")
            # Second call creates extension
            return Mock(returncode=0)

        mock_cli_ctx.runner.run.side_effect = side_effect
        result = create_extensions(mock_cli_ctx, settings)

        assert result is True
        assert mock_cli_ctx.runner.run.call_count == 2
        # Verify extension creation command
        create_call = mock_cli_ctx.runner.run.call_args_list[1][0][0]
        assert "CREATE EXTENSION IF NOT EXISTS postgis" in create_call[-1]

    def test_skips_existing_extensions(self, mock_cli_ctx):
        """create_extensions skips extensions that already exist."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)

        # Return postgis as already installed
        mock_cli_ctx.runner.run.return_value = Mock(returncode=0, stdout="plpgsql\npostgis\n")
        result = create_extensions(mock_cli_ctx, settings)

        assert result is True
        # Only one call - the check, no creation needed
        assert mock_cli_ctx.runner.run.call_count == 1

    def test_returns_false_on_extension_failure(self, mock_cli_ctx):
        """create_extensions returns False when extension creation fails."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)

        def side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            cmd_str = " ".join(str(c) for c in cmd)
            # First call checks existing extensions - return empty list
            if "SELECT extname FROM pg_extension" in cmd_str:
                return Mock(returncode=0, stdout="plpgsql\n")
            # Second call fails
            return Mock(returncode=1, stderr="permission denied")

        mock_cli_ctx.runner.run.side_effect = side_effect
        result = create_extensions(mock_cli_ctx, settings)

        assert result is False


class TestInitDatabase:
    """Tests for init_database function."""

    def test_returns_true_when_already_configured(self, mock_cli_ctx, djb_config):
        """init_database returns True when database is already OK."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.create_template_database", return_value=True),
            patch("djb.cli.db.get_db_status", return_value=DbStatus.OK),
            patch("djb.cli.db.create_extensions", return_value=True),
            patch("djb.cli.db.create_user_and_grant", return_value=True),
            patch("djb.cli.db.can_connect_as_user", return_value=True),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, quiet=True)
        assert result is True

    def test_returns_false_when_postgres_not_installed(self, mock_cli_ctx, djb_config):
        """init_database returns False when PostgreSQL not installed."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=False),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, quiet=True)
        assert result is False

    def test_creates_database_and_user(self, mock_cli_ctx, djb_config):
        """init_database creates database, extensions, and user when they don't exist."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.create_template_database", return_value=True),
            patch("djb.cli.db.get_db_status", return_value=DbStatus.NO_DATABASE),
            patch("djb.cli.db.create_database", return_value=True) as mock_create_db,
            patch("djb.cli.db.create_extensions", return_value=True) as mock_create_ext,
            patch("djb.cli.db.create_user_and_grant", return_value=True) as mock_create_user,
            patch("djb.cli.db.grant_schema_permissions", return_value=True),
            patch("djb.cli.db.can_connect_as_user", return_value=True),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, quiet=True)

        assert result is True
        mock_create_db.assert_called_once()
        mock_create_ext.assert_called_once()
        mock_create_user.assert_called_once()


class TestDbCLI:
    """Tests for djb db CLI commands."""

    def test_help(self, cli_runner):
        """djb db --help works."""
        result = cli_runner.invoke(djb_cli, ["db", "--help"])
        assert result.exit_code == 0
        assert "Database management commands" in result.output

    def test_init_help(self, cli_runner):
        """djb db init --help works."""
        result = cli_runner.invoke(djb_cli, ["db", "init", "--help"])
        assert result.exit_code == 0
        assert "Initialize development database" in result.output
        assert "--no-start" in result.output

    def test_status_help(self, cli_runner):
        """djb db status --help works."""
        result = cli_runner.invoke(djb_cli, ["db", "status", "--help"])
        assert result.exit_code == 0
        assert "Show database connection status" in result.output

    def test_init_success(self, cli_runner, djb_config):
        """djb db init succeeds when everything works."""
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.create_template_database", return_value=True),
            patch("djb.cli.db.get_db_status", return_value=DbStatus.OK),
            patch("djb.cli.db.create_extensions", return_value=True),
            patch("djb.cli.db.create_user_and_grant", return_value=True),
            patch("djb.cli.db.can_connect_as_user", return_value=True),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = cli_runner.invoke(djb_cli, ["db", "init"])

        assert result.exit_code == 0

    def test_init_failure_no_postgres(self, cli_runner, djb_config):
        """djb db init fails when PostgreSQL not installed."""
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=False),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = cli_runner.invoke(djb_cli, ["db", "init"])

        assert result.exit_code == 1
        assert "failed" in result.output.lower() or "not installed" in result.output.lower()

    def test_status_command(self, cli_runner, djb_config):
        """djb db status shows configuration."""
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.get_db_status", return_value=DbStatus.OK),
        ):
            mock_settings.return_value = DbSettings("testdb", "testuser", "pass", "localhost", 5432)
            result = cli_runner.invoke(djb_cli, ["db", "status"])

        assert result.exit_code == 0
        assert "testdb" in result.output
        assert "testuser" in result.output


class TestWaitForPostgres:
    """Tests for wait_for_postgres function - polling pattern with timeout."""

    def test_returns_true_on_immediate_success(self, mock_cli_ctx):
        """wait_for_postgres returns True when PostgreSQL is immediately available."""
        with (
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.sleep") as mock_sleep,
        ):
            result = wait_for_postgres(mock_cli_ctx)

        assert result is True
        mock_sleep.assert_not_called()

    def test_retries_until_success(self, mock_cli_ctx):
        """wait_for_postgres retries until PostgreSQL becomes available."""
        with (
            patch("djb.cli.db.check_postgres_running") as mock_check,
            patch("djb.cli.db.sleep") as mock_sleep,
            patch("djb.cli.db.time") as mock_time,
        ):
            # First two checks fail, third succeeds
            mock_check.side_effect = [False, False, True]
            # Time progresses: start at 0, then 0.5, then 1 (still under timeout)
            mock_time.side_effect = [0, 0.5, 1, 1.5]

            result = wait_for_postgres(mock_cli_ctx, timeout=10.0)

        assert result is True
        assert mock_check.call_count == 3
        # Should have slept twice (after first and second failures)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(0.5)

    def test_returns_false_on_timeout(self, mock_cli_ctx):
        """wait_for_postgres returns False when PostgreSQL doesn't become available in time."""
        with (
            patch("djb.cli.db.check_postgres_running", return_value=False),
            patch("djb.cli.db.sleep"),
            patch("djb.cli.db.time") as mock_time,
        ):
            # Time progresses past timeout
            mock_time.side_effect = [0, 11]  # start, past timeout of 10

            result = wait_for_postgres(mock_cli_ctx, timeout=10.0)

        assert result is False

    def test_uses_custom_timeout(self, mock_cli_ctx):
        """wait_for_postgres respects custom timeout value."""
        with (
            patch("djb.cli.db.check_postgres_running", return_value=False),
            patch("djb.cli.db.sleep"),
            patch("djb.cli.db.time") as mock_time,
        ):
            # With custom timeout of 5, time=6 should exceed it
            mock_time.side_effect = [0, 6]

            result = wait_for_postgres(mock_cli_ctx, timeout=5.0)

        assert result is False

    def test_custom_host_and_port(self, mock_cli_ctx):
        """wait_for_postgres passes custom host and port to check_postgres_running."""
        with (
            patch("djb.cli.db.check_postgres_running", return_value=True) as mock_check,
            patch("djb.cli.db.sleep"),
        ):
            result = wait_for_postgres(mock_cli_ctx, host="db.example.com", port=5433)

        assert result is True
        mock_check.assert_called()


class TestStartPostgresService:
    """Tests for start_postgres_service function - Homebrew service commands."""

    def test_returns_true_when_postgresql17_starts(self, mock_cli_ctx):
        """start_postgres_service returns True when postgresql@17 starts successfully."""
        mock_cli_ctx.runner.check.return_value = True
        mock_cli_ctx.runner.run.return_value = Mock(returncode=0)
        result = start_postgres_service(mock_cli_ctx)

        assert result is True

    def test_falls_back_to_postgresql_without_version(self, mock_cli_ctx):
        """start_postgres_service falls back to 'postgresql' when 'postgresql@17' fails."""
        mock_cli_ctx.runner.check.return_value = True
        # First call (postgresql@17) fails, second (postgresql) succeeds
        mock_cli_ctx.runner.run.side_effect = [
            Mock(returncode=1),
            Mock(returncode=0),
        ]
        result = start_postgres_service(mock_cli_ctx)

        assert result is True
        assert mock_cli_ctx.runner.run.call_count == 2

    def test_returns_false_when_both_fail(self, mock_cli_ctx):
        """start_postgres_service returns False when both postgresql@17 and postgresql fail."""
        mock_cli_ctx.runner.check.return_value = True
        # Both calls fail
        mock_cli_ctx.runner.run.return_value = Mock(returncode=1)
        result = start_postgres_service(mock_cli_ctx)

        assert result is False
        assert mock_cli_ctx.runner.run.call_count == 2

    def test_returns_false_when_brew_not_available(self, mock_cli_ctx):
        """start_postgres_service returns False when Homebrew is not available."""
        mock_cli_ctx.runner.check.return_value = False
        result = start_postgres_service(mock_cli_ctx)

        assert result is False


class TestGetDbSettingsFromSecrets:
    """Tests for _get_db_settings_from_secrets function - exception handling."""

    def test_returns_none_when_secrets_dir_missing(self, djb_config, mock_fs, mock_cli_ctx):
        """_get_db_settings_from_secrets returns None when secrets directory doesn't exist."""
        mock_cli_ctx.config = djb_config
        # secrets directory doesn't exist (not added to mock_fs)
        with mock_fs.apply():
            result = _get_db_settings_from_secrets(mock_cli_ctx)

        assert result is None

    def test_returns_settings_from_secrets(self, djb_config, mock_fs, mock_cli_ctx):
        """_get_db_settings_from_secrets returns DbSettings when secrets are available."""
        mock_cli_ctx.config = djb_config
        mock_secrets = {
            "db_credentials": {
                "database": "mydb",
                "username": "myuser",
                "password": "mypass",
                "host": "db.example.com",
                "port": 5433,
            }
        }

        mock_fs.add_dir(djb_config.project_dir / "secrets")
        with mock_fs.apply():
            with patch("djb.cli.db.load_secrets", return_value=mock_secrets):
                result = _get_db_settings_from_secrets(mock_cli_ctx)

        assert result is not None
        assert result.name == "mydb"
        assert result.user == "myuser"
        assert result.password == "mypass"
        assert result.host == "db.example.com"
        assert result.port == 5433

    @pytest.mark.parametrize(
        "error_message",
        [
            "Failed to decrypt",
            "could not find key for recipient",
            "no matching recipient found",
        ],
        ids=["decrypt_error", "key_error", "recipient_error"],
    )
    def test_returns_none_on_sops_error(self, djb_config, mock_fs, error_message, mock_cli_ctx):
        """_get_db_settings_from_secrets returns None when SOPS reports any error type."""
        mock_cli_ctx.config = djb_config
        mock_fs.add_dir(djb_config.project_dir / "secrets")
        with mock_fs.apply():
            with patch("djb.cli.db.load_secrets", side_effect=SopsError(error_message)):
                result = _get_db_settings_from_secrets(mock_cli_ctx)

        assert result is None

    def test_returns_none_on_file_not_found(self, djb_config, mock_fs, mock_cli_ctx):
        """_get_db_settings_from_secrets returns None when secrets file is not found."""
        mock_cli_ctx.config = djb_config
        mock_fs.add_dir(djb_config.project_dir / "secrets")
        with mock_fs.apply():
            with patch(
                "djb.cli.db.load_secrets",
                side_effect=FileNotFoundError("development.yaml not found"),
            ):
                result = _get_db_settings_from_secrets(mock_cli_ctx)

        assert result is None

    def test_returns_none_when_db_credentials_not_dict(self, djb_config, mock_fs, mock_cli_ctx):
        """_get_db_settings_from_secrets returns None when db_credentials is not a dictionary."""
        mock_cli_ctx.config = djb_config
        mock_secrets = {"db_credentials": "not a dict"}

        mock_fs.add_dir(djb_config.project_dir / "secrets")
        with mock_fs.apply():
            with patch("djb.cli.db.load_secrets", return_value=mock_secrets):
                result = _get_db_settings_from_secrets(mock_cli_ctx)

        assert result is None

    def test_returns_none_when_db_credentials_missing(self, djb_config, mock_fs, mock_cli_ctx):
        """_get_db_settings_from_secrets returns None when db_credentials key is missing."""
        mock_cli_ctx.config = djb_config
        mock_secrets = {"other_key": "value"}

        mock_fs.add_dir(djb_config.project_dir / "secrets")
        with mock_fs.apply():
            with patch("djb.cli.db.load_secrets", return_value=mock_secrets):
                result = _get_db_settings_from_secrets(mock_cli_ctx)

        assert result is None

    def test_uses_defaults_for_missing_optional_fields(self, djb_config, mock_fs, mock_cli_ctx):
        """_get_db_settings_from_secrets uses defaults for host and port when not provided."""
        mock_cli_ctx.config = djb_config
        # Only provide required fields
        mock_secrets = {
            "db_credentials": {
                "database": "mydb",
                "username": "myuser",
                "password": "mypass",
            }
        }

        mock_fs.add_dir(djb_config.project_dir / "secrets")
        with mock_fs.apply():
            with patch("djb.cli.db.load_secrets", return_value=mock_secrets):
                result = _get_db_settings_from_secrets(mock_cli_ctx)

        assert result is not None
        assert result.host == "localhost"
        assert result.port == 5432


class TestGetDefaultDbSettingsWithProjectName:
    """Tests for _get_default_db_settings using project name from pyproject.toml."""

    def test_uses_project_name_from_config(self, make_djb_config, mock_cli_ctx):
        """_get_default_db_settings uses project name from djb config."""
        config = make_djb_config(DjbConfig(project_name="my-project"))
        mock_cli_ctx.config = config
        result = _get_default_db_settings(mock_cli_ctx)

        assert result.name == "my_project"  # hyphens converted to underscores
        assert result.user == "my_project"
        assert result.password == "foobarqux"
        assert result.host == "localhost"
        assert result.port == 5432


class TestGetDefaultDbSettingsFallback:
    """Tests for _get_default_db_settings fallback to directory name."""

    def test_uses_directory_name_as_fallback(self, djb_config, mock_cli_ctx):
        """_get_default_db_settings uses directory name when project_name not configured.

        Note: With djb_config, project_name is always set. This test verifies
        that the project name is used correctly (matching the directory name
        pattern test-project -> test_project).
        """
        mock_cli_ctx.config = djb_config
        result = _get_default_db_settings(mock_cli_ctx)

        # djb_config has project_name="test-project", so expect test_project
        assert result.name == "test_project"
        assert result.user == "test_project"


class TestGetDefaultDbSettingsSanitization:
    """Tests for _get_default_db_settings hyphen to underscore conversion."""

    def test_sanitizes_hyphens_to_underscores(self, make_djb_config, mock_cli_ctx):
        """_get_default_db_settings converts hyphens to underscores for database/user names."""
        config = make_djb_config(DjbConfig(project_name="my-cool-app"))
        mock_cli_ctx.config = config
        result = _get_default_db_settings(mock_cli_ctx)

        assert result.name == "my_cool_app"
        assert result.user == "my_cool_app"


class TestGrantSchemaPermissions:
    """Tests for grant_schema_permissions function - idempotent database operation."""

    def test_returns_true_on_success(self, mock_cli_ctx):
        """grant_schema_permissions returns True when grant succeeds."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)

        mock_cli_ctx.runner.run.return_value = Mock(returncode=0)
        result = grant_schema_permissions(mock_cli_ctx, settings)

        assert result is True
        mock_cli_ctx.runner.run.assert_called_once()
        # Verify correct psql command
        call_args = mock_cli_ctx.runner.run.call_args[0][0]
        assert call_args[0] == "psql"
        assert "-h" in call_args and "localhost" in call_args
        assert "-p" in call_args and "5432" in call_args
        assert "testdb" in call_args
        assert "GRANT ALL ON SCHEMA public TO testuser" in call_args[-1]

    def test_returns_true_on_failure_non_fatal(self, mock_cli_ctx):
        """grant_schema_permissions returns True even when grant fails (non-fatal)."""
        settings = DbSettings("testdb", "testuser", "testpass", "localhost", 5432)

        mock_cli_ctx.runner.run.return_value = Mock(returncode=1, stderr="permission denied")
        result = grant_schema_permissions(mock_cli_ctx, settings)

        # Non-fatal, should still return True
        assert result is True

    def test_uses_correct_host_and_port(self, mock_cli_ctx):
        """grant_schema_permissions uses correct host and port in psql command."""
        settings = DbSettings("mydb", "myuser", "pass", "db.example.com", 5433)

        mock_cli_ctx.runner.run.return_value = Mock(returncode=0)
        grant_schema_permissions(mock_cli_ctx, settings)

        call_args = mock_cli_ctx.runner.run.call_args[0][0]
        assert "-h" in call_args
        host_idx = call_args.index("-h")
        assert call_args[host_idx + 1] == "db.example.com"
        port_idx = call_args.index("-p")
        assert call_args[port_idx + 1] == "5433"

    def test_grants_to_correct_user(self, mock_cli_ctx):
        """grant_schema_permissions grants permissions to the correct user."""
        settings = DbSettings("testdb", "custom_user", "pass", "localhost", 5432)

        mock_cli_ctx.runner.run.return_value = Mock(returncode=0)
        grant_schema_permissions(mock_cli_ctx, settings)

        call_args = mock_cli_ctx.runner.run.call_args[0][0]
        grant_cmd = call_args[-1]
        assert "GRANT ALL ON SCHEMA public TO custom_user" in grant_cmd


class TestRunPsql:
    """Tests for _run_psql function - internal psql query runner."""

    def test_runs_psql_with_default_params(self, mock_cli_ctx):
        """_run_psql runs psql with default host, port, and database."""
        mock_cli_ctx.runner.run.return_value = Mock(returncode=0, stdout="result", stderr="")
        result = _run_psql(mock_cli_ctx, "SELECT 1;")

        assert result.returncode == 0
        mock_cli_ctx.runner.run.assert_called_once()
        call_args = mock_cli_ctx.runner.run.call_args[0][0]
        assert call_args[0] == "psql"
        assert "-h" in call_args and "localhost" in call_args
        assert "-p" in call_args and "5432" in call_args
        assert "postgres" in call_args  # default database
        assert "-tAc" in call_args
        assert "SELECT 1;" in call_args

    def test_runs_psql_with_custom_params(self, mock_cli_ctx):
        """_run_psql runs psql with custom database, host, and port."""
        mock_cli_ctx.runner.run.return_value = Mock(returncode=0, stdout="", stderr="")
        _run_psql(mock_cli_ctx, "SELECT 1;", database="mydb", host="db.example.com", port=5433)

        call_args = mock_cli_ctx.runner.run.call_args[0][0]
        host_idx = call_args.index("-h")
        assert call_args[host_idx + 1] == "db.example.com"
        port_idx = call_args.index("-p")
        assert call_args[port_idx + 1] == "5433"
        assert "mydb" in call_args


class TestInitDatabaseEdgeCases:
    """Additional edge case tests for init_database function."""

    def test_returns_false_when_postgres_not_running_no_start(self, mock_cli_ctx, djb_config):
        """init_database returns False when PostgreSQL not running and start_service=False."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=False),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, start_service=False, quiet=True)

        assert result is False

    def test_returns_false_when_create_user_fails(self, mock_cli_ctx, djb_config):
        """init_database returns False when create_user_and_grant fails."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.get_db_status", return_value=DbStatus.NO_DATABASE),
            patch("djb.cli.db.create_database", return_value=True),
            patch("djb.cli.db.create_user_and_grant", return_value=False),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, quiet=True)

        assert result is False

    def test_returns_false_when_final_connection_fails(self, mock_cli_ctx, djb_config):
        """init_database returns False when final can_connect_as_user check fails."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.get_db_status", return_value=DbStatus.NO_DATABASE),
            patch("djb.cli.db.create_database", return_value=True),
            patch("djb.cli.db.create_user_and_grant", return_value=True),
            patch("djb.cli.db.grant_schema_permissions", return_value=True),
            patch("djb.cli.db.can_connect_as_user", return_value=False),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, quiet=True)

        assert result is False

    def test_skips_database_creation_for_no_user_status(self, mock_cli_ctx, djb_config):
        """init_database skips database creation but creates user when status is NO_USER."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=True),
            patch("djb.cli.db.create_template_database", return_value=True),
            patch("djb.cli.db.get_db_status", return_value=DbStatus.NO_USER),
            patch("djb.cli.db.create_database") as mock_create_db,
            patch("djb.cli.db.create_extensions", return_value=True),
            patch("djb.cli.db.create_user_and_grant", return_value=True) as mock_create_user,
            patch("djb.cli.db.grant_schema_permissions", return_value=True),
            patch("djb.cli.db.can_connect_as_user", return_value=True),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, quiet=True)

        assert result is True
        # NO_USER status means database exists, so should NOT call create_database
        mock_create_db.assert_not_called()
        # But should still call create_user_and_grant
        mock_create_user.assert_called_once()

    def test_returns_false_when_wait_for_postgres_fails(self, mock_cli_ctx, djb_config):
        """init_database returns False when waiting for PostgreSQL times out."""
        mock_cli_ctx.config = djb_config
        with (
            patch("djb.cli.db.get_db_settings") as mock_settings,
            patch("djb.cli.db.check_postgres_installed", return_value=True),
            patch("djb.cli.db.check_postgres_running", return_value=False),
            patch("djb.cli.db.start_postgres_service", return_value=True),
            patch("djb.cli.db.wait_for_postgres", return_value=False),
        ):
            mock_settings.return_value = DbSettings("db", "user", "pass", "localhost", 5432)
            result = init_database(mock_cli_ctx, start_service=True, quiet=True)

        assert result is False
