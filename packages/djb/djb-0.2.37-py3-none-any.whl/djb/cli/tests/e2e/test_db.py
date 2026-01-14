"""End-to-end tests for djb db CLI commands.

These tests exercise the database management CLI against real local PostgreSQL.

Commands tested:
- djb db init
- djb db status

Requirements:
- PostgreSQL must be installed and running locally
"""

from __future__ import annotations

import subprocess  # noqa: TID251 - invoking psql directly
import uuid
from unittest.mock import patch

import pytest

from djb.cli.context import CliContext
from djb.cli.db import (
    DbSettings,
    DbStatus,
    can_connect_as_user,
    check_postgres_installed,
    check_postgres_running,
    create_database,
    create_user_and_grant,
    database_exists,
    get_db_status,
    grant_schema_permissions,
    user_exists,
)
from djb.cli.djb import djb_cli


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def make_db_settings() -> DbSettings:
    """Generate unique database settings for this test.

    Uses a UUID-based name to ensure isolation between tests.
    """
    unique_id = uuid.uuid4().hex[:8]
    return DbSettings(
        name=f"djb_e2e_test_{unique_id}",
        user=f"djb_e2e_user_{unique_id}",
        password="test_password_123",
        host="localhost",
        port=5432,
    )


@pytest.fixture
def make_db_settings_with_cleanup(make_db_settings: DbSettings, make_cli_ctx: CliContext):
    """Fixture that yields settings for a database that doesn't yet
    exist, and drops any database and user that was created for these
    settings by the test after the test exits.

    Yields settings, then cleans up after the test exits.
    """
    yield make_db_settings

    # Clean up: drop database and user

    # Drop database first (must disconnect all sessions)
    if database_exists(
        make_cli_ctx, make_db_settings.name, make_db_settings.host, make_db_settings.port
    ):
        # Force disconnect all sessions
        subprocess.run(
            [
                "psql",
                "-h",
                make_db_settings.host,
                "-p",
                str(make_db_settings.port),
                "postgres",
                "-c",
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{make_db_settings.name}';",
            ],
            capture_output=True,
        )
        subprocess.run(
            [
                "psql",
                "-h",
                make_db_settings.host,
                "-p",
                str(make_db_settings.port),
                "postgres",
                "-c",
                f"DROP DATABASE IF EXISTS {make_db_settings.name};",
            ],
            capture_output=True,
        )

    # Drop user
    if user_exists(
        make_cli_ctx, make_db_settings.user, make_db_settings.host, make_db_settings.port
    ):
        subprocess.run(
            [
                "psql",
                "-h",
                make_db_settings.host,
                "-p",
                str(make_db_settings.port),
                "postgres",
                "-c",
                f"DROP USER IF EXISTS {make_db_settings.user};",
            ],
            capture_output=True,
        )


class TestDbFunctions:
    """E2E tests for database utility functions."""

    def test_check_postgres_installed(self):
        """PostgreSQL is detected as installed."""
        assert check_postgres_installed() is True

    def test_check_postgres_running(self, make_cli_ctx: CliContext):
        """PostgreSQL is detected as running."""
        assert check_postgres_running(make_cli_ctx, "localhost", 5432) is True

    def test_database_exists_false_for_nonexistent(
        self, make_cli_ctx: CliContext, make_db_settings: DbSettings
    ):
        """Database_exists returns False for non-existent database."""
        # Use a random name that definitely doesn't exist
        assert (
            database_exists(make_cli_ctx, f"nonexistent_{uuid.uuid4().hex}", "localhost", 5432)
            is False
        )

    def test_create_database_and_user(
        self, make_cli_ctx: CliContext, make_db_settings_with_cleanup: DbSettings
    ):
        """Creating a database and user from scratch."""
        settings = make_db_settings_with_cleanup

        # Initially neither should exist
        assert database_exists(make_cli_ctx, settings.name, settings.host, settings.port) is False
        assert user_exists(make_cli_ctx, settings.user, settings.host, settings.port) is False

        # Create database
        result = create_database(make_cli_ctx, settings)
        assert result is True
        assert database_exists(make_cli_ctx, settings.name, settings.host, settings.port) is True

        # Create user and grant privileges
        result = create_user_and_grant(make_cli_ctx, settings)
        assert result is True
        assert user_exists(make_cli_ctx, settings.user, settings.host, settings.port) is True

        # Grant schema permissions
        result = grant_schema_permissions(make_cli_ctx, settings)
        assert result is True

        # Verify connection works
        assert can_connect_as_user(make_cli_ctx, settings) is True

    def test_get_db_status_no_database(
        self, make_cli_ctx: CliContext, make_db_settings: DbSettings
    ):
        """E2E: get_db_status returns NO_DATABASE for non-existent database against real PostgreSQL."""
        # Use settings for a non-existent database
        status = get_db_status(make_cli_ctx, make_db_settings)
        assert status == DbStatus.NO_DATABASE

    def test_get_db_status_ok(
        self, make_cli_ctx: CliContext, make_db_settings_with_cleanup: DbSettings
    ):
        """Returns OK when database is fully configured."""
        settings = make_db_settings_with_cleanup

        # Create everything
        create_database(make_cli_ctx, settings)
        create_user_and_grant(make_cli_ctx, settings)
        grant_schema_permissions(make_cli_ctx, settings)

        # Status should be OK
        status = get_db_status(make_cli_ctx, settings)
        assert status == DbStatus.OK


