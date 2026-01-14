"""
CloudflareConfig - Nested config for Cloudflare DNS settings.

This module defines the CloudflareConfig dataclass used for configuring
Cloudflare DNS behavior during deployments.

Structure:
    [cloudflare]
    auto_dns = true   # Auto-configure DNS during deploy
    ttl = 60          # Low TTL for easy IP changes
    proxied = false   # DNS-only, no Cloudflare proxy

The API token is stored in secrets (secrets/production.enc.env) not config.
"""

from __future__ import annotations

from djb.config.field import ConfigBase
from djb.config.storage import ProjectConfigType
from djb.config.fields.bool import BoolField
from djb.config.fields.int import IntField


class CloudflareConfig(ConfigBase):
    """Nested config for Cloudflare DNS settings.

    Fields:
        auto_dns - If True, auto-configure DNS during `djb deploy k8s`
            and `djb deploy heroku` commands. (default: True)
        ttl - TTL in seconds for DNS records. Low value (60) allows
            quick IP changes. (default: 60)
        proxied - If True, traffic flows through Cloudflare's proxy
            (enables CDN, WAF). If False, DNS-only mode. (default: False)

    The Cloudflare API token is stored in secrets:
        djb secrets set cloudflare.api_token

    Configured via TOML sections:
        [cloudflare]
        auto_dns = true
        ttl = 60
        proxied = false

    Used in DjbConfig as:
        cloudflare: CloudflareConfig = NestedConfigField(CloudflareConfig)

    Access values via:
        config.cloudflare.auto_dns  # True by default
        config.cloudflare.ttl       # 60 by default
        config.cloudflare.proxied   # False by default
    """

    # Auto-configure DNS during deploy commands
    auto_dns: bool = BoolField(config_storage=ProjectConfigType, default=True)

    # TTL in seconds for DNS records (60 = minimum, easy IP changes)
    ttl: int = IntField(config_storage=ProjectConfigType, default=60)

    # Whether to proxy through Cloudflare (CDN, WAF) or DNS-only
    proxied: bool = BoolField(config_storage=ProjectConfigType, default=False)
