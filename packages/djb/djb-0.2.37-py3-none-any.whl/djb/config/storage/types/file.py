"""
File-based ConfigType implementations.

Each ConfigType declares its io_types - the base class handles mode interleaving.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from djb.config.storage.io.toml import (
    CoreConfigIO,
    LocalConfigIO,
    ProjectConfigIO,
    PyprojectConfigIO,
)
from djb.config.storage.types.base import ConfigType

if TYPE_CHECKING:
    from djb.config.storage.io import ConfigIO


class LocalConfigType(ConfigType):
    """Config type for local settings (.djb/local.toml)."""

    io_types = [LocalConfigIO]
    name = "LOCAL"


class ProjectConfigType(ConfigType):
    """Config type for project-level settings.

    Reads from project.toml and pyproject.toml[tool.djb].
    Writes to project.toml if it exists, otherwise pyproject.toml.
    """

    io_types = [ProjectConfigIO, PyprojectConfigIO]
    name = "PROJECT"

    def _get_write_io(self) -> "ConfigIO":
        """Get the IO for writing config values.

        If .djb/project.toml exists, writes go there.
        Otherwise, writes go to pyproject.toml[tool.djb].
        """
        mode = self._get_mode()
        project_io = ProjectConfigIO(self.config, mode_prefix=mode)
        if project_io.exists:
            return project_io
        return PyprojectConfigIO(self.config, mode_prefix=mode)


class CoreConfigType(ConfigType):
    """Config type for core defaults (djb package core.toml, read-only)."""

    io_types = [CoreConfigIO]
    name = "CORE"
    writable = False
    explicit = False
