"""Tests for buildpack spec parsing and utilities."""

from __future__ import annotations


import pytest

from djb.buildpacks.constants import DOCKERFILES_DIR, BuildpackError
from djb.buildpacks.specs import BuildpackChainSpec, BuildpackSpec, parse


class TestParse:
    """Tests for the parse() function."""

    def test_public_image_simple(self) -> None:
        """parse() identifies simple public images by colon."""
        spec = parse("python:3.14-slim", validate_dockerfile=False)

        assert spec.raw == "python:3.14-slim"
        assert spec.is_public is True
        assert spec.namespace == "python"
        assert spec.dockerfile_path is None

    def test_public_image_with_registry(self) -> None:
        """parse() extracts namespace from registry/org/image:tag format."""
        spec = parse("oven/bun:latest", validate_dockerfile=False)

        assert spec.raw == "oven/bun:latest"
        assert spec.is_public is True
        assert spec.namespace == "bun"
        assert spec.dockerfile_path is None

    def test_public_image_with_full_registry(self) -> None:
        """parse() extracts namespace from ghcr.io/org/image:tag format."""
        spec = parse("ghcr.io/org/myimage:v1", validate_dockerfile=False)

        assert spec.raw == "ghcr.io/org/myimage:v1"
        assert spec.is_public is True
        assert spec.namespace == "myimage"

    def test_custom_buildpack(self) -> None:
        """parse() identifies custom buildpacks without colon."""
        spec = parse("gdal-slim-dynamic-v1", validate_dockerfile=False)

        assert spec.raw == "gdal-slim-dynamic-v1"
        assert spec.is_public is False
        assert spec.namespace is None
        assert spec.dockerfile_path == DOCKERFILES_DIR / "Dockerfile.gdal-slim-dynamic-v1"

    def test_custom_buildpack_validates_dockerfile_exists(self) -> None:
        """parse() raises BuildpackError when Dockerfile doesn't exist."""
        with pytest.raises(BuildpackError, match="Dockerfile not found"):
            parse("nonexistent-buildpack-v1", validate_dockerfile=True)

    def test_custom_buildpack_skip_validation(self) -> None:
        """parse() skips Dockerfile validation when validate_dockerfile=False."""
        spec = parse("nonexistent-buildpack-v1", validate_dockerfile=False)

        assert spec.raw == "nonexistent-buildpack-v1"
        assert spec.is_public is False


class TestBuildpackSpecLayerName:
    """Tests for BuildpackSpec.layer_name()."""

    def test_public_image_removes_colon(self) -> None:
        """layer_name() removes colon from public images."""
        spec = parse("python:3.14-slim", validate_dockerfile=False)

        assert spec.laminate_name() == "python3.14-slim"

    def test_public_image_strips_registry(self) -> None:
        """layer_name() strips registry prefix from public images."""
        spec = parse("oven/bun:latest", validate_dockerfile=False)

        assert spec.laminate_name() == "bunlatest"

    def test_public_image_strips_full_registry(self) -> None:
        """layer_name() strips full registry path."""
        spec = parse("ghcr.io/org/myimage:v1", validate_dockerfile=False)

        assert spec.laminate_name() == "myimagev1"

    def test_custom_buildpack_without_version(self) -> None:
        """layer_name() returns raw spec for static custom buildpacks."""
        spec = parse("test-buildpack-v1", validate_dockerfile=False)

        assert spec.laminate_name() == "test-buildpack-v1"

    def test_custom_buildpack_with_resolved_version(self) -> None:
        """layer_name() inserts version after base name for dynamic buildpacks."""
        spec = parse("gdal-slim-dynamic-v1", validate_dockerfile=False)

        assert spec.laminate_name("3.10.0") == "gdal3.10.0-slim-dynamic-v1"

    def test_custom_buildpack_version_inserted_after_first_hyphen(self) -> None:
        """layer_name() splits on first hyphen only."""
        spec = parse("gdal-slim-dynamic-v1", validate_dockerfile=False)

        # "gdal" + "3.10" + "-" + "slim-dynamic-v1"
        assert spec.laminate_name("3.10") == "gdal3.10-slim-dynamic-v1"


