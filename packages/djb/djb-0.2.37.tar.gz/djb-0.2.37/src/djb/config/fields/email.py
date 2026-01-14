"""
EmailField - Field for email addresses with validation.

Uses GitConfigIO("user.email") as a field-specific config store,
which is checked after standard stores (cli > env > local > project > core).
"""

from __future__ import annotations

import re
from functools import partial
from typing import Any

from djb.config.field import ConfigFieldABC, ConfigValidationError
from djb.config.storage.io.external import GitConfigIO

# Basic email pattern - allows most valid emails
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailField(ConfigFieldABC):
    """Field for email addresses with format validation.

    Uses GitConfigIO("user.email") as an extra store in the resolution chain.
    The base resolve() handles all resolution logic.
    """

    def __init__(self, **kwargs):
        """Initialize with git config as field-specific store."""
        super().__init__(
            prompt_text="Enter your email",
            validation_hint="expected: user@domain.com",
            config_store_factories=[partial(GitConfigIO, "user.email")],
            **kwargs,
        )

    def validate(self, value: Any) -> None:
        """Validate email format."""
        if not self._require_string(value):
            return
        if not EMAIL_PATTERN.match(value):
            raise ConfigValidationError(f"Invalid email format: {value!r}")
