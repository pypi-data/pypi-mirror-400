"""Unit tests for djb secrets CLI commands.

Tests that require real file I/O (secrets encryption, key management) are in e2e/test_secrets.py.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from djb.cli.secrets import (
    _check_homebrew_installed,
    _check_prerequisites,
    _ensure_gpg_setup,
    _ensure_prerequisites,
    _install_with_homebrew,
    secrets,
)
from djb.secrets import GpgError


class TestPrerequisiteChecks:
    """Tests for prerequisite checking functions."""

    @pytest.mark.parametrize(
        "which_result,expected",
        [
            ("/usr/local/bin/brew", True),
            (None, False),
        ],
        ids=["present", "missing"],
    )
    def test_check_homebrew_installed(self, which_result, expected):
        """_check_homebrew_installed returns True/False based on shutil.which result."""
        with patch("shutil.which", return_value=which_result):
            assert _check_homebrew_installed() is expected

    @pytest.mark.parametrize(
        "returncode,stderr,expected",
        [
            (0, "", True),
            (1, "error", False),
        ],
        ids=["success", "failure"],
    )
    def test_install_with_homebrew_returncode(self, mock_cli_ctx, returncode, stderr, expected):
        """_install_with_homebrew returns True/False based on CmdRunner returncode."""
        mock_result = type("Result", (), {"returncode": returncode, "stderr": stderr})()
        mock_cli_ctx.runner.run.return_value = mock_result
        with patch("djb.cli.secrets.logger"):
            result = _install_with_homebrew(mock_cli_ctx, "sops")
            assert result is expected

    def test_ensure_prerequisites_all_installed(self, mock_cli_ctx):
        """_ensure_prerequisites returns True when all tools installed."""
        with (
            patch("djb.cli.secrets.check_sops_installed", return_value=True),
            patch("djb.cli.secrets.check_age_installed", return_value=True),
            patch("djb.cli.secrets.logger"),
        ):
            result = _ensure_prerequisites(mock_cli_ctx)
            assert result is True

    def test_ensure_prerequisites_missing_tools_no_homebrew(self, mock_cli_ctx):
        """_ensure_prerequisites returns False when tools missing and no brew."""
        with (
            patch("djb.cli.secrets.check_sops_installed", return_value=False),
            patch("djb.cli.secrets.check_age_installed", return_value=False),
            patch("djb.cli.secrets._check_homebrew_installed", return_value=False),
            patch("platform.system", return_value="Linux"),
            patch("djb.cli.secrets.logger"),
        ):
            result = _ensure_prerequisites(mock_cli_ctx)
            assert result is False

    def test_ensure_prerequisites_auto_install_macos(self, mock_cli_ctx):
        """_ensure_prerequisites auto-installs on macOS with Homebrew."""
        with (
            patch("djb.cli.secrets.check_sops_installed", return_value=False),
            patch("djb.cli.secrets.check_age_installed", return_value=False),
            patch("djb.cli.secrets._check_homebrew_installed", return_value=True),
            patch("platform.system", return_value="Darwin"),
            patch("djb.cli.secrets._install_with_homebrew", return_value=True) as mock_install,
            patch("djb.cli.secrets.logger"),
        ):
            result = _ensure_prerequisites(mock_cli_ctx)
            assert result is True
            # Should have called install for both tools
            assert mock_install.call_count == 2

    def test_ensure_prerequisites_quiet_mode(self, mock_cli_ctx):
        """_ensure_prerequisites doesn't log when quiet=True."""
        with (
            patch("djb.cli.secrets.check_sops_installed", return_value=True),
            patch("djb.cli.secrets.check_age_installed", return_value=True),
            patch("djb.cli.secrets.logger") as mock_logger,
        ):
            _ensure_prerequisites(mock_cli_ctx, quiet=True)
            # Should not call done for installed tools in quiet mode
            mock_logger.done.assert_not_called()

    def test_ensure_prerequisites_macos_no_homebrew(self, mock_cli_ctx):
        """_ensure_prerequisites on macOS without Homebrew shows install hints."""
        with (
            patch("djb.cli.secrets.check_sops_installed", return_value=False),
            patch("djb.cli.secrets.check_age_installed", return_value=True),
            patch("djb.cli.secrets._check_homebrew_installed", return_value=False),
            patch("platform.system", return_value="Darwin"),
            patch("djb.cli.secrets.logger") as mock_logger,
        ):
            result = _ensure_prerequisites(mock_cli_ctx)
            assert result is False
            # Should suggest installing Homebrew first
            mock_logger.info.assert_any_call("  First install Homebrew: https://brew.sh")

    def test_ensure_prerequisites_auto_install_fails(self, mock_cli_ctx):
        """_ensure_prerequisites returns False when auto-install fails."""
        with (
            patch("djb.cli.secrets.check_sops_installed", return_value=False),
            patch("djb.cli.secrets.check_age_installed", return_value=True),
            patch("djb.cli.secrets._check_homebrew_installed", return_value=True),
            patch("platform.system", return_value="Darwin"),
            patch("djb.cli.secrets._install_with_homebrew", return_value=False),
            patch("djb.cli.secrets.logger"),
        ):
            result = _ensure_prerequisites(mock_cli_ctx)
            assert result is False

    def test_check_prerequisites_exits_on_failure(self, mock_cli_ctx):
        """_check_prerequisites calls sys.exit when prerequisites fail."""
        with (
            patch("djb.cli.secrets._ensure_prerequisites", return_value=False),
            pytest.raises(SystemExit) as exc_info,
        ):
            _check_prerequisites(mock_cli_ctx)
        assert exc_info.value.code == 1


