"""
ConfigStore ABC and Provenance type.

The ConfigStore ABC defines the common interface at every layer:
- ConfigIO - Single source I/O (TOML files, env vars, dicts)
- ConfigType - Abstract category (LOCAL, PROJECT, CORE)
- ResolutionChain - Queries ConfigTypes in priority order

All layers implement get/set/has (key-level) + load/save (data-level).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase

# Provenance is a tuple of ConfigStore instances representing the path
# through the layers. e.g., (PROJECT, PyprojectConfigIO) means:
# - The value was found via PROJECT ConfigType
# - Specifically from the PyprojectConfigIO source
#
# When writing, we walk this chain: pop head, pass rest down.
# Each layer can continue the chain or redirect (migration).
Provenance = tuple["ConfigStore", ...]


class ConfigStore(ABC):
    """Common interface for all config layers.

    Implemented by:
    - ConfigIO: Single source I/O (TOML files, env vars, dicts)
    - ConfigType: Abstract category (LOCAL, PROJECT, CORE)
    - ResolutionChain: Queries ConfigTypes in priority order

    All layers implement the same operations:
    - Key-level: get, set, has
    - Data-level: load, save

    The default set() implementation walks the rest chain automatically.
    Leaf nodes (ConfigIO) override it to perform the actual write.
    """

    # Class attributes - subclasses override
    name: ClassVar[str] = ""
    writable: ClassVar[bool] = True
    explicit: ClassVar[bool] = True  # Whether values from this store are explicit user config

    config: "DjbConfigBase"

    def __init__(self, config: "DjbConfigBase") -> None:
        """Initialize ConfigStore with config reference.

        Args:
            config: DjbConfigBase instance (may be partially resolved during bootstrap).
        """
        self.config = config

    # =========================================================================
    # Key-level operations
    # =========================================================================

    @abstractmethod
    def get(self, key: str) -> tuple[Any, Provenance | None]:
        """Get value and provenance for a key.

        Args:
            key: Configuration key to get.

        Returns:
            Tuple of (value, provenance). Returns (None, None) if not found.
            Provenance is a tuple of ConfigStore instances representing the path.
        """
        ...

    def set(self, key: str, value: Any, *, rest: Provenance = ()) -> None:
        """Set a value for a key.

        Default implementation walks the rest chain to the final IO.
        Override in leaf nodes (ConfigIO) to perform the actual write.

        Args:
            key: Configuration key to set.
            value: Value to set.
            rest: Remaining provenance chain from caller. Empty for new values.
        """
        if rest:
            # Walk down the chain
            rest[0].set(key, value, rest=rest[1:])
        else:
            # Leaf node - must be overridden in ConfigIO
            raise NotImplementedError(
                f"{self.__class__.__name__}.set() reached end of chain without override. "
                "ConfigIO subclasses must override set() to perform the actual write."
            )

    def delete(self, key: str, *, rest: Provenance = ()) -> None:
        """Delete a value for a key.

        Default implementation walks the rest chain to the final IO.
        Override in leaf nodes (ConfigIO) to perform the actual delete.

        Args:
            key: Configuration key to delete.
            rest: Remaining provenance chain from caller. Empty for new values.
        """
        if rest:
            # Walk down the chain
            rest[0].delete(key, rest=rest[1:])
        else:
            # Leaf node - must be overridden in ConfigIO
            raise NotImplementedError(
                f"{self.__class__.__name__}.delete() reached end of chain without override. "
                "ConfigIO subclasses must override delete() to perform the actual delete."
            )

    @abstractmethod
    def has(self, key: str) -> bool:
        """Check if a key exists.

        Args:
            key: Configuration key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        ...

    # =========================================================================
    # Data-level operations
    # =========================================================================

    def load(self, *, rest: Provenance = ()) -> dict[str, Any]:
        """Load entire config from this source.

        Default implementation walks the rest chain to the final IO.
        Override in leaf nodes (ConfigIO) to perform the actual load.

        Args:
            rest: Remaining provenance chain. If provided, load from rest[0].

        Returns:
            Configuration dict at mode section.
        """
        if rest:
            return rest[0].load(rest=rest[1:])
        raise NotImplementedError(
            f"{self.__class__.__name__}.load() reached end of chain without override. "
            "ConfigIO subclasses must override load() to perform the actual load."
        )

    def save(self, data: dict[str, Any], *, rest: Provenance = ()) -> None:
        """Save entire config to this source.

        Default implementation walks the rest chain to the final IO.
        Override in leaf nodes (ConfigIO) to perform the actual save.

        Args:
            data: Configuration dict to save.
            rest: Remaining provenance chain. If provided, save to rest[0].
        """
        if rest:
            rest[0].save(data, rest=rest[1:])
        else:
            raise NotImplementedError(
                f"{self.__class__.__name__}.save() reached end of chain without override. "
                "ConfigIO subclasses must override save() to perform the actual save."
            )

    # =========================================================================
    # IO access
    # =========================================================================

    @abstractmethod
    def get_io(self) -> "ConfigStore":
        """Get the underlying ConfigIO for this store.

        For ConfigIO: returns self (identity).
        For ConfigType: returns the write IO (e.g., ProjectConfigIO for PROJECT_TYPE).

        Returns:
            The ConfigIO instance for this store.
        """
        ...
