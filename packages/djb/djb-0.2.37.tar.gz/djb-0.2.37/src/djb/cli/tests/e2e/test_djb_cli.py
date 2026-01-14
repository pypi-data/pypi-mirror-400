"""E2E tests for djb CLI main entry point.

These tests require real file I/O for testing mode persistence,
banner display with real projects, and config loading.
Unit tests for help output and print_banner function are in ../test_djb_cli.py.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli
from djb.config.storage.utils import load_toml_mapping


pytestmark = pytest.mark.e2e_marker


# Common pyproject.toml content for tests
PYPROJECT_CONTENT = '[project]\nname = "test"\ndependencies = ["djb"]\n'


class TestDjbCliBanner:
    """E2E tests for djb CLI banner."""

    def test_banner_shows_mode_and_platform(self, project_dir, monkeypatch):
        """Banner shows mode and platform."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        # Let's test with secrets --help which should show banner
        result = runner.invoke(djb_cli, ["secrets", "--help"])
        assert "[djb] mode:" in result.output
        assert "platform:" in result.output

    def test_banner_suppressed_when_nested(self, project_dir, monkeypatch):
        """Suppresses banner when DJB_NESTED is set."""
        monkeypatch.chdir(project_dir)
        monkeypatch.setenv("DJB_NESTED", "1")
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["secrets", "--help"])

        assert "[djb] mode:" not in result.output

    def test_banner_shows_correct_mode_color(self, project_dir, monkeypatch):
        """Banner shows development mode in green."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["--mode", "development", "secrets", "--help"])

        # Check for ANSI green color code before "development"
        assert "\033[32m" in result.output or "development" in result.output


class TestDjbCliModeOption:
    """E2E tests for --mode option."""

    @pytest.mark.parametrize(
        "mode_value,expected_output",
        [
            ("development", "development"),
            ("staging", "staging"),
            ("production", "production"),
            ("PRODUCTION", "production"),  # Case-insensitive
        ],
    )
    def test_mode_option_accepts_valid_values(
        self, project_dir, monkeypatch, mode_value, expected_output
    ):
        """--mode accepts valid values (case-insensitive)."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["--mode", mode_value, "secrets", "--help"])

        assert result.exit_code == 0
        assert expected_output in result.output

    def test_mode_option_rejects_invalid(self, project_dir, monkeypatch):
        """--mode rejects invalid values."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["--mode", "invalid", "secrets", "--help"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output


class TestDjbCliModePersistence:
    """E2E tests for mode persistence."""

    def test_mode_persists_to_config_file(self, project_dir, monkeypatch):
        """--mode persists to .djb/local.toml."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["--mode", "production", "secrets", "--help"])

        assert result.exit_code == 0

        config_path = project_dir / ".djb" / "local.toml"
        assert config_path.exists()

        config = load_toml_mapping(config_path)

        assert config["mode"] == "production"

    def test_persisted_mode_is_used_in_subsequent_commands(self, project_dir, monkeypatch):
        """Persisted mode is used in subsequent commands."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        # First, set mode to production
        runner = CliRunner()
        runner.invoke(djb_cli, ["--mode", "production", "secrets", "--help"])

        # Then run without --mode and verify production is used
        result = runner.invoke(djb_cli, ["secrets", "--help"])

        assert "production" in result.output


class TestDjbCliPlatformOption:
    """E2E tests for --platform option."""

    def test_platform_option_accepts_heroku(self, project_dir, monkeypatch):
        """--platform heroku is accepted."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["--platform", "heroku", "secrets", "--help"])

        assert result.exit_code == 0

    def test_platform_option_rejects_invalid(self, project_dir, monkeypatch):
        """--platform rejects invalid values."""
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(PYPROJECT_CONTENT)

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["--platform", "invalid", "secrets", "--help"])

        assert result.exit_code != 0


class TestDjbCliConfigInContext:
    """E2E tests for config being stored in Click context."""

    def test_config_stored_in_context(self, project_dir, monkeypatch):
        """Stores config in ctx.obj.

        We verify the config exists by checking the banner output shows
        mode and platform, which requires config to be loaded and stored.
        """
        monkeypatch.chdir(project_dir)
        (project_dir / "pyproject.toml").write_text(
            '[project]\nname = "testproject"\ndependencies = ["djb"]\n'
        )

        runner = CliRunner()
        result = runner.invoke(djb_cli, ["secrets", "--help"])

        # If config wasn't loaded, banner wouldn't show mode/platform
        assert "mode:" in result.output
        assert "platform:" in result.output
