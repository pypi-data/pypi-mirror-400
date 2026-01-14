"""Shared fixtures for djb config E2E tests.

Inherits fixtures from:
- Parent conftest.py (clean_djb_env for cache clearing)
- djb.testing.e2e (make_pyproject)
- cli/tests/e2e/fixtures (project_dir, make_config_file, make_pyproject_dir_with_git)
"""

from __future__ import annotations

# Import make_pyproject first since make_pyproject_dir_with_git depends on it
from djb.testing.e2e import make_pyproject  # noqa: F401 - re-exported fixture

from djb.cli.tests.e2e.fixtures import (  # noqa: F401 - re-exported fixtures
    make_config_file,
    make_project_with_git_repo,
    make_pyproject_dir_with_git,
    project_dir,
)
from djb.config import DjbConfig
from djb.config.storage.types import LocalConfigIO, ProjectConfigType
from djb.types import Mode


# =============================================================================
# Test helpers for creating stores with config
# =============================================================================


def make_local_config_io(make_djb_config, mode: Mode | None = None) -> LocalConfigIO:
    """Create LocalConfigIO with a test config."""
    overrides = DjbConfig(mode=mode) if mode is not None else None
    config = make_djb_config(overrides)
    return LocalConfigIO(config)


def make_project_config_type(make_djb_config, mode: Mode | None = None) -> ProjectConfigType:
    """Create ProjectConfigType with a test config."""
    overrides = DjbConfig(mode=mode) if mode is not None else None
    config = make_djb_config(overrides)
    return ProjectConfigType(config)
