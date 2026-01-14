"""Hetzner VPS machine states - VPS provisioning.

States are ordered as they appear in the HetznerVPSMaterialized composite:
1. HetznerSSHKeyResolved - SSH key is resolved
2. HetznerServerNameSet - Server name is generated
3. HetznerServerExists - Server exists in Hetzner Cloud
4. HetznerServerRunning - Server is in 'running' status
5. HetznerVPSMaterialized - Composite state
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import TYPE_CHECKING

from djb.core.logging import get_logger
from djb.machine_state import (
    ForceCreateOptions,
    MachineContext,
    MachineStateABC,
    task,
)
from djb.machine_state.materialize.ssh_key import resolve_ssh_key_name
from djb.types import K8sProvider

from .helpers import create_hetzner_provider, generate_server_name

if TYPE_CHECKING:
    pass


@dataclass
class HetznerMaterializeOptions(ForceCreateOptions):
    """CLI options for the Hetzner materialize command.

    Inherited from ForceCreateOptions:
        force_create: Force creation of a new server even if one exists.
            Appends timestamp to server name to avoid conflicts.

    Inherited from BaseOptions:
        search_strategy: Strategy for finding first unsatisfied task.
    """

    pass


# =============================================================================
# HetznerSSHKeyResolved
# =============================================================================


class HetznerSSHKeyResolved(MachineStateABC):
    """SSH key is resolved and saved to config.

    Check:
        True if hetzner.ssh_key_name is set in config.

    Satisfy:
        Resolve SSH key via Hetzner API:
        - Single key: auto-select
        - Multiple keys: match by config email or prompt interactively
        Saves resolved key to config.
    """

    def describe(self, ctx: MachineContext) -> str:
        return "Hetzner SSH key"

    def check(self, ctx: MachineContext) -> bool:
        # Already resolved if set in config
        return ctx.config.hetzner.ssh_key_name is not None

    @task
    def satisfy(self, ctx: MachineContext) -> None:
        provider = create_hetzner_provider(ctx)
        resolved = resolve_ssh_key_name(
            provider,
            config_email=ctx.config.email,
            auto_select=ctx.config.yes,
        )
        ctx.config.set("hetzner.ssh_key_name", resolved)


# =============================================================================
# HetznerServerNameSet
# =============================================================================


class HetznerServerNameSet(MachineStateABC):
    """Server name is set in config.

    Check:
        True if hetzner.server_name is set in config (unless force_create).

    Satisfy:
        Generate server name from project name and mode.
        If force_create and server already exists in Hetzner, appends timestamp
        for uniqueness.
        Saves name to config.
    """

    def describe(self, ctx: MachineContext[HetznerMaterializeOptions]) -> str:
        return "Hetzner server name"

    def check(self, ctx: MachineContext[HetznerMaterializeOptions]) -> bool:
        force_create = ctx.options.force_create if ctx.options else False
        if force_create:
            # Always need a new name if force_create
            return False
        return ctx.config.hetzner.server_name is not None

    @task
    def satisfy(self, ctx: MachineContext[HetznerMaterializeOptions]) -> None:
        force_create = ctx.options.force_create if ctx.options else False
        server_name = generate_server_name(ctx.config)

        if force_create:
            # Check if server already exists in Hetzner
            provider = create_hetzner_provider(ctx)
            if provider.get_server(server_name):
                # Generate unique name with timestamp
                server_name = f"{server_name}-{int(time.time())}"

        ctx.config.set("hetzner.server_name", server_name)


# =============================================================================
# HetznerServerExists
# =============================================================================


class HetznerServerExists(MachineStateABC):
    """Server exists in Hetzner Cloud with IP saved to config.

    Check:
        True if server exists in Hetzner Cloud and IP is in k8s.host.

    Satisfy:
        Create server via Hetzner API with configured settings.
        Saves server IP to k8s.host, and server_type/location/image to hetzner config.
    """

    def describe(self, ctx: MachineContext) -> str:
        name = ctx.config.hetzner.server_name
        return f"Hetzner server '{name}'" if name else "Hetzner server"

    def check(self, ctx: MachineContext) -> bool:
        # server_name guaranteed by HetznerServerNameSet running first
        name = ctx.config.hetzner.server_name
        assert name is not None, "hetzner.server_name must be set by HetznerServerNameSet"
        provider = create_hetzner_provider(ctx)
        server = provider.get_server(name)
        if server and server.ip:
            # Ensure IP is in config (idempotent)
            if ctx.config.k8s.host != server.ip:
                ctx.config.set("k8s.host", server.ip)
            return True
        return False

    @task
    def satisfy(self, ctx: MachineContext) -> None:
        logger = get_logger(__name__)

        server_type = ctx.config.hetzner.effective_server_type
        location = ctx.config.hetzner.effective_location
        image = ctx.config.hetzner.effective_image
        server_name = ctx.config.hetzner.server_name
        ssh_key_name = ctx.config.hetzner.ssh_key_name

        # These should be set by prior machine states
        assert server_name is not None, "hetzner.server_name must be set by HetznerServerNameSet"
        assert ssh_key_name is not None, "hetzner.ssh_key_name must be set by HetznerSSHKeyResolved"

        provider = create_hetzner_provider(ctx)

        # Log server creation details
        logger.next(f"Creating Hetzner server: {server_name}")
        logger.info(f"  Type: {server_type}")
        logger.info(f"  Location: {location}")
        logger.info(f"  Image: {image}")
        logger.info(f"  SSH Key: {ssh_key_name}")

        server = provider.create_server(
            name=server_name,
            server_type=server_type,
            location=location,
            image=image,
            ssh_key_name=ssh_key_name,
        )
        logger.done(f"Server created: {server.name} (ID: {server.id})")

        # Save IP to k8s.host (unified SSH settings)
        ctx.config.set("k8s.host", server.ip)

        # Save instance state to hetzner config
        ctx.config.set("hetzner.server_type", server_type)
        ctx.config.set("hetzner.location", location)
        ctx.config.set("hetzner.image", image)


# =============================================================================
# HetznerServerRunning
# =============================================================================


class HetznerServerRunning(MachineStateABC):
    """Server is in 'running' status.

    Check:
        True if server exists and status is 'running'.

    Satisfy:
        Wait for server to become ready (up to 5 minutes).
    """

    def describe(self, ctx: MachineContext) -> str:
        name = ctx.config.hetzner.server_name
        return f"Hetzner server '{name}' running" if name else "Hetzner server running"

    def check(self, ctx: MachineContext) -> bool:
        # server_name guaranteed by HetznerServerNameSet running first
        name = ctx.config.hetzner.server_name
        assert name is not None, "hetzner.server_name must be set by HetznerServerNameSet"
        provider = create_hetzner_provider(ctx)
        server = provider.get_server(name)
        return server is not None and server.status == "running"

    @task
    def satisfy(self, ctx: MachineContext) -> None:
        logger = get_logger(__name__)

        provider = create_hetzner_provider(ctx)
        server_name = ctx.config.hetzner.server_name

        # Should be set by prior machine states
        assert server_name is not None, "server_name must be set by HetznerServerNameSet"

        logger.next("Waiting for server to be ready")
        # HetznerError propagates with appropriate message if server doesn't become ready
        server = provider.wait_for_server(server_name, timeout=300)
        logger.done(f"Server ready: {server.ip}")


# =============================================================================
# HetznerVPSMaterialized (Composite)
# =============================================================================


class HetznerVPSMaterialized(MachineStateABC):
    """Hetzner VPS exists and is running.

    Composite state that ensures:
    1. SSH key is resolved (interactive if multiple)
    2. Server name is set (generated if needed)
    3. Server exists in Hetzner Cloud
    4. Server is in 'running' status

    Dependencies are implicit from declaration order.

    Skipped if config.k8s.provider != K8sProvider.HETZNER, allowing this
    state to be embedded in other composites without running when not applicable.
    """

    ssh_key_resolved = HetznerSSHKeyResolved()
    server_name_set = HetznerServerNameSet()
    server_exists = HetznerServerExists()
    server_running = HetznerServerRunning()

    def skip(self, ctx: MachineContext) -> bool:
        """Skip if not using Hetzner provider."""
        return ctx.config.k8s.provider != K8sProvider.HETZNER
