"""
SecretsConfig - Nested config for secrets encryption settings.

This module defines the SecretsConfig dataclass used for configuring
secrets encryption behavior per mode.
"""

from __future__ import annotations

from djb.config.field import ConfigBase
from djb.config.fields.bool import BoolField
from djb.config.storage import ProjectConfigType


class SecretsConfig(ConfigBase):
    """Nested config for secrets settings.

    Fields:
        encrypt - Whether to encrypt secrets with SOPS/age (default: True)

    Configured via TOML sections:
        [secrets]
        encrypt = true

        [development.secrets]
        encrypt = false  # Disable encryption for development

    Used in DjbConfig as:
        secrets: SecretsConfig = NestedConfigField(SecretsConfig)

    Access values via:
        config.secrets.encrypt  # True or False based on mode
    """

    encrypt: bool = BoolField(config_storage=ProjectConfigType, default=True)
