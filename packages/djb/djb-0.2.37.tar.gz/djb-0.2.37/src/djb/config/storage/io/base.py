"""
ConfigIO abstract base class and ConfigRoot enum.

ConfigIO is the lowest layer in the config system - it talks directly
to a single source (TOML file, environment variables, in-memory dict).

ConfigRoot determines how relative paths are resolved:
- PROJECT: Relative to project root
- PACKAGE: Relative to djb package (for core.toml)
- HOME: Relative to user's home directory (future)
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from djb.config.storage.base import ConfigStore
from djb.config.storage.utils import insert_key_ordered, navigate_config_path

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase
    from djb.config.storage.base import Provenance

# Production mode values live at root level, not under a [production] section
PRODUCTION_MODE = "production"


class ConfigRoot(Enum):
    """Root location for config file path resolution."""

    PROJECT = "project"  # Relative to project root
    PACKAGE = "package"  # Relative to djb package (core.toml)
    HOME = "home"  # Relative to home dir (future)


class ConfigIO(ConfigStore):
    """Abstract base class for single-source config I/O.

    ConfigIO implements the ConfigStore protocol for the lowest layer.
    It reads from and writes to a single source (file, env, dict).

    Provenance: Returns (self,) - just itself.

    Subclasses should set:
    - name: Human-readable name (class attribute)
    - writable: Whether writes are supported (class attribute, default True)
    - explicit: Whether this is explicit user config (class attribute, default True)
    """

    # Path resolution attributes - subclasses should override these
    root: ConfigRoot = ConfigRoot.PROJECT
    relative_path: Path | None = None  # Override in subclass for file-based IOs

    # Base prefix for path composition - subclasses override (e.g., "tool.djb" for PyprojectConfigIO)
    base_prefix: ClassVar[str | None] = None

    # Mode prefix for path composition (e.g., "staging", "development")
    _mode_prefix: str | None = None

    def __init__(
        self,
        config: "DjbConfigBase",
        *,
        mode_prefix: str | None = None,
    ) -> None:
        """Initialize ConfigIO with config reference.

        Args:
            config: DjbConfigBase instance (may be partially resolved during bootstrap).
            mode_prefix: Mode prefix for path composition (e.g., "staging").
                When set, all paths are prefixed with this mode.
        """
        super().__init__(config)
        self._mode_prefix = mode_prefix

    # =========================================================================
    # Path composition
    # =========================================================================

    def full_path(self, key: str) -> tuple[str | None, str]:
        """Build complete navigation path: base_prefix / mode_prefix / key.

        This method composes all path components and splits into (nav_path, leaf_key):
        - base_prefix: Static prefix set by subclass (e.g., "tool.djb" for PyprojectConfigIO)
        - mode_prefix: Mode prefix (e.g., "staging", "development"). Production is omitted.
        - key: Dotted key path (e.g., "hetzner.default_server_type")

        Production handling: If mode_prefix is "production", it's omitted from the path
        (production values are stored at root level, not in a [production] section).

        Returns:
            Tuple of (nav_path, leaf_key). nav_path is None if leaf is at root.

        Examples:
            >>> io = PyprojectConfigIO(ctx, mode_prefix="staging")
            >>> io.full_path("hetzner.default_server_type")
            ('tool.djb.staging.hetzner', 'default_server_type')

            >>> io = PyprojectConfigIO(ctx, mode_prefix="production")
            >>> io.full_path("mode")
            ('tool.djb', 'mode')

            >>> io = ProjectConfigIO(ctx)
            >>> io.full_path("mode")
            (None, 'mode')
        """
        # Filter out production mode - production values live at root
        mode = (
            self._mode_prefix
            if self._mode_prefix and self._mode_prefix != PRODUCTION_MODE
            else None
        )
        segments = [self.base_prefix, mode, key]
        full = ".".join(s for s in segments if s)
        if "." in full:
            nav_path, leaf_key = full.rsplit(".", 1)
            return (nav_path, leaf_key)
        return (None, full)

    # =========================================================================
    # In-config navigation methods
    # =========================================================================

    def _load_raw_data(self) -> dict[str, Any]:
        """Load raw data from source (no navigation).

        Subclasses implement this to provide raw data:
        - TomlConfigIO: reads TOML file (dict)
        - DictConfigIO: returns the in-memory dict
        - EnvConfigIO: returns EnvDict for lazy env var access

        Returns:
            Raw data mapping (no prefix/mode navigation applied).
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _load_raw_data()")

    # =========================================================================
    # Key-level operations (ConfigStore interface)
    # =========================================================================

    def get(self, key: str) -> tuple[Any, "Provenance | None"]:
        """Get value, return (self,) as provenance if found.

        Args:
            key: Configuration key to get.

        Returns:
            Tuple of (value, provenance). Returns (None, None) if not found.
        """
        value = self._get_value(key)
        if value is not None:
            return (value, (self,))
        return (None, None)

    def set(self, key: str, value: Any, *, rest: "Provenance" = ()) -> None:  # noqa: ARG002
        """Set value directly to this source.

        Args:
            key: Configuration key to set.
            value: Value to set.
            rest: Ignored (ConfigIO is the final layer).
        """
        self._set_value(key, value)

    def delete(self, key: str, *, rest: "Provenance" = ()) -> None:  # noqa: ARG002
        """Delete value from this source.

        Args:
            key: Configuration key to delete.
            rest: Ignored (ConfigIO is the final layer).
        """
        self._delete_value(key)

    def has(self, key: str) -> bool:
        """Check if key exists in this source.

        Uses _load_raw_data() + navigate_config_path() for navigation.
        Falls back to _get_value() for external sources without raw data.
        Returns True for both flat values and sections.

        The key can be a dotted path (e.g., "hetzner.default_server_type").
        Full path is composed as: base_prefix.mode_prefix.key
        Then navigates to all-but-last segment, checks at last segment.

        Args:
            key: Configuration key to check (may be dotted).

        Returns:
            True if the key exists, False otherwise.
        """
        try:
            data = self._load_raw_data()
        except NotImplementedError:
            # Fall back to _get_value for external sources (GitConfigIO, etc.)
            return self._get_value(key) is not None

        if not data:
            return False

        nav_path, leaf_key = self.full_path(key)
        result = navigate_config_path(data, nav_path)
        if result is None:
            return False

        return leaf_key in result

    # =========================================================================
    # Data-level operations (ConfigStore interface)
    # =========================================================================

    def load(self, *, rest: "Provenance" = ()) -> dict[str, Any]:  # noqa: ARG002
        """Load entire config from this source.

        Loads from root and navigates to the mode section if applicable.
        Uses _load_raw_data() + navigate_config_path().

        Args:
            rest: Ignored (ConfigIO is the final layer).

        Returns:
            Configuration dict at the mode section, or empty dict.
        """
        try:
            data = self._load_raw_data()
        except NotImplementedError:
            return {}

        if not data:
            return {}

        # Navigate to base_prefix + mode_prefix section
        mode = (
            self._mode_prefix
            if self._mode_prefix and self._mode_prefix != PRODUCTION_MODE
            else None
        )
        segments = [self.base_prefix, mode]
        section_path = ".".join(s for s in segments if s) or None
        result = navigate_config_path(data, section_path)
        if result is None:
            return {}

        return dict(result)

    def save(self, data: dict[str, Any], *, rest: "Provenance" = ()) -> None:  # noqa: ARG002
        """Save entire config to this source.

        Saves to root, navigating to the mode section if applicable.
        Uses _load_raw_data() + navigate_config_path() + _write_raw_data().

        Args:
            data: Configuration dict to save.
            rest: Ignored (ConfigIO is the final layer).
        """
        if not self.writable:
            raise ValueError(f"Cannot write to {self.name}")

        raw = self._load_raw_data()

        # Navigate to base_prefix + mode_prefix section
        mode = (
            self._mode_prefix
            if self._mode_prefix and self._mode_prefix != PRODUCTION_MODE
            else None
        )
        segments = [self.base_prefix, mode]
        section_path = ".".join(s for s in segments if s) or None
        target = navigate_config_path(raw, section_path, ensure=True)
        target.update(data)
        self._write_raw_data(raw)

    # =========================================================================
    # Properties (ConfigStore interface)
    # =========================================================================

    @property
    def exists(self) -> bool:
        """Whether the source exists (file exists, etc.). Default is True."""
        return True

    def get_io(self) -> "ConfigIO":
        """Get the underlying ConfigIO - returns self for ConfigIO."""
        return self

    # Whether values from this source are explicit user configuration.
    # Explicit sources are user-controlled (local.toml, project.toml).
    # Derived sources (core.toml, git config) override this to False.
    explicit = True

    def resolve_path(self) -> Path:
        """Get the full file path using config.project_dir.

        Returns:
            Full path to the config file.

        Raises:
            NotImplementedError: If this source has no file path.
        """
        if self.relative_path is None:
            raise NotImplementedError(f"{self.__class__.__name__} has no file path")

        if self.root == ConfigRoot.PROJECT:
            return self.config.project_dir / self.relative_path
        elif self.root == ConfigRoot.PACKAGE:
            # Relative to djb package (for core.toml)
            return Path(__file__).parent.parent.parent / self.relative_path
        elif self.root == ConfigRoot.HOME:
            return Path.home() / self.relative_path
        else:
            raise ValueError(f"Unknown ConfigRoot: {self.root}")

    # =========================================================================
    # Internal methods (subclasses must implement)
    # =========================================================================

    def _get_value(self, key: str) -> Any | None:
        """Get a single value by key.

        Uses _load_raw_data() + navigate_config_path() for navigation.
        Returns both flat values and nested dicts (sections).
        External sources may override for special key handling.

        The key can be a dotted path (e.g., "hetzner.default_server_type").
        Full path is composed as: base_prefix.mode_prefix.key
        Then navigates to all-but-last segment, gets value at last segment.

        Args:
            key: Configuration key (may be dotted).

        Returns:
            The value (or section dict), or None if not found.
        """
        try:
            data = self._load_raw_data()
        except NotImplementedError:
            return None

        if not data:
            return None

        nav_path, leaf_key = self.full_path(key)
        result = navigate_config_path(data, nav_path)
        if result is None:
            return None

        return result.get(leaf_key)

    def _set_value(self, key: str, value: Any) -> None:
        """Set a single value by key.

        Uses _load_raw_data() + navigate_config_path() + _write_raw_data().
        Read-only sources raise ValueError.

        The key can be a dotted path (e.g., "hetzner.default_server_type").
        Full path is composed as: base_prefix.mode_prefix.key
        Then navigates to all-but-last segment, sets value at last segment.

        For TOML sources, new keys are inserted in alphabetical order near
        related keys (grouped by prefix). Existing keys preserve their position.

        Args:
            key: Configuration key (may be dotted).
            value: Value to set.
        """
        if not self.writable:
            raise ValueError(f"Cannot write to {self.name}")

        data = self._load_raw_data()

        nav_path, leaf_key = self.full_path(key)
        target = navigate_config_path(data, nav_path, ensure=True)

        # Use ordered insertion for new keys (preserves position for existing)
        if leaf_key not in target:
            insert_key_ordered(target, leaf_key, value)
        else:
            target[leaf_key] = value

        self._write_raw_data(data)

    def _delete_value(self, key: str) -> None:
        """Delete a single value by key.

        Uses _load_raw_data() + navigate_config_path() + _write_raw_data().
        Read-only sources raise ValueError.
        Cleans up empty parent dicts after deletion.

        The key can be a dotted path (e.g., "hetzner.default_server_type").
        Full path is composed as: base_prefix.mode_prefix.key
        Then navigates to all-but-last segment, deletes at last segment.

        Args:
            key: Configuration key (may be dotted).
        """
        if not self.writable:
            raise ValueError(f"Cannot delete from {self.name}")

        data = self._load_raw_data()

        nav_path, leaf_key = self.full_path(key)
        target = navigate_config_path(data, nav_path)
        if target is not None and leaf_key in target:
            del target[leaf_key]
            # Clean up empty parent dicts - use nav_path (not full path with leaf)
            if nav_path:
                self._cleanup_empty_parents(data, nav_path)
            self._write_raw_data(data)

    def _cleanup_empty_parents(self, data: dict[str, Any], path: str) -> None:
        """Remove empty parent dicts after key deletion.

        Walks the path from deepest to shallowest, removing empty dicts.

        Args:
            data: Root data dict.
            path: Dotted path string to the section that was modified.
        """
        if not path:
            return

        parts = path.split(".")
        # Walk from deepest to shallowest
        for i in range(len(parts), 0, -1):
            parent_path = ".".join(parts[:i])
            parent = navigate_config_path(data, parent_path)
            if parent is not None and len(parent) == 0:
                # Remove this empty dict from its parent
                if i == 1:
                    # Top level
                    del data[parts[0]]
                else:
                    grandparent = navigate_config_path(data, ".".join(parts[: i - 1]))
                    if grandparent is not None:
                        del grandparent[parts[i - 1]]

    def _write_raw_data(self, data: dict[str, Any]) -> None:
        """Write raw data to source.

        Subclasses implement this to write data:
        - TomlConfigIO: writes TOML file
        - DictConfigIO: raises (read-only)
        - EnvConfigIO: raises (read-only)

        Args:
            data: Raw data dict to write.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _write_raw_data()")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
