"""
DomainNameConfig - Configuration for a single domain name.

This module defines the DomainNameConfig dataclass that stores metadata
about a domain, primarily which DNS manager handles it.

Used as values in the domain_names map:
    [heroku]
    domain_names = { "example.com" = { manager = "cloudflare" } }
"""

from __future__ import annotations

from djb.config.field import ConfigBase
from djb.config.fields.enum import EnumField
from djb.types import DomainNameManager


class DomainNameConfig(ConfigBase):
    """Configuration for a single domain name.

    Fields:
        manager - DNS management provider for this domain.
            - cloudflare: Managed via Cloudflare API
            - heroku: Managed via Heroku (for *.herokuapp.com)
            - manual: No automatic DNS management

    Used in domain_names map within HerokuConfig/K8sConfig:
        domain_names = { "example.com" = { manager = "cloudflare" } }

    Access values via:
        config.heroku.domain_names["example.com"].manager  # DomainNameManager.CLOUDFLARE
    """

    # DNS management provider for this domain
    manager: DomainNameManager = EnumField(DomainNameManager, default=DomainNameManager.MANUAL)
