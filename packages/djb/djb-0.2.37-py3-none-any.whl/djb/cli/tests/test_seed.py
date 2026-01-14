"""Tests for djb seed CLI command."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from djb.cli.djb import djb_cli
from djb.cli.seed import load_seed_command, run_seed_command
from djb.config import DjbConfig


class TestSeedCommand:
    """Tests for seed CLI command.

    Tests needing config overrides use make_djb_config factory fixture.
    Tests with default config use djb_config fixture directly.
    """

    def test_help_unconfigured(self, cli_runner, djb_config):
        """djb seed --help shows configuration instructions when no seed_command is configured."""
        result = cli_runner.invoke(djb_cli, ["seed", "--help"])

        assert result.exit_code == 0
        assert "Run the host project's seed command" in result.output
        assert "No seed_command is currently configured" in result.output
        assert "djb config seed_command" in result.output
        assert "Example seed command in your project" in result.output

    def test_help_configured(self, cli_runner, make_djb_config):
        """djb seed --help shows host command help when seed_command is configured."""

        @click.command()
        @click.option("--truncate", is_flag=True, help="Clear database before seeding")
        def mock_seed(truncate):
            """Populate the database with sample data."""

        config = make_djb_config(DjbConfig(seed_command="myapp.cli:seed"))
        with (
            patch("djb.cli.djb.get_djb_config", return_value=config),
            patch("djb.cli.seed.load_seed_command", return_value=mock_seed),
        ):
            result = cli_runner.invoke(djb_cli, ["seed", "--help"])

        assert result.exit_code == 0
        assert "Run the host project's seed command" in result.output
        assert "Configured seed command: myapp.cli:seed" in result.output
        assert "--- Host command help ---" in result.output
        assert "Populate the database with sample data" in result.output

    def test_seed_without_config_fails(self, cli_runner, djb_config):
        """djb seed without config fails with helpful message."""
        result = cli_runner.invoke(djb_cli, ["seed"])

        assert result.exit_code == 1
        assert "No seed_command configured" in result.output
        assert "djb config seed_command" in result.output

    def test_seed_with_invalid_config_fails(self, cli_runner, make_djb_config):
        """djb seed with invalid module path fails."""
        config = make_djb_config(DjbConfig(seed_command="nonexistent.module:cmd"))
        with (
            patch("djb.cli.djb.get_djb_config", return_value=config),
            patch("djb.cli.seed.load_seed_command", return_value=None),
        ):
            result = cli_runner.invoke(djb_cli, ["seed"])

        assert result.exit_code == 1
        assert "Could not load seed_command" in result.output

    def test_seed_runs_host_command(self, cli_runner, make_djb_config):
        """djb seed invokes the configured host command."""
        invoked = []

        @click.command()
        def mock_seed_cmd():
            """Mock seed command."""
            invoked.append(True)

        config = make_djb_config(DjbConfig(seed_command="myapp.cli:seed"))
        with (
            patch("djb.cli.djb.get_djb_config", return_value=config),
            patch("djb.cli.seed.load_seed_command", return_value=mock_seed_cmd),
        ):
            result = cli_runner.invoke(djb_cli, ["seed"])

        assert result.exit_code == 0
        assert invoked == [True], "Host command should have been invoked"

    def test_seed_passes_extra_args_to_host_command(self, cli_runner, make_djb_config):
        """djb seed passes extra arguments to the host command."""
        received_args = {}

        @click.command()
        @click.option("--truncate", is_flag=True)
        @click.option("--count", type=int, default=10)
        def mock_seed_cmd(truncate, count):
            """Mock seed command with options."""
            received_args["truncate"] = truncate
            received_args["count"] = count

        config = make_djb_config(DjbConfig(seed_command="myapp.cli:seed"))
        with (
            patch("djb.cli.djb.get_djb_config", return_value=config),
            patch("djb.cli.seed.load_seed_command", return_value=mock_seed_cmd),
        ):
            result = cli_runner.invoke(djb_cli, ["seed", "--truncate", "--count", "50"])

        assert result.exit_code == 0
        assert received_args == {"truncate": True, "count": 50}

    def test_seed_host_command_failure_propagates(self, cli_runner, make_djb_config):
        """djb seed propagates host command failures."""

        @click.command()
        def mock_seed_cmd():
            """Mock seed command that fails."""
            raise click.ClickException("Database connection failed")

        config = make_djb_config(DjbConfig(seed_command="myapp.cli:seed"))
        with (
            patch("djb.cli.djb.get_djb_config", return_value=config),
            patch("djb.cli.seed.load_seed_command", return_value=mock_seed_cmd),
        ):
            result = cli_runner.invoke(djb_cli, ["seed"])

        assert result.exit_code == 1
        assert "Database connection failed" in result.output


class TestLoadSeedCommand:
    """Tests for load_seed_command() function directly."""

    def test_load_valid_command(self):
        """load_seed_command loads a valid Click command from module:attr format."""
        # Create a mock module with a click command
        mock_command = click.Command(name="test_cmd", callback=lambda: None)
        mock_module = Mock()
        mock_module.my_command = mock_command

        with patch("djb.cli.seed.importlib.import_module", return_value=mock_module):
            result = load_seed_command("mymodule:my_command")

        assert result is mock_command

    def test_load_command_invalid_format_missing_colon(self):
        """load_seed_command returns None and logs warning for invalid format."""
        with patch("djb.cli.seed.logger") as mock_logger:
            result = load_seed_command("invalid_format_no_colon")

        assert result is None
        mock_logger.warning.assert_called_once()
        assert "Invalid seed_command format" in mock_logger.warning.call_args[0][0]

    def test_load_command_nonexistent_module(self):
        """load_seed_command returns None and logs warning for non-existent module."""
        # Patch logger first to avoid issues with import_module affecting module resolution
        with patch("djb.cli.seed.logger") as mock_logger:
            with patch(
                "djb.cli.seed.importlib.import_module",
                side_effect=ImportError("No module named 'nonexistent'"),
            ):
                result = load_seed_command("nonexistent.module:cmd")

        assert result is None
        mock_logger.warning.assert_called_once()
        assert "Could not import" in mock_logger.warning.call_args[0][0]

    def test_load_command_nonexistent_attribute(self):
        """load_seed_command returns None and logs warning for non-existent attribute."""

        class ModuleWithoutAttr:
            """Module mock that raises AttributeError for getattr."""

            pass

        mock_module = ModuleWithoutAttr()

        with patch("djb.cli.seed.logger") as mock_logger:
            with patch("djb.cli.seed.importlib.import_module", return_value=mock_module):
                result = load_seed_command("mymodule:nonexistent_attr")

        assert result is None
        mock_logger.warning.assert_called_once()
        assert "Could not find" in mock_logger.warning.call_args[0][0]

    def test_load_command_not_a_click_command(self):
        """load_seed_command returns None when attribute isn't a Click command."""
        mock_module = Mock()
        mock_module.not_a_command = "just a string"

        with patch("djb.cli.seed.logger") as mock_logger:
            with patch("djb.cli.seed.importlib.import_module", return_value=mock_module):
                result = load_seed_command("mymodule:not_a_command")

        assert result is None
        mock_logger.warning.assert_called_once()
        assert "is not a Click command" in mock_logger.warning.call_args[0][0]

    def test_load_command_handles_callable_that_is_not_command(self):
        """load_seed_command returns None when callable isn't a Click command."""
        mock_module = Mock()
        mock_module.my_function = lambda: "hello"

        with patch("djb.cli.seed.logger") as mock_logger:
            with patch("djb.cli.seed.importlib.import_module", return_value=mock_module):
                result = load_seed_command("mymodule:my_function")

        assert result is None
        mock_logger.warning.assert_called_once()

    def test_load_command_with_click_group(self):
        """load_seed_command loads Click groups successfully."""
        mock_group = click.Group(name="test_group")
        mock_module = Mock()
        mock_module.my_group = mock_group

        with patch("djb.cli.seed.importlib.import_module", return_value=mock_module):
            result = load_seed_command("mymodule:my_group")

        assert result is mock_group


