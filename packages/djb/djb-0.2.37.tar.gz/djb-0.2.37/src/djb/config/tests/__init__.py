"""
Config test utilities and base classes.

Autouse Fixtures (conftest.py):
    clean_djb_env - Removes DJB_* environment variables before each test

Provides:
    ConfigTestBase - Base class for test config objects with provenance tracking
    make_test_config - Factory for creating test config instances
"""

from __future__ import annotations

import attrs

from djb.config.storage.base import Provenance
from djb.config.storage.types import (
    CoreConfigIO,
    DerivedConfigType,
    LocalConfigIO,
)
from djb.config.storage.io import (
    GitConfigIO,
    CwdPathConfigIO,
    CwdNameConfigIO,
    PyprojectNameConfigIO,
)

# IO types that represent derived (non-explicit) sources
_DERIVED_IO_TYPES = (
    CoreConfigIO,
    DerivedConfigType,
    GitConfigIO,
    CwdPathConfigIO,
    CwdNameConfigIO,
    PyprojectNameConfigIO,
)


def _is_provenance_explicit(provenance: Provenance) -> bool:
    """Check if a Provenance tuple represents an explicit source."""
    if not provenance:
        return False
    for store in provenance:
        if isinstance(store, _DERIVED_IO_TYPES):
            return False
    return True


@attrs.frozen
class ConfigTestBase:
    """Base class for test configurations with provenance tracking.

    This is a simple @attrs.frozen class that provides the same provenance
    tracking methods as DjbConfig, without the full field resolution machinery.

    Usage:
        @attrs.frozen
        class MyTestConfig(ConfigTestBase):
            name: str = "default"

        config = MyTestConfig(_provenance={"name": (LOCAL_IO,)})
        assert config.is_explicit("name")
    """

    _provenance: dict[str, Provenance] = attrs.field(factory=dict, repr=False, alias="_provenance")

    def is_explicit(self, field: str) -> bool:
        """Check if a field was explicitly configured."""
        provenance = self._provenance.get(field)
        if provenance is None:
            return False
        return _is_provenance_explicit(provenance)

    def is_derived(self, field: str) -> bool:
        """Check if a field was derived from secondary sources."""
        provenance = self._provenance.get(field)
        if provenance is None:
            return False
        return not _is_provenance_explicit(provenance)

    def is_configured(self, field: str) -> bool:
        """Check if a field has a configured value."""
        return self.get_source(field) is not None

    def get_source(self, field: str) -> Provenance | None:
        """Get the source of a field's value."""
        return self._provenance.get(field)


__all__ = [
    "ConfigTestBase",
    "LocalConfigIO",
]
