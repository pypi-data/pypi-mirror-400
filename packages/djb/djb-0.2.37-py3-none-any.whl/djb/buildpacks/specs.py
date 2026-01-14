"""Buildpack spec parsing and utilities.

A buildpack spec is a string that describes either a public Docker image
or a custom buildpack:
- Public: "python:3.14-slim", "oven/bun:latest" (contains `:`)
- Custom: "gdal-slim-dynamic-v1" (no `:`, maps to Dockerfile.gdal-slim-dynamic-v1)
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from djb.buildpacks.constants import DOCKERFILES_DIR, BuildpackError


@dataclass(frozen=True)
class BuildpackSpec:
    """Parsed buildpack specification.

    Attributes:
        raw: Original spec string
        is_public: True if this is a public image (contains `:`)
        namespace: Derived namespace for public images (e.g., "bun" from "oven/bun:latest")
        dockerfile_path: Path to Dockerfile for custom buildpacks, None for public images
    """

    raw: str
    is_public: bool
    namespace: str | None
    dockerfile_path: Path | None

    def laminate_name(self, resolved_version: str | None = None) -> str:
        """Get name of laminate layer to place on top of (append) to a composite image

        Examples:
            "python:3.14-slim" -> "python3.14-slim"
            "oven/bun:1.3.5" -> "bun1.3.5"
            "gdal-slim-dynamic-v1" + "3.10" -> "gdal3.10-slim-dynamic-v1"

        Args:
            resolved_version: Version resolved from pyproject.toml for dynamic buildpacks

        Returns:
            Name of laminate layer for composite naming
        """
        if self.is_public:
            # Public image: strip registry prefix, replace : with nothing
            spec = self.raw
            if "/" in spec:
                spec = spec.split("/")[-1]
            return spec.replace(":", "")
        elif resolved_version:
            # Dynamic buildpack: insert version after base name
            # "gdal-slim-dynamic-v1" + "3.10" → "gdal3.10-slim-dynamic-v1"
            parts = self.raw.split("-", 1)
            return f"{parts[0]}{resolved_version}-{parts[1]}"
        else:
            # Static custom buildpack: use as-is
            return self.raw


class BuildpackChainSpec:
    """A chain of buildpack specs with composite name generation.

    Usage:
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim", "gdal-slim-dynamic-v1"],
            registry="localhost:32000",
        )
        chain.set_resolved_version("gdal-slim-dynamic-v1", "3.10")
        image_tag = chain.composite_name()
        # "localhost:32000/python3.14-slim-gdal3.10-slim-dynamic-v1:latest"
    """

    def __init__(
        self,
        specs: list[BuildpackSpec],
        registry: str,
    ) -> None:
        self.specs = specs
        self.registry = registry
        self._resolved_versions: dict[str, str] = {}

    @classmethod
    def from_strings(
        cls,
        spec_strings: list[str],
        registry: str,
        *,
        validate_dockerfiles: bool = True,
    ) -> "BuildpackChainSpec":
        """Create a chain from spec strings.

        Args:
            spec_strings: List of buildpack spec strings
            registry: Docker registry host
            validate_dockerfiles: If True, validate Dockerfiles exist for custom specs

        Returns:
            BuildpackChainSpec instance
        """
        specs = [parse(s, validate_dockerfile=validate_dockerfiles) for s in spec_strings]
        return cls(specs, registry)

    def set_resolved_version(self, spec_raw: str, version: str) -> None:
        """Set resolved version for a dynamic buildpack."""
        self._resolved_versions[spec_raw] = version

    def cured_image_tag(self, laminate_names: list[str] | None = None) -> str:
        """Build the cured image tag for given laminate layer names.

        Returns:
            Cured image tag (e.g., "localhost:32000/python3.14-slim-gdal3.10-slim-dynamic-v1:latest")
        """
        if laminate_names is None:
            laminate_names = [
                spec.laminate_name(self._resolved_versions.get(spec.raw)) for spec in self.specs
            ]
        return f"{self.registry}/{'-'.join(laminate_names)}:latest"

    def __iter__(self) -> Iterator[tuple[BuildpackSpec, str]]:
        """Iterate over (spec, cured_image_tag) tuples.

        Yields:
            Tuples of (BuildpackSpec, str) where the string is the cured image tag
            for the composite up to and including this spec.
        """
        segments: list[str] = []
        for spec in self.specs:
            segments.append(spec.laminate_name(self._resolved_versions.get(spec.raw)))
            yield spec, self.cured_image_tag(segments)

    def __len__(self):
        return len(self.specs)

    def __getitem__(self, index: int) -> BuildpackSpec:
        return self.specs[index]


def parse(spec: str, *, validate_dockerfile: bool = True) -> BuildpackSpec:
    """Parse a buildpack spec string into a BuildpackSpec.

    Args:
        spec: Buildpack spec string (e.g., "python:3.14-slim" or "gdal-slim-dynamic-v1")
        validate_dockerfile: If True, raise BuildpackError if custom buildpack's Dockerfile
                            doesn't exist. Set to False for parsing without validation.

    Returns:
        Parsed BuildpackSpec

    Raises:
        BuildpackError: If validate_dockerfile=True and Dockerfile not found for custom buildpack
    """
    is_public = ":" in spec

    if is_public:
        # Public image: derive namespace from image name
        # "postgres:17-trixie" → "postgres"
        # "oven/bun:latest" → "bun"
        name = spec.split(":")[0]
        namespace = name.split("/")[-1]
        return BuildpackSpec(
            raw=spec,
            is_public=True,
            namespace=namespace,
            dockerfile_path=None,
        )
    else:
        # Custom buildpack: lookup Dockerfile
        dockerfile_path = DOCKERFILES_DIR / f"Dockerfile.{spec}"
        if validate_dockerfile and not dockerfile_path.exists():
            raise BuildpackError(
                f"Dockerfile not found: {dockerfile_path}\n"
                f"Custom buildpack '{spec}' requires Dockerfile.{spec} in {DOCKERFILES_DIR}"
            )
        return BuildpackSpec(
            raw=spec,
            is_public=False,
            namespace=None,
            dockerfile_path=dockerfile_path,
        )
