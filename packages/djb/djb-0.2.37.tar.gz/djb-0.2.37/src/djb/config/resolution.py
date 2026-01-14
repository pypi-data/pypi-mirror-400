"""
Config resolution machinery - layered config lookup with provenance tracking.

This module provides:
- ResolutionChain: Queries ConfigTypes in priority order, returns Provenance
- get_standard_stores: Factory for building the standard stores list
- build_resolution_chain: Factory for building the standard resolution chain
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from djb.config.storage.io import DictConfigIO, EnvConfigIO
from djb.config.storage.base import ConfigStore, Provenance
from djb.config.storage.types import (
    ConfigType,
    CoreConfigType,
    LocalConfigType,
    ProjectConfigType,
)

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase


# ===========================================================================
# ResolutionChain - Queries ConfigTypes in priority order
# ===========================================================================


class ResolutionChain:
    """Queries ConfigStores in priority order.

    The top layer in the config system. It queries stores in order:
    cli > env > local > project > core (+ any extra stores)

    Returns Provenance tuple for routing writes back to the correct source.

    Note: This is not a ConfigStore itself - it's a chain of stores.
    """

    def __init__(self, stores: Sequence[ConfigStore]):
        """Initialize with ordered list of ConfigStores.

        Args:
            stores: ConfigStores in priority order (highest first).
                   Each store should have ctx set with project_root and mode.
        """
        self._stores = stores
        self._provenance: dict[str, Provenance] = {}  # Cache of where each value came from

    def get_provenance(self, key: str) -> Provenance | None:
        """Get cached provenance for a key.

        Returns the provenance tuple from the last get() call for this key.
        """
        return self._provenance.get(key)

    def get(self, key: str) -> tuple[Any, Provenance | None]:
        """Query stores in priority order, return first match with provenance.

        Args:
            key: Configuration key to get.

        Returns:
            Tuple of (value, provenance). Provenance is (ConfigType, ConfigIO).
            Returns (None, None) if not found.
        """
        for store in self._stores:
            value, provenance = store.get(key)

            if value is not None:
                if provenance is not None:
                    self._provenance[key] = provenance  # Cache it
                return (value, provenance)

        return (None, None)

    def get_all(self, key: str):
        """Yield all (value, provenance) pairs from all stores.

        Unlike get(), this yields all values from all stores,
        allowing callers to try each value until finding a valid one.

        Args:
            key: Configuration key to get.

        Yields:
            Tuples of (value, provenance) for each store that has the key.
        """
        for store in self._stores:
            value, provenance = store.get(key)

            if value is not None:
                yield (value, provenance)

    def has(self, key: str) -> bool:
        """Check if key exists in any store.

        Args:
            key: Configuration key to check.

        Returns:
            True if the key exists in any store.
        """
        for store in self._stores:
            if store.has(key):
                return True
        return False

    def set(
        self,
        key: str,
        value: Any,
        *,
        rest: Provenance = (),
        source: Provenance | None = None,
        default_destination: Provenance | None = None,
    ) -> None:
        """Write a value to config via provenance chain.

        Args:
            key: Configuration key to set.
            value: Value to set.
            rest: Not used - for ConfigStore interface compatibility.
            source: Provenance from get(). Walks chain to write back to same location.
            default_destination: Provenance for new values (typically field's config_type).
        """
        provenance = source or default_destination
        if not provenance:
            raise ValueError("Either source or default_destination is required for set()")

        # Walk the provenance chain - delegate to first element
        provenance[0].set(key, value, rest=provenance[1:])

    def delete(
        self,
        key: str,
        *,
        rest: Provenance = (),
        source: Provenance | None = None,
        default_destination: Provenance | None = None,
    ) -> None:
        """Delete a value from config via provenance chain.

        Args:
            key: Configuration key to delete.
            rest: Not used - for ConfigStore interface compatibility.
            source: Provenance from get(). Walks chain to delete from same location.
            default_destination: Provenance for new values (typically field's config_type).
        """
        provenance = source or default_destination
        if not provenance:
            raise ValueError("Either source or default_destination is required for delete()")

        # Walk the provenance chain - delegate to first element
        provenance[0].delete(key, rest=provenance[1:])

    def load(self, *, rest: Provenance = ()) -> dict[str, Any]:  # noqa: ARG002
        """Load and merge data from all stores.

        Iterates stores in reverse priority order (lowest first), merging
        data so highest priority stores win.

        Returns:
            Merged data dict with highest-priority values winning.
        """
        merged: dict[str, Any] = {}

        # Iterate in reverse (lowest priority first, highest wins)
        for store in reversed(self._stores):
            # ConfigType wraps ConfigIOs - iterate their layers for proper merging
            if isinstance(store, ConfigType):
                io_layers = store._get_read_layers()
                for io in reversed(io_layers):
                    data = io.load()
                    if data:
                        merged.update(data)
            else:
                # ConfigIO and other stores - use load() directly
                data = store.load()
                if data:
                    merged.update(data)

        return merged

    def save(self, data: dict[str, Any], *, rest: Provenance = ()) -> None:
        """Not typically used - caller uses provenance[-1].save() instead."""
        raise NotImplementedError("Use provenance[-1].save() to save to source")

    @property
    def name(self) -> str:
        return "resolution_chain"

    @property
    def writable(self) -> bool:
        return False  # Writes go through provenance chain


def get_standard_stores(
    config: "DjbConfigBase",
    *,
    env: Mapping[str, str] | None = None,
) -> list[ConfigStore]:
    """Get the standard stores list for config resolution.

    Returns stores in priority order:
    override > env > local > project > core

    The override layer is only included if config._overrides_dict is set.
    Each ConfigType handles mode interleaving internally (mode section
    before base section for non-production modes).

    Args:
        config: DjbConfigBase instance (may be partially resolved during bootstrap).
        env: Environment variables mapping. None means use os.environ.
            If not provided, uses config._env if set, otherwise os.environ.

    Returns:
        List of ConfigStore instances in priority order.
    """
    stores: list[ConfigStore] = []

    # Add override layer if present (highest priority)
    # _overrides_dict is already merged by get_augmented_djb_config()
    overrides_dict = getattr(config, "_overrides_dict", None)
    if overrides_dict:
        stores.append(DictConfigIO(config, overrides_dict, name="override", explicit=True))

    # Use provided env, or config._env, or let EnvConfigIO use os.environ
    effective_env = env if env is not None else getattr(config, "_env", None)

    # Standard stores in priority order
    stores.extend(
        [
            EnvConfigIO(config, effective_env),
            LocalConfigType(config),
            ProjectConfigType(config),
            CoreConfigType(config),
        ]
    )

    return stores


def build_resolution_chain(
    config: "DjbConfigBase",
    *,
    env: Mapping[str, str] | None = None,
) -> ResolutionChain:
    """Build the standard resolution chain.

    Priority order: override > env > local > project > core

    Each ConfigType handles mode interleaving internally.

    Args:
        config: DjbConfigBase instance (may be partially resolved during bootstrap).
        env: Environment variables mapping. None means use os.environ.

    Returns:
        ResolutionChain configured with standard priority order.
    """
    return ResolutionChain(
        get_standard_stores(
            config,
            env=env,
        )
    )
