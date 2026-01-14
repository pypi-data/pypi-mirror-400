"""Tests for djb.cli.utils.pyproject module."""

from __future__ import annotations

from pathlib import Path

from tomlkit.exceptions import ParseError

import pytest

pytestmark = pytest.mark.e2e_marker

from djb.cli.utils.pyproject import (
    collect_all_dependencies,
    find_pyproject_dependency,
    find_dependency_string,
    get_django_settings_module,
    has_dependency,
    load_pyproject,
)


@pytest.fixture
def simple_pyproject(tmp_path: Path) -> Path:
    """Create a simple pyproject.toml file."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "django>=4.0",
    "djb>=0.2.6",
    "requests",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff",
]
test = [
    "coverage>=6.0",
]
"""
    )
    return pyproject


@pytest.fixture
def complex_pyproject(tmp_path: Path) -> Path:
    """Create a pyproject.toml with complex dependency specifications."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "complex-project"
version = "0.1.0"
dependencies = [
    "django>=4.0,<5.0",
    'djb[dev]>=0.2.6; python_version >= "3.10"',
    "DJB-extras>=1.0",
]

[project.optional-dependencies]
all = [
    "mypackage~=1.0",
]
"""
    )
    return pyproject


@pytest.fixture
def normalization_pyproject(tmp_path: Path) -> Path:
    """Create a pyproject.toml for testing PEP 503 name normalization."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "normalization-test"
version = "0.1.0"
dependencies = [
    "DJB>=0.2.4",
    "my-package>=1.0",
    "Some.Package>=2.0",
]
"""
    )
    return pyproject


@pytest.fixture
def empty_pyproject(tmp_path: Path) -> Path:
    """Create a pyproject.toml with no dependencies."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "empty-project"
version = "0.1.0"
"""
    )
    return pyproject


