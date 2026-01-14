"""E2E tests for djb config CLI command.

These tests require real file I/O for testing config file operations.
Unit tests for output format are in ../test_config_cmd.py.
"""

from __future__ import annotations

import json

import pytest

from djb.cli.djb import djb_cli
from djb.config import DjbConfig, get_djb_config
from djb.config.validation import reset_warning_state


pytestmark = pytest.mark.e2e_marker


class TestConfigShow:
    """E2E tests for djb config --show with real project directories."""

    def test_show_outputs_valid_json(self, cli_runner, project_dir, make_config_file):
        """'show' subcommand outputs valid JSON with all config fields."""
        # Create a config with domain_names to test serialization
        make_config_file(
            {
                "heroku": {
                    "domain_names": {
                        "example.com": {"manager": "cloudflare"},
                        "app.herokuapp.com": {"manager": "platform"},
                    }
                },
                "k8s": {
                    "domain_names": {
                        "k8s.example.com": {"manager": "cloudflare"},
                    }
                },
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "show"]
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Should be valid JSON
        config_data = json.loads(result.output)
        # Should have expected top-level keys
        assert "project_dir" in config_data
        assert "mode" in config_data
        assert "heroku" in config_data
        assert "k8s" in config_data
        # domain_names should be serialized as dicts, not ConfigBase objects
        assert "domain_names" in config_data["heroku"]
        assert "example.com" in config_data["heroku"]["domain_names"]

    def test_with_provenance_shows_environment_source(self, cli_runner, project_dir, monkeypatch):
        """--with-provenance shows environment as source for env vars."""
        monkeypatch.setenv("DJB_PROJECT_NAME", "env-project")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "show", "--with-provenance"],
        )

        assert result.exit_code == 0
        # Provenance shows the ConfigIO name - "env" for environment variables
        assert "// project_name: env" in result.output


class TestConfigProjectName:
    """E2E tests for djb config project_name subcommand."""

    def test_show_current_value_from_pyproject(self, cli_runner, make_pyproject_dir_with_git):
        """Showing current project_name (falls back to pyproject.toml)."""
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(make_pyproject_dir_with_git), "-q", "config", "project_name"],
        )

        assert result.exit_code == 0
        # Should show the project name from pyproject.toml
        assert "project_name:" in result.output

    def test_set_valid_project_name(self, cli_runner, project_dir):
        """Setting a valid project name."""
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "my-app"],
        )

        assert result.exit_code == 0
        assert "project_name set to: my-app" in result.output

    def test_set_project_name_uppercase_normalized(self, cli_runner, project_dir):
        """Uppercase project names are normalized to lowercase."""
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "MyApp"],
        )

        assert result.exit_code == 0
        # Value is normalized to lowercase
        assert "project_name set to: myapp" in result.output

    def test_set_invalid_project_name_starts_with_hyphen(self, cli_runner, project_dir):
        """Project names starting with hyphen are rejected."""
        # Use -- to separate options from arguments (otherwise -myapp is parsed as -m option)
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--", "-myapp"],
        )

        assert result.exit_code != 0
        # Error includes validation hint about expected format
        assert "lowercase alphanumeric" in result.output

    def test_delete_project_name(self, cli_runner, project_dir):
        """Deleting the project_name setting."""
        # Clear pyproject.toml name so we can test config file operations
        (project_dir / "pyproject.toml").write_text("[project]\n")

        # First set a value (writes to djb.yaml config file)
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "my-app"],
        )
        assert result.exit_code == 0

        # Then delete it
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--delete"],
        )

        assert result.exit_code == 0
        assert "project_name removed" in result.output

    def test_delete_from_mode_section_even_when_value_from_environment(
        self, cli_runner, project_dir, monkeypatch
    ):
        """Delete removes from mode section even if value comes from environment."""
        monkeypatch.setenv("DJB_PROJECT_NAME", "env-project")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--delete"],
        )

        # Delete succeeds (removes from mode section, even if nothing was there)
        assert result.exit_code == 0
        assert "project_name removed" in result.output

    def test_delete_from_mode_section_even_when_value_from_directory_name(
        self, cli_runner, project_dir
    ):
        """Delete removes from mode section even if value derived from directory name."""
        # Clear pyproject.toml so it falls back to directory name
        (project_dir / "pyproject.toml").write_text("[project]\n")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "project_name", "--delete"],
        )

        # Delete succeeds (removes from mode section, even if nothing was there)
        assert result.exit_code == 0
        assert "project_name removed" in result.output


