"""
Skaffold configuration generation for djb.

Generates skaffold.yaml dynamically from project configuration to enable
hot-reload development workflows with Kubernetes.

Skaffold Features:
- File sync: Changes to Python, templates, and static files sync instantly
- Port forwarding: Automatic port forwarding for local development
- Build profiles: Different configurations for dev vs production
- Hot reload: Gunicorn --reload watches for synced file changes

Usage:
    config = SkaffoldConfig(
        project_name="myapp",
        project_package="myapp",
        registry_address="k3d-registry.localhost:5000",
    )
    generator = SkaffoldGenerator()
    yaml_content = generator.generate(config)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import jinja2


@dataclass
class SkaffoldConfig:
    """Configuration for Skaffold manifest generation.

    Attributes:
        project_name: Name of the project (used for image naming, service names).
        project_package: Python package name for sync patterns (e.g., "beachresort25").
        registry_address: Container registry address (e.g., "k3d-registry.localhost:5000").
        buildpack_image: Pre-built buildpack chain image to use as base.
        local_port: Local port for port forwarding (default: 8000).
        container_port: Container port the app listens on (default: 8000).
        dockerfile: Path to Dockerfile (default: "Dockerfile").
        sync_patterns: Additional sync patterns beyond defaults.
        manifests_dir: Directory containing K8s manifests (default: "k8s").
    """

    project_name: str
    project_package: str
    registry_address: str
    buildpack_image: str
    local_port: int = 8000
    container_port: int = 8000
    dockerfile: str = "Dockerfile"
    sync_patterns: list[dict[str, str]] = field(default_factory=list)
    manifests_dir: str = "k8s"


class SkaffoldGenerator:
    """Generator for Skaffold configuration files.

    Generates skaffold.yaml from project configuration using Jinja2 templates.

    Example:
        config = SkaffoldConfig(
            project_name="myapp",
            project_package="myapp",
            registry_address="k3d-registry.localhost:5000",
        )
        generator = SkaffoldGenerator()
        yaml_content = generator.generate(config)
    """

    # Skaffold API version
    API_VERSION = "skaffold/v4beta13"

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the generator.

        Args:
            templates_dir: Path to templates directory.
                           Defaults to templates/ in this package.
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"

        self._templates_dir = templates_dir
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(templates_dir)),
            autoescape=False,  # YAML, not HTML
            keep_trailing_newline=True,
        )

    def generate(self, config: SkaffoldConfig) -> str:
        """Generate skaffold.yaml content.

        Args:
            config: Skaffold configuration.

        Returns:
            Generated YAML content.
        """
        template = self._env.get_template("skaffold.yaml.j2")

        # Build default sync patterns
        sync_patterns = self._build_sync_patterns(config)

        context = {
            "api_version": self.API_VERSION,
            "project_name": config.project_name,
            "project_package": config.project_package,
            "registry_address": config.registry_address,
            "buildpack_image": config.buildpack_image,
            "local_port": config.local_port,
            "container_port": config.container_port,
            "dockerfile": config.dockerfile,
            "sync_patterns": sync_patterns,
            "manifests_dir": config.manifests_dir,
        }

        return template.render(**context)

    def _build_sync_patterns(self, config: SkaffoldConfig) -> list[dict[str, str]]:
        """Build the list of file sync patterns.

        Default patterns:
        - Python files: **/*.py -> /app
        - Django templates: **/templates/**/* -> /app
        - Frontend assets: frontend/dist/**/* -> /app/staticfiles

        Args:
            config: Skaffold configuration.

        Returns:
            List of sync pattern dicts with 'src' and 'dest' keys.
        """
        patterns = [
            # Python code
            {"src": f"{config.project_package}/**/*.py", "dest": "/app"},
            # Django templates
            {"src": f"{config.project_package}/**/templates/**/*", "dest": "/app"},
            # Frontend assets (if using frontend build)
            {"src": "frontend/dist/**/*", "dest": "/app/staticfiles"},
            # Static files
            {"src": f"{config.project_package}/static/**/*", "dest": "/app"},
        ]

        # Add custom patterns
        patterns.extend(config.sync_patterns)

        return patterns

    def write(self, config: SkaffoldConfig, output_path: Path) -> None:
        """Generate and write skaffold.yaml to a file.

        Args:
            config: Skaffold configuration.
            output_path: Path to write the generated file.
        """
        content = self.generate(config)
        output_path.write_text(content)


def generate_skaffold_config(
    project_name: str,
    project_package: str,
    registry_address: str,
    buildpack_image: str,
    **kwargs,
) -> str:
    """Convenience function to generate Skaffold configuration.

    Args:
        project_name: Name of the project.
        project_package: Python package name.
        registry_address: Container registry address.
        buildpack_image: Pre-built buildpack chain image tag.
        **kwargs: Additional SkaffoldConfig options.

    Returns:
        Generated YAML content.
    """
    config = SkaffoldConfig(
        project_name=project_name,
        project_package=project_package,
        registry_address=registry_address,
        buildpack_image=buildpack_image,
        **kwargs,
    )
    generator = SkaffoldGenerator()
    return generator.generate(config)