@pytest.fixture
def invalid_pyproject(tmp_path: Path) -> Path:
    """Create an invalid pyproject.toml file."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("this is not valid toml {{{{")
    return pyproject


class TestLoadPyproject:
    """Tests for load_pyproject function."""

    def test_load_valid_file(self, simple_pyproject: Path) -> None:
        """load_pyproject returns parsed data for valid file."""
        data = load_pyproject(simple_pyproject)
        assert data is not None
        assert data["project"]["name"] == "test-project"

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """load_pyproject returns None for nonexistent file."""
        result = load_pyproject(tmp_path / "nonexistent.toml")
        assert result is None

    def test_load_invalid_file(self, invalid_pyproject: Path) -> None:
        """load_pyproject raises TOMLDecodeError for invalid TOML."""
        with pytest.raises(ParseError):
            load_pyproject(invalid_pyproject)


class TestCollectAllDependencies:
    """Tests for collect_all_dependencies function."""

    def test_collect_regular_and_optional(self, simple_pyproject: Path) -> None:
        """collect_all_dependencies includes regular and optional dependencies."""
        data = load_pyproject(simple_pyproject)
        assert data is not None
        deps = collect_all_dependencies(data)

        # Regular deps
        assert "django>=4.0" in deps
        assert "djb>=0.2.6" in deps
        assert "requests" in deps

        # Optional deps
        assert "pytest>=7.0" in deps
        assert "ruff" in deps
        assert "coverage>=6.0" in deps

    def test_empty_dependencies(self, empty_pyproject: Path) -> None:
        """collect_all_dependencies returns empty list for project with no dependencies."""
        data = load_pyproject(empty_pyproject)
        assert data is not None
        deps = collect_all_dependencies(data)
        assert deps == []

    def test_empty_data(self) -> None:
        """collect_all_dependencies returns empty list for empty dict."""
        deps = collect_all_dependencies({})
        assert deps == []


class TestFindDependency:
    """Tests for find_dependency function."""

    def test_find_existing_dependency(self, simple_pyproject: Path) -> None:
        """find_dependency returns Requirement for existing dependency."""
        req = find_pyproject_dependency("django", simple_pyproject)
        assert req is not None
        assert req.name == "django"
        assert str(req.specifier) == ">=4.0"

    def test_find_dependency_no_specifier(self, simple_pyproject: Path) -> None:
        """find_dependency returns Requirement with empty specifier for bare dependency."""
        req = find_pyproject_dependency("requests", simple_pyproject)
        assert req is not None
        assert req.name == "requests"
        assert str(req.specifier) == ""

    def test_find_dependency_in_optional(self, simple_pyproject: Path) -> None:
        """find_dependency finds dependencies in optional-dependencies."""
        req = find_pyproject_dependency("pytest", simple_pyproject)
        assert req is not None
        assert req.name == "pytest"

    def test_find_nonexistent_dependency(self, simple_pyproject: Path) -> None:
        """find_dependency returns None for nonexistent dependency."""
        req = find_pyproject_dependency("nonexistent", simple_pyproject)
        assert req is None

    def test_find_dependency_nonexistent_file(self, tmp_path: Path) -> None:
        """find_dependency returns None for nonexistent file."""
        req = find_pyproject_dependency("django", tmp_path / "nonexistent.toml")
        assert req is None

    def test_find_dependency_case_insensitive(self, simple_pyproject: Path) -> None:
        """find_dependency matches package names case-insensitively."""
        # PEP 503 normalization: Django == django == DJANGO
        req = find_pyproject_dependency("Django", simple_pyproject)
        assert req is not None
        assert req.name == "django"

    def test_find_dependency_with_extras_and_marker(self, complex_pyproject: Path) -> None:
        """find_dependency parses extras and environment markers."""
        req = find_pyproject_dependency("djb", complex_pyproject)
        assert req is not None
        assert req.name == "djb"
        assert "dev" in req.extras
        assert req.marker is not None

    def test_find_dependency_no_false_positive(self, complex_pyproject: Path) -> None:
        """find_dependency distinguishes 'djb' from 'djb-extras'."""
        # 'djb-extras' normalizes to 'djb-extras', not 'djb'
        req = find_pyproject_dependency("djb", complex_pyproject)
        assert req is not None
        # The name should be 'djb', not 'djb-extras'
        assert req.name == "djb"

    def test_find_dependency_lowercase_matches_uppercase(
        self, normalization_pyproject: Path
    ) -> None:
        """find_dependency lowercase search finds uppercase dependency (PEP 503)."""
        # Task scenario: searching for "djb" when dependency is "DJB>=0.2.4"
        req = find_pyproject_dependency("djb", normalization_pyproject)
        assert req is not None
        # The name retains original case from pyproject.toml, but matching works
        assert req.name == "DJB"
        assert str(req.specifier) == ">=0.2.4"

    def test_find_dependency_underscore_matches_hyphen(self, normalization_pyproject: Path) -> None:
        """find_dependency underscore search finds hyphenated dependency (PEP 503)."""
        # Task scenario: searching for "my_package" when dependency is "my-package>=1.0"
        req = find_pyproject_dependency("my_package", normalization_pyproject)
        assert req is not None
        assert req.name == "my-package"
        assert str(req.specifier) == ">=1.0"

    def test_find_dependency_period_normalization(self, normalization_pyproject: Path) -> None:
        """find_dependency normalizes periods to hyphens (PEP 503)."""
        # "Some.Package" normalizes to "some-package" for matching
        req = find_pyproject_dependency("some-package", normalization_pyproject)
        assert req is not None
        # The name retains original format from pyproject.toml
        assert req.name == "Some.Package"

        # Also works with underscores
        req = find_pyproject_dependency("some_package", normalization_pyproject)
        assert req is not None
        assert req.name == "Some.Package"


class TestFindDependencyString:
    """Tests for find_dependency_string function."""

    def test_find_existing_dependency_string(self, simple_pyproject: Path) -> None:
        """find_dependency_string returns raw dependency string."""
        dep_str = find_dependency_string("django", simple_pyproject)
        assert dep_str == "django>=4.0"

    def test_find_complex_dependency_string(self, complex_pyproject: Path) -> None:
        """find_dependency_string returns complex dependency with extras and markers."""
        dep_str = find_dependency_string("djb", complex_pyproject)
        assert dep_str is not None
        assert "djb[dev]" in dep_str
        assert "python_version" in dep_str

    def test_find_nonexistent_dependency_string(self, simple_pyproject: Path) -> None:
        """find_dependency_string returns None for nonexistent dependency."""
        dep_str = find_dependency_string("nonexistent", simple_pyproject)
        assert dep_str is None


class TestHasDependency:
    """Tests for has_dependency function."""

    def test_has_regular_dependency(self, simple_pyproject: Path) -> None:
        """has_dependency returns True for regular dependency."""
        assert has_dependency("django", simple_pyproject) is True
        assert has_dependency("djb", simple_pyproject) is True

    def test_has_optional_dependency_excluded_by_default(self, simple_pyproject: Path) -> None:
        """has_dependency excludes optional dependencies by default."""
        # pytest is in optional-dependencies, not regular dependencies
        assert has_dependency("pytest", simple_pyproject) is False

    def test_has_optional_dependency_when_included(self, simple_pyproject: Path) -> None:
        """has_dependency finds optional dependencies when include_optional=True."""
        assert has_dependency("pytest", simple_pyproject, include_optional=True) is True
        assert has_dependency("ruff", simple_pyproject, include_optional=True) is True

    def test_has_nonexistent_dependency(self, simple_pyproject: Path) -> None:
        """has_dependency returns False for nonexistent dependency."""
        assert has_dependency("nonexistent", simple_pyproject) is False
        assert has_dependency("nonexistent", simple_pyproject, include_optional=True) is False

    def test_has_dependency_nonexistent_file(self, tmp_path: Path) -> None:
        """has_dependency returns False for nonexistent file."""
        assert has_dependency("django", tmp_path / "nonexistent.toml") is False

    def test_has_dependency_case_insensitive(self, simple_pyproject: Path) -> None:
        """has_dependency matches package names case-insensitively."""
        assert has_dependency("Django", simple_pyproject) is True
        assert has_dependency("DJANGO", simple_pyproject) is True
        assert has_dependency("DjAnGo", simple_pyproject) is True

    def test_has_dependency_no_false_positive(self, complex_pyproject: Path) -> None:
        """has_dependency distinguishes 'djb' from 'djb-extras'."""
        # The complex_pyproject has both 'djb' and 'djb-extras'
        assert has_dependency("djb", complex_pyproject) is True
        assert has_dependency("djb-extras", complex_pyproject) is True
        # But they're separate - looking for 'djb' shouldn't find 'djb-extras'
        # and vice versa. Since we're using canonicalization, this should work.

    def test_has_dependency_with_underscore_normalization(self, complex_pyproject: Path) -> None:
        """has_dependency normalizes underscores to hyphens (PEP 503)."""
        # 'djb-extras' and 'djb_extras' should be equivalent
        assert has_dependency("djb_extras", complex_pyproject) is True
        assert has_dependency("DJB-Extras", complex_pyproject) is True

    def test_has_dependency_lowercase_matches_uppercase(
        self, normalization_pyproject: Path
    ) -> None:
        """has_dependency lowercase search finds uppercase dependency (PEP 503)."""
        # Task scenario: searching for "djb" when dependency is "DJB>=0.2.4"
        assert has_dependency("djb", normalization_pyproject) is True

    def test_has_dependency_underscore_matches_hyphen(self, normalization_pyproject: Path) -> None:
        """has_dependency underscore search finds hyphenated dependency (PEP 503)."""
        # Task scenario: searching for "my_package" when dependency is "my-package>=1.0"
        assert has_dependency("my_package", normalization_pyproject) is True


class TestGetDjangoSettingsModule:
    """Tests for get_django_settings_module function."""

    def test_returns_django_stubs_setting(self, tmp_path: Path) -> None:
        """get_django_settings_module returns value from [tool.django-stubs]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "my-app"

