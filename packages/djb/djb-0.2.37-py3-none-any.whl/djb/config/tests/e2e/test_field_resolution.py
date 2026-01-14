"""E2E tests for ConfigFieldABC.resolve() method."""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.config.config import DjbConfig, get_djb_config
from djb.config.field import ConfigFieldABC, StringField

pytestmark = pytest.mark.e2e_marker


class TestConfigFieldABCResolve:
    """Tests for ConfigFieldABC.resolve() method."""

    def test_resolves_from_configs(self, project_dir: Path, make_config_file):
        """resolve() returns value from config layers with provenance."""
        field = StringField()
        field.field_name = "name"

        make_config_file({"name": "John"})
        # Use get_djb_config to actually read from files
        config = get_djb_config(DjbConfig(project_dir=project_dir), env={})

        value, provenance = field.resolve(config, env={})
        assert value == "John"
        assert provenance is not None
        assert len(provenance) >= 1

    def test_resolves_from_env(self, project_dir: Path):
        """resolve() returns value from env layer with env_key."""
        field = StringField()
        field.field_name = "email"

        # Use get_djb_config to actually read from files
        config = get_djb_config(DjbConfig(project_dir=project_dir), env={})

        value, provenance = field.resolve(config, env={"DJB_EMAIL": "test@example.com"})
        assert value == "test@example.com"
        assert provenance is not None

    def test_resolves_to_default(self, project_dir: Path):
        """resolve() returns default with no provenance."""
        field = StringField(default="default-value")
        field.field_name = "name"

        # Use get_djb_config to actually read from files (no name in config)
        config = get_djb_config(DjbConfig(project_dir=project_dir), env={})

        value, provenance = field.resolve(config, env={})
        assert value == "default-value"
        assert provenance is None

    def test_resolves_to_none_no_default(self, project_dir: Path):
        """resolve() returns (None, None) when no value and no default."""
        field = StringField()
        field.field_name = "optional"

        config = get_djb_config(DjbConfig(project_dir=project_dir), env={})

        value, provenance = field.resolve(config, env={})
        assert value is None
        assert provenance is None

    def test_applies_normalizer(self, project_dir: Path, make_config_file):
        """resolve() applies normalize() to resolved value."""

        class LowercaseField(ConfigFieldABC):
            def normalize(self, value):
                return value.lower() if isinstance(value, str) else value

        field = LowercaseField()
        field.field_name = "name"

        make_config_file({"name": "JOHN"})
        config = get_djb_config(DjbConfig(project_dir=project_dir), env={})

        value, provenance = field.resolve(config, env={})
        assert value == "john"
        assert provenance is not None

    def test_respects_priority(self, project_dir: Path, make_config_file):
        """resolve() respects override > env > local > project priority."""
        field = StringField()
        field.field_name = "name"

        make_config_file({"name": "local-value"})
        make_config_file({"name": "project-value"}, config_type="project")
        config = get_djb_config(DjbConfig(project_dir=project_dir), env={})

        # Env beats config
        value, provenance = field.resolve(config, env={"DJB_NAME": "env-value"})
        assert value == "env-value"
        assert provenance is not None
