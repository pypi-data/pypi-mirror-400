"""
djb deploy k8s terraform - Infrastructure provisioning command.

Provisions Kubernetes infrastructure using the ClusterProvider abstraction.
Supports local (k3d/microk8s), remote (SSH-based), and cloud (Hetzner) clusters.

This is a declarative, idempotent command - each execution checks the
health of all infrastructure components and only provisions/fixes what's
missing or unhealthy.

Local Mode (no --host):
-----------------------
$ djb deploy k8s terraform                    # k3d (default)
$ djb deploy k8s terraform --microk8s         # local microk8s

Remote Mode (SSH-based, microk8s):
----------------------------------
$ djb deploy k8s terraform --host 192.168.1.100 --microk8s
$ djb deploy k8s terraform --host server.example.com --port 2222 --microk8s

Hetzner Cloud Mode:
-------------------
$ djb -m staging deploy k8s terraform --provider hetzner \\
    --server-type cx23 --location nbg1 --ssh-key-name my-key

Checking microk8s...           ✓ installed and running
Checking dns addon...          ✓ enabled
Checking storage addon...      ✓ enabled
Checking registry addon...     ✗ not enabled -> enabling...
Checking ingress addon...      ✓ enabled
Checking cert-manager addon... ✓ enabled
Checking CloudNativePG...      ✓ installed
Checking ClusterIssuer...      ✓ configured

Infrastructure ready.

Implementation
--------------
Uses K8sInfrastructureReady composite MachineState:
- HetznerVPSMaterialized: Create VPS (skipped if not Hetzner provider)
- K8sClusterCreated: Create K8s cluster
- K8sClusterRunning: Start K8s cluster
- K8sAddonsEnabled: Enable required addons
- CloudNativePGInstalled: Install PostgreSQL operator
- LetsEncryptIssuerConfigured: Configure TLS (skipped if no host or no_tls)
"""

from __future__ import annotations

from pathlib import Path

import click

from djb.cli.context import CliContext, djb_pass_context, is_invoked_standalone
from djb.cli.k8s.k8s import CliK8sContext
from djb.config import DjbConfig, HetznerConfig, K8sConfig, LetsEncryptConfig
from djb.core.logging import get_logger
from djb.machine_state import MachineContext
from djb.machine_state.terraform import K8sInfrastructureReady
from djb.machine_state.terraform.states import TerraformOptions
from djb.secrets import SecretsManager
from djb.types import K8sClusterType, K8sProvider

logger = get_logger(__name__)


def _get_project_name_from_context(ctx: click.Context) -> str:
    """Get project name from Click context if available."""
    cli_ctx = ctx.find_object(CliContext)
    if cli_ctx is not None and cli_ctx.config is not None:
        return cli_ctx.config.project_name
    return "djb-project"


