"""
djb deploy k8s materialize - Cloud VPS provisioning command.

Creates cloud VPS instances for Kubernetes deployments. This command handles
the physical/virtual machine creation step, storing server info in project
config for subsequent terraform and deploy commands.

Supported Providers
-------------------
- hetzner: Hetzner Cloud (requires API token in secrets)

Usage Examples
--------------
# Create Hetzner VPS for staging
djb -m staging deploy k8s materialize --provider hetzner --ssh-key-name my-key

# Force create new server (errors if already configured)
djb -m staging deploy k8s materialize --provider hetzner --create

Design Philosophy
-----------------
"Materialize" means to make physical/real - bringing a virtual machine into
existence. This is distinct from "terraform" which shapes/provisions the
machine with K8s infrastructure.

The command is idempotent: if a server is already configured and exists,
it verifies the server and returns. Use --create to force new server creation.

Implementation
--------------
Uses HetznerVPSMaterialized composite MachineState:
- HetznerSSHKeyResolved: Resolve SSH key (interactive if multiple)
- HetznerServerNameSet: Generate server name
- HetznerServerExists: Create server via API
- HetznerServerRunning: Wait for server to be ready
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import click

from djb.cli.context import CliK8sContext, djb_pass_context
from djb.config import HetznerConfig
from djb.config.config import DjbConfig
from djb.core.logging import get_logger
from djb.machine_state import MachineContext
from djb.machine_state.materialize import HetznerVPSMaterialized
from djb.machine_state.materialize.hetzner.states import HetznerMaterializeOptions
from djb.secrets import SecretsManager

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


def is_server_materialized(config: DjbConfig, provider: str) -> bool:
    """Check if a cloud server is configured for the current mode.

    Args:
        config: DjbConfig with current mode
        provider: Cloud provider name (e.g., "hetzner")

    Returns:
        True if server is configured (has IP and name)
    """
    if provider == "hetzner":
        return bool(config.k8s.host and config.hetzner.server_name)
    return False


@click.command("materialize")
@click.option(
    "--provider",
    type=click.Choice(["hetzner"]),
    required=True,
    help="Cloud provider for VPS provisioning.",
)
@click.option(
    "--create",
    "force_create",
    is_flag=True,
    help="Force new server creation (logs restore commands).",
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
@djb_pass_context(CliK8sContext)
@click.pass_context
def materialize(
    ctx: click.Context,
    cli_ctx: CliK8sContext,
    provider: str,
    force_create: bool,
    server_type: str | None,
    location: str | None,
    image: str | None,
    ssh_key_name: str | None,
) -> None:
    """Create cloud VPS for K8s deployment.

    Creates a server using the specified cloud provider and stores
    the server info in project config for the current mode.

    This command is typically invoked automatically by `terraform` when
    no server is configured, but can be run directly for explicit control.

    \\b
    Hetzner Cloud mode:
      djb -m staging deploy k8s materialize --provider hetzner \\
          --server-type cx22 --location nbg1 --ssh-key-name my-key

    \\b
    The command stores server info in project config [hetzner] section:
      server_name = "myproject-staging"
      server_ip = "116.203.x.x"

    \\b
    Subsequent commands use this config automatically:
      djb -m staging deploy k8s terraform  # Uses stored server
      djb -m staging deploy k8s            # Deploys to stored server
    """
    if cli_ctx.config is None:
        raise click.ClickException("Config not available. Run from a djb project directory.")

    if provider == "hetzner":
        _materialize_hetzner(
            cli_ctx=cli_ctx,
            force_create=force_create,
            server_type=server_type,
            location=location,
            image=image,
            ssh_key_name=ssh_key_name,
        )
    else:
        raise click.ClickException(f"Unknown provider: {provider}")


def _materialize_hetzner(
    cli_ctx: CliK8sContext,
    force_create: bool,
    server_type: str | None,
    location: str | None,
    image: str | None,
    ssh_key_name: str | None,
) -> None:
    """Create or retrieve Hetzner VPS using MachineState pattern.

    Args:
        cli_ctx: CLI context with runner and config
        force_create: If True, force creation of new server
        server_type: Override server type (None = use config default)
        location: Override location (None = use config default)
        image: Override image (None = use config default)
        ssh_key_name: Override SSH key name (None = auto-detect)
    """
    # Create override config - None values fall through to base config
    override_config = DjbConfig(
        hetzner=HetznerConfig(
            server_type=server_type,
            location=location,
            image=image,
            ssh_key_name=ssh_key_name,
        )
    )

    # Merge parent config with subcommand overrides
    config = cli_ctx.config.augment(override_config)

    # Create MachineContext with typed options
    secrets_manager = SecretsManager(cli_ctx.runner, config.project_dir)
    options = HetznerMaterializeOptions(force_create=force_create)
    machine_ctx = MachineContext(
        config=config,
        runner=cli_ctx.runner,
        logger=logger,
        secrets=secrets_manager,
        options=options,
    )

    # Run MachineState DAG
    state = HetznerVPSMaterialized()
    result = state.satisfy(machine_ctx).run()

    if not result.success:
        raise click.ClickException(result.message)

    # Success message
    logger.note()
    logger.done(f"Server materialized: {config.hetzner.server_name} ({config.k8s.host})")
    logger.note()
    logger.info("Next steps:")
    logger.info(f"  Provision infrastructure: djb -m {config.mode.value} deploy k8s terraform")
