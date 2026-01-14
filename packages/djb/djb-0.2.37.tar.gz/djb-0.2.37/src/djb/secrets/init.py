"""
djb secrets initialization - Initialize secrets for environments.

Provides functions for creating and upgrading encrypted secrets files
for different deployment environments using SOPS.

There are two types of secrets:
- User secrets (development.yaml): Encrypted with user's own age key, gitignored
- Project secrets (staging.yaml, production.yaml): Multi-recipient encryption, committed

This separation allows new users to get started immediately without waiting
for a teammate to rotate project secrets.
"""

from __future__ import annotations

import secrets as py_secrets
import string
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import yaml

from djb.config import DjbConfig
from djb.core.logging import get_logger
from djb.types import Mode

if TYPE_CHECKING:
    from djb.cli.context import CliContext

from djb.secrets.core import (
    SecretsManager,
    SopsError,
    check_age_installed,
    check_sops_installed,
    format_identity,
    generate_age_key,
    get_default_key_path,
    get_encrypted_key_path,
    get_public_key_from_private,
    is_sops_encrypted,
    rotate_keys,
)
from djb.secrets.gpg import GpgError, check_gpg_installed
from djb.secrets.protected import (
    ProtectedFileError,
    protect_age_key,
    protected_age_key,
)

logger = get_logger(__name__)