class TestConfigModeSpecificWriting:
    """E2E tests for writing config values to mode-specific sections.

    These tests verify that writes go to the correct mode section in .djb/project.toml.
    We create an empty project.toml first so that writes go there instead of pyproject.toml.
    """

    def test_set_with_mode_development_writes_to_development_section(
        self, cli_runner, project_dir, make_config_file
    ):
        """Setting a value with --mode development writes to [development] section."""
        # Create empty project.toml so writes go there (not to pyproject.toml)
        make_config_file({}, config_type="project")

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:dev_seed",
            ],
        )

        assert result.exit_code == 0
        assert (
            "seed_command set to: myapp.cli:dev_seed in project.toml in [development]"
            in result.output
        )

        # Verify the file contains the [development] section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[development]" in content
        assert 'seed_command = "myapp.cli:dev_seed"' in content

    def test_set_with_mode_staging_writes_to_staging_section(
        self, cli_runner, project_dir, make_config_file
    ):
        """Setting a value with --mode staging writes to [staging] section."""
        # Create empty project.toml so writes go there (not to pyproject.toml)
        make_config_file({}, config_type="project")

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "staging",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:staging_seed",
            ],
        )

        assert result.exit_code == 0
        assert (
            "seed_command set to: myapp.cli:staging_seed in project.toml in [staging]"
            in result.output
        )

        # Verify the file contains the [staging] section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[staging]" in content
        assert 'seed_command = "myapp.cli:staging_seed"' in content

    def test_set_with_mode_production_writes_to_root(
        self, cli_runner, project_dir, make_config_file
    ):
        """Setting a value with --mode production writes to root section."""
        # Create empty project.toml so writes go there (not to pyproject.toml)
        make_config_file({}, config_type="project")

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "production",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:seed",
            ],
        )

        assert result.exit_code == 0
        # Production writes to root, no section indicator in output
        assert "seed_command set to: myapp.cli:seed" in result.output
        assert "[production]" not in result.output

        # Verify seed_command is at root level, not in a section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        # Hostname should appear at root (before any section headers)
        lines = content.split("\n")
        seed_command_line = next((i for i, line in enumerate(lines) if "seed_command" in line), -1)
        section_line = next((i for i, line in enumerate(lines) if line.startswith("[")), len(lines))
        assert (
            seed_command_line < section_line
        ), "seed_command should be in root section (before any [section])"

    def test_set_without_mode_uses_default_development_mode(
        self, cli_runner, project_dir, make_config_file
    ):
        """Setting a value without --mode uses the default mode (development)."""
        # Create empty project.toml so writes go there (not to pyproject.toml)
        make_config_file({}, config_type="project")

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-q",
                "config",
                "seed_command",
                "myapp.cli:seed",
            ],
        )

        assert result.exit_code == 0
        assert (
            "seed_command set to: myapp.cli:seed in project.toml in [development]" in result.output
        )

        # Verify the file contains the [development] section
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[development]" in content

    def test_delete_with_mode_removes_from_mode_section(
        self, cli_runner, project_dir, make_config_file
    ):
        """Deleting with --mode removes value from that mode's section."""
        # Create empty project.toml so writes go there (not to pyproject.toml)
        make_config_file({}, config_type="project")

        # First set a value in development section
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:dev_seed",
            ],
        )
        assert result.exit_code == 0

        # Now delete it from development section
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "--delete",
            ],
        )

        assert result.exit_code == 0
        assert "seed_command removed from project.toml in [development]" in result.output

        # Verify seed_command is gone from the file
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "seed_command" not in content

    def test_mode_sections_are_preserved_when_adding_new_values(
        self, cli_runner, project_dir, make_config_file
    ):
        """Adding values to different mode sections preserves existing sections."""
        # Create empty project.toml so writes go there (not to pyproject.toml)
        make_config_file({}, config_type="project")

        # Set development seed_command
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "development",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:dev_seed",
            ],
        )
        assert result.exit_code == 0

        # Set staging seed_command
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "staging",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:staging_seed",
            ],
        )
        assert result.exit_code == 0

        # Set production (root) seed_command
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "--mode",
                "production",
                "-q",
                "config",
                "seed_command",
                "myapp.cli:seed",
            ],
        )
        assert result.exit_code == 0

        # Verify all three are in the file
        config_file = project_dir / ".djb" / "project.toml"
        content = config_file.read_text()
        assert "[development]" in content
        assert "[staging]" in content
        assert content.count("seed_command") == 3  # One for each mode


