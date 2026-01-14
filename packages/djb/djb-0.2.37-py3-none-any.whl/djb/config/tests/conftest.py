"""
Shared test fixtures for djb config tests.

See __init__.py for the full list of available fixtures and utilities.

Auto-enabled fixtures (applied to all tests automatically):
    clean_djb_env - Ensures a clean environment by removing DJB_* env vars

Factory fixtures:
    make_config_file - Factory for creating config files in .djb directory
    mock_cmd_runner - Mock for CmdRunner methods (provides .run)
"""

from __future__ import annotations

import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from djb.config.config import DjbConfig

import pytest

from djb.config.storage.utils import save_toml_mapping

from djb.config.storage.base import ConfigStore, Provenance
from djb.testing import mock_cli_ctx, mock_cmd_runner  # noqa: F401 - exported fixtures
from djb.testing.e2e import make_cli_ctx, make_djb_config  # noqa: F401 - exported fixtures


# =============================================================================
# Test Helpers for Provenance
# =============================================================================


class MockConfigIO(ConfigStore):
    """Mock ConfigStore for testing provenance with explicit/derived property.

    This is a minimal ConfigStore implementation for testing. It doesn't
    perform any real I/O but satisfies the ConfigStore interface.
    """

    def __init__(self, name: str, *, explicit: bool = True, writable: bool = True) -> None:
        # Don't call super().__init__() - we don't need a real config
        self._name = name
        self._explicit = explicit
        self._writable = writable

    @property
    def name(self) -> str:  # type: ignore[override]
        return self._name

    @property
    def explicit(self) -> bool:  # type: ignore[override]
        return self._explicit

    @property
    def writable(self) -> bool:  # type: ignore[override]
        return self._writable

    def get(self, key: str) -> tuple[Any, Provenance | None]:
        return None, None

    def has(self, key: str) -> bool:
        return False

    def get_io(self) -> ConfigStore:
        return self


def explicit_provenance() -> Provenance:
    """Create a provenance tuple representing an explicit source."""
    return (MockConfigIO("explicit_io", explicit=True),)


def derived_provenance() -> Provenance:
    """Create a provenance tuple representing a derived source."""
    return (MockConfigIO("derived_io", explicit=False),)


class MockConfigStore(ConfigStore):
    """Mock ConfigStore for testing acquire() with config_store_factories.

    Unlike MockConfigIO (for provenance testing), this store returns actual
    values and is used to test field acquisition from external sources.
    """

    name = "mock store"
    writable = False

    def __init__(self, key: str, value: str | None, config: "DjbConfig") -> None:
        super().__init__(config)
        self._key = key
        self._value = value

    def has(self, key: str) -> bool:
        return key == self._key and self._value is not None

    def get(self, key: str) -> tuple[str | None, Provenance | None]:
        if key == self._key:
            return (self._value, None)
        return (None, None)

    def get_io(self) -> "MockConfigStore":
        return self


def mock_store_factory(key: str, value: str | None):
    """Create a factory that returns MockConfigStore with given key/value."""
    return lambda config: MockConfigStore(key, value, config)


# Environment variables that may be set by CLI test fixtures
_DJB_ENV_VARS = [
    "DJB_PROJECT_DIR",
    "DJB_PROJECT_NAME",
    "DJB_NAME",
    "DJB_EMAIL",
    "DJB_MODE",
    "DJB_PLATFORM",
    "DJB_HOSTNAME",
]


@pytest.fixture(autouse=True)
def clean_djb_env() -> Generator[None, None, None]:
    """Ensure a clean environment for config tests.

    This fixture:
    - Removes all DJB_* environment variables before each test
    - Restores the original env state afterward
    """
    old_env = {k: os.environ.get(k) for k in _DJB_ENV_VARS}
    for k in _DJB_ENV_VARS:
        os.environ.pop(k, None)
    try:
        yield
    finally:
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture
def make_config_file(tmp_path: Path) -> Callable[..., Path]:
    """Factory for creating config files in .djb directory.

    Returns a factory function that creates config files with the given content.

    Pytest:
        Uses pytest's `tmp_path` fixture internally, so files are created in the
        same temporary directory available to the test function.

    Args:
        content: Dict or TOML string content to write to the config file
        config_type: Either "local" or "project" (default: "local")

    Returns:
        Path to the created config file

    Usage:
        def test_something(tmp_path, make_config_file):
            # Pass a dict (recommended):
            config_path = make_config_file({"name": "John", "email": "john@example.com"})
            # Creates {tmp_path}/.djb/local.toml

            # For project config:
            config_path = make_config_file({"seed_command": "myapp.cli:seed"}, config_type="project")
            # Creates {tmp_path}/.djb/project.toml

            # You can also pass a TOML string:
            config_path = make_config_file('name = "John"')
    """
    config_dir = tmp_path / ".djb"

    def _create(
        content: str | dict,
        config_type: Literal["local", "project"] = "local",
    ) -> Path:
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / f"{config_type}.toml"

        if isinstance(content, dict):
            save_toml_mapping(config_file, content)
        else:
            config_file.write_text(content)

        return config_file

    return _create
