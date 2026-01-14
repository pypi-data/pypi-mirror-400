"""Tests for K3dProvider.

These tests mock CmdRunner to avoid requiring k3d to be installed.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from djb.k8s.cluster import K3dProvider
from djb.k8s.cluster.provider import (
    ClusterNotFoundError,
    ClusterProvisionError,
)
from djb.testing import MockCliContext


class TestK3dProviderProperties:
    """Tests for K3dProvider properties."""

    def test_name(self, mock_cli_ctx: MockCliContext) -> None:
        """Test name property."""
        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.name == "k3d"

    def test_registry_address(self, mock_cli_ctx: MockCliContext) -> None:
        """Test registry_address property."""
        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.registry_address == "k3d-registry.localhost:5000"

    def test_is_local(self, mock_cli_ctx: MockCliContext) -> None:
        """Test is_local property."""
        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.is_local is True


class TestK3dProviderCreate:
    """Tests for K3dProvider.create method."""

    def test_create_new_cluster(self, mock_cli_ctx: MockCliContext) -> None:
        """Test creating a new cluster."""
        # Mock exists check (cluster doesn't exist), then create
        mock_cli_ctx.run_mock.side_effect = [
            Mock(returncode=0, stdout="[]", stderr=""),  # cluster list
            Mock(returncode=0, stdout="", stderr=""),  # cluster create
        ]

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        provider.create("test-cluster")

        # Verify cluster create was called
        calls = mock_cli_ctx.run_mock.call_args_list
        assert len(calls) == 2
        create_call = calls[1]
        cmd = create_call[0][0]  # First positional arg is the command list
        assert "cluster" in cmd
        assert "create" in cmd
        assert "test-cluster" in cmd

    def test_create_existing_cluster(self, mock_cli_ctx: MockCliContext) -> None:
        """Test create returns False when cluster already exists."""
        clusters = [
            {
                "name": "test-cluster",
                "nodes": [{"State": {"Running": True}}],
            }
        ]
        mock_cli_ctx.run_mock.return_value = Mock(
            returncode=0, stdout=json.dumps(clusters), stderr=""
        )

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        created = provider.create("test-cluster")

        assert created is False
        # Should only check existence
        assert mock_cli_ctx.run_mock.call_count == 1

    def test_create_failure_raises_error(self, mock_cli_ctx: MockCliContext) -> None:
        """Test that creation failure raises ClusterProvisionError."""
        mock_cli_ctx.run_mock.side_effect = [
            Mock(returncode=0, stdout="[]", stderr=""),  # cluster list
            Mock(returncode=1, stdout="", stderr="creation failed"),
        ]

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        with pytest.raises(ClusterProvisionError):
            provider.create("test-cluster")


class TestK3dProviderDelete:
    """Tests for K3dProvider.delete method."""

    def test_delete_existing_cluster(self, mock_cli_ctx: MockCliContext) -> None:
        """Test deleting an existing cluster."""
        clusters = [{"name": "test-cluster", "nodes": []}]
        mock_cli_ctx.run_mock.side_effect = [
            Mock(returncode=0, stdout=json.dumps(clusters), stderr=""),
            Mock(returncode=0, stdout="", stderr=""),  # delete
        ]

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        provider.delete("test-cluster")

        # Verify delete was called
        calls = mock_cli_ctx.run_mock.call_args_list
        delete_call = calls[1]
        cmd = delete_call[0][0]
        assert "delete" in cmd

    def test_delete_nonexistent_cluster(self, mock_cli_ctx: MockCliContext) -> None:
        """Test deleting a cluster that doesn't exist."""
        mock_cli_ctx.run_mock.return_value = Mock(returncode=0, stdout="[]", stderr="")

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        provider.delete("nonexistent")  # Should not raise


class TestK3dProviderExists:
    """Tests for K3dProvider.exists method."""

    def test_exists_true(self, mock_cli_ctx: MockCliContext) -> None:
        """Test exists returns True for existing cluster."""
        clusters = [{"name": "test-cluster", "nodes": []}]
        mock_cli_ctx.run_mock.return_value = Mock(
            returncode=0, stdout=json.dumps(clusters), stderr=""
        )

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.exists("test-cluster") is True

    def test_exists_false(self, mock_cli_ctx: MockCliContext) -> None:
        """Test exists returns False for nonexistent cluster."""
        mock_cli_ctx.run_mock.return_value = Mock(returncode=0, stdout="[]", stderr="")

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.exists("nonexistent") is False


class TestK3dProviderIsRunning:
    """Tests for K3dProvider.is_running method."""

    def test_is_running_true(self, mock_cli_ctx: MockCliContext) -> None:
        """Test is_running returns True for running cluster."""
        clusters = [
            {
                "name": "test-cluster",
                "nodes": [{"State": {"Running": True}}],
            }
        ]
        mock_cli_ctx.run_mock.return_value = Mock(
            returncode=0, stdout=json.dumps(clusters), stderr=""
        )

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.is_running("test-cluster") is True

    def test_is_running_false_stopped(self, mock_cli_ctx: MockCliContext) -> None:
        """Test is_running returns False for stopped cluster."""
        clusters = [
            {
                "name": "test-cluster",
                "nodes": [{"State": {"Running": False}}],
            }
        ]
        mock_cli_ctx.run_mock.return_value = Mock(
            returncode=0, stdout=json.dumps(clusters), stderr=""
        )

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.is_running("test-cluster") is False


class TestK3dProviderGetKubeconfig:
    """Tests for K3dProvider.get_kubeconfig method."""

    def test_get_kubeconfig(self, mock_cli_ctx: MockCliContext) -> None:
        """Test getting kubeconfig."""
        kubeconfig = "apiVersion: v1\nclusters: []"
        clusters = [{"name": "test-cluster", "nodes": []}]

        mock_cli_ctx.run_mock.side_effect = [
            Mock(returncode=0, stdout=json.dumps(clusters), stderr=""),
            Mock(returncode=0, stdout=kubeconfig, stderr=""),
        ]

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        result = provider.get_kubeconfig("test-cluster")
        assert result == kubeconfig

    def test_get_kubeconfig_nonexistent(self, mock_cli_ctx: MockCliContext) -> None:
        """Test getting kubeconfig for nonexistent cluster."""
        mock_cli_ctx.run_mock.return_value = Mock(returncode=0, stdout="[]", stderr="")

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        with pytest.raises(ClusterNotFoundError):
            provider.get_kubeconfig("nonexistent")


class TestK3dProviderKubectl:
    """Tests for K3dProvider.kubectl method."""

    @patch("tempfile.NamedTemporaryFile")
    def test_kubectl_command(self, mock_tempfile: MagicMock, mock_cli_ctx: MockCliContext) -> None:
        """Test running kubectl command."""
        kubeconfig = "apiVersion: v1\nclusters: []"
        clusters = [{"name": "test-cluster", "nodes": []}]

        # Mock tempfile
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.name = "/tmp/kubeconfig.yaml"
        mock_tempfile.return_value = mock_file

        mock_cli_ctx.run_mock.side_effect = [
            Mock(returncode=0, stdout=json.dumps(clusters), stderr=""),
            Mock(returncode=0, stdout=kubeconfig, stderr=""),
            Mock(returncode=0, stdout="output", stderr=""),
        ]

        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        with patch("pathlib.Path.unlink"):
            returncode, stdout, stderr = provider.kubectl("test-cluster", "get", "pods")

        assert returncode == 0
        assert stdout == "output"
