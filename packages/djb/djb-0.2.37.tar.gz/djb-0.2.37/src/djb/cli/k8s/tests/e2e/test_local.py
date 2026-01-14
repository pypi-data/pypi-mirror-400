"""E2E tests for djb deploy k8s local commands (Skaffold-based).

These tests verify the CLI commands work correctly with mocked cluster providers.
Full E2E tests with real k3d/microk8s clusters would require those tools installed.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli

pytestmark = pytest.mark.e2e_marker


class TestDeployK8sLocalCluster:
    """E2E tests for `djb deploy k8s local cluster` subcommands."""

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    @patch("djb.cli.k8s.local.get_cluster_provider")
    def test_cluster_status_no_cluster(
        self,
        mock_get_provider: MagicMock,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test cluster status when no cluster exists."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = True
        mock_provider = MagicMock()
        mock_provider.exists.return_value = False
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "cluster", "status"])
        assert result.exit_code == 0
        assert "does not exist" in result.output

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    @patch("djb.cli.k8s.local.get_cluster_provider")
    def test_cluster_status_running(
        self,
        mock_get_provider: MagicMock,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test cluster status when cluster is running."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = True
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        mock_provider.registry_address = "k3d-registry.localhost:5000"
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "cluster", "status"])
        assert result.exit_code == 0
        assert "running" in result.output

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    @patch("djb.cli.k8s.local.get_cluster_provider")
    def test_cluster_create_success(
        self,
        mock_get_provider: MagicMock,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test cluster create command."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = True
        mock_provider = MagicMock()
        mock_provider.exists.return_value = False
        mock_provider.is_running.return_value = False
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "cluster", "create"])
        assert result.exit_code == 0
        mock_provider.create.assert_called_once()
        mock_provider.enable_addons.assert_called_once()

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    @patch("djb.cli.k8s.local.get_cluster_provider")
    def test_cluster_create_already_exists(
        self,
        mock_get_provider: MagicMock,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test cluster create when cluster already exists."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = True
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_provider.is_running.return_value = True
        # create() returns False when cluster already exists
        mock_provider.create.return_value = False
        # start() returns False when already running
        mock_provider.start.return_value = False
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "cluster", "create"])
        assert result.exit_code == 0
        assert "already exists" in result.output
        mock_provider.create.assert_called_once()

    @patch("djb.cli.k8s.local._check_docker_available")
    def test_cluster_create_no_docker(
        self,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test cluster create fails when Docker is not available."""
        mock_check_docker.return_value = False

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "cluster", "create"])
        assert result.exit_code != 0
        assert "Docker is not available" in result.output

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    @patch("djb.cli.k8s.local.get_cluster_provider")
    def test_cluster_delete_with_confirmation(
        self,
        mock_get_provider: MagicMock,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test cluster delete with -y flag."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = True
        mock_provider = MagicMock()
        mock_provider.exists.return_value = True
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(djb_cli, ["-y", "deploy", "k8s", "local", "cluster", "delete"])
        assert result.exit_code == 0
        mock_provider.delete.assert_called_once()


class TestDeployK8sLocalDev:
    """E2E tests for `djb deploy k8s local dev` command."""

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    @patch("djb.cli.k8s.local.get_cluster_provider")
    def test_dev_requires_running_cluster(
        self,
        mock_get_provider: MagicMock,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test dev command fails when cluster is not running."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = True
        mock_provider = MagicMock()
        mock_provider.exists.return_value = False
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "dev"])
        assert result.exit_code != 0
        assert "does not exist" in result.output

    @patch("djb.cli.k8s.local._check_docker_available")
    def test_dev_requires_docker(
        self,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test dev command fails when Docker is not available."""
        mock_check_docker.return_value = False

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "dev"])
        assert result.exit_code != 0
        assert "Docker is not available" in result.output

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    def test_dev_requires_skaffold(
        self,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test dev command fails when Skaffold is not installed."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = False  # skaffold not available

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "dev"])
        assert result.exit_code != 0
        assert "Skaffold is not installed" in result.output


class TestDeployK8sLocalBuild:
    """E2E tests for `djb deploy k8s local build` command."""

    @patch("djb.cli.k8s.local._check_docker_available")
    @patch("djb.cli.k8s.local._check_tool_available")
    @patch("djb.cli.k8s.local.get_cluster_provider")
    def test_build_requires_running_cluster(
        self,
        mock_get_provider: MagicMock,
        mock_check_tool: MagicMock,
        mock_check_docker: MagicMock,
        cli_runner: CliRunner,
    ) -> None:
        """Test build command fails when cluster is not running."""
        mock_check_docker.return_value = True
        mock_check_tool.return_value = True
        mock_provider = MagicMock()
        mock_provider.is_running.return_value = False
        mock_get_provider.return_value = mock_provider

        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "build"])
        assert result.exit_code != 0
        assert "not running" in result.output
