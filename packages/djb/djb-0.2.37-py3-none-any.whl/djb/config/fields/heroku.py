"""
HerokuConfig - Nested config for Heroku deployment settings.

This module defines the HerokuConfig dataclass used for configuring
Heroku deployment, primarily the domain names map.

Structure:
    [heroku]
    domain_names = { "example.herokuapp.com" = { manager = "heroku" } }
"""

from __future__ import annotations

from djb.config.field import ConfigBase
from djb.config.storage import ProjectConfigType
from djb.config.fields.domain_config import DomainNameConfig
from djb.config.fields.domain_names import DomainNamesMapField


class HerokuConfig(ConfigBase):
    """Nested config for Heroku deployment settings.

    Fields:
        domain_names - Map of domain names to their configuration.
            Keys are domain names, values contain metadata (manager, etc.).
            Includes the auto-generated *.herokuapp.com domain and any
            custom domains configured via `djb domain add`.

    Configured via TOML inline table:
        [heroku]
        domain_names = { "myapp-abc123.herokuapp.com" = { manager = "platform" }, "example.com" = { manager = "cloudflare" } }

        [staging.heroku]  # Mode-specific override
        domain_names = { "myapp-staging-xyz.herokuapp.com" = { manager = "platform" } }

    Used in DjbConfig as:
        heroku: HerokuConfig = NestedConfigField(HerokuConfig)

    Access values via:
        config.heroku.domain_names  # dict[str, DomainNameConfig]
        config.heroku.domain_names["example.com"].manager  # DomainNameManager.CLOUDFLARE
    """

    # Map of domain names to their configuration
    # Keys are domain names, values contain metadata (manager, etc.)
    domain_names: dict[str, DomainNameConfig] = DomainNamesMapField(
        config_storage=ProjectConfigType
    )
