"""
Derived ConfigType implementation.

For fields that are computed at runtime and not stored in config files:
- project_dir: Derived from cwd or environment
- project_name: May fall back to pyproject.toml [project].name or directory name
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from djb.config.storage.types.base import ConfigType

if TYPE_CHECKING:
    from djb.config.storage.io import ConfigIO
    from djb.config.storage.base import Provenance


class DerivedConfigType(ConfigType):
    """Config type for derived fields (computed at runtime).

    No I/O - values are computed by the field's resolve() method.
    Cannot be read from or written to via ConfigType methods.
    """

    name = "DERIVED"
    writable = False
    explicit = False  # Derived fields are not explicit user configuration

    def get(self, key: str) -> tuple[Any, "Provenance | None"]:
        """Derived fields don't have values in the config system.

        The field's resolve() method computes the value.
        """
        return (None, None)

    def _get_read_layers(self) -> list["ConfigIO"]:
        return []

    def _get_write_io(self) -> "ConfigIO":
        raise ValueError("Cannot write derived fields")
