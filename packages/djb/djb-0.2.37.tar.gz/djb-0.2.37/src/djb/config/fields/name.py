"""
NameField - Field for user name with git config fallback.

Uses GitConfigIO("user.name") as a field-specific config store,
which is checked after standard stores (cli > env > local > project > core).
"""

from __future__ import annotations

from functools import partial

from djb.config.field import ConfigFieldABC
from djb.config.storage.io.external import GitConfigIO


class NameField(ConfigFieldABC):
    """Field for user name with git config fallback.

    Uses GitConfigIO("user.name") as an extra store in the resolution chain.
    The base resolve() handles all resolution logic.
    """

    def __init__(self, **kwargs):
        """Initialize with git config as field-specific store."""
        super().__init__(
            prompt_text="Enter your name",
            config_store_factories=[partial(GitConfigIO, "user.name")],
            **kwargs,
        )
