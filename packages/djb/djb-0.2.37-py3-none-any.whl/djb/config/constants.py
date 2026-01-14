"""
Shared constants for the config system.

This module is a leaf module with no config package imports,
used for constants that are shared across multiple modules
where placing them in a single owner would create circular imports.
"""

from enum import Enum

# Metadata key for storing ConfigField in attrs field metadata
ATTRSLIB_METADATA_KEY = "djb_config_field"


# =============================================================================
# Hetzner Cloud Enums
# =============================================================================
# These enums define known values for Hetzner Cloud configuration.
# Used with strict=False in EnumField for forward compatibility - unknown
# values (e.g., new server types) are accepted with a warning.


class HetznerServerType(str, Enum):
    """Known Hetzner Cloud server types.

    See: https://www.hetzner.com/cloud#pricing
    """

    # ========================================================================
    # Shared Cost-Optimized
    # ========================================================================
    CX23 = "cx23"
    """
    Price: € 3.49 / month - € 0.0056 / hour 
    VCPU: 2, RAM: 4, SSD: 40, Traffic: 20 (EU), 1 (US)
    """

    CX33 = "cx33"
    """
    Price: € 5.49 / month - € 0.0088 / hour 
    VCPU: 4, RAM: 8, SSD: 80, Traffic: 20 (EU), 1 (US)
    """

    # ========================================================================
    # Shared Regular Performance
    # ========================================================================
    CPX22 = "cpx22"
    """
    Price: € 6.49 / month - € 0.0104 / hour 
    VCPU: 2, RAM: 4, SSD: 80, Traffic: 20 (EU), 1 (US)
    """

    CPX32 = "cpx32"
    """
    Price: € 10.99 / month - € 0.0176 / hour 
    VCPU: 4, RAM: 8, SSD: 160, Traffic: 20 (EU), 1 (US)
    """

    # ========================================================================
    # Dedicated General Purpose
    # ========================================================================
    CCX13 = "ccx13"
    """
    Price: € 12.49 / month - € 0.02 / hour 
    VCPU: 2, RAM: 8, SSD: 80, Traffic: 20 (EU), 1 (US)
    """
    CCX23 = "ccx23"
    """
    Price: € 24.49 / month - € 0.0392 / hour 
    VCPU: 4, RAM: 16, SSD: 160, Traffic: 20 (EU), 1 (US)
    """


class HetznerLocation(str, Enum):
    """Known Hetzner Cloud datacenter locations.

    See: https://docs.hetzner.com/cloud/general/locations
    """

    NBG1 = "nbg1"  # Nuremberg, Germany
    FSN1 = "fsn1"  # Falkenstein, Germany
    HEL1 = "hel1"  # Helsinki, Finland
    ASH = "ash"  # Ashburn, Virginia, USA
    HIL = "hil"  # Hillsboro, Oregon, USA


class HetznerImage(str, Enum):
    """Known Hetzner Cloud OS images.

    See: https://docs.hetzner.com/cloud/servers/getting-started/creating-a-server
    """

    UBUNTU_24_04 = "ubuntu-24.04"
    UBUNTU_22_04 = "ubuntu-22.04"
    UBUNTU_20_04 = "ubuntu-20.04"
    DEBIAN_12 = "debian-12"
    DEBIAN_11 = "debian-11"
    FEDORA_40 = "fedora-40"
    ROCKY_9 = "rocky-9"
    ALMA_9 = "alma-9"
