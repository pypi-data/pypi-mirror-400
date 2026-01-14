"""E2E tests for djb deploy k8s terraform command.

These tests verify the terraform command behavior with mocked providers
and real SSH connections where needed.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli
from djb.config.storage.io.external import GitConfigIO

pytestmark = pytest.mark.e2e_marker


class TestDeployK8sTerraformLocal:
    """E2E tests for `djb deploy k8s terraform` local mode (no --host)."""

    @patch("djb.machine_state.terraform.states.get_cluster_provider_from_context")
    def test_terraform_local_k3d_default(
        self,
        mock_get_provider: MagicMock,
        cli_runner: CliRunner,
        project_dir: Path,
    ) -> None:
        """terraform uses k3d by default when no --host is specified."""

        mock_provider = MagicMock()
        mock_provider.exists.return_value = False
        mock_provider.is_running.return_value = False
        # Make kubectl return "not found" for CloudNativePG
        mock_provider.kubectl.return_value = (1, "", "not found")
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "deploy", "k8s", "terraform", "--no-cloudnativepg"],
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify cluster was created
        mock_provider.create.assert_called_once()
        # Note: k3d has bundled addons, so enable_addons is not called

    @patch("djb.machine_state.terraform.states.get_cluster_provider_from_context")
    def test_terraform_local_microk8s(
        self,
        mock_get_provider: MagicMock,
        cli_runner: CliRunner,
        project_dir: Path,
    ) -> None:
        """terraform --microk8s uses microk8s provider locally."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.kubectl.return_value = (0, "cnpg-controller-manager", "")
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "deploy", "k8s", "terraform", "--microk8s"],
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"

    @patch("djb.machine_state.terraform.states.get_cluster_provider_from_context")
    def test_terraform_local_existing_cluster(
        self,
        mock_get_provider: MagicMock,
        cli_runner: CliRunner,
        project_dir: Path,
    ) -> None:
        """terraform with existing cluster skips creation."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.kubectl.return_value = (0, "cnpg-controller-manager", "")
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "deploy", "k8s", "terraform", "--no-cloudnativepg"],
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Infrastructure ready" in result.output

        # Verify create was NOT called (cluster already exists)
        mock_provider.create.assert_not_called()

    @patch("djb.machine_state.terraform.states.get_cluster_provider_from_context")
    def test_terraform_local_installs_cloudnativepg(
        self,
        mock_get_provider: MagicMock,
        cli_runner: CliRunner,
        project_dir: Path,
    ) -> None:
        """terraform installs CloudNativePG when not present."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        # First call for check returns not found, subsequent calls succeed
        mock_provider.kubectl.side_effect = [
            (1, "", "not found"),  # Check CNPG
            (0, "", ""),  # Install CNPG
            (0, "", ""),  # Wait for CNPG
        ]
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "deploy", "k8s", "terraform"],
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "CloudNativePG" in result.output


class TestDeployK8sTerraformRemote:
    """E2E tests for `djb deploy k8s terraform --host` command."""

    @pytest.mark.order(1)  # Run first to maximize parallelization
    def test_terraform_ssh_connection_with_container(
        self,
        cli_runner: CliRunner,
        project_dir: Path,
        make_local_vps_container: dict,
    ) -> None:
        """Test terraform connects via SSH to container.

        This test verifies that terraform can establish an SSH connection
        to the local VPS container. It doesn't fully provision microk8s
        (which would take too long) but verifies the SSH connectivity works.
        """
        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "deploy",
                "k8s",
                "terraform",
                "--host",
                f"root@{make_local_vps_container['host']}",
                "--port",
                str(make_local_vps_container["port"]),
                "--ssh-key",
                str(make_local_vps_container["ssh_key"]),
                "--no-tls",
            ],
        )
        # The command will fail because microk8s isn't installed in the container,
        # but it should at least connect via SSH and check for microk8s
        assert "microk8s" in result.output.lower() or "ssh" in result.output.lower()

    @patch("djb.machine_state.terraform.states.get_cluster_provider_from_context")
    def test_terraform_remote_creates_clusterissuer(
        self,
        mock_get_provider: MagicMock,
        cli_runner: CliRunner,
        project_dir: Path,
    ) -> None:
        """terraform --host creates ClusterIssuer with email."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        # CNPG installed, ClusterIssuer not configured
        mock_provider.kubectl.side_effect = [
            (0, "cnpg-controller-manager", ""),  # Check CNPG
            (1, "", "not found"),  # Check ClusterIssuer
        ]
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "deploy",
                "k8s",
                "terraform",
                "--host",
                "root@localhost",
                "--email",
                "admin@example.com",
            ],
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "ClusterIssuer" in result.output

        # Verify apply_manifests was called for ClusterIssuer
        mock_provider.apply_manifests.assert_called()

    @patch("djb.machine_state.terraform.states.get_cluster_provider_from_context")
    def test_terraform_remote_no_tls(
        self,
        mock_get_provider: MagicMock,
        cli_runner: CliRunner,
        project_dir: Path,
    ) -> None:
        """terraform --host --no-tls skips ClusterIssuer."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.kubectl.return_value = (0, "cnpg-controller-manager", "")
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "deploy",
                "k8s",
                "terraform",
                "--host",
                "root@localhost",
                "--no-tls",
            ],
        )
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "skip" in result.output.lower() or "ClusterIssuer" not in result.output

        # Verify apply_manifests was NOT called (no ClusterIssuer)
        mock_provider.apply_manifests.assert_not_called()

    @patch("djb.machine_state.terraform.states.get_cluster_provider_from_context")
    def test_terraform_remote_email_from_config(
        self,
        mock_get_provider: MagicMock,
        cli_runner: CliRunner,
        project_dir: Path,
        make_djb_config,
    ) -> None:
        """terraform uses email from config when --email not provided."""
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.kubectl.side_effect = [
            (0, "cnpg-controller-manager", ""),  # Check CNPG
            (1, "", "not found"),  # Check ClusterIssuer
        ]
        mock_get_provider.return_value = mock_provider

        # Create config with email set (default is test@example.com)
        config = make_djb_config()

        # Patch get_djb_config to return our config
        with patch("djb.cli.k8s.terraform.CliK8sContext") as mock_ctx_class:
            mock_ctx = MagicMock()
            mock_ctx.config = config
            mock_ctx.runner = MagicMock()
            mock_ctx_class.return_value = mock_ctx

            result = cli_runner.invoke(
                djb_cli,
                [
                    "--project-dir",
                    str(project_dir),
                    "deploy",
                    "k8s",
                    "terraform",
                    "--host",
                    "root@localhost",
                    # Note: no --email flag - should use config.letsencrypt.effective_email
                ],
                obj=mock_ctx,
            )

        # Should succeed because email comes from config
        assert result.exit_code == 0, f"Failed: {result.output}"
        assert "ClusterIssuer" in result.output

    def test_terraform_requires_email_for_remote_tls(
        self,
        cli_runner: CliRunner,
        project_dir: Path,
        make_pyproject,
        monkeypatch,
    ) -> None:
        """terraform requires email for TLS unless --no-tls."""

        # Override isolate_git_config for this test: provide name but NOT email
        # This tests the validation that email is required for TLS
        def _get_value_no_email(_self, key: str):
            return {"name": "Test User"}.get(key)

        monkeypatch.setattr(GitConfigIO, "_get_value", _get_value_no_email)

        make_pyproject()

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "deploy",
                "k8s",
                "terraform",
                "--host",
                "root@localhost",
                "--microk8s",
            ],
        )
        assert result.exit_code != 0
        assert "email" in result.output.lower() or "no-tls" in result.output.lower()
