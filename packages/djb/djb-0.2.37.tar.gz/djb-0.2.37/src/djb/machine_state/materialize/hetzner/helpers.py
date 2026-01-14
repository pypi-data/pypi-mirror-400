"""Shared helpers for Hetzner MachineStates.

Internal utilities for Hetzner VPS provisioning states.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from djb.core.exceptions import ImproperlyConfigured
from djb.k8s.cloud import HetznerCloudProvider

if TYPE_CHECKING:
    from djb.config import DjbConfig
    from djb.machine_state import MachineContext

__all__ = [
    "create_hetzner_provider",
    "generate_server_name",
]


def create_hetzner_provider(ctx: MachineContext) -> HetznerCloudProvider:
    """Construct HetznerCloudProvider from secrets.

    Args:
        ctx: MachineContext with secrets manager.

    Returns:
        HetznerCloudProvider instance.

    Raises:
        ImproperlyConfigured: If API token not found in secrets.
    """
    if ctx.secrets is None:
        raise ImproperlyConfigured("SecretsManager required for Hetzner provisioning")

    secrets = ctx.secrets.load_secrets(ctx.config.mode)
    if not secrets:
        raise ImproperlyConfigured(
            f"No secrets found for mode '{ctx.config.mode}'.\n"
            f"Add Hetzner API token to secrets/{ctx.config.mode}.yaml:\n"
            f"  hetzner:\n"
            f"    api_token: hc_xxx..."
        )

    # Try nested structure or flat key
    hetzner_section = secrets.get("hetzner", {})
    if isinstance(hetzner_section, dict):
        api_token = hetzner_section.get("api_token")
    else:
        api_token = None

    if not api_token:
        api_token = secrets.get("hetzner_api_token")

    if not api_token:
        raise ImproperlyConfigured(
            f"Hetzner API token not found in secrets/{ctx.config.mode}.yaml.\n"
            f"Add it as:\n"
            f"  hetzner:\n"
            f"    api_token: hc_xxx..."
        )

    return HetznerCloudProvider(api_token)


def generate_server_name(config: DjbConfig) -> str:
    """Generate server name from project name and mode.

    Returns:
        Server name like "myproject-staging" or "myproject" (for production)
    """
    base_name = config.project_name
    if config.mode.value == "production":
        return base_name
    return f"{base_name}-{config.mode.value}"
