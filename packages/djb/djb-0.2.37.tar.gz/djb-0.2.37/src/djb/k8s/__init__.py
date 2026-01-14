"""
Kubernetes module for djb.

This module provides:
- Cluster provider abstraction (k3d, microk8s) for local and remote clusters
- Skaffold configuration generation for hot-reload development
- Jinja2-based template rendering for generating K8s manifests

Cluster Providers:
    ClusterProvider: Protocol for cluster implementations
    K3dProvider: Local k3d cluster (fast, ~30s startup)
    Microk8sProvider: Local or remote microk8s
    SSHConfig: Configuration for remote SSH connections
    get_cluster_provider: Factory function for getting providers

Skaffold:
    SkaffoldConfig: Configuration for Skaffold generation
    SkaffoldGenerator: Generates skaffold.yaml from config
    generate_skaffold_config: Convenience function

Manifest Generation:
    K8sManifestGenerator: Main class for rendering K8s manifests
    render_template: Project-first template resolution and rendering
    render_manifest: Deprecated, use render_template instead
    render_all_manifests: Render all manifests for a deployment

Template Contexts (runtime values, passed to templates as deploy_ctx):
    DjangoCtx: Base class for contexts that run Django (provides djb_mode)
    DeploymentCtx: For deployment.yaml (image, replicas, port, resources, etc.)
    ServiceCtx: For service.yaml (port)
    SecretsCtx: For secrets.yaml (secrets dict)
    DatabaseCtx: For cnpg-cluster.yaml (instances, size, resources)
    MigrationCtx: For migration-job.yaml (image, command)

Template Variables:
    Templates receive two context variables:
    - deploy_ctx: Template-specific context (DeploymentCtx, SecretsCtx, etc.)
    - djb_config: DjbConfig with user configuration (project_name, db_name, email)
"""

from djb.k8s.cluster import (
    Addon,
    ClusterError,
    ClusterProvider,
    K3dProvider,
    Microk8sProvider,
    SSHConfig,
    get_cluster_provider,
    register_provider,
)
from djb.k8s.generator import (
    DatabaseCtx,
    DeploymentCtx,
    DjangoCtx,
    K8sManifestGenerator,
    MigrationCtx,
    SecretsCtx,
    ServiceCtx,
    render_all_manifests,
    render_manifest,
    render_template,
)
from djb.k8s.skaffold import (
    SkaffoldConfig,
    SkaffoldGenerator,
    generate_skaffold_config,
)

__all__ = [
    # Cluster providers
    "ClusterProvider",
    "Addon",
    "K3dProvider",
    "Microk8sProvider",
    "SSHConfig",
    "get_cluster_provider",
    "register_provider",
    "ClusterError",
    # Skaffold
    "SkaffoldConfig",
    "SkaffoldGenerator",
    "generate_skaffold_config",
    # Manifest generation
    "K8sManifestGenerator",
    "render_template",
    "render_manifest",
    "render_all_manifests",
    # Template contexts
    "DjangoCtx",
    "DeploymentCtx",
    "ServiceCtx",
    "SecretsCtx",
    "DatabaseCtx",
    "MigrationCtx",
]
