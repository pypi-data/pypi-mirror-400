"""
Hetzner Cloud provider implementation.

Uses the official hcloud Python SDK to manage Hetzner Cloud VPS instances.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from hcloud import Client
from hcloud.images import Image
from hcloud.locations import Location
from hcloud.server_types import ServerType
from hcloud.servers import Server
from hcloud.ssh_keys import SSHKey

from djb.core.exceptions import DjbError
from djb.k8s.cloud.provider import ServerInfo

if TYPE_CHECKING:
    from hcloud.servers import BoundServer


class HetznerError(DjbError):
    """Hetzner Cloud API error."""

    pass


class HetznerCloudProvider:
    """Hetzner Cloud provider implementation.

    Provides methods to create, query, and manage Hetzner Cloud VPS instances.

    Example:
        provider = HetznerCloudProvider(api_token="hc_xxx...")
        server = provider.create_server(
            name="myproject-staging",
            server_type="cx23",
            location="nbg1",
            image="ubuntu-24.04",
            ssh_key_name="my-laptop-key",
        )
        print(f"Server IP: {server.ip}")
    """

    def __init__(self, api_token: str) -> None:
        """Initialize Hetzner Cloud provider.

        Args:
            api_token: Hetzner Cloud API token
        """
        self._client = Client(token=api_token)

    def _server_to_info(self, server: BoundServer) -> ServerInfo:
        """Convert hcloud server to ServerInfo."""
        ip = ""
        if server.public_net and server.public_net.ipv4:
            ip = server.public_net.ipv4.ip or ""
        return ServerInfo(
            name=server.name or "",
            ip=ip,
            id=server.id or 0,
            status=server.status or "unknown",
        )

    def create_server(
        self,
        name: str,
        server_type: str,
        location: str,
        image: str,
        ssh_key_name: str | None = None,
    ) -> ServerInfo:
        """Create a new Hetzner Cloud server.

        Args:
            name: Server name (must be unique within the account)
            server_type: Server type (e.g., "cx23", "cx32", "cx42")
            location: Datacenter location (e.g., "nbg1", "fsn1", "hel1")
            image: OS image (e.g., "ubuntu-24.04", "debian-12")
            ssh_key_name: Name of SSH key registered in Hetzner Cloud

        Returns:
            ServerInfo with the created server details

        Raises:
            HetznerError: If server creation fails
        """
        # Get SSH key if specified
        ssh_keys: list[SSHKey] = []
        if ssh_key_name:
            ssh_key = self._client.ssh_keys.get_by_name(ssh_key_name)
            if ssh_key is None:
                available_keys = [k.name for k in self._client.ssh_keys.get_all()]
                raise HetznerError(
                    f"SSH key '{ssh_key_name}' not found in Hetzner Cloud. "
                    f"Available keys: {available_keys}"
                )
            ssh_keys.append(ssh_key)

        # Validate server type exists
        server_type_obj = self._client.server_types.get_by_name(server_type)
        if server_type_obj is None:
            raise HetznerError(f"Server type '{server_type}' not found")

        # Validate location exists
        location_obj = self._client.locations.get_by_name(location)
        if location_obj is None:
            raise HetznerError(f"Location '{location}' not found")

        # Validate image exists
        architecture = server_type_obj.architecture or "x86"
        image_obj = self._client.images.get_by_name_and_architecture(
            name=image, architecture=architecture
        )
        if image_obj is None:
            raise HetznerError(f"Image '{image}' not found for architecture {architecture}")

        try:
            response = self._client.servers.create(
                name=name,
                server_type=ServerType(name=server_type),
                image=Image(name=image),
                location=Location(name=location),
                ssh_keys=ssh_keys if ssh_keys else None,
            )
            server = response.server
        except Exception as e:
            raise HetznerError(f"Failed to create server: {e}") from e

        return self._server_to_info(server)

    def get_server(self, name: str) -> ServerInfo | None:
        """Get server by name.

        Args:
            name: Server name to look up

        Returns:
            ServerInfo if found, None if server doesn't exist
        """
        server = self._client.servers.get_by_name(name)
        if server is None:
            return None
        return self._server_to_info(server)

    def list_ssh_keys(self) -> list[str]:
        """List all SSH key names registered in Hetzner Cloud.

        Returns:
            List of SSH key names
        """
        keys = self._client.ssh_keys.get_all()
        return [k.name for k in keys if k.name]

    def get_ssh_keys_with_details(self) -> list[tuple[str, str | None]]:
        """Get SSH keys with their public keys.

        Returns:
            List of (name, public_key) tuples. The public_key may contain
            an email comment at the end (e.g., "ssh-ed25519 AAAA... user@example.com").
        """
        keys = self._client.ssh_keys.get_all()
        return [(k.name, k.public_key) for k in keys if k.name]

    def delete_server(self, name: str) -> None:
        """Delete a server by name.

        Args:
            name: Server name to delete

        Raises:
            HetznerError: If server not found or deletion fails
        """
        server = self._client.servers.get_by_name(name)
        if server is None:
            raise HetznerError(f"Server '{name}' not found")

        try:
            server.delete()
        except Exception as e:
            raise HetznerError(f"Failed to delete server: {e}") from e

    def wait_for_server(self, name: str, timeout: int = 120) -> ServerInfo:
        """Wait for server to be ready.

        Polls the server status until it reaches "running" state.

        Args:
            name: Server name to wait for
            timeout: Maximum wait time in seconds

        Returns:
            ServerInfo when server is ready

        Raises:
            HetznerError: If timeout is reached or server not found
        """
        start_time = time.time()
        poll_interval = 5

        while True:
            server = self._client.servers.get_by_name(name)
            if server is None:
                raise HetznerError(f"Server '{name}' not found while waiting")

            if server.status == Server.STATUS_RUNNING:
                return self._server_to_info(server)

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise HetznerError(
                    f"Timeout waiting for server '{name}' to be ready. "
                    f"Current status: {server.status}"
                )

            time.sleep(poll_interval)
