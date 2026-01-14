"""
djb.secrets - Encrypted secrets management with SOPS.

Provides encrypted secrets storage using SOPS with age encryption.

Quick start:
    from djb.secrets import SecretsManager, SopsError
    from djb.types import Mode

    try:
        manager = SecretsManager(runner, project_dir)
        secrets = manager.load_secrets(Mode.PRODUCTION)
    except SopsError as e:
        print(f"Decryption failed: {e}")

Public API:
    Core:
        SecretsManager - High-level secrets management class (recommended)
            - load_secrets(mode) - Load decrypted secrets (handles GPG protection)
            - save_secrets(mode, data) - Save encrypted secrets
            - view_secrets(mode, key) - View secrets or specific key
            - set_secret(mode, key, value) - Set a secret value
            - edit_secrets(mode) - Open secrets in SOPS editor
            - export_private_key() - Export private key for backup
            - get_public_key() - Get public key from private key
            - rotate_all_secrets(modes) - Re-encrypt for updated recipients
            - recipients - Property: dict of public_key -> identity
            - recipient_keys - Property: list of public keys
            - sops_config_path - Property: path to .sops.yaml
            - save_config(recipients) - Write .sops.yaml
        encrypt_file, decrypt_file - SOPS file encryption/decryption
        generate_age_key, AgeKeyPair - Create new age keypair
        parse_identity, ParsedIdentity - Parsed git-style identity strings
        SopsError - SOPS operation failures

    Django Integration:
        load_secrets_for_django - Load secrets with Django environment detection
        lazy_database_config - Lazy-loading database config (defers GPG decryption)

    Errors:
        GpgError, GpgTimeoutError, ProtectedFileError - Error classes

    Initialization:
        init_or_upgrade_secrets - Set up secrets infrastructure
        SecretsStatus - Initialization status enum

    Internal (not part of public API):
        protected_age_key - Use SecretsManager methods instead
        protect_age_key, unprotect_age_key - Use CLI commands instead
        is_age_key_protected - Use SecretsManager internally
        GPG functions - Internal to secrets module
"""

from __future__ import annotations

from djb.secrets.core import (
    SOPS_TIMEOUT,
    AgeKeyPair,
    ParsedIdentity,
    SecretsManager,
    SopsError,
    check_age_installed,
    check_sops_installed,
    decrypt_file,
    encrypt_file,
    find_placeholder_secrets,
    format_identity,
    generate_age_key,
    get_nested_value,
    get_public_key_from_private,
    is_placeholder_value,
    is_sops_encrypted,
    is_valid_age_public_key,
    load_secrets,
    parse_identity,
    rotate_keys,
    set_nested_value,
)
from djb.secrets.django import lazy_database_config, load_secrets_for_django
from djb.secrets.paths import (
    get_default_key_path,
    get_default_secrets_dir,
    get_encrypted_key_path,
)
from djb.secrets.gpg import (
    GPG_INTERACTIVE_TIMEOUT,
    GPG_TIMEOUT,
    GpgError,
    GpgTimeoutError,
    check_gpg_installed,
    ensure_loopback_pinentry,
    generate_gpg_key,
    get_default_gpg_email,
    get_gpg_home,
    get_gpg_key_id,
    gpg_decrypt_file,
    gpg_encrypt_file,
    has_gpg_secret_key,
    init_gpg_agent_config,
    is_gpg_encrypted,
    setup_gpg_tty,
)
from djb.secrets.init import (
    SecretsStatus,
    init_or_upgrade_secrets,
)
from djb.secrets.protected import (
    ProtectedFileError,
    is_age_key_protected,
    protect_age_key,
    protected_age_key,
    unprotect_age_key,
)

__all__ = [
    # Core SOPS functions
    "AgeKeyPair",
    "ParsedIdentity",
    "SOPS_TIMEOUT",
    "SecretsManager",
    "SopsError",
    "check_age_installed",
    "check_sops_installed",
    "decrypt_file",
    "encrypt_file",
    "find_placeholder_secrets",
    "format_identity",
    "generate_age_key",
    "get_default_key_path",
    "get_default_secrets_dir",
    "get_encrypted_key_path",
    "get_nested_value",
    "get_public_key_from_private",
    "is_placeholder_value",
    "is_sops_encrypted",
    "is_valid_age_public_key",
    "lazy_database_config",
    "load_secrets",
    "load_secrets_for_django",
    "parse_identity",
    "rotate_keys",
    "set_nested_value",
    # GPG functions
    "GPG_INTERACTIVE_TIMEOUT",
    "GPG_TIMEOUT",
    "GpgError",
    "GpgTimeoutError",
    "check_gpg_installed",
    "ensure_loopback_pinentry",
    "generate_gpg_key",
    "get_default_gpg_email",
    "get_gpg_home",
    "get_gpg_key_id",
    "gpg_decrypt_file",
    "gpg_encrypt_file",
    "has_gpg_secret_key",
    "init_gpg_agent_config",
    "is_gpg_encrypted",
    "setup_gpg_tty",
    # Protected file access
    "ProtectedFileError",
    "is_age_key_protected",
    "protect_age_key",
    "protected_age_key",
    "unprotect_age_key",
    # Initialization
    "SecretsStatus",
    "init_or_upgrade_secrets",
]