class TestBuildpackChainSpec:
    """Tests for BuildpackChainSpec class."""

    def test_from_strings_creates_chain(self) -> None:
        """from_strings() creates a chain of parsed specs."""
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim", "oven/bun:latest"],
            registry="localhost:32000",
            validate_dockerfiles=False,
        )

        assert len(chain) == 2
        assert chain[0].raw == "python:3.14-slim"
        assert chain[1].raw == "oven/bun:latest"

    def test_from_strings_validates_dockerfiles(self) -> None:
        """from_strings() validates Dockerfiles by default."""
        with pytest.raises(BuildpackError, match="Dockerfile not found"):
            BuildpackChainSpec.from_strings(
                ["nonexistent-buildpack-v1"],
                registry="localhost:32000",
                validate_dockerfiles=True,
            )

    def test_cured_image_tag_single_public(self) -> None:
        """cured_image_tag() generates tag for single public image."""
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim"],
            registry="localhost:32000",
            validate_dockerfiles=False,
        )

        assert chain.cured_image_tag() == "localhost:32000/python3.14-slim:latest"

    def test_cured_image_tag_multiple_public(self) -> None:
        """cured_image_tag() joins multiple layer names with hyphen."""
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim", "oven/bun:latest", "postgres:17-trixie"],
            registry="localhost:32000",
            validate_dockerfiles=False,
        )

        assert (
            chain.cured_image_tag()
            == "localhost:32000/python3.14-slim-bunlatest-postgres17-trixie:latest"
        )

    def test_cured_image_tag_with_resolved_version(self) -> None:
        """cured_image_tag() includes resolved versions for dynamic buildpacks."""
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim", "gdal-slim-dynamic-v1"],
            registry="localhost:32000",
            validate_dockerfiles=False,
        )
        chain.set_resolved_version("gdal-slim-dynamic-v1", "3.10.0")

        assert (
            chain.cured_image_tag()
            == "localhost:32000/python3.14-slim-gdal3.10.0-slim-dynamic-v1:latest"
        )

    def test_iteration(self) -> None:
        """BuildpackChainSpec iterates (spec, cured_image_tag) tuples."""
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim", "oven/bun:latest"],
            registry="localhost:32000",
            validate_dockerfiles=False,
        )

        items = list(chain)
        assert len(items) == 2

        spec0, tag0 = items[0]
        assert isinstance(spec0, BuildpackSpec)
        assert spec0.raw == "python:3.14-slim"
        assert tag0 == "localhost:32000/python3.14-slim:latest"

        spec1, tag1 = items[1]
        assert isinstance(spec1, BuildpackSpec)
        assert spec1.raw == "oven/bun:latest"
        assert tag1 == "localhost:32000/python3.14-slim-bunlatest:latest"

    def test_iteration_with_resolved_version(self) -> None:
        """Iteration includes resolved versions in cured_image_tag."""
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim", "gdal-slim-dynamic-v1"],
            registry="localhost:32000",
            validate_dockerfiles=False,
        )
        chain.set_resolved_version("gdal-slim-dynamic-v1", "3.10.0")

        items = list(chain)
        _, tag1 = items[1]
        assert tag1 == "localhost:32000/python3.14-slim-gdal3.10.0-slim-dynamic-v1:latest"

    def test_indexing(self) -> None:
        """BuildpackChainSpec supports indexing."""
        chain = BuildpackChainSpec.from_strings(
            ["python:3.14-slim", "oven/bun:latest"],
            registry="localhost:32000",
            validate_dockerfiles=False,
        )

        assert chain[0].raw == "python:3.14-slim"
        assert chain[1].raw == "oven/bun:latest"


class TestBuildpackSpecFrozen:
    """Tests for BuildpackSpec immutability."""

    def test_spec_is_frozen(self) -> None:
        """BuildpackSpec is immutable (frozen dataclass)."""
        spec = parse("python:3.14-slim", validate_dockerfile=False)

        with pytest.raises(AttributeError):
            spec.raw = "modified"  # type: ignore[misc]
