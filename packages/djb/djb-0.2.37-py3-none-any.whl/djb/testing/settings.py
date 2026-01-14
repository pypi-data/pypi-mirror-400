"""
Minimal Django settings for djb tests.

This provides just enough configuration for pytest-django to work when
testing djb as a standalone package. Host projects using djb will have
their own settings configured via DJANGO_SETTINGS_MODULE.
"""

import os
from pathlib import Path

from djb.secrets import lazy_database_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

SECRET_KEY = "djb-test-secret-key-not-for-production"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

DATABASES = {
    "default": lazy_database_config(
        BASE_DIR,
        default_name="djb_test",
        default_user=os.environ.get("USER", "postgres"),
        default_password="",
        warn_on_failure=False,
    )
}

# Use in-memory email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Minimal settings required by Django
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
