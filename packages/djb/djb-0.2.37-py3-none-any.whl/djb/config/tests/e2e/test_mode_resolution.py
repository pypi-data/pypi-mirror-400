"""E2E tests for mode-aware resolution of config fields."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from djb.config import DjbConfig
from djb.config.config import get_djb_config
from djb.config.resolution import build_resolution_chain
from djb.types import Mode

pytestmark = pytest.mark.e2e_marker


class TestModeAwareResolution:
    """E2E tests for mode-aware resolution of regular fields."""

    def test_regular_field_uses_mode_section(
        self,
        project_dir: Path,
        make_config_file: Callable[..., Path],
    ):
        """Regular fields should pick up values from mode sections.

        When running in staging mode, a value set in [staging] section
        should override the base value.
        """
        make_config_file(
            """
project_name = "production-app"

[staging]
project_name = "staging-app"
""",
            config_type="local",
        )

        # Use get_djb_config to actually read from files
        config = get_djb_config(DjbConfig(project_dir=project_dir, mode=Mode.STAGING), env={})
        chain = build_resolution_chain(config)

        value, _ = chain.get("project_name")
        assert value == "staging-app"

    def test_regular_field_uses_base_in_production_mode(
        self,
        project_dir: Path,
        make_config_file: Callable[..., Path],
    ):
        """In production mode, base values are used (mode sections are ignored)."""
        make_config_file(
            """
project_name = "production-app"

[staging]
project_name = "staging-app"
""",
            config_type="local",
        )

        # Use get_djb_config to actually read from files
        config = get_djb_config(DjbConfig(project_dir=project_dir, mode=Mode.PRODUCTION), env={})
        chain = build_resolution_chain(config)

        value, _ = chain.get("project_name")
        assert value == "production-app"
