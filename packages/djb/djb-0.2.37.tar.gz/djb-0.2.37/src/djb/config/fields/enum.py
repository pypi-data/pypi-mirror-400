"""
EnumField - Field for enum types with automatic parsing.

Handles parsing strings to enum values, with fallback to default
when parsing fails.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from djb.config.field import ConfigFieldABC
from djb.core.logging import get_logger

logger = get_logger(__name__)


class EnumField(ConfigFieldABC):
    """Field for enum types with automatic parsing.

    Args:
        enum_class: The enum class to parse values into.
        strict: If True (default), unknown values fall back to default.
            If False, unknown values are accepted as-is with a warning.
            Use strict=False for forward compatibility (e.g., new Hetzner
            server types that aren't in the enum yet).
        **kwargs: Passed to ConfigFieldABC.__init__().
    """

    def __init__(self, enum_class: type[Enum], *, strict: bool = True, **kwargs: Any):
        super().__init__(**kwargs)
        self.enum_class = enum_class
        self.strict = strict

    def normalize(self, value: Any) -> Any:
        """Parse string to enum.

        If strict=False, unknown values are accepted with a warning.
        None is passed through unchanged (for nullable fields).
        """
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value
        # Use the enum's parse method if available (like Mode.parse)
        parse_method = getattr(self.enum_class, "parse", None)
        if callable(parse_method):
            parsed = parse_method(value)
            if parsed is not None:
                return parsed
        # Fall back to trying to create enum from value
        try:
            return self.enum_class(value)
        except (ValueError, KeyError):
            if not self.strict:
                # Accept unknown value with warning (for forward compatibility)
                known_values = [e.value for e in self.enum_class]
                logger.warning(
                    f"Unknown value '{value}' for {self.enum_class.__name__}. "
                    f"Known values: {known_values}. Accepting as-is."
                )
                return value
            return self.get_default()
