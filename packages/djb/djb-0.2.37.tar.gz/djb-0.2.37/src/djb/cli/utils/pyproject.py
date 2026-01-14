"""
Pyproject TOML parsing utilities.

Provides common functions for loading and parsing pyproject.toml files,
specifically for extracting dependency information.

Functions:
    load_pyproject: Load and parse a pyproject.toml file
    collect_all_dependencies: Collect dependencies from regular + optional deps
    find_dependency: Find a dependency by name, returns parsed Requirement
    find_dependency_string: Find a dependency by name, returns raw string
    has_dependency: Check if a package is a dependency (in regular deps only)
    get_django_settings_module: Get Django settings module from pyproject.toml
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from djb.config.storage.utils import load_toml_mapping
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

if TYPE_CHECKING:
    from djb.core.cmd_runner import CmdRunner

# Timeout for tool availability checks (same as TOOL_CHECK_TIMEOUT in utils/__init__.py)
# Defined locally to avoid circular import since utils/__init__.py imports from this module
_TOOL_CHECK_TIMEOUT = 10


def load_pyproject(pyproject_path: Path) -> dict | None:
    """Load and parse a pyproject.toml file.

    Args:
        pyproject_path: Path to the pyproject.toml file.

    Returns:
        Parsed TOML data as a dict, or None if the file doesn't exist.

    Raises:
        tomlkit.exceptions.ParseError: If the file exists but contains invalid TOML.
    """
    if not pyproject_path.exists():
        return None

    return load_toml_mapping(pyproject_path)


def collect_all_dependencies(data: dict) -> list[str]:
    """Collect all dependencies from a pyproject.toml data dict.

    Collects from both [project.dependencies] and [project.optional-dependencies].

    Args:
        data: Parsed pyproject.toml data.

    Returns:
        List of dependency strings (e.g., ["django>=4.0", "djb[dev]>=0.2.6"]).
    """
    all_deps: list[str] = []

    if "project" not in data:
        return all_deps

    project = data["project"]

    if "dependencies" in project:
        deps = project["dependencies"]
        if isinstance(deps, list):
            all_deps.extend(deps)

    if "optional-dependencies" in project:
        for group_deps in project["optional-dependencies"].values():
            if isinstance(group_deps, list):
                all_deps.extend(group_deps)

    return all_deps


def find_pyproject_dependency(package_name: str, pyproject_path: Path) -> Requirement | None:
    """Find a dependency by name, returning the parsed Requirement object.

    Uses proper TOML parsing and packaging.requirements.Requirement
    for correct PEP 508 handling (version specifiers, extras, markers).

    Package names are normalized using PEP 503 canonicalization, so
    "Django", "django", and "DJANGO" all match the same dependency.

    Args:
        package_name: Name of the package to find.
        pyproject_path: Path to the pyproject.toml file.

    Returns:
        Parsed Requirement object if found, None otherwise.
    """
    data = load_pyproject(pyproject_path)
    if data is None:
        return None

    all_deps = collect_all_dependencies(data)
    normalized_name = canonicalize_name(package_name)

    for dep in all_deps:
        try:
            req = Requirement(dep)
            if canonicalize_name(req.name) == normalized_name:
                return req
        except InvalidRequirement:
            # Skip malformed dependency strings
            continue

    return None


def find_dependency_string(package_name: str, pyproject_path: Path) -> str | None:
    """Find a dependency by name, returning the raw dependency string.

    Uses proper TOML parsing and packaging.requirements.Requirement
    for correct PEP 508 handling.

    Args:
        package_name: Name of the package to find.
        pyproject_path: Path to the pyproject.toml file.

    Returns:
        The full dependency string (e.g., 'djb[dev]>=0.2.3; python_version >= "3.10"')
        or None if not found.
    """
    data = load_pyproject(pyproject_path)
    if data is None:
        return None

    all_deps = collect_all_dependencies(data)
    normalized_name = canonicalize_name(package_name)

    for dep in all_deps:
        try:
            req = Requirement(dep)
            if canonicalize_name(req.name) == normalized_name:
                return dep
        except InvalidRequirement:
            # Skip malformed dependency strings
            continue

    return None


def has_dependency(
    package_name: str,
    pyproject_path: Path,
    *,
    include_optional: bool = False,
) -> bool:
    """Check if a package is listed as a dependency.

    Uses proper TOML parsing and packaging.requirements.Requirement
    for correct PEP 508 handling. Package names are normalized using
    PEP 503 canonicalization.

    Args:
        package_name: Name of the package to check.
        pyproject_path: Path to the pyproject.toml file.
        include_optional: If True, also check optional-dependencies.
                          If False (default), only check regular dependencies.

    Returns:
        True if the package is found, False otherwise.

    Raises:
        tomlkit.exceptions.ParseError: If the file contains invalid TOML.
    """
    data = load_pyproject(pyproject_path)
    if data is None:
        return False

    if "project" not in data:
        return False

    project = data["project"]
    normalized_name = canonicalize_name(package_name)

    # Check regular dependencies
    if "dependencies" in project:
        deps = project["dependencies"]
        if isinstance(deps, list):
            for dep in deps:
                try:
                    req = Requirement(dep)
                    if canonicalize_name(req.name) == normalized_name:
                        return True
                except InvalidRequirement:
                    continue

    # Optionally check optional dependencies
    if include_optional and "optional-dependencies" in project:
        for group_deps in project["optional-dependencies"].values():
            if isinstance(group_deps, list):
                for dep in group_deps:
                    try:
                        req = Requirement(dep)
                        if canonicalize_name(req.name) == normalized_name:
                            return True
                    except InvalidRequirement:
                        continue

    return False


def get_dependency_groups(pyproject_path: Path) -> list[str]:
    """Get list of dependency group names from pyproject.toml.

    Looks for [dependency-groups] section (PEP 735 format).

    Args:
        pyproject_path: Path to the pyproject.toml file.

    Returns:
        List of dependency group names (e.g., ["geo", "dev"]).
        Returns empty list if no groups are defined.
    """
    data = load_pyproject(pyproject_path)
    if data is None:
        return []

    groups = data.get("dependency-groups", {})
    return list(groups.keys())


def get_django_settings_module(
    pyproject_path: Path,
    fallback_name: str | None = None,
) -> str | None:
    """Get Django settings module from pyproject.toml.

    Looks for [tool.django-stubs].django_settings_module first.
    Falls back to converting fallback_name (replacing hyphens with underscores).

    Args:
        pyproject_path: Path to the pyproject.toml file.
        fallback_name: Name to use for fallback (e.g., project_name).
                       Hyphens are converted to underscores.

    Returns:
        Django settings module string (e.g., "beachresort25.settings"),
        or None if not found and no fallback provided.
    """
    data = load_pyproject(pyproject_path)
    if data is not None:
        module = data.get("tool", {}).get("django-stubs", {}).get("django_settings_module")
        if module:
            return module

    if fallback_name:
        package_name = fallback_name.replace("-", "_")
        return f"{package_name}.settings"

    return None


def has_pytest_cov(runner: CmdRunner, project_root: Path) -> bool:
    """Check if pytest-cov is available in the project's environment.

    Args:
        runner: CmdRunner instance for executing commands.
        project_root: Root directory of the project.

    Returns:
        True if pytest-cov is available, False otherwise.
    """
    return runner.check(
        ["uv", "run", "python", "-c", "import pytest_cov"],
        cwd=project_root,
        timeout=_TOOL_CHECK_TIMEOUT,
    )


def has_pytest_xdist(runner: CmdRunner, project_root: Path) -> bool:
    """Check if pytest-xdist is available in the project's environment.

    Args:
        runner: CmdRunner instance for executing commands.
        project_root: Root directory of the project.

    Returns:
        True if pytest-xdist is available, False otherwise.
    """
    return runner.check(
        ["uv", "run", "python", "-c", "import xdist"],
        cwd=project_root,
        timeout=_TOOL_CHECK_TIMEOUT,
    )
