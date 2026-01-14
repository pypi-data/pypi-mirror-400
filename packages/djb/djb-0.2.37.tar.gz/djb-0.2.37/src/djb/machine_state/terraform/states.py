"""Terraform machine states - K8s infrastructure provisioning.

States are ordered as they appear in the K8sInfrastructureReady composite:
1. K8sClusterCreated - Create K8s cluster
2. K8sClusterRunning - Start K8s cluster
3. K8sAddonsEnabled - Enable required addons
4. CloudNativePGInstalled - Install PostgreSQL operator
5. LetsEncryptIssuerConfigured - Configure TLS
6. K8sInfrastructureReady - Composite state
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from djb.core.logging import get_logger
from djb.k8s import Addon, ClusterError, render_template
from djb.machine_state import ForceCreateOptions, MachineStateABC, task
from djb.machine_state.materialize.hetzner import HetznerVPSMaterialized

from .helpers import get_cluster_provider_from_context

if TYPE_CHECKING:
    from djb.machine_state import MachineContext

logger = get_logger(__name__)


@dataclass
class TerraformOptions(ForceCreateOptions):
    """Options for terraform states.

    This is intentionally thin - prefer config for persistent settings.
    Options are for ephemeral runtime flags that don't make sense to persist.

    Inherited from ForceCreateOptions:
        force_create: Force new server creation even if one exists.

    Inherited from BaseOptions:
        search_strategy: Strategy for finding first unsatisfied task.

    All other settings come from config:
        - config.k8s.cluster_name - Cluster name (or derived from project_name)
        - config.k8s.cluster_type - K8s distribution (K3D or MICROK8S)
        - config.k8s.host - SSH host (None = local mode)
        - config.k8s.port - SSH port
        - config.k8s.ssh_key - Path to SSH private key
        - config.k8s.no_cloudnativepg - Skip CloudNativePG
        - config.k8s.no_tls - Skip Let's Encrypt
        - config.letsencrypt.effective_email - Email for TLS
        - config.k8s.provider - K8sProvider (MANUAL or HETZNER)
    """

    pass


# =============================================================================
# K8sClusterCreated
# =============================================================================


class K8sClusterCreated(MachineStateABC):
    """Kubernetes cluster exists.

    Check:
        True if cluster exists.

    Satisfy:
        Create cluster using the appropriate provider (k3d or microk8s).
        For remote mode (host set), connects via SSH to create/manage.
    """

    def describe(self, ctx: MachineContext[TerraformOptions]) -> str:
        cluster_name = ctx.config.k8s.effective_cluster_name
        return f"K8s cluster '{cluster_name}' exists"

    def check(self, ctx: MachineContext[TerraformOptions]) -> bool:
        provider = get_cluster_provider_from_context(ctx)
        cluster_name = ctx.config.k8s.effective_cluster_name
        return provider.exists(cluster_name)

    @task
    def satisfy(self, ctx: MachineContext[TerraformOptions]) -> None:
        provider = get_cluster_provider_from_context(ctx)
        cluster_name = ctx.config.k8s.effective_cluster_name
        cluster_type = ctx.config.k8s.cluster_type.value

        created = provider.create(cluster_name)
        if created:
            logger.done(f"{cluster_type} cluster '{cluster_name}' created")
        else:
            # check() said not satisfied but cluster exists - race condition?
            logger.warning(f"{cluster_type} cluster '{cluster_name}' already exists")


# =============================================================================
# K8sClusterRunning
# =============================================================================


class K8sClusterRunning(MachineStateABC):
    """Kubernetes cluster is running.

    Check:
        True if cluster is running.

    Satisfy:
        Start cluster if stopped.
    """

    def describe(self, ctx: MachineContext[TerraformOptions]) -> str:
        cluster_name = ctx.config.k8s.effective_cluster_name
        return f"K8s cluster '{cluster_name}' running"

    def check(self, ctx: MachineContext[TerraformOptions]) -> bool:
        provider = get_cluster_provider_from_context(ctx)
        cluster_name = ctx.config.k8s.effective_cluster_name
        return provider.is_running(cluster_name)

    @task
    def satisfy(self, ctx: MachineContext[TerraformOptions]) -> None:
        provider = get_cluster_provider_from_context(ctx)
        cluster_name = ctx.config.k8s.effective_cluster_name

        started = provider.start(cluster_name)
        if started:
            logger.done(f"Cluster '{cluster_name}' started")
        else:
            # check() said not satisfied but cluster is running - race condition?
            logger.warning(f"Cluster '{cluster_name}' already running")


# =============================================================================
# K8sAddonsEnabled
# =============================================================================


# Core addons required by all deployments
REQUIRED_ADDONS = [Addon.DNS, Addon.STORAGE, Addon.INGRESS, Addon.REGISTRY]


def _needs_cert_manager(ctx: MachineContext[TerraformOptions]) -> bool:
    """Return True if cert-manager is required for TLS."""
    k8s = ctx.config.k8s
    email = ctx.config.letsencrypt.effective_email
    return k8s.is_public and not k8s.no_tls and bool(email)


def _required_addons(needs_cert_manager: bool) -> list[Addon]:
    """Get the list of addons required by the deployment."""
    addons = list(REQUIRED_ADDONS)
    if needs_cert_manager:
        addons.append(Addon.CERT_MANAGER)
    return addons


class K8sAddonsEnabled(MachineStateABC):
    """Kubernetes cluster addons are enabled.

    Check:
        True if all required addons are enabled.

    Satisfy:
        Enable only the missing addons via provider.enable_addons().
        Addons are abstract requirements; providers map to concrete names.
    """

    def _missing_addons(self, ctx: MachineContext[TerraformOptions]) -> list[Addon]:
        """Get list of addons that need to be enabled."""
        provider = get_cluster_provider_from_context(ctx)
        k8s = ctx.config.k8s
        cluster_name = k8s.effective_cluster_name
        required = _required_addons(_needs_cert_manager(ctx))
        enabled = provider.get_enabled_addons(cluster_name)
        return [addon for addon in required if addon not in enabled]

    def describe(self, ctx: MachineContext[TerraformOptions]) -> str:
        addons = _required_addons(_needs_cert_manager(ctx))
        return f"K8s addons: {', '.join(a.value for a in addons)}"

    def check(self, ctx: MachineContext[TerraformOptions]) -> bool:
        return not self._missing_addons(ctx)

    @task
    def satisfy(self, ctx: MachineContext[TerraformOptions]) -> None:
        provider = get_cluster_provider_from_context(ctx)
        k8s = ctx.config.k8s
        cluster_name = k8s.effective_cluster_name
        required = _required_addons(_needs_cert_manager(ctx))
        missing = self._missing_addons(ctx)

        if not missing:
            logger.done(f"All addons already enabled: {', '.join(a.value for a in required)}")
            return

        # Enable addons one at a time for incremental progress
        for addon in missing:
            logger.next(f"Enabling addon: {addon.value}")
            provider.enable_addons(cluster_name, [addon])
            logger.done(f"Addon enabled: {addon.value}")


# =============================================================================
# CloudNativePGInstalled
# =============================================================================


class CloudNativePGInstalled(MachineStateABC):
    """CloudNativePG PostgreSQL operator is installed.

    Skip:
        If config.k8s.no_cloudnativepg is True.

    Check:
        True if cnpg-controller-manager deployment exists.

    Satisfy:
        Apply CloudNativePG operator manifest and wait for ready.
    """

    def describe(self, ctx: MachineContext[TerraformOptions]) -> str:
        return "CloudNativePG operator"

    def skip(self, ctx: MachineContext[TerraformOptions]) -> bool:
        """Skip if user requested no CloudNativePG."""
        return ctx.config.k8s.no_cloudnativepg

    def check(self, ctx: MachineContext[TerraformOptions]) -> bool:
        provider = get_cluster_provider_from_context(ctx)
        cluster_name = ctx.config.k8s.effective_cluster_name

        try:
            returncode, stdout, _ = provider.kubectl(
                cluster_name,
                "get",
                "deployment",
                "-n",
                "cnpg-system",
                "cnpg-controller-manager",
            )
            return returncode == 0 and "cnpg-controller-manager" in stdout
        except ClusterError:
            return False

    @task
    def satisfy(self, ctx: MachineContext[TerraformOptions]) -> None:
        provider = get_cluster_provider_from_context(ctx)
        k8s = ctx.config.k8s
        cluster_name = k8s.effective_cluster_name

        logger.next("Installing CloudNativePG operator")

        # Apply the CloudNativePG operator manifest
        returncode, _, stderr = provider.kubectl(
            cluster_name,
            "apply",
            "-f",
            k8s.cnpg_manifest_url,
        )
        if returncode != 0:
            raise RuntimeError(f"Failed to install CloudNativePG: {stderr}")

        # Wait for the operator to be ready
        logger.info("Waiting for CloudNativePG operator to be ready...")
        returncode, _, stderr = provider.kubectl(
            cluster_name,
            "wait",
            "--for=condition=available",
            f"--timeout={k8s.kubectl_wait_timeout_s}s",
            "deployment/cnpg-controller-manager",
            "-n",
            "cnpg-system",
        )
        if returncode != 0:
            logger.warning(f"CloudNativePG operator may not be fully ready: {stderr}")

        logger.done("CloudNativePG installed")


# =============================================================================
# LetsEncryptIssuerConfigured
# =============================================================================


class LetsEncryptIssuerConfigured(MachineStateABC):
    """Let's Encrypt ClusterIssuer is configured.

    Skip:
        If no host (local mode), no_tls flag, or no email provided.

    Check:
        True if letsencrypt-prod ClusterIssuer exists.

    Satisfy:
        Create ClusterIssuer manifest with ACME configuration.
    """

    def describe(self, ctx: MachineContext[TerraformOptions]) -> str:
        return "Let's Encrypt ClusterIssuer"

    def skip(self, ctx: MachineContext[TerraformOptions]) -> bool:
        """Skip if not public (local mode), no_tls flag, or no email."""
        k8s = ctx.config.k8s
        email = ctx.config.letsencrypt.effective_email
        return not k8s.is_public or k8s.no_tls or not email

    def check(self, ctx: MachineContext[TerraformOptions]) -> bool:
        k8s = ctx.config.k8s
        provider = get_cluster_provider_from_context(ctx)
        cluster_name = k8s.effective_cluster_name

        try:
            returncode, stdout, _ = provider.kubectl(
                cluster_name, "get", "clusterissuer", "letsencrypt-prod"
            )
            return returncode == 0 and "letsencrypt-prod" in stdout
        except ClusterError:
            return False

    @task
    def satisfy(self, ctx: MachineContext[TerraformOptions]) -> None:
        provider = get_cluster_provider_from_context(ctx)
        cluster_name = ctx.config.k8s.effective_cluster_name

        logger.next("Creating Let's Encrypt ClusterIssuer")

        manifest = render_template("clusterissuer-letsencrypt.yaml", ctx.config)
        try:
            provider.apply_manifests(cluster_name, {"clusterissuer.yaml": manifest})
        except ClusterError as e:
            raise RuntimeError(f"Failed to create ClusterIssuer: {e}")

        logger.done("ClusterIssuer created")


# =============================================================================
# K8sInfrastructureReady (Composite)
# =============================================================================


class K8sInfrastructureReady(MachineStateABC):
    """K8s infrastructure is fully provisioned.

    Composite state that ensures:
    1. VPS is materialized (Hetzner only, skipped otherwise)
    2. K8s cluster exists and is running
    3. Required addons are enabled
    4. CloudNativePG operator is installed (unless no_cloudnativepg)
    5. Let's Encrypt ClusterIssuer is configured (when host set, unless no_tls)

    Substates implement skip() to be conditionally skipped:
    - HetznerVPSMaterialized: skip when config.k8s.provider != "hetzner"
    - CloudNativePGInstalled: skip when config.k8s.no_cloudnativepg
    - LetsEncryptIssuerConfigured: skip when no host/no_tls/no email

    The metaclass auto-generates describe(), check(), and satisfy() from
    class attributes. Dependencies are implicit from declaration order.
    """

    # VPS provisioning (skips when not using Hetzner)
    vps_materialized = HetznerVPSMaterialized()

    # K8s cluster management
    cluster_created = K8sClusterCreated()
    cluster_running = K8sClusterRunning()
    addons_enabled = K8sAddonsEnabled()

    # Operators and services
    cloudnativepg_installed = CloudNativePGInstalled()
    letsencrypt_issuer = LetsEncryptIssuerConfigured()