@click.command("terraform")
@click.option(
    "--microk8s",
    "use_microk8s",
    is_flag=True,
    help="Use microk8s instead of k3d.",
)
@click.option(
    "--host",
    default=None,
    help="SSH host IP/hostname for remote provisioning. If not set, runs locally.",
)
@click.option(
    "--port",
    default=None,
    type=int,
    help="SSH port (default: 22).",
)
@click.option(
    "--ssh-key",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to SSH private key.",
)
@click.option(
    "--provider",
    type=click.Choice(["manual", "hetzner"]),
    default=None,
    help="Cloud provider for VPS provisioning (overrides config).",
)
@click.option(
    "--create",
    "force_create",
    is_flag=True,
    help="Force new server creation (Hetzner only).",
)
@click.option(
    "--server-type",
    default=None,
    help="Server type for cloud provisioning (default from config: hetzner.default_server_type).",
)
@click.option(
    "--location",
    default=None,
    help="Datacenter location for cloud provisioning (default from config: hetzner.default_location).",
)
@click.option(
    "--image",
    default=None,
    help="OS image for cloud provisioning (default from config: hetzner.default_image).",
)
@click.option(
    "--ssh-key-name",
    default=None,
    help="SSH key name registered with cloud provider.",
)
@click.option(
    "--domain",
    default=None,
    help="Domain for Let's Encrypt TLS certificates.",
)
@click.option(
    "--email",
    default=None,
    help="Email for Let's Encrypt (required for TLS when host is set).",
)
@click.option(
    "--no-cloudnativepg",
    is_flag=True,
    help="Skip CloudNativePG operator installation.",
)
@click.option(
    "--no-tls",
    is_flag=True,
    help="Skip Let's Encrypt ClusterIssuer setup.",
)
@djb_pass_context(CliK8sContext)
@click.pass_context
def terraform(
    ctx: click.Context,
    cli_ctx: CliK8sContext,
    use_microk8s: bool,
    host: str | None,
    port: int | None,
    ssh_key: Path | None,
    provider: str | None,  # CLI option for cloud provider name
    force_create: bool,
    server_type: str | None,
    location: str | None,
    image: str | None,
    ssh_key_name: str | None,
    domain: str | None,
    email: str | None,
    no_cloudnativepg: bool,
    no_tls: bool,
) -> None:
    """Provision Kubernetes infrastructure.

    Supports local clusters (for development), remote clusters (via SSH),
    and cloud-provisioned clusters (Hetzner). Uses the ClusterProvider
    abstraction to encapsulate differences between k3d and microk8s.

    This command is idempotent - each execution checks the health of all
    infrastructure components and only provisions/fixes what's missing.

    \b
    Local mode (no --host, default k3d):
      djb deploy k8s terraform              # k3d (fast, ~30s)
      djb deploy k8s terraform --microk8s   # microk8s

    \b
    Remote mode (--host, requires --microk8s):
      djb deploy k8s terraform --host 192.168.1.100 --microk8s
      djb deploy k8s terraform --host server --port 2222 --microk8s --email admin@example.com

    \b
    Hetzner Cloud mode (creates VPS + provisions):
      djb -m staging deploy k8s terraform --provider hetzner \\
          --server-type cx23 --location nbg1 --ssh-key-name my-key

    \b
    Infrastructure provisioned:
    * K8s cluster (k3d or microk8s)
    * Addons: dns, storage, registry, ingress
    * CloudNativePG operator (PostgreSQL)
    * Let's Encrypt ClusterIssuer (when host is set, for TLS)
    """
    config = cli_ctx.config
    cmd_runner = cli_ctx.runner
    project_name = config.project_name

    # Always set cluster_name (derived if not in config)
    derived_name = config.k8s.cluster_name or f"djb-{project_name}"
    config = config.augment(DjbConfig(k8s=K8sConfig(cluster_name=derived_name)))

    # K8s overrides from CLI flags
    if provider:
        parsed = K8sProvider.parse(provider)
        if parsed:
            config = config.augment(DjbConfig(k8s=K8sConfig(provider=parsed)))
    if use_microk8s:
        config = config.augment(DjbConfig(k8s=K8sConfig(cluster_type=K8sClusterType.MICROK8S)))
    if host:
        config = config.augment(DjbConfig(k8s=K8sConfig(host=host)))
    if port:
        config = config.augment(DjbConfig(k8s=K8sConfig(port=port)))
    if ssh_key:
        config = config.augment(DjbConfig(k8s=K8sConfig(ssh_key=ssh_key)))
    if no_cloudnativepg:
        config = config.augment(DjbConfig(k8s=K8sConfig(no_cloudnativepg=True)))
    if no_tls:
        config = config.augment(DjbConfig(k8s=K8sConfig(no_tls=True)))

    # Hetzner overrides
    config = config.augment(
        DjbConfig(
            hetzner=HetznerConfig(
                server_type=server_type,
                location=location,
                image=image,
                ssh_key_name=ssh_key_name,
            )
        )
    )

    # LetsEncrypt override
    if email:
        config = config.augment(DjbConfig(letsencrypt=LetsEncryptConfig(email=email)))

    # Validate after augment (all values now come from config)
    is_hetzner = config.k8s.provider == K8sProvider.HETZNER

    # Validate: Hetzner mode doesn't take --host (it sets k8s.host after materialization)
    if is_hetzner and host is not None:
        raise click.ClickException(
            "Cannot use --host with --provider hetzner. "
            "Hetzner mode provisions and connects to the VPS automatically."
        )

    # Remote mode (host set or Hetzner) requires email for TLS
    will_have_host = host is not None or is_hetzner
    if will_have_host and not config.k8s.no_tls and not config.letsencrypt.effective_email:
        raise click.ClickException(
            "Email is required for Let's Encrypt TLS.\n"
            "Use --email, set email or letsencrypt.email in config, or --no-tls to skip."
        )

    # Create thin options (only force_create)
    options = TerraformOptions(force_create=force_create)

    # Log what we're doing
    cluster_type_str = config.k8s.cluster_type.value
    if is_hetzner:
        logger.info(f"Provisioning Hetzner {cluster_type_str} cluster: {config.k8s.cluster_name}")
    elif config.k8s.host:
        logger.info(f"Provisioning {cluster_type_str} on {config.k8s.host}:{config.k8s.port}")
    else:
        logger.info(f"Provisioning local {cluster_type_str} cluster: {config.k8s.cluster_name}")

    # Create MachineContext
    secrets_manager = SecretsManager(cmd_runner, config.project_dir)
    machine_ctx = MachineContext(
        config=config,
        runner=cmd_runner,
        logger=logger,
        secrets=secrets_manager,
        options=options,
    )

    # Run infrastructure provisioning
    result = K8sInfrastructureReady().satisfy(machine_ctx).run()

    if not result.success:
        raise click.ClickException(result.message)

    # Success message
    logger.note()
    logger.done("Infrastructure ready!")

    # Only show next steps when invoked standalone (not as part of deploy flow)
    if is_invoked_standalone(ctx):
        logger.note()
        logger.info("Next steps:")
        if config.k8s.host:
            effective_host = config.k8s.host
            logger.info(
                f"  Deploy app: djb deploy k8s --host {effective_host}"
                + (f" --port {config.k8s.port}" if config.k8s.port != 22 else "")
            )
        else:
            logger.info("  Start dev loop: djb deploy k8s local dev")
