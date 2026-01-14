"""Version resolver utilities for dynamic buildpacks.

Dynamic buildpacks derive their version from pyproject.toml dependencies.
For example, "gdal-slim-dynamic-v1" resolves its version from the "gdal"
dependency in pyproject.toml.

The "dynamic" suffix signals "this version is resolved dynamically."

Usage:
    from djb.buildpacks.resolvers import resolve_gdal_version

    version = resolve_gdal_version(pyproject_path)
    # version = "3.10" (from gdal==3.10.0 in pyproject.toml)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from djb.cli.utils.pyproject import find_pyproject_dependency

if TYPE_CHECKING:
    from packaging.specifiers import SpecifierSet


def min_version_from_specifier(specifier: "SpecifierSet") -> str:
    """Extract minimum version from a packaging.specifiers.SpecifierSet.

    Examples:
        "==3.10.0" → "3.10.0"
        ">=3.10.0,<4.0" → "3.10.0"
        "~=3.10" → "3.10"

    Args:
        specifier: A SpecifierSet from packaging.requirements.Requirement.specifier

    Returns:
        The minimum version string

    Raises:
        ValueError: If no version can be extracted
    """
    # Prefer exact or minimum bound operators
    for spec in specifier:
        if spec.operator in ("==", ">=", "~="):
            return spec.version
    # Fallback: return first version found
    for spec in specifier:
        return spec.version
    raise ValueError(f"Could not extract version from {specifier}")


def resolve_gdal_version(pyproject_path: Path) -> str:
    """Resolve GDAL version from pyproject.toml gdal dependency.

    Args:
        pyproject_path: Path to pyproject.toml

    Returns:
        GDAL version string (e.g., "3.10")

    Raises:
        ValueError: If gdal dependency not found
    """
    req = find_pyproject_dependency("gdal", pyproject_path)
    if req is None:
        raise ValueError("gdal dependency not found in pyproject.toml")
    return min_version_from_specifier(req.specifier)
