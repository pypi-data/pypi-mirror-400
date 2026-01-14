"""
Cloud provider module for djb K8s deployments.

This module provides cloud provider abstractions for provisioning VPS instances
that can be used for Kubernetes deployments.

Exports:
    CloudProviderProtocol: Protocol for cloud provider implementations
    ServerInfo: Dataclass with server information
    HetznerCloudProvider: Hetzner Cloud implementation
    HetznerError: Hetzner-specific errors

Note: Cloudflare DNS has been moved to djb.dns module (it's not K8s-specific).
"""

from djb.k8s.cloud.hetzner import HetznerCloudProvider, HetznerError
from djb.k8s.cloud.provider import CloudProviderProtocol, ServerInfo

__all__ = [
    "CloudProviderProtocol",
    "HetznerCloudProvider",
    "HetznerError",
    "ServerInfo",
]
