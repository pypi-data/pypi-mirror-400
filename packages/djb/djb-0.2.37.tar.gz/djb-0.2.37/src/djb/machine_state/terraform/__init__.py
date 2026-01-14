"""Terraform machine states for K8s infrastructure provisioning.

This module provides declarative states for provisioning Kubernetes
infrastructure: cluster creation, addon enablement, CloudNativePG
installation, and Let's Encrypt configuration.

Main exports:
    K8sInfrastructureReady - Composite state for full infrastructure setup
    TerraformOptions - Options dataclass for ephemeral state configuration;
        most options are in DjbConfig.

Individual states:
    K8sClusterCreated - Cluster exists
    K8sClusterRunning - Cluster is running
    K8sAddonsEnabled - Required addons are enabled
    CloudNativePGInstalled - PostgreSQL operator is installed
    LetsEncryptIssuerConfigured - TLS ClusterIssuer is configured

Helpers:
    get_cluster_provider_from_context - Create ClusterProvider from context

Usage:
    from djb.machine_state.terraform import (
        K8sInfrastructureReady,
        TerraformOptions,
    )

    options = TerraformOptions(force_create=True)

    ctx = MachineContext(config=config, runner=runner, options=options)
    result = K8sInfrastructureReady().satisfy(ctx).run()
"""

from .helpers import get_cluster_provider_from_context
from .states import (
    CloudNativePGInstalled,
    K8sAddonsEnabled,
    K8sClusterCreated,
    K8sClusterRunning,
    K8sInfrastructureReady,
    LetsEncryptIssuerConfigured,
    TerraformOptions,
)

__all__ = [
    # Composite
    "K8sInfrastructureReady",
    # Options
    "TerraformOptions",
    # Leaf states
    "K8sClusterCreated",
    "K8sClusterRunning",
    "K8sAddonsEnabled",
    "CloudNativePGInstalled",
    "LetsEncryptIssuerConfigured",
    # Helpers
    "get_cluster_provider_from_context",
]
