"""Tests for cluster provider factory."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from djb.k8s.cluster import (
    ClusterProvider,
    K3dProvider,
    Microk8sProvider,
    SSHConfig,
    get_cluster_provider,
    register_provider,
)
from djb.k8s.cluster.factory import list_providers
from djb.testing import MockCliContext

if TYPE_CHECKING:
    from djb.config import DjbConfig
    from djb.core.cmd_runner import CmdRunner


class TestGetClusterProvider:
    """Tests for get_cluster_provider factory function."""

    def test_get_k3d_provider(self, mock_cli_ctx: MockCliContext) -> None:
        """Test getting a k3d provider."""
        provider = get_cluster_provider("k3d", mock_cli_ctx.runner, mock_cli_ctx.config)
        assert isinstance(provider, K3dProvider)
        assert provider.name == "k3d"
        assert provider.is_local is True

    def test_get_local_microk8s_provider(self, mock_cli_ctx: MockCliContext) -> None:
        """Test getting a local microk8s provider."""
        provider = get_cluster_provider("microk8s", mock_cli_ctx.runner, mock_cli_ctx.config)
        assert isinstance(provider, Microk8sProvider)
        assert provider.name == "microk8s"
        assert provider.is_local is True

    def test_get_remote_microk8s_provider(self, mock_cli_ctx: MockCliContext) -> None:
        """Test getting a remote microk8s provider with SSH config."""
        ssh_config = SSHConfig(
            host="root@server.example.com",
            key_path=Path("/path/to/key"),
            port=22,
        )
        provider = get_cluster_provider(
            "microk8s", mock_cli_ctx.runner, mock_cli_ctx.config, ssh_config=ssh_config
        )
        assert isinstance(provider, Microk8sProvider)
        assert provider.name == "microk8s"
        assert provider.is_local is False

    def test_unknown_provider_raises_error(self, mock_cli_ctx: MockCliContext) -> None:
        """Test that unknown provider type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown cluster type"):
            get_cluster_provider("unknown", mock_cli_ctx.runner, mock_cli_ctx.config)

    def test_k3d_with_ssh_config_raises_error(self, mock_cli_ctx: MockCliContext) -> None:
        """Test that k3d with SSH config raises ValueError."""
        ssh_config = SSHConfig(host="root@server.example.com")
        with pytest.raises(ValueError, match="local-only provider"):
            get_cluster_provider(
                "k3d", mock_cli_ctx.runner, mock_cli_ctx.config, ssh_config=ssh_config
            )


class TestRegisterProvider:
    """Tests for register_provider function."""

    def test_register_custom_provider(self, mock_cli_ctx: MockCliContext) -> None:
        """Test registering a custom provider."""

        class CustomProvider:
            def __init__(self, cmd_runner: "CmdRunner", config: DjbConfig) -> None:
                self._runner = cmd_runner
                self._config = config

            @property
            def name(self) -> str:
                return "custom"

            @property
            def is_local(self) -> bool:
                return True

        register_provider("custom", CustomProvider)
        assert "custom" in list_providers()

        # Get the custom provider
        provider = get_cluster_provider("custom", mock_cli_ctx.runner, mock_cli_ctx.config)
        assert provider.name == "custom"


class TestListProviders:
    """Tests for list_providers function."""

    def test_list_providers_includes_defaults(self) -> None:
        """Test that list_providers includes default providers."""
        providers = list_providers()
        assert "k3d" in providers
        assert "microk8s" in providers


class TestClusterProviderProtocol:
    """Tests for ClusterProvider protocol compliance."""

    def test_k3d_implements_protocol(self, mock_cli_ctx: MockCliContext) -> None:
        """Test that K3dProvider implements ClusterProvider protocol."""
        provider = K3dProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert isinstance(provider, ClusterProvider)

    def test_microk8s_implements_protocol(self, mock_cli_ctx: MockCliContext) -> None:
        """Test that Microk8sProvider implements ClusterProvider protocol."""
        provider = Microk8sProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
        assert isinstance(provider, ClusterProvider)


class TestSSHConfig:
    """Tests for SSHConfig dataclass."""

    def test_ssh_config_defaults(self) -> None:
        """Test SSHConfig default values."""
        config = SSHConfig(host="root@server")
        assert config.host == "root@server"
        assert config.key_path is None
        assert config.port == 22

    def test_ssh_config_with_all_options(self) -> None:
        """Test SSHConfig with all options specified."""
        config = SSHConfig(
            host="deploy@192.168.1.100",
            key_path=Path("/home/user/.ssh/id_ed25519"),
            port=2222,
        )
        assert config.host == "deploy@192.168.1.100"
        assert config.key_path == Path("/home/user/.ssh/id_ed25519")
        assert config.port == 2222

    def test_ssh_config_is_frozen(self) -> None:
        """Test that SSHConfig is immutable."""
        config = SSHConfig(host="root@server")
        with pytest.raises(AttributeError):
            config.host = "other@server"  # type: ignore[misc]
