"""E2E tests for djb deploy k8s CLI commands.

Tests for _build_container_remote and render_template Dockerfile handling
during K8s deployment.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, Mock

import click
import pytest

from djb.cli.k8s.deploy import _build_container_remote
from djb.k8s import render_template
from djb.config import DjbConfig, K8sBackendConfig, K8sConfig
from djb.core.cmd_runner import CmdRunner
from djb.testing import DEFAULT_K8S_CONFIG


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


class TestBuildContainerRemote:
    """Tests for _build_container_remote function.

    This function builds a container image on a remote server.
    When managed_dockerfile=True and no Dockerfile exists, it should
    copy the template locally before syncing to remote.
    """

    def test_copies_dockerfile_template_when_managed_and_missing(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """_build_container_remote copies template when managed_dockerfile=True and no Dockerfile exists.

        This is the key fix: when managed_dockerfile=True and no Dockerfile exists
        locally or on remote, the template should be copied to deployment/k8s/backend/Dockerfile.j2
        before syncing to remote.
        """
        # Create DjbConfig with managed_dockerfile=True (default)
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Create mock SSH
        mock_ssh = MagicMock()
        mock_ssh.host = "test-server"
        mock_ssh.port = 22

        # Track whether the sync has happened (simulates rsync copying files to remote)
        sync_happened = {"value": False}

        # Configure SSH to report Dockerfile.j2 exists on remote AFTER sync
        def ssh_run_side_effect(cmd, *args, **kwargs):
            if "mkdir" in cmd:
                sync_happened["value"] = True
            # Use startswith to avoid matching docker build -f flag
            if cmd.startswith("test -f"):
                if "Dockerfile.j2" in cmd and sync_happened["value"]:
                    # After sync, template exists on remote
                    return (0, "", "")
                # File doesn't exist by default
                return (1, "", "")
            # All other commands succeed
            return (0, "", "")

        mock_ssh.run.side_effect = ssh_run_side_effect

        # Mock CmdRunner for this test
        mock_runner = MagicMock(spec=CmdRunner)
        mock_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Call the function - it should copy the template locally first
        _build_container_remote(
            runner=mock_runner,
            ssh=mock_ssh,
            djb_config=djb_config,
            commit_sha="abc1234",
            buildpack_image="localhost:32000/buildpack:latest",
        )

        # Verify the template was copied to the project
        dockerfile_path = project_dir / "deployment" / "k8s" / "backend" / "Dockerfile.j2"
        assert dockerfile_path.exists(), (
            "Dockerfile.j2 template should be copied to deployment/k8s/backend/ "
            "when managed_dockerfile=True and no Dockerfile exists"
        )

    def test_raises_error_when_not_managed_and_missing(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """_build_container_remote raises ClickException when managed_dockerfile=False and no Dockerfile exists."""
        # Create K8sConfig with managed_dockerfile=False
        k8s_config = K8sConfig(
            domain_names=DEFAULT_K8S_CONFIG.domain_names,
            backend=K8sBackendConfig(
                managed_dockerfile=False,
                remote_build=True,
                buildpacks=["python:3.14-slim"],
                buildpack_registry="localhost:32000",
            ),
            db_name=DEFAULT_K8S_CONFIG.db_name,
            cluster_name=DEFAULT_K8S_CONFIG.cluster_name,
            host=DEFAULT_K8S_CONFIG.host,
            no_cloudnativepg=DEFAULT_K8S_CONFIG.no_cloudnativepg,
            no_tls=DEFAULT_K8S_CONFIG.no_tls,
        )
        djb_config = make_djb_config(DjbConfig(project_name="testproject", k8s=k8s_config))

        # Create mock SSH
        mock_ssh = MagicMock()
        mock_ssh.host = "test-server"
        mock_ssh.port = 22

        # Create mock CmdRunner
        mock_runner = MagicMock(spec=CmdRunner)

        with pytest.raises(click.ClickException) as exc_info:
            _build_container_remote(
                runner=mock_runner,
                ssh=mock_ssh,
                djb_config=djb_config,
                commit_sha="abc1234",
                buildpack_image="localhost:32000/buildpack:latest",
            )

        assert "managed_dockerfile" in str(exc_info.value).lower()

    def test_uses_existing_dockerfile_template(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """_build_container_remote uses existing Dockerfile.j2 if present locally."""
        # Create DjbConfig with managed_dockerfile=True (default)
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Create existing Dockerfile.j2 in project
        dockerfile_dir = project_dir / "deployment" / "k8s" / "backend"
        dockerfile_dir.mkdir(parents=True)
        (dockerfile_dir / "Dockerfile.j2").write_text("FROM python:3.12")

        # Create mock SSH
        mock_ssh = MagicMock()
        mock_ssh.host = "test-server"
        mock_ssh.port = 22

        # Configure SSH - use startswith for test -f
        def ssh_run_side_effect(cmd, *args, **kwargs):
            if cmd.startswith("test -f"):
                if "Dockerfile.j2" in cmd:
                    return (0, "", "")  # Template exists
                return (1, "", "")  # Plain Dockerfile doesn't exist
            # All other commands succeed
            return (0, "", "")

        mock_ssh.run.side_effect = ssh_run_side_effect

        # Create mock CmdRunner
        mock_runner = MagicMock(spec=CmdRunner)
        mock_runner.run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Should not raise an exception
        _build_container_remote(
            runner=mock_runner,
            ssh=mock_ssh,
            djb_config=djb_config,
            commit_sha="abc1234",
            buildpack_image="localhost:32000/buildpack:latest",
        )

        # The test verifies no exception was raised and the existing file wasn't overwritten
        assert (dockerfile_dir / "Dockerfile.j2").read_text() == "FROM python:3.12"


class TestRenderTemplateDockerfile:
    """Tests for render_template with backend Dockerfiles.

    These tests verify the render_template function's behavior for
    Dockerfile resolution, copying from djb, and Jinja2 rendering.
    """

    def test_returns_none_when_no_dockerfile_exists(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """render_template copies djb template when no Dockerfile exists."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Ensure no Dockerfile exists
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        assert not backend_dir.exists()

        # render_template should copy from djb and render
        result = render_template("Dockerfile", djb_config, subdir="backend")

        # Template should now exist
        assert (backend_dir / "Dockerfile.j2").exists()
        # Rendered Dockerfile should also exist
        assert (backend_dir / "Dockerfile").exists()
        # Content should have project name rendered
        assert "testproject" in result

    def test_returns_template_path_when_j2_exists(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """render_template uses existing .j2 template when present."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Create template
        dockerfile_dir = project_dir / "deployment" / "k8s" / "backend"
        dockerfile_dir.mkdir(parents=True)
        template_path = dockerfile_dir / "Dockerfile.j2"
        template_path.write_text("FROM python:3.12\nLABEL project={{ djb_config.project_name }}")

        result = render_template("Dockerfile", djb_config, subdir="backend")

        # Should render the template
        assert "LABEL project=testproject" in result

    def test_returns_dockerfile_path_when_plain_exists(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """render_template returns plain Dockerfile content when it exists."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Create plain Dockerfile (not .j2)
        dockerfile_dir = project_dir / "deployment" / "k8s" / "backend"
        dockerfile_dir.mkdir(parents=True)
        dockerfile_path = dockerfile_dir / "Dockerfile"
        dockerfile_path.write_text("FROM python:3.12\n# Plain Dockerfile")

        result = render_template("Dockerfile", djb_config, subdir="backend")

        # Should return plain file content (no interpolation)
        assert result == "FROM python:3.12\n# Plain Dockerfile"

    def test_prefers_plain_over_template(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """render_template prefers plain Dockerfile over .j2 template."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Create both files
        dockerfile_dir = project_dir / "deployment" / "k8s" / "backend"
        dockerfile_dir.mkdir(parents=True)
        (dockerfile_dir / "Dockerfile").write_text("# Plain Dockerfile")
        (dockerfile_dir / "Dockerfile.j2").write_text("# Template {{ djb_config.project_name }}")

        result = render_template("Dockerfile", djb_config, subdir="backend")

        # Plain Dockerfile takes priority
        assert result == "# Plain Dockerfile"


class TestRenderTemplateCreatesTemplate:
    """Tests for render_template template creation behavior."""

    def test_creates_dockerfile_template_in_project(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """render_template copies djb template to project."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Ensure the directory doesn't exist
        backend_dir = project_dir / "deployment" / "k8s" / "backend"
        assert not backend_dir.exists()

        render_template("Dockerfile", djb_config, subdir="backend")

        # Template should be copied
        expected_path = backend_dir / "Dockerfile.j2"
        assert expected_path.exists()
        assert "FROM" in expected_path.read_text()

    def test_creates_parent_directories(
        self,
        make_djb_config: Callable[..., DjbConfig],
        project_dir: Path,
    ):
        """render_template creates parent directories if needed."""
        djb_config = make_djb_config(DjbConfig(project_name="testproject"))

        # Ensure the directory doesn't exist
        assert not (project_dir / "deployment").exists()

        render_template("Dockerfile", djb_config, subdir="backend")

        assert (project_dir / "deployment" / "k8s" / "backend").exists()
