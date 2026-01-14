"""
In-memory dict ConfigIO implementation.

Used for CLI overrides - read-only during resolution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from djb.config.storage.io.base import ConfigIO

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase


class DictConfigIO(ConfigIO):
    """Config I/O for in-memory dict (CLI overrides or runtime overrides).

    Read-only - overrides are passed at runtime and not modified.
    """

    name = "cli"  # Default, can be overridden in __init__
    writable = False
    explicit = False  # Default, can be overridden in __init__

    def __init__(
        self,
        config: "DjbConfigBase",
        data: dict[str, Any] | None,
        *,
        name: str = "cli",
        explicit: bool = False,
    ):
        """Initialize with config reference and data dict.

        Args:
            config: DjbConfig instance (may be partially resolved during bootstrap).
            data: In-memory configuration dict. None means empty dict.
            name: Human-readable name for this source (e.g., "cli", "override").
            explicit: Whether values from this source are explicit user config.
        """
        super().__init__(config)
        self._data = data if data is not None else {}
        self.name = name  # type: ignore[misc]  # Override class var with instance var
        self.explicit = explicit  # type: ignore[misc]

    def _load_raw_data(self) -> dict[str, Any]:
        """Return the in-memory dict."""
        return self._data

    # Everything else inherited from base class (writable=False blocks writes)
