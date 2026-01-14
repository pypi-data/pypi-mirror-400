"""Unit tests for djb publish module.

All tests use FAKE_PROJECT_DIR and mock external dependencies. Tests that
require real file I/O (TOML parsing, file operations) are in e2e/test_publish.py.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import click
import pytest

from djb.cli.publish import (
    bump_version,
    get_current_branch,
    wait_for_uv_resolvable,
)
from djb.cli.tests import FAKE_PROJECT_DIR


class TestGetCurrentBranch:
    """Tests for get_current_branch function - covers git command and fallback."""

    def test_returns_branch_name(self, mock_cli_ctx):
        """get_current_branch returns branch name from git command."""
        mock_cli_ctx.runner.run.return_value = Mock(stdout="feature-branch\n")

        result = get_current_branch(mock_cli_ctx, FAKE_PROJECT_DIR)

        assert result == "feature-branch"
        mock_cli_ctx.runner.run.assert_called_once()
        call_args = mock_cli_ctx.runner.run.call_args
        assert call_args[0][0] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        assert call_args[1]["cwd"] == FAKE_PROJECT_DIR

    def test_falls_back_to_main_on_empty_output(self, mock_cli_ctx):
        """get_current_branch falls back to 'main' when git returns empty output."""
        # Detached HEAD or empty output scenario
        mock_cli_ctx.runner.run.return_value = Mock(stdout="")

        result = get_current_branch(mock_cli_ctx, FAKE_PROJECT_DIR)

        assert result == "main"

    def test_falls_back_to_main_on_whitespace_only(self, mock_cli_ctx):
        """get_current_branch falls back to 'main' when git returns only whitespace."""
        mock_cli_ctx.runner.run.return_value = Mock(stdout="   \n")

        result = get_current_branch(mock_cli_ctx, FAKE_PROJECT_DIR)

        assert result == "main"

    def test_strips_whitespace_from_branch_name(self, mock_cli_ctx):
        """get_current_branch strips leading/trailing whitespace from branch name."""
        mock_cli_ctx.runner.run.return_value = Mock(stdout="  main  \n")

        result = get_current_branch(mock_cli_ctx, FAKE_PROJECT_DIR)

        assert result == "main"


class TestBumpVersion:
    """Tests for bump_version function."""

    def test_bump_patch(self):
        """bump_version bumps patch version."""
        assert bump_version("0.2.5", "patch") == "0.2.6"

    def test_bump_minor(self):
        """bump_version bumps minor version and resets patch."""
        assert bump_version("0.2.5", "minor") == "0.3.0"

    def test_bump_major(self):
        """bump_version bumps major version and resets minor and patch."""
        assert bump_version("0.2.5", "major") == "1.0.0"

    def test_invalid_version_format(self):
        """bump_version raises for invalid version format."""
        with pytest.raises(click.ClickException):
            bump_version("invalid", "patch")

    def test_unknown_part(self):
        """bump_version raises for unknown version part."""
        with pytest.raises(click.ClickException):
            bump_version("0.2.5", "unknown")


class TestWaitForUvResolvable:
    """Tests for wait_for_uv_resolvable function."""

    def test_returns_true_on_immediate_success(self, mock_cli_ctx):
        """wait_for_uv_resolvable returns True when first lock attempt succeeds."""
        with (
            patch("djb.cli.publish.bust_uv_cache") as mock_bust,
            patch("djb.cli.publish.regenerate_uv_lock", return_value=True) as mock_lock,
            patch("djb.cli.publish.time.sleep") as mock_sleep,
        ):
            result = wait_for_uv_resolvable(mock_cli_ctx, FAKE_PROJECT_DIR, "1.0.0")

        assert result is True
        mock_bust.assert_called_once()
        mock_lock.assert_called_once_with(mock_cli_ctx.runner, FAKE_PROJECT_DIR, quiet=True)
        mock_sleep.assert_not_called()

    def test_retries_until_success(self, mock_cli_ctx):
        """wait_for_uv_resolvable retries with exponential backoff until success."""
        with (
            patch("djb.cli.publish.bust_uv_cache") as mock_bust,
            patch("djb.cli.publish.regenerate_uv_lock") as mock_lock,
            patch("djb.cli.publish.time.sleep") as mock_sleep,
            patch("djb.cli.publish.time.time") as mock_time,
        ):
            # First two attempts fail, third succeeds
            mock_lock.side_effect = [False, False, True]
            # Start at 0, then 1, then 2 (still under timeout of 300)
            mock_time.side_effect = [0, 1, 2, 3]

            result = wait_for_uv_resolvable(mock_cli_ctx, FAKE_PROJECT_DIR, "1.0.0", timeout=300)

        assert result is True
        assert mock_bust.call_count == 3
        assert mock_lock.call_count == 3
        # Should have slept twice (after first and second failures)
        assert mock_sleep.call_count == 2
        # Check exponential backoff: first sleep is initial_interval (5), second is doubled (10)
        mock_sleep.assert_any_call(5)
        mock_sleep.assert_any_call(10)

    def test_returns_false_on_timeout(self, mock_cli_ctx):
        """wait_for_uv_resolvable returns False when package isn't resolvable in time."""
        with (
            patch("djb.cli.publish.bust_uv_cache"),
            patch("djb.cli.publish.regenerate_uv_lock", return_value=False) as mock_lock,
            patch("djb.cli.publish.time.sleep"),
            patch("djb.cli.publish.time.time") as mock_time,
        ):
            # Time progresses past timeout
            mock_time.side_effect = [0, 0, 301]  # start, first check, second check (past timeout)

            result = wait_for_uv_resolvable(mock_cli_ctx, FAKE_PROJECT_DIR, "1.0.0", timeout=300)

        assert result is False
        assert mock_lock.call_count == 1  # Only one attempt before timeout

    def test_uses_custom_timeout(self, mock_cli_ctx):
        """wait_for_uv_resolvable respects custom timeout value."""
        with (
            patch("djb.cli.publish.bust_uv_cache"),
            patch("djb.cli.publish.regenerate_uv_lock", return_value=False),
            patch("djb.cli.publish.time.sleep"),
            patch("djb.cli.publish.time.time") as mock_time,
        ):
            # With custom timeout of 60, time=61 should exceed it
            mock_time.side_effect = [0, 0, 61]

            result = wait_for_uv_resolvable(mock_cli_ctx, FAKE_PROJECT_DIR, "1.0.0", timeout=60)

        assert result is False

    def test_exponential_backoff_caps_at_max_interval(self, mock_cli_ctx):
        """wait_for_uv_resolvable exponential backoff respects max_interval."""
        with (
            patch("djb.cli.publish.bust_uv_cache"),
            patch("djb.cli.publish.regenerate_uv_lock") as mock_lock,
            patch("djb.cli.publish.time.sleep") as mock_sleep,
            patch("djb.cli.publish.time.time") as mock_time,
        ):
            # Many failures then success
            mock_lock.side_effect = [False, False, False, False, False, True]
            # Time progresses slowly to allow many retries
            mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6]

            result = wait_for_uv_resolvable(
                mock_cli_ctx,
                FAKE_PROJECT_DIR,
                "1.0.0",
                initial_interval=5,
                max_interval=15,
                timeout=300,
            )

        assert result is True
        # Sleep intervals: 5, 10, 15, 15, 15 (capped at 15)
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls == [5, 10, 15, 15, 15]

    def test_custom_initial_interval(self, mock_cli_ctx):
        """wait_for_uv_resolvable uses custom initial_interval value."""
        with (
            patch("djb.cli.publish.bust_uv_cache"),
            patch("djb.cli.publish.regenerate_uv_lock") as mock_lock,
            patch("djb.cli.publish.time.sleep") as mock_sleep,
            patch("djb.cli.publish.time.time") as mock_time,
        ):
            mock_lock.side_effect = [False, True]
            mock_time.side_effect = [0, 1, 2]

            result = wait_for_uv_resolvable(
                mock_cli_ctx, FAKE_PROJECT_DIR, "1.0.0", initial_interval=10
            )

        assert result is True
        mock_sleep.assert_called_once_with(10)
