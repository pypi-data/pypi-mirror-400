"""E2E tests for ProjectConfigType write behavior.

ProjectConfigType has fallback write logic:
- If .djb/project.toml exists, writes go there
- Otherwise, writes fall back to pyproject.toml[tool.djb]

This enables projects to start with just pyproject.toml and migrate
to project.toml when they need a dedicated space.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from djb.config.storage.utils import load_toml_mapping
from djb.types import Mode

from .conftest import make_project_config_type

pytestmark = pytest.mark.e2e_marker


class TestProjectConfigTypeWriteLocation:
    """Tests for ProjectConfigType write location fallback logic.

    The key behavior tested:
    - get_io() returns ProjectConfigIO (project.toml) when it exists
    - get_io() returns PyprojectConfigIO (pyproject.toml) when project.toml doesn't exist
    """

    def test_writes_to_project_toml_when_exists(
        self,
        project_dir: Path,
        make_config_file: Callable[..., Path],
        make_djb_config,
    ):
        """When project.toml exists, writes target project.toml."""
        make_config_file({}, config_type="project")

        write_io = make_project_config_type(make_djb_config).get_io()

        assert write_io.resolve_path() == project_dir / ".djb" / "project.toml"

    def test_falls_back_to_pyproject_when_project_toml_missing(
        self,
        project_dir: Path,
        make_djb_config,
    ):
        """When project.toml doesn't exist, writes target pyproject.toml."""
        write_io = make_project_config_type(make_djb_config).get_io()

        assert write_io.resolve_path() == project_dir / "pyproject.toml"


class TestProjectConfigTypeNestedWrites:
    """Tests for nested field prefix writes with the fallback logic.

    These tests verify that dotted keys (e.g., "hetzner.eu.server_type")
    work correctly with both project.toml and pyproject.toml destinations.
    """

    def test_nested_write_to_project_toml(
        self,
        project_dir: Path,
        make_config_file: Callable[..., Path],
        make_djb_config,
    ):
        """Nested writes create proper TOML structure in project.toml."""
        make_config_file({}, config_type="project")

        # Use production mode to avoid mode-prefixed sections
        make_project_config_type(make_djb_config, mode=Mode.PRODUCTION).set(
            "hetzner.eu.server_type", "cx32"
        )

        # Verify raw TOML structure: [hetzner.eu] section with server_type key
        data = load_toml_mapping(project_dir / ".djb" / "project.toml")
        assert data["hetzner"]["eu"]["server_type"] == "cx32"  # type: ignore[index]  # tomlkit stub

    def test_nested_write_to_pyproject(
        self,
        project_dir: Path,
        make_djb_config,
    ):
        """Nested writes go to pyproject.toml[tool.djb] when project.toml is absent."""
        # Use production mode to avoid mode-prefixed sections
        make_project_config_type(make_djb_config, mode=Mode.PRODUCTION).set(
            "hetzner.eu.server_type", "cx32"
        )

        # Verify via config layer (which handles tool.djb navigation)
        value, _ = make_project_config_type(make_djb_config, mode=Mode.PRODUCTION).get(
            "hetzner.eu.server_type"
        )
        assert value == "cx32"

        # Also verify raw TOML structure
        data = load_toml_mapping(project_dir / "pyproject.toml")
        assert data["tool"]["djb"]["hetzner"]["eu"]["server_type"] == "cx32"  # type: ignore[index]  # tomlkit stub

    def test_mode_nested_write_to_project_toml(
        self,
        project_dir: Path,
        make_config_file: Callable[..., Path],
        make_djb_config,
    ):
        """Mode + nested writes create proper TOML structure in project.toml."""
        make_config_file({}, config_type="project")

        make_project_config_type(make_djb_config, mode=Mode.STAGING).set(
            "hetzner.eu.server_type", "cx21"
        )

        # Verify raw TOML structure: [staging.hetzner.eu] section
        data = load_toml_mapping(project_dir / ".djb" / "project.toml")
        assert data["staging"]["hetzner"]["eu"]["server_type"] == "cx21"  # type: ignore[index]  # tomlkit stub

    def test_mode_nested_write_to_pyproject(
        self,
        project_dir: Path,
        make_djb_config,
    ):
        """Mode + nested writes go to pyproject.toml when project.toml is absent."""
        make_project_config_type(make_djb_config, mode=Mode.STAGING).set(
            "hetzner.eu.server_type", "cx21"
        )

        # Verify via config layer
        value, _ = make_project_config_type(make_djb_config, mode=Mode.STAGING).get(
            "hetzner.eu.server_type"
        )
        assert value == "cx21"

        # Also verify raw TOML structure
        data = load_toml_mapping(project_dir / "pyproject.toml")
        assert data["tool"]["djb"]["staging"]["hetzner"]["eu"]["server_type"] == "cx21"  # type: ignore[index]  # tomlkit stub


class TestProjectConfigTypeDelete:
    """Tests for delete behavior with nested fields."""

    def test_delete_cleans_up_empty_parent_sections(
        self,
        make_config_file: Callable[..., Path],
        make_djb_config,
    ):
        """Deleting a nested value removes empty parent sections."""
        make_config_file({}, config_type="project")

        # Create nested structure
        make_project_config_type(make_djb_config).set("hetzner.eu.server_type", "cx32")

        # Delete the value
        make_project_config_type(make_djb_config).delete("hetzner.eu.server_type")

        # Verify the value and empty parents are gone
        config = make_project_config_type(make_djb_config).load()
        assert "hetzner" not in config
