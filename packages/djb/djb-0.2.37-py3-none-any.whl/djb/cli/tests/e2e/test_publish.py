"""End-to-end tests for djb publish CLI command.

Commands tested:
- djb publish

Tests requiring real file I/O for TOML parsing and directory creation.
"""

from __future__ import annotations

import os
from pathlib import Path

from tomlkit.exceptions import ParseError
from unittest.mock import patch

import click
import pytest

from djb.cli.djb import djb_cli
from djb.cli.editable import find_djb_dir
from djb.cli.publish import (
    PUBLISH_WORKFLOW_TEMPLATE,
    ensure_publish_workflow,
    find_version_file,
    get_package_info,
    get_version,
    is_dependency_of,
    set_version,
    update_parent_dependency,
)
from djb.cli.utils import find_dependency_string
from djb.config import find_project_root
from djb.core.exceptions import ProjectNotFound

from . import DJB_PYPROJECT_CONTENT, make_editable_pyproject


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


class TestFindDjbDirRaiseOnMissing:
    """Tests for find_djb_dir with raise_on_missing=True."""

    def test_finds_djb_in_cwd(self, project_dir: Path):
        """Finding djb when in djb directory."""
        (project_dir / "pyproject.toml").write_text(DJB_PYPROJECT_CONTENT)

        with patch("djb.cli.editable.Path.cwd", return_value=project_dir):
            result = find_djb_dir(raise_on_missing=True)
            assert result == project_dir

    def test_finds_djb_in_subdirectory(self, project_dir: Path, project_with_djb: Path):
        """Finding djb/ subdirectory."""
        with patch("djb.cli.editable.Path.cwd", return_value=project_dir):
            result = find_djb_dir(raise_on_missing=True)
            assert result == project_with_djb

    def test_raises_when_not_found(self, project_dir: Path):
        """Raises ClickException when djb not found."""
        with patch("djb.cli.editable.Path.cwd", return_value=project_dir):
            with pytest.raises(click.ClickException):
                find_djb_dir(raise_on_missing=True)


class TestGetVersion:
    """Tests for get_version function."""

    def test_gets_version(self, project_dir: Path):
        """Getting version from pyproject.toml."""
        (project_dir / "pyproject.toml").write_text('[project]\nname = "djb"\nversion = "0.2.5"')

        result = get_version(project_dir)
        assert result == "0.2.5"

    def test_raises_when_version_not_found(self, project_dir: Path):
        """Raises when version not in pyproject.toml."""
        (project_dir / "pyproject.toml").write_text('[project]\nname = "djb"')

        with pytest.raises(click.ClickException):
            get_version(project_dir)


class TestGetPackageInfo:
    """Tests for get_package_info function - covers all error paths."""

    def test_returns_name_and_version(self, project_dir: Path):
        """Returns tuple of (name, version) on success."""
        (project_dir / "pyproject.toml").write_text('[project]\nname = "djb"\nversion = "0.2.5"')

        name, version = get_package_info(project_dir)

        assert name == "djb"
        assert version == "0.2.5"

    def test_accepts_hyphenated_package_name(self, project_dir: Path):
        """Handles package names with hyphens."""
        (project_dir / "pyproject.toml").write_text(
            '[project]\nname = "django-model-changes"\nversion = "1.0.0"'
        )

        name, version = get_package_info(project_dir)

        assert name == "django-model-changes"
        assert version == "1.0.0"

    def test_error_missing_pyproject(self, project_dir: Path):
        """Raises ClickException when pyproject.toml is missing."""
        with pytest.raises(click.ClickException) as exc_info:
            get_package_info(project_dir)

        assert "pyproject.toml" in str(exc_info.value.message)

    def test_error_missing_project_name(self, project_dir: Path):
        """Raises ClickException when project.name is missing."""
        (project_dir / "pyproject.toml").write_text('[project]\nversion = "0.2.5"')

        with pytest.raises(click.ClickException) as exc_info:
            get_package_info(project_dir)

        assert "name" in str(exc_info.value.message).lower()

    def test_error_missing_project_version(self, project_dir: Path):
        """Raises ClickException when project.version is missing."""
        (project_dir / "pyproject.toml").write_text('[project]\nname = "djb"')

        with pytest.raises(click.ClickException) as exc_info:
            get_package_info(project_dir)

        assert "version" in str(exc_info.value.message).lower()

    def test_error_missing_project_section(self, project_dir: Path):
        """Raises ClickException when [project] section is missing."""
        (project_dir / "pyproject.toml").write_text('[tool.other]\nkey = "value"')

        with pytest.raises(click.ClickException) as exc_info:
            get_package_info(project_dir)

        assert "name" in str(exc_info.value.message).lower()

    def test_error_invalid_toml(self, project_dir: Path):
        """Raises ClickException for invalid TOML syntax."""
        (project_dir / "pyproject.toml").write_text("invalid toml [ syntax")

        with pytest.raises(click.ClickException) as exc_info:
            get_package_info(project_dir)

        assert "Invalid TOML" in str(exc_info.value.message)


