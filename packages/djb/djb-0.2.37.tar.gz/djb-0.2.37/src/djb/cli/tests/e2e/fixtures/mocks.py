"""Mock fixtures for E2E tests.

These fixtures mock external cloud services (Heroku, PyPI, Hetzner, Cloudflare).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock, patch

import pytest

from djb.cli.utils import CmdRunner
from djb.dns import DnsRecord
from djb.k8s.cloud import ServerInfo

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mock_heroku_cli():
    """Mock Heroku CLI commands via CmdRunner.run.

    Intercepts heroku commands and returns appropriate mock responses.
    Non-heroku commands fall through to real execution.
    Unknown heroku commands return an error to catch typos and missing mock cases.
    """
    original_run = CmdRunner.run

    def heroku_side_effect(runner_self, cmd, *args, **kwargs):
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd

        if "heroku" not in cmd_str:
            # Not a heroku command, use real CmdRunner
            return original_run(runner_self, cmd, *args, **kwargs)

        # Mock known heroku commands
        if "auth:whoami" in cmd_str:
            return Mock(returncode=0, stdout="e2e-test@example.com\n", stderr="")
        if "apps:info" in cmd_str:
            return Mock(returncode=0, stdout="=== e2e-test-app\n", stderr="")
        if "config:set" in cmd_str:
            return Mock(returncode=0, stdout="", stderr="")
        if "config:get" in cmd_str:
            return Mock(returncode=0, stdout="mock-value\n", stderr="")
        if "buildpacks" in cmd_str:
            return Mock(returncode=0, stdout="heroku/python\n", stderr="")
        if "addons" in cmd_str:
            return Mock(returncode=0, stdout="", stderr="")
        if "run" in cmd_str:
            return Mock(returncode=0, stdout="", stderr="")
        if "git:remote" in cmd_str:
            return Mock(returncode=0, stdout="", stderr="")

        # Unknown heroku command - return error to catch typos/missing mocks
        return Mock(
            returncode=1,
            stdout="",
            stderr=f"mock_heroku_cli: Unknown command '{cmd_str}'. Add a mock case.",
        )

    with patch.object(CmdRunner, "run", heroku_side_effect):
        yield


@pytest.fixture
def mock_pypi_publish():
    """Mock PyPI publishing workflow.

    Mocks the publish-related functions to avoid actual PyPI uploads.
    """
    with patch.object(CmdRunner, "run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        yield mock_run


@pytest.fixture
def mock_hetzner_provider() -> Generator[MagicMock, None, None]:
    """Mock HetznerCloudProvider for E2E tests.

    Mocks the provider class to avoid real Hetzner API calls.
    Returns a mock instance that can be configured per-test for different scenarios.

    Default behaviors:
    - get_server: Returns None (no existing server)
    - list_ssh_keys: Returns ["my-key"]
    - get_ssh_keys_with_details: Returns [("my-key", "ssh-ed25519 ... test@example.com")]
    - create_server: Returns a ServerInfo with test values
    - wait_for_server: Returns a ServerInfo with test values

    Usage:
        def test_something(mock_hetzner_provider):
            # Override default behavior for this test
            mock_hetzner_provider.get_server.return_value = ServerInfo(
                name="existing", ip="5.6.7.8", id=999, status="running"
            )
    """
    with patch("djb.machine_state.materialize.hetzner.helpers.HetznerCloudProvider") as mock_class:
        mock_provider = MagicMock()
        mock_class.return_value = mock_provider

        # Default behaviors - can be overridden in individual tests
        mock_provider.get_server.return_value = None  # No existing server
        mock_provider.list_ssh_keys.return_value = ["my-key"]
        mock_provider.get_ssh_keys_with_details.return_value = [
            ("my-key", "ssh-ed25519 AAAA... test@example.com")
        ]
        mock_provider.create_server.return_value = ServerInfo(
            name="test-server", ip="1.2.3.4", id=12345, status="running"
        )
        mock_provider.wait_for_server.return_value = ServerInfo(
            name="test-server", ip="1.2.3.4", id=12345, status="running"
        )

        yield mock_provider


@pytest.fixture
def mock_cloudflare_provider() -> Generator[MagicMock, None, None]:
    """Mock CloudflareDnsProvider for E2E tests.

    Mocks the provider class to avoid real Cloudflare API calls.
    Returns a mock instance that can be configured per-test for different scenarios.

    Default behaviors:
    - get_zone_id: Returns "zone-123"
    - configure_domain: Returns a list with A records for bare and www
    - list_records: Returns empty list
    - delete_record: No-op

    Usage:
        def test_something(mock_cloudflare_provider):
            # Override default behavior for this test
            mock_cloudflare_provider.list_records.return_value = [
                DnsRecord(id="rec-1", name="example.com", ...)
            ]
    """
    with patch("djb.cli.domain.CloudflareDnsProvider") as mock_class:
        mock_provider = MagicMock()
        mock_class.return_value = mock_provider

        # Default behaviors - can be overridden in individual tests
        mock_provider.get_zone_id.return_value = "zone-123"
        mock_provider.configure_domain.return_value = [
            DnsRecord(
                id="rec-1",
                type="A",
                name="example.com",
                content="1.2.3.4",
                ttl=300,
                proxied=False,
            ),
            DnsRecord(
                id="rec-2",
                type="A",
                name="www.example.com",
                content="1.2.3.4",
                ttl=300,
                proxied=False,
            ),
        ]
        mock_provider.list_records.return_value = []

        yield mock_provider
