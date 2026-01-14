"""E2E tests for djb deploy k8s main command.

These tests verify the k8s deployment command behavior with mocked providers
and real config loading.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from djb.cli.djb import djb_cli

pytestmark = pytest.mark.e2e_marker


class TestDeployK8sAutoProvisioning:
    """E2E tests for auto-provisioning flow."""

    def test_k8s_without_host_triggers_auto_provisioning(
        self, cli_runner: CliRunner, make_djb_config
    ) -> None:
        """Test that deploy k8s without --host attempts auto-provisioning.

        When run from a djb project directory with Hetzner config, the command
        will attempt to auto-provision using the configured server. This test
        verifies that the auto-provisioning flow is triggered.
        """
        # Create a config with Hetzner server configured
        config = make_djb_config()

        # Mock the auto-provisioning functions to verify they're called
        # without actually connecting to infrastructure
        with (
            patch("djb.cli.djb.get_djb_config", return_value=config),
            patch(
                "djb.cli.k8s.k8s._ensure_server_materialized",
                return_value="root@test-server",
            ) as mock_materialize,
            patch("djb.cli.k8s.k8s._ensure_infrastructure_provisioned") as mock_provision,
            patch("djb.cli.k8s.k8s._ensure_dns_configured"),  # Avoid secrets loading
            patch("djb.cli.k8s.k8s._ensure_buildpacks_built"),  # Avoid buildpack building
            patch(
                "djb.cli.k8s.k8s.deploy_k8s",
                side_effect=Exception("Mock deploy error"),
            ),
        ):
            result = cli_runner.invoke(djb_cli, ["deploy", "k8s"])

            # Verify auto-provisioning was triggered (not a "missing --host" error)
            assert result.exit_code != 0
            assert "Mock deploy error" in str(result.exception)

            # The auto-provisioning functions should have been called
            mock_materialize.assert_called_once()
            mock_provision.assert_called_once()
