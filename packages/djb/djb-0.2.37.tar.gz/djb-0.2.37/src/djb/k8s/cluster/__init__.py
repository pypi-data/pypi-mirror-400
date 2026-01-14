"""
Cluster provider abstraction for djb K8s deployments.

This module provides a unified interface for managing Kubernetes clusters,
whether local (k3d, microk8s) or remote (microk8s via SSH). The abstraction
ensures that the CLI commands don't need to know the specific cluster type.

Design Principles:
- The k3d/microk8s distinction does NOT leak into CLI commands
- Adding a new cluster type (EKS, GKE) requires ONLY implementing ClusterProvider
- Same interface for local development and production deployment

Exports:
    ClusterProvider: Protocol defining the cluster interface
    K3dProvider: Local k3d cluster implementation
    Microk8sProvider: Local or remote microk8s implementation
    SSHConfig: Configuration for remote SSH connections
    get_cluster_provider: Factory function to get the right provider
    ClusterError: Base exception for cluster operations

Example:
    # Local k3d cluster
    provider = get_cluster_provider("k3d", cmd_runner, config)
    provider.create("myapp-dev")

    # Remote microk8s via SSH
    ssh_config = SSHConfig(host="root@server", key_path="~/.ssh/id_ed25519")
    provider = get_cluster_provider("microk8s", cmd_runner, config, ssh_config=ssh_config)
    provider.create("myapp")
"""

from djb.k8s.cluster.factory import get_cluster_provider, register_provider
from djb.k8s.cluster.k3d import K3dProvider
from djb.k8s.cluster.microk8s import Microk8sProvider
from djb.k8s.cluster.provider import Addon, ClusterError, ClusterProvider, SSHConfig

__all__ = [
    # Protocol
    "ClusterProvider",
    "Addon",
    # Implementations
    "K3dProvider",
    "Microk8sProvider",
    # Configuration
    "SSHConfig",
    # Factory
    "get_cluster_provider",
    "register_provider",
    # Errors
    "ClusterError",
]
