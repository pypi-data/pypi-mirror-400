"""
TOML-based ConfigIO implementations.

Provides ConfigIO subclasses for TOML config files:
- TomlConfigIO: Base class with root + relative path + optional prefix
- LocalConfigIO: .djb/local.toml
- ProjectConfigIO: .djb/project.toml
- PyprojectConfigIO: pyproject.toml[tool.djb]
- CoreConfigIO: Bundled core.toml (read-only)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomlkit

from djb.config.storage.io.base import ConfigIO, ConfigRoot
from djb.config.storage.utils import load_toml_mapping, save_toml_mapping

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase


class TomlConfigIO(ConfigIO):
    """Base class for TOML file I/O.

    Handles:
    - Path resolution via root + relative_path
    - Path composition via base_prefix / mode_prefix / key
    - Mode-based sections (development, staging)
    """

    # Subclasses should set these class attributes
    relative_path: Path | None = Path("")  # Override in subclass

    # DEPRECATED: Use base_prefix instead. Will be removed after migration.
    prefix: str | None = None  # e.g., "tool.djb" for pyproject.toml

    def __init__(
        self,
        config: "DjbConfigBase",
        *,
        mode_prefix: str | None = None,
    ):
        """Initialize with config reference.

        Args:
            config: DjbConfig instance (may be partially resolved during bootstrap).
            mode_prefix: Mode prefix for path composition (e.g., "staging").
        """
        super().__init__(config, mode_prefix=mode_prefix)

    @property
    def path(self) -> Path:
        """Get the full file path using stored project_root."""
        return self.resolve_path()

    @property
    def exists(self) -> bool:
        """Whether the file exists."""
        return self.path.exists()

    # =========================================================================
    # Raw data loading (for base class navigation)
    # =========================================================================

    def _load_raw_data(self) -> tomlkit.TOMLDocument:
        """Load raw TOML file (no navigation).

        Returns the entire TOML file contents as a TOMLDocument,
        preserving comments and key ordering. Base class handles
        all navigation via navigate_config_path().
        """
        path = self.resolve_path()
        if not path.exists():
            return tomlkit.document()
        return load_toml_mapping(path)

    # =========================================================================
    # Raw I/O - only thing IOs need to implement
    # =========================================================================

    # _load_raw_data() - defined above
    # _write_raw_data() - defined below

    def _write_raw_data(self, data: tomlkit.TOMLDocument | dict[str, Any]) -> None:
        """Write raw data to TOML file.

        Accepts both TOMLDocument (preserves comments/ordering) and plain dict.
        """
        file_path = self.resolve_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        save_toml_mapping(file_path, data)

    # Everything else inherited from base class:
    # - load() via _load_raw_data() + navigate_read()
    # - save() via _load_raw_data() + navigate_write() + _write_raw_data()
    # - has() via _load_raw_data() + navigate_read()
    # - _get_value() via _load_raw_data() + navigate_read()
    # - _set_value() via navigate_write() + _write_raw_data()
    # - _delete_value() via navigate_write() + _write_raw_data()


class LocalConfigIO(TomlConfigIO):
    """Config I/O for .djb/local.toml (user-specific, gitignored)."""

    root = ConfigRoot.PROJECT
    relative_path = Path(".djb/local.toml")
    name = "local.toml"


class ProjectConfigIO(TomlConfigIO):
    """Config I/O for .djb/project.toml (project settings, committed)."""

    root = ConfigRoot.PROJECT
    relative_path = Path(".djb/project.toml")
    name = "project.toml"


class PyprojectConfigIO(TomlConfigIO):
    """Config I/O for pyproject.toml[tool.djb] section."""

    root = ConfigRoot.PROJECT
    relative_path = Path("pyproject.toml")
    base_prefix = "tool.djb"
    name = "pyproject.toml[tool.djb]"

    # DEPRECATED: Use base_prefix instead
    prefix = "tool.djb"


class CoreConfigIO(TomlConfigIO):
    """Config I/O for bundled core.toml (djb defaults, read-only)."""

    root = ConfigRoot.PACKAGE
    relative_path = Path("core.toml")
    name = "core.toml"
    writable = False
    explicit = False

    # Write methods inherited from base class will check writable=False and raise
