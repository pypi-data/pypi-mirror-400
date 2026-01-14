"""
Factory function for creating ClusterProvider instances.

The factory pattern enables:
- Consistent interface for getting cluster providers
- Easy extensibility for new cluster types
- Runtime registration of custom providers
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from djb.k8s.cluster.k3d import K3dProvider
from djb.k8s.cluster.microk8s import Microk8sProvider
from djb.k8s.cluster.provider import ClusterProvider, SSHConfig

if TYPE_CHECKING:
    from djb.config import DjbConfig
    from djb.core.cmd_runner import CmdRunner

# Registry of available providers
_PROVIDERS: dict[str, type] = {
    "k3d": K3dProvider,
    "microk8s": Microk8sProvider,
}


def register_provider(name: str, provider_class: type) -> None:
    """Register a custom cluster provider.

    Use this to add support for additional cluster types like EKS, GKE, etc.

    Args:
        name: Provider name (e.g., "eks", "gke").
        provider_class: Class that implements ClusterProvider protocol.

    Example:
        from djb.k8s.cluster import register_provider

        class EksProvider:
            # ... implement ClusterProvider protocol ...
            pass

        register_provider("eks", EksProvider)
    """
    _PROVIDERS[name] = provider_class


def get_cluster_provider(
    cluster_type: str,
    cmd_runner: "CmdRunner",
    config: "DjbConfig",
    ssh_config: SSHConfig | None = None,
) -> ClusterProvider:
    """Factory function to get a cluster provider.

    This is the main entry point for getting cluster providers. The CLI
    commands use this function without needing to know which specific
    provider implementation is being used.

    Args:
        cluster_type: Type of cluster ("k3d" or "microk8s").
        cmd_runner: Command runner instance for executing shell commands.
        config: DjbConfig instance for accessing configuration values.
        ssh_config: SSH configuration for remote clusters.
                    Only applicable to microk8s.

    Returns:
        ClusterProvider instance.

    Raises:
        ValueError: If cluster_type is unknown.
        ValueError: If ssh_config is provided for a local-only provider.

    Examples:
        # Local k3d cluster
        provider = get_cluster_provider("k3d", cmd_runner, config)

        # Local microk8s
        provider = get_cluster_provider("microk8s", cmd_runner, config)

        # Remote microk8s via SSH
        ssh_config = SSHConfig(
            host="root@server",
            key_path=Path("~/.ssh/id_ed25519"),
        )
        provider = get_cluster_provider("microk8s", cmd_runner, config, ssh_config=ssh_config)
    """
    if cluster_type not in _PROVIDERS:
        available = ", ".join(sorted(_PROVIDERS.keys()))
        raise ValueError(
            f"Unknown cluster type: '{cluster_type}'. " f"Available types: {available}"
        )

    provider_class = _PROVIDERS[cluster_type]

    # Handle SSH config
    if ssh_config is not None:
        if cluster_type == "k3d":
            raise ValueError(
                "k3d is a local-only provider and does not support SSH. "
                "Use 'microk8s' for remote clusters."
            )
        # Microk8sProvider accepts ssh_config
        return provider_class(cmd_runner, config, ssh_config=ssh_config)

    # Local provider
    if cluster_type == "microk8s":
        return provider_class(cmd_runner, config, ssh_config=None)

    return provider_class(cmd_runner, config)


def list_providers() -> list[str]:
    """List available cluster provider types.

    Returns:
        List of registered provider names.
    """
    return sorted(_PROVIDERS.keys())
