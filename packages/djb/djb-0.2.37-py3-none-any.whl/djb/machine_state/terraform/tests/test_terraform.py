"""Unit tests for terraform MachineStates.

These tests mock the ClusterProvider to test state behavior.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from djb.config import DjbConfig, K8sConfig
from djb.machine_state.terraform import (
    CloudNativePGInstalled,
    K8sAddonsEnabled,
    K8sClusterCreated,
    K8sClusterRunning,
    K8sInfrastructureReady,
    LetsEncryptIssuerConfigured,
    TerraformOptions,
    get_cluster_provider_from_context,
)
from djb.k8s import Addon
from djb.types import K8sClusterType


# =============================================================================
# TerraformOptions Tests
# =============================================================================


class TestTerraformOptions:
    """Tests for TerraformOptions dataclass."""

    def test_default_values(self) -> None:
        """TerraformOptions has sensible defaults."""
        opts = TerraformOptions()

        assert opts.force_create is False

    def test_force_create(self) -> None:
        """TerraformOptions accepts force_create."""
        opts = TerraformOptions(force_create=True)

        assert opts.force_create is True


# =============================================================================
# Terraform Helpers Tests
# =============================================================================


class TestTerraformHelpers:
    """Tests for terraform helper functions."""

    def test_rejects_remote_k3d(self, mock_djb_config, mock_machine_context) -> None:
        """get_cluster_provider_from_context() rejects k3d with a remote host."""
        config = mock_djb_config(
            DjbConfig(k8s=K8sConfig(host="192.168.1.100", cluster_type=K8sClusterType.K3D))
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.raises(ValueError, match="microk8s"):
            get_cluster_provider_from_context(ctx)


# =============================================================================
# K8sClusterCreated Tests
# =============================================================================


class TestK8sClusterCreated:
    """Tests for K8sClusterCreated state."""

    def test_describe(self, mock_djb_config, mock_machine_context) -> None:
        """describe() returns cluster name."""
        state = K8sClusterCreated()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(cluster_name="djb-myapp")))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.describe(ctx) == "K8s cluster 'djb-myapp' exists"

    def test_describe_derives_from_project_name(
        self, mock_djb_config, mock_machine_context
    ) -> None:
        """describe() derives cluster name from project_name if not set."""
        state = K8sClusterCreated()
        config = mock_djb_config(DjbConfig(project_name="myapp", k8s=K8sConfig(cluster_name=None)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.describe(ctx) == "K8s cluster 'djb-myapp' exists"

    def test_check_true_when_cluster_exists(self, mock_machine_context) -> None:
        """check() returns True when cluster exists."""
        state = K8sClusterCreated()
        ctx = mock_machine_context(options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.exists.return_value = True
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is True

    def test_check_false_when_cluster_not_exists(self, mock_machine_context) -> None:
        """check() returns False when cluster doesn't exist."""
        state = K8sClusterCreated()
        ctx = mock_machine_context(options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.exists.return_value = False
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is False

    def test_satisfy_creates_cluster(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() creates cluster via provider."""
        state = K8sClusterCreated()
        config = mock_djb_config(
            DjbConfig(k8s=K8sConfig(cluster_name="djb-myapp", cluster_type=K8sClusterType.K3D))
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.exists.return_value = False  # check() returns False
            mock_provider.create.return_value = True
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            task = state.satisfy(ctx)
            result = task.run()

            assert result.success is True
            mock_provider.create.assert_called_once_with("djb-myapp")


# =============================================================================
# K8sClusterRunning Tests
# =============================================================================


class TestK8sClusterRunning:
    """Tests for K8sClusterRunning state."""

    def test_describe(self, mock_djb_config, mock_machine_context) -> None:
        """describe() returns cluster name."""
        state = K8sClusterRunning()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(cluster_name="djb-myapp")))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.describe(ctx) == "K8s cluster 'djb-myapp' running"

    def test_describe_derives_from_project_name(
        self, mock_djb_config, mock_machine_context
    ) -> None:
        """describe() derives cluster name from project_name if not set."""
        state = K8sClusterRunning()
        config = mock_djb_config(DjbConfig(project_name="myapp", k8s=K8sConfig(cluster_name=None)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.describe(ctx) == "K8s cluster 'djb-myapp' running"

    def test_check_true_when_cluster_running(self, mock_machine_context) -> None:
        """check() returns True when cluster is running."""
        state = K8sClusterRunning()
        ctx = mock_machine_context(options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.is_running.return_value = True
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is True

    def test_check_false_when_cluster_not_running(self, mock_machine_context) -> None:
        """check() returns False when cluster is not running."""
        state = K8sClusterRunning()
        ctx = mock_machine_context(options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.is_running.return_value = False
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is False

    def test_satisfy_starts_cluster(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() starts cluster via provider."""
        state = K8sClusterRunning()
        config = mock_djb_config(
            DjbConfig(k8s=K8sConfig(cluster_name="djb-myapp", cluster_type=K8sClusterType.K3D))
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.is_running.return_value = False  # check() returns False
            mock_provider.start.return_value = True
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            task = state.satisfy(ctx)
            result = task.run()

            assert result.success is True
            mock_provider.start.assert_called_once_with("djb-myapp")


# =============================================================================
# K8sAddonsEnabled Tests
# =============================================================================


class TestK8sAddonsEnabled:
    """Tests for K8sAddonsEnabled state."""

    def test_describe_k3d(self, mock_djb_config, mock_machine_context) -> None:
        """describe() lists k3d addons."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(cluster_type=K8sClusterType.K3D)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert "dns" in state.describe(ctx)
        assert "registry" in state.describe(ctx)

    def test_describe_with_host(self, mock_djb_config, mock_machine_context) -> None:
        """describe() lists addons including cert-manager when host is set."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(
            DjbConfig(k8s=K8sConfig(host="192.168.1.100"), email="test@example.com")
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        desc = state.describe(ctx)
        assert "dns" in desc
        assert "storage" in desc
        assert "registry" in desc
        assert "ingress" in desc
        assert "cert-manager" in desc

    def test_describe_skips_cert_manager_when_no_tls(
        self, mock_djb_config, mock_machine_context
    ) -> None:
        """describe() omits cert-manager when TLS is disabled."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(host="192.168.1.100", no_tls=True)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        desc = state.describe(ctx)
        assert "cert-manager" not in desc

    def test_describe_skips_cert_manager_without_email(
        self, mock_djb_config, mock_machine_context
    ) -> None:
        """describe() omits cert-manager when no email is configured."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(host="192.168.1.100")))
        # Explicitly set email to None (to_overrides() doesn't track None values)
        config.email = None
        config.letsencrypt.email = None
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        desc = state.describe(ctx)
        assert "cert-manager" not in desc

    def test_check_true_when_all_enabled(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns True when all required addons are enabled."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(cluster_type=K8sClusterType.K3D)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            # k3d requires dns, storage, ingress, registry
            mock_provider.get_enabled_addons.return_value = {
                Addon.DNS,
                Addon.STORAGE,
                Addon.INGRESS,
                Addon.REGISTRY,
            }
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is True

    def test_check_false_when_missing_addons(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns False when some addons are missing."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(cluster_type=K8sClusterType.MICROK8S)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            # Only dns enabled, but microk8s needs dns, storage, registry, ingress
            mock_provider.get_enabled_addons.return_value = {Addon.DNS}
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is False

    def test_satisfy_enables_missing_addons(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() enables only missing addons, one at a time."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(
                    cluster_name="djb-myapp", cluster_type=K8sClusterType.MICROK8S, host=None
                )
            )
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            # Only dns is enabled, so storage, registry, ingress should be missing
            mock_provider.get_enabled_addons.return_value = {Addon.DNS}
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            task = state.satisfy(ctx)
            result = task.run()

            assert result.success is True
            # Each addon enabled individually for incremental progress
            assert mock_provider.enable_addons.call_count == 3  # storage, registry, ingress
            # Collect all enabled addons from all calls
            enabled: set[Addon] = set()
            for call in mock_provider.enable_addons.call_args_list:
                assert call[0][0] == "djb-myapp"
                enabled.update(call[0][1])
            # dns is already enabled, so shouldn't be in the list
            assert Addon.DNS not in enabled
            # storage, registry, ingress should be enabled
            assert Addon.STORAGE in enabled
            assert Addon.REGISTRY in enabled
            assert Addon.INGRESS in enabled

    def test_satisfy_skips_when_all_enabled(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() doesn't call enable_addons when all are enabled."""
        state = K8sAddonsEnabled()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(cluster_name="djb-myapp", cluster_type=K8sClusterType.K3D, host=None)
            )
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            # All required addons are already enabled
            mock_provider.get_enabled_addons.return_value = {
                Addon.DNS,
                Addon.STORAGE,
                Addon.INGRESS,
                Addon.REGISTRY,
            }
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            task = state.satisfy(ctx)
            result = task.run()

            assert result.success is True
            mock_provider.enable_addons.assert_not_called()


# =============================================================================
# CloudNativePGInstalled Tests
# =============================================================================


class TestCloudNativePGInstalled:
    """Tests for CloudNativePGInstalled state."""

    def test_describe(self, mock_machine_context) -> None:
        """describe() returns expected string."""
        state = CloudNativePGInstalled()
        ctx = mock_machine_context(options=TerraformOptions())

        assert state.describe(ctx) == "CloudNativePG operator"

    def test_skip_when_flag_set(self, mock_djb_config, mock_machine_context) -> None:
        """skip() returns True when no_cloudnativepg is True."""
        state = CloudNativePGInstalled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(no_cloudnativepg=True)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.skip(ctx) is True

    def test_check_true_when_installed(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns True when operator is installed."""
        state = CloudNativePGInstalled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(no_cloudnativepg=False)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.kubectl.return_value = (0, "cnpg-controller-manager", "")
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is True

    def test_check_false_when_not_installed(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns False when operator not installed."""
        state = CloudNativePGInstalled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(no_cloudnativepg=False)))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.kubectl.return_value = (1, "", "not found")
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is False

    def test_satisfy_installs_operator(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() applies CNPG manifest."""
        state = CloudNativePGInstalled()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(cluster_name="djb-myapp")))
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            # First call (check) returns not found, subsequent calls succeed
            mock_provider.kubectl.side_effect = [
                (1, "", "not found"),  # check() - deployment not found
                (0, "", ""),  # satisfy() - apply succeeds
                (0, "", ""),  # satisfy() - wait succeeds
            ]
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            task = state.satisfy(ctx)
            result = task.run()

            assert result.success is True
            # Verify kubectl was called - at least 2 calls (check + apply)
            assert mock_provider.kubectl.call_count >= 2
            # The apply call should be the second call
            apply_call = mock_provider.kubectl.call_args_list[1]
            assert apply_call[0][0] == "djb-myapp"
            assert "apply" in apply_call[0]


# =============================================================================
# LetsEncryptIssuerConfigured Tests
# =============================================================================


class TestLetsEncryptIssuerConfigured:
    """Tests for LetsEncryptIssuerConfigured state."""

    def test_describe(self, mock_machine_context) -> None:
        """describe() returns expected string."""
        state = LetsEncryptIssuerConfigured()
        ctx = mock_machine_context(options=TerraformOptions())

        assert state.describe(ctx) == "Let's Encrypt ClusterIssuer"

    def test_skip_when_not_public(self, mock_djb_config, mock_machine_context) -> None:
        """skip() returns True when not public (local mode)."""
        state = LetsEncryptIssuerConfigured()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(host=None)))  # is_public=False
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.skip(ctx) is True

    def test_skip_when_no_tls(self, mock_djb_config, mock_machine_context) -> None:
        """skip() returns True when no_tls is True."""
        state = LetsEncryptIssuerConfigured()
        config = mock_djb_config(
            DjbConfig(k8s=K8sConfig(host="192.168.1.100", no_tls=True), email="a@b.com")
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.skip(ctx) is True

    def test_skip_when_no_email(self, mock_djb_config, mock_machine_context) -> None:
        """skip() returns True when no email provided."""
        state = LetsEncryptIssuerConfigured()
        config = mock_djb_config(DjbConfig(k8s=K8sConfig(host="192.168.1.100", no_tls=False)))
        # Explicitly set email to None (to_overrides() doesn't track None values)
        config.email = None
        config.letsencrypt.email = None
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        assert state.skip(ctx) is True

    def test_check_true_when_issuer_exists(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns True when ClusterIssuer exists."""
        state = LetsEncryptIssuerConfigured()
        config = mock_djb_config(
            DjbConfig(k8s=K8sConfig(host="192.168.1.100", no_tls=False), email="a@b.com")
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.kubectl.return_value = (0, "letsencrypt-prod", "")
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is True

    def test_check_false_when_issuer_not_exists(
        self, mock_djb_config, mock_machine_context
    ) -> None:
        """check() returns False when ClusterIssuer doesn't exist."""
        state = LetsEncryptIssuerConfigured()
        config = mock_djb_config(
            DjbConfig(k8s=K8sConfig(host="192.168.1.100", no_tls=False), email="a@b.com")
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            mock_provider.kubectl.return_value = (1, "", "not found")
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )

            assert state.check(ctx) is False

    def test_satisfy_creates_issuer(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() applies ClusterIssuer manifest."""
        state = LetsEncryptIssuerConfigured()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(cluster_name="djb-myapp", host="192.168.1.100"),
                email="admin@example.com",
            )
        )
        ctx = mock_machine_context(config=config, options=TerraformOptions())

        # Mock manifest content with email
        mock_manifest = "apiVersion: cert-manager.io/v1\nemail: admin@example.com"

        with pytest.MonkeyPatch.context() as mp:
            mock_provider = MagicMock()
            # check() returns not found, so satisfy() runs
            mock_provider.kubectl.return_value = (1, "", "not found")
            mp.setattr(
                "djb.machine_state.terraform.states.get_cluster_provider_from_context",
                lambda _: mock_provider,
            )
            # Mock render_template to avoid filesystem operations
            mp.setattr(
                "djb.machine_state.terraform.states.render_template",
                lambda *args, **kwargs: mock_manifest,
            )

            task = state.satisfy(ctx)
            result = task.run()

            assert result.success is True
            mock_provider.apply_manifests.assert_called_once()
            call_args = mock_provider.apply_manifests.call_args
            assert call_args[0][0] == "djb-myapp"
            manifests = call_args[0][1]
            assert "clusterissuer.yaml" in manifests
            assert "admin@example.com" in manifests["clusterissuer.yaml"]


# =============================================================================
# K8sInfrastructureReady Composite Tests
# =============================================================================


class TestK8sInfrastructureReady:
    """Tests for K8sInfrastructureReady composite state."""

    def test_has_substates(self) -> None:
        """Composite state has expected substates."""
        substates = K8sInfrastructureReady._substates
        assert "vps_materialized" in substates
        assert "cluster_running" in substates
        assert "addons_enabled" in substates
        assert "cloudnativepg_installed" in substates
        assert "letsencrypt_issuer" in substates

    def test_describe(self, mock_machine_context) -> None:
        """describe() derives from class name."""
        state = K8sInfrastructureReady()
        ctx = mock_machine_context(options=TerraformOptions())

        # Derived from class name by metaclass
        assert state.describe(ctx) == "K8s infrastructure ready"
