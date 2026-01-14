"""
BoolField - Field for boolean configuration values.

Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive).
Stores as boolean in config YAML files.
"""

from __future__ import annotations

from typing import Any

from djb.config.field import ConfigFieldABC, ConfigValidationError

# Truthy string values (lowercase)
_TRUTHY_VALUES = frozenset({"true", "yes", "on", "1"})

# Falsy string values (lowercase)
_FALSY_VALUES = frozenset({"false", "no", "off", "0"})


class BoolField(ConfigFieldABC):
    """Field for boolean values with flexible parsing.

    Accepts string representations: "true"/"false", "yes"/"no", "on"/"off", "1"/"0".
    Also accepts actual boolean and integer values.
    Stores as boolean in YAML.
    """

    def normalize(self, value: Any) -> bool:
        """Normalize various boolean representations to bool.

        Args:
            value: The raw value to normalize (string, bool, or int).

        Returns:
            Boolean value.

        Raises:
            ConfigValidationError: If value cannot be converted to boolean.
        """
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            return bool(value)

        if isinstance(value, str):
            lower = value.lower().strip()
            if lower in _TRUTHY_VALUES:
                return True
            if lower in _FALSY_VALUES:
                return False

        raise ConfigValidationError(
            f"Cannot convert to boolean: {value!r}. " f"Expected: true/false, yes/no, on/off, 1/0"
        )

    def validate(self, value: Any) -> None:
        """Validate that value is a boolean."""
        if value is None:
            return  # Allow None for optional fields
        if not isinstance(value, bool):
            raise ConfigValidationError(
                f"{self.field_name} must be a boolean. Got: {type(value).__name__}"
            )