class TestConfigGenericCommands:
    """E2E tests for generic get/set/delete subcommands."""

    def test_get_shows_current_value(self, cli_runner, project_dir, make_config_file):
        """Get shows current value for a key."""
        make_config_file({"seed_command": "myapp:seed"}, config_type="project")
        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "get", "seed_command"]
        )
        assert result.exit_code == 0
        assert "seed_command:" in result.output
        assert "myapp:seed" in result.output

    def test_set_writes_value(self, cli_runner, project_dir, make_config_file):
        """Set writes value to config file."""
        make_config_file({}, config_type="project")
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-q",
                "config",
                "set",
                "seed_command",
                "myapp:seed",
            ],
        )
        assert result.exit_code == 0
        assert "seed_command set to:" in result.output

        # Verify the value was actually persisted
        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "get", "seed_command"]
        )
        assert result.exit_code == 0
        assert "myapp:seed" in result.output

    def test_set_invalid_value_shows_error(self, cli_runner, project_dir, make_config_file):
        """Set with invalid value shows validation error."""
        make_config_file({}, config_type="project")
        # Use -- to separate options from arguments (otherwise -invalid is parsed as option)
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-q",
                "config",
                "set",
                "--",
                "project_name",
                "-invalid",
            ],
        )
        assert result.exit_code != 0
        assert "lowercase alphanumeric" in result.output  # Validation message

    def test_delete_removes_value(self, cli_runner, project_dir, make_config_file):
        """Delete removes value from config file."""
        make_config_file({"seed_command": "myapp:seed"}, config_type="project")
        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "delete", "seed_command"]
        )
        assert result.exit_code == 0
        assert "seed_command removed" in result.output

        # Verify the value was actually removed
        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "get", "seed_command"]
        )
        assert result.exit_code == 0
        assert "(not set)" in result.output

    def test_get_nested_key(self, cli_runner, project_dir, make_config_file):
        """Get works with nested keys like hetzner.server_name."""
        make_config_file({"hetzner": {"server_name": "my-server"}}, config_type="project")
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "get", "hetzner.server_name"],
        )
        assert result.exit_code == 0
        assert "hetzner.server_name:" in result.output
        assert "my-server" in result.output

    def test_set_nested_key(self, cli_runner, project_dir, make_config_file):
        """Set works with nested keys like letsencrypt.email."""
        make_config_file({}, config_type="project")
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-q",
                "config",
                "set",
                "letsencrypt.email",
                "certs@example.com",
            ],
        )
        assert result.exit_code == 0
        assert "letsencrypt.email set to:" in result.output

        # Verify the value was actually persisted
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "get", "letsencrypt.email"],
        )
        assert result.exit_code == 0
        assert "certs@example.com" in result.output


