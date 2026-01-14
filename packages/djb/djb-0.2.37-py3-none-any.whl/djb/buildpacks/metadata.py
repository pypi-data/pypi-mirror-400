"""Buildpack metadata registry.

Centralizes buildpack configuration: build timeouts, version resolvers, etc.

Usage:
    from djb.buildpacks.metadata import (
        BuildpackMeta,
        BUILDPACK_META,
        has_version_resolver,
        resolve_version,
        get_build_timeout,
    )

    # Check if a spec has a dynamic version resolver
    if has_version_resolver("gdal-slim-dynamic-v1"):
        version = resolve_version("gdal-slim-dynamic-v1", pyproject_path)

    # Get build timeout for a spec
    timeout = get_build_timeout("gdal-slim-dynamic-v1")  # 1800
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from djb.buildpacks.resolvers import resolve_gdal_version

PUBLIC_IMAGE_BUILD_TIMEOUT_SECONDS = 300
DEFAULT_CUSTOM_BUILD_TIMEOUT_SECONDS = 900


@dataclass(frozen=True)
class BuildpackMeta:
    """Metadata for a buildpack spec."""

    timeout_seconds: int = DEFAULT_CUSTOM_BUILD_TIMEOUT_SECONDS
    version_resolver: Callable[[Path], str] | None = None


# Registry: buildpack spec → metadata
BUILDPACK_META: dict[str, BuildpackMeta] = {
    "gdal-slim-dynamic-v1": BuildpackMeta(
        timeout_seconds=1800,
        version_resolver=resolve_gdal_version,
    ),
}


def has_version_resolver(spec: str) -> bool:
    """Check if spec has a dynamic version resolver.

    Args:
        spec: Buildpack spec (e.g., "gdal-slim-dynamic-v1")

    Returns:
        True if spec has a registered version resolver
    """
    meta = BUILDPACK_META.get(spec)
    return meta is not None and meta.version_resolver is not None


def resolve_version(spec: str, pyproject_path: Path) -> str:
    """Resolve version for a dynamic buildpack spec.

    Args:
        spec: Buildpack spec with dynamic version (e.g., "gdal-slim-dynamic-v1")
        pyproject_path: Path to pyproject.toml

    Returns:
        Resolved version string (e.g., "3.10")

    Raises:
        KeyError: If spec has no registered resolver
        ValueError: If dependency not found in pyproject.toml
    """
    meta = BUILDPACK_META.get(spec)
    if meta is None or meta.version_resolver is None:
        raise KeyError(f"No version resolver for spec: {spec}")
    return meta.version_resolver(pyproject_path)


def get_build_timeout(spec: str) -> int:
    """Get build timeout for a buildpack spec.

    Args:
        spec: Buildpack spec (e.g., "gdal-slim-dynamic-v1")

    Returns:
        Build timeout in seconds
    """
    meta = BUILDPACK_META.get(spec)
    if meta is not None:
        return meta.timeout_seconds
    return DEFAULT_CUSTOM_BUILD_TIMEOUT_SECONDS
