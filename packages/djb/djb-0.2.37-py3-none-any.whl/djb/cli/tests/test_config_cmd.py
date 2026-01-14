"""Unit tests for djb config CLI command.

Tests that require real file I/O (config file operations) are in e2e/test_config_cmd.py.
"""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

from djb.cli.config_cmd import _format_json_with_provenance
from djb.cli.djb import djb_cli
from djb.config import DjbConfig, get_field_descriptor
from djb.config.field import ConfigFieldABC
from djb.config.storage.io import DictConfigIO, EnvConfigIO, LocalConfigIO


class TestConfigShow:
    """Tests for djb config show output format."""

    def test_show_outputs_json(self, cli_runner, djb_config):
        """'show' subcommand outputs valid JSON."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "show"])

        assert result.exit_code == 0
        # Should be valid JSON
        config = json.loads(result.output)
        assert isinstance(config, dict)

    def test_show_contains_expected_keys(self, cli_runner, djb_config):
        """'show' output contains all expected config keys."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Get expected keys from DjbConfig.__fields__
        # Excludes private fields (starting with _)
        expected_keys = {name for name in DjbConfig.__fields__ if not name.startswith("_")}
        assert expected_keys == set(config.keys())

    def test_show_excludes_private_attributes(self, cli_runner, djb_config):
        """'show' output excludes private attributes."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Private attributes should not be in output
        assert "_loaded" not in config
        assert "_provenance" not in config

    def test_show_serializes_enums_as_strings(self, cli_runner, djb_config):
        """Mode and platform are serialized as strings, not enum objects."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Should be string values, not enum representations
        assert config["mode"] == "development"
        assert config["platform"] == "heroku"

    def test_show_serializes_path_as_string(self, cli_runner, djb_config):
        """project_dir is serialized as a string path."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "show"])

        assert result.exit_code == 0
        config = json.loads(result.output)

        # Should be a string, not a Path object representation
        assert isinstance(config["project_dir"], str)
        assert not config["project_dir"].startswith("PosixPath")

    def test_config_without_args_shows_help(self, cli_runner, djb_config):
        """'djb config' without args shows help."""
        result = cli_runner.invoke(djb_cli, ["-q", "config"])

        assert result.exit_code == 0
        assert "Manage djb configuration" in result.output
        assert "show" in result.output

    def test_with_provenance_outputs_json_with_comments(self, cli_runner, djb_config):
        """--with-provenance shows JSON with // comments on separate lines."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "show", "--with-provenance"])

        assert result.exit_code == 0
        # Should contain JSON structure with // comments
        assert "{" in result.output
        assert "}" in result.output
        assert "//" in result.output
        assert '"project_dir":' in result.output

    def test_with_provenance_shows_all_keys(self, cli_runner, djb_config):
        """--with-provenance output contains all config keys."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "show", "--with-provenance"])

        assert result.exit_code == 0
        assert '"project_dir":' in result.output
        assert '"project_name":' in result.output
        assert '"mode":' in result.output


# Tests for config project_name subcommand that require file I/O are in e2e/test_config_cmd.py


class TestFormatWithProvenance:
    """Unit tests for _format_json_with_provenance helper function."""

    def test_formats_config_as_json_with_comments(self, make_djb_config):
        """_format_json_with_provenance produces JSON with // comments on separate lines."""
        config = make_djb_config()
        # Create a mock config object
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "project_dir": "/path/to/project",
            "mode": "development",
        }
        cli_io = DictConfigIO(config, {"project_dir": "/path/to/project"})
        mock_config.get_source.side_effect = lambda key: {
            "project_dir": (cli_io,),
            "mode": None,  # Not set
        }.get(key)

        result = _format_json_with_provenance(mock_config)

        # Should have JSON structure with // comments
        assert "{" in result
        assert "}" in result
        assert "//" in result
        assert '"project_dir":' in result
        assert '"mode":' in result

    def test_includes_provenance_for_each_key(self, make_djb_config):
        """_format_json_with_provenance shows provenance for each config key."""
        config = make_djb_config()
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "name": "Test User",
            "email": "test@example.com",
        }
        local_io = LocalConfigIO(config)
        env_io = EnvConfigIO(config, None)
        mock_config.get_source.side_effect = lambda key: {
            "name": (local_io,),
            "email": (env_io,),
        }.get(key)

        result = _format_json_with_provenance(mock_config)

        # Should include provenance from IO names
        assert "local.toml" in result
        assert "env" in result

    def test_shows_not_set_for_none_source(self):
        """_format_json_with_provenance shows '(not set)' when source is None."""
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "seed_command": None,
        }
        mock_config.get_source.return_value = None

        result = _format_json_with_provenance(mock_config)

        assert "(not set)" in result

    def test_provenance_on_separate_line(self, make_djb_config):
        """_format_json_with_provenance puts provenance on line before value."""
        config = make_djb_config()
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "name": "test",
        }
        cli_io = DictConfigIO(config, {})
        mock_config.get_source.return_value = (cli_io,)

        result = _format_json_with_provenance(mock_config)

        # Should have "// name: cli" on separate line before "name:"
        assert "// name: cli" in result
        assert '"name": "test"' in result


class TestGetFieldDescriptor:
    """Unit tests for get_field_descriptor helper function."""

    def test_returns_config_field_for_valid_field(self):
        """get_field_descriptor returns ConfigFieldABC for valid field."""
        result = get_field_descriptor("project_name")
        assert isinstance(result, ConfigFieldABC)
        assert result.field_name == "project_name"

    def test_raises_for_unknown_field(self):
        """get_field_descriptor raises AttributeError for unknown field."""
        with pytest.raises(AttributeError) as exc_info:
            get_field_descriptor("nonexistent_field")
        assert "nonexistent_field" in str(exc_info.value)


class TestConfigGenericCommands:
    """Tests for generic get/set/delete subcommands."""

    def test_get_unknown_key_shows_error(self, cli_runner, djb_config):
        """Get with unknown key shows error."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "get", "unknown_key"])
        assert result.exit_code != 0
        assert "unknown_key" in result.output

    def test_set_unknown_key_shows_error(self, cli_runner, djb_config):
        """Set with unknown key shows error."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "set", "unknown_key", "value"])
        assert result.exit_code != 0
        assert "unknown_key" in result.output

    def test_delete_unknown_key_shows_error(self, cli_runner, djb_config):
        """Delete with unknown key shows error."""
        result = cli_runner.invoke(djb_cli, ["-q", "config", "delete", "unknown_key"])
        assert result.exit_code != 0
        assert "unknown_key" in result.output
