"""
PathField - Field for filesystem path configuration values.

Accepts: strings representing paths or Path objects.
Stores as string in config TOML files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from djb.config.field import ConfigFieldABC, ConfigValidationError


class PathField(ConfigFieldABC):
    """Field for filesystem path values.

    Accepts string paths and Path objects.
    Stores as string in TOML, returns as Path object.
    """

    def normalize(self, value: Any) -> Path:
        """Normalize to Path.

        Args:
            value: The raw value to normalize (string or Path).

        Returns:
            Path object.

        Raises:
            ConfigValidationError: If value cannot be converted to Path.
        """
        if isinstance(value, Path):
            return value

        if isinstance(value, str):
            return Path(value)

        raise ConfigValidationError(
            f"Cannot convert to path: {value!r}. Expected a string or Path."
        )

    def validate(self, value: Any) -> None:
        """Validate that value is a Path."""
        if value is None:
            return  # Allow None for optional fields
        if not isinstance(value, Path):
            raise ConfigValidationError(
                f"{self.field_name} must be a Path. Got: {type(value).__name__}"
            )

    def serialize(self, value: Path | None) -> str | None:
        """Serialize Path to string for TOML storage."""
        if value is None:
            return None
        return str(value)
