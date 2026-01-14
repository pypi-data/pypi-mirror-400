"""
Buildpacks module - composable Docker base images for fast deployments.

Buildpacks are layered Docker images that can be chained together:
    python:3.14-slim -> oven/bun:latest -> postgres:17-trixie -> gdal-slim-dynamic-v1

The colon (`:`) is the discriminator:
- With `:` (e.g., `python:3.14-slim`) -> Public image reference
  - If first in chain: used as-is
  - If not first: merged via Dockerfile.glue into /buildpacks/{namespace}/
- Without `:` (e.g., `gdal-slim-dynamic-v1`) -> Custom buildpack with Dockerfile.{spec}

**Dynamic buildpacks**: Specs ending in `-dynamic-v{n}` resolve their version from
pyproject.toml dependencies. For example, `gdal-slim-dynamic-v1` looks up the
`gdal` dependency version.

**Namespacing**: Public images after position 0 are isolated in /buildpacks/{namespace}/
to prevent file conflicts. The namespace is derived from the image name:
- "postgres:17-trixie" -> /buildpacks/postgres/
- "oven/bun:latest" -> /buildpacks/bun/

Environment variables for each namespace are written to /etc/buildpack-env,
which should be sourced by the application entrypoint.

Usage:
    from djb.buildpacks import RemoteBuildpackChain, LocalBuildpackChain

    # Build the full buildpack chain (remote via SSH)
    chain = RemoteBuildpackChain(
        registry="localhost:32000",
        ssh=ssh_client,
        pyproject_path=Path("pyproject.toml"),
    )
    final_image = chain.build(["python:3.14-slim", "oven/bun:latest", "gdal-slim-dynamic-v1"])

    # Build locally for development
    chain = LocalBuildpackChain(
        registry="k3d-registry.localhost:5000",
        runner=runner,
        pyproject_path=Path("pyproject.toml"),
    )
    final_image = chain.build(["python:3.14-slim", "gdal-slim-dynamic-v1"])

Exports:
    RemoteBuildpackChain - Build buildpack chains remotely via SSH
    LocalBuildpackChain - Build buildpack chains locally with Docker
    BuildpackSpec - Parsed buildpack specification dataclass
    BuildpackChainSpec - Chain of specs with composite naming
    BuildpackMeta - Metadata dataclass for buildpack specs (timeout, version resolver)
    BUILDPACK_META - Registry of buildpack specs to their metadata
    parse - Parse a buildpack spec string into BuildpackSpec
    has_version_resolver - Check if spec has a dynamic version resolver
    resolve_version - Resolve version for a dynamic buildpack spec
    get_build_timeout - Get build timeout for a buildpack spec
    BuildpackError - Exception for buildpack-related errors
    DOCKERFILES_DIR - Path to buildpack Dockerfiles
"""

from __future__ import annotations

from djb.buildpacks.constants import DOCKERFILES_DIR, BuildpackError
from djb.buildpacks.local import LocalBuildpackChain
from djb.buildpacks.metadata import (
    BUILDPACK_META,
    BuildpackMeta,
    get_build_timeout,
    has_version_resolver,
    resolve_version,
)
from djb.buildpacks.remote import RemoteBuildpackChain
from djb.buildpacks.specs import BuildpackChainSpec, BuildpackSpec, parse

__all__ = [
    "RemoteBuildpackChain",
    "LocalBuildpackChain",
    "BuildpackSpec",
    "BuildpackChainSpec",
    "BuildpackMeta",
    "BUILDPACK_META",
    "parse",
    "has_version_resolver",
    "resolve_version",
    "get_build_timeout",
    "BuildpackError",
    "DOCKERFILES_DIR",
]