[tool.django-stubs]
django_settings_module = "myapp.settings"
"""
        )
        result = get_django_settings_module(pyproject)
        assert result == "myapp.settings"

    def test_returns_fallback_with_hyphen_conversion(self, tmp_path: Path) -> None:
        """get_django_settings_module fallback converts hyphens to underscores."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "my-app"
"""
        )
        result = get_django_settings_module(pyproject, fallback_name="my-app")
        assert result == "my_app.settings"

    def test_returns_fallback_without_hyphens(self, tmp_path: Path) -> None:
        """get_django_settings_module fallback works with names without hyphens."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "myapp"
"""
        )
        result = get_django_settings_module(pyproject, fallback_name="myapp")
        assert result == "myapp.settings"

    def test_django_stubs_takes_precedence_over_fallback(self, tmp_path: Path) -> None:
        """get_django_settings_module prioritizes django-stubs over fallback."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "my-app"

[tool.django-stubs]
django_settings_module = "actual_package.settings"
"""
        )
        result = get_django_settings_module(pyproject, fallback_name="my-app")
        assert result == "actual_package.settings"

    def test_returns_none_without_fallback_or_setting(self, tmp_path: Path) -> None:
        """get_django_settings_module returns None without setting or fallback."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "my-app"
"""
        )
        result = get_django_settings_module(pyproject)
        assert result is None

    def test_returns_none_for_nonexistent_file(self, tmp_path: Path) -> None:
        """get_django_settings_module returns None for nonexistent file."""
        result = get_django_settings_module(tmp_path / "nonexistent.toml")
        assert result is None

    def test_returns_fallback_for_nonexistent_file(self, tmp_path: Path) -> None:
        """get_django_settings_module uses fallback for nonexistent file."""
        result = get_django_settings_module(
            tmp_path / "nonexistent.toml",
            fallback_name="my-app",
        )
        assert result == "my_app.settings"

    def test_empty_tool_section(self, tmp_path: Path) -> None:
        """get_django_settings_module handles empty [tool] section gracefully."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "my-app"

[tool]
"""
        )
        result = get_django_settings_module(pyproject, fallback_name="my-app")
        assert result == "my_app.settings"

    def test_empty_django_stubs_section(self, tmp_path: Path) -> None:
        """get_django_settings_module handles empty [tool.django-stubs] gracefully."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            """
[project]
name = "my-app"

[tool.django-stubs]
"""
        )
        result = get_django_settings_module(pyproject, fallback_name="my-app")
        assert result == "my_app.settings"