class TestSecretsCommandGroup:
    """Tests for the secrets command group."""

    def test_secrets_help(self, cli_runner):
        """secrets --help shows available commands."""
        result = cli_runner.invoke(secrets, ["--help"])
        assert result.exit_code == 0
        assert "Manage encrypted secrets" in result.output

    def test_secrets_init_help(self, cli_runner):
        """secrets init --help shows options."""
        result = cli_runner.invoke(secrets, ["init", "--help"])
        assert result.exit_code == 0
        assert "--key-path" in result.output
        assert "--secrets-dir" in result.output
        assert "--force" in result.output


class TestGenerateKeyCommand:
    """Tests for the secrets generate-key command."""

    def test_generate_key_output(self, cli_runner):
        """secrets generate-key produces a valid Django secret key."""
        result = cli_runner.invoke(secrets, ["generate-key"])
        assert result.exit_code == 0
        assert "Generated Django secret key" in result.output

    def test_generate_key_unique(self, cli_runner):
        """secrets generate-key produces unique keys each time."""
        result1 = cli_runner.invoke(secrets, ["generate-key"])
        result2 = cli_runner.invoke(secrets, ["generate-key"])
        # Extract keys (they should be different)
        assert result1.output != result2.output


class TestEnsureGpgSetup:
    """Unit tests for _ensure_gpg_setup helper function."""

    def test_returns_true_when_gpg_key_exists(self, mock_cli_ctx):
        """_ensure_gpg_setup returns True when user has GPG key."""
        # Set config attributes needed for this test
        mock_cli_ctx.config = type(
            "Config", (), {"email": "test@example.com", "name": "Test User"}
        )()
        with (
            patch("djb.cli.secrets.init_gpg_agent_config", return_value=False),
            patch("djb.cli.secrets.has_gpg_secret_key", return_value=True),
        ):
            result = _ensure_gpg_setup(mock_cli_ctx)
            assert result is True

    def test_creates_gpg_agent_config_if_needed(self, mock_cli_ctx):
        """_ensure_gpg_setup creates GPG agent config when not exists."""
        mock_cli_ctx.config = type(
            "Config", (), {"email": "test@example.com", "name": "Test User"}
        )()
        with (
            patch("djb.cli.secrets.init_gpg_agent_config", return_value=True) as mock_init,
            patch("djb.cli.secrets.has_gpg_secret_key", return_value=True),
            patch("djb.cli.secrets.logger") as mock_logger,
        ):
            result = _ensure_gpg_setup(mock_cli_ctx)
            assert result is True
            mock_init.assert_called_once()
            mock_logger.done.assert_called_once()
            assert "GPG agent config" in str(mock_logger.done.call_args)

    def test_generates_gpg_key_when_missing(self, mock_cli_ctx):
        """_ensure_gpg_setup generates GPG key when none exists."""
        mock_cli_ctx.config = type(
            "Config", (), {"email": "test@example.com", "name": "Test User"}
        )()

        with (
            patch("djb.cli.secrets.init_gpg_agent_config", return_value=False),
            patch("djb.cli.secrets.has_gpg_secret_key", return_value=False),
            patch("djb.cli.secrets.generate_gpg_key") as mock_generate,
            patch("djb.cli.secrets.logger"),
        ):
            result = _ensure_gpg_setup(mock_cli_ctx)
            assert result is True
            mock_generate.assert_called_once_with(
                mock_cli_ctx.runner, "Test User", "test@example.com"
            )

    def test_uses_email_prefix_when_no_name(self, mock_cli_ctx):
        """_ensure_gpg_setup uses email prefix as name when name not configured."""
        mock_cli_ctx.config = type("Config", (), {"email": "test@example.com", "name": None})()

        with (
            patch("djb.cli.secrets.init_gpg_agent_config", return_value=False),
            patch("djb.cli.secrets.has_gpg_secret_key", return_value=False),
            patch("djb.cli.secrets.generate_gpg_key") as mock_generate,
            patch("djb.cli.secrets.logger"),
        ):
            _ensure_gpg_setup(mock_cli_ctx)
            mock_generate.assert_called_once_with(mock_cli_ctx.runner, "test", "test@example.com")

    def test_returns_false_when_no_email_configured(self, mock_cli_ctx):
        """_ensure_gpg_setup fails when email not configured."""
        mock_cli_ctx.config = type("Config", (), {"email": None, "name": "Test User"})()

        with (
            patch("djb.cli.secrets.init_gpg_agent_config", return_value=False),
            patch("djb.cli.secrets.has_gpg_secret_key", return_value=False),
            patch("djb.cli.secrets.logger") as mock_logger,
        ):
            result = _ensure_gpg_setup(mock_cli_ctx)
            assert result is False
            mock_logger.fail.assert_called_once()
            assert "Email not configured" in str(mock_logger.fail.call_args)

    def test_returns_false_when_gpg_key_generation_fails(self, mock_cli_ctx):
        """_ensure_gpg_setup returns False when GPG key generation fails."""
        mock_cli_ctx.config = type(
            "Config", (), {"email": "test@example.com", "name": "Test User"}
        )()

        with (
            patch("djb.cli.secrets.init_gpg_agent_config", return_value=False),
            patch("djb.cli.secrets.has_gpg_secret_key", return_value=False),
            patch("djb.cli.secrets.generate_gpg_key", side_effect=GpgError("Failed")),
            patch("djb.cli.secrets.logger") as mock_logger,
        ):
            result = _ensure_gpg_setup(mock_cli_ctx)
            assert result is False
            mock_logger.fail.assert_called_once()
            mock_logger.info.assert_called()  # Should suggest manual generation
