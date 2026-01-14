"""
Cloud provider protocol and common types.

This module defines the abstract interface for cloud provider implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ServerInfo:
    """Information about a provisioned server.

    Attributes:
        name: Server name (e.g., "myproject-staging")
        ip: Public IP address
        id: Provider-specific server ID
        status: Current status (e.g., "running", "starting")
    """

    name: str
    ip: str
    id: int
    status: str


class CloudProviderProtocol(Protocol):
    """Protocol for cloud provider implementations.

    Implementations provide methods to create, query, and manage VPS instances.
    Each provider handles its own authentication (typically via API tokens).

    Example implementations:
        - HetznerCloudProvider: Hetzner Cloud VPS
        - Future: DigitalOceanProvider, LinodeProvider, etc.
    """

    def create_server(
        self,
        name: str,
        server_type: str,
        location: str,
        image: str,
        ssh_key_name: str | None = None,
    ) -> ServerInfo:
        """Create a new server.

        Args:
            name: Server name (must be unique within the account)
            server_type: Server type/size (e.g., "cx23", "cx32")
            location: Datacenter location (e.g., "nbg1", "fsn1")
            image: OS image (e.g., "ubuntu-24.04")
            ssh_key_name: Name of SSH key registered with the provider

        Returns:
            ServerInfo with the created server details

        Raises:
            Provider-specific error if creation fails
        """
        ...

    def get_server(self, name: str) -> ServerInfo | None:
        """Get server by name.

        Args:
            name: Server name to look up

        Returns:
            ServerInfo if found, None if server doesn't exist
        """
        ...

    def delete_server(self, name: str) -> None:
        """Delete a server by name.

        Args:
            name: Server name to delete

        Raises:
            Provider-specific error if deletion fails
        """
        ...

    def wait_for_server(self, name: str, timeout: int = 120) -> ServerInfo:
        """Wait for server to be ready.

        Polls the server status until it reaches "running" state.

        Args:
            name: Server name to wait for
            timeout: Maximum wait time in seconds

        Returns:
            ServerInfo when server is ready

        Raises:
            Provider-specific error if timeout is reached or server fails
        """
        ...
