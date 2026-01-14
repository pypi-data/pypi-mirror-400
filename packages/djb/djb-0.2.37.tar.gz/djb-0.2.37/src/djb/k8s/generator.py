"""
Kubernetes manifest generator using Jinja2 templates.

Renders K8s manifests from templates with project-specific configuration.
Templates are stored in the templates/ subdirectory.

Template Variables:
    Templates receive two context variables:
    - deploy_ctx: Template-specific runtime context (DeploymentCtx, SecretsCtx, etc.)
    - djb_config: DjbConfig with user configuration (project_name, db_name, email, etc.)

    Templates access config values from djb_config:
    - {{ djb_config.project_name }}, {{ djb_config.db_name }}
    - {{ djb_config.k8s.domain_names }}, {{ djb_config.email }}

    Runtime values come from deploy_ctx:
    - {{ deploy_ctx.image }}, {{ deploy_ctx.replicas }}
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from djb.templates import BUILDPACKS_DOCKERFILES_DIR, DJB_TEMPLATES_DIR
from djb.types import Mode

if TYPE_CHECKING:
    from djb.config import DjbConfig


# Template directory path
TEMPLATES_DIR = Path(__file__).parent / "templates"


# =============================================================================
# Template-specific context dataclasses
# =============================================================================


@dataclass
class DjangoCtx:
    """Base context for templates that run Django code.

    Provides djb_mode for environment detection in Django settings.
    Mode is a str subclass, so {{ deploy_ctx.djb_mode }} renders as the value.
    """

    djb_mode: Mode = Mode.PRODUCTION


@dataclass
class DeploymentCtx(DjangoCtx):
    """Runtime context for deployment.yaml template.

    Config values like project_name come from djb_config.
    """

    image: str = ""  # Required, but default needed for dataclass inheritance
    replicas: int = 1
    port: int = 8000
    resources: dict[str, Any] = field(
        default_factory=lambda: {
            "requests": {"memory": "256Mi", "cpu": "100m"},
            "limits": {"memory": "512Mi", "cpu": "500m"},
        }
    )
    health_path: str = "/health/"
    env_vars: dict[str, str] = field(default_factory=dict)
    # Boolean flags for conditional rendering (actual secrets are in SecretsCtx)
    has_secrets: bool = False
    has_database: bool = False
    # Timestamp to force pod restart on each deploy (even with same image tag)
    deploy_timestamp: str = ""


@dataclass
class ServiceCtx:
    """Runtime context for service.yaml template."""

    port: int = 8000


@dataclass
class SecretsCtx:
    """Runtime context for secrets.yaml template."""

    secrets: dict[str, str] = field(default_factory=dict)


@dataclass
class DatabaseCtx:
    """Runtime context for cnpg-cluster.yaml template."""

    instances: int = 1
    size: str = "10Gi"
    storage_class: str | None = None
    memory: str = "256Mi"
    cpu: str = "100m"
    memory_limit: str = "512Mi"
    cpu_limit: str = "500m"


@dataclass
class MigrationCtx(DjangoCtx):
    """Runtime context for migration-job.yaml template."""

    image: str = ""  # Required, but default needed for dataclass inheritance
    command: str = "python manage.py migrate --noinput"
    has_secrets: bool = False
    env_vars: dict[str, str] = field(default_factory=dict)


class K8sManifestGenerator:
    """Generator for Kubernetes manifests using Jinja2 templates.

    Templates receive two context variables:
    - deploy_ctx: Template-specific runtime context (DeploymentCtx, SecretsCtx, etc.)
    - djb_config: DjbConfig with user configuration (project_name, db_name, email, etc.)

    Example:
        generator = K8sManifestGenerator()
        deployment_ctx = DeploymentCtx(image="localhost:32000/myapp:abc123")
        deployment = generator.render("deployment.yaml.j2", deployment_ctx, djb_config)
    """

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the generator.

        Args:
            templates_dir: Custom templates directory (default: built-in templates).
        """
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["yaml", "yml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters
        self.env.filters["b64encode"] = self._b64encode

    @staticmethod
    def _b64encode(value: str | dict | list) -> str:
        """Base64 encode a value for K8s secrets.

        Handles both strings and nested structures (dicts/lists) by
        JSON-encoding non-string values first.
        """
        if isinstance(value, str):
            data = value
        else:
            # Serialize nested structures to JSON
            data = json.dumps(value, separators=(",", ":"))
        return base64.b64encode(data.encode()).decode()

    def render(
        self,
        template_name: str,
        djb_config: DjbConfig,
        deploy_ctx: Any = None,
    ) -> str:
        """Render a single template.

        Args:
            template_name: Name of the template file (e.g., "deployment.yaml.j2").
            djb_config: User configuration (project_name, db_name, email, etc.).
            deploy_ctx: Template-specific runtime context. Can be None for templates
                that only use djb_config (e.g., namespace.yaml.j2).

        Returns:
            Rendered YAML manifest.
        """
        template = self.env.get_template(template_name)
        return template.render(deploy_ctx=deploy_ctx, djb_config=djb_config)

    def render_all(
        self,
        djb_config: DjbConfig,
        *,
        deployment: DeploymentCtx,
        service: ServiceCtx | None = None,
        secrets: SecretsCtx | None = None,
        database: DatabaseCtx | None = None,
    ) -> dict[str, str]:
        """Render all manifests for a deployment.

        Args:
            djb_config: User configuration (project_name, db_name, email, etc.).
            deployment: Runtime context for deployment.yaml (required).
            service: Runtime context for service.yaml. Defaults to using deployment.port.
            secrets: Runtime context for secrets.yaml. Only rendered if provided.
            database: Runtime context for cnpg-cluster.yaml. Only rendered if provided.

        Returns:
            Dict mapping manifest names to rendered YAML.
        """
        manifests = {}

        # Namespace (only needs djb_config)
        manifests["namespace.yaml"] = self.render("namespace.yaml.j2", djb_config)

        # Deployment
        manifests["deployment.yaml"] = self.render("deployment.yaml.j2", djb_config, deployment)

        # Service (default to deployment port if not specified)
        service_ctx = service or ServiceCtx(port=deployment.port)
        manifests["service.yaml"] = self.render("service.yaml.j2", djb_config, service_ctx)

        # Secrets (if provided)
        if secrets and secrets.secrets:
            manifests["secrets.yaml"] = self.render("secrets.yaml.j2", djb_config, secrets)

        # Ingress (if domain names configured, only needs djb_config)
        if djb_config.k8s.domain_names:
            manifests["ingress.yaml"] = self.render("ingress.yaml.j2", djb_config)

        # Database (CloudNativePG)
        if database:
            manifests["cnpg-cluster.yaml"] = self.render(
                "cnpg-cluster.yaml.j2", djb_config, database
            )

        return manifests


def _get_djb_source_dir(subdir: str) -> Path:
    """Get the djb source directory for a given subdir.

    Maps project subdirectories to their djb source locations:
    - manifests → djb/src/djb/k8s/templates/
    - backend → djb/src/djb/templates/deployment/k8s/backend/
    - buildpacks → djb/src/djb/buildpacks/dockerfiles/
    """
    if subdir == "manifests":
        return TEMPLATES_DIR
    elif subdir == "backend":
        return DJB_TEMPLATES_DIR / "deployment" / "k8s" / "backend"
    elif subdir == "buildpacks":
        return BUILDPACKS_DOCKERFILES_DIR
    else:
        raise ValueError(f"Unknown subdir: {subdir}")


def render_template(
    filename: str,
    djb_config: DjbConfig,
    subdir: str = "manifests",
    deploy_ctx: Any = None,
) -> str:
    """Resolve and return file content with project-first resolution.

    Resolution order:
    1. If file exists in project → use it directly (no interpolation)
    2. If .j2 template exists in project → render from project's template
    3. Otherwise → copy from djb, render if .j2, write to project

    This allows projects to:
    - Use plain files for full control (no interpolation)
    - Use .j2 templates for Jinja2 interpolation
    - Start with djb defaults and customize as needed

    Args:
        filename: Bare filename, e.g., "deployment.yaml" or "Dockerfile"
        djb_config: User configuration (project_name, db_name, email, etc.)
        subdir: Subdirectory under deployment/k8s/, e.g., "manifests", "backend", "buildpacks"
        deploy_ctx: Template-specific runtime context for Jinja2 rendering

    Returns:
        File content (rendered if from .j2 template, raw otherwise)
    """
    project_dir = djb_config.project_dir
    target_dir = project_dir / "deployment" / "k8s" / subdir

    file_path = target_dir / filename
    template_name = f"{filename}.j2"
    template_path = target_dir / template_name

    # 1. If file exists in project, use it directly
    if file_path.exists():
        return file_path.read_text()

    # 2. If .j2 template exists in project, render from it
    if template_path.exists():
        generator = K8sManifestGenerator(templates_dir=target_dir)
        rendered = generator.render(template_name, djb_config, deploy_ctx)
        file_path.write_text(rendered)
        return rendered

    # 3. Copy from djb, render if .j2, write to project
    target_dir.mkdir(parents=True, exist_ok=True)
    djb_source_dir = _get_djb_source_dir(subdir)

    # Check if djb has a .j2 template
    djb_template_path = djb_source_dir / template_name
    djb_file_path = djb_source_dir / filename

    if djb_template_path.exists():
        # Copy .j2 template to project
        template_path.write_text(djb_template_path.read_text())
        # Render and write
        generator = K8sManifestGenerator(templates_dir=target_dir)
        rendered = generator.render(template_name, djb_config, deploy_ctx)
        file_path.write_text(rendered)
        return rendered
    elif djb_file_path.exists():
        # Copy plain file to project (buildpacks use plain Dockerfiles)
        content = djb_file_path.read_text()
        file_path.write_text(content)
        return content
    else:
        raise FileNotFoundError(f"Template not found: {filename} (looked in {djb_source_dir})")


# Keep render_manifest as alias for backward compatibility during migration
def render_manifest(
    template_name: str,
    djb_config: DjbConfig,
    deploy_ctx: Any = None,
) -> str:
    """Deprecated: Use render_template instead."""
    # Strip .j2 suffix if present for new API
    filename = template_name.removesuffix(".j2")
    return render_template(filename, djb_config, subdir="manifests", deploy_ctx=deploy_ctx)


def render_all_manifests(
    djb_config: DjbConfig,
    *,
    deployment: DeploymentCtx,
    service: ServiceCtx | None = None,
    secrets: SecretsCtx | None = None,
    database: DatabaseCtx | None = None,
) -> dict[str, str]:
    """Convenience function to render all manifests.

    Args:
        djb_config: User configuration (project_name, db_name, email, etc.).
        deployment: Runtime context for deployment.yaml (required).
        service: Runtime context for service.yaml. Defaults to using deployment.port.
        secrets: Runtime context for secrets.yaml. Only rendered if provided.
        database: Runtime context for cnpg-cluster.yaml. Only rendered if provided.

    Returns:
        Dict mapping manifest names to rendered YAML.
    """
    generator = K8sManifestGenerator()
    return generator.render_all(
        djb_config,
        deployment=deployment,
        service=service,
        secrets=secrets,
        database=database,
    )
