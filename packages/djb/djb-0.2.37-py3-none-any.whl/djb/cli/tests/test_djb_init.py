"""Unit tests for djb init command.

All tests use FAKE_PROJECT_DIR and mock external dependencies. Tests that
require real file I/O (secrets encryption, Django settings modification)
are in e2e/test_init.py.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from djb.config import DjbConfig
from djb.cli.init.config import configure_all_fields
from djb.cli.init.deps import (
    install_brew_dependencies,
    install_frontend_dependencies,
    install_python_dependencies,
)
from djb.cli.init.secrets import auto_commit_secrets
from djb.cli.init.shared import get_clipboard_command
from djb.cli.tests import FAKE_PROJECT_DIR
from djb.config.acquisition import AcquisitionResult


class TestInstallBrewDependencies:
    """Unit tests for install_brew_dependencies helper function."""

    def test_skips_when_skip_flag_set(self, mock_cmd_runner):
        """install_brew_dependencies skips when skip=True."""
        with patch("djb.cli.init.deps.logger") as mock_logger:
            install_brew_dependencies(mock_cmd_runner, skip=True)
            mock_logger.skip.assert_called_once_with("System dependency installation")

    def test_skips_on_unsupported_platform(self, mock_cmd_runner):
        """install_brew_dependencies skips on unsupported platforms."""
        with (
            patch("djb.cli.init.deps.sys.platform", "win32"),
            patch("djb.cli.init.deps.logger") as mock_logger,
        ):
            install_brew_dependencies(mock_cmd_runner, skip=False)
            mock_logger.skip.assert_called_once()
            assert "not supported" in str(mock_logger.skip.call_args)

    def test_raises_when_brew_not_found(self, mock_cmd_runner):
        """install_brew_dependencies raises ClickException when Homebrew not found."""
        mock_cmd_runner.check.return_value = False
        with (
            patch("djb.cli.init.deps.sys.platform", "darwin"),
            patch("djb.cli.init.deps.logger"),
        ):
            with pytest.raises(Exception) as exc_info:
                install_brew_dependencies(mock_cmd_runner, skip=False)
            assert "Homebrew is required" in str(exc_info.value)

    def test_installs_missing_sops(self, mock_cmd_runner):
        """install_brew_dependencies installs sops when not present."""

        def check_side_effect(cmd):
            " ".join(cmd)
            if cmd == ["which", "brew"]:
                return True
            if cmd == ["which", "sops"]:
                return False  # sops not installed
            return True  # Everything else already installed

        mock_cmd_runner.check.side_effect = check_side_effect
        mock_cmd_runner.run.return_value = Mock(returncode=0)

        with (
            patch("djb.cli.init.deps.sys.platform", "darwin"),
            patch("djb.cli.init.deps.logger"),
        ):
            install_brew_dependencies(mock_cmd_runner, skip=False)

        # Verify sops was installed
        cmd_calls = [call.args[0] for call in mock_cmd_runner.run.call_args_list]
        install_calls = [c for c in cmd_calls if "install" in c and "sops" in c]
        assert len(install_calls) == 1
        assert install_calls[0] == ["brew", "install", "sops"]

    def test_skips_already_installed_packages(self, mock_cmd_runner):
        """install_brew_dependencies skips already-installed packages."""
        # Everything is installed
        mock_cmd_runner.check.return_value = True

        with (
            patch("djb.cli.init.deps.sys.platform", "darwin"),
            patch("djb.cli.init.deps.logger") as mock_logger,
        ):
            install_brew_dependencies(mock_cmd_runner, skip=False)

        # No install commands should have been called
        assert mock_cmd_runner.run.call_count == 0
        # logger.info should report all packages as already installed
        info_calls = [str(c) for c in mock_logger.info.call_args_list]
        assert any("Already installed:" in c for c in info_calls)
        assert any("sops" in c for c in info_calls)
        assert any("age" in c for c in info_calls)
        assert any("gnupg" in c for c in info_calls)

    def test_installs_all_missing_packages(self, mock_cmd_runner):
        """install_brew_dependencies installs all missing packages."""

        def check_side_effect(cmd):
            # brew exists, nothing else is installed
            if cmd == ["which", "brew"]:
                return True
            return False

        mock_cmd_runner.check.side_effect = check_side_effect
        mock_cmd_runner.run.return_value = Mock(returncode=0)

        with (
            patch("djb.cli.init.deps.sys.platform", "darwin"),
            patch("djb.cli.init.deps.logger"),
        ):
            install_brew_dependencies(mock_cmd_runner, skip=False)

        # All packages should be installed
        cmd_calls = [call.args[0] for call in mock_cmd_runner.run.call_args_list]
        installed_packages = [c[2] for c in cmd_calls if c[0] == "brew" and c[1] == "install"]
        assert "sops" in installed_packages
        assert "age" in installed_packages
        assert "gnupg" in installed_packages
        assert "postgresql@17" in installed_packages
        assert "gdal" in installed_packages
        assert "oven-sh/bun/bun" in installed_packages


class TestInstallPythonDependencies:
    """Unit tests for install_python_dependencies helper function."""

    def test_skips_when_skip_flag_set(self, mock_cmd_runner):
        """install_python_dependencies skips uv sync when skip=True."""
        with patch("djb.cli.init.deps.logger") as mock_logger:
            install_python_dependencies(mock_cmd_runner, FAKE_PROJECT_DIR, skip=True)
            mock_logger.skip.assert_called_once_with("Python dependency installation")

    def test_runs_uv_sync(self, mock_cmd_runner):
        """install_python_dependencies runs uv sync with correct arguments."""
        install_python_dependencies(mock_cmd_runner, FAKE_PROJECT_DIR, skip=False)
        mock_cmd_runner.run.assert_called_once()
        call_args = mock_cmd_runner.run.call_args
        assert call_args[0][0] == ["uv", "sync", "--upgrade-package", "djb"]
        assert call_args[1]["cwd"] == FAKE_PROJECT_DIR
        assert "Installing Python dependencies" in call_args[1]["label"]


class TestInstallFrontendDependencies:
    """Unit tests for install_frontend_dependencies helper function."""

    def test_skips_when_skip_flag_set(self, mock_cmd_runner):
        """install_frontend_dependencies skips bun install when skip=True."""
        with patch("djb.cli.init.deps.logger") as mock_logger:
            install_frontend_dependencies(mock_cmd_runner, FAKE_PROJECT_DIR, skip=True)
            mock_logger.skip.assert_called_once_with("Frontend dependency installation")

    def test_skips_when_frontend_dir_missing(self, mock_cmd_runner):
        """install_frontend_dependencies skips when frontend/ directory missing."""
        with (
            patch.object(Path, "exists", return_value=False),
            patch("djb.cli.init.deps.logger") as mock_logger,
        ):
            install_frontend_dependencies(mock_cmd_runner, FAKE_PROJECT_DIR, skip=False)
            skip_call = str(mock_logger.skip.call_args)
            assert "Frontend directory not found" in skip_call

    def test_runs_bun_install(self, mock_cmd_runner):
        """install_frontend_dependencies runs bun install in frontend directory."""
        frontend_dir = FAKE_PROJECT_DIR / "frontend"

        with patch.object(Path, "exists", return_value=True):
            install_frontend_dependencies(mock_cmd_runner, FAKE_PROJECT_DIR, skip=False)
            mock_cmd_runner.run.assert_called_once()
            call_args = mock_cmd_runner.run.call_args
            assert call_args[0][0] == ["bun", "install"]
            assert call_args[1]["cwd"] == frontend_dir
            assert "Installing frontend dependencies" in call_args[1]["label"]


class TestAutoCommitSecrets:
    """Unit tests for auto_commit_secrets helper function."""

    def test_skips_when_not_git_repo(self, mock_cmd_runner):
        """auto_commit_secrets skips when not in a git repo."""
        with patch.object(Path, "exists", return_value=False):
            auto_commit_secrets(mock_cmd_runner, FAKE_PROJECT_DIR, "test@example.com")
            mock_cmd_runner.run.assert_not_called()

    def test_skips_when_no_email(self, mock_cmd_runner):
        """auto_commit_secrets skips when email is None."""
        with patch.object(Path, "exists", return_value=True):
            auto_commit_secrets(mock_cmd_runner, FAKE_PROJECT_DIR, None)
            mock_cmd_runner.run.assert_not_called()

    def test_skips_when_sops_config_not_modified(self, mock_cmd_runner):
        """auto_commit_secrets skips when .sops.yaml is not modified."""
        # git status returns empty (no changes)
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="")
        with patch.object(Path, "exists", return_value=True):
            auto_commit_secrets(mock_cmd_runner, FAKE_PROJECT_DIR, "test@example.com")
            # Only git status should be called, not git add/commit
            assert mock_cmd_runner.run.call_count == 1

    def test_commits_modified_sops_config(self, mock_cmd_runner):
        """auto_commit_secrets commits modified .sops.yaml."""

        def run_cmd_side_effect(cmd, **kwargs):
            if "status" in cmd:
                return Mock(returncode=0, stdout="M secrets/.sops.yaml")
            return Mock(returncode=0, stdout="[main abc123] Add public key")

        mock_cmd_runner.run.side_effect = run_cmd_side_effect

        with (
            patch.object(Path, "exists", return_value=True),
            patch("djb.cli.init.secrets.logger"),
        ):
            auto_commit_secrets(mock_cmd_runner, FAKE_PROJECT_DIR, "test@example.com")

        # Verify git add and commit were called
        cmd_calls = [call.args[0] for call in mock_cmd_runner.run.call_args_list]
        add_calls = [c for c in cmd_calls if c[0] == "git" and c[1] == "add"]
        commit_calls = [c for c in cmd_calls if c[0] == "git" and c[1] == "commit"]
        assert len(add_calls) == 1
        assert "secrets/.sops.yaml" in add_calls[0]
        assert len(commit_calls) == 1
        assert "Add public key for test@example.com" in commit_calls[0]


class TestGetClipboardCommand:
    """Unit tests for get_clipboard_command platform detection function."""

    def test_returns_pbcopy_on_macos(self):
        """get_clipboard_command returns 'pbcopy' on macOS."""
        with (
            patch("djb.cli.init.shared.sys.platform", "darwin"),
            patch("builtins.open", side_effect=FileNotFoundError),
        ):
            result = get_clipboard_command()
            assert result == "pbcopy"

    def test_returns_clip_exe_on_wsl2(self):
        """get_clipboard_command returns 'clip.exe' on WSL2."""
        # WSL2 is detected by reading /proc/version and finding "microsoft"
        mock_proc_version = "Linux version 5.15.90.1-microsoft-standard-WSL2"
        with (
            patch("djb.cli.init.shared.sys.platform", "linux"),
            patch("builtins.open", return_value=__import__("io").StringIO(mock_proc_version)),
        ):
            result = get_clipboard_command()
            assert result == "clip.exe"

    def test_returns_xclip_on_linux(self):
        """get_clipboard_command returns 'xclip' on regular Linux."""
        # Regular Linux (not WSL) - /proc/version doesn't contain "microsoft"
        mock_proc_version = "Linux version 6.2.0-generic (buildd@lcy02-amd64-001)"
        with (
            patch("djb.cli.init.shared.sys.platform", "linux"),
            patch("builtins.open", return_value=__import__("io").StringIO(mock_proc_version)),
        ):
            result = get_clipboard_command()
            assert result == "xclip"

    def test_returns_xclip_when_proc_version_not_found(self):
        """get_clipboard_command falls back to 'xclip' when /proc/version missing."""
        with (
            patch("djb.cli.init.shared.sys.platform", "linux"),
            patch("builtins.open", side_effect=FileNotFoundError),
        ):
            result = get_clipboard_command()
            assert result == "xclip"

    def test_returns_xclip_when_proc_version_permission_denied(self):
        """get_clipboard_command falls back to 'xclip' on permission error."""
        with (
            patch("djb.cli.init.shared.sys.platform", "linux"),
            patch("builtins.open", side_effect=PermissionError),
        ):
            result = get_clipboard_command()
            assert result == "xclip"

    def test_wsl2_detection_case_insensitive(self):
        """get_clipboard_command WSL2 detection is case-insensitive."""
        # "Microsoft" with capital M should still be detected
        mock_proc_version = "Linux version 5.15.90.1-Microsoft-standard-WSL2"
        with (
            patch("djb.cli.init.shared.sys.platform", "linux"),
            patch("builtins.open", return_value=__import__("io").StringIO(mock_proc_version)),
        ):
            result = get_clipboard_command()
            assert result == "clip.exe"


class TestConfigureAllFields:
    """Unit tests for configure_all_fields orchestration function."""

    def test_returns_configured_values(self, djb_config: DjbConfig):
        """configure_all_fields returns dict of configured field values."""
        mock_results = [
            ("name", AcquisitionResult(value="Test User", should_save=True)),
            ("email", AcquisitionResult(value="test@example.com", should_save=True)),
        ]
        project_dir = djb_config.project_dir

        with (
            patch("djb.cli.init.config.acquire_all_fields", return_value=iter(mock_results)),
            patch("djb.cli.init.config.logger"),
        ):
            result = configure_all_fields(project_dir, djb_config)

        assert result == {"name": "Test User", "email": "test@example.com"}

    def test_tracks_git_config_sources(self, djb_config: DjbConfig):
        """configure_all_fields tracks values copied from git config."""
        mock_results = [
            (
                "name",
                AcquisitionResult(value="Git User", should_save=True, source_name="git config"),
            ),
            (
                "email",
                AcquisitionResult(
                    value="git@example.com", should_save=True, source_name="git config"
                ),
            ),
        ]
        project_dir = djb_config.project_dir

        with (
            patch("djb.cli.init.config.acquire_all_fields", return_value=iter(mock_results)),
            patch("djb.cli.init.config.logger") as mock_logger,
        ):
            configure_all_fields(project_dir, djb_config)

        # Should log a summary about git config copies
        info_calls = [str(c) for c in mock_logger.info.call_args_list]
        assert any("git config" in c for c in info_calls)

    def test_logs_config_file_location(self, djb_config):
        """configure_all_fields logs the config file location."""
        mock_results = [
            ("name", AcquisitionResult(value="Test User", should_save=True)),
        ]
        project_dir = djb_config.project_dir

        with (
            patch("djb.cli.init.config.acquire_all_fields", return_value=iter(mock_results)),
            patch("djb.cli.init.config.logger") as mock_logger,
        ):
            configure_all_fields(project_dir, djb_config)

        # Should log the config file path
        info_calls = [str(c) for c in mock_logger.info.call_args_list]
        assert any("Config saved to" in c for c in info_calls)

    def test_does_not_log_config_path_for_non_identity_fields(self, djb_config):
        """configure_all_fields only logs config path for name/email fields."""
        mock_results = [
            ("project_name", AcquisitionResult(value="my-project", should_save=True)),
        ]
        project_dir = djb_config.project_dir

        with (
            patch("djb.cli.init.config.acquire_all_fields", return_value=iter(mock_results)),
            patch("djb.cli.init.config.logger") as mock_logger,
        ):
            configure_all_fields(project_dir, djb_config)

        # Should NOT log "Config saved to" for non-identity fields
        info_calls = [str(c) for c in mock_logger.info.call_args_list]
        assert not any("Config saved to" in c for c in info_calls)
