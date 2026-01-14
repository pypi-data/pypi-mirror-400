"""Tests for djb editable module.

Unit tests use mocking fixtures from conftest.py to avoid real file I/O.
All tests should use mock_fs for file operation mocking.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest
from tomlkit.exceptions import ParseError

from djb.cli.djb import djb_cli
from djb.config.storage.utils import dump_toml
from djb.cli.editable import (
    DJB_REPO,
    PRE_COMMIT_HOOK_CONTENT,
    _get_djb_source_config,
    _get_workspace_members,
    install_pre_commit_hook,
    _remove_djb_source_entry,
    _remove_djb_workspace_member,
    clone_djb_repo,
    find_djb_dir,
    get_djb_source_path,
    get_djb_version_specifier,
    get_installed_djb_version,
    install_editable_djb,
    is_djb_editable,
    is_djb_package_dir,
    show_status,
    uninstall_editable_djb,
)
from djb.cli.tests import FAKE_PROJECT_DIR
from djb.testing import MockFilesystem

# Common mock return value for version display
MOCK_VERSION_OUTPUT = "Name: djb\nVersion: 0.2.5\nLocation: /path/to/site-packages"


def add_pyproject(
    mock_fs: MockFilesystem, parsed: dict | None, path: Path = FAKE_PROJECT_DIR
) -> None:
    """Add a pyproject.toml file to mock_fs from a parsed dict.

    If parsed is None, does nothing (simulating missing pyproject.toml).
    """
    if parsed is not None:
        mock_fs.add_file(path / "pyproject.toml", dump_toml(parsed))


def make_editable_pyproject_dict(djb_path: str = "djb") -> dict[str, Any]:
    """Create parsed pyproject.toml dict with djb in editable mode."""
    return {
        "project": {"name": "myproject"},
        "tool": {
            "uv": {
                "workspace": {"members": [djb_path]},
                "sources": {"djb": {"workspace": True, "editable": True}},
            }
        },
    }


class TestGetDjbVersionSpecifier:
    """Tests for get_djb_version_specifier function."""

    def test_returns_version_specifier(self, mock_fs):
        """get_djb_version_specifier returns version specifier when present."""
        parsed = {
            "project": {
                "name": "myproject",
                "dependencies": ["django>=6.0.0", "djb>=0.2.6"],
            }
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result == ">=0.2.6"

    def test_returns_none_when_no_djb(self, mock_fs):
        """get_djb_version_specifier returns None when djb not in dependencies."""
        parsed = {
            "project": {
                "name": "myproject",
                "dependencies": ["django>=6.0.0"],
            }
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result is None

    def test_returns_none_when_pyproject_missing(self, mock_fs):
        """Returns None when pyproject.toml is missing for version specifier lookup."""
        # Don't add pyproject.toml to mock_fs
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result is None

    @pytest.mark.parametrize(
        "dep_string,expected",
        [
            # Various version specifiers
            ("djb>=0.2.6", ">=0.2.6"),
            ("djb==0.2.6", "==0.2.6"),
            ("djb~=0.2.6", "~=0.2.6"),
            ("djb<1.0", "<1.0"),
            ("djb<=0.2.6", "<=0.2.6"),
            ("djb>0.2.5", ">0.2.5"),
            ("djb!=0.2.3", "!=0.2.3"),
            # Compound version specifiers (packaging sorts specifiers alphabetically by operator)
            ("djb>=0.2.6,<1.0", "<1.0,>=0.2.6"),
            # Extras syntax (specifier should still be extracted)
            ("djb[dev]>=0.2.6", ">=0.2.6"),
            ("djb[dev,test]>=0.2.6,<1.0", "<1.0,>=0.2.6"),
            # Dependency without version constraint
            ("djb", None),
            # No specifier with extras
            ("djb[dev]", None),
        ],
    )
    def test_parses_pep508_specifiers(self, mock_fs, dep_string, expected):
        """get_djb_version_specifier parses PEP 508 specifiers and returns normalized constraint."""
        parsed = {
            "project": {
                "name": "myproject",
                "dependencies": [dep_string],
            }
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result == expected

    def test_does_not_match_prefix_package(self, mock_fs):
        """get_djb_version_specifier does not match djb-extras package."""
        parsed = {
            "project": {
                "name": "myproject",
                "dependencies": ["djb-extras>=0.2.6"],
            }
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result is None

    def test_finds_djb_in_optional_dependencies(self, mock_fs):
        """get_djb_version_specifier finds djb in optional dependencies."""
        parsed = {
            "project": {
                "name": "myproject",
                "dependencies": [],
                "optional-dependencies": {"dev": ["djb>=0.2.6"]},
            }
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result == ">=0.2.6"

    def test_extracts_specifier_ignoring_markers(self, mock_fs):
        """get_djb_version_specifier extracts specifier ignoring PEP 508 markers."""
        parsed = {
            "project": {
                "name": "myproject",
                "dependencies": ['djb>=0.2.6; python_version >= "3.10"'],
            }
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result == ">=0.2.6"

    def test_extracts_specifier_with_extras_and_markers(self, mock_fs):
        """get_djb_version_specifier extracts specifier from deps with extras and markers."""
        parsed = {
            "project": {
                "name": "myproject",
                "dependencies": ['djb[dev]>=0.2.6; sys_platform == "linux"'],
            }
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_version_specifier(FAKE_PROJECT_DIR)
        assert result == ">=0.2.6"

    def test_raises_for_invalid_toml(self, mock_fs):
        """get_djb_version_specifier raises TOMLDecodeError on malformed pyproject.toml."""
        # Provide invalid TOML content
        mock_fs.add_file(FAKE_PROJECT_DIR / "pyproject.toml", "invalid toml [[[")
        with pytest.raises(ParseError):
            with mock_fs.apply():
                get_djb_version_specifier(FAKE_PROJECT_DIR)


class TestFindDjbDir:
    """Tests for find_djb_dir function."""

    def test_finds_djb_in_subdirectory(self, mock_fs):
        """find_djb_dir finds djb/ subdirectory with pyproject.toml."""
        # Mock that djb/pyproject.toml exists
        mock_fs.add_file(FAKE_PROJECT_DIR / "djb" / "pyproject.toml", "")
        with mock_fs.apply():
            result = find_djb_dir(FAKE_PROJECT_DIR)
        assert result == FAKE_PROJECT_DIR / "djb"

    def test_finds_djb_when_inside_djb_directory(self, mock_fs):
        """find_djb_dir finds djb when cwd is inside djb directory."""
        # djb/ doesn't exist, but we're in a djb package directory
        parsed = {"project": {"name": "djb", "version": "0.1.0"}}
        # Don't add djb/pyproject.toml (simulating it doesn't exist)
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = find_djb_dir(FAKE_PROJECT_DIR)
        assert result == FAKE_PROJECT_DIR

    def test_returns_none_when_not_found(self, mock_fs):
        """find_djb_dir returns None when djb directory not found."""
        # No djb/pyproject.toml and no pyproject.toml
        with mock_fs.apply():
            result = find_djb_dir(FAKE_PROJECT_DIR)
        assert result is None

    def test_returns_none_for_non_djb_pyproject(self, mock_fs):
        """find_djb_dir returns None when pyproject.toml exists but is not djb."""
        # djb/ doesn't exist, and current dir pyproject.toml is not djb
        parsed = {"project": {"name": "other-project"}}
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = find_djb_dir(FAKE_PROJECT_DIR)
        assert result is None

    def test_uses_cwd_when_repo_root_is_none(self, mock_fs):
        """find_djb_dir uses current working directory when repo_root is None."""
        mock_fs.add_file(FAKE_PROJECT_DIR / "djb" / "pyproject.toml", "")
        mock_fs.cwd = FAKE_PROJECT_DIR
        with mock_fs.apply():
            result = find_djb_dir(None)
        assert result == FAKE_PROJECT_DIR / "djb"


class TestIsDjbEditable:
    """Tests for is_djb_editable function."""

    def test_returns_true_when_editable(self, mock_fs):
        """is_djb_editable returns True when djb is in uv.sources."""
        parsed = make_editable_pyproject_dict()
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = is_djb_editable(FAKE_PROJECT_DIR)
        assert result is True

    def test_returns_false_when_not_editable(self, mock_fs):
        """is_djb_editable returns False when djb is not in uv.sources."""
        parsed = {"project": {"name": "myproject", "dependencies": {"djb": "^0.1.0"}}}
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = is_djb_editable(FAKE_PROJECT_DIR)
        assert result is False

    def test_returns_false_when_pyproject_missing(self, mock_fs):
        """is_djb_editable returns False when pyproject.toml is missing."""
        # Don't add pyproject.toml
        with mock_fs.apply():
            result = is_djb_editable(FAKE_PROJECT_DIR)
        assert result is False

    def test_returns_false_when_sources_exists_but_no_djb(self, mock_fs):
        """is_djb_editable returns False when uv.sources exists but djb not in it."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"sources": {"other-package": {"path": "../other"}}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = is_djb_editable(FAKE_PROJECT_DIR)
        assert result is False