class TestConfigValidationWarnings:
    """E2E tests for unrecognized config key warnings.

    These tests verify warning deduplication - warnings for unrecognized config
    keys are only emitted once per project directory per process, preventing
    duplicate warnings when Django's runserver reloads config.
    """

    @pytest.fixture(autouse=True)
    def clear_warned_dirs(self):
        """Clear the set of warned project directories before each test.

        The config system tracks which project directories have already been
        warned about unrecognized keys (stored in _warned_project_dirs). This
        prevents duplicate warnings but means tests need a fresh slate.
        """
        reset_warning_state()

    def test_warning_only_emitted_once_per_process(self, project_dir, make_config_file, capsys):
        """Warnings for unrecognized keys are emitted only once per process.

        This prevents duplicate warnings when Django's runserver reloads config.
        """
        # Create a config file with an unrecognized key
        make_config_file({"unrecognized_key": "some_value"}, config_type="project")

        # Load config multiple times (simulating Django runserver reloads)
        # Each call creates a fresh config instance
        get_djb_config(DjbConfig(project_dir=project_dir))
        get_djb_config(DjbConfig(project_dir=project_dir))
        get_djb_config(DjbConfig(project_dir=project_dir))

        # Check stdout for warnings (DjbLogger writes to stdout)
        captured = capsys.readouterr()
        stdout = captured.out

        # Warning should appear exactly once (deduplicated by _warned_keys)
        assert stdout.count("Unrecognized config keys") == 1, f"Expected 1 header, got: {stdout}"
        assert stdout.count("unrecognized_key") == 1, f"Expected 1 key mention, got: {stdout}"

    def test_warning_format(self, project_dir, make_config_file, capsys):
        """Warning format shows file and key name."""
        # Create config files with unrecognized keys
        make_config_file({"bad_key": "value"}, config_type="project")
        make_config_file({"another_bad": "value"}, config_type="local")

        # Load config - warnings emitted during load
        get_djb_config(DjbConfig(project_dir=project_dir))

        # Check stdout for warning format (DjbLogger writes to stdout)
        captured = capsys.readouterr()
        stdout = captured.out

        assert "Unrecognized config keys" in stdout, f"Expected header warning: {stdout}"
        assert "project.toml: bad_key" in stdout, f"Expected project.toml warning: {stdout}"
        assert "local.toml: another_bad" in stdout, f"Expected local.toml warning: {stdout}"