class TestFindVersionFile:
    """Tests for find_version_file function - covers src and flat layouts."""

    def test_finds_src_layout(self, project_dir: Path):
        """Finds _version.py in src layout."""
        # Create src layout structure
        version_dir = project_dir / "src" / "djb"
        version_dir.mkdir(parents=True)
        version_file = version_dir / "_version.py"
        version_file.write_text('__version__ = "0.2.5"')

        result = find_version_file(project_dir, "djb")

        assert result == version_file

    def test_finds_flat_layout(self, project_dir: Path):
        """Finds _version.py in flat layout."""
        # Create flat layout structure
        version_dir = project_dir / "djb"
        version_dir.mkdir()
        version_file = version_dir / "_version.py"
        version_file.write_text('__version__ = "0.2.5"')

        result = find_version_file(project_dir, "djb")

        assert result == version_file

    def test_prefers_src_layout_over_flat(self, project_dir: Path):
        """Prefers src layout when both exist."""
        # Create both layouts
        src_version_dir = project_dir / "src" / "djb"
        src_version_dir.mkdir(parents=True)
        src_version_file = src_version_dir / "_version.py"
        src_version_file.write_text('__version__ = "src"')

        flat_version_dir = project_dir / "djb"
        flat_version_dir.mkdir()
        flat_version_file = flat_version_dir / "_version.py"
        flat_version_file.write_text('__version__ = "flat"')

        result = find_version_file(project_dir, "djb")

        assert result == src_version_file

    def test_returns_none_when_not_found(self, project_dir: Path):
        """Returns None when _version.py doesn't exist."""
        result = find_version_file(project_dir, "djb")

        assert result is None

    def test_converts_hyphens_to_underscores(self, project_dir: Path):
        """Converts hyphens to underscores for directory lookup."""
        # Create src layout with underscored directory
        version_dir = project_dir / "src" / "django_model_changes"
        version_dir.mkdir(parents=True)
        version_file = version_dir / "_version.py"
        version_file.write_text('__version__ = "1.0.0"')

        result = find_version_file(project_dir, "django-model-changes")

        assert result == version_file


