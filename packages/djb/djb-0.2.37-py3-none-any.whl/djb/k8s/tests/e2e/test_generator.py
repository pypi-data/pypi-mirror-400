"""Tests for K8s manifest generation."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e_marker

import base64
from typing import TYPE_CHECKING

from djb.config import DjbConfig
from djb.config.fields.domain_config import DomainNameConfig
from djb.config.fields.k8s import K8sBackendConfig, K8sConfig
from djb.k8s import (
    DatabaseCtx,
    DeploymentCtx,
    K8sManifestGenerator,
    SecretsCtx,
    ServiceCtx,
)
from djb.types import DomainNameManager

if TYPE_CHECKING:
    from collections.abc import Callable


class TestK8sManifestGenerator:
    """Tests for K8s manifest generation."""

    def test_render_namespace(self, make_djb_config: Callable[..., DjbConfig]) -> None:
        """Test rendering namespace manifest."""
        djb_config = make_djb_config(DjbConfig(project_name="myapp"))
        generator = K8sManifestGenerator()
        manifest = generator.render("namespace.yaml.j2", djb_config)

        assert "kind: Namespace" in manifest
        assert "name: myapp" in manifest
        assert "app.kubernetes.io/managed-by: djb" in manifest

    def test_render_deployment(self, make_djb_config: Callable[..., DjbConfig]) -> None:
        """Test rendering deployment manifest."""
        deploy_ctx = DeploymentCtx(
            image="localhost:32000/myapp:abc123",
            replicas=2,
            port=8000,
        )
        djb_config = make_djb_config()
        generator = K8sManifestGenerator()
        manifest = generator.render("deployment.yaml.j2", djb_config, deploy_ctx)

        assert "kind: Deployment" in manifest
        assert "replicas: 2" in manifest
        assert "containerPort: 8000" in manifest
        assert "localhost:32000/myapp:abc123" in manifest

    def test_render_service(self, make_djb_config: Callable[..., DjbConfig]) -> None:
        """Test rendering service manifest."""
        service_ctx = ServiceCtx(port=8000)
        djb_config = make_djb_config()
        generator = K8sManifestGenerator()
        manifest = generator.render("service.yaml.j2", djb_config, service_ctx)

        assert "kind: Service" in manifest
        assert "type: ClusterIP" in manifest
        assert "targetPort: 8000" in manifest

    def test_render_ingress_with_tls(self, make_djb_config: Callable[..., DjbConfig]) -> None:
        """Test rendering ingress manifest with TLS."""
        djb_config = make_djb_config(
            DjbConfig(
                project_name="myapp",
                k8s=K8sConfig(
                    domain_names={
                        "myapp.example.com": DomainNameConfig(manager=DomainNameManager.CLOUDFLARE)
                    },
                    backend=K8sBackendConfig(
                        managed_dockerfile=True,
                        remote_build=True,
                        buildpacks=["python:3.14-slim"],
                        buildpack_registry="localhost:32000",
                    ),
                    db_name="",
                ),
                email="admin@example.com",
            )
        )
        generator = K8sManifestGenerator()
        manifest = generator.render("ingress.yaml.j2", djb_config)

        assert "kind: Ingress" in manifest
        assert "host: myapp.example.com" in manifest
        assert "host: www.myapp.example.com" in manifest
        assert "secretName: myapp-1-tls" in manifest
        assert "cert-manager.io/cluster-issuer" in manifest

    def test_render_ingress_without_email(self) -> None:
        """Test rendering ingress manifest without email skips TLS."""
        # Create config directly without resolution to ensure email=None
        # (get_djb_config would resolve email from git config)
        djb_config = DjbConfig(
            project_name="myapp",
            k8s=K8sConfig(
                domain_names={
                    "myapp.example.com": DomainNameConfig(manager=DomainNameManager.CLOUDFLARE)
                },
                backend=K8sBackendConfig(
                    managed_dockerfile=True,
                    remote_build=True,
                    buildpacks=["python:3.14-slim"],
                    buildpack_registry="localhost:32000",
                ),
                db_name="",
            ),
            email=None,
        )
        generator = K8sManifestGenerator()
        manifest = generator.render("ingress.yaml.j2", djb_config)

        assert "kind: Ingress" in manifest
        assert "host: myapp.example.com" in manifest
        # Should not have TLS since no email
        assert "cert-manager.io/cluster-issuer" not in manifest

    def test_render_secrets(self, make_djb_config: Callable[..., DjbConfig]) -> None:
        """Test rendering secrets manifest with base64 encoding."""
        secrets_ctx = SecretsCtx(secrets={"API_KEY": "secret123", "DB_PASSWORD": "pass456"})
        djb_config = make_djb_config()
        generator = K8sManifestGenerator()
        manifest = generator.render("secrets.yaml.j2", djb_config, secrets_ctx)

        assert "kind: Secret" in manifest
        assert "type: Opaque" in manifest
        # Secrets should be base64 encoded
        assert base64.b64encode(b"secret123").decode() in manifest
        assert base64.b64encode(b"pass456").decode() in manifest

    def test_render_cnpg_cluster(self, make_djb_config: Callable[..., DjbConfig]) -> None:
        """Test rendering CloudNativePG cluster manifest."""
        db_ctx = DatabaseCtx(size="20Gi", instances=2)
        djb_config = make_djb_config()
        generator = K8sManifestGenerator()
        manifest = generator.render("cnpg-cluster.yaml.j2", djb_config, db_ctx)

        assert "kind: Cluster" in manifest
        assert "apiVersion: postgresql.cnpg.io/v1" in manifest
        assert "instances: 2" in manifest
        assert "size: 20Gi" in manifest

    def test_render_cnpg_cluster_uses_db_name(
        self, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Test that CNPG cluster uses db_name for database and owner."""
        db_ctx = DatabaseCtx()
        # Project name with hyphen - db_name should replace with underscore
        djb_config = make_djb_config(DjbConfig(project_name="my-app"))
        generator = K8sManifestGenerator()
        manifest = generator.render("cnpg-cluster.yaml.j2", djb_config, db_ctx)

        # Project name stays as-is for k8s resources
        assert "name: my-app-db" in manifest
        assert "namespace: my-app" in manifest
        # Database name uses underscore (PostgreSQL requirement)
        assert "database: my_app" in manifest
        assert "owner: my_app" in manifest

    def test_render_cnpg_cluster_with_custom_db_name(
        self, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Test that custom db_name from config is used."""
        db_ctx = DatabaseCtx()
        djb_config = make_djb_config(
            DjbConfig(
                project_name="my-app",
                k8s=K8sConfig(
                    domain_names={},
                    backend=K8sBackendConfig(
                        managed_dockerfile=True,
                        remote_build=True,
                        buildpacks=["python:3.14-slim"],
                        buildpack_registry="localhost:32000",
                    ),
                    db_name="custom_database",
                ),
            )
        )
        generator = K8sManifestGenerator()
        manifest = generator.render("cnpg-cluster.yaml.j2", djb_config, db_ctx)

        # Custom db_name should be used
        assert "database: custom_database" in manifest
        assert "owner: custom_database" in manifest

    def test_render_all_manifests_with_domains(
        self, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Test rendering all manifests includes ingress when domains configured."""
        deployment_ctx = DeploymentCtx(
            image="localhost:32000/myapp:abc123",
            has_secrets=True,
        )
        secrets_ctx = SecretsCtx(secrets={"API_KEY": "secret123"})
        db_ctx = DatabaseCtx()
        djb_config = make_djb_config(
            DjbConfig(
                project_name="myapp",
                k8s=K8sConfig(
                    domain_names={
                        "myapp.example.com": DomainNameConfig(manager=DomainNameManager.CLOUDFLARE)
                    },
                    backend=K8sBackendConfig(
                        managed_dockerfile=True,
                        remote_build=True,
                        buildpacks=["python:3.14-slim"],
                        buildpack_registry="localhost:32000",
                    ),
                    db_name="",
                ),
            )
        )
        generator = K8sManifestGenerator()
        manifests = generator.render_all(
            djb_config,
            deployment=deployment_ctx,
            secrets=secrets_ctx,
            database=db_ctx,
        )

        assert "namespace.yaml" in manifests
        assert "deployment.yaml" in manifests
        assert "service.yaml" in manifests
        assert "ingress.yaml" in manifests  # Included because domains configured
        assert "secrets.yaml" in manifests
        assert "cnpg-cluster.yaml" in manifests

    def test_render_all_manifests_without_domains(
        self, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Test rendering all manifests excludes ingress when no domains."""
        deployment_ctx = DeploymentCtx(
            image="localhost:32000/myapp:abc123",
            has_secrets=True,
        )
        secrets_ctx = SecretsCtx(secrets={"API_KEY": "secret123"})
        db_ctx = DatabaseCtx()
        # Default K8sConfig has empty domains
        djb_config = make_djb_config()
        generator = K8sManifestGenerator()
        manifests = generator.render_all(
            djb_config,
            deployment=deployment_ctx,
            secrets=secrets_ctx,
            database=db_ctx,
        )

        assert "namespace.yaml" in manifests
        assert "deployment.yaml" in manifests
        assert "service.yaml" in manifests
        # No ingress without domains
        assert "ingress.yaml" not in manifests
        assert "secrets.yaml" in manifests
        assert "cnpg-cluster.yaml" in manifests

    def test_render_without_optional_components(
        self, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Test rendering without optional components."""
        deployment_ctx = DeploymentCtx(
            image="localhost:32000/myapp:abc123",
        )
        djb_config = make_djb_config()
        generator = K8sManifestGenerator()
        manifests = generator.render_all(djb_config, deployment=deployment_ctx)

        # Core manifests should be present
        assert "namespace.yaml" in manifests
        assert "deployment.yaml" in manifests
        assert "service.yaml" in manifests

        # Optional manifests should not be present
        assert "ingress.yaml" not in manifests
        assert "secrets.yaml" not in manifests
        assert "cnpg-cluster.yaml" not in manifests
