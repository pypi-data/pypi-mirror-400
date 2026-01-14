"""SSH key resolution utilities.

Provider-agnostic SSH key resolution. Works with any cloud provider
that implements get_ssh_keys_with_details().
"""

from __future__ import annotations

from typing import Protocol

from djb.core.exceptions import ImproperlyConfigured
from djb.core.logging import get_logger


class SSHKeyProvider(Protocol):
    """Protocol for SSH key providers."""

    def get_ssh_keys_with_details(self) -> list[tuple[str, str | None]]:
        """Return list of (key_name, public_key) tuples. Public key may be None."""
        ...


class NoSSHKeysFound(ImproperlyConfigured):
    """No SSH keys found in cloud provider."""

    pass


class MultipleSSHKeysFound(ImproperlyConfigured):
    """Multiple SSH keys found and no auto-selection possible.

    Attributes:
        key_names: List of available SSH key names.
    """

    def __init__(self, key_names: list[str]) -> None:
        self.key_names = key_names
        keys_list = ", ".join(key_names)
        super().__init__(
            f"Multiple SSH keys found: {keys_list}. "
            f"Use --ssh-key-name to specify which key to use, "
            f"or use --yes to auto-select the first key."
        )


def extract_email_from_public_key(public_key: str | None) -> str | None:
    """Extract email from SSH public key comment.

    SSH public keys typically end with a comment that may contain an email:
    "ssh-ed25519 AAAA... user@example.com"
    """
    if not public_key:
        return None

    parts = public_key.strip().split()
    if len(parts) >= 3:
        comment = parts[-1]
        if "@" in comment and "." in comment.split("@")[-1]:
            return comment.lower()
    return None


def resolve_ssh_key_name(
    provider: SSHKeyProvider,
    config_email: str | None = None,
    auto_select: bool = False,
) -> str:
    """Resolve SSH key name, auto-selecting if possible.

    Resolution order:
    1. Single key available -> auto-select
    2. Match key by config email -> auto-select with note
    3. auto_select=True -> select first key
    4. Multiple keys -> raise MultipleSSHKeysFound

    Args:
        provider: Any provider implementing SSHKeyProvider protocol
        config_email: Email from djb config to match against SSH key comments
        auto_select: If True, auto-select the first key when multiple exist

    Returns:
        SSH key name to use

    Raises:
        NoSSHKeysFound: If no SSH keys available in cloud provider.
        MultipleSSHKeysFound: If multiple keys exist and no auto-selection possible.
    """
    logger = get_logger(__name__)

    keys_with_details = provider.get_ssh_keys_with_details()

    if not keys_with_details:
        raise NoSSHKeysFound(
            "No SSH keys found in cloud provider. " "Add an SSH key to your cloud provider account."
        )

    all_key_names = [name for name, _ in keys_with_details]

    # Single key - auto-select
    if len(keys_with_details) == 1:
        key_name = keys_with_details[0][0]
        logger.info(f"Using SSH key: {key_name}")
        return key_name

    # Try to match by email from config
    if config_email:
        config_email_lower = config_email.lower()
        for key_name, public_key in keys_with_details:
            # Check if key name itself matches the email
            if key_name.lower() == config_email_lower:
                logger.note(f"Auto-selected SSH key '{key_name}' (matches config email)")
                return key_name
            # Check if email in public key comment matches
            key_email = extract_email_from_public_key(public_key)
            if key_email and key_email == config_email_lower:
                logger.note(
                    f"Auto-selected SSH key '{key_name}' (matches config email: {config_email})"
                )
                return key_name

    # auto_select flag - select first key
    if auto_select:
        key_name = all_key_names[0]
        logger.info(f"Using SSH key: {key_name}")
        return key_name

    # Multiple keys and no auto-selection possible
    raise MultipleSSHKeysFound(all_key_names)
