"""
K8sConfig - Nested config for Kubernetes deployment settings.

This module defines K8s deployment configuration with domain names and backend settings.

Structure:
    [k8s]
    domain_names = { "example.com" = { manager = "cloudflare" } }

    [k8s.backend]
    managed_dockerfile = true
    remote_build = true
    buildpacks = ["python:3.14-slim", "gdal:v1"]
    buildpack_registry = "localhost:32000"
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from djb.config.field import ConfigBase, StringField, pass_config

if TYPE_CHECKING:
    from djb.config import DjbConfig
from djb.config.fields.bool import BoolField
from djb.config.fields.domain_config import DomainNameConfig
from djb.config.fields.domain_names import DomainNamesMapField
from djb.config.fields.enum import EnumField
from djb.config.fields.int import IntField
from djb.config.fields.list import ListField
from djb.config.fields.nested import NestedConfigField
from djb.config.fields.path import PathField
from djb.config.storage import CoreConfigIO, ProjectConfigType
from djb.types import K8sClusterType, K8sProvider


class K8sBackendConfig(ConfigBase):
    """Nested config for K8s backend deployment settings.

    Fields:
        managed_dockerfile - If True, djb manages the Dockerfile template
            and will copy/update it. If False, djb won't overwrite an
            existing Dockerfile.
        remote_build - If True, build Docker images on the remote server
            (native x86_64, no QEMU). If False, build locally and transfer.
        buildpacks - List of buildpack images to chain (e.g., ["python:3.14-slim", "gdal:v1"]).
            Each buildpack builds FROM the previous one. The final image becomes
            the base for the application layer.
        buildpack_registry - Registry host for buildpack images (default: localhost:32000).

    Configured via TOML sections:
        [k8s.backend]
        managed_dockerfile = true
        remote_build = true
        buildpacks = ["python:3.14-slim", "gdal:v1", "postgresql:v1"]
        buildpack_registry = "localhost:32000"

    Access values via:
        config.k8s.backend.managed_dockerfile  # True by default
        config.k8s.backend.remote_build  # True by default
        config.k8s.backend.buildpacks  # ["python:3.14-slim"] by default
        config.k8s.backend.buildpack_registry  # "localhost:32000" by default
    """

    # If True, djb manages the Dockerfile template and can update it.
    # If False, djb won't overwrite an existing Dockerfile.
    managed_dockerfile: bool = BoolField(config_storage=ProjectConfigType, default=True)

    # If True, build on remote server (native x86_64). If False, build locally.
    remote_build: bool = BoolField(config_storage=ProjectConfigType, default=True)

    # Chained buildpack images. Each builds FROM the previous.
    # Format: ["name:version", ...] e.g., ["python:3.14-slim", "gdal:v1"]
    buildpacks: list[str] = ListField(
        StringField, config_storage=ProjectConfigType, default=["python:3.14-slim"]
    )

    # Registry for buildpack images.
    buildpack_registry: str = StringField(
        config_storage=ProjectConfigType, default="localhost:32000"
    )


class K8sConfig(ConfigBase):
    """Nested config for Kubernetes deployment settings.

    Fields:
        provider - Cloud provider for VPS provisioning: "manual" or "hetzner".
            "manual" requires explicit --host for remote deployments.
            "hetzner" auto-provisions a VPS via Hetzner Cloud API.
        domain_names - Map of domain names to their configuration.
            Keys are domain names, values contain metadata (manager, etc.).
            Configured via `djb domain add` with Cloudflare DNS.
        db_name - Optional PostgreSQL database/owner name override.
            If not set, derived from project_name by replacing hyphens
            with underscores (PostgreSQL identifier requirement).
        cluster_name - K8s cluster name. If not set, derived as f"djb-{project_name}".
        cluster_type - K8s distribution: "k3d" (default) or "microk8s".
        host - SSH host for remote access. If set, commands run via SSH.
            If None, commands run locally.
        port - SSH port (default: 22).
        ssh_key - Path to SSH private key.
        no_cloudnativepg - Skip CloudNativePG operator installation.
        no_tls - Skip Let's Encrypt TLS setup.
        cnpg_manifest_url - CloudNativePG operator manifest URL.
        cert_manager_manifest_url - cert-manager manifest URL for TLS support.
        kubectl_wait_timeout_s - Kubectl wait timeout in seconds (default: 120).

    Contains sub-configs for backend and (future) frontend deployments.

    Configured via TOML inline table:
        [k8s]
        provider = "hetzner"  # or "manual" (default)
        cluster_type = "microk8s"  # or "k3d" (default)
        host = "192.168.1.100"  # for remote access
        domain_names = { "example.com" = { manager = "cloudflare" } }

        [k8s.backend]
        managed_dockerfile = true

    Used in DjbConfig as:
        k8s: K8sConfig = NestedConfigField(K8sConfig)

    Access values via:
        config.k8s.provider  # K8sProvider.MANUAL by default
        config.k8s.cluster_type  # K8sClusterType.K3D by default
        config.k8s.host  # None by default (local mode)
        config.k8s.domain_names  # dict[str, DomainNameConfig]
        config.k8s.backend.managed_dockerfile  # True by default
    """

    # Cloud provider for VPS provisioning
    provider: K8sProvider = EnumField(
        K8sProvider, config_storage=ProjectConfigType, default=K8sProvider.MANUAL
    )

    # Map of domain names to their configuration
    # Keys are domain names, values contain metadata (manager, etc.)
    domain_names: dict[str, DomainNameConfig] = DomainNamesMapField(
        config_storage=ProjectConfigType
    )

    # Backend deployment settings (Django/Python)
    backend: K8sBackendConfig = NestedConfigField(K8sBackendConfig)

    # Optional PostgreSQL database/owner name override
    # If empty, derived from project_name (hyphens replaced with underscores)
    db_name: str = StringField(config_storage=ProjectConfigType, default="")

    # K8s cluster name (e.g., "djb-myproject")
    # If not set, derived from project_name as f"djb-{project_name}"
    cluster_name: str | None = StringField(config_storage=ProjectConfigType, default=None)

    # K8s distribution type
    cluster_type: K8sClusterType = EnumField(
        K8sClusterType, config_storage=ProjectConfigType, default=K8sClusterType.K3D
    )

    # SSH settings for remote access
    # If host is set, commands run via SSH; if None, commands run locally
    host: str | None = StringField(config_storage=ProjectConfigType, default=None)
    port: int = IntField(config_storage=ProjectConfigType, default=22)
    ssh_key: Path | None = PathField(config_storage=ProjectConfigType, default=None)

    # Feature flags
    no_cloudnativepg: bool = BoolField(config_storage=ProjectConfigType, default=False)
    no_tls: bool = BoolField(config_storage=ProjectConfigType, default=False)

    # Cluster operator settings (defaults in core.toml)
    cnpg_manifest_url: str = StringField(config_storage=CoreConfigIO)
    cert_manager_manifest_url: str = StringField(config_storage=CoreConfigIO)
    kubectl_wait_timeout_s: int = IntField(config_storage=CoreConfigIO)

    @property
    def is_public(self) -> bool:
        """True if this is a public-facing deployment (has remote host)."""
        return self.host is not None

    @pass_config.property
    def effective_cluster_name(self, config: "DjbConfig") -> str:
        """Cluster name, falling back to djb-{project_name}."""
        return self.cluster_name or f"djb-{config.project_name}"
