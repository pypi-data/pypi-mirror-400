"""Terraform machine state helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from djb.k8s import SSHConfig, get_cluster_provider
from djb.types import K8sClusterType

if TYPE_CHECKING:
    from djb.k8s import ClusterProvider
    from djb.machine_state import MachineContext

    from .states import TerraformOptions


def get_cluster_provider_from_context(
    ctx: MachineContext[TerraformOptions],
) -> ClusterProvider:
    """Create ClusterProvider from context config.

    All settings come from config.k8s:
    - host: If set, use SSH; if None, run locally
    - port: SSH port (default 22)
    - ssh_key: Path to SSH private key
    - cluster_type: K8s distribution (k3d, microk8s)

    Args:
        ctx: MachineContext with TerraformOptions

    Returns:
        ClusterProvider instance (k3d or microk8s)
    """
    k8s = ctx.config.k8s

    if k8s.host and k8s.cluster_type == K8sClusterType.K3D:
        raise ValueError(
            "Remote provisioning requires microk8s. "
            "Use --microk8s or set k8s.cluster_type = 'microk8s'."
        )

    if k8s.host:
        # SSH to host (any host - remote server, Hetzner VPS, etc.)
        ssh_config = SSHConfig(
            host=f"root@{k8s.host}",
            port=k8s.port,
            key_path=k8s.ssh_key,
        )
    else:
        # No host = run locally
        ssh_config = None

    return get_cluster_provider(k8s.cluster_type.value, ctx.runner, ctx.config, ssh_config)
