"""
ConfigIO implementations - Single source I/O for the config system.

Exports:
    ConfigIO: Abstract base class for single-source I/O
    ConfigRoot: Enum for path resolution (PROJECT, PACKAGE, HOME)

    TOML-based:
    - TomlConfigIO: Base class for TOML file I/O
    - LocalConfigIO: .djb/local.toml
    - ProjectConfigIO: .djb/project.toml
    - PyprojectConfigIO: pyproject.toml[tool.djb]
    - CoreConfigIO: Bundled core.toml (read-only)

    Transient:
    - EnvConfigIO: Environment variables with DJB_ prefix
    - DictConfigIO: In-memory dict (CLI/runtime overrides)

    External:
    - ExternalConfigIO: Base for external sources (read-only by default)
    - GitConfigIO: Reads/writes git config (user.name, user.email)
    - CwdPathConfigIO: Infers project_dir from cwd (read-only)
    - CwdNameConfigIO: Infers project_name from directory name (read-only)
    - PyprojectNameConfigIO: Reads project name from pyproject.toml [project].name (read-only)
"""

from djb.config.storage.io.base import ConfigIO, ConfigRoot
from djb.config.storage.io.dict import DictConfigIO
from djb.config.storage.io.env import EnvConfigIO
from djb.config.storage.io.external import (
    CwdNameConfigIO,
    CwdPathConfigIO,
    ExternalConfigIO,
    GitConfigIO,
    PyprojectNameConfigIO,
)
from djb.config.storage.io.toml import (
    CoreConfigIO,
    LocalConfigIO,
    ProjectConfigIO,
    PyprojectConfigIO,
    TomlConfigIO,
)

__all__ = [
    # Base
    "ConfigIO",
    "ConfigRoot",
    # TOML-based
    "TomlConfigIO",
    "LocalConfigIO",
    "ProjectConfigIO",
    "PyprojectConfigIO",
    "CoreConfigIO",
    # Transient
    "EnvConfigIO",
    "DictConfigIO",
    # External
    "ExternalConfigIO",
    "GitConfigIO",
    "CwdPathConfigIO",
    "CwdNameConfigIO",
    "PyprojectNameConfigIO",
]
