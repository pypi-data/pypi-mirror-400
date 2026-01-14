"""
HetznerConfig - Nested config for Hetzner Cloud settings.

This module defines the HetznerConfig dataclass used for configuring
Hetzner Cloud server provisioning defaults and instance state.

Fields are split into two categories:
- Default fields (config_file="core"): Provisioning defaults from core.toml
- Instance fields (config_file="project"): Server state from materialize command
"""

from __future__ import annotations

from djb.config.constants import (
    HetznerImage,
    HetznerLocation,
    HetznerServerType,
)
from djb.config.field import ConfigBase, StringField
from djb.config.storage import CoreConfigIO, ProjectConfigType
from djb.config.fields.enum import EnumField


class HetznerConfig(ConfigBase):
    """Nested config for Hetzner Cloud settings.

    Default fields (from core.toml, overridable via project/local):
        default_server_type - Server type for provisioning (e.g., "cx22")
        default_location - Datacenter location (e.g., "nbg1")
        default_image - OS image (e.g., "ubuntu-24.04")

    Instance fields (from project.toml, populated by materialize command):
        server_name - Name of the provisioned server
        ssh_key_name - SSH key used for the server
        server_type - Actual server type the server is running on
        location - Actual datacenter location
        image - Actual OS image

    Computed properties (use effective_* to get the right value):
        effective_server_type - instance value or default
        effective_location - instance value or default
        effective_image - instance value or default

    Configured via TOML sections:
        [hetzner]                    # Production defaults/instance
        default_server_type = "cx22"
        default_location = "nbg1"
        default_image = "ubuntu-24.04"
        server_name = "myproject-prod"
        server_type = "cx22"
        location = "nbg1"
        image = "ubuntu-24.04"

        [staging.hetzner]            # Staging overrides
        server_name = "myproject-staging"
        server_type = "cx32"

    Used in DjbConfig as:
        hetzner: HetznerConfig = NestedConfigField(HetznerConfig)()

    Access values via:
        config.hetzner.default_server_type  # "cx22" from core.toml
        config.hetzner.server_name          # None or provisioned name
        config.hetzner.effective_server_type  # instance value or default
    """

    # === Default fields (config_file="core") ===
    # Defined in core.toml, can be overridden in project/local.
    # CLI writes require --project or --local flag.

    default_server_type: str = EnumField(
        HetznerServerType,
        strict=False,
        config_storage=CoreConfigIO,
        default=HetznerServerType.CX23,
    )
    default_location: str = EnumField(
        HetznerLocation,
        strict=False,
        config_storage=CoreConfigIO,
        default=HetznerLocation.NBG1,
    )
    default_image: str = EnumField(
        HetznerImage,
        strict=False,
        config_storage=CoreConfigIO,
        default=HetznerImage.UBUNTU_24_04,
    )

    # === Project fields (config_file="project") ===
    # Populated by `djb deploy k8s materialize` command.
    # Mode-specific (stored in [staging.hetzner] for staging mode, etc.)

    server_name: str | None = StringField(config_storage=ProjectConfigType, default=None)
    """Name of the provisioned server (e.g., 'myproject-staging')."""

    ssh_key_name: str | None = StringField(config_storage=ProjectConfigType, default=None)
    """SSH key name registered with Hetzner Cloud for server access."""

    # Actual server config - set after creation so we know what it's running on
    server_type: str | None = EnumField(
        HetznerServerType,
        strict=False,
        config_storage=ProjectConfigType,
        default=None,
    )
    location: str | None = EnumField(
        HetznerLocation,
        strict=False,
        config_storage=ProjectConfigType,
        default=None,
    )
    image: str | None = EnumField(
        HetznerImage,
        strict=False,
        config_storage=ProjectConfigType,
        default=None,
    )

    # === Computed properties ===

    @property
    def effective_server_type(self) -> str:
        """Server type: instance value > default."""
        return self.server_type or self.default_server_type

    @property
    def effective_location(self) -> str:
        """Location: instance value > default."""
        return self.location or self.default_location

    @property
    def effective_image(self) -> str:
        """Image: instance value > default."""
        return self.image or self.default_image