def _get_encrypted_recipients(secrets_file: Path) -> set[str]:
    """Get the list of recipients from a SOPS-encrypted file's metadata.

    SOPS stores recipient info in the 'sops.age' section of encrypted files.

    Returns:
        Set of public key strings the file is encrypted for, or empty set if
        the file doesn't exist or can't be parsed.
    """
    if not secrets_file.exists():
        return set()

    try:
        with open(secrets_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "sops" not in data or "age" not in data["sops"]:
            return set()

        return {entry["recipient"] for entry in data["sops"]["age"]}
    except (OSError, yaml.YAMLError, KeyError, TypeError):
        # File read error, invalid YAML, or unexpected structure
        return set()


class SecretsStatus(NamedTuple):
    """Status of secrets initialization for an environment."""

    initialized: list[str]  # Newly created
    upgraded: list[str]  # Existing but upgraded with new keys
    up_to_date: list[str]  # Already up to date


class MergeResult(NamedTuple):
    """Result of _deep_merge_missing() - merged dict and list of added keys."""

    result: dict
    added_keys: list[str]


def _generate_secret_key(length: int = 50) -> str:
    """Generate a random secret key suitable for Django's SECRET_KEY."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(py_secrets.choice(chars) for _ in range(length))


def _get_template(mode: Mode, *, project_name: str | None = None) -> dict:
    """Get the secrets template for a mode.

    Template structure varies by mode:
    - Production: django_secret_key, superuser (no db_credentials since
      Heroku provides DATABASE_URL)
    - Dev/Staging: django_secret_key, db_credentials, superuser (for local
      database setup)

    For dev mode, values are auto-generated with sensible defaults.
    For public modes (staging/production), placeholders indicate values
    that need to be configured by the team.
    """
    # Dev gets sensible auto-generated defaults (local only - gitignored)
    if mode == Mode.DEVELOPMENT:
        db_name = project_name or "app"
        return {
            "django_secret_key": _generate_secret_key(),
            "db_credentials": {
                "username": db_name,
                "password": _generate_secret_key(20),
                "database": db_name,
                "host": "localhost",
                "port": 5432,
            },
            "superuser": {
                "username": "admin",
                "email": "admin@example.com",
                "password": _generate_secret_key(16),
            },
        }

    # Production doesn't need db_credentials (Heroku provides DATABASE_URL)
    if mode == Mode.PRODUCTION:
        return {
            "django_secret_key": f"CHANGE-ME-{mode.value.upper()}-KEY",
            "superuser": {
                "username": "admin",
                "email": "admin@example.com",
                "password": f"CHANGE-ME-{mode.value.upper()}-PASSWORD",
            },
        }

    # Staging needs db_credentials for non-Heroku deployments
    return {
        "django_secret_key": f"CHANGE-ME-{mode.value.upper()}-KEY",
        "db_credentials": {
            "username": "app",
            "password": f"CHANGE-ME-{mode.value.upper()}-PASSWORD",
            "database": "app",
            "host": "localhost",
            "port": 5432,
        },
        "superuser": {
            "username": "admin",
            "email": "admin@example.com",
            "password": f"CHANGE-ME-{mode.value.upper()}-PASSWORD",
        },
    }


def _deep_merge_missing(existing: dict, template: dict) -> MergeResult:
    """Merge template keys into existing dict, only adding missing keys.

    Returns MergeResult with the merged dict and a list of keys that were added.
    """
    result = dict(existing)
    added: list[str] = []

    for key, value in template.items():
        if key not in result:
            result[key] = value
            added.append(key)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            # Recursively merge nested dicts
            nested_result, nested_added = _deep_merge_missing(result[key], value)
            result[key] = nested_result
            added.extend(f"{key}.{k}" for k in nested_added)

    return MergeResult(result, added)


def _do_secrets_upgrade(
    ctx: "CliContext",
    project_dir: Path,
    key_path: Path,
    all_public_keys: list[str],
    needs_rotate: bool,
    project_name: str | None,
) -> SecretsStatus:
    """Perform the actual secrets upgrade with a valid key path.

    When encryption is enabled, this function requires the age key file to exist
    at key_path. When the key is GPG-protected, callers should invoke this inside
    a protected_age_key() context to ensure the key is temporarily decrypted.

    Args:
        ctx: CLI context with runner and config.
        project_dir: Project root directory
        key_path: Path to the (unencrypted) age private key file
        all_public_keys: List of all team member public keys (empty if no encryption)
        needs_rotate: Whether project secrets need key rotation
        project_name: Project name for template defaults

    Returns:
        SecretsStatus indicating what was done
    """
    runner = ctx.runner
    config = ctx.config
    manager = SecretsManager(runner, project_dir, key_path=key_path)
    if needs_rotate:
        logger.next("Rotating recipients for updated team")
        for mode in Mode.public():
            # Skip rotation if encryption is disabled for this mode
            mode_config = config.augment(DjbConfig(mode=mode))
            if not mode_config.secrets.encrypt:
                logger.info(f"Skipping {mode} (encryption disabled)")
                continue

            secrets_file = manager.secrets_dir / f"{mode}.yaml"
            if secrets_file.exists():
                try:
                    rotate_keys(runner, secrets_file, all_public_keys, key_path)
                    logger.done(f"Rotated recipients for {mode}")
                except SopsError as e:
                    logger.warning(f"Failed to rotate recipients for {mode}: {e}")
                    logger.info("Ask a team member who can decrypt to run: djb secrets rotate")

    initialized: list[str] = []
    upgraded: list[str] = []
    up_to_date: list[str] = []

    for mode in Mode.all():
        secrets_file = manager.secrets_dir / f"{mode}.yaml"
        template = _get_template(mode, project_name=project_name)
        mode_config = config.augment(DjbConfig(mode=mode))
        encrypt = mode_config.secrets.encrypt
        is_public = mode in Mode.public()

        # Skip public modes that need encryption if we don't have recipients
        if is_public and encrypt and not all_public_keys:
            continue

        if not secrets_file.exists():
            manager.save_secrets(mode, template)
            initialized.append(str(mode))
            continue

        # Upgrade existing secrets - public secrets might fail to decrypt
        try:
            existing = manager.load_secrets(mode)
            merged, added = _deep_merge_missing(existing, template)

            if added:
                manager.save_secrets(mode, merged)
                upgraded.append(str(mode))
            elif not encrypt and is_sops_encrypted(secrets_file):
                # Transition from encrypted to plaintext
                manager.save_secrets(mode, existing, public_keys=[])
                upgraded.append(str(mode))
            else:
                up_to_date.append(str(mode))
        except (FileNotFoundError, SopsError):
            # Public secrets: silently skip (new team member may not have access yet)
            # Dev secrets: re-raise (user should be able to decrypt their own secrets)
            if not is_public:
                raise

    return SecretsStatus(initialized=initialized, upgraded=upgraded, up_to_date=up_to_date)


def _prepare_secrets_dir(secrets_dir: Path) -> None:
    """Prepare secrets directory with gitignore.

    Creates the secrets directory if needed and ensures .gitignore is up to date.
    """
    # Ensure secrets directory exists
    secrets_dir.mkdir(parents=True, exist_ok=True)

    # Create .gitignore for secrets directory if it doesn't exist
    gitignore_path = secrets_dir / ".gitignore"
    gitignore_content = (
        "# Decrypted secrets (never commit these)\n"
        "*.decrypted.yaml\n"
        "*.plaintext.yaml\n"
        "*.secret\n"
        "*.tmp.yaml\n"
        "\n"
        "# User secrets (encrypted with user's own key, not shared)\n"
        "development.yaml\n"
    )
    if not gitignore_path.exists():
        gitignore_path.write_text(gitignore_content)


def _manage_recipients_and_upgrade(
    ctx: "CliContext",
    project_dir: Path,
    key_path: Path,
    public_key: str | None,
    email: str | None,
    name: str | None,
    project_name: str | None,
) -> SecretsStatus:
    """Manage recipients and perform secrets upgrade.

    This handles:
    - Adding the user's public key to .sops.yaml if needed
    - Detecting team membership changes
    - Calling _do_secrets_upgrade with appropriate parameters

    Args:
        ctx: CLI context with runner and config.
        project_dir: Project root directory
        key_path: Path to the age private key file
        public_key: The user's public key (None if no key access)
        email: User's email for identity
        name: User's name for identity
        project_name: Project name for template defaults

    Returns:
        SecretsStatus indicating what was done
    """
    runner = ctx.runner
    manager = SecretsManager(runner, project_dir, key_path=key_path)
    all_public_keys: list[str] = []
    needs_rotate = False

    if public_key is not None:
        # Get existing recipients from .sops.yaml (if any)
        recipients = manager.recipients
        original_recipients = dict(recipients)

        # Format identity (Name <email> or just email)
        identity = format_identity(name, email) if email else "unknown@example.com"

        # Add user's key if not already present
        if public_key not in recipients:
            recipients[public_key] = identity
            logger.done(f"Added public key for {identity}")
        elif email and not recipients[public_key]:
            # Update identity if we have it and it was missing
            recipients[public_key] = identity

        # Only write .sops.yaml if recipients changed
        if recipients != original_recipients:
            manager.save_config(recipients)
            logger.done("Updated .sops.yaml configuration")

        # Get all public keys for project secrets (multi-recipient)
        all_public_keys = list(recipients.keys())
        expected_keys = set(all_public_keys)

        # Check project secrets files to detect team membership changes
        all_added: set[str] = set()
        all_removed: set[str] = set()

        for mode in Mode.public():
            secrets_file = manager.secrets_dir / f"{mode}.yaml"
            if secrets_file.exists():
                actual_keys = _get_encrypted_recipients(secrets_file)
                if actual_keys:  # Only compare if we could read the keys
                    added = expected_keys - actual_keys
                    removed = actual_keys - expected_keys
                    all_added.update(added)
                    all_removed.update(removed)

        # Report team membership changes (exclude current user's key)
        other_added = all_added - {public_key}
        if other_added:
            for key in other_added:
                added_identity = recipients.get(key, "unknown")
                logger.warning(f"New team member added: {added_identity}")

        if all_removed:
            for key in all_removed:
                logger.warning(f"Team member removed: {key[:20]}...")

        # Determine if we need rotation due to team membership changes
        needs_rotate = bool(other_added or all_removed)

    return _do_secrets_upgrade(
        ctx=ctx,
        project_dir=project_dir,
        key_path=key_path,
        all_public_keys=all_public_keys,
        needs_rotate=needs_rotate,
        project_name=project_name,
    )


def init_or_upgrade_secrets(
    ctx: "CliContext",
    project_root: Path,
    email: str | None = None,
    name: str | None = None,
    project_name: str | None = None,
) -> SecretsStatus:
    """Initialize or upgrade secrets for all environments.

    Secrets are divided into two categories:
    - User secrets (development.yaml): Encrypted with user's own key only, gitignored
    - Project secrets (staging.yaml, production.yaml): Multi-recipient, committed

    For each environment:
    - If secrets file doesn't exist: create it from template
    - If secrets file exists: upgrade it with any new template keys

    Args:
        ctx: CLI context with runner and config.
        project_root: Root directory of the project
        email: Email to associate with the public key
        name: Name to associate with the public key (for git-style identity)
        project_name: Project name (used for db_credentials defaults in dev)

    Returns a SecretsStatus indicating what was done.

    Raises:
        RuntimeError: If SOPS or age is not installed
    """
    runner = ctx.runner
    config = ctx.config
    key_path = get_default_key_path(project_root)
    secrets_dir = project_root / "secrets"

    # Check which modes have encryption disabled
    disabled_modes = [
        mode for mode in Mode.all() if not config.augment(DjbConfig(mode=mode)).secrets.encrypt
    ]
    any_encryption_needed = len(disabled_modes) < len(Mode.all())

    # Check if all plaintext modes are already set up
    plaintext_modes_ready = all(
        (secrets_dir / f"{mode}.yaml").exists()
        and not is_sops_encrypted(secrets_dir / f"{mode}.yaml")
        for mode in disabled_modes
    )

    # Prepare secrets directory (migrations, gitignore)
    _prepare_secrets_dir(secrets_dir)

    # If no encryption needed anywhere, just do the upgrade without any key setup
    if not any_encryption_needed:
        return _manage_recipients_and_upgrade(
            ctx, project_root, key_path, None, email, name, project_name
        )

    # Check prerequisites
    if not check_sops_installed():
        raise RuntimeError("SOPS is not installed")
    if not check_age_installed():
        raise RuntimeError("age is not installed")

    # Check if key exists unencrypted
    if key_path.exists():
        public_key = get_public_key_from_private(runner, key_path)
        return _manage_recipients_and_upgrade(
            ctx, project_root, key_path, public_key, email, name, project_name
        )

    # Check if key is GPG-protected
    encrypted_path = get_encrypted_key_path(key_path)
    if encrypted_path.exists():
        # Skip decryption if all plaintext modes are already set up
        if plaintext_modes_ready:
            logger.info("Skipping encrypted modes (age key is GPG-protected)")
            return _manage_recipients_and_upgrade(
                ctx, project_root, key_path, None, email, name, project_name
            )

        # Try to decrypt - do everything inside single GPG context
        try:
            with protected_age_key(project_root, runner) as decrypted_key_path:
                public_key = get_public_key_from_private(runner, decrypted_key_path)
                return _manage_recipients_and_upgrade(
                    ctx, project_root, decrypted_key_path, public_key, email, name, project_name
                )
        except (GpgError, ProtectedFileError) as e:
            if disabled_modes:
                logger.warning(f"Could not access GPG-protected age key: {e}")
                logger.info(
                    f"Continuing with plaintext modes: {', '.join(str(m) for m in disabled_modes)}"
                )
                return _manage_recipients_and_upgrade(
                    ctx, project_root, key_path, None, email, name, project_name
                )
            raise

    # No key exists - generate new one
    public_key, _ = generate_age_key(runner, key_path)
    logger.done(f"Generated age key at {key_path}")

    # Try to protect new key with GPG
    if check_gpg_installed():
        try:
            if protect_age_key(project_root, runner):
                logger.done("Protected age key with GPG encryption")
        except GpgError as e:
            logger.warning(f"Could not enable GPG protection: {e}")
            logger.info("Age key remains unencrypted. Run 'djb secrets protect' to retry.")
    else:
        logger.warning("GPG not installed - age key stored without encryption")
        logger.info("Install GPG and run 'djb secrets protect' to secure your key")

    return _manage_recipients_and_upgrade(
        ctx, project_root, key_path, public_key, email, name, project_name
    )
