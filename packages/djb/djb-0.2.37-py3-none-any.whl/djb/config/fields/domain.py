"""
DomainNameField - Field for domain names with validation.

Validates domain name format using regex pattern matching.
"""

from __future__ import annotations

import re
from typing import Any

from djb.config.field import ConfigFieldABC, ConfigValidationError

# Domain name validation pattern:
# - Each label: 1-63 chars, alphanumeric or hyphen, cannot start/end with hyphen
# - Total domain: up to 253 chars
# - At least one dot (TLD required)
DOMAIN_NAME_PATTERN = re.compile(
    r"^(?!-)"  # Cannot start with hyphen
    r"(?:[a-zA-Z0-9-]{1,63}\.)*"  # Subdomains
    r"[a-zA-Z0-9-]{1,63}"  # Final label
    r"(?<!-)$"  # Cannot end with hyphen
)


class DomainNameField(ConfigFieldABC):
    """Field for domain names with format validation.

    Validates domain names like 'example.com', 'sub.example.co.uk'.
    """

    def __init__(self, **kwargs: Any):
        """Initialize domain name field."""
        super().__init__(
            validation_hint="expected: valid domain name (e.g., example.com)",
            **kwargs,
        )

    def validate(self, value: Any) -> None:
        """Validate domain name format."""
        if not self._require_string(value):
            return

        # Check length
        if len(value) > 253:
            raise ConfigValidationError(f"Domain name too long (max 253 chars): {value!r}")

        # Check for at least one dot (TLD required)
        if "." not in value:
            raise ConfigValidationError(f"Invalid domain name (missing TLD): {value!r}")

        # Check pattern
        if not DOMAIN_NAME_PATTERN.match(value):
            raise ConfigValidationError(f"Invalid domain name: {value!r}")

        # Check individual label lengths
        for label in value.split("."):
            if len(label) > 63:
                raise ConfigValidationError(f"Domain label too long (max 63 chars): {label!r}")
            if label.startswith("-") or label.endswith("-"):
                raise ConfigValidationError(f"Domain label cannot start/end with hyphen: {label!r}")
