"""
ConfigType abstract base class.

ConfigType is the middle layer in the config system - it represents
an abstract config category (LOCAL, PROJECT, CORE) and delegates to
one or more ConfigIO layers.

Key innovation: ConfigType can have multiple read layers (e.g., PROJECT
reads from both project.toml and pyproject.toml) but writes to a default.

Mode interleaving is handled automatically by the base class based on
the io_types class attribute.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from djb.config.storage.base import ConfigStore

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase
    from djb.config.storage.io import ConfigIO
    from djb.config.storage.base import Provenance

# Production mode values live at root level, not under a [production] section
PRODUCTION_MODE = "production"


class ConfigType(ConfigStore):
    """Base class for config type categories.

    ConfigType implements the ConfigStore protocol for the middle layer.
    It queries one or more ConfigIO layers and returns provenance.

    Subclasses declare io_types - the base class handles mode interleaving:
    - For non-production modes, adds mode-prefixed IO before base IO
    - Production mode reads/writes to root (no mode section)

    Example subclass:
        class LocalConfigType(ConfigType):
            io_types = [LocalConfigIO]
            name = "LOCAL"
    """

    # Class attributes - subclasses override
    io_types: list[type["ConfigIO"]] = []  # IO classes in priority order
    name = ""  # Human-readable name
    writable = True  # Whether writes are supported
    explicit = True  # Whether this is explicit user config

    def __init__(
        self,
        config: "DjbConfigBase",
    ) -> None:
        """Initialize ConfigType with config reference.

        Args:
            config: DjbConfigBase instance (may be partially resolved during bootstrap).
        """
        super().__init__(config)

    # =========================================================================
    # Mode interleaving - base class handles this
    # =========================================================================

    def _get_mode(self) -> str | None:
        """Get mode from config for mode-aware section reading/writing.

        Returns None for production mode (values live at root) or during
        mode resolution (mode is None on config).
        """
        config_mode = self.config.mode
        if config_mode and config_mode != PRODUCTION_MODE:
            return config_mode
        return None

    def _get_read_layers(self) -> list["ConfigIO"]:
        """Build mode-interleaved layers from io_types.

        For each IO type in io_types, adds mode-prefixed layer before base layer
        when mode is non-production.

        Returns:
            List of ConfigIO instances in priority order.
        """
        layers: list["ConfigIO"] = []
        mode = self._get_mode()

        for io_type in self.io_types:
            if mode:
                layers.append(io_type(self.config, mode_prefix=mode))
            layers.append(io_type(self.config))

        return layers

    def _get_write_io(self) -> "ConfigIO":
        """Get default write IO (first io_type with mode prefix if applicable).

        Returns:
            ConfigIO instance for writing.

        Raises:
            ValueError: If this ConfigType is not writable.
        """
        if not self.writable:
            raise ValueError(f"Cannot write to {self.name}")

        mode = self._get_mode()
        return self.io_types[0](self.config, mode_prefix=mode)

    # =========================================================================
    # Key-level operations (ConfigStore interface)
    # =========================================================================

    def get(self, key: str) -> tuple[Any, "Provenance | None"]:
        """Query ConfigIO layers, return first match with provenance.

        Args:
            key: Configuration key to get.

        Returns:
            Tuple of (value, provenance). Provenance is (self, io) where
            io is the ConfigIO that had the value. Returns (None, None)
            if not found.
        """
        for io in self._get_read_layers():
            value, io_provenance = io.get(key)
            if value is not None and io_provenance is not None:
                # Prepend self to the provenance chain
                return (value, (self, *io_provenance))
        return (None, None)

    def set(self, key: str, value: Any, *, rest: "Provenance" = ()) -> None:
        """Set value via inherited chain-walking.

        If rest is empty, sets up chain with default write IO (migration or new value).

        Args:
            key: Configuration key to set.
            value: Value to set.
            rest: Remaining provenance chain. If empty, uses default write IO.
        """
        if not rest:
            # No rest - set up chain with default write IO
            rest = (self._get_write_io(),)
        # Let inherited chain-walking do its job
        super().set(key, value, rest=rest)

    def delete(self, key: str, *, rest: "Provenance" = ()) -> None:
        """Delete value via inherited chain-walking.

        If rest is empty, sets up chain with default write IO.

        Args:
            key: Configuration key to delete.
            rest: Remaining provenance chain. If empty, uses default write IO.
        """
        if not rest:
            # No rest - set up chain with default write IO
            rest = (self._get_write_io(),)
        # Let inherited chain-walking do its job
        super().delete(key, rest=rest)

    def has(self, key: str) -> bool:
        """Check if key exists in any read layer.

        Args:
            key: Configuration key to check.

        Returns:
            True if the key exists in any read layer.
        """
        return any(io.has(key) for io in self._get_read_layers())

    # =========================================================================
    # Data-level operations (ConfigStore interface)
    # =========================================================================

    def load(self, *, rest: "Provenance" = ()) -> dict[str, Any]:
        """Load via inherited chain-walking.

        If rest is empty, sets up chain with default write IO.

        Args:
            rest: Remaining provenance chain. If empty, uses default write IO.

        Returns:
            Configuration dict at mode section.
        """
        if not rest:
            rest = (self._get_write_io(),)
        return super().load(rest=rest)

    def save(self, data: dict[str, Any], *, rest: "Provenance" = ()) -> None:
        """Save via inherited chain-walking.

        If rest is empty, sets up chain with default write IO.

        Args:
            data: Configuration dict to save.
            rest: Remaining provenance chain. If empty, uses default write IO.
        """
        if not rest:
            rest = (self._get_write_io(),)
        super().save(data, rest=rest)

    # =========================================================================
    # Properties (ConfigStore interface)
    # =========================================================================

    def get_io(self) -> "ConfigIO":
        """Get the underlying ConfigIO - returns the write IO for ConfigType."""
        return self._get_write_io()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
