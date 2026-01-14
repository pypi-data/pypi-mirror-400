"""
IntField - Field for integer configuration values.

Accepts: integers or string representations of integers.
Stores as integer in config YAML files.
"""

from __future__ import annotations

from typing import Any

from djb.config.field import ConfigFieldABC, ConfigValidationError


class IntField(ConfigFieldABC):
    """Field for integer values.

    Accepts string representations of integers and actual int values.
    Stores as integer in YAML.
    """

    def normalize(self, value: Any) -> int:
        """Normalize to integer.

        Args:
            value: The raw value to normalize (string or int).

        Returns:
            Integer value.

        Raises:
            ConfigValidationError: If value cannot be converted to integer.
        """
        if isinstance(value, int) and not isinstance(value, bool):
            return value

        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                pass

        raise ConfigValidationError(
            f"Cannot convert to integer: {value!r}. Expected an integer value."
        )

    def validate(self, value: Any) -> None:
        """Validate that value is an integer."""
        if value is None:
            return  # Allow None for optional fields
        if not isinstance(value, int) or isinstance(value, bool):
            raise ConfigValidationError(
                f"{self.field_name} must be an integer. Got: {type(value).__name__}"
            )
