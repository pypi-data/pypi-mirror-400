"""
ConfigType and ConfigIO classes for the config system.

This module provides config storage classes. Fields use these classes as
their config_storage parameter, and instances are created at resolution
time when ctx is available.

Classes:
    LocalConfigIO: For .djb/local.toml
    CoreConfigIO: For bundled core.toml (read-only)
    EnvConfigIO: For DJB_* environment variables
    DictConfigIO: For in-memory dict (CLI overrides)
    ProjectConfigIO: For .djb/project.toml
    PyprojectConfigIO: For pyproject.toml[tool.djb]
    LocalConfigType: Wraps LocalConfigIO with mode interleaving
    ProjectConfigType: Reads from project.toml + pyproject.toml
    CoreConfigType: Wraps CoreConfigIO with mode interleaving (read-only)
    DerivedConfigType: Marker for derived fields (no I/O)
"""

from djb.config.storage.io.dict import DictConfigIO
from djb.config.storage.io.env import EnvConfigIO
from djb.config.storage.io.toml import (
    CoreConfigIO,
    LocalConfigIO,
    ProjectConfigIO,
    PyprojectConfigIO,
)
from djb.config.storage.types.base import ConfigType
from djb.config.storage.types.derived import DerivedConfigType
from djb.config.storage.types.file import (
    CoreConfigType,
    LocalConfigType,
    ProjectConfigType,
)

__all__ = [
    # ConfigIO classes
    "LocalConfigIO",
    "CoreConfigIO",
    "EnvConfigIO",
    "DictConfigIO",
    "ProjectConfigIO",
    "PyprojectConfigIO",
    # ConfigType classes
    "LocalConfigType",
    "ProjectConfigType",
    "CoreConfigType",
    "DerivedConfigType",
    "ConfigType",
]
