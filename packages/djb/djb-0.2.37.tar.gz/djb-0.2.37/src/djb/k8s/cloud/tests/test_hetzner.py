"""Unit tests for HetznerCloudProvider.

These tests mock the hcloud SDK to test the provider logic.
"""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from djb.config.constants import (
    HetznerImage,
    HetznerLocation,
    HetznerServerType,
)
from djb.k8s.cloud import HetznerCloudProvider, HetznerError, ServerInfo

# Use enum defaults for test values
DEFAULT_SERVER_TYPE = HetznerServerType.CX23.value
DEFAULT_LOCATION = HetznerLocation.NBG1.value
DEFAULT_IMAGE = HetznerImage.UBUNTU_24_04.value


class TestHetznerCloudProvider:
    """Tests for HetznerCloudProvider."""

    @pytest.fixture
    def mock_client(self) -> Generator[MagicMock, None, None]:
        """Create a mock hcloud Client."""
        with patch("djb.k8s.cloud.hetzner.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            yield mock_client

    def test_create_server_success(self, mock_client: MagicMock) -> None:
        """Test successful server creation."""
        # Set up mocks
        mock_ssh_key = MagicMock()
        mock_ssh_key.name = "my-key"
        mock_client.ssh_keys.get_by_name.return_value = mock_ssh_key

        mock_server_type = MagicMock()
        mock_server_type.architecture = "x86"
        mock_client.server_types.get_by_name.return_value = mock_server_type

        mock_location = MagicMock()
        mock_client.locations.get_by_name.return_value = mock_location

        mock_image = MagicMock()
        mock_client.images.get_by_name_and_architecture.return_value = mock_image

        mock_server = MagicMock()
        mock_server.name = "test-server"
        mock_server.id = 12345
        mock_server.status = "running"
        mock_server.public_net.ipv4.ip = "1.2.3.4"

        mock_response = MagicMock()
        mock_response.server = mock_server
        mock_client.servers.create.return_value = mock_response

        # Create provider and server
        provider = HetznerCloudProvider(api_token="test-token")
        server = provider.create_server(
            name="test-server",
            server_type=DEFAULT_SERVER_TYPE,
            location=DEFAULT_LOCATION,
            image=DEFAULT_IMAGE,
            ssh_key_name="my-key",
        )

        # Verify result
        assert server.name == "test-server"
        assert server.ip == "1.2.3.4"
        assert server.id == 12345
        assert server.status == "running"

    def test_create_server_ssh_key_not_found(self, mock_client: MagicMock) -> None:
        """Test server creation fails when SSH key not found."""
        mock_client.ssh_keys.get_by_name.return_value = None
        mock_client.ssh_keys.get_all.return_value = [
            MagicMock(name="other-key"),
            MagicMock(name="another-key"),
        ]

        provider = HetznerCloudProvider(api_token="test-token")

        with pytest.raises(HetznerError) as exc_info:
            provider.create_server(
                name="test-server",
                server_type=DEFAULT_SERVER_TYPE,
                location=DEFAULT_LOCATION,
                image=DEFAULT_IMAGE,
                ssh_key_name="missing-key",
            )

        assert "SSH key 'missing-key' not found" in str(exc_info.value)
        assert "other-key" in str(exc_info.value)

    def test_create_server_invalid_server_type(self, mock_client: MagicMock) -> None:
        """Test server creation fails with invalid server type."""
        mock_ssh_key = MagicMock()
        mock_client.ssh_keys.get_by_name.return_value = mock_ssh_key
        mock_client.server_types.get_by_name.return_value = None

        provider = HetznerCloudProvider(api_token="test-token")

        with pytest.raises(HetznerError) as exc_info:
            provider.create_server(
                name="test-server",
                server_type="invalid-type",
                location=DEFAULT_LOCATION,
                image=DEFAULT_IMAGE,
                ssh_key_name="my-key",
            )

        assert "Server type 'invalid-type' not found" in str(exc_info.value)

    def test_get_server_found(self, mock_client: MagicMock) -> None:
        """Test getting an existing server."""
        mock_server = MagicMock()
        mock_server.name = "test-server"
        mock_server.id = 12345
        mock_server.status = "running"
        mock_server.public_net.ipv4.ip = "1.2.3.4"
        mock_client.servers.get_by_name.return_value = mock_server

        provider = HetznerCloudProvider(api_token="test-token")
        server = provider.get_server("test-server")

        assert server is not None
        assert server.name == "test-server"
        assert server.ip == "1.2.3.4"

    def test_get_server_not_found(self, mock_client: MagicMock) -> None:
        """Test getting a non-existent server returns None."""
        mock_client.servers.get_by_name.return_value = None

        provider = HetznerCloudProvider(api_token="test-token")
        server = provider.get_server("missing-server")

        assert server is None

    def test_delete_server_success(self, mock_client: MagicMock) -> None:
        """Test successful server deletion."""
        mock_server = MagicMock()
        mock_client.servers.get_by_name.return_value = mock_server

        provider = HetznerCloudProvider(api_token="test-token")
        provider.delete_server("test-server")

        mock_server.delete.assert_called_once()

    def test_delete_server_not_found(self, mock_client: MagicMock) -> None:
        """Test deleting a non-existent server raises error."""
        mock_client.servers.get_by_name.return_value = None

        provider = HetznerCloudProvider(api_token="test-token")

        with pytest.raises(HetznerError) as exc_info:
            provider.delete_server("missing-server")

        assert "Server 'missing-server' not found" in str(exc_info.value)

    def test_wait_for_server_already_running(self, mock_client: MagicMock) -> None:
        """Test wait_for_server when server is already running."""
        mock_server = MagicMock()
        mock_server.name = "test-server"
        mock_server.id = 12345
        mock_server.status = "running"
        mock_server.public_net.ipv4.ip = "1.2.3.4"
        mock_client.servers.get_by_name.return_value = mock_server

        provider = HetznerCloudProvider(api_token="test-token")
        server = provider.wait_for_server("test-server", timeout=10)

        assert server.status == "running"

    def test_wait_for_server_not_found(self, mock_client: MagicMock) -> None:
        """Test wait_for_server when server doesn't exist."""
        mock_client.servers.get_by_name.return_value = None

        provider = HetznerCloudProvider(api_token="test-token")

        with pytest.raises(HetznerError) as exc_info:
            provider.wait_for_server("missing-server", timeout=10)

        assert "not found while waiting" in str(exc_info.value)


class TestServerInfo:
    """Tests for ServerInfo dataclass."""

    def test_server_info_immutable(self) -> None:
        """Test that ServerInfo is immutable (frozen)."""
        info = ServerInfo(name="test", ip="1.2.3.4", id=123, status="running")

        with pytest.raises(AttributeError):
            info.name = "changed"  # type: ignore[misc]

    def test_server_info_equality(self) -> None:
        """Test ServerInfo equality."""
        info1 = ServerInfo(name="test", ip="1.2.3.4", id=123, status="running")
        info2 = ServerInfo(name="test", ip="1.2.3.4", id=123, status="running")
        info3 = ServerInfo(name="other", ip="1.2.3.4", id=123, status="running")

        assert info1 == info2
        assert info1 != info3