class TestConfigLint:
    """E2E tests for djb config lint command."""

    def test_lint_shows_unsorted_file(self, cli_runner, project_dir, make_config_file):
        """Lint reports when keys are not sorted alphabetically."""
        make_config_file('zebra = "z"\napple = "a"\n', config_type="project")

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint"]
        )

        assert result.exit_code == 0
        assert "project.toml: keys not sorted" in result.output

    def test_lint_fix_sorts_keys(self, cli_runner, project_dir, make_config_file):
        """Lint --fix sorts keys alphabetically."""
        config_path = make_config_file('zebra = "z"\napple = "a"\n', config_type="project")

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint", "--fix"]
        )

        assert result.exit_code == 0
        assert "project.toml: sorted keys alphabetically" in result.output

        # Verify keys are now sorted
        content = config_path.read_text()
        lines = [line for line in content.strip().split("\n") if line]
        assert lines[0].startswith("apple"), f"Expected 'apple' first, got: {lines}"
        assert lines[1].startswith("zebra"), f"Expected 'zebra' second, got: {lines}"

    def test_lint_check_exits_1_when_unsorted(self, cli_runner, project_dir, make_config_file):
        """Lint --check exits with code 1 when keys are unsorted."""
        make_config_file('zebra = "z"\napple = "a"\n', config_type="project")

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint", "--check"]
        )

        assert result.exit_code == 1

    def test_lint_check_exits_0_when_sorted(self, cli_runner, project_dir, make_config_file):
        """Lint --check exits with code 0 when keys are already sorted."""
        make_config_file('apple = "a"\nzebra = "z"\n', config_type="project")

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint", "--check"]
        )

        assert result.exit_code == 0

    def test_lint_preserves_comments(self, cli_runner, project_dir, make_config_file):
        """Lint --fix preserves comments attached to keys."""
        config_path = make_config_file(
            '# Comment for zebra\nzebra = "z"\n# Comment for apple\napple = "a"\n',
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint", "--fix"]
        )

        assert result.exit_code == 0

        # Verify comments are preserved
        sorted_content = config_path.read_text()
        assert "# Comment for apple" in sorted_content
        assert "# Comment for zebra" in sorted_content

    def test_lint_project_flag_only_checks_project_toml(
        self, cli_runner, project_dir, make_config_file
    ):
        """--project flag limits lint to project.toml only."""
        make_config_file('apple = "a"\nzebra = "z"\n', config_type="project")
        make_config_file('zebra = "z"\napple = "a"\n', config_type="local")  # Unsorted

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "--project", "lint", "--check"],
        )

        # Should pass because project.toml is sorted, ignoring local.toml
        assert result.exit_code == 0

    def test_lint_local_flag_only_checks_local_toml(
        self, cli_runner, project_dir, make_config_file
    ):
        """--local flag limits lint to local.toml only."""
        make_config_file('zebra = "z"\napple = "a"\n', config_type="project")  # Unsorted
        make_config_file('apple = "a"\nzebra = "z"\n', config_type="local")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "-q", "config", "--local", "lint", "--check"],
        )

        # Should pass because local.toml is sorted, ignoring project.toml
        assert result.exit_code == 0

    def test_lint_mode_sections_sorted_after_regular_keys(
        self, cli_runner, project_dir, make_config_file
    ):
        """Mode sections (development, staging) come after regular root keys.

        In TOML, root keys must appear before any [table] sections.
        The mode_sections_last option ensures mode sections sort after
        regular keys, and are sorted alphabetically among themselves.
        """
        # Valid TOML: root keys first, then tables
        # Mode sections should stay at the end, sorted alphabetically
        content = """\
zebra = "z"
apple = "a"

[staging]
seed_command = "staging:seed"

[development]
seed_command = "dev:seed"
"""
        config_path = make_config_file(content, config_type="project")

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint", "--fix"]
        )

        assert result.exit_code == 0, result.output

        # Verify structure after sorting
        sorted_content = config_path.read_text()
        apple_pos = sorted_content.find("apple")
        zebra_pos = sorted_content.find("zebra")
        development_pos = sorted_content.find("[development]")
        staging_pos = sorted_content.find("[staging]")

        # Root keys sorted alphabetically
        assert apple_pos < zebra_pos, f"apple should come before zebra\n{sorted_content}"
        # Root keys before mode sections
        assert (
            zebra_pos < development_pos
        ), f"zebra should come before [development]\n{sorted_content}"
        # Mode sections sorted alphabetically: development < staging
        assert (
            development_pos < staging_pos
        ), f"[development] should come before [staging]\n{sorted_content}"

    def test_lint_both_files_when_no_flag(self, cli_runner, project_dir, make_config_file):
        """Without --local or --project, lint checks both files."""
        make_config_file('zebra = "z"\napple = "a"\n', config_type="project")
        make_config_file('zulu = "z"\nalpha = "a"\n', config_type="local")

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint"]
        )

        assert result.exit_code == 0
        assert "project.toml: keys not sorted" in result.output
        assert "local.toml: keys not sorted" in result.output

    def test_lint_already_sorted_shows_message(self, cli_runner, project_dir, make_config_file):
        """When files are already sorted, show success message."""
        make_config_file('apple = "a"\nzebra = "z"\n', config_type="project")

        result = cli_runner.invoke(
            djb_cli, ["--project-dir", str(project_dir), "-q", "config", "lint"]
        )

        assert result.exit_code == 0
        assert "project.toml: already sorted" in result.output
