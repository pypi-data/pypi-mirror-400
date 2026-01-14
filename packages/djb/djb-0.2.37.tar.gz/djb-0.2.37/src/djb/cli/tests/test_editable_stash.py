"""Tests for djb editable_stash module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from djb.cli.editable_stash import (
    bust_uv_cache,
    regenerate_uv_lock,
    restore_editable,
    stashed_editable,
)
from djb.cli.tests import FAKE_PROJECT_DIR


class TestBustUvCache:
    """Tests for bust_uv_cache function."""

    def test_runs_uv_cache_clean(self, mock_cmd_runner):
        """bust_uv_cache runs uv cache clean djb command."""
        mock_cmd_runner.run.return_value = Mock(returncode=0)
        bust_uv_cache(mock_cmd_runner)

        mock_cmd_runner.run.assert_called_once()
        args = mock_cmd_runner.run.call_args[0][0]
        assert args == ["uv", "cache", "clean", "djb"]


class TestRegenerateUvLock:
    """Tests for regenerate_uv_lock function."""

    def test_runs_uv_lock_refresh(self, mock_cmd_runner):
        """regenerate_uv_lock runs uv lock --refresh command."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")
        result = regenerate_uv_lock(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is True
        mock_cmd_runner.run.assert_called_once()
        args = mock_cmd_runner.run.call_args[0][0]
        assert args == ["uv", "lock", "--refresh"]
        assert mock_cmd_runner.run.call_args[1]["cwd"] == FAKE_PROJECT_DIR

    def test_returns_false_on_failure(self, mock_cmd_runner):
        """regenerate_uv_lock returns False when uv lock --refresh fails."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="error")
        result = regenerate_uv_lock(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True)

        assert result is False

    def test_prints_error_when_not_quiet(self, mock_cmd_runner):
        """regenerate_uv_lock prints error message when not in quiet mode."""
        with patch("djb.cli.editable_stash.logger") as mock_logger:
            mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="some error")
            regenerate_uv_lock(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=False)

        # Should have printed an error via logger
        mock_logger.fail.assert_called()


class TestStashedEditableContextManager:
    """Tests for stashed_editable context manager."""

    def test_yields_true_when_editable(self, mock_cmd_runner):
        """stashed_editable yields True when djb was in editable mode."""
        with (
            patch("djb.cli.editable_stash.is_djb_editable", return_value=True),
            patch("djb.cli.editable_stash.uninstall_editable_djb") as mock_uninstall,
            patch("djb.cli.editable_stash.install_editable_djb") as mock_install,
        ):
            with stashed_editable(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True) as was_editable:
                assert was_editable is True
                # Inside context: should have called uninstall
                mock_uninstall.assert_called_once_with(
                    mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True
                )
                mock_install.assert_not_called()

            # After context: should have called install
            mock_install.assert_called_once_with(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True)

    def test_yields_false_when_not_editable(self, mock_cmd_runner):
        """stashed_editable yields False when djb was not in editable mode."""
        with (
            patch("djb.cli.editable_stash.is_djb_editable", return_value=False),
            patch("djb.cli.editable_stash.uninstall_editable_djb") as mock_uninstall,
            patch("djb.cli.editable_stash.install_editable_djb") as mock_install,
        ):
            with stashed_editable(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True) as was_editable:
                assert was_editable is False
                # Should not call uninstall when not editable
                mock_uninstall.assert_not_called()

            # Should not call install when was not editable
            mock_install.assert_not_called()

    def test_restores_on_exception(self, mock_cmd_runner):
        """stashed_editable restores editable mode even on exception."""
        with (
            patch("djb.cli.editable_stash.is_djb_editable", return_value=True),
            patch("djb.cli.editable_stash.uninstall_editable_djb"),
            patch("djb.cli.editable_stash.install_editable_djb") as mock_install,
        ):
            with pytest.raises(ValueError):
                with stashed_editable(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True):
                    raise ValueError("Test exception")

            # Should still have called install to restore
            mock_install.assert_called_once_with(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True)

    def test_prints_messages_when_not_quiet(self, mock_cmd_runner):
        """stashed_editable prints status messages when not in quiet mode."""
        with (
            patch("djb.cli.editable_stash.is_djb_editable", return_value=True),
            patch("djb.cli.editable_stash.uninstall_editable_djb"),
            patch("djb.cli.editable_stash.install_editable_djb"),
            patch("djb.cli.editable_stash.logger") as mock_logger,
        ):
            with stashed_editable(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=False):
                pass

        # Should have printed messages via logger
        assert mock_logger.info.call_count >= 2


class TestRestoreEditable:
    """Tests for restore_editable function."""

    def test_calls_install_editable_djb(self, mock_cmd_runner):
        """restore_editable calls install_editable_djb with correct arguments."""
        with patch("djb.cli.editable_stash.install_editable_djb") as mock_install:
            mock_install.return_value = True
            result = restore_editable(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True)

        assert result is True
        mock_install.assert_called_once_with(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True)

    def test_returns_false_on_failure(self, mock_cmd_runner):
        """restore_editable returns False when install_editable_djb fails."""
        with patch("djb.cli.editable_stash.install_editable_djb") as mock_install:
            mock_install.return_value = False
            result = restore_editable(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is False