class TestUninstallEditableDjb:
    """Tests for uninstall_editable_djb function."""

    def test_successful_uninstall(self, mock_cmd_runner):
        """uninstall_editable_djb successfully uninstalls and reinstalls from PyPI."""
        # Mock returns version info for the uv pip show call
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")

        result = uninstall_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is True
        # Calls: uv remove djb, uv add djb, uv pip show djb (for version display)
        assert mock_cmd_runner.run.call_count == 3

        # First call: uv remove djb
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert first_call[0][0] == ["uv", "remove", "djb"]

        # Second call: uv add --refresh djb
        second_call = mock_cmd_runner.run.call_args_list[1]
        assert second_call[0][0] == ["uv", "add", "--refresh", "djb"]

    def test_failure_on_remove(self, mock_cmd_runner):
        """uninstall_editable_djb returns False when uv remove command fails."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="error")

        result = uninstall_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is False
        assert mock_cmd_runner.run.call_count == 1

    def test_failure_on_add(self, mock_cmd_runner):
        """uninstall_editable_djb returns False when uv add fails after successful remove."""

        def side_effect(cmd, *args, **kwargs):
            if cmd == ["uv", "remove", "djb"]:
                return Mock(returncode=0)
            return Mock(returncode=1, stderr="error")

        mock_cmd_runner.run.side_effect = side_effect

        result = uninstall_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is False
        assert mock_cmd_runner.run.call_count == 2

    def test_quiet_mode_suppresses_output(self, mock_cmd_runner, capsys):
        """uninstall_editable_djb with quiet=True suppresses click.echo output."""
        uninstall_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True)

        captured = capsys.readouterr()
        assert "Removing" not in captured.out
        assert "Re-adding" not in captured.out


class TestCloneDjbRepo:
    """Tests for clone_djb_repo function."""

    def test_successful_clone(self, mock_cmd_runner):
        """clone_djb_repo successfully clones the repository."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")
        target_dir = FAKE_PROJECT_DIR / "djb"

        result = clone_djb_repo(mock_cmd_runner, target_dir)

        assert result is True
        mock_cmd_runner.run.assert_called_once()
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert call_args == ["git", "clone", DJB_REPO, str(target_dir)]

    def test_clone_with_custom_repo(self, mock_cmd_runner):
        """clone_djb_repo clones from custom repository URL when provided."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")
        target_dir = FAKE_PROJECT_DIR / "djb"
        custom_repo = "git@github.com:other/djb.git"

        result = clone_djb_repo(mock_cmd_runner, target_dir, djb_repo=custom_repo)

        assert result is True
        call_args = mock_cmd_runner.run.call_args[0][0]
        assert call_args == ["git", "clone", custom_repo, str(target_dir)]

    def test_clone_failure(self, mock_cmd_runner):
        """clone_djb_repo returns False when git clone fails."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="fatal: repository not found")
        target_dir = FAKE_PROJECT_DIR / "djb"

        result = clone_djb_repo(mock_cmd_runner, target_dir)

        assert result is False

    def test_quiet_mode(self, mock_cmd_runner, capsys):
        """clone_djb_repo with quiet=True suppresses output."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")
        target_dir = FAKE_PROJECT_DIR / "djb"

        clone_djb_repo(mock_cmd_runner, target_dir, quiet=True)

        captured = capsys.readouterr()
        assert "Cloning" not in captured.out


class TestInstallEditableDjb:
    """Tests for install_editable_djb function."""

    def test_successful_install(self, mock_cmd_runner, mock_fs):
        """install_editable_djb successfully installs djb in editable mode."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")
        djb_dir = FAKE_PROJECT_DIR / "djb"

        # Mock find_djb_dir to return the djb path (simulating project_with_djb fixture)
        mock_fs.add_file(FAKE_PROJECT_DIR / "djb" / "pyproject.toml", "")
        with (
            mock_fs.apply(),
            patch("djb.cli.editable.find_djb_dir", return_value=djb_dir),
        ):
            result = install_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is True
        # Calls: uv add --editable, uv pip show djb (for version display)
        assert mock_cmd_runner.run.call_count == 2
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert first_call[0][0] == ["uv", "add", "--editable", str(djb_dir)]

    def test_clones_when_djb_not_found(self, mock_cmd_runner, mock_fs):
        """install_editable_djb clones djb repo when directory not found."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")

        # Don't add djb/pyproject.toml to simulate it doesn't exist
        with mock_fs.apply():
            result = install_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is True
        # Calls: git clone, uv add --editable, uv pip show djb
        assert mock_cmd_runner.run.call_count == 3
        # First call should be git clone
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert first_call[0][0][0:2] == ["git", "clone"]
        assert DJB_REPO in first_call[0][0]

    def test_clone_failure_returns_false(self, mock_cmd_runner, mock_fs):
        """install_editable_djb returns False when git clone subprocess fails during editable install."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="clone failed")

        # Don't add djb/pyproject.toml to simulate it doesn't exist
        with mock_fs.apply():
            result = install_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is False
        # Only git clone should have been called
        assert mock_cmd_runner.run.call_count == 1

    def test_custom_repo_and_dir(self, mock_cmd_runner, mock_fs):
        """install_editable_djb uses custom repo URL and target directory."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")
        custom_repo = "git@github.com:custom/djb.git"
        custom_dir = "packages/djb"

        # Don't add packages/djb/pyproject.toml to simulate it doesn't exist
        with mock_fs.apply():
            result = install_editable_djb(
                mock_cmd_runner, FAKE_PROJECT_DIR, djb_repo=custom_repo, djb_dir=custom_dir
            )

        assert result is True
        # First call should be git clone with custom repo and dir
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert first_call[0][0] == ["git", "clone", custom_repo, str(FAKE_PROJECT_DIR / custom_dir)]

    def test_failure_on_uv_add(self, mock_cmd_runner, mock_fs):
        """install_editable_djb returns False when uv add --editable fails."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="error")
        djb_dir = FAKE_PROJECT_DIR / "djb"

        mock_fs.add_file(FAKE_PROJECT_DIR / "djb" / "pyproject.toml", "")
        with (
            mock_fs.apply(),
            patch("djb.cli.editable.find_djb_dir", return_value=djb_dir),
        ):
            result = install_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is False

    def test_quiet_mode_suppresses_output(self, mock_cmd_runner, mock_fs, capsys):
        """install_editable_djb with quiet=True suppresses click.echo output."""
        djb_dir = FAKE_PROJECT_DIR / "djb"

        mock_fs.add_file(FAKE_PROJECT_DIR / "djb" / "pyproject.toml", "")
        with (
            mock_fs.apply(),
            patch("djb.cli.editable.find_djb_dir", return_value=djb_dir),
        ):
            install_editable_djb(mock_cmd_runner, FAKE_PROJECT_DIR, quiet=True)

        captured = capsys.readouterr()
        assert "Installing" not in captured.out


