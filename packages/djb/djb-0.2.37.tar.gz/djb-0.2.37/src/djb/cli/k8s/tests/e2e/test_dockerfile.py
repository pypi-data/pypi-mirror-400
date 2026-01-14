"""E2E tests for Dockerfile resolution and rendering via render_template.

Tests cover:
- render_template: Dockerfile path resolution order
- render_template: Template copying from djb templates
- render_template: Jinja2 template rendering with DjbConfig
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from djb.config import DjbConfig
from djb.k8s import render_template
from djb.templates import DJB_TEMPLATES_DIR

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

pytestmark = pytest.mark.e2e_marker


class TestRenderTemplateResolveDockerfile:
    """Tests for render_template() Dockerfile resolution behavior."""

    def test_copies_template_when_no_dockerfile_exists(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """When no Dockerfile exists, copies from djb and renders."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        result = render_template("Dockerfile", djb_config, subdir="backend")

        # Both template and rendered file should exist
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        assert (backend_dir / "Dockerfile.j2").exists()
        assert (backend_dir / "Dockerfile").exists()
        # Result should contain project name
        assert "testproject" in result

    def test_prefers_plain_dockerfile_over_template(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Dockerfile takes priority over Dockerfile.j2."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        # Create both files
        plain_path = backend_dir / "Dockerfile"
        template_path = backend_dir / "Dockerfile.j2"
        plain_path.write_text("FROM python:3.12-slim\n# plain")
        template_path.write_text("FROM python:3.12-slim\n# template")

        result = render_template("Dockerfile", djb_config, subdir="backend")

        # Plain Dockerfile is used (no interpolation)
        assert result == "FROM python:3.12-slim\n# plain"

    def test_uses_plain_dockerfile_when_no_template(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Falls back to Dockerfile when Dockerfile.j2 doesn't exist."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        plain_path = backend_dir / "Dockerfile"
        plain_path.write_text("FROM python:3.12-slim")

        result = render_template("Dockerfile", djb_config, subdir="backend")
        assert result == "FROM python:3.12-slim"

    def test_renders_template_when_only_template_exists(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Renders Dockerfile.j2 when it's the only file present."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        template_path = backend_dir / "Dockerfile.j2"
        template_path.write_text(
            "FROM python:3.12-slim\nLABEL project={{ djb_config.project_name }}"
        )

        result = render_template("Dockerfile", djb_config, subdir="backend")
        assert "LABEL project=testproject" in result


class TestRenderTemplateCopyDockerfile:
    """Tests for render_template() template copying behavior."""

    def test_copies_template_to_project(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Copies djb template to deployment/k8s/backend/Dockerfile.j2."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        render_template("Dockerfile", djb_config, subdir="backend")

        expected_path = project_dir / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
        assert expected_path.exists()

    def test_creates_directory_structure(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Creates deployment/k8s/backend/ directories if they don't exist."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        assert not backend_dir.exists()

        render_template("Dockerfile", djb_config, subdir="backend")

        assert backend_dir.exists()
        assert backend_dir.is_dir()

    def test_template_content_matches_source(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Copied template matches the djb source template."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        render_template("Dockerfile", djb_config, subdir="backend")

        result_path = project_dir / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
        source_template = DJB_TEMPLATES_DIR / "deployment" / "k8s" / "backend" / "Dockerfile.j2"

        expected_content = source_template.read_text()
        actual_content = result_path.read_text()

        assert actual_content == expected_content

    def test_template_contains_jinja2_variables(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Copied template contains Jinja2 variables for later rendering."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        render_template("Dockerfile", djb_config, subdir="backend")

        result_path = project_dir / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
        content = result_path.read_text()

        # Check for expected Jinja2 variables from the template
        assert "{{ djb_config.project_name }}" in content


class TestRenderTemplateRenderDockerfile:
    """Tests for render_template() template rendering behavior."""

    def test_renders_template_with_project_name(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Renders template and substitutes project_name variable."""
        djb_config = make_djb_config(DjbConfig(project_name="myproject"))
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        template_path = backend_dir / "Dockerfile.j2"
        template_path.write_text(
            "ENV DJANGO_SETTINGS_MODULE={{ djb_config.project_name }}.settings"
        )

        result = render_template("Dockerfile", djb_config, subdir="backend")

        assert "ENV DJANGO_SETTINGS_MODULE=myproject.settings" in result
        assert "{{ djb_config.project_name }}" not in result

        # Rendered Dockerfile should also exist on disk
        dockerfile_path = backend_dir / "Dockerfile"
        assert dockerfile_path.exists()
        assert "myproject" in dockerfile_path.read_text()

    def test_output_path_is_next_to_template(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Rendered Dockerfile is written next to the template file."""
        djb_config = make_djb_config(DjbConfig(project_name="myproject"))
        subdir = project_dir / "deployment" / "k8s" / "backend"
        subdir.mkdir(parents=True)
        template_path = subdir / "Dockerfile.j2"
        template_path.write_text("FROM python:3.12-slim")

        render_template("Dockerfile", djb_config, subdir="backend")

        result = subdir / "Dockerfile"
        assert result.exists()

    def test_renders_full_djb_template(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Renders the full djb Dockerfile template successfully."""
        djb_config = make_djb_config(DjbConfig(project_name="testapp"))

        # Let render_template copy and render the djb template
        result = render_template("Dockerfile", djb_config, subdir="backend")

        # Verify key substitutions
        assert "DJANGO_SETTINGS_MODULE=testapp.settings" in result
        assert "testapp.wsgi:application" in result
        assert "{{ djb_config" not in result  # No unrendered variables


class TestProjectNameWithHyphens:
    """Edge case tests for project names containing hyphens."""

    def test_resolve_works_with_hyphenated_project_name(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Dockerfile resolution works with hyphenated project names."""
        djb_config = make_djb_config(DjbConfig(project_name="my-cool-project"))
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)
        template = backend_dir / "Dockerfile.j2"
        template.write_text("FROM python:3.12-slim")

        # Should not raise
        result = render_template("Dockerfile", djb_config, subdir="backend")
        assert "FROM python:3.12-slim" in result

    def test_render_with_hyphenated_project_name(
        self, project_dir: Path, make_djb_config: Callable[..., DjbConfig]
    ) -> None:
        """Template rendering preserves hyphens in project name."""
        djb_config = make_djb_config(DjbConfig(project_name="my-cool-project"))
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        backend_dir.mkdir(parents=True)

        template_path = backend_dir / "Dockerfile.j2"
        template_path.write_text("PROJECT={{ djb_config.project_name }}")

        result = render_template("Dockerfile", djb_config, subdir="backend")

        assert "PROJECT=my-cool-project" in result