class TestSetVersion:
    """Tests for set_version function."""

    def test_sets_version(self, project_dir: Path):
        """Setting version in pyproject.toml and _version.py."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "djb"\nversion = "0.2.5"')

        # Create the src/djb directory structure
        version_dir = project_dir / "src" / "djb"
        version_dir.mkdir(parents=True)
        version_file = version_dir / "_version.py"
        version_file.write_text('__version__ = "0.2.5"')

        set_version(project_dir, "djb", "0.3.0")

        # Check pyproject.toml
        content = pyproject.read_text()
        assert 'version = "0.3.0"' in content
        assert 'version = "0.2.5"' not in content

        # Check _version.py
        version_content = version_file.read_text()
        assert '__version__ = "0.3.0"' in version_content
        assert '__version__ = "0.2.5"' not in version_content


class TestFindParentProject:
    """Tests for finding parent project using find_project_root."""

    def test_finds_parent_with_djb_dependency(self, project_dir: Path, project_with_djb: Path):
        """Finding parent project with djb dependency."""
        parent_pyproject = project_dir / "pyproject.toml"
        parent_pyproject.write_text(
            '[project]\nname = "myproject"\ndependencies = ["djb>=0.2.5"]\n'
        )

        path, _source = find_project_root(start_path=project_with_djb.parent)
        assert path == project_dir

    def test_raises_when_no_parent(self, project_with_djb: Path):
        """Raises ProjectNotFound when no parent project."""
        # Clear DJB_PROJECT_DIR to test actual search behavior
        with patch.dict(os.environ, {"DJB_PROJECT_DIR": ""}, clear=False):
            with pytest.raises(ProjectNotFound):
                find_project_root(start_path=project_with_djb.parent)

    def test_raises_when_parent_without_djb(self, project_dir: Path, project_with_djb: Path):
        """Raises ProjectNotFound when parent doesn't depend on djb."""
        parent_pyproject = project_dir / "pyproject.toml"
        parent_pyproject.write_text(
            '[project]\nname = "myproject"\ndependencies = ["other-package>=1.0"]\n'
        )

        # Clear DJB_PROJECT_DIR to test actual search behavior
        with patch.dict(os.environ, {"DJB_PROJECT_DIR": ""}, clear=False):
            with pytest.raises(ProjectNotFound):
                find_project_root(start_path=project_with_djb.parent)


class TestUpdateParentDependency:
    """Tests for update_parent_dependency function."""

    def test_updates_version(self, project_dir: Path):
        """Updates djb version in dependencies."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    "djb>=0.2.4",
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert '"djb>=0.2.5"' in content
        assert '"djb>=0.2.4"' not in content

    def test_returns_false_when_no_change(self, project_dir: Path):
        """Returns False when version already correct."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    "djb>=0.2.5",
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")
        assert result is False

    @pytest.mark.parametrize(
        "old_dep,expected_new",
        [
            # Various version specifiers
            ("djb==0.2.4", "djb>=0.2.5"),
            ("djb~=0.2.4", "djb>=0.2.5"),
            ("djb<1.0", "djb>=0.2.5"),
            ("djb<=0.2.4", "djb>=0.2.5"),
            ("djb>0.2.3", "djb>=0.2.5"),
            ("djb!=0.2.3", "djb>=0.2.5"),
            # Compound version specifiers
            ("djb>=0.2.4,<1.0", "djb>=0.2.5"),
            # Extras syntax
            ("djb[dev]>=0.2.4", "djb[dev]>=0.2.5"),
            ("djb[dev,test]>=0.2.4", "djb[dev,test]>=0.2.5"),
            # Dependency without version constraint
            ("djb", "djb>=0.2.5"),
            # No specifier with extras
            ("djb[dev]", "djb[dev]>=0.2.5"),
        ],
    )
    def test_updates_all_pep508_specifiers(self, project_dir: Path, old_dep, expected_new):
        """Updates dependency string for all PEP 508 version specifiers and extras."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            f"""
