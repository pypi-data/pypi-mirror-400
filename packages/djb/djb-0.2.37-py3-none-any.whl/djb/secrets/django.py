"""
Django settings integration for djb secrets.

Provides convenience functions for loading secrets in Django settings.py
with automatic support for test overrides and environment detection.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any

from django.utils.functional import SimpleLazyObject

from djb.cli.context import CliContext
from djb.secrets.core import SopsError, load_secrets
from djb.secrets.gpg import GpgError
from djb.secrets.protected import ProtectedFileError
from djb.types import Mode


def load_secrets_for_django(
    base_dir: Path,
    *,
    warn_on_failure: bool = True,
) -> dict[str, Any]:
    """
    Load secrets for Django settings with automatic environment detection.

    This is a convenience wrapper for Django settings.py that:
    - Auto-detects environment (production on Heroku, else from ENVIRONMENT env var)
    - Respects TEST_SECRETS_DIR and TEST_AGE_KEY_PATH environment variables
    - Falls back to base_dir/secrets for the secrets directory
    - Handles failures gracefully (returns empty dict with optional warning)
    - Skips loading on Heroku where secrets come from environment variables

    Usage in settings.py:
        from djb.secrets import load_secrets_for_django
        BASE_DIR = Path(__file__).resolve().parent.parent
        _secrets = load_secrets_for_django(BASE_DIR)
        SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or _secrets.get("django_secret_key")

    Args:
        base_dir: Project base directory (typically Django's BASE_DIR)
        warn_on_failure: If True, emit warnings on failure (default True)

    Returns:
        Dictionary of decrypted secrets, or empty dict on failure/Heroku

    Environment variables:
        DYNO: If set, assumes Heroku and returns empty dict
        ENVIRONMENT: Secrets environment (development, staging, production). Defaults to "development"
        TEST_SECRETS_DIR: Override secrets directory (for pytest)
        TEST_AGE_KEY_PATH: Override age key path (for pytest)
    """
    # On Heroku, secrets come from environment variables
    is_heroku = "DYNO" in os.environ
    if is_heroku:
        return {}

    # Determine mode
    env_str = "production" if is_heroku else os.environ.get("ENVIRONMENT", "development")
    mode = Mode(env_str)

    # Allow tests to provide their own secrets infrastructure
    secrets_dir = (
        Path(os.environ["TEST_SECRETS_DIR"])
        if "TEST_SECRETS_DIR" in os.environ
        else base_dir / "secrets"
    )
    key_path = Path(os.environ["TEST_AGE_KEY_PATH"]) if "TEST_AGE_KEY_PATH" in os.environ else None

    try:
        runner = CliContext().runner
        return load_secrets(
            runner,
            mode=mode,
            secrets_dir=secrets_dir,
            key_path=key_path,
        )
    except (FileNotFoundError, SopsError, GpgError, ProtectedFileError) as e:
        if warn_on_failure:
            warnings.warn(f"Could not load secrets: {e}", stacklevel=2)
        return {}


def lazy_database_config(
    base_dir: Path,
    *,
    engine: str = "django.db.backends.postgresql",
    default_name: str = "myproject",
    default_user: str = "myproject",
    default_password: str = "password",
    default_host: str = "localhost",
    default_port: int = 5432,
    warn_on_failure: bool = True,
    test_template: str | None = None,
) -> SimpleLazyObject:
    """
    Create a lazy database config that loads secrets only when first accessed.

    Returns a SimpleLazyObject wrapping the database config dict. Secrets are
    only loaded when the config is first accessed (e.g., when Django connects
    to the database). This allows CLI commands that don't use the database to
    run without triggering GPG decryption.

    Usage in settings.py:
        from djb.secrets import lazy_database_config

        BASE_DIR = Path(__file__).resolve().parent.parent

        if IS_PRODUCTION:
            DATABASES = {"default": dj_database_url.config(...)}
        else:
            DATABASES = {"default": lazy_database_config(
                BASE_DIR,
                engine="django.contrib.gis.db.backends.postgis",
                default_name="myapp",
                default_user="myapp",
            )}

    Args:
        base_dir: Project base directory (typically Django's BASE_DIR)
        engine: Database engine (default: django.db.backends.postgresql)
        default_name: Default database name if secrets unavailable
        default_user: Default database user if secrets unavailable
        default_password: Default database password if secrets unavailable
        default_host: Default database host if secrets unavailable
        default_port: Default database port if secrets unavailable
        warn_on_failure: If True, emit warnings when secrets fail to load
        test_template: PostgreSQL template database for tests (e.g., 'template_postgis')

    Returns:
        SimpleLazyObject wrapping the database config dict

    Note:
        The config looks for 'db_credentials' in secrets with keys:
        database, username, password, host, port
    """

    def _build_config() -> dict[str, Any]:
        secrets = load_secrets_for_django(base_dir, warn_on_failure=warn_on_failure)
        db_creds = secrets.get("db_credentials")
        db_creds = db_creds if isinstance(db_creds, dict) else {}
        config: dict[str, Any] = {
            "ENGINE": engine,
            "NAME": db_creds.get("database", default_name),
            "USER": db_creds.get("username", default_user),
            "PASSWORD": db_creds.get("password", default_password),
            "HOST": db_creds.get("host", default_host),
            "PORT": db_creds.get("port", default_port),
        }
        if test_template:
            config["TEST"] = {"TEMPLATE": test_template}
        return config

    return SimpleLazyObject(_build_config)
