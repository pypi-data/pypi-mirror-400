"""
IPAddressField - Field for IP addresses with validation.

Validates IPv4 and IPv6 addresses using Python's ipaddress module.
"""

from __future__ import annotations

import ipaddress
from typing import Any

from djb.config.field import ConfigFieldABC, ConfigValidationError


class IPAddressField(ConfigFieldABC):
    """Field for IP addresses with format validation.

    Validates both IPv4 and IPv6 addresses using Python's ipaddress module.
    """

    def __init__(self, **kwargs: Any):
        """Initialize IP address field."""
        super().__init__(
            validation_hint="expected: valid IPv4 or IPv6 address",
            **kwargs,
        )

    def validate(self, value: Any) -> None:
        """Validate IP address format."""
        if not self._require_string(value):
            return
        try:
            ipaddress.ip_address(value)
        except ValueError as e:
            raise ConfigValidationError(f"Invalid IP address: {value!r}") from e