[project]
name = "myproject"
dependencies = [
    "{old_dep}",
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert f'"{expected_new}"' in content
        assert f'"{old_dep}"' not in content

    def test_preserves_pep508_environment_markers(self, project_dir: Path):
        """Updates version while preserving PEP 508 environment markers."""
        pyproject = project_dir / "pyproject.toml"
        # Use single quotes for TOML string since marker contains double quotes
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    'djb>=0.2.4; python_version >= "3.10"',
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert "'djb>=0.2.5; python_version >= " in content
        assert "'djb>=0.2.4; python_version >= " not in content

    def test_preserves_extras_and_markers(self, project_dir: Path):
        """Updates version while preserving extras and environment markers."""
        pyproject = project_dir / "pyproject.toml"
        # Use single quotes for TOML string since marker contains double quotes
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    'djb[dev]>=0.2.4; sys_platform == "linux"',
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert "'djb[dev]>=0.2.5; sys_platform == " in content
        assert "'djb[dev]>=0.2.4; sys_platform == " not in content

    def test_returns_false_when_package_not_found(self, project_dir: Path):
        """Returns False when package is not a dependency."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    "django>=4.0",
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")
        assert result is False

    def test_updates_optional_dependencies(self, project_dir: Path):
        """Updates package in optional dependencies."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = []

[project.optional-dependencies]
dev = [
    "djb>=0.2.4",
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert '"djb>=0.2.5"' in content
        assert '"djb>=0.2.4"' not in content

    def test_preserves_formatting_and_comments(self, project_dir: Path):
        """Preserves file formatting including comments."""
        pyproject = project_dir / "pyproject.toml"
        original = """
[project]
name = "myproject"
# Important dependencies
dependencies = [
    "django>=4.0",  # Web framework
    "djb>=0.2.4",   # Deployment tool
    "requests>=2.0",
]
"""
        pyproject.write_text(original)

        result = update_parent_dependency(project_dir, "djb", "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert '"djb>=0.2.5"' in content
        assert "# Important dependencies" in content
        assert "# Web framework" in content
        assert "# Deployment tool" in content
        assert '"django>=4.0"' in content
        assert '"requests>=2.0"' in content

    def test_single_quotes(self, project_dir: Path):
        """Handles single-quoted dependencies."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    'djb>=0.2.4',
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")

        assert result is True
        content = pyproject.read_text()
        assert "'djb>=0.2.5'" in content
        assert "'djb>=0.2.4'" not in content

    def test_does_not_match_prefix_package(self, project_dir: Path):
        """Does not update djb-extras dependency when updating djb package."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myproject"
dependencies = [
    "djb-extras>=0.2.4",
]
"""
        )

        result = update_parent_dependency(project_dir, "djb", "0.2.5")
        assert result is False

        content = pyproject.read_text()
        assert '"djb-extras>=0.2.4"' in content

    def test_raises_for_invalid_toml(self, project_dir: Path):
        """update_parent_dependency raises TOMLDecodeError on malformed pyproject.toml."""
        pyproject = project_dir / "pyproject.toml"
        original_content = "invalid toml [ syntax"
        pyproject.write_text(original_content)

        with pytest.raises(ParseError):
            update_parent_dependency(project_dir, "djb", "0.2.5")

        # Verify file wasn't modified
        assert pyproject.read_text() == original_content


class TestFindDependencyString:
    """Tests for find_dependency_string function.

    This function uses TOML parsing and packaging.requirements.Requirement
    to find a dependency string. These direct tests cover edge cases not
    observable through update_parent_dependency() since both return
    None/False for error cases with no distinction.
    """

    def test_finds_simple_dependency(self, project_dir: Path):
        """Finds basic dependency string."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\ndependencies = ["djb>=0.2.4"]\n')

        result = find_dependency_string("djb", pyproject)

        assert result == "djb>=0.2.4"

    def test_finds_dependency_with_extras(self, project_dir: Path):
        """Finds dependency with extras syntax."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\ndependencies = ["djb[dev,test]>=0.2.4"]\n')

        result = find_dependency_string("djb", pyproject)

        assert result == "djb[dev,test]>=0.2.4"

    def test_finds_dependency_with_markers(self, project_dir: Path):
        """Finds dependency with environment markers."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """[project]
dependencies = ['djb>=0.2.4; python_version >= "3.10"']
"""
        )

        result = find_dependency_string("djb", pyproject)

        assert result == 'djb>=0.2.4; python_version >= "3.10"'

    def test_finds_dependency_in_optional_dependencies(self, project_dir: Path):
        """Finds dependency in optional-dependencies section."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """[project]
dependencies = []

[project.optional-dependencies]
dev = ["djb>=0.2.4"]
"""
        )

        result = find_dependency_string("djb", pyproject)

        assert result == "djb>=0.2.4"

    def test_returns_none_when_not_found(self, project_dir: Path):
        """Returns None when package not in dependencies."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\ndependencies = ["django>=4.0"]\n')

        result = find_dependency_string("djb", pyproject)

        assert result is None

    def test_raises_for_toml_parse_error(self, project_dir: Path):
        """find_dependency_string raises TOMLDecodeError on malformed pyproject.toml."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text("invalid toml [ syntax")

        with pytest.raises(ParseError):
            find_dependency_string("djb", pyproject)

    def test_returns_none_when_project_section_missing(self, project_dir: Path):
        """Returns None when [project] section is missing."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[tool.other]\nkey = "value"\n')

        result = find_dependency_string("djb", pyproject)

        assert result is None

    def test_skips_malformed_deps_finds_valid(self, project_dir: Path):
        """Skips malformed dependency strings but finds valid ones.

        This edge case is only testable with direct tests because
        update_parent_dependency() doesn't expose which deps were skipped.
        """
        pyproject = project_dir / "pyproject.toml"
        # Include malformed deps that will fail Requirement() parsing
        pyproject.write_text(
            """[project]
dependencies = [
    "not a valid @ dependency string!!",
    "djb>=0.2.4",
    "another invalid >>>>> thing",
]
"""
        )

        result = find_dependency_string("djb", pyproject)

        assert result == "djb>=0.2.4"

    def test_skips_non_list_dependencies(self, project_dir: Path):
        """Handles non-list dependencies value."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\ndependencies = "not-a-list"\n')

        result = find_dependency_string("djb", pyproject)

        assert result is None

    def test_skips_non_list_optional_dependencies(self, project_dir: Path):
        """Handles non-list optional-dependencies value."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """[project]
dependencies = []

[project.optional-dependencies]
dev = "not-a-list"
"""
        )

        result = find_dependency_string("djb", pyproject)

        assert result is None

    def test_package_name_case_insensitive(self, project_dir: Path):
        """Package name matching is case-insensitive per PEP 503.

        The new implementation uses canonicalize_name for proper PEP 503
        normalization. Both "Django" and "django" match "Django>=4.0".
        """
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\ndependencies = ["Django>=4.0"]\n')

        # Uppercase query finds the dependency
        result = find_dependency_string("Django", pyproject)
        assert result == "Django>=4.0"

        # Lowercase query also finds it (PEP 503 normalization)
        result = find_dependency_string("django", pyproject)
        assert result == "Django>=4.0"

        # Mixed case also works
        result = find_dependency_string("DJANGO", pyproject)
        assert result == "Django>=4.0"

    def test_does_not_match_prefix_package(self, project_dir: Path):
        """Returns None for djb-extras when searching for djb dependency string."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text('[project]\ndependencies = ["djb-extras>=0.1"]\n')

        result = find_dependency_string("djb", pyproject)

        assert result is None

    def test_multiple_optional_dependency_groups(self, project_dir: Path):
        """Searches across multiple optional-dependencies groups."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            """[project]
dependencies = ["requests>=2.0"]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
deploy = ["djb>=0.2.4"]
"""
        )

        result = find_dependency_string("djb", pyproject)

        assert result == "djb>=0.2.4"


class TestPublishCommand:
    """Tests for publish CLI command."""

    @pytest.fixture
    def djb_project_v024(self, project_dir: Path):
        """Create djb project with version 0.2.4 for publish tests."""
        djb_dir = project_dir / "djb"
        djb_dir.mkdir()
        (djb_dir / "pyproject.toml").write_text('[project]\nname = "djb"\nversion = "0.2.4"\n')
        return djb_dir

    def test_help(self, cli_runner):
        """Publish --help works."""
        result = cli_runner.invoke(djb_cli, ["publish", "--help"])
        assert result.exit_code == 0
        assert "Bump version and publish a Python package to PyPI" in result.output
        assert "--major" in result.output
        assert "--minor" in result.output
        assert "--patch" in result.output
        assert "--dry-run" in result.output

    def test_dry_run_basic(self, cli_runner, project_dir: Path, djb_project_v024):
        """Dry-run shows planned actions."""
        with patch("djb.cli.publish.Path.cwd", return_value=project_dir):
            result = cli_runner.invoke(djb_cli, ["publish", "--dry-run"])

        assert result.exit_code == 0
        assert "[dry-run]" in result.output
        assert "0.2.5" in result.output
        assert "v0.2.5" in result.output

    def test_dry_run_with_editable_parent(self, cli_runner, project_dir: Path, djb_project_v024):
        """Dry-run shows editable handling steps."""
        parent_pyproject = project_dir / "pyproject.toml"
        parent_pyproject.write_text(
            '[project]\nname = "myproject"\ndependencies = ["djb>=0.2.4"]\n\n'
            + make_editable_pyproject("djb").split("\n\n", 1)[
                1
            ]  # Get just the [tool.uv.sources] part
        )

        with patch("djb.cli.publish.Path.cwd", return_value=project_dir):
            result = cli_runner.invoke(djb_cli, ["publish", "--dry-run"])

        assert result.exit_code == 0
        assert "editable" in result.output.lower()
        assert "Stash editable djb configuration" in result.output
        assert "Re-enable editable djb with current version" in result.output

    def test_dry_run_minor_bump(self, cli_runner, project_dir: Path, djb_project_v024):
        """Dry-run with --minor flag."""
        with patch("djb.cli.publish.Path.cwd", return_value=project_dir):
            result = cli_runner.invoke(djb_cli, ["publish", "--minor", "--dry-run"])

        assert result.exit_code == 0
        assert "0.3.0" in result.output

    def test_dry_run_major_bump(self, cli_runner, project_dir: Path, djb_project_v024):
        """Dry-run with --major flag."""
        with patch("djb.cli.publish.Path.cwd", return_value=project_dir):
            result = cli_runner.invoke(djb_cli, ["publish", "--major", "--dry-run"])

        assert result.exit_code == 0
        assert "1.0.0" in result.output


class TestIsDependencyOf:
    """Tests for is_dependency_of function."""

    @pytest.mark.parametrize(
        "content,package,expected",
        [
            # Basic dependency with version constraint
            ('[project]\ndependencies = ["djb>=0.2.4"]\n', "djb", True),
            ('[project]\ndependencies = ["djb>=0.2.4"]\n', "other", False),
            # Dependency with multiple constraints
            ('[project]\ndependencies = ["djb>=0.2.4,<1.0"]\n', "djb", True),
            # Dependency without version constraint
            ('[project]\ndependencies = ["djb"]\n', "djb", True),
            # Single quotes
            ("[project]\ndependencies = ['djb>=0.2.4']\n", "djb", True),
            # Package with hyphen
            (
                '[project]\ndependencies = ["django-model-changes>=0.5"]\n',
                "django-model-changes",
                True,
            ),
            # Package with underscore
            ('[project]\ndependencies = ["my_package>=1.0"]\n', "my_package", True),
            # Empty dependencies
            ("[project]\ndependencies = []\n", "djb", False),
            # Optional dependencies
            ('[project.optional-dependencies]\ndev = ["djb>=0.2"]\n', "djb", True),
            # Multiple dependencies
            (
                '[project]\ndependencies = ["other>=1.0", "djb>=0.2.4", "another>=2.0"]\n',
                "djb",
                True,
            ),
            # Prefix package names should NOT match (fixed false positive)
            ('[project]\ndependencies = ["djb-extras>=0.1"]\n', "djb", False),
            ('[project]\ndependencies = ["djb_extras>=0.1"]\n', "djb", False),
            ('[project]\ndependencies = ["djb123>=0.1"]\n', "djb", False),
            # Similar prefix in different package (should NOT match)
            ('[project]\ndependencies = ["django>=4.0"]\n', "djan", False),
            # Package with extras syntax
            ('[project]\ndependencies = ["djb[dev]>=0.1"]\n', "djb", True),
            # Package with environment marker
            ('[project]\ndependencies = ["djb ; python_version >= \\"3.8\\""]\n', "djb", True),
        ],
    )
    def test_is_dependency_of(self, project_dir: Path, content, package, expected):
        """Is_dependency_of with various pyproject.toml content."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(content)

        result = is_dependency_of(package, project_dir)
        assert result is expected

    def test_returns_false_when_no_pyproject(self, project_dir: Path):
        """is_dependency_of returns False when pyproject.toml is missing."""
        result = is_dependency_of("djb", project_dir)
        assert result is False

    def test_raises_for_toml_parse_error(self, project_dir: Path):
        """is_dependency_of raises TOMLDecodeError on malformed pyproject.toml."""
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text("invalid toml [ syntax")

        with pytest.raises(ParseError):
            is_dependency_of("djb", project_dir)


class TestEnsurePublishWorkflow:
    """Tests for ensure_publish_workflow function."""

    def test_creates_workflow_when_not_exists(self, project_dir: Path):
        """ensure_publish_workflow creates .github/workflows/publish.yaml when file doesn't exist."""
        result = ensure_publish_workflow(project_dir)

        assert result is True
        workflow_file = project_dir / ".github" / "workflows" / "publish.yaml"
        assert workflow_file.exists()
        content = workflow_file.read_text()
        assert content == PUBLISH_WORKFLOW_TEMPLATE

    def test_returns_false_when_exists(self, project_dir: Path):
        """Returns False when workflow file already exists."""
        # Create existing workflow
        workflow_dir = project_dir / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)
        workflow_file = workflow_dir / "publish.yaml"
        workflow_file.write_text("existing content")

        result = ensure_publish_workflow(project_dir)

        assert result is False
        # Content should be unchanged
        assert workflow_file.read_text() == "existing content"

    def test_is_idempotent(self, project_dir: Path):
        """Calling multiple times has same result."""
        # First call creates
        result1 = ensure_publish_workflow(project_dir)
        workflow_file = project_dir / ".github" / "workflows" / "publish.yaml"
        content1 = workflow_file.read_text()

        # Second call doesn't modify
        result2 = ensure_publish_workflow(project_dir)
        content2 = workflow_file.read_text()

        assert result1 is True
        assert result2 is False
        assert content1 == content2

    def test_creates_parent_directories(self, project_dir: Path):
        """Creates .github/workflows directories if needed."""
        assert not (project_dir / ".github").exists()

        ensure_publish_workflow(project_dir)

        assert (project_dir / ".github").is_dir()
        assert (project_dir / ".github" / "workflows").is_dir()

    def test_workflow_contains_expected_content(self, project_dir: Path):
        """Workflow file has expected GitHub Actions content."""
        ensure_publish_workflow(project_dir)

        workflow_file = project_dir / ".github" / "workflows" / "publish.yaml"
        content = workflow_file.read_text()

        # Check key sections are present
        assert "name: Publish to PyPI" in content
        assert "on:\n  push:\n    tags:" in content
        assert "v*.*.*" in content
        assert "permissions:" in content
        assert "id-token: write" in content
        assert "environment: pypi" in content
        assert "pypa/gh-action-pypi-publish" in content