class TestEditableDjbCommand:
    """Tests for editable CLI command."""

    def test_help(self, cli_runner):
        """editable --help shows usage information."""
        result = cli_runner.invoke(djb_cli, ["editable", "--help"])
        assert result.exit_code == 0
        assert "Install or uninstall djb in editable mode" in result.output
        assert "uninstall" in result.output  # Now a subcommand
        assert "status" in result.output  # Also a subcommand
        assert "--djb-repo" in result.output
        assert "--djb-dir" in result.output

    def test_install_success(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable command successfully installs djb in editable mode."""
        djb_dir = FAKE_PROJECT_DIR / "djb"
        mock_fs.add_file(FAKE_PROJECT_DIR / "djb" / "pyproject.toml", "")
        mock_fs.cwd = FAKE_PROJECT_DIR
        with (
            mock_fs.apply(),
            patch("djb.cli.editable.find_djb_dir", return_value=djb_dir),
        ):
            result = cli_runner.invoke(djb_cli, ["editable"])

        assert result.exit_code == 0
        assert "editable mode" in result.output

    def test_install_clones_when_not_found(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable command clones djb repo when directory not found."""
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")
        mock_fs.cwd = FAKE_PROJECT_DIR
        # Don't add djb/pyproject.toml to simulate it doesn't exist
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable"])

        assert result.exit_code == 0
        # Check that git clone was called
        calls = [call.args[0] for call in mock_cmd_runner.run.call_args_list]
        assert any(cmd[0:2] == ["git", "clone"] for cmd in calls)

    def test_install_failure_on_clone(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable command fails when clone fails."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="clone failed")
        mock_fs.cwd = FAKE_PROJECT_DIR
        # Don't add djb/pyproject.toml to simulate it doesn't exist
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable"])

        assert result.exit_code == 1
        assert "Failed to install" in result.output

    def test_custom_repo_option(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable --djb-repo option uses custom repository URL."""
        custom_repo = "git@github.com:custom/djb.git"
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")
        mock_fs.cwd = FAKE_PROJECT_DIR
        # Don't add djb/pyproject.toml to simulate it doesn't exist
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable", "--djb-repo", custom_repo])

        assert result.exit_code == 0
        # Check that git clone was called with custom repo
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert custom_repo in first_call.args[0]

    def test_custom_dir_option(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable --djb-dir option uses custom target directory."""
        custom_dir = "packages/djb"
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")
        mock_fs.cwd = FAKE_PROJECT_DIR
        # Don't add packages/djb/pyproject.toml to simulate it doesn't exist
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable", "--djb-dir", custom_dir])

        assert result.exit_code == 0
        # Check that git clone was called with custom dir
        first_call = mock_cmd_runner.run.call_args_list[0]
        assert str(FAKE_PROJECT_DIR / custom_dir) in first_call.args[0]

    def test_uninstall_success(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable --uninstall successfully reverts to PyPI version."""
        parsed = make_editable_pyproject_dict()
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout="Version: 0.2.5", stderr="")
        add_pyproject(mock_fs, parsed)
        mock_fs.cwd = FAKE_PROJECT_DIR
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable", "uninstall"])

        assert result.exit_code == 0
        assert "PyPI" in result.output

    def test_uninstall_failure(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable --uninstall fails when uv commands fail."""
        parsed = make_editable_pyproject_dict()
        mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="error")
        add_pyproject(mock_fs, parsed)
        mock_fs.cwd = FAKE_PROJECT_DIR
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable", "uninstall"])

        assert result.exit_code == 1
        assert "Failed to uninstall" in result.output or "Failed to remove" in result.output


class TestGetDjbSourcePath:
    """Tests for get_djb_source_path function."""

    def test_returns_path_when_editable(self, mock_fs):
        """get_djb_source_path returns path when djb is in editable mode."""
        host_parsed = make_editable_pyproject_dict()
        djb_parsed = {"project": {"name": "djb"}}
        add_pyproject(mock_fs, host_parsed)
        mock_fs.add_file(FAKE_PROJECT_DIR / "djb" / "pyproject.toml", dump_toml(djb_parsed))
        with mock_fs.apply():
            result = get_djb_source_path(FAKE_PROJECT_DIR)
        assert result == "djb"

    def test_returns_none_when_not_editable(self, mock_fs):
        """get_djb_source_path returns None when djb is not in editable mode."""
        parsed = {"project": {"name": "myproject"}}
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = get_djb_source_path(FAKE_PROJECT_DIR)
        assert result is None

    def test_returns_none_when_pyproject_missing(self, mock_fs):
        """get_djb_source_path returns None when pyproject.toml is missing."""
        # Don't add pyproject.toml
        with mock_fs.apply():
            result = get_djb_source_path(FAKE_PROJECT_DIR)
        assert result is None


class TestGetInstalledDjbVersion:
    """Tests for get_installed_djb_version function."""

    def test_returns_version_when_installed(self, mock_cmd_runner):
        """get_installed_djb_version returns version when djb is installed."""
        mock_cmd_runner.run.return_value = Mock(
            returncode=0,
            stdout="Name: djb\nVersion: 0.2.5\nLocation: /path/to/site-packages",
        )
        result = get_installed_djb_version(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result == "0.2.5"

    def test_returns_none_when_not_installed(self, mock_cmd_runner):
        """get_installed_djb_version returns None when djb is not installed."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="not found")
        result = get_installed_djb_version(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is None


class TestShowStatus:
    """Tests for show_status function."""

    def test_shows_editable_status(self, mock_fs, capsys, mock_cmd_runner):
        """show_status displays editable mode status."""
        parsed = make_editable_pyproject_dict()
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout=MOCK_VERSION_OUTPUT)
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            show_status(mock_cmd_runner, FAKE_PROJECT_DIR)

        captured = capsys.readouterr()
        assert "0.2.5" in captured.out
        assert "editable" in captured.out.lower()

    def test_shows_pypi_status(self, mock_fs, capsys, mock_cmd_runner):
        """show_status displays PyPI mode status."""
        parsed = {"project": {"name": "myproject"}}
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout=MOCK_VERSION_OUTPUT)
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            show_status(mock_cmd_runner, FAKE_PROJECT_DIR)

        captured = capsys.readouterr()
        assert "0.2.5" in captured.out
        assert "PyPI" in captured.out

    def test_shows_not_installed(self, mock_fs, capsys, mock_cmd_runner):
        """show_status displays not installed when djb is missing."""
        mock_cmd_runner.run.return_value = Mock(returncode=1, stdout="", stderr="")
        # Don't add pyproject.toml
        with mock_fs.apply():
            show_status(mock_cmd_runner, FAKE_PROJECT_DIR)

        captured = capsys.readouterr()
        assert "Not installed" in captured.out


class TestEditableDjbStatusCommand:
    """Tests for editable status CLI subcommand."""

    def test_status_subcommand(self, cli_runner, djb_config, mock_fs, mock_cmd_runner):
        """editable status shows current installation status."""
        parsed = make_editable_pyproject_dict()
        mock_cmd_runner.run.return_value = Mock(returncode=0, stdout=MOCK_VERSION_OUTPUT)
        add_pyproject(mock_fs, parsed)
        mock_fs.cwd = FAKE_PROJECT_DIR
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable", "status"])

        assert result.exit_code == 0
        assert "status" in result.output.lower() or "editable" in result.output.lower()

    def test_already_editable_message(self, cli_runner, djb_config, mock_fs):
        """editable shows message when already in editable mode."""
        parsed = make_editable_pyproject_dict()
        add_pyproject(mock_fs, parsed)
        mock_fs.cwd = FAKE_PROJECT_DIR
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable"])

        assert result.exit_code == 0
        assert "already" in result.output.lower()

    def test_not_editable_uninstall_message(self, cli_runner, djb_config, mock_fs):
        """editable --uninstall shows message when not in editable mode."""
        parsed = {"project": {"name": "myproject"}}
        add_pyproject(mock_fs, parsed)
        mock_fs.cwd = FAKE_PROJECT_DIR
        with mock_fs.apply():
            result = cli_runner.invoke(djb_cli, ["editable", "uninstall"])

        assert result.exit_code == 0
        assert "not" in result.output.lower()


class TestGetDjbSourceConfig:
    """Tests for _get_djb_source_config function."""

    def test_returns_config_when_present(self, mock_fs: MockFilesystem):
        """_get_djb_source_config returns djb config dict when [tool.uv.sources.djb] is present."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"sources": {"djb": {"workspace": True, "editable": True}}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_djb_source_config(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == {"workspace": True, "editable": True}

    def test_returns_none_when_no_djb_source(self, mock_fs: MockFilesystem):
        """_get_djb_source_config returns None when [tool.uv.sources] has no djb entry."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"sources": {"other-package": {"path": "../other"}}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_djb_source_config(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result is None

    @pytest.mark.parametrize(
        "parsed,missing_section",
        [
            (
                {
                    "project": {"name": "myproject"},
                    "tool": {"uv": {"dev-dependencies": ["pytest"]}},
                },
                "sources",
            ),
            (
                {"project": {"name": "myproject"}, "tool": {"pytest": {"testpaths": ["tests"]}}},
                "uv",
            ),
            (
                {"project": {"name": "myproject"}},
                "tool",
            ),
        ],
        ids=["no_sources", "no_uv", "no_tool"],
    )
    def test_returns_none_when_section_missing(
        self, mock_fs: MockFilesystem, parsed, missing_section
    ):
        """_get_djb_source_config returns None when required section is missing."""
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_djb_source_config(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result is None

    def test_returns_none_for_missing_file(self, mock_fs: MockFilesystem):
        """_get_djb_source_config returns None when pyproject.toml file is missing."""
        # Don't add the file - it won't exist
        with mock_fs.apply():
            result = _get_djb_source_config(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result is None

    def test_raises_for_invalid_toml(self, mock_fs: MockFilesystem):
        """_get_djb_source_config raises TOMLDecodeError on invalid TOML syntax."""
        mock_fs.add_file(FAKE_PROJECT_DIR / "pyproject.toml", "invalid [[ toml")
        with pytest.raises(ParseError):
            with mock_fs.apply():
                _get_djb_source_config(FAKE_PROJECT_DIR / "pyproject.toml")

    def test_parses_path_instead_of_workspace(self, mock_fs: MockFilesystem):
        """_get_djb_source_config handles djb config with path instead of workspace."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"sources": {"djb": {"path": "../djb", "editable": True}}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_djb_source_config(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == {"path": "../djb", "editable": True}

    def test_parses_empty_djb_config(self, mock_fs: MockFilesystem):
        """_get_djb_source_config handles empty djb config dict."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"sources": {"djb": {}}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_djb_source_config(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == {}


class TestGetWorkspaceMembers:
    """Tests for _get_workspace_members function."""

    def test_returns_members_when_present(self, mock_fs: MockFilesystem):
        """_get_workspace_members returns workspace members list when configured."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"workspace": {"members": ["djb", "packages/other"]}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == ["djb", "packages/other"]

    def test_returns_empty_list_when_no_members(self, mock_fs: MockFilesystem):
        """_get_workspace_members returns empty list when workspace has no members key."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"workspace": {"exclude": ["examples/*"]}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == []

    @pytest.mark.parametrize(
        "parsed,missing_section",
        [
            (
                {
                    "project": {"name": "myproject"},
                    "tool": {"uv": {"dev-dependencies": ["pytest"]}},
                },
                "workspace",
            ),
            (
                {"project": {"name": "myproject"}, "tool": {"pytest": {"testpaths": ["tests"]}}},
                "uv",
            ),
            (
                {"project": {"name": "myproject"}},
                "tool",
            ),
        ],
        ids=["no_workspace", "no_uv", "no_tool"],
    )
    def test_returns_empty_list_when_section_missing(
        self, mock_fs: MockFilesystem, parsed, missing_section
    ):
        """_get_workspace_members returns empty list when required section is missing."""
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == []

    def test_returns_empty_list_for_missing_file(self, mock_fs: MockFilesystem):
        """_get_workspace_members returns empty list when pyproject.toml doesn't exist."""
        # Don't add the file - it won't exist
        with mock_fs.apply():
            result = _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == []

    def test_raises_for_invalid_toml(self, mock_fs: MockFilesystem):
        """_get_workspace_members raises TOMLDecodeError on malformed TOML."""
        mock_fs.add_file(FAKE_PROJECT_DIR / "pyproject.toml", "invalid [[ toml")
        with pytest.raises(ParseError):
            with mock_fs.apply():
                _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")

    def test_parses_single_workspace_member(self, mock_fs: MockFilesystem):
        """_get_workspace_members handles single workspace member."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"workspace": {"members": ["djb"]}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == ["djb"]

    def test_parses_empty_members_list(self, mock_fs: MockFilesystem):
        """_get_workspace_members handles empty members list."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"workspace": {"members": []}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == []

    def test_parses_glob_patterns_in_members(self, mock_fs: MockFilesystem):
        """_get_workspace_members handles glob patterns in members list."""
        parsed = {
            "project": {"name": "myproject"},
            "tool": {"uv": {"workspace": {"members": ["packages/*", "djb"]}}},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = _get_workspace_members(FAKE_PROJECT_DIR / "pyproject.toml")
        assert result == ["packages/*", "djb"]


class TestIsDjbPackageDir:
    """Tests for is_djb_package_dir function."""

    def test_returns_true_for_valid_djb_package(self, mock_fs: MockFilesystem):
        """is_djb_package_dir returns True when pyproject.toml has name = "djb"."""
        parsed = {"project": {"name": "djb"}}
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = is_djb_package_dir(FAKE_PROJECT_DIR)
        assert result is True

    def test_returns_false_for_different_package_name(self, mock_fs: MockFilesystem):
        """is_djb_package_dir returns False when pyproject.toml has a different package name."""
        parsed = {"project": {"name": "other-package"}}
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = is_djb_package_dir(FAKE_PROJECT_DIR)
        assert result is False

    def test_returns_false_when_pyproject_missing(self, mock_fs: MockFilesystem):
        """is_djb_package_dir returns False when pyproject.toml is missing."""
        # Don't add the file - it won't exist
        with mock_fs.apply():
            result = is_djb_package_dir(FAKE_PROJECT_DIR)
        assert result is False

    def test_raises_for_invalid_toml(self, mock_fs: MockFilesystem):
        """is_djb_package_dir raises TOMLDecodeError on malformed pyproject.toml."""
        mock_fs.add_file(FAKE_PROJECT_DIR / "pyproject.toml", "invalid [[ toml")
        with pytest.raises(ParseError):
            with mock_fs.apply():
                is_djb_package_dir(FAKE_PROJECT_DIR)

    @pytest.mark.parametrize(
        "parsed,description",
        [
            ({"tool": {"pytest": {"testpaths": ["tests"]}}}, "no_project_section"),
            ({"project": {"version": "1.0.0"}}, "no_name_key"),
            ({}, "empty_file"),
        ],
        ids=["no_project_section", "no_name_key", "empty_file"],
    )
    def test_returns_false_for_incomplete_config(
        self, mock_fs: MockFilesystem, parsed, description
    ):
        """is_djb_package_dir returns False when required project name is missing or file is empty."""
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = is_djb_package_dir(FAKE_PROJECT_DIR)
        assert result is False

    def test_parses_realistic_pyproject_structure(self, mock_fs: MockFilesystem):
        """is_djb_package_dir handles realistic pyproject.toml structure."""
        parsed = {
            "project": {
                "name": "djb",
                "version": "0.2.30",
                "description": "Django Backend development tools",
                "dependencies": {"click": ">=8.0"},
            },
            "tool": {"uv": {"dev-dependencies": ["pytest", "ruff"]}},
            "build-system": {"requires": ["hatchling"], "build-backend": "hatchling.build"},
        }
        add_pyproject(mock_fs, parsed)
        with mock_fs.apply():
            result = is_djb_package_dir(FAKE_PROJECT_DIR)
        assert result is True


class TestRemoveDjbWorkspaceMember:
    """Tests for _remove_djb_workspace_member function."""

    def test_removes_workspace_section_with_only_djb(self, mock_fs: MockFilesystem):
        """_remove_djb_workspace_member removes entire [tool.uv.workspace] section when djb is only member."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.workspace]
members = [
    "djb",
]

[tool.uv.sources]
djb = { workspace = true, editable = true }
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_workspace_member(pyproject)

        assert result is True
        content = mock_fs.get_written_content(pyproject)
        assert content is not None
        assert "[tool.uv.workspace]" not in content
        assert '"djb"' not in content
        # Other content should remain
        assert "[project]" in content
        assert "[tool.uv.sources]" in content

    def test_parses_compact_workspace_format(self, mock_fs: MockFilesystem):
        """_remove_djb_workspace_member handles compact single-line workspace format."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.workspace]
members = ["djb"]

[tool.uv.sources]
djb = { workspace = true, editable = true }
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_workspace_member(pyproject)

        assert result is True
        content = mock_fs.get_written_content(pyproject)
        assert content is not None
        assert "[tool.uv.workspace]" not in content

    def test_returns_true_when_no_workspace_section(self, mock_fs: MockFilesystem):
        """_remove_djb_workspace_member returns True (no-op) when no workspace section exists."""
        input_content = """\
[project]
name = "myproject"
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_workspace_member(pyproject)

        assert result is True
        # No write should have occurred
        mock_fs.assert_not_written(pyproject)

    def test_returns_true_when_no_djb_in_workspace(self, mock_fs: MockFilesystem):
        """_remove_djb_workspace_member returns True (no-op) when djb not in workspace members."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.workspace]
members = ["other-package"]
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_workspace_member(pyproject)

        assert result is True
        # No write should have occurred
        mock_fs.assert_not_written(pyproject)

    def test_returns_true_when_file_missing(self, mock_fs: MockFilesystem):
        """_remove_djb_workspace_member returns True when pyproject.toml is missing."""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        # Don't add the file - it won't exist
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_workspace_member(pyproject)

        assert result is True

    def test_warns_on_complex_format(self, mock_fs: MockFilesystem, capsys):
        """_remove_djb_workspace_member warns when format is too complex for regex (multiple members)."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.workspace]
members = ["djb", "other-package"]
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_workspace_member(pyproject, quiet=False)

        assert result is True  # Still returns True (non-fatal)
        captured = capsys.readouterr()
        assert "manually" in captured.out.lower() or "manually" in captured.err.lower()


class TestInstallPreCommitHook:
    """Tests for install_pre_commit_hook function."""

    def test_installs_hook_in_git_repo(self, mock_hook_io):
        """install_pre_commit_hook installs hook when .git directory exists."""
        git_dir = FAKE_PROJECT_DIR / ".git"
        hooks_dir = git_dir / "hooks"
        mock_hook_io.dirs.add(git_dir)
        mock_hook_io.dirs.add(hooks_dir)

        result = install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

        assert result is True
        hook_path = hooks_dir / "pre-commit"
        assert hook_path in mock_hook_io.written_files
        assert mock_hook_io.written_files[hook_path] == PRE_COMMIT_HOOK_CONTENT
        # Check chmod was called with execute bits
        assert (hook_path, 0o755) in mock_hook_io.chmod_calls

    def test_creates_hooks_dir_if_missing(self, mock_hook_io):
        """install_pre_commit_hook creates hooks directory if it doesn't exist."""
        git_dir = FAKE_PROJECT_DIR / ".git"
        hooks_dir = git_dir / "hooks"
        mock_hook_io.dirs.add(git_dir)
        # Don't add hooks dir - it will be created by mkdir

        result = install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

        assert result is True
        assert hooks_dir in mock_hook_io.dirs  # mkdir was called
        hook_path = hooks_dir / "pre-commit"
        assert hook_path in mock_hook_io.written_files

    def test_updates_existing_hook(self, mock_hook_io):
        """install_pre_commit_hook updates hook if it already exists with different content."""
        git_dir = FAKE_PROJECT_DIR / ".git"
        hooks_dir = git_dir / "hooks"
        hook_path = hooks_dir / "pre-commit"
        mock_hook_io.dirs.add(git_dir)
        mock_hook_io.dirs.add(hooks_dir)
        mock_hook_io.files[hook_path] = "#!/bin/bash\necho 'old hook'\n"

        result = install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

        assert result is True
        assert mock_hook_io.written_files[hook_path] == PRE_COMMIT_HOOK_CONTENT

    def test_skips_if_already_up_to_date(self, mock_hook_io):
        """install_pre_commit_hook returns True without writing if content matches."""
        git_dir = FAKE_PROJECT_DIR / ".git"
        hooks_dir = git_dir / "hooks"
        hook_path = hooks_dir / "pre-commit"
        mock_hook_io.dirs.add(git_dir)
        mock_hook_io.dirs.add(hooks_dir)
        mock_hook_io.files[hook_path] = PRE_COMMIT_HOOK_CONTENT

        result = install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

        assert result is True
        # No write should have occurred since content matches
        assert hook_path not in mock_hook_io.written_files

    def test_returns_false_if_not_git_repo(self, mock_hook_io):
        """install_pre_commit_hook returns False when not in a git repo."""
        # No .git directory in mock_hook_io.dirs

        result = install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

        assert result is False

    def test_returns_false_if_git_is_file(self, mock_hook_io):
        """Returns False when .git is a file (submodule worktree)."""
        # Add .git as a file, not a directory
        git_path = FAKE_PROJECT_DIR / ".git"
        mock_hook_io.files[git_path] = "gitdir: /path/to/real/git/dir"
        # Note: .git is NOT in mock_hook_io.dirs, so is_dir() returns False

        result = install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

        assert result is False


class TestRemoveDjbSourceEntry:
    """Tests for _remove_djb_source_entry function."""

    def test_removes_workspace_source_entry(self, mock_fs: MockFilesystem):
        """_remove_djb_source_entry removes djb = { workspace = true } from sources."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.sources]
djb = { workspace = true }
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_source_entry(pyproject)

        assert result is True
        content = mock_fs.get_written_content(pyproject)
        assert content is not None
        assert "djb" not in content
        # Empty sources section should be removed
        assert "[tool.uv.sources]" not in content
        assert "[project]" in content

    def test_removes_editable_source_entry(self, mock_fs: MockFilesystem):
        """_remove_djb_source_entry removes djb = { workspace = true, editable = true } from sources."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.sources]
djb = { workspace = true, editable = true }
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_source_entry(pyproject)

        assert result is True
        content = mock_fs.get_written_content(pyproject)
        assert content is not None
        assert "djb" not in content
        assert "[tool.uv.sources]" not in content

    def test_removes_path_source_entry(self, mock_fs: MockFilesystem):
        """_remove_djb_source_entry removes djb = { path = "djb", editable = true } from sources."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.sources]
djb = { path = "djb", editable = true }
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_source_entry(pyproject)

        assert result is True
        content = mock_fs.get_written_content(pyproject)
        assert content is not None
        assert "djb" not in content
        assert "[tool.uv.sources]" not in content

    def test_preserves_other_sources(self, mock_fs: MockFilesystem):
        """_remove_djb_source_entry preserves other source entries when removing djb."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.sources]
djb = { workspace = true }
other-package = { path = "other" }
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_source_entry(pyproject)

        assert result is True
        content = mock_fs.get_written_content(pyproject)
        assert content is not None
        assert "djb" not in content
        # Other source and section should remain
        assert "[tool.uv.sources]" in content
        assert "other-package" in content

    def test_returns_true_when_no_sources_section(self, mock_fs: MockFilesystem):
        """_remove_djb_source_entry returns True (no-op) when no sources section exists."""
        input_content = """\
[project]
name = "myproject"
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_source_entry(pyproject)

        assert result is True
        # No write should have occurred
        mock_fs.assert_not_written(pyproject)

    def test_returns_true_when_file_missing(self, mock_fs: MockFilesystem):
        """_remove_djb_source_entry returns True when pyproject.toml is missing."""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        # Don't add the file - it won't exist
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_source_entry(pyproject)

        assert result is True

    def test_returns_true_when_no_djb_in_sources(self, mock_fs: MockFilesystem):
        """_remove_djb_source_entry returns True (no-op) when djb not in sources."""
        input_content = """\
[project]
name = "myproject"

[tool.uv.sources]
other-package = { path = "other" }
"""
        pyproject = FAKE_PROJECT_DIR / "pyproject.toml"
        mock_fs.add_file(pyproject, input_content)
        with mock_fs.apply(mock_locking=True):
            result = _remove_djb_source_entry(pyproject)

        assert result is True
        # No write should have occurred
        mock_fs.assert_not_written(pyproject)
