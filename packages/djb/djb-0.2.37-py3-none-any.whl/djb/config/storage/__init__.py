"""
Config storage - Unified interface for config sources.

This package provides the ConfigStore protocol at every layer:

ConfigStore interface:
    ConfigStore: Protocol for all config layers
    Provenance: Tuple of ConfigStore instances (routing path)

    ConfigIO (single source I/O):
    - ConfigIO: ABC for single-source I/O
    - ConfigRoot: Enum for path resolution (PROJECT, PACKAGE, HOME)
    - TomlConfigIO, LocalConfigIO, ProjectConfigIO, PyprojectConfigIO, CoreConfigIO
    - EnvConfigIO, DictConfigIO
    - ExternalConfigIO, GitConfigIO, CwdPathConfigIO, CwdNameConfigIO, PyprojectNameConfigIO

    ConfigType (multi-source wrapper):
    - ConfigType: ABC for config categories (only needed for multi-source like PROJECT)
    - ProjectConfigType: Reads from project.toml + pyproject.toml[tool.djb]
    - DerivedConfigType: Marker for derived fields (no I/O)

Note: Fields use classes (not instances) for config_storage. Instances are
created at resolution time when config is available.
"""

# ===========================================================================
# ConfigStore protocol and Provenance type
# ===========================================================================
from djb.config.storage.base import ConfigStore, Provenance

# ===========================================================================
# ConfigIO implementations (single source I/O)
# ===========================================================================
from djb.config.storage.io import (
    # Base
    ConfigIO,
    ConfigRoot,
    # TOML-based
    TomlConfigIO,
    LocalConfigIO,
    ProjectConfigIO,
    PyprojectConfigIO,
    CoreConfigIO,
    # Transient
    EnvConfigIO,
    DictConfigIO,
    # External
    ExternalConfigIO,
    GitConfigIO,
    CwdPathConfigIO,
    CwdNameConfigIO,
    PyprojectNameConfigIO,
)

# ===========================================================================
# ConfigType implementations
# ===========================================================================
from djb.config.storage.types import (
    # Base type (for multi-source wrappers)
    ConfigType,
    # Types for instantiation
    LocalConfigType,
    ProjectConfigType,
    CoreConfigType,
    DerivedConfigType,
)

from djb.config.storage.utils import (
    deep_merge,
    navigate_config_path,
    get_config_dir,
)

__all__ = [
    # Protocol and Provenance
    "ConfigStore",
    "Provenance",
    # ConfigIO (single source I/O)
    "ConfigIO",
    "ConfigRoot",
    "TomlConfigIO",
    "LocalConfigIO",
    "ProjectConfigIO",
    "PyprojectConfigIO",
    "CoreConfigIO",
    "EnvConfigIO",
    "DictConfigIO",
    "ExternalConfigIO",
    "GitConfigIO",
    "CwdPathConfigIO",
    "CwdNameConfigIO",
    "PyprojectNameConfigIO",
    # ConfigType (for multi-source wrappers)
    "ConfigType",
    "LocalConfigType",
    "ProjectConfigType",
    "CoreConfigType",
    "DerivedConfigType",
    # Utilities
    "deep_merge",
    "navigate_config_path",
    "get_config_dir",
]
