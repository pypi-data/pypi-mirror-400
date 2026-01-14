"""
ClusterProvider protocol - abstract interface for K8s clusters.

This protocol defines the contract that all cluster implementations must follow.
It enables the same code path to work for local development (k3d, microk8s)
and production deployment (remote microk8s via SSH).

The protocol is designed for extensibility - adding support for EKS, GKE,
or other cluster types only requires implementing this interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol, runtime_checkable

from djb.core.exceptions import DjbError


class Addon(str, Enum):
    """Abstract addon names for K8s clusters.

    These are abstract requirements that providers map to concrete implementations.
    Using the same name as the concrete addon when possible.

    Provider mappings:
        Addon        | k3d                     | microk8s
        -------------|-------------------------|------------------
        DNS          | coredns (bundled)       | dns
        STORAGE      | local-storage (bundled) | storage
        INGRESS      | traefik (bundled)       | ingress
        REGISTRY     | k3d registry (bundled)  | registry
        CERT_MANAGER | cert-manager (kubectl)  | cert-manager
    """

    DNS = "dns"
    STORAGE = "storage"
    INGRESS = "ingress"
    REGISTRY = "registry"
    CERT_MANAGER = "cert-manager"


class ClusterError(DjbError):
    """Base exception for cluster operations."""


class ClusterNotFoundError(ClusterError):
    """Cluster does not exist."""


class ClusterProvisionError(ClusterError):
    """Failed to provision cluster."""


class ClusterAddonError(ClusterError):
    """Failed to enable addon."""


@dataclass(frozen=True)
class SSHConfig:
    """Configuration for remote SSH connections.

    Used to configure Microk8sProvider for remote cluster management.

    Args:
        host: SSH target in format "user@hostname" or just "hostname".
        key_path: Path to SSH private key (optional, uses ssh-agent if not specified).
        port: SSH port (default: 22).
    """

    host: str
    key_path: Path | None = None
    port: int = 22


@runtime_checkable
class ClusterProvider(Protocol):
    """Abstract interface for K8s clusters.

    Used for BOTH local development AND production deployment.

    Implementations:
    - K3dProvider: Local k3d cluster (fast, ~30s startup)
    - Microk8sProvider: Local OR remote microk8s (via SSH)
    - Future: EksProvider, GkeProvider, etc.

    The CLI commands use this interface without knowing the specific
    implementation, ensuring the cluster type distinction doesn't
    leak into the driving layer.
    """

    @property
    def name(self) -> str:
        """Human-readable name (e.g., 'k3d', 'microk8s').

        Used for logging and user messages.
        """
        ...

    @property
    def registry_address(self) -> str:
        """Registry address for pushing images.

        Returns the container registry address where images should be pushed.
        This varies by cluster type:
        - k3d: k3d-registry.localhost:5000
        - microk8s: localhost:32000 (tunneled if remote)
        """
        ...

    @property
    def is_local(self) -> bool:
        """True if cluster runs locally.

        Used to determine if SSH tunneling or port forwarding is needed.
        """
        ...

    def create(self, cluster_name: str) -> bool:
        """Create/provision the cluster.

        For local clusters, this creates a new cluster.
        For remote clusters, this installs and configures the cluster software.
        Idempotent: does nothing if cluster already exists.

        Args:
            cluster_name: Name for the cluster/namespace.

        Returns:
            True if cluster was created, False if it already existed.

        Raises:
            ClusterProvisionError: If cluster creation fails.
        """
        ...

    def start(self, cluster_name: str) -> bool:
        """Start the cluster if it's stopped.

        Idempotent: does nothing if cluster is already running.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            True if cluster was started, False if it was already running.

        Raises:
            ClusterError: If starting fails.
        """
        ...

    def delete(self, cluster_name: str) -> None:
        """Delete the cluster.

        Args:
            cluster_name: Name of the cluster to delete.

        Raises:
            ClusterError: If deletion fails.
        """
        ...

    def exists(self, cluster_name: str) -> bool:
        """Check if cluster exists.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            True if the cluster exists.
        """
        ...

    def is_running(self, cluster_name: str) -> bool:
        """Check if cluster is running and healthy.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            True if the cluster is running and healthy.
        """
        ...

    def get_kubeconfig(self, cluster_name: str) -> str:
        """Get kubeconfig for kubectl.

        Returns the kubeconfig content or path that can be used
        with kubectl. For remote clusters, this handles SSH tunneling.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            Kubeconfig content or path.

        Raises:
            ClusterNotFoundError: If cluster doesn't exist.
        """
        ...

    def enable_addons(self, cluster_name: str, addons: list[Addon]) -> None:
        """Enable cluster addons.

        Available addons vary by cluster type:
        - k3d: Uses k3d addon system
        - microk8s: dns, storage, registry, ingress, cert-manager, etc.

        Args:
            cluster_name: Name of the cluster.
            addons: List of Addon enum values to enable.

        Raises:
            ClusterAddonError: If addon enablement fails.
        """
        ...

    def get_enabled_addons(self, cluster_name: str) -> set[Addon]:
        """Get the set of enabled addons.

        Args:
            cluster_name: Name of the cluster.

        Returns:
            Set of Addon enum values that are currently enabled.
        """
        ...

    def kubectl(self, cluster_name: str, *args: str) -> tuple[int, str, str]:
        """Run kubectl command against cluster.

        Args:
            cluster_name: Name of the cluster.
            *args: kubectl arguments.

        Returns:
            Tuple of (returncode, stdout, stderr).
        """
        ...

    def apply_manifests(self, cluster_name: str, manifests: dict[str, str]) -> None:
        """Apply K8s manifests to cluster.

        Args:
            cluster_name: Name of the cluster.
            manifests: Dict of filename -> manifest content.

        Raises:
            ClusterError: If manifest application fails.
        """
        ...