class TestRunSeedCommand:
    """Tests for run_seed_command() function directly."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock DjbConfig."""
        config = MagicMock()
        config.seed_command = None
        return config

    def test_run_seed_no_command_configured(self, mock_config):
        """run_seed_command returns False and logs warning when seed_command missing."""
        mock_config.seed_command = None

        with patch("djb.cli.seed.logger") as mock_logger:
            result = run_seed_command(mock_config)

        assert result is False
        mock_logger.warning.assert_called_once()
        assert "No seed_command configured" in mock_logger.warning.call_args[0][0]

    def test_run_seed_load_fails(self, mock_config):
        """run_seed_command returns False when load fails."""
        mock_config.seed_command = "bad.module:cmd"

        with (
            patch("djb.cli.seed.django.setup"),
            patch("djb.cli.seed.load_seed_command", return_value=None),
        ):
            result = run_seed_command(mock_config)

        assert result is False

    def test_run_seed_successful_execution(self, mock_config):
        """run_seed_command returns True on successful execution."""
        mock_config.seed_command = "myapp.cli:seed"

        invoked = []

        @click.command()
        def mock_seed():
            invoked.append(True)

        with (
            patch("djb.cli.seed.django.setup"),
            patch("djb.cli.seed.load_seed_command", return_value=mock_seed),
        ):
            result = run_seed_command(mock_config)

        assert result is True
        assert invoked == [True]

    def test_run_seed_click_exception_returns_false(self, mock_config):
        """run_seed_command returns False on ClickException from host command."""
        mock_config.seed_command = "myapp.cli:seed"

        @click.command()
        def failing_seed():
            raise click.ClickException("Seeding failed")

        with (
            patch("djb.cli.seed.django.setup"),
            patch("djb.cli.seed.load_seed_command", return_value=failing_seed),
            patch("djb.cli.seed.logger") as mock_logger,
        ):
            result = run_seed_command(mock_config)

        assert result is False
        mock_logger.error.assert_called_once()
        assert "Seed failed" in mock_logger.error.call_args[0][0]
        assert "Seeding failed" in mock_logger.error.call_args[0][0]

    def test_run_seed_generic_exception_returns_false(self, mock_config):
        """run_seed_command returns False on generic exception from host command."""
        mock_config.seed_command = "myapp.cli:seed"

        @click.command()
        def crashing_seed():
            raise ValueError("Unexpected error")

        with (
            patch("djb.cli.seed.django.setup"),
            patch("djb.cli.seed.load_seed_command", return_value=crashing_seed),
            patch("djb.cli.seed.logger") as mock_logger,
        ):
            result = run_seed_command(mock_config)

        assert result is False
        mock_logger.error.assert_called_once()
        assert "Seed failed" in mock_logger.error.call_args[0][0]

    def test_run_seed_command_without_options(self, mock_config):
        """run_seed_command works with simple commands without options."""
        mock_config.seed_command = "myapp.cli:seed"

        invoked = []

        @click.command()
        def simple_seed():
            """A simple seed command without options."""
            invoked.append(True)

        with (
            patch("djb.cli.seed.django.setup"),
            patch("djb.cli.seed.load_seed_command", return_value=simple_seed),
        ):
            result = run_seed_command(mock_config)

        assert result is True
        assert invoked == [True]
