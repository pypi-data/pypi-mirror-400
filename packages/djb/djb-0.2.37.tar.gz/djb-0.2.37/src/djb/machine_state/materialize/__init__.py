"""MachineStates for VPS materialization (Hetzner, local).

Barrel Exports:
    HetznerMaterializeOptions: CLI options for Hetzner materialize command
    HetznerSSHKeyResolved: SSH key is resolved and saved to config
    HetznerServerNameSet: Server name is generated and saved to config
    HetznerServerExists: Server exists in Hetzner Cloud with IP saved
    HetznerServerRunning: Server is in 'running' status
    HetznerVPSMaterialized: Composite state for full VPS provisioning
"""

from djb.machine_state.materialize.hetzner import (
    HetznerServerExists,
    HetznerServerNameSet,
    HetznerServerRunning,
    HetznerSSHKeyResolved,
    HetznerVPSMaterialized,
)
from djb.machine_state.materialize.hetzner.states import HetznerMaterializeOptions

__all__ = [
    "HetznerMaterializeOptions",
    "HetznerSSHKeyResolved",
    "HetznerServerNameSet",
    "HetznerServerExists",
    "HetznerServerRunning",
    "HetznerVPSMaterialized",
]