class TestDbInit:
    """E2E tests for djb db init command."""

    def test_init_creates_database(
        self,
        cli_runner,
        make_cli_ctx: CliContext,
        make_db_settings_with_cleanup: DbSettings,
        make_pyproject_dir_with_git,
    ):
        """Db init creates the database and user."""
        settings = make_db_settings_with_cleanup

        # Initially database should not exist
        assert database_exists(make_cli_ctx, settings.name, settings.host, settings.port) is False

        with patch("djb.cli.db.get_db_settings", return_value=settings):
            result = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(make_pyproject_dir_with_git), "db", "init", "--no-start"],
            )

        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Database should now exist
        assert database_exists(make_cli_ctx, settings.name, settings.host, settings.port) is True
        assert user_exists(make_cli_ctx, settings.user, settings.host, settings.port) is True
        assert can_connect_as_user(make_cli_ctx, settings) is True

    def test_init_is_idempotent(
        self,
        cli_runner,
        make_cli_ctx: CliContext,
        make_db_settings_with_cleanup: DbSettings,
        make_pyproject_dir_with_git,
    ):
        """Running 'djb db init' twice is idempotent: database remains accessible."""
        settings = make_db_settings_with_cleanup

        with patch("djb.cli.db.get_db_settings", return_value=settings):
            # First run
            result1 = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(make_pyproject_dir_with_git), "db", "init", "--no-start"],
            )
            assert result1.exit_code == 0, f"First run failed: {result1.output}"

            # Second run - should succeed without errors
            result2 = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(make_pyproject_dir_with_git), "db", "init", "--no-start"],
            )
            assert result2.exit_code == 0, f"Second run failed: {result2.output}"

        # Should still work
        assert can_connect_as_user(make_cli_ctx, settings) is True


class TestDbStatus:
    """E2E tests for djb db status command."""

    def test_status_shows_not_configured(
        self,
        cli_runner,
        make_db_settings: DbSettings,
        make_pyproject_dir_with_git,
    ):
        """Status shows database not configured when it doesn't exist."""
        settings = make_db_settings

        with patch("djb.cli.db.get_db_settings", return_value=settings):
            result = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(make_pyproject_dir_with_git), "db", "status"],
            )

        # Should complete but show database doesn't exist
        assert result.exit_code == 0
        assert "does not exist" in result.output or "not" in result.output.lower()

    def test_status_shows_configured(
        self,
        cli_runner,
        make_cli_ctx: CliContext,
        make_db_settings_with_cleanup: DbSettings,
        make_pyproject_dir_with_git,
    ):
        """Status shows database is configured when it exists."""
        settings = make_db_settings_with_cleanup

        # Create the database first
        create_database(make_cli_ctx, settings)
        create_user_and_grant(make_cli_ctx, settings)
        grant_schema_permissions(make_cli_ctx, settings)

        with patch("djb.cli.db.get_db_settings", return_value=settings):
            result = cli_runner.invoke(
                djb_cli,
                ["--project-dir", str(make_pyproject_dir_with_git), "db", "status"],
            )

        assert result.exit_code == 0
        # Should show database name and indicate it's accessible
        assert settings.name in result.output
        assert "accessible" in result.output.lower() or "configured" in result.output.lower()
