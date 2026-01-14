"""Tests for E2E test utilities.

These tests verify that the test utility functions work correctly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from . import add_django_settings_from_startproject


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


class TestAddDjangoSettingsFromStartproject:
    """Tests for add_django_settings_from_startproject utility."""

    def test_creates_realistic_settings(self, project_dir: Path):
        """add_django_settings_from_startproject creates realistic Django settings."""
        add_django_settings_from_startproject(project_dir, "myproject")

        settings_dir = project_dir / "myproject"
        assert settings_dir.exists()
        assert (settings_dir / "__init__.py").exists()
        assert (settings_dir / "settings.py").exists()
        assert (settings_dir / "urls.py").exists()
        assert (settings_dir / "wsgi.py").exists()
        assert (settings_dir / "asgi.py").exists()

        settings_content = (settings_dir / "settings.py").read_text()
        # Real startproject generates all of these:
        assert "SECRET_KEY" in settings_content
        assert "DEBUG" in settings_content
        assert "INSTALLED_APPS" in settings_content
        assert "MIDDLEWARE" in settings_content
        assert "ROOT_URLCONF" in settings_content
        assert "TEMPLATES" in settings_content
        assert "DATABASES" in settings_content
        assert "AUTH_PASSWORD_VALIDATORS" in settings_content
        assert "LANGUAGE_CODE" in settings_content
        assert "TIME_ZONE" in settings_content
        assert "STATIC_URL" in settings_content

    def test_creates_manage_py(self, project_dir: Path):
        """add_django_settings_from_startproject creates manage.py in project root."""
        add_django_settings_from_startproject(project_dir, "myproject")

        manage_py = project_dir / "manage.py"
        assert manage_py.exists()
        content = manage_py.read_text()
        assert "django" in content
        assert "myproject.settings" in content

    def test_custom_package_name(self, project_dir: Path):
        """add_django_settings_from_startproject works with custom package names."""
        add_django_settings_from_startproject(project_dir, "customproject")

        settings_dir = project_dir / "customproject"
        assert settings_dir.exists()
        assert (settings_dir / "settings.py").exists()

        settings_content = (settings_dir / "settings.py").read_text()
        # Django's startproject uses the package name in WSGI_APPLICATION
        assert "customproject.wsgi.application" in settings_content
