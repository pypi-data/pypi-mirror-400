"""
ListField - Field for list values (e.g., domains).

This module provides a field type for handling list values in config files.
Similar to NestedConfigField but for lists of items.
"""

from __future__ import annotations

from typing import Any

from djb.config.field import ConfigFieldABC, ConfigValidationError, StringField


class ListField(ConfigFieldABC):
    """Field for list values.

    Takes an item field class (like NestedConfigField takes a nested_class)
    for type-safe handling and validation of list items.

    Example usage:
        # List of strings
        domains: list[str] = ListField(StringField, config_file="project")()

    Configured via TOML:
        [heroku]
        domains = ["example.com", "staging.example.com"]
    """

    def __init__(
        self,
        item_field_class: type[ConfigFieldABC] = StringField,
        **kwargs: Any,
    ):
        """Initialize a list field.

        Args:
            item_field_class: Field class for list items (default: StringField).
                Used for normalization and validation of each item.
            **kwargs: Passed to ConfigFieldABC.__init__().
        """
        # Default to empty list if not specified
        if "default" not in kwargs:
            kwargs["default"] = []
        super().__init__(**kwargs)
        self.item_field_class = item_field_class
        # Create an instance for validation (reused for all items)
        self._item_field = item_field_class()

    def get_default(self) -> list:
        """Get the default value (empty list if none specified)."""
        default = super().get_default()
        if default is None:
            return []
        return list(default)  # Return a copy to avoid mutation

    def normalize(self, value: Any) -> list:
        """Normalize value to a list, normalizing each item."""
        if value is None:
            return []
        if not isinstance(value, list):
            # Single value becomes a one-item list
            value = [value]
        # Normalize each item using the item field
        return [self._item_field.normalize(item) for item in value]

    def validate(self, value: Any) -> None:
        """Validate that value is a list with valid items."""
        if value is None:
            return

        if not isinstance(value, list):
            raise ConfigValidationError(
                f"{self.field_name} must be a list, got: {type(value).__name__}"
            )

        # Validate each item using the item field
        for i, item in enumerate(value):
            try:
                self._item_field.field_name = f"{self.field_name}[{i}]"
                self._item_field.validate(item)
            except ConfigValidationError as e:
                raise ConfigValidationError(f"{self.field_name}[{i}]: {e}") from e
