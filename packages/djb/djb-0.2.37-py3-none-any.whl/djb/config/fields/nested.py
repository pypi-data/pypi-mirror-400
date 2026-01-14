"""
NestedConfigField - Field for nested config dataclasses.

Reads from a TOML section matching the field name (e.g., [hetzner]).
Mode overrides come from [mode.section] (e.g., [development.hetzner]).
Supports arbitrary nesting depth (e.g., [hetzner.eu] for hetzner.eu.server_type).
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any, TYPE_CHECKING

from djb.config.field import ConfigFieldABC
from djb.config.storage import DerivedConfigType
from djb.config.storage.base import Provenance

if TYPE_CHECKING:
    from djb.config.config import DjbConfigBase


class NestedConfigField(ConfigFieldABC):
    """Field for nested config dataclasses.

    Nested field path is derived from field_name, combined with key_prefix passed
    from parent for deeply nested configs. e.g., field name "hetzner" reads from
    [hetzner] TOML section, and field "eu" nested under "hetzner" reads from
    [hetzner.eu].

    The nested class must be a ConfigBase subclass with fields
    that use ConfigFieldABC subclasses (e.g., EnumField, StringField).

    Usage in DjbConfig:
        hetzner: HetznerConfig = NestedConfigField(HetznerConfig)

    For deeply nested configs:
        # In HetznerConfig:
        eu: HetznerRegionConfig = NestedConfigField(HetznerRegionConfig)
        # Reads from [hetzner.eu] section

    Supports chaining for get_field_descriptor:
        DjbConfig.hetzner.server_type  # Returns the field descriptor
    """

    def __getattr__(self, name: str) -> ConfigFieldABC:
        """Enable chaining with accumulated nested_field_prefix.

        Returns a COPY of the nested field with nested_field_prefix set from parent
        context. This allows chained access like `DjbConfig.hetzner.eu.server_type`
        to have the correct full nested_field_prefix ("hetzner.eu").

        How it works for `DjbConfig.hetzner.eu.server_type`:
        1. `DjbConfig.hetzner` -> returns original descriptor (nested_field_prefix=None)
        2. `hetzner.eu` -> __getattr__("eu") returns copy with nested_field_prefix="hetzner"
        3. `eu.server_type` -> copy's __getattr__ returns copy with nested_field_prefix="hetzner.eu"

        Args:
            name: Attribute name to look up in nested class.

        Returns:
            A COPY of the ConfigFieldABC descriptor with nested_field_prefix set.

        Raises:
            AttributeError: If the nested class doesn't have this field.
        """
        nested_fields = getattr(self.nested_class, "__fields__", {})
        if name in nested_fields:
            field = nested_fields[name]
            bound = copy.copy(field)

            # Build path: parent's nested_field_prefix + parent's field_name
            if self.nested_field_prefix:
                bound.nested_field_prefix = f"{self.nested_field_prefix}.{self.field_name}"
            else:
                bound.nested_field_prefix = self.field_name

            return bound
        raise AttributeError(
            f"{type(self).__name__!r} object has no attribute {name!r} "
            f"(and {self.nested_class.__name__} has no field {name!r})"
        )

    def __init__(self, nested_class: type, **kwargs: Any):
        """Initialize a nested config field.

        Args:
            nested_class: A ConfigBase subclass with ConfigField fields.
            **kwargs: Passed to ConfigFieldABC.__init__().
        """
        # Nested configs use DerivedConfigType - they aggregate values from multiple sources
        # and their individual fields handle their own persistence
        kwargs.setdefault("config_storage", DerivedConfigType)
        super().__init__(**kwargs)
        self.nested_class = nested_class

    def resolve(
        self,
        config: "DjbConfigBase",
        *,
        key_prefix: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> tuple[Any, Provenance | None]:
        """Resolve nested config by delegating to child fields.

        Each child field calls its own resolve() with the accumulated key_prefix.
        This allows each field to use its own resolution logic (validation,
        normalization, config_storage, etc.).

        Args:
            config: DjbConfigBase instance (may be partially resolved during bootstrap).
            key_prefix: Prefix from parent nested field (e.g., "hetzner" for eu field).
            env: Environment variables mapping. None means use os.environ.

        Returns:
            Tuple of (nested_instance, provenance). Provenance is (DerivedConfigType,)
            if any value came from config (since nested configs aggregate from
            multiple sources), otherwise None for defaults only.
        """
        # Build this level's prefix by combining incoming prefix with field_name
        if key_prefix:
            prefix = f"{key_prefix}.{self.field_name}"
        else:
            prefix = self.field_name

        # Let each child field resolve itself with the prefix
        resolved_values: dict[str, Any] = {}
        any_from_config = False

        for field_name, config_field in self.nested_class.__fields__.items():
            # Each child field resolves with our prefix
            value, provenance = config_field.resolve(
                config,
                key_prefix=prefix,
                env=env,
            )
            if provenance is not None:
                any_from_config = True
            resolved_values[field_name] = value

        # Create nested instance
        nested_instance = self.nested_class(**resolved_values)

        # Store config reference for @pass_config decorated methods/properties
        nested_instance._config = config

        # Return DerivedConfigType provenance if any value came from config
        # (since nested configs aggregate from multiple sources)
        result_provenance = (DerivedConfigType(config),) if any_from_config else None
        self._provenance = result_provenance  # Cache on field for DjbConfig.get_source()
        return (nested_instance, result_provenance)
