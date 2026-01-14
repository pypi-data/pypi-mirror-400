"""
DomainNamesMapField - Field for domain names map with metadata.

This module provides a field type for handling domain name mappings
where each domain has associated configuration (like DNS manager).

Structure:
    [heroku]
    domain_names = { "example.com" = { manager = "cloudflare" } }
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from djb.config.field import ConfigFieldABC, ConfigValidationError
from djb.config.fields.domain import DomainNameField
from djb.config.fields.domain_config import DomainNameConfig
from djb.types import DomainNameManager

if TYPE_CHECKING:
    pass


class DomainNamesMapField(ConfigFieldABC):
    """Field for domain names map with per-domain configuration.

    Takes a dict mapping domain names to their config (manager, etc.).

    Example usage:
        domain_names: dict[str, DomainNameConfig] = DomainNamesMapField(
            config_file="project"
        )()

    Configured via TOML inline table:
        [heroku]
        domain_names = { "example.com" = { manager = "cloudflare" } }
    """

    def __init__(self, **kwargs: Any):
        """Initialize a domain names map field.

        Args:
            **kwargs: Passed to ConfigFieldABC.__init__().
        """
        # Default to empty dict if not specified
        if "default" not in kwargs:
            kwargs["default"] = {}
        super().__init__(**kwargs)
        # Create validator for domain names
        self._domain_validator = DomainNameField()

    def get_default(self) -> dict[str, DomainNameConfig]:
        """Get the default value (empty dict if none specified)."""
        default = super().get_default()
        if default is None:
            return {}
        return dict(default)  # Return a copy to avoid mutation

    def normalize(self, value: Any) -> dict[str, DomainNameConfig]:
        """Normalize value to a domain names map.

        Handles:
        - None -> empty dict
        - Dict -> parse each value into DomainNameConfig
        """
        if value is None:
            return {}

        if not isinstance(value, dict):
            raise ConfigValidationError(
                f"{self.field_name} must be a dict, got: {type(value).__name__}"
            )

        # Parse dict format
        result = {}
        for domain, config in value.items():
            if not isinstance(domain, str):
                raise ConfigValidationError(
                    f"{self.field_name} keys must be strings, got: {type(domain).__name__}"
                )

            # Parse config dict into DomainNameConfig
            if isinstance(config, dict):
                manager_str = config.get("manager", "manual")
                manager = DomainNameManager.parse(manager_str, DomainNameManager.MANUAL)
                if manager is None:
                    manager = DomainNameManager.MANUAL
                result[domain] = DomainNameConfig(manager=manager)
            elif isinstance(config, DomainNameConfig):
                result[domain] = config
            else:
                # Unknown format, use manual
                result[domain] = DomainNameConfig(manager=DomainNameManager.MANUAL)

        return result

    def validate(self, value: Any) -> None:
        """Validate that value is a valid domain names map."""
        if value is None:
            return

        if not isinstance(value, dict):
            raise ConfigValidationError(
                f"{self.field_name} must be a dict, got: {type(value).__name__}"
            )

        # Validate each domain name
        for domain in value.keys():
            self._domain_validator.field_name = f"{self.field_name}[{domain!r}]"
            self._domain_validator.validate(domain)

            # Validate config
            config = value[domain]
            if not isinstance(config, DomainNameConfig):
                raise ConfigValidationError(
                    f"{self.field_name}[{domain!r}] must be DomainNameConfig, "
                    f"got: {type(config).__name__}"
                )

    def serialize(self, value: Any) -> dict[str, dict[str, str]]:
        """Serialize DomainNameConfig objects to TOML-compatible dicts."""
        if value is None:
            return {}

        return {domain: {"manager": config.manager.value} for domain, config in value.items()}
