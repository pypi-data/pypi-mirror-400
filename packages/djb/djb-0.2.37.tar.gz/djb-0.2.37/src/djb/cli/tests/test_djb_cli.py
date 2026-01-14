"""Unit tests for djb CLI main entry point.

Tests that require real file I/O (mode persistence, config loading) are in e2e/test_djb_cli.py.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli, print_banner
from djb.config import DjbConfig
from djb.types import Mode


class TestDjbCliHelp:
    """Tests for djb CLI help and options."""

    def test_help_shows_options_and_choices(self):
        """djb --help shows all global options and choices."""
        runner = CliRunner()
        result = runner.invoke(djb_cli, ["--help"])

        assert result.exit_code == 0

        # Global options
        assert "--project-dir" in result.output
        assert "--mode" in result.output
        assert "--platform" in result.output
        assert "--log-level" in result.output

        # Mode choices
        assert "development" in result.output
        assert "staging" in result.output
        assert "production" in result.output

        # Platform choices
        assert "heroku" in result.output


class TestPrintBanner:
    """Tests for print_banner function."""

    @pytest.mark.parametrize(
        "mode,expected",
        [
            (Mode.DEVELOPMENT, "development"),
            (Mode.STAGING, "staging"),
            (Mode.PRODUCTION, "production"),
        ],
    )
    def test_print_banner_shows_mode(self, capsys, make_djb_config, mode, expected):
        """print_banner shows correct mode in banner."""
        config = make_djb_config(DjbConfig(mode=mode))
        print_banner(config)

        captured = capsys.readouterr()
        assert "[djb]" in captured.out
        assert expected in captured.out

    def test_print_banner_format(self, capsys, make_djb_config):
        """print_banner formats banner with mode and platform."""
        config = make_djb_config()
        print_banner(config)

        captured = capsys.readouterr()
        assert "mode:" in captured.out
        assert "platform:" in captured.out
        assert "heroku" in captured.out


# Tests for banner display, mode/platform options with real project dirs
# are in e2e/test_djb_cli.py
